# -*- coding: utf-8 -*-
import sys, io, json, os
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'

# 定位分类标准
positioning = {
    'preference_extraction': {
        'public_ok': False,
        'rule': '不足，必须自建为主',
        'action': '移除',
    },
    'knowledge_retrieval': {
        'public_ok': 'assist_only',
        'rule': '可辅助，必须加入中文 OS 场景',
        'action': '仅作辅助参考，不进入封存',
    },
    'tool_result': {
        'public_ok': False,
        'rule': '必须真实回放与自建',
        'action': '移除（非麒麟 VM 回放）',
    },
    'conflict_resolution': {
        'public_ok': False,
        'rule': '基本必须自建',
        'action': '移除',
    },
    'precise_forgetting': {
        'public_ok': False,
        'rule': '必须自建',
        'action': '移除',
    },
    'end_to_end_session': {
        'public_ok': False,
        'rule': '必须在麒麟环境生成',
        'action': '移除',
    },
}

# 需要检查的文件
files_to_check = {
    'trajectories (LongMemEval-V2)': base + r'\data\interim\gold_candidates_tool_result.jsonl',
    'preference_extraction': base + r'\data\interim\gold_candidates_preference_extraction.jsonl',
    'knowledge_retrieval': base + r'\data\interim\gold_candidates_knowledge_retrieval.jsonl',
    'conflict_resolution': base + r'\data\interim\gold_candidates_conflict_resolution.jsonl',
    'precise_forgetting': base + r'\data\interim\gold_candidates_precise_forgetting.jsonl',
    'end_to_end_session': base + r'\data\interim\gold_candidates_end_to_end_session.jsonl',
}

print('========== 按定位分类筛选结果 ==========')
print()

all_keep = {}
all_remove = {}
total_keep = 0
total_remove = 0

for name, fpath in files_to_check.items():
    if not os.path.exists(fpath):
        print(f'[{name}] 文件不存在，跳过')
        continue
    
    items = []
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    
    # 检测 task_type
    task_types = Counter()
    for item in items:
        tt = item.get('task_type', 'unknown')
        task_types[tt] += 1
    
    main_tt = task_types.most_common(1)[0][0] if task_types else 'unknown'
    rule = positioning.get(main_tt, {}).get('rule', '未定义')
    action = positioning.get(main_tt, {}).get('action', '未知')
    public_ok = positioning.get(main_tt, {}).get('public_ok', False)
    
    # 判断：是否保留
    if public_ok == 'assist_only':
        # 知识检索：可辅助，但需加中文 OS 场景
        keep = []
        remove = items
        for item in items:
            lang = item.get('language', '')
            source = item.get('source', '')
            inp = json.dumps(item.get('input', {}), ensure_ascii=False)
            is_os_scene = any(kw in inp for kw in ['麒麟', 'kylin', 'OS', '系统', '桌面', '文件', '终端'])
            if lang == 'zh-CN' and is_os_scene:
                keep.append(item)
            else:
                remove_item = item
                remove_item['_remove_reason'] = f'语言={lang}, 非中文OS场景'
                remove.append(remove_item)
    elif public_ok:
        keep = items
        remove = []
    else:
        # 必须自建/真实回放 → 全部移除
        keep = []
        remove = items
        for item in items:
            item['_remove_reason'] = f'定位要求: {rule}'
    
    all_keep[name] = keep
    all_remove[name] = remove
    total_keep += len(keep)
    total_remove += len(remove)
    
    print(f'=== {name} ===')
    print(f'  总条数: {len(items)}')
    print(f'  主要 task_type: {main_tt}')
    print(f'  定位规则: {rule}')
    print(f'  判定: {action}')
    print(f'  保留: {len(keep)} 条 | 移除: {len(remove)} 条')
    print()

print(f'========== 汇总 ==========')
print(f'  总计保留: {total_keep} 条')
print(f'  总计移除: {total_remove} 条')
print()

# 输出被移除的 trajectories 详情
print('========== trajectories 被移除详情 ==========')
removed = all_remove.get('trajectories (LongMemEval-V2)', [])
if removed:
    # 按 domain 统计
    domains = Counter()
    outcomes = Counter()
    for item in removed:
        domains[item.get('input', {}).get('domain', 'unknown')] += 1
        outcomes[item.get('gold', {}).get('status', 'unknown')] += 1
    print(f'  共 {len(removed)} 条被移除')
    print(f'  Domain 分布:')
    for d, c in domains.most_common():
        print(f'    {d}: {c}')
    print(f'  Status 分布:')
    for o, c in outcomes.most_common():
        print(f'    {o}: {c}')
    print(f'  移除原因: 定位要求"必须真实回放与自建"，trajectories 来自 HuggingFace 公开数据集')
    print(f'              非麒麟 VM 真实回放，不符合 Tool Result 定位标准')
else:
    print('  无 trajectories 数据被移除')
print()

# 输出知识检索中可能保留的数据
print('========== 知识检索辅助数据详情 ==========')
kept_kr = all_keep.get('knowledge_retrieval', [])
removed_kr = all_remove.get('knowledge_retrieval', [])
if kept_kr:
    print(f'  保留: {len(kept_kr)} 条（中文+OS场景）')
if removed_kr:
    # 统计移除原因
    reasons = Counter()
    for item in removed_kr:
        reasons[item.get('_remove_reason', 'unknown')] += 1
    print(f'  移除: {len(removed_kr)} 条')
    for r, c in reasons.most_common():
        print(f'    {r}: {c}')
print()

# 输出建议
print('========== 后续建议 ==========')
print('''
1. trajectories (1,702条) 全部移除 → 放入 data/interim/filtered_out_by_positioning.jsonl
   原因：Tool Result 必须来自麒麟 VM 真实回放，公开数据不符合定位

2. 知识检索中非中文/非OS场景的数据 → 保留在 interim 作辅助参考
   但最终封存集必须使用中文 OS 场景数据

3. 自建数据（偏好/冲突/遗忘/端到端）全部保留
   因为它们本身就是自建的中文麒麟 OS 场景数据

4. 下一步重点：在麒麟 VM 上真实执行 Tool Result 和端到端场景
''')