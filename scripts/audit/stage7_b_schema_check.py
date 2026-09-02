#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段 7 B 侧 Schema 校验：必填字段 + timestamp + raw_id 溯源 + 行数对账 + enum 字典

用法: python scripts/audit/stage7_b_schema_check.py
"""
import glob
import json
import os
import sys
import io
from datetime import datetime
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(REPO_ROOT, 'data', 'processed')

SCHEMA_REQUIRED = [
    "sample_id", "dataset_version", "task_type", "language",
    "user_id", "conversation_id", "timestamp", "input", "gold",
    "evidence", "source", "template_family", "annotator_a",
    "annotator_b", "review_status",
]

EXPECTED_COUNTS = {
    "conflict_resolution.jsonl": 40,
    "end_to_end_session.jsonl": 15,
    "knowledge_retrieval.jsonl": 60,
    "knowledge_retrieval_t2ranking.jsonl": 200,
    "multiwoz_dialogues_sample.jsonl": 200,
    "multiwoz_public_sample.jsonl": 100,
    "precise_forgetting.jsonl": 40,
    "preference_extraction.jsonl": 60,
}

EXPECTED_TOTAL = sum(EXPECTED_COUNTS.values())


def valid_ts(ts):
    if not ts or not isinstance(ts, str):
        return False
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def main():
    now = datetime.now().isoformat(timespec='seconds')
    print(f'========== 阶段 7 B 侧 Schema 校验 ({now}) ==========')
    print()

    issues = {
        'missing_field': [],
        'invalid_ts': [],
        'missing_raw_id_public': [],
        'missing_source_file': [],
        'missing_source_version': [],
        'row_count_mismatch': [],
        'tool_result_exists': [],
    }
    total = 0
    file_counts = {}
    task_types = Counter()
    sources = Counter()
    template_families = Counter()
    review_statuses = Counter()
    ts_3digit = []

    # 检查 tool_result.jsonl 是否已删除
    tool_result_path = os.path.join(PROCESSED, 'tool_result.jsonl')
    if os.path.exists(tool_result_path):
        issues['tool_result_exists'].append('tool_result.jsonl 仍存在（应已删除）')
    else:
        print('✅ tool_result.jsonl 已删除')
    print()

    # 遍历所有 JSONL 文件
    for path in sorted(glob.glob(os.path.join(PROCESSED, '*.jsonl'))):
        fname = os.path.basename(path)
        count = 0
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                count += 1
                total += 1
                r = json.loads(line)
                sid = r.get('sample_id', f'{fname}:{count}')

                # 必填字段检查
                for f in SCHEMA_REQUIRED:
                    if f not in r:
                        issues['missing_field'].append(f'{sid}:{f}')

                # timestamp 合法性
                ts = r.get('timestamp')
                if not valid_ts(ts):
                    issues['invalid_ts'].append(f'{sid}:{ts}')

                # 检查 3 位日期残留
                if isinstance(ts, str) and len(ts) >= 14:
                    day_part = ts[8:11] if len(ts) > 10 else ''
                    if day_part and day_part[0] == '-' and day_part[1:].isdigit() and len(day_part[1:]) == 3:
                        ts_3digit.append(f'{sid}:{ts}')

                # raw_id 溯源（public_derived）
                src = r.get('source', '')
                if src == 'public_derived' and not r.get('raw_id'):
                    issues['missing_raw_id_public'].append(sid)

                # source_file / source_version
                if not r.get('source_file'):
                    issues['missing_source_file'].append(sid)
                if not r.get('source_version'):
                    issues['missing_source_version'].append(sid)

                # 枚举统计
                task_types[r.get('task_type', 'unknown')] += 1
                sources[src] += 1
                template_families[r.get('template_family', 'unknown')] += 1
                review_statuses[r.get('review_status', 'unknown')] += 1

        file_counts[fname] = count

        # 行数对账
        expected = EXPECTED_COUNTS.get(fname)
        if expected is not None and count != expected:
            issues['row_count_mismatch'].append(f'{fname}: 实际 {count} vs 预期 {expected}')
            print(f'  ⚠️ {fname}: {count} 行（预期 {expected}）')
        else:
            print(f'  ✅ {fname}: {count} 行')

    print()
    print(f'总记录数: {total}（预期 {EXPECTED_TOTAL}）')
    if total != EXPECTED_TOTAL:
        issues['row_count_mismatch'].append(f'总计: 实际 {total} vs 预期 {EXPECTED_TOTAL}')
    print()

    # enum_dictionary.json 校验
    print('--- enum_dictionary.json 校验 ---')
    enum_path = os.path.join(PROCESSED, 'enum_dictionary.json')
    if os.path.exists(enum_path):
        with open(enum_path, encoding='utf-8') as f:
            enum_data = json.load(f)
        enum_task_types = set(enum_data.get('enum', {}).get('task_type', []))
        actual_task_types = set(task_types.keys())
        if enum_task_types == actual_task_types:
            print(f'  ✅ task_type 枚举一致: {sorted(enum_task_types)}')
        else:
            print(f'  ⚠️ task_type 不一致: enum={sorted(enum_task_types)} actual={sorted(actual_task_types)}')

        enum_sources = set(enum_data.get('enum', {}).get('source', []))
        actual_sources = set(sources.keys())
        if enum_sources == actual_sources:
            print(f'  ✅ source 枚举一致: {sorted(enum_sources)}')
        else:
            print(f'  ⚠️ source 不一致: enum={sorted(enum_sources)} actual={sorted(actual_sources)}')

        enum_tf = set(enum_data.get('enum', {}).get('template_family', []))
        actual_tf = set(template_families.keys())
        if enum_tf == actual_tf:
            print(f'  ✅ template_family 枚举一致 ({len(enum_tf)} 个)')
        else:
            print(f'  ⚠️ template_family 不一致: enum_only={sorted(enum_tf - actual_tf)} actual_only={sorted(actual_tf - enum_tf)}')

        tf_dist = enum_data.get('template_family_distribution', {})
        mismatch = False
        for tf, count in tf_dist.items():
            if template_families.get(tf, 0) != count:
                print(f'  ⚠️ template_family 分布不一致: {tf} enum={count} actual={template_families.get(tf, 0)}')
                mismatch = True
        if not mismatch:
            print(f'  ✅ template_family 分布一致')
    else:
        print('  ⚠️ enum_dictionary.json 不存在')
    print()

    # 3 位日期残留检查
    print('--- timestamp 3 位日期残留检查 ---')
    if ts_3digit:
        print(f'  ⚠️ 发现 {len(ts_3digit)} 条 3 位日期残留:')
        for item in ts_3digit[:5]:
            print(f'    {item}')
        issues['invalid_ts'].extend(ts_3digit)
    else:
        print('  ✅ 无 3 位日期残留')
    print()

    # 汇总
    print('--- 校验汇总 ---')
    all_ok = True
    for category, items in issues.items():
        if items:
            print(f'  ❌ {category}: {len(items)} 项')
            for item in items[:3]:
                print(f'      {item}')
            if len(items) > 3:
                print(f'      ... 共 {len(items)} 项')
            all_ok = False
        else:
            print(f'  ✅ {category}: 0')

    print()
    print(f'结论: {"✅ 全部通过" if all_ok else "⚠️ 存在需关注项"}')
    print(f'总进度: {total}/{EXPECTED_TOTAL} 条记录校验完成')


if __name__ == '__main__':
    main()
