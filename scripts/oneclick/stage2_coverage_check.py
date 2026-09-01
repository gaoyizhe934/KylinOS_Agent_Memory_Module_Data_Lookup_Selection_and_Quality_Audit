# -*- coding: utf-8 -*-
"""阶段 2: 候选覆盖检查（Gate 2 快速验证）。

依据手册 3.4 候选搜索停止条件与 v2.0 重建计划阶段 2 要求：
1. 六类任务每类至少 2 个正式候选（方法论/结构参考不计入候选数）；
2. Gate 2 登记完整性：每个数据集有正式名称、版本线索、官方来源、
   任务说明，以及数据入口（data_url）。

只读本地 registry/dataset_registry.csv，不访问网络，可随时复跑。
与 URL 可访问性检查的分工：本脚本只验证登记完整性（data_url 已填写）；
可访问性由 stage2_check_urls.py 以网络请求验证并按失败条件退出。

退出码: 覆盖达标且无 ❌缺失 字段为 0，否则为 1。
"""
import argparse
import csv
import os
import sys

from net_utils import setup_stdout_utf8

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TASK_CATEGORIES = [
    ('偏好提取', ['偏好']),
    ('知识检索', ['检索']),
    ('冲突处理', ['冲突']),
    ('精准遗忘', ['遗忘']),
    ('Tool Result', ['tool result', 'tool']),
    ('端到端会话', ['端到端']),
]

REFERENCE_ONLY_KEYWORDS = ['方法论参考', '结构参考']

PENDING_KEYWORDS = ['待核验', '待人工', '待确认']


def load_registry(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def is_reference_only(row):
    """结论为方法论参考/结构参考的数据集不作为任务候选计数。"""
    conclusion = (row.get('conclusion') or '')
    return any(k in conclusion for k in REFERENCE_ONLY_KEYWORDS)


def match_categories(task):
    task_l = (task or '').lower()
    return [cat for cat, keywords in TASK_CATEGORIES if any(k.lower() in task_l for k in keywords)]


def field_status(value):
    """登记字段状态: ❌缺失 / ⚠️待核验 / ✅。"""
    v = (value or '').strip()
    if not v:
        return '❌缺失'
    if any(k in v for k in PENDING_KEYWORDS) and len(v) <= 20:
        return '⚠️待核验'
    return '✅'


def main():
    parser = argparse.ArgumentParser(description='六类任务候选覆盖检查（Gate 2 快速验证）')
    parser.add_argument('--registry', default=os.path.join(REPO_ROOT, 'registry', 'dataset_registry.csv'),
                        help='登记表路径（默认: 仓库根目录下 registry/dataset_registry.csv）')
    parser.add_argument('--min-candidates', type=int, default=2,
                        help='每类任务最少正式候选数（默认 2，依据手册 3.4）')
    args = parser.parse_args()

    setup_stdout_utf8()
    rows = load_registry(args.registry)
    print('========== 阶段 2 候选覆盖检查（Gate 2 快速验证）==========')
    print(f'登记表: {os.path.relpath(args.registry, REPO_ROOT)}')
    print(f'登记数据集总数: {len(rows)}')
    print()

    # 按六类任务归类
    by_category = {cat: {'candidates': [], 'references': []} for cat, _ in TASK_CATEGORIES}
    unclassified = []
    for row in rows:
        cats = match_categories(row.get('task'))
        if not cats:
            unclassified.append(row['dataset_id'])
            continue
        bucket = 'references' if is_reference_only(row) else 'candidates'
        for cat in cats:
            by_category[cat][bucket].append(row['dataset_id'])

    print('## 一、六类任务候选覆盖')
    print()
    print('| 任务类型 | 正式候选数 | 达标 | 候选数据集 | 另含参考类（不计入） |')
    print('| --- | --- | --- | --- | --- |')
    all_pass = True
    for cat, _ in TASK_CATEGORIES:
        entry = by_category[cat]
        n = len(entry['candidates'])
        ok = n >= args.min_candidates
        all_pass = all_pass and ok
        mark = '✅' if ok else '❌'
        refs = ', '.join(entry['references']) if entry['references'] else '—'
        cands = ', '.join(entry['candidates'])
        print(f'| {cat} | {n} | {mark} | {cands} | {refs} |')

    print()
    print(f'覆盖标准: 每类任务 >= {args.min_candidates} 个正式候选（方法论/结构参考不计入）')
    print(f'覆盖结论: {"达标" if all_pass else "不达标"}')
    if unclassified:
        print(f'未归入六类任务的登记项（参考类）: {", ".join(unclassified)}')
    print()

    # Gate 2 登记完整性
    print('## 二、Gate 2 登记完整性（正式名称/版本线索/官方来源/任务说明/数据入口）')
    print()
    print('| 数据集 | 正式名称 | 版本线索 | 官方来源 | 任务说明 | 数据入口 | 定位 |')
    print('| --- | --- | --- | --- | --- | --- | --- |')
    pending_items = []
    missing_items = []
    for row in rows:
        did = row['dataset_id']
        statuses = {
            'formal_name': field_status(row.get('formal_name')),
            'version': field_status(row.get('version')),
            'official_url': field_status(row.get('official_url')),
            'task': field_status(row.get('task')),
            'data_url': field_status(row.get('data_url')),
        }
        for field, st in statuses.items():
            if st == '❌缺失':
                missing_items.append(f'{did}.{field}')
            elif st != '✅':
                pending_items.append(f'{did}.{field}={st}')
        print(f'| {did} | {statuses["formal_name"]} | {statuses["version"]} | '
              f'{statuses["official_url"]} | {statuses["task"]} | {statuses["data_url"]} | '
              f'{row.get("conclusion", "")} |')

    print()
    if missing_items:
        print(f'❌缺失字段（阻塞项，须补齐后重跑本命令）: {"; ".join(missing_items)}')
    if pending_items:
        print(f'待人工核验项（不阻塞覆盖结论，Gate 2 批准前需 Reviewer 确认）: {"; ".join(pending_items)}')
    if not missing_items and not pending_items:
        print('登记完整性: 全部字段齐备')
    integrity_pass = not missing_items
    print()
    print(f'总体结论: 覆盖{"达标" if all_pass else "不达标"}；登记完整性{"通过" if integrity_pass else "不通过"}；'
          f'Gate 2 最终状态待 Reviewer 批准。')
    print('数据入口可访问性验证: python scripts/oneclick/stage2_check_urls.py（按失败条件退出）')
    sys.exit(0 if (all_pass and integrity_pass) else 1)


if __name__ == '__main__':
    main()
