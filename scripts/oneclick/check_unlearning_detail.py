# -*- coding: utf-8 -*-
import sys, io, urllib.request, ssl, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ua = {'User-Agent': 'Mozilla/5.0'}

# 获取详细卡片信息
url = 'https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench'
req = urllib.request.Request(url, headers=ua)
resp = urllib.request.urlopen(req, timeout=20, context=ctx)
info = json.loads(resp.read().decode('utf-8'))
card = info.get('cardData', {})
print('=== 详细卡片信息 ===')
print(f'  cardData keys: {list(card.keys())}')
lic = card.get('license', 'N/A')
print(f'  license: {lic}')
print(f'  tags: {info.get("tags", [])[:15]}')

# 查看 README
print()
print('=== README 前800字 ===')
url2 = 'https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench/raw/main/README.md'
req2 = urllib.request.Request(url2, headers=ua)
resp2 = urllib.request.urlopen(req2, timeout=20, context=ctx)
readme = resp2.read().decode('utf-8')
print(readme[:800])
print()
print('=== README 总长度 ===')
print(f'{len(readme)} chars')