# -*- coding: utf-8 -*-
"""更新 dataset_registry.csv 中的 License 状态"""
import sys, io, csv, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'registry', 'dataset_registry.csv')

rows = []
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        did = row['dataset_id']
        # 更新 T2Ranking
        if did == 't2ranking_2023':
            row['license'] = 'Apache-2.0（HF Data Card 已确认，License 原文已存档）'
            row['allowed_uses'] = '研究、修改、内部演示、公开展示、再分发（以 Apache-2.0 原文为准）'
        rows.append(row)

with open(path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print('[OK] dataset_registry.csv updated')
print()
print('=== License 最终状态汇总 ===')
for r in rows:
    lic = r['license']
    status = 'OK' if 'Apache' in lic or 'MIT' in lic or 'OMG' in lic else 'PENDING'
    print(f'  [{status}] {r["dataset_id"]:30s} | {lic}')