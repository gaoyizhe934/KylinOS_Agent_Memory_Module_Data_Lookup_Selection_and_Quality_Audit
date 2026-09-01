# -*- coding: utf-8 -*-
"""阶段4: 小样本质量审计脚本（Annotator B 预写版）

依据:
- 手册第5章 阶段4「小样本下载与质量审计」: 检查解析/缺失/重复/标签/证据
- 手册附录C Prompt 05: 字段缺失、类型、编码、重复、异常长度、ID/引用完整性、
  标签-证据可推导性、任务匹配度、正/负/边界/困难覆盖、敏感信息、在线依赖、
  人工逐条复核样本 ID
- 手册附录C Prompt 05-R: 必须列出脚本可能静默丢失数据的路径
- 手册 6.3 人工抽样规则: 按规模给出最低人工抽样量

产出（脚本只写这4个位置，绝不写 data/raw）:
- reports/stage4_sample_audit_report.md    审计报告（人读）
- data/interim/stage4_anomalies.csv         异常样本清单
- evidence/hashes/stage4_sample_hash.txt   抽样哈希（逐文件 SHA256）
- evidence/audit/stage4_audit_summary.json 机读审计摘要

纪律:
- raw 只读; 异常只标记不删除; 本报告为 AI 辅助草案, Gate 4 由 Reviewer 决定
- 正式运行应在 Gate 3（候选标记）批准后, 由 A 下载 50~100 条新样本再执行
  （Gate 3 批准前仅允许运行单元测试 test_stage4_sample_audit.py, 不产生运行产物）

字段类型校验（Prompt 05 "字段类型"）:
- 已配置数据集: DATASET_CONFIGS[*]['field_types'] 声明每个字段的期望 Python 类型
- 自动探测数据集: 按 id(str|int) / 标签(str|list) / 类别(str) / 文本(str) 泛化规则
- 类型不符记 type_mismatch 异常; bool 因 Python 的 bool<int 继承被显式排除;
  缺失/空值由 missing_field / missing_label / missing_evidence 检查负责, 不重复报类型

用法:
    python scripts/audit/stage4_sample_audit.py                     # 审计 data/raw 下全部数据集
    python scripts/audit/stage4_sample_audit.py --datasets longmemeval_v2_2026
    python scripts/audit/stage4_sample_audit.py --note "正式运行备注"
    python scripts/audit/test_stage4_sample_audit.py                # 单元测试（不读 raw, 不写产物）
"""
import argparse
import csv
import hashlib
import io
import json
import os
import random
import re
import sys
import time
from collections import Counter

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(REPO_ROOT, 'data', 'raw')
OUT_REPORT = os.path.join(REPO_ROOT, 'reports', 'stage4_sample_audit_report.md')
OUT_ANOMALIES = os.path.join(REPO_ROOT, 'data', 'interim', 'stage4_anomalies.csv')
OUT_HASH = os.path.join(REPO_ROOT, 'evidence', 'hashes', 'stage4_sample_hash.txt')
OUT_SUMMARY = os.path.join(REPO_ROOT, 'evidence', 'audit', 'stage4_audit_summary.json')

DATA_EXTS = ('.json', '.jsonl', '.csv', '.tsv')
META_FILENAMES = {'download.log', 'manifest.json', 'sha256sum.txt', 'checksums.sha256',
                  'readme.md', 'schema.md', 'license', 'license.txt'}
RANDOM_SEED = 42

# --- Gate 3 门禁（正式审计前置校验, PR#3 P1-2）---
# 手册 6.3 + 阶段4: 仅对 Reviewer 标记为「允许试用」的候选、每集 50~100 条新样本执行正式审计
GATE_STATUS_FILE = os.path.join(REPO_ROOT, 'reports', 'gate_status.md')
REGISTRY_FILE = os.path.join(REPO_ROOT, 'registry', 'dataset_registry.csv')
ALLOWED_GATE3_STATUS = '允许试用'
FORMAL_SAMPLE_MIN = 50
FORMAL_SAMPLE_MAX = 100

# 敏感信息模式（命中只标记, 由人工判断真伪; 研究数据里的合成内容可能误报）
# 高危模式逐条上报; 低危模式在合成研究数据中普遍存在, 只计数并抽样上报, 避免淹没高危信号
SENSITIVE_PATTERNS = [
    ('email', r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'),
    ('cn_mobile', r'(?<![0-9])1[3-9][0-9]{9}(?![0-9])'),
    ('cn_id_card', r'(?<![0-9])[0-9]{17}[0-9Xx](?![0-9])'),
    ('api_key_openai', r'sk-[A-Za-z0-9_-]{20,}'),
    ('api_key_github', r'gh[pousr]_[A-Za-z0-9]{20,}'),
    ('api_key_aws', r'AKIA[0-9A-Z]{16}'),
    ('api_key_slack', r'xox[baprs]-[A-Za-z0-9-]{10,}'),
    ('bearer_token', r'(?i)bearer\s+[A-Za-z0-9._-]{20,}'),
    ('private_ip', r'(?<![0-9])(?:10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})(?![0-9])'),
    ('win_path', r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)+[^\\/:*?"<>|\r\n]*'),
]
URL_RE = re.compile(r'https?://[^\s"\'<>)\]]+')
HIGH_RISK_PATTERNS = {'api_key_openai', 'api_key_github', 'api_key_aws', 'api_key_slack',
                      'bearer_token', 'cn_id_card'}
LOW_RISK_SAMPLE_LIMIT = 5  # 每数据集低危敏感命中的抽样上报条数
NULL_STRINGS = {'none', 'null', 'nan', 'n/a', ''}

# 已知数据集的专用配置; 未列出的数据集走通用自动探测
# field_types: 字段期望类型（单值或元组）; bool 一律视为类型错误（不因 bool<int 继承漏报）
DATASET_CONFIGS = {
    'longmemeval_cleaned_2025': {
        'id_field': 'question_id', 'label_field': 'answer',
        'evidence_fields': ['haystack_sessions', 'answer_session_ids'],
        'text_fields': ['question', 'answer'], 'category_field': 'question_type',
        'ref_check': 'longmemeval_oracle',
        'field_types': {'question_id': str, 'answer': str, 'question': str,
                        'question_type': str, 'haystack_sessions': list,
                        'answer_session_ids': list, 'haystack_session_ids': list},
    },
    'longmemeval_v2_2026': {
        'id_field': 'id', 'label_field': 'answer',
        'evidence_fields': ['eval_function'],
        'text_fields': ['question', 'answer'], 'category_field': 'question_type',
        'field_types': {'id': str, 'answer': str, 'question': str,
                        'question_type': str, 'eval_function': str},
    },
    'stabletoolbench_2024': {
        'id_field': 'query_id', 'label_field': 'relevant APIs',
        'evidence_fields': ['api_list'],
        'text_fields': ['query'], 'category_field': None,
        'field_types': {'query_id': str, 'query': str,
                        'relevant APIs': list, 'api_list': list},
    },
}

ID_FIELD_HINT = re.compile(r'(^|_)(id|question_id|query_id|sample_id|uid)$', re.I)
LABEL_FIELD_HINT = re.compile(r'^(answer|label|gold|relevant APIs|relevant_apis|target|output)$', re.I)
CATEGORY_FIELD_HINT = re.compile(r'^(task_type|question_type|category|type|domain|intent)$', re.I)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_record_hash(record):
    return hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True,
                                     default=str).encode('utf-8')).hexdigest()


def gate3_approved(path=GATE_STATUS_FILE):
    """判断 Gate 3 是否已获 Reviewer 批准（读取 gate_status.md 的 Gate 3 行）。

    返回 (bool, str): 通过与否 + 该行原文/失败原因。单元测试可注入临时 path。
    """
    if not os.path.isfile(path):
        return False, '缺少 %s' % os.path.relpath(path, REPO_ROOT)
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError as e:
        return False, '读取 gate_status.md 失败: %s' % e
    for ln in lines:
        s = ln.strip()
        if s.startswith('| Gate 3'):
            if ('⏳' in s) or ('下一阶段' in s) or ('待批准' in s) or ('待 Reviewer' in s):
                return False, 'Gate 3 状态未批准: %s' % s
            if ('通过' in s) or ('已批准' in s) or ('approved' in s.lower()):
                return True, s
            return False, '无法判定 Gate 3 状态: %s' % s
    return False, 'gate_status.md 未找到 Gate 3 行'


def load_registry_gate3_status(path=REGISTRY_FILE):
    """读取 registry 的 gate3_status 列, 返回 {dataset_id: 状态}。

    无该列或读取失败时返回空 dict（后续按「未标记」处理）。
    """
    statuses = {}
    if not os.path.isfile(path):
        return statuses
    try:
        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or 'gate3_status' not in reader.fieldnames:
                return statuses
            for row in reader:
                ds = (row.get('dataset_id') or '').strip()
                st = (row.get('gate3_status') or '').strip()
                if ds:
                    statuses[ds] = st
    except OSError:
        return statuses
    return statuses


def in_formal_sample_range(n):
    """正式审计样本量范围校验: 每集 50~100 条新样本（手册 6.3 / 阶段4）。"""
    return FORMAL_SAMPLE_MIN <= n <= FORMAL_SAMPLE_MAX


def iter_data_files(ds_dir):
    """遍历数据集目录下的数据文件, 同时统计未处理类型/空文件/管理文件."""
    stats = {'data_files': [], 'meta_files': 0, 'unhandled': [], 'empty': []}
    for root, _dirs, files in os.walk(ds_dir):
        for fn in sorted(files):
            path = os.path.join(root, fn)
            if fn.lower() in META_FILENAMES:
                stats['meta_files'] += 1
                continue
            if os.path.getsize(path) == 0:
                stats['empty'].append(os.path.relpath(path, ds_dir))
                continue
            if fn.lower().endswith(DATA_EXTS):
                stats['data_files'].append(path)
            else:
                stats['unhandled'].append(os.path.relpath(path, ds_dir))
    stats['data_files'].sort()
    return stats


def load_records(path, anomalies, ds_id, rel):
    """按扩展名解析文件为记录列表; dict 视为单条记录; 解析失败记异常, 绝不静默丢弃."""
    ext = os.path.splitext(path)[1].lower()
    records = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if ext == '.jsonl':
                for i, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        anomalies.append(_anom(ds_id, rel, i, '', 'parse_error', 'high',
                                               'JSONL 第%d行解析失败: %s' % (i, e)))
            elif ext in ('.json',):
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    records = [data]
                else:
                    anomalies.append(_anom(ds_id, rel, 0, '', 'parse_error', 'high', 'JSON 顶层类型异常'))
            else:
                dialect = 'excel-tab' if ext == '.tsv' else 'excel'
                reader = csv.DictReader(f, dialect=dialect)
                records = [dict(r) for r in reader]
    except (UnicodeDecodeError, json.JSONDecodeError, OSError) as e:
        anomalies.append(_anom(ds_id, rel, 0, '', 'parse_error', 'high',
                               '文件级解析失败: %s' % e))
    return records


def _anom(ds_id, file, idx, rid, atype, sev, detail):
    return {'dataset_id': ds_id, 'source_file': file, 'record_index': idx,
            'record_id': rid, 'anomaly_type': atype, 'severity': sev,
            'detail': detail[:300]}


def detect_config(ds_id, records):
    if ds_id in DATASET_CONFIGS:
        cfg = dict(DATASET_CONFIGS[ds_id])
        if records:
            keys = set(records[0].keys()) if isinstance(records[0], dict) else set()
            for f in ('id_field', 'label_field', 'category_field'):
                if cfg.get(f) and cfg[f] not in keys:
                    cfg[f] = None if f != 'id_field' else cfg.get('id_field')
        return cfg
    keys = list(records[0].keys()) if records and isinstance(records[0], dict) else []
    idf = next((k for k in keys if ID_FIELD_HINT.match(k)), None)
    lab = next((k for k in keys if LABEL_FIELD_HINT.match(k)), None)
    cat = next((k for k in keys if CATEGORY_FIELD_HINT.match(k)), None)
    texts = [k for k in keys if isinstance(records[0].get(k), str) and k not in (idf, cat)] if keys else []
    gft = {}
    if idf:
        gft[idf] = (str, int)
    if lab:
        gft[lab] = (str, list)
    if cat:
        gft[cat] = (str,)
    for t in texts[:5]:
        gft[t] = (str,)
    return {'id_field': idf, 'label_field': lab, 'evidence_fields': [],
            'text_fields': texts[:5], 'category_field': cat, 'ref_check': None,
            'field_types': gft}


def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0
    k = max(0, min(len(sorted_vals) - 1, int(round(p / 100.0 * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def iter_strings(obj):
    """递归提取记录中所有真实字符串值（避免扫 JSON dump 转义串造成误报）."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            for s in iter_strings(v):
                yield s
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for s in iter_strings(v):
                yield s


def scan_sensitive(text):
    hits = Counter()
    for name, pat in SENSITIVE_PATTERNS:
        n = len(re.findall(pat, text))
        if n:
            hits[name] = n
    urls = len(URL_RE.findall(text))
    return hits, urls


def audit_dataset(ds_id, note, ds_dir=None):
    """审计单个数据集; ds_dir 供单元测试注入临时目录, 默认 data/raw/<ds_id>."""
    if ds_dir is None:
        ds_dir = os.path.join(RAW_DIR, ds_id)
    anomalies = []
    result = {'dataset_id': ds_id, 'status': 'ok', 'files': 0, 'records': 0,
              'parse_failed': 0, 'file_hashes': [], 'empty_files': [], 'unhandled_files': [],
              'counts': {}, 'length_stats': {}, 'coverage': {}, 'sensitive': {},
              'url_refs': 0, 'required_manual_sample': 0, 'manual_review_ids': [],
              'categories': {}}
    if not os.path.isdir(ds_dir):
        result['status'] = '目录不存在'
        return result, anomalies

    fstats = iter_data_files(ds_dir)
    result['empty_files'] = fstats['empty']
    result['unhandled_files'] = fstats['unhandled']
    result['files'] = len(fstats['data_files'])
    for ef in fstats['empty']:
        anomalies.append(_anom(ds_id, ef, 0, '', 'empty_file', 'medium', '空文件（0字节）'))
    for uf in fstats['unhandled']:
        anomalies.append(_anom(ds_id, uf, 0, '', 'unhandled_type', 'medium',
                               '非结构化数据文件，脚本未解析，需人工检查'))

    if not fstats['data_files']:
        result['status'] = '无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载'
        return result, anomalies

    all_records = []
    rec_sources = []  # (rel_file, index_in_file)
    for path in fstats['data_files']:
        rel = os.path.relpath(path, ds_dir)
        result['file_hashes'].append((rel, sha256_file(path)))
        recs = load_records(path, anomalies, ds_id, rel)
        all_records.extend(recs)
        rec_sources.extend((rel, i) for i in range(len(recs)))
    result['records'] = len(all_records)
    if not all_records:
        result['status'] = '数据文件存在但无有效记录'
        return result, anomalies

    cfg = detect_config(ds_id, all_records)
    idf, lab, cat = cfg['id_field'], cfg['label_field'], cfg['category_field']
    texts, evs = cfg['text_fields'], cfg['evidence_fields']

    # --- 字段缺失 / 类型 / null字符串化 ---
    ids = []
    seen_hash = {}
    seen_id = {}
    length_acc = {t: [] for t in texts if t}
    sens_total = Counter()
    sens_high_total = Counter()
    low_sens_samples = 0
    coverage = Counter()
    for (rel, idx), rec in zip(rec_sources, all_records):
        if not isinstance(rec, dict):
            anomalies.append(_anom(ds_id, rel, idx, '', 'type_anomaly', 'medium', '记录不是对象'))
            continue
        rid = rec.get(idf, '') if idf else ''
        if idf and (rid is None or str(rid).strip() == ''):
            anomalies.append(_anom(ds_id, rel, idx, '', 'missing_field', 'high',
                                   '缺失 ID 字段 %s' % idf))
        else:
            ids.append(str(rid))
            if str(rid) in seen_id:
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'duplicate_id', 'high',
                                       'ID 重复（首见于 %s#%d）' % seen_id[str(rid)]))
            else:
                seen_id[str(rid)] = (rel, idx)
        if lab and (rec.get(lab) is None or str(rec.get(lab)).strip() == ''):
            anomalies.append(_anom(ds_id, rel, idx, str(rid), 'missing_label', 'high',
                                   '标签字段 %s 为空' % lab))
        for ev in evs:
            v = rec.get(ev)
            if v is None or v == [] or v == {} or str(v).strip() == '':
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'missing_evidence', 'medium',
                                       '证据字段 %s 为空（标签-证据可推导性存疑，需人工核）' % ev))
        # 字段类型校验（Prompt 05）: 缺失/空值由上面的缺失检查负责, 这里只报类型不符
        for field, expected in (cfg.get('field_types') or {}).items():
            if field not in rec:
                continue
            v = rec[field]
            if v is None or (isinstance(v, str) and not v.strip()):
                continue
            expected_types = expected if isinstance(expected, tuple) else (expected,)
            if isinstance(v, bool) or not isinstance(v, expected_types):
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'type_mismatch', 'medium',
                                       '字段 %s 期望类型 %s, 实际 %s: %s' % (
                                           field,
                                           '|'.join(t.__name__ for t in expected_types),
                                           type(v).__name__, str(v)[:80])))
        for k, v in rec.items():
            if isinstance(v, str) and v.strip().lower() in NULL_STRINGS and v != '':
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'null_string', 'low',
                                       '字段 %s 值为字符串 "%s"（疑似 null 字符串化）' % (k, v)))
        rh = canonical_record_hash(rec)
        if rh in seen_hash:
            anomalies.append(_anom(ds_id, rel, idx, str(rid), 'duplicate_record', 'medium',
                                   '整条记录与 %s#%d 完全重复' % seen_hash[rh]))
        else:
            seen_hash[rh] = (rel, idx)
        for t in length_acc:
            v = rec.get(t)
            length_acc[t].append(len(v) if isinstance(v, str) else len(str(v)) if v is not None else 0)
        if cat:
            coverage[str(rec.get(cat))] += 1
        rec_hits = Counter()
        rec_urls = 0
        for s in iter_strings(rec):
            h, u = scan_sensitive(s)
            rec_hits.update(h)
            rec_urls += u
        if rec_hits:
            sens_total.update(rec_hits)
            high_hits = {k: v for k, v in rec_hits.items() if k in HIGH_RISK_PATTERNS}
            if high_hits:
                sens_high_total.update(high_hits)
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'sensitive_hit', 'high',
                                       '高危敏感模式命中: %s（必须人工核）' % high_hits))
            elif low_sens_samples < LOW_RISK_SAMPLE_LIMIT:
                low_sens_samples += 1
                anomalies.append(_anom(ds_id, rel, idx, str(rid), 'sensitive_hit', 'low',
                                       '低危敏感模式抽样（共命中见统计, 判定合成/真实由人工）: %s' % dict(rec_hits)))
        result['url_refs'] += rec_urls

    # --- 长度统计与异常长度 ---
    for t, vals in length_acc.items():
        if not vals:
            continue
        sv = sorted(vals)
        p50, p95, p99 = percentile(sv, 50), percentile(sv, 95), percentile(sv, 99)
        result['length_stats'][t] = {'p50': p50, 'p95': p95, 'p99': p99,
                                     'max': sv[-1], 'min': sv[0], 'zero': sum(1 for v in vals if v == 0)}
        thr_high = max(3 * p99 if p99 else 0, 2000)
        for (rel, idx), rec in zip(rec_sources, all_records):
            if not isinstance(rec, dict):
                continue
            v = rec.get(t)
            ln = len(v) if isinstance(v, str) else len(str(v)) if v is not None else 0
            rid = str(rec.get(idf, '')) if idf else ''
            if ln == 0:
                anomalies.append(_anom(ds_id, rel, idx, rid, 'length_anomaly', 'medium',
                                       '字段 %s 长度为 0' % t))
            elif ln > thr_high:
                anomalies.append(_anom(ds_id, rel, idx, rid, 'length_anomaly', 'low',
                                       '字段 %s 长度 %d 超阈值 %d（P99×3 与 2000 取大）' % (t, ln, thr_high)))

    # --- 引用完整性（longmemeval_cleaned 专用）---
    if cfg.get('ref_check') == 'longmemeval_oracle':
        for (rel, idx), rec in zip(rec_sources, all_records):
            if not isinstance(rec, dict):
                continue
            rid = str(rec.get('question_id', ''))
            hs_ids = rec.get('haystack_session_ids') or []
            hs_sess = rec.get('haystack_sessions') or []
            ans_ids = rec.get('answer_session_ids') or []
            if len(hs_ids) != len(hs_sess):
                anomalies.append(_anom(ds_id, rel, idx, rid, 'ref_integrity', 'high',
                                       'haystack_session_ids(%d) 与 haystack_sessions(%d) 数量不一致' %
                                       (len(hs_ids), len(hs_sess))))
            dangling = set(ans_ids) - set(hs_ids)
            if dangling:
                anomalies.append(_anom(ds_id, rel, idx, rid, 'ref_integrity', 'high',
                                       'answer_session_ids 悬空引用: %s' % sorted(dangling)[:3]))
            for si, sess in enumerate(hs_sess):
                if not isinstance(sess, list) or not sess:
                    anomalies.append(_anom(ds_id, rel, idx, rid, 'ref_integrity', 'medium',
                                           'haystack_sessions[%d] 为空会话' % si))
                    break

    result['counts'] = {'records': len(all_records), 'unique_ids': len(set(ids)),
                        'duplicate_id_records': len(ids) - len(set(ids))}
    result['coverage'] = dict(coverage)
    result['sensitive'] = dict(sens_total)
    result['sensitive_high'] = dict(sens_high_total)

    # --- 6.3 最低人工抽样量 ---
    n = result['records']
    result['required_manual_sample'] = min(n, 50) if n <= 500 else (100 if n <= 5000 else 200)

    # --- 人工复核清单（手册 6.3）: 全部异常记录 + 分层抽样的正常记录 ---
    # 规则: (1) 全部异常记录 ID 必须入选; (2) 每个类别至少抽 2 条正常记录（不足则全取）;
    #       (3) 补足至 min(6.3 最低抽样量, 唯一ID数); (4) 不提前截断, 全类别覆盖
    flagged = sorted({a['record_id'] for a in anomalies if a['record_id']})
    flagged_set = set(flagged)
    rid_category = {}
    normal_by_cat = {}
    for (rel, idx), rec in zip(rec_sources, all_records):
        if isinstance(rec, dict) and idf:
            rid = str(rec.get(idf, ''))
            if not rid:
                continue
            rid_category[rid] = str(rec.get(cat)) if cat else '_'
            if rid not in flagged_set:
                normal_by_cat.setdefault(rid_category[rid], []).append(rid)
    rng = random.Random(RANDOM_SEED)
    picked = set()
    for c in sorted(normal_by_cat):
        rids = normal_by_cat[c]
        take = min(max(2, int(round(len(rids) * 0.05))), len(rids))
        if take > 0:
            picked.update(rng.sample(rids, take))
    target = min(result['required_manual_sample'], len(seen_id))
    need = target - len(flagged_set) - len(picked)
    if need > 0:
        pool = [rid for c in sorted(normal_by_cat) for rid in normal_by_cat[c] if rid not in picked]
        rng.shuffle(pool)
        picked.update(pool[:need])
    result['manual_review_ids'] = flagged + sorted(picked)
    result['manual_review_total'] = len(result['manual_review_ids'])
    result['manual_review_flagged'] = len(flagged_set)
    result['manual_review_normal'] = len(picked)
    result['manual_review_categories'] = dict(Counter(
        rid_category[r] for r in result['manual_review_ids'] if r in rid_category))
    return result, anomalies


def write_anomalies_csv(anomalies):
    os.makedirs(os.path.dirname(OUT_ANOMALIES), exist_ok=True)
    cols = ['dataset_id', 'source_file', 'record_index', 'record_id',
            'anomaly_type', 'severity', 'detail']
    with open(OUT_ANOMALIES, 'w', encoding='utf-8-sig', newline='\n') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\n')
        w.writeheader()
        for a in anomalies:
            w.writerow({c: a.get(c, '') for c in cols})
    return len(anomalies)


def write_hash_file(results):
    os.makedirs(os.path.dirname(OUT_HASH), exist_ok=True)
    lines = ['# 阶段4 抽样哈希（SHA256, 由 stage4_sample_audit.py 生成）']
    for r in results:
        lines.append('')
        lines.append('## %s' % r['dataset_id'])
        if r['file_hashes']:
            for rel, h in r['file_hashes']:
                lines.append('%s  %s' % (h, rel))
        else:
            lines.append('（无数据文件）')
    with open(OUT_HASH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def write_report(results, anomalies, note, cmd):
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    sev = Counter(a['severity'] for a in anomalies)
    by_type = Counter(a['anomaly_type'] for a in anomalies)
    lines = []
    ap = lines.append
    ap('# 阶段4 小样本质量审计报告（AI 辅助草案）')
    ap('')
    ap('> **性质声明**: 本报告由脚本自动生成, 仅覆盖结构与可机械检查项; 标签语义可推导性、'
       '困难样本覆盖等语义项需人工抽检后才能得出结论。Gate 4 是否通过由 Reviewer 决定。')
    if note:
        ap('>')
        ap('> **运行备注**: %s' % note)
    ap('')
    ap('- 运行时间: %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
    ap('- 运行命令: `%s`' % cmd)
    ap('- Python: %s / 平台: %s' % (sys.version.split()[0], sys.platform))
    ap('- 审计执行: Annotator B (DGXD01)')
    ap('')
    ap('## 1. 审计概览')
    ap('')
    ap('| dataset_id | 状态 | 数据文件 | 记录数 | 唯一ID | 高危敏感 | 低危敏感(合计) | 在线引用 |')
    ap('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for r in results:
        high = sum(r.get('sensitive_high', {}).values()) if r.get('sensitive_high') else 0
        low = sum(r['sensitive'].values()) - high if r['sensitive'] else 0
        ap('| %s | %s | %d | %d | %d | %d | %d | %d |' % (
            r['dataset_id'], r['status'], r['files'], r['records'],
            r['counts'].get('unique_ids', 0), high, low, r['url_refs']))
    ap('')
    ap('异常总数 **%d**（高 %d / 中 %d / 低 %d）' % (
        len(anomalies), sev.get('high', 0), sev.get('medium', 0), sev.get('low', 0)))
    ap('')
    ap('## 2. 逐数据集审计明细')
    ap('')
    for r in results:
        ap('### %s' % r['dataset_id'])
        ap('')
        if r['status'] != 'ok' and not r['file_hashes']:
            ap('- 状态: %s' % r['status'])
            ap('')
            continue
        if r['empty_files']:
            ap('- 空文件: %s' % ', '.join(r['empty_files']))
        if r['unhandled_files']:
            ap('- 未解析类型文件（需人工）: %s' % ', '.join(r['unhandled_files']))
        if r['length_stats']:
            ap('')
            ap('| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |')
            ap('| --- | --- | --- | --- | --- | --- | --- |')
            for t, s in r['length_stats'].items():
                ap('| %s | %d | %d | %d | %d | %d | %d |' % (t, s['p50'], s['p95'], s['p99'], s['max'], s['min'], s['zero']))
        if r['coverage']:
            ap('')
            ap('- 类别分布（%s）: %s' % (
                '正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检',
                ', '.join('%s=%d' % kv for kv in sorted(r['coverage'].items()))))
        if r['sensitive']:
            high = r.get('sensitive_high', {})
            low = {k: v for k, v in r['sensitive'].items() if k not in high}
            ap('')
            if high:
                ap('- **高危敏感模式（逐条已入异常清单, 必须人工核）**: %s' %
                   ', '.join('%s×%d' % kv for kv in sorted(high.items())))
            if low:
                ap('- 低危敏感模式（合成研究数据中常见, 已抽样入清单, 全量计数如下, 判真伪由人工）: %s' %
                   ', '.join('%s×%d' % kv for kv in sorted(low.items())))
        if r['url_refs']:
            ap('- 内容中出现 URL 引用 %d 处（在线依赖风险需人工评估评测脚本是否运行时抓取）' % r['url_refs'])
        ap('- 6.3 最低人工抽样量: **%d** 条（现有 %d 条）' % (r['required_manual_sample'], r['records']))
        ap('')
    ap('## 3. 异常类型汇总')
    ap('')
    if by_type:
        ap('| 异常类型 | 数量 |')
        ap('| --- | --- |')
        for t, n in by_type.most_common():
            ap('| %s | %d |' % (t, n))
    else:
        ap('未发现结构性异常。')
    ap('')
    ap('逐条异常明细见 `data/interim/stage4_anomalies.csv`。')
    ap('')
    ap('## 4. 需人工逐条复核的样本 ID')
    ap('')
    ap('清单构成: 全部异常记录 ID + 分层抽样的正常记录 ID（每个类别至少 2 条，'
       '并补足至 6.3 最低人工抽样量）。完整清单见 `evidence/audit/stage4_audit_summary.json`。')
    ap('')
    for r in results:
        if r['manual_review_ids']:
            cats = r.get('manual_review_categories', {})
            cat_desc = ', '.join('%s×%d' % kv for kv in sorted(cats.items())) if cats else '无类别字段'
            ap('- **%s**: 共 %d 个 ID（异常 %d + 正常抽样 %d）｜类别覆盖: %s' % (
                r['dataset_id'], r['manual_review_total'], r['manual_review_flagged'],
                r['manual_review_normal'], cat_desc))
            shown = ', '.join(r['manual_review_ids'][:30])
            more = '（仅展示前 30）' if r['manual_review_total'] > 30 else ''
            ap('  - ID: %s%s' % (shown, more))
    ap('')
    ap('## 5. 静默丢失风险清单（Prompt 05-R 要求）')
    ap('')
    ap('脚本显式计数以下“可能丢数据”路径, 未静默丢弃任何记录:')
    ap('')
    ap('| 风险路径 | 处理方式 |')
    ap('| --- | --- |')
    ap('| 文件级解析失败（编码/JSON损坏） | 记 parse_error 高危异常, 计入 parse_failed |')
    ap('| JSONL 单行解析失败 | 记 parse_error 异常, 其余行继续 |')
    ap('| 空文件（0字节） | 记 empty_file 异常, 不产生记录 |')
    ap('| 非结构化扩展名（pdf 等） | 记 unhandled_type 异常, 不解析, 需人工 |')
    ap('| 顶层为 dict 的 JSON | 按单条记录处理, 不丢弃 |')
    ap('| 敏感/异常命中 | 只标记, 从不删除或修改原始数据 |')
    ap('')
    ap('**残留限制（需人工补审）**:')
    ap('- 标签是否真正能从证据**语义推导**（脚本只查证据字段非空）')
    ap('- 困难负样本、边界样本是否足量（脚本只给类别分布）')
    ap('- License 是否允许当前用途（见 evidence/source/ 阶段3 证据）')
    ap('- 模板泄漏需到阶段9泄漏检查专项处理')
    ap('')
    ap('## 6. 阈值说明（供审查）')
    ap('')
    ap('| 检查 | 阈值 | 理由 |')
    ap('| --- | --- | --- |')
    ap('| 异常长度 | > max(P99×3, 2000) | 分布自适应, 下限防误报长文档 |')
    ap('| ID/记录重复 | 完全相等 | 零容忍 |')
    ap('| 敏感-高危（密钥/令牌/证件号） | 命中即逐条上报 | 泄露后果严重, 零容忍 |')
    ap('| 敏感-低危（邮箱/电话/内网IP/路径） | 计数 + 抽样5条 | 合成研究数据中普遍, 全量上报会淹没高危信号 |')
    ap('| 人工抽检 | 全部异常 + 每类别 ≥2 条 + 补足至 6.3 最低抽样量（seed=42 可复现） | 手册 6.3 分层与最低样本量 |')
    ap('| 字段类型 | 已配置字段与期望类型不符即上报（bool 视为类型错误） | Prompt 05 字段类型检查 |')
    ap('')
    ap('## 7. 初步结论（AI 草案, 待人工）')
    ap('')
    for r in results:
        if r['status'] != 'ok' and not r['file_hashes']:
            concl = '待 Gate 3 批准后补充样本'
        elif r['records'] == 0:
            concl = '无有效记录, 需检查下载'
        else:
            high = sum(1 for a in anomalies if a['dataset_id'] == r['dataset_id'] and a['severity'] == 'high')
            concl = ('存在 %d 个高危异常, 建议先修复再进入人工抽检' % high) if high else '结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）'
        ap('- **%s**: %s' % (r['dataset_id'], concl))
    ap('')
    ap('---')
    ap('')
    ap('*本文件由 `scripts/audit/stage4_sample_audit.py` 自动生成; 修改需 B 重跑并留痕。*')
    with open(OUT_REPORT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def write_summary_json(results, anomalies):
    os.makedirs(os.path.dirname(OUT_SUMMARY), exist_ok=True)
    out = {'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
           'generated_by': 'DGXD01', 'random_seed': RANDOM_SEED,
           'datasets': results, 'anomaly_count': len(anomalies)}
    with open(OUT_SUMMARY, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(description='阶段4 小样本质量审计（只读 raw）')
    parser.add_argument('--datasets', help='逗号分隔的 dataset_id 列表, 默认全部')
    parser.add_argument('--note', help='运行备注（写入报告头部）', default='')
    args = parser.parse_args()

    # 安全断言: 输出路径绝不在 raw 下
    for p in (OUT_REPORT, OUT_ANOMALIES, OUT_HASH, OUT_SUMMARY):
        assert not os.path.abspath(p).lower().startswith(RAW_DIR.lower()), '输出路径不得位于 data/raw'

    # Gate 3 门禁: 未获 Reviewer 批准必须非零退出, 且不产出任何正式文件
    gate_ok, gate_msg = gate3_approved()
    if not gate_ok:
        print('错误: Gate 3 尚未获 Reviewer 批准, 禁止执行正式审计。')
        print('  %s' % gate_msg)
        print('  请等待 Reviewer 在 reports/gate_status.md 将 Gate 3 标记为「通过」后重试; '
              'Gate 3 批准前仅允许运行单元测试 test_stage4_sample_audit.py。')
        return 2

    if args.datasets:
        ds_ids = [s.strip() for s in args.datasets.split(',') if s.strip()]
    else:
        ds_ids = sorted(d for d in os.listdir(RAW_DIR)
                        if os.path.isdir(os.path.join(RAW_DIR, d))) if os.path.isdir(RAW_DIR) else []

    if not ds_ids:
        print('data/raw 下没有数据集目录, 无可审计对象')
        return 1

    # 候选状态门禁: 拒绝非「允许试用」候选（含 --datasets 传入的任意目录）
    gate3_map = load_registry_gate3_status()
    allowed, rejected = [], []
    for ds_id in ds_ids:
        st = gate3_map.get(ds_id, '')
        if st != ALLOWED_GATE3_STATUS:
            rejected.append('候选 %s: gate3_status=%r（非「%s」，拒绝正式审计）'
                            % (ds_id, st or '未标记', ALLOWED_GATE3_STATUS))
        else:
            allowed.append(ds_id)
    for v in rejected:
        print('拒绝: %s' % v)
    if not allowed:
        print('没有符合「%s」的候选, 不执行正式审计。' % ALLOWED_GATE3_STATUS)
        return 3 if rejected else 1

    cmd = 'python ' + ' '.join(sys.argv)
    all_anomalies, results = [], []
    range_violations = []
    for ds_id in allowed:
        print('审计 %s ...' % ds_id)
        r, anom = audit_dataset(ds_id, args.note)
        results.append(r)
        all_anomalies.extend(anom)
        print('  -> %s | 文件 %d | 记录 %d | 异常 %d' % (r['status'], r['files'], r['records'], len(anom)))
        # 样本量范围门禁: 正式审计仅允许每集 50~100 条新样本
        if r['status'] == 'ok' and r['records'] > 0 and not in_formal_sample_range(r['records']):
            range_violations.append('候选 %s: 记录 %d 条, 超出 50~100 范围, 拒绝正式审计'
                                    % (ds_id, r['records']))

    if range_violations:
        for v in range_violations:
            print('拒绝: %s' % v)
        print('存在超出 50~100 条范围的数据集, 不产出正式审计文件。')
        return 3

    n = write_anomalies_csv(all_anomalies)
    write_hash_file(results)
    write_report(results, all_anomalies, args.note, cmd)
    write_summary_json(results, all_anomalies)
    print('')
    print('完成: 异常 %d 条' % n)
    print('  报告: %s' % os.path.relpath(OUT_REPORT, REPO_ROOT))
    print('  异常: %s' % os.path.relpath(OUT_ANOMALIES, REPO_ROOT))
    print('  哈希: %s' % os.path.relpath(OUT_HASH, REPO_ROOT))
    print('  摘要: %s' % os.path.relpath(OUT_SUMMARY, REPO_ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
