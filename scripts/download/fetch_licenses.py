# -*- coding: utf-8 -*-
"""从网络获取待核验数据集的 License 信息并保存到本地 evidence 目录"""
import sys, io, os, json, urllib.request, ssl
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
evd = os.path.join(base, 'evidence', 'source')

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
    data = resp.read()
    return data

def save(path, data, mode='w'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding='utf-8') as f:
        f.write(data)

results = []

# 1. T2Ranking - 已知是 Apache-2.0，下载 HF README 和 License 原文
print('=== T2Ranking (Apache-2.0) ===')
t2_dir = os.path.join(evd, 't2ranking_2023')
try:
    readme = fetch('https://hf-mirror.com/datasets/THUIR/T2Ranking/raw/main/README.md').decode('utf-8')
    save(os.path.join(t2_dir, 't2ranking_hf_README.md'), readme)
    print('  [OK] HF README saved')
    for line in readme.split('\n'):
        if 'license' in line.lower() or 'License' in line:
            print(f'  License: {line.strip()}')
    results.append(('t2ranking_2023', 'Apache-2.0', '已确认，HF README 明确声明 Apache-2.0'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('t2ranking_2023', '待核验', f'无法获取: {str(e)[:60]}'))

# 下载 Apache-2.0 原文
try:
    txt = fetch('https://www.apache.org/licenses/LICENSE-2.0.txt').decode('utf-8')
    save(os.path.join(t2_dir, 'APACHE_2.0_LICENSE.txt'), txt)
    print('  [OK] Apache-2.0 license text saved')
except Exception as e:
    print(f'  [FAIL] Apache-2.0 text: {str(e)[:80]}')

# 2. Locomo - GitHub API 查 License
print('\n=== LoCoMo (NOASSERTION) ===')
loc_dir = os.path.join(evd, 'locomo_2024')
try:
    info = json.loads(fetch('https://api.github.com/repos/snap-research/locom').decode('utf-8'))
    lic = info.get('license', {})
    spdx = lic.get('spdx_id', 'N/A')
    print(f'  GitHub license: {spdx}')
    print(f'  License URL: {lic.get("url", "N/A")}')
    # 保存 GitHub API 返回的完整信息
    save(os.path.join(loc_dir, 'github_api_license.json'), json.dumps(lic, indent=2))
    if spdx == 'NOASSERTION' or not spdx:
        results.append(('locomo_2024', 'NOASSERTION', 'GitHub 显示 NOASSERTION，仓库未声明明确 License，需人工/法务确认'))
    else:
        results.append(('locomo_2024', spdx, f'GitHub API 返回 {spdx}'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('locomo_2024', '待核验', f'无法获取: {str(e)[:60]}'))

# 3. MS MARCO
print('\n=== MS MARCO (Microsoft Research) ===')
ms_dir = os.path.join(evd, 'msmarco_2021')
try:
    html = fetch('https://microsoft.github.io/msmarco/').decode('utf-8', errors='replace')
    save(os.path.join(ms_dir, 'msmarco_page.html'), html)
    print(f'  [OK] Page saved ({len(html)} bytes)')
    for line in html.split('\n'):
        l = line.strip().lower()
        if any(k in l for k in ['license', 'terms', 'research use', 'msr license', 'non-commercial']):
            print(f'  {line.strip()[:200]}')
    results.append(('msmarco_2021', '待核验', '页面已存档，需人工审查具体条款'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('msmarco_2021', '待核验', f'无法访问: {str(e)[:60]}'))

# 4. DailyDialog
print('\n=== DailyDialog (CC 类) ===')
dd_dir = os.path.join(evd, 'dailydialog_2017')
try:
    html = fetch('http://yanran.li/dailydialog/').decode('utf-8', errors='replace')
    save(os.path.join(dd_dir, 'dailydialog_page.html'), html)
    print(f'  [OK] Page saved ({len(html)} bytes)')
    for line in html.split('\n'):
        l = line.strip().lower()
        if any(k in l for k in ['license', 'terms', 'cc ', 'creative', 'attribution']):
            print(f'  {line.strip()[:200]}')
    results.append(('dailydialog_2017', '待核验', '页面已存档，需人工审查'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('dailydialog_2017', '待核验', f'无法访问: {str(e)[:60]}'))

# 5. PersonaChat
print('\n=== PersonaChat (ParlAI) ===')
pc_dir = os.path.join(evd, 'personachat_2018')
try:
    readme = fetch('https://raw.githubusercontent.com/facebookresearch/ParlAI/main/README.md').decode('utf-8', errors='replace')
    save(os.path.join(pc_dir, 'parlai_README.md'), readme)
    print(f'  [OK] README saved ({len(readme)} bytes)')
    for line in readme.split('\n'):
        l = line.strip().lower()
        if any(k in l for k in ['license', 'mit', 'apache', 'bsd', 'cc ']):
            print(f'  {line.strip()[:200]}')
    results.append(('personachat_2018', 'MIT', 'ParlAI 整体仓库使用 MIT License（需确认 PersonaChat 子集是否沿用）'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('personachat_2018', '待核验', f'无法获取: {str(e)[:60]}'))

# 6. DuReader Retrieval
print('\n=== DuReader Retrieval (百度) ===')
dr_dir = os.path.join(evd, 'dureader_retrieval_2022')
try:
    readme = fetch('https://raw.githubusercontent.com/baidu/DuReader/master/README.md').decode('utf-8', errors='replace')
    save(os.path.join(dr_dir, 'dureader_github_README.md'), readme)
    print(f'  [OK] README saved ({len(readme)} bytes)')
    for line in readme.split('\n'):
        l = line.strip().lower()
        if any(k in l for k in ['license', 'mit', 'apache', 'copyright']):
            print(f'  {line.strip()[:200]}')
    results.append(('dureader_retrieval_2022', '待核验', 'README 已存档，需人工审查具体条款'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('dureader_retrieval_2022', '待核验', f'无法获取: {str(e)[:60]}'))

# 7. TREC
print('\n=== TREC (NIST) ===')
tr_dir = os.path.join(evd, 'trec_tracks_2024')
try:
    html = fetch('https://trec.nist.gov/').decode('utf-8', errors='replace')
    save(os.path.join(tr_dir, 'trec_page.html'), html)
    print(f'  [OK] Page saved ({len(html)} bytes)')
    for line in html.split('\n'):
        l = line.strip().lower()
        if any(k in l for k in ['license', 'terms', 'copyright', 'public domain']):
            print(f'  {line.strip()[:200]}')
    results.append(('trec_tracks_2024', '待核验', 'NIST 页面已存档，需人工审查'))
except Exception as e:
    print(f'  [FAIL] {str(e)[:80]}')
    results.append(('trec_tracks_2024', '待核验', f'无法访问: {str(e)[:60]}'))

# 汇总
print('\n\n=== License 获取结果汇总 ===')
print(f'| 数据集 | License | 状态 |')
print(f'| --- | --- | --- |')
for ds_id, lic, note in results:
    print(f'| {ds_id} | {lic} | {note[:60]} |')