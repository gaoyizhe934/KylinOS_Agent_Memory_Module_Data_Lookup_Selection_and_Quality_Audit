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

# 提取所有 action 类型
action_types = Counter()
action_samples = []
for item in items[:500]:  # 前500条
    states = item.get('states', [])
    for state in states:
        action = state.get('action')
        if action:
            action_str = str(action)[:100]
            action_types[action_str] += 1
            if len(action_samples) < 30:
                action_samples.append(action_str)

print('=== Action 类型分布（前30种）===')
for a, c in action_types.most_common(30):
    print(f'  [{c}] {a}')
print()

# 提取 thought 模式
print('=== Thought 模式样本（前10条）===')
thought_types = Counter()
for item in items[:200]:
    states = item.get('states', [])
    for state in states[:2]:
        thought = state.get('thought', '')
        if thought:
            # 提取前几个词
            words = thought.lower().split()[:8]
            key = ' '.join(words)
            thought_types[key] += 1
for t, c in thought_types.most_common(10):
    print(f'  [{c}] {t}')
print()

# 总结：可映射的麒麟 OS 场景
print('=== 英文场景 → 麒麟 OS 中文场景映射建议 ===')
print()
print('Enterprise (WorkArena) 场景:')
print('  英文: Create/Update/Delete incidents, Assign work, Filter lists')
print('  → 麒麟 OS: 创建/编辑/删除文件, 管理系统设置, 过滤文件列表')
print('  英文: Onboard users, Manage expenses')
print('  → 麒麟 OS: 添加用户账户, 管理系统资源')
print('  英文: Knowledge base Q&A')
print('  → 麒麟 OS: 系统帮助文档查询')
print()
print('Web (WebArena) 场景:')
print('  英文: Shopping cart, Content management, Data analysis')
print('  → 麒麟 OS: 应用商店操作, 文件管理, 系统监控')
print('  英文: Search/Filter information')
print('  → 麒麟 OS: 搜索文件/系统配置')
print()

# 统计每条轨迹的 action 数量和类型
action_counts = []
for item in items:
    states = item.get('states', [])
    total_actions = sum(1 for s in states if s.get('action'))
    action_counts.append(total_actions)

avg_actions = sum(action_counts) / len(action_counts) if action_counts else 0
print(f'平均每条轨迹的 action 数: {avg_actions:.1f}')
print(f'最短 action 链: {min(action_counts)}')
print(f'最长 action 链: {max(action_counts)}')