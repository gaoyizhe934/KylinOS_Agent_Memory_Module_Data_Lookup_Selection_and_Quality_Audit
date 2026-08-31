# -*- coding: utf-8 -*-
import sys, io, json
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'
src = base + r'\data\raw\longmemeval_v2_2026\v0_sample\trajectories.jsonl'

items = []
with open(src, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            items.append(json.loads(line))

total = len(items)
print(f'总条数: {total}')
print()

# 1. domain 分布
domains = Counter()
for item in items:
    domains[item.get('domain', 'unknown')] += 1
print('=== Domain 分布 ===')
for d, c in domains.most_common():
    print(f'  {d}: {c} ({c/total*100:.1f}%)')
print()

# 2. outcome 分布
outcomes = Counter()
for item in items:
    outcomes[item.get('outcome', 'unknown')] += 1
print('=== Outcome 分布 ===')
for o, c in outcomes.most_common():
    print(f'  {o}: {c} ({c/total*100:.1f}%)')
print()

# 3. 提取 goal 关键词，识别任务类型
goal_keywords = Counter()
goal_samples = []
for item in items:
    goal = item.get('goal', '')
    # 提取前几个关键词
    words = goal.lower().split()[:5]
    key = ' '.join(words)
    goal_keywords[key] += 1
    if len(goal_samples) < 20:
        goal_samples.append(goal[:150])

print('=== Goal 样本（前20条）===')
for g in goal_samples:
    print(f'  {g}')
print()

# 4. 按 goal 开头分类
goal_types = Counter()
for item in items:
    goal = item.get('goal', '').lower().strip()
    # 提取动词开头
    if goal.startswith('create'):
        goal_types['create'] += 1
    elif goal.startswith('find') or goal.startswith('search') or goal.startswith('retrieve') or goal.startswith('get'):
        goal_types['find/search/retrieve'] += 1
    elif goal.startswith('update') or goal.startswith('modify') or goal.startswith('edit') or goal.startswith('change'):
        goal_types['update/modify'] += 1
    elif goal.startswith('delete') or goal.startswith('remove'):
        goal_types['delete/remove'] += 1
    elif goal.startswith('assign') or goal.startswith('allocate') or goal.startswith('schedule'):
        goal_types['assign/allocate'] += 1
    elif goal.startswith('generate') or goal.startswith('produce') or goal.startswith('write'):
        goal_types['generate/write'] += 1
    elif goal.startswith('analyze') or goal.startswith('calculate') or goal.startswith('compute'):
        goal_types['analyze/calculate'] += 1
    elif goal.startswith('set up') or goal.startswith('configure') or goal.startswith('install'):
        goal_types['setup/configure'] += 1
    elif goal.startswith('compare'):
        goal_types['compare'] += 1
    elif goal.startswith('filter'):
        goal_types['filter'] += 1
    else:
        goal_types['other'] += 1

print('=== Goal 类型分类 ===')
for gt, c in goal_types.most_common():
    print(f'  {gt}: {c}')
print()

# 5. 分析 environment
envs = Counter()
for item in items:
    env = item.get('environment', '')
    if env:
        envs[env[:80]] += 1
print('=== Environment 样本 ===')
for e, c in envs.most_common(10):
    print(f'  [{c}] {e}')
print()

# 6. 统计 states 长度
state_lengths = []
for item in items:
    states = item.get('states', [])
    state_lengths.append(len(states))
avg_states = sum(state_lengths) / len(state_lengths) if state_lengths else 0
print(f'=== States 统计 ===')
print(f'  平均 states 数: {avg_states:.1f}')
print(f'  最短: {min(state_lengths)}')
print(f'  最长: {max(state_lengths)}')
print()

# 7. 看一条完整的 state 结构
print('=== 一条完整 state 结构 ===')
for item in items:
    states = item.get('states', [])
    if states:
        first_state = states[0]
        print(f'  state keys: {list(first_state.keys())}')
        print(f'  state 示例: {json.dumps(first_state, ensure_ascii=False)[:500]}')
        break