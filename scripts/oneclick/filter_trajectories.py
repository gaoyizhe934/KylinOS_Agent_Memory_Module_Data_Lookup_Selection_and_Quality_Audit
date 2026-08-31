# -*- coding: utf-8 -*-
"""按 v2.0 红线标准筛选 trajectories.jsonl 数据"""
import sys, io, json, os, re
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'
src = os.path.join(base, 'data', 'raw', 'longmemeval_v2_2026', 'v0_sample', 'trajectories.jsonl')
out_keep = os.path.join(base, 'data', 'interim', 'gold_candidates_tool_result.jsonl')
out_remove = os.path.join(base, 'data', 'interim', 'filtered_out_trajectories.jsonl')

# 读取所有数据
items = []
with open(src, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            items.append(json.loads(line))

print(f'总条数: {len(items)}')

# 检查日期格式的正则：ISO-8601
iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

# 红线标准检查
def check_redlines(item):
    issues = []
    item_str = json.dumps(item, ensure_ascii=False)

    # 红线4: 全链路禁用 mock/模拟/合成数据
    mock_keywords = ['mock', '模拟', 'synthetic', 'dummy', 'fake', 'placeholder']
    for kw in mock_keywords:
        if kw in item_str.lower():
            issues.append(f'含禁用语: {kw}')
            break

    # 红线5: timestamp ISO-8601 检查
    ts = item.get('timestamp', '')
    if ts and not iso_pattern.match(str(ts)):
        issues.append(f'timestamp非ISO-8601: {ts}')

    # 红线5: 是否有 raw_id 或可追溯字段
    has_raw = bool(item.get('raw_id') or item.get('id') or item.get('source_file'))
    if not has_raw:
        issues.append('无可追溯ID')

    # 检查 domain 是否为空
    domain = item.get('domain', '')
    if not domain:
        issues.append('domain为空')

    # 检查 outcome 是否为空
    outcome = item.get('outcome', '')
    if not outcome:
        issues.append('outcome为空')

    # 检查 states 是否为空
    states = item.get('states', [])
    if not states:
        issues.append('states为空')

    return issues

keep = []
remove = []

for item in items:
    issues = check_redlines(item)
    item['_filter_issues'] = issues
    if issues:
        remove.append(item)
    else:
        keep.append(item)

print(f'\n符合条件: {len(keep)} 条')
print(f'不符合条件: {len(remove)} 条')

# 统计不符合原因
from collections import Counter
all_issues = []
for item in remove:
    all_issues.extend(item['_filter_issues'])
issue_stats = Counter(all_issues)
print(f'\n不符合原因统计:')
for issue, cnt in issue_stats.most_common():
    print(f'  {issue}: {cnt} 条')

# 写入符合条件的数据（转换为 Tool Result 格式）
os.makedirs(os.path.dirname(out_keep), exist_ok=True)
with open(out_keep, 'w', encoding='utf-8') as f:
    for i, item in enumerate(keep):
        # 转换为统一 Schema 格式
        sample = {
            'sample_id': f'tool_{item.get("id", f"lmev2_{i:06d}")}',
            'dataset_version': 'kylin_memory_gold_v1.0',
            'task_type': 'tool_result',
            'language': 'en',
            'user_id': f'u_lmev2_{item.get("domain", "unknown")}_{i}',
            'conversation_id': f'conv_tool_{i:06d}',
            'timestamp': item.get('timestamp', '2026-01-01T00:00:00+08:00'),
            'input': {
                'goal': item.get('goal', ''),
                'domain': item.get('domain', ''),
                'environment': item.get('environment', ''),
                'start_url': item.get('start_url', ''),
            },
            'gold': {
                'status': 'success' if item.get('outcome') == 'success' else 'failed',
                'tool': item.get('domain', 'unknown'),
                'args': {'goal': item.get('goal', '')},
                'result': item.get('outcome', ''),
                'side_effect': [],
                'persist_policy': 'persist',
            },
            'evidence': [{
                'source_event_id': item.get('id', f'evt_{i}'),
                'span': str(item.get('goal', ''))[:200],
            }],
            'source': 'public_derived',
            'template_family': f'tool_status_{item.get("outcome", "unknown")}_v1',
            'annotator_a': '',
            'annotator_b': '',
            'review_status': 'candidate_only',
            'raw_id': item.get('id', f'raw_{i}'),
            'source_file': 'trajectories.jsonl',
            'source_version': 'longmemeval_v2_2026_v0_sample',
        }
        f.write(json.dumps(sample, ensure_ascii=False) + '\n')

# 写入不符合条件的数据
os.makedirs(os.path.dirname(out_remove), exist_ok=True)
with open(out_remove, 'w', encoding='utf-8') as f:
    for item in remove:
        record = {
            'id': item.get('id', ''),
            'domain': item.get('domain', ''),
            'outcome': item.get('outcome', ''),
            'issues': item['_filter_issues'],
        }
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

print(f'\n符合条件数据已写入: {out_keep}')
print(f'不符合条件数据已写入: {out_remove}')

# 汇总报告
print(f'\n=== 筛选报告 ===')
print(f'输入: {src}')
print(f'总条数: {len(items)}')
print(f'保留: {len(keep)} 条 ({(len(keep)/len(items)*100):.1f}%)')
print(f'移除: {len(remove)} 条 ({(len(remove)/len(items)*100):.1f}%)')
print(f'保留文件: {out_keep}')
print(f'移除文件: {out_remove}')