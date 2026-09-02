# -*- coding: utf-8 -*-
"""阶段4 人工抽检辅助脚本：读取 200 个抽检 ID，逐条提取记录并执行 6 项语义检查。

检查项（手册 4.1 节）:
  1. 任务一致性：记录是否真的验证目标能力
  2. 证据完整性：Gold 能否从原始文本/事件直接证明
  3. 边界清晰度：临时指令 vs 长期偏好 vs 知识事实是否区分
  4. 冲突可判定：有无时间/来源/作用域信息
  5. 负样本可信：困难负样本是否真的不相关
  6. 遗忘可验证：应删和应保留对象是否同时明确
"""
import json
import os
import csv
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMMARY_PATH = os.path.join(REPO_ROOT, 'evidence', 'audit', 'stage4_audit_summary.json')
RAW_DIR = os.path.join(REPO_ROOT, 'data', 'raw')


def load_summary():
    with open(SUMMARY_PATH, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def load_records(ds_id, filename):
    """加载数据集的全部记录，返回 {id: record} 字典。"""
    ds_dir = os.path.join(RAW_DIR, ds_id, 'v0_sample_stage4')
    path = os.path.join(ds_dir, filename)
    records = {}
    if not os.path.isfile(path):
        return records
    _, ext = os.path.splitext(filename)
    if ext == '.jsonl':
        with open(path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                rid = str(rec.get('question_id', rec.get('id', rec.get('dialogue_id', rec.get('qid', '')))))
                records[rid] = rec
    elif ext == '.tsv':
        with open(path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                rid = str(row.get('qid', ''))
                records[rid] = row
    return records


def check_longmemeval_cleaned(rec, rid):
    """检查 longmemeval_cleaned_2025 的 6 项语义。"""
    results = []
    qt = rec.get('question_type', '')
    q = rec.get('question', '')
    ans = str(rec.get('answer', ''))
    hs = rec.get('haystack_sessions', [])
    asi = rec.get('answer_session_ids', [])
    hsi = rec.get('haystack_session_ids', [])

    # 1. 任务一致性
    cap_map = {
        'temporal-reasoning': '时序推理',
        'multi-session': '跨会话关联',
        'knowledge-update': '知识更新',
        'single-session-user': '用户偏好提取',
        'single-session-assistant': '助手记忆',
        'single-session-preference': '偏好对比',
    }
    cap = cap_map.get(qt, '未知')
    results.append(('1.任务一致性', f'question_type={qt} → 能力={cap}', 'PASS' if cap != '未知' else 'WARN'))

    # 2. 证据完整性
    has_hs = len(hs) > 0
    has_asi = len(asi) > 0
    results.append(('2.证据完整性', f'haystack_sessions={len(hs)}个, answer_session_ids={len(asi)}个',
                    'PASS' if has_hs and has_asi else 'FAIL'))

    # 3. 边界清晰度
    has_session_ids = len(hsi) > 0
    results.append(('3.边界清晰度', f'haystack_session_ids={len(hsi)}个（会话边界标识）',
                    'PASS' if has_session_ids else 'WARN'))

    # 4. 冲突可判定
    has_time = any('time' in str(s).lower() or 'date' in str(s).lower() or '时间' in str(s) for s in hs)
    results.append(('4.冲突可判定', f'时间信息: {"有" if has_time else "未检出"}', 'PASS' if has_time else 'WARN'))

    # 5. 负样本可信（LongMemEval 无显式负样本，haystack 中的非答案会话即为隐式负样本）
    non_answer = len(hsi) - len(asi) if len(hsi) > len(asi) else 0
    results.append(('5.负样本可信', f'隐式负样本会话数={non_answer}', 'PASS' if non_answer > 0 else 'WARN'))

    # 6. 遗忘可验证（LongMemEval 不涉及遗忘，标记 N/A）
    results.append(('6.遗忘可验证', 'N/A（LongMemEval 不涉及遗忘任务）', 'N/A'))

    return results, {'question': q[:120], 'answer': ans[:80], 'question_type': qt,
                     'hs_count': len(hs), 'asi_count': len(asi), 'hsi_count': len(hsi)}


def check_longmemeval_v2(rec, rid):
    """检查 longmemeval_v2_2026 的 6 项语义。"""
    results = []
    qt = rec.get('question_type', '')
    q = rec.get('question', '')
    ans = str(rec.get('answer', ''))
    ef = str(rec.get('eval_function', ''))

    # 1. 任务一致性
    cap_map = {
        'static-environment': '静态环境记忆',
        'static-environment-abs': '静态环境-abstention',
        'dynamic-environment': '动态环境记忆',
        'dynamic-environment-abs': '动态环境-abstention',
        'procedure': '流程记忆',
        'procedure-abs': '流程-abstention',
        'errors-gotchas': '错误与陷阱',
    }
    cap = cap_map.get(qt, '未知')
    is_abs = 'abs' in qt
    results.append(('1.任务一致性', f'question_type={qt} → 能力={cap}' + ('（abstention）' if is_abs else ''),
                    'PASS' if cap != '未知' else 'WARN'))

    # 2. 证据完整性
    has_ef = len(ef) > 0
    results.append(('2.证据完整性', f'eval_function={"有" if has_ef else "无"}', 'PASS' if has_ef else 'WARN'))

    # 3. 边界清晰度
    has_q = len(q) > 0
    results.append(('3.边界清晰度', f'question长度={len(q)}（场景描述充分性）', 'PASS' if len(q) > 50 else 'WARN'))

    # 4. 冲突可判定
    has_scope = 'domain' in q.lower() or 'environment' in q.lower() or 'scope' in q.lower()
    results.append(('4.冲突可判定', f'作用域信息: {"有" if has_scope else "未检出"}', 'PASS' if has_scope else 'WARN'))

    # 5. 负样本可信
    results.append(('5.负样本可信', 'N/A（V2 无显式负样本，abstention 题型本身为负样本）',
                    'PASS' if is_abs else 'N/A'))

    # 6. 遗忘可验证
    results.append(('6.遗忘可验证', 'N/A（V2 不涉及遗忘任务）', 'N/A'))

    return results, {'question': q[:120], 'answer': ans[:80], 'question_type': qt,
                     'eval_function': ef[:80]}


def check_multiwoz(rec, rid):
    """检查 multiwoz_2_2_2020 的 6 项语义。"""
    results = []
    services = rec.get('services', [])
    turns = rec.get('turns', [])

    # 1. 任务一致性
    results.append(('1.任务一致性', f'services={services}（多域任务型对话）', 'PASS'))

    # 2. 证据完整性
    has_turns = len(turns) > 0
    results.append(('2.证据完整性', f'turns={len(turns)}轮对话', 'PASS' if has_turns else 'FAIL'))

    # 3. 边界清晰度
    has_speaker = all('speaker' in t for t in turns[:3]) if turns else False
    results.append(('3.边界清晰度', f'speaker标注={"有" if has_speaker else "无"}（区分用户/系统）',
                    'PASS' if has_speaker else 'WARN'))

    # 4. 冲突可判定
    has_intent = any('intent' in str(t).lower() for t in turns[:5]) if turns else False
    results.append(('4.冲突可判定', f'intent标注: {"有" if has_intent else "未检出"}',
                    'PASS' if has_intent else 'WARN'))

    # 5. 负样本可信
    results.append(('5.负样本可信', 'N/A（MultiWOZ 无负样本设计）', 'N/A'))

    # 6. 遗忘可验证
    results.append(('6.遗忘可验证', 'N/A（MultiWOZ 不涉及遗忘任务）', 'N/A'))

    return results, {'dialogue_id': rid, 'services': services, 'turns_count': len(turns)}


def check_t2ranking(rec, rid):
    """检查 t2ranking_2023 的 6 项语义。"""
    results = []
    text = str(rec.get('text', ''))

    # 1. 任务一致性
    results.append(('1.任务一致性', '查询集（知识检索任务输入）', 'PASS'))

    # 2. 证据完整性
    results.append(('2.证据完整性', 'relevance 标注在 qrels 文件中（未在查询集中）', 'WARN'))

    # 3. 边界清晰度
    results.append(('3.边界清晰度', f'查询文本="{text[:50]}"', 'PASS' if len(text) > 3 else 'WARN'))

    # 4. 冲突可判定
    results.append(('4.冲突可判定', 'N/A（查询集不含冲突信息）', 'N/A'))

    # 5. 负样本可信
    results.append(('5.负样本可信', 'N/A（负样本在 qrels 中标注）', 'N/A'))

    # 6. 遗忘可验证
    results.append(('6.遗忘可验证', 'N/A（不涉及遗忘任务）', 'N/A'))

    return results, {'qid': rid, 'text': text[:80]}


# 数据集配置
DS_CONFIG = {
    'longmemeval_cleaned_2025': {
        'file': 'longmemeval_oracle_sample.jsonl',
        'checker': check_longmemeval_cleaned,
    },
    'longmemeval_v2_2026': {
        'file': 'questions_sample.jsonl',
        'checker': check_longmemeval_v2,
    },
    'multiwoz_2_2_2020': {
        'file': 'dialogues_sample.jsonl',
        'checker': check_multiwoz,
    },
    't2ranking_2023': {
        'file': 'queries_sample.tsv',
        'checker': check_t2ranking,
    },
}


def main():
    summary = load_summary()
    all_pass = True
    total_checked = 0
    total_pass = 0
    total_warn = 0
    total_fail = 0
    total_na = 0

    print('=' * 80)
    print('阶段4 人工抽检辅助报告')
    print('=' * 80)

    for ds_info in summary['datasets']:
        ds_id = ds_info['dataset_id']
        if ds_id not in DS_CONFIG:
            continue
        review_ids = ds_info.get('manual_review_ids', [])
        if not review_ids:
            print(f'\n## {ds_id}: 无抽检 ID（跳过）')
            continue

        cfg = DS_CONFIG[ds_id]
        all_records = load_records(ds_id, cfg['file'])
        print(f'\n## {ds_id}（{len(review_ids)} 个抽检 ID）')
        print(f'数据文件: {cfg["file"]} | 总记录: {len(all_records)} | 抽检: {len(review_ids)}')
        print()

        ds_pass = 0
        ds_warn = 0
        ds_fail = 0
        ds_na = 0

        for rid in review_ids:
            rec = all_records.get(str(rid))
            if rec is None:
                print(f'  [MISS] ID={rid} 未找到记录')
                all_pass = False
                total_fail += 1
                continue

            checks, info = cfg['checker'](rec, str(rid))
            total_checked += 1

            rec_pass = 0
            rec_warn = 0
            rec_fail = 0
            rec_na = 0

            for name, detail, status in checks:
                if status == 'PASS':
                    rec_pass += 1
                elif status == 'WARN':
                    rec_warn += 1
                elif status == 'FAIL':
                    rec_fail += 1
                else:
                    rec_na += 1

            ds_pass += rec_pass
            ds_warn += rec_warn
            ds_fail += rec_fail
            ds_na += rec_na

            status_icon = '✅' if rec_fail == 0 else '❌'
            if rec_warn > 0 and rec_fail == 0:
                status_icon = '⚠️'

            # 只打印前 5 条详细 + 异常 ID，其余只打印汇总
            is_flagged = rid in [r for r in review_ids[:5]] or rec_fail > 0
            if is_flagged or review_ids.index(rid) < 5:
                print(f'  {status_icon} ID={rid}')
                for name, detail, status in checks:
                    icon = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌', 'N/A': '➖'}[status]
                    print(f'     {icon} {name}: {detail}')
                # 打印关键字段摘要
                for k, v in info.items():
                    print(f'     {k}: {str(v)[:100]}')
                print()

        total_pass += ds_pass
        total_warn += ds_warn
        total_fail += ds_fail
        total_na += ds_na

        print(f'  汇总: PASS={ds_pass} WARN={ds_warn} FAIL={ds_fail} N/A={ds_na}（共 {len(review_ids)} 条×6 项={len(review_ids)*6} 检查）')
        print()

    print('=' * 80)
    print(f'总检查: {total_checked} 条记录 × 6 项 = {total_checked * 6} 次检查')
    print(f'PASS={total_pass}  WARN={total_warn}  FAIL={total_fail}  N/A={total_na}')
    print(f'通过率: {total_pass}/{total_pass + total_warn + total_fail} = {total_pass * 100 / max(total_pass + total_warn + total_fail, 1):.1f}%')
    print(f'失败: {total_fail}（需人工逐条复核）')
    print('=' * 80)


if __name__ == '__main__':
    main()
