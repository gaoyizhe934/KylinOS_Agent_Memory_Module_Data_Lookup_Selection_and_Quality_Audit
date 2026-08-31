# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'

# 检查被移除的数据
print('=== 被移除的数据示例（前10条）===')
with open(base + r'\data\interim\filtered_out_trajectories.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 10:
            break
        item = json.loads(line.strip())
        did = item.get('id', '')
        dom = item.get('domain', '')
        out = item.get('outcome', '')
        iss = item.get('issues', [])
        print(f'  id={did}  domain={dom}  outcome={out}  issues={iss}')

# 检查保留的数据
print()
print('=== 保留的数据示例（前3条）===')
with open(base + r'\data\interim\gold_candidates_tool_result.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 3:
            break
        item = json.loads(line.strip())
        sid = item['sample_id']
        tt = item['task_type']
        st = item['gold']['status']
        src = item['source']
        rid = item['raw_id']
        print(f'  sample_id={sid}  task_type={tt}  status={st}  source={src}  raw_id={rid}')

print()
print('=== 被移除数据按 domain 统计 ===')
from collections import Counter
domains = Counter()
with open(base + r'\data\interim\filtered_out_trajectories.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line.strip())
        domains[item.get('domain', 'unknown')] += 1
for d, c in domains.most_common():
    print(f'  {d}: {c}')

print()
print('=== 保留数据按 status 统计 ===')
statuses = Counter()
with open(base + r'\data\interim\gold_candidates_tool_result.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line.strip())
        statuses[item['gold']['status']] += 1
for s, c in statuses.most_common():
    print(f'  {s}: {c}')