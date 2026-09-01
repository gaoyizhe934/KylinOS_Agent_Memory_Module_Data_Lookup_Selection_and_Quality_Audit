# -*- coding: utf-8 -*-
"""阶段 2: 检查现有数据集 URL 可访问性"""
import sys, io, csv, os, json, urllib.request, ssl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 使用代理
proxy = 'http://127.0.0.1:7890'
proxy_handler = urllib.request.ProxyHandler({'http': proxy, 'https': proxy})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = r'C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807'
reg_path = os.path.join(base, 'registry', 'dataset_registry.csv')

rows = []
with open(reg_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

def check_url(url, timeout=8):
    """检查 URL 可访问性，返回 (status, http_code_or_error)"""
    if not url:
        return ('EMPTY', '无URL')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        code = resp.status
        resp.close()
        if 200 <= code < 400:
            return ('OK', str(code))
        return ('ERROR', f'HTTP {code}')
    except urllib.error.HTTPError as e:
        return ('ERROR', f'HTTP {e.code}')
    except urllib.error.URLError as e:
        return ('ERROR', f'无法连接: {str(e.reason)[:40]}')
    except socket.timeout:
        return ('TIMEOUT', '超时')
    except Exception as e:
        return ('ERROR', f'{str(e)[:40]}')

print('========== 现有数据集 URL 可访问性检查 ==========')
print()
print(f'| 数据集 | 官方URL | 状态 | 下载URL | 状态 |')
print(f'| --- | --- | --- | --- | --- |')
for row in rows:
    did = row['dataset_id']
    official = row['official_url']
    data_url = row['data_url']
    s1 = check_url(official)
    s2 = check_url(data_url)
    status1 = f'{s1[0]}:{s1[1]}'
    status2 = f'{s2[0]}:{s2[1]}'
    print(f'| {did} | {official[:50]} | {status1} | {(data_url or "")[:50]} | {status2} |')

print()
print('说明: OK=可访问, EMPTY=无URL, ERROR=不可访问')
print('注意: 部分站点可能对爬虫有反爬限制，HTTP 403/429 不一定代表数据不可用，需人工确认。')