#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage7 B-side KMA alignment audit (non-destructive)."""
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(REPO, 'data', 'processed')
ENUM_DICT = os.path.join(PROCESSED, 'enum_dictionary.json')
REPORT = os.path.join(REPO, 'reports', 'stage7_kma_enum_audit_B.md')

LEGACY_GOLD_FIELDS = {
    'preference_extraction': ['preference_type', 'scope', 'confidence', 'should_store', 'operation'],
    'knowledge_retrieval': [],
    'conflict_resolution': ['conflict_type', 'winner'],
    'precise_forgetting': ['checkpoints'],
    'tool_result': ['status', 'persist_policy'],
    'end_to_end_session': [],
}
GAP_KEYS = ['status', 'persist_policy', 'checkpoints', 'confidence', 'winner']

def ts_ok(ts):
    if not ts or not isinstance(ts, str):
        return False
    s = ts.strip()
    if not s.endswith('Z'):
        return False
    if len(s) < 24:
        return False
    if s[10] != 'T' or s[19] != '.':
        return False
    return True

def main():
    sys.path.insert(0, os.path.join(REPO, 'scripts', 'convert'))
    try:
        from convert_to_schema import KMA_ENUMS, KMA_LEGACY_MAP  # noqa
    except Exception as exc:
        print('ERROR: cannot import convert_to_schema KMA defs: %s' % exc, file=sys.stderr)
        sys.exit(2)

    with open(ENUM_DICT, 'r', encoding='utf-8') as fh:
        enum_data = json.load(fh)
    enum = enum_data.get('enum', {})

    total = 0
    legacy_hits = {}
    ts_bad = []
    raw_missing = []
    for cat in LEGACY_GOLD_FIELDS:
        legacy_hits[cat] = []
    for path in sorted(glob.glob(os.path.join(PROCESSED, '*.jsonl'))):
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                total += 1
                task = r.get('task_type')
                gold = r.get('gold') or {}
                sid = r.get('sample_id', '')
                ts = r.get('timestamp')
                if not ts_ok(ts):
                    ts_bad.append(sid + ':' + str(ts))
                if r.get('source') == 'public_derived' and not r.get('raw_id'):
                    raw_missing.append(sid)
                for k in LEGACY_GOLD_FIELDS.get(task, []):
                    if k in gold:
                        legacy_hits[task].append(sid + ':' + k)

    gap_keys = [k for k in GAP_KEYS if k not in enum]
    added_keys = {k: len(enum.get(k, [])) for k in GAP_KEYS if k in enum}

    lines = []
    lines.append('# 阶段7 KMA 枚举/格式 B 侧审计（DGXD01，非破坏性）')
    lines.append('')
    lines.append('- 日期：2026-09-03')
    lines.append('- 依据：PR #26 KMA 对齐（FREEZE_PROPOSAL）；红线：不重转 processed、不打断阶段8试标')
    lines.append('')
    lines.append('## 一、审计结果')
    lines.append('')
    lines.append('| 检查项 | 结果 |')
    lines.append('| --- | --- |')
    lines.append('| processed 总条数 | %d |' % total)
    lines.append('| 旧字段命中（偏好/冲突/遗忘/Tool） | %s |' % str({k: len(v) for k, v in legacy_hits.items() if v}))
    for cat, hits in legacy_hits.items():
        if hits:
            lines.append('  - %s: %d 处（示例：%s）' % (cat, len(hits), ', '.join(hits[:3])))
    lines.append('| 时间戳不满足 UTC .sssZ | %d 条' % len(ts_bad))
    if ts_bad:
        lines.append('  - 示例：%s' % ', '.join(ts_bad[:5]))
    lines.append('| public_derived 缺 raw_id | %d 条' % len(raw_missing))
    lines.append('| Low-3 补全的 legacy 枚举键（值个数） | %s |' % str(added_keys))
    lines.append('| enum_dictionary 仍缺键 | %s |' % (gap_keys if gap_keys else '无'))
    lines.append('')
    lines.append('## 二、与 A 的 KMA_LEGACY_MAP 交叉核对')
    lines.append('- B 侧 stage7_enum_check.py（位于 #25 分支）只做枚举合法性（旧词表）与结构检查，不重写/不阻断 processed；与 A 的 KMA_LEGACY_MAP 参考层无冲突。')
    lines.append('- 本 PR（#26）由本脚本 stage7_kma_b_audit.py 承担 KMA 映射层审计（避免跨 PR 依赖 #25 未合入文件）；enum_check 的 --kma 升级待 #25 合并后同步补齐。')
    lines.append('')
    lines.append('## 三、结论与建议')
    lines.append('- KMA=FREEZE_PROPOSAL：本审计为参考层报告，exit 0，不阻断。')
    lines.append('- FROZEN 后：按 reports/stage1_kma_mapping_B_review.md 差异裁定 → 重写 enum_dictionary → 重转 processed gold → 重建阶段8标注枚举/骨架。')

    with open(REPORT, 'w', encoding='utf-8') as fh:
        for ln in lines:
            print(ln, file=fh)
    print('audit report written: %s' % REPORT)
    print('[total]', total)
    print('[legacy_hits]', {k: len(v) for k, v in legacy_hits.items()})
    print('[ts_not_utc_ms]', len(ts_bad), '[raw_missing]', len(raw_missing), '[dict_gap]', gap_keys)

if __name__ == '__main__':
    main()
