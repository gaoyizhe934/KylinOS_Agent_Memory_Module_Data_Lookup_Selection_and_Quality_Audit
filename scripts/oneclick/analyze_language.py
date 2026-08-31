# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'

# 1. 现有中文 processed 数据
print('=== 现有中文 processed 数据（preference_extraction）===')
with open(base + r'\data\processed\preference_extraction.jsonl', 'r', encoding='utf-8') as f:
    item = json.loads(f.readline().strip())
lang = item.get('language', 'N/A')
inp = json.dumps(item.get('input', {}), ensure_ascii=False)[:200]
gold = json.dumps(item.get('gold', {}), ensure_ascii=False)[:200]
print(f'  language: {lang}')
print(f'  input: {inp}')
print(f'  gold: {gold}')
print()

# 2. 转换后的 trajectories 数据
print('=== 转换后的 trajectories 数据 ===')
with open(base + r'\data\interim\gold_candidates_tool_result.jsonl', 'r', encoding='utf-8') as f:
    item = json.loads(f.readline().strip())
lang = item.get('language', 'N/A')
inp = json.dumps(item.get('input', {}), ensure_ascii=False)[:200]
gold = json.dumps(item.get('gold', {}), ensure_ascii=False)[:200]
print(f'  language: {lang}')
print(f'  input: {inp}')
print(f'  gold: {gold}')
print()

# 3. 检测 trajectories 原始数据语言
print('=== trajectories 原始数据语言检测 ===')
en_count = 0
cn_count = 0
total = 0
with open(base + r'\data\raw\longmemeval_v2_2026\v0_sample\trajectories.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line.strip())
        goal = item.get('goal', '')
        total += 1
        has_cn = any('\u4e00' <= c <= '\u9fff' for c in goal)
        if has_cn:
            cn_count += 1
        else:
            en_count += 1
        if total <= 5:
            print(f'  含中文: {has_cn} | goal: {str(goal)[:100]}')

print(f'\n统计: 总{total}条, 英文={en_count}, 中文={cn_count}')

# 4. 检查所有 processed 数据的语言
print('\n=== 所有 processed 数据语言分布 ===')
import glob
for fpath in sorted(glob.glob(base + r'\data\processed\*.jsonl')):
    if 'multiwoz' in fpath:
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        first = f.readline().strip()
        if first:
            item = json.loads(first)
            tt = item.get('task_type', '?')
            lang = item.get('language', '?')
            print(f'  {fpath.split(chr(92))[-1]} ({tt}): language={lang}')