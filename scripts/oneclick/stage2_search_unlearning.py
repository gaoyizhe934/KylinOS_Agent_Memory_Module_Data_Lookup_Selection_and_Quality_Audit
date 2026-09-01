# -*- coding: utf-8 -*-
"""阶段 2: 检索机器遗忘/精准遗忘相关公开数据集"""
import sys, io, urllib.request, ssl, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {'User-Agent': 'Mozilla/5.0'}

def hf_search(query, limit=10):
    url = 'https://huggingface.co/api/datasets?search=' + urllib.parse.quote(query) + '&limit=' + str(limit)
    req = urllib.request.Request(url, headers=ua)
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    return json.loads(resp.read().decode('utf-8'))

import urllib.parse

# 1. 详情
print('=== machine-unlearning-bench/data-unlearning-bench ===')
try:
    url = 'https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench'
    req = urllib.request.Request(url, headers=ua)
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    info = json.loads(resp.read().decode('utf-8'))
    desc = info.get('description', '')
    card = info.get('cardData', {})
    print(f'  description: {str(desc)[:200]}')
    print(f'  downloads: {info.get("downloads", 0)}')
    print(f'  license: {card.get("license", "N/A")}')
    print(f'  siblings: {len(info.get("siblings", []))} files')
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')

# 2. 搜索
queries = ['machine unlearning', 'unlearning', 'forgetting', 'knowledge unlearning', 'model unlearning']
for q in queries:
    print(f'\n=== 搜索: {q} ===')
    try:
        results = hf_search(q)
        for d in results:
            did = d.get('id', '')
            dl = d.get('downloads', 0)
            if dl > 50:  # 只显示有一定下载量的
                print(f'  {did} (downloads={dl})')
    except Exception as e:
        print(f'  [FAIL] {str(e)[:80]}')