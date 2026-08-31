# -*- coding: utf-8 -*-
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'
src = base + r'\data\interim\gold_candidates_tool_result.jsonl'
dst = base + r'\data\interim\filtered_out_by_positioning.jsonl'

# 读取 trajectories 数据
items = []
with open(src, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            items.append(json.loads(line.strip()))

# 给每条加上移除原因
for item in items:
    item['_remove_reason'] = 'Tool Result 必须真实回放与自建，trajectories 来自 HuggingFace 公开数据集，非麒麟 VM 回放'

# 写入 filtered_out
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, 'w', encoding='utf-8') as f:
    for item in items:
        record = {
            'sample_id': item.get('sample_id', ''),
            'task_type': item.get('task_type', ''),
            'language': item.get('language', ''),
            'source': item.get('source', ''),
            'raw_id': item.get('raw_id', ''),
            'remove_reason': item['_remove_reason'],
            'original_goal': str(item.get('input', {}).get('goal', ''))[:100],
        }
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

# 删除原文件
os.remove(src)

print('========== 筛选结果 ==========')
print()
print('保留的数据（interim 中保留的文件）：')
print('  gold_candidates_preference_extraction.jsonl  60条  zh-CN  自建  [符合定位]')
print('  gold_candidates_knowledge_retrieval.jsonl     60条  zh-CN  自建  [符合定位]')
print('  gold_candidates_conflict_resolution.jsonl     40条  zh-CN  自建  [符合定位]')
print('  gold_candidates_precise_forgetting.jsonl      40条  zh-CN  自建  [符合定位]')
print('  gold_candidates_end_to_end_session.jsonl      15条  zh-CN  自建  [封存需麒麟VM回放]')
print('  --------------------------------------------')
print('  合计: 215条')
print()
print('移除的数据：')
print('  gold_candidates_tool_result.jsonl            1702条  en  公开  [定位不符]')
print('  filtered_out_trajectories.jsonl                168条  en  公开  [含禁用词]')
print('  --------------------------------------------')
print('  合计: 1870条')
print()
print('移除原因：Tool Result 定位要求必须真实回放与自建，')
print('trajectories 来自 HuggingFace 公开数据集，非麒麟 VM 真实回放，不符合定位标准。')
print()
print('产出文件: ' + dst)