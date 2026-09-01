# -*- coding: utf-8 -*-
"""阶段 3: 候选数据集版本线索锁定与存档校验（Gate 3 版本验收命令）。

用法（在仓库根目录执行）:
    python scripts/audit/stage3_version_lock.py             # 校验模式（离线，CI 验收）
    python scripts/audit/stage3_version_lock.py --fetch     # 抓取模式（在线，A 执行）
    python scripts/audit/stage3_version_lock.py --fetch --proxy http://127.0.0.1:7890

产出（仅 --fetch 模式写入）:
    evidence/source/<dataset_id>/api_snapshot_20260901/*.json  API 关键字段存档
    evidence/source/<dataset_id>/version_lock_20260901.md      版本线索锁定卡

版本线索来源:
    - GitHub 仓库: 默认分支 HEAD Commit SHA + 提交时间（GitHub REST API v3）
    - HuggingFace 数据集: main revision SHA + lastModified（HF Hub API）
    - Web 门户（无仓库类）: 核验时点 + HTTP 状态 + 固定版本号（如 OMG 规范文档号）

退出码:
    0 = 全部候选版本线索齐备（校验模式）或全部抓取成功（抓取模式）
    1 = 存在缺失项或抓取失败

说明: 上游 SHA 会随官方更新而变化；version_lock 锁定的是核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。复测发现 SHA 变化时应
追加新日期的锁文件（保留历史）并交 Reviewer 裁决。
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'oneclick'))
from net_utils import check_url, fetch_json, set_proxy, setup_stdout_utf8  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVIDENCE_ROOT = os.path.join(REPO_ROOT, 'evidence', 'source')
SNAPSHOT_DATE = '20260901'
CST = timezone(timedelta(hours=8))

CANDIDATES = [
    {
        'id': 'longmemeval_cleaned_2025', 'formal': 'LongMemEval (cleaned)',
        'github': ['xiaowu0162/LongMemEval'], 'hf': ['xiaowu0162/longmemeval-cleaned'], 'webs': [],
    },
    {
        'id': 'longmemeval_v2_2026', 'formal': 'LongMemEval-V2',
        'github': ['xiaowu0162/LongMemEval-V2'], 'hf': ['xiaowu0162/longmemeval-v2'], 'webs': [],
    },
    {
        'id': 'stabletoolbench_2024', 'formal': 'StableToolBench',
        'github': ['THUNLP-MT/StableToolBench'], 'hf': [], 'webs': [],
    },
    {
        'id': 'toolbench_2024', 'formal': 'ToolBench',
        'github': ['OpenBMB/ToolBench'], 'hf': [], 'webs': [],
        'note': '方法论参考（Reviewer 裁决 2026-09-01，PR#1 审批意见第四节第 4 条）；'
                '版本线索仍锁定，保证已存档 README 可追溯到具体仓库状态',
    },
    {
        'id': 't2ranking_2023', 'formal': 'T2Ranking',
        'github': ['THUIR/T2Ranking'], 'hf': ['THUIR/T2Ranking'], 'webs': [],
    },
    {
        'id': 'dureader_retrieval_2022', 'formal': 'DuReader Retrieval',
        'github': ['baidu/DuReader', 'PaddlePaddle/RocketQA'], 'hf': [], 'webs': [],
    },
    {
        'id': 'multiwoz_2_2_2020', 'formal': 'MultiWOZ 2.2',
        'github': ['budzianowski/multiwoz'], 'hf': [], 'webs': [],
    },
    {
        'id': 'personachat_2018', 'formal': 'PersonaChat (ParlAI)',
        'github': ['facebookresearch/ParlAI'], 'hf': [],
        'webs': [('http://parl.ai/downloads/personachat/personachat.tgz', '官方 tgz 数据入口')],
    },
    {
        'id': 'msmarco_2021', 'formal': 'MS MARCO',
        'github': [], 'hf': ['microsoft/ms_marco'],
        'webs': [('https://microsoft.github.io/msmarco/', '官方项目页')],
    },
    {
        'id': 'trec_tracks_2024', 'formal': 'TREC (NIST)',
        'github': [], 'hf': [],
        'webs': [('https://trec.nist.gov/data.html', '官方数据门户')],
        'note': 'NIST 无单一 repo/release；版本线索以门户核验时点 + HTTP 状态存档；'
                '具体 Track 子集版本在子集选定后单独锁定',
    },
    {
        'id': 'bpmn_2_0_2013', 'formal': 'BPMN 2.0 (OMG 标准)',
        'github': [], 'hf': [],
        'webs': [('https://www.omg.org/spec/BPMN/2.0/PDF', '官方规范 PDF 入口')],
        'note': '规范版本固定为 BPMN 2.0.2（OMG 文档 formal/2013-12-09）；'
                '版本线索以规范文档号 + PDF 入口核验时点存档，官方 PDF 已在证据包另行下载',
    },
    {
        'id': 'machine_unlearning_bench_2025', 'formal': 'Data Unlearning Bench (KLOM)',
        'github': [], 'hf': ['machine-unlearning-bench/data-unlearning-bench'], 'webs': [],
    },
]


def now_cst():
    return datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')


def now_utc_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def snapshot_dir(dataset_id):
    return os.path.join(EVIDENCE_ROOT, dataset_id, 'api_snapshot_' + SNAPSHOT_DATE)


def write_file_lf(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def write_json(path, obj):
    write_file_lf(path, json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def slug(text):
    return text.replace('/', '__')


def fetch_github(full_repo, snap_dir, fetched_at):
    """锁定一个 GitHub 仓库默认分支 HEAD 的 Commit SHA，返回版本线索 dict。"""
    repo_api = f'https://api.github.com/repos/{full_repo}'
    repo_info = fetch_json(repo_api)
    branch = repo_info.get('default_branch') or 'master'
    commit_api = f'{repo_api}/commits/{branch}'
    commit = fetch_json(commit_api)
    extract = {
        '_meta': {
            'api_endpoint': commit_api,
            'fetched_at_utc': fetched_at,
            'note': '关键字段提取存档（files[].patch 等大字段已裁剪）；复现: GET api_endpoint',
        },
        'sha': commit.get('sha'),
        'html_url': commit.get('html_url'),
        'commit': commit.get('commit'),
        'parents': commit.get('parents'),
        'stats': commit.get('stats'),
        'files_count': len(commit.get('files') or []),
    }
    write_json(os.path.join(snap_dir, f'github_commit_{slug(full_repo)}.json'), extract)
    write_json(os.path.join(snap_dir, f'github_repo_{slug(full_repo)}.json'), {
        '_meta': {'api_endpoint': repo_api, 'fetched_at_utc': fetched_at},
        'default_branch': branch,
        'html_url': repo_info.get('html_url'),
        'pushed_at': repo_info.get('pushed_at'),
        'updated_at': repo_info.get('updated_at'),
        'license': (repo_info.get('license') or {}).get('spdx_id'),
    })
    message = (commit.get('commit') or {}).get('message') or ''
    return {
        'kind': 'github',
        'source': full_repo,
        'sha': commit.get('sha'),
        'date': ((commit.get('commit') or {}).get('committer') or {}).get('date'),
        'branch': branch,
        'message': message.splitlines()[0] if message else '',
        'endpoint': commit_api,
        'snapshot_file': f'github_commit_{slug(full_repo)}.json',
    }


def fetch_hf(dataset_id, snap_dir, fetched_at):
    """锁定一个 HuggingFace 数据集 main revision SHA，返回版本线索 dict。"""
    api = f'https://huggingface.co/api/datasets/{dataset_id}'
    info = fetch_json(api)
    write_json(os.path.join(snap_dir, f'hf_dataset_{slug(dataset_id)}.json'), {
        '_meta': {'api_endpoint': api, 'fetched_at_utc': fetched_at},
        'sha': info.get('sha'),
        'lastModified': info.get('lastModified'),
        'cardData': info.get('cardData'),
        'siblings_count': len(info.get('siblings') or []),
        'id': info.get('id'),
    })
    return {
        'kind': 'hf',
        'source': dataset_id,
        'sha': info.get('sha'),
        'date': info.get('lastModified'),
        'license': (info.get('cardData') or {}).get('license'),
        'endpoint': api,
        'snapshot_file': f'hf_dataset_{slug(dataset_id)}.json',
    }


def check_web(url, note, snap_dir, fetched_at):
    status, detail = check_url(url, timeout=15)
    result = {
        'kind': 'web',
        'source': url,
        'note': note,
        'status': f'{status} {detail}'.strip(),
        'endpoint': url,
        'snapshot_file': 'web_check.json',
    }
    return result


def write_web_snapshot(snap_dir, results, fetched_at):
    write_json(os.path.join(snap_dir, 'web_check.json'), {
        '_meta': {'checked_at_utc': fetched_at, 'tool': 'scripts/audit/stage3_version_lock.py --fetch'},
        'checks': [{'url': r['source'], 'note': r['note'], 'status': r['status']} for r in results],
    })


def render_lock_md(cand, clues, fetched_cst):
    lines = []
    lines.append(f"# {cand['id']} 版本线索锁定（{SNAPSHOT_DATE[:4]}-{SNAPSHOT_DATE[4:6]}-{SNAPSHOT_DATE[6:]}）")
    lines.append('')
    lines.append(f"- 正式名称：{cand['formal']}")
    lines.append(f"- 核验时间：{fetched_cst}（Asia/Shanghai）")
    lines.append('- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）')
    lines.append('- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`')
    lines.append('')
    lines.append('## 版本线索')
    lines.append('')
    if not clues:
        lines.append('（无）')
    for idx, c in enumerate(clues, 1):
        lines.append(f"### 来源 {idx}（{c['kind']}）：{c['source']}")
        lines.append('')
        if c['kind'] == 'web':
            lines.append(f"- 入口说明：{c['note']}")
            lines.append(f"- 核验结果：{c['status']}")
            lines.append(f"- 入口 URL：{c['endpoint']}")
        else:
            lines.append(f"- {'Commit SHA' if c['kind'] == 'github' else 'Revision SHA'}：{c['sha']}")
            if c['kind'] == 'github':
                lines.append(f"- 分支：{c['branch']}")
                lines.append(f"- 提交时间：{c['date']}")
                lines.append(f"- 提交标题：{c['message']}")
            else:
                lines.append(f"- 最后修改：{c['date']}")
                if c.get('license'):
                    lines.append(f"- License（HF 卡片机读声明）：{c['license']}")
            lines.append(f"- API 端点：{c['endpoint']}")
        lines.append(f"- 存档文件：api_snapshot_{SNAPSHOT_DATE}/{c['snapshot_file']}")
        lines.append('')
    if cand.get('note'):
        lines.append('## 备注')
        lines.append('')
        lines.append(cand['note'])
        lines.append('')
    lines.append('## 使用说明')
    lines.append('')
    lines.append('上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，')
    lines.append('作为阶段 6「再次下载可得到同一版本」的验收基线。')
    lines.append('复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。')
    return '\n'.join(lines) + '\n'


def run_fetch(args):
    fetched_at = now_utc_iso()
    fetched_cst = now_cst()
    failures = []
    targets = [c for c in CANDIDATES if not args.only or c['id'] == args.only]
    print('========== 阶段 3 版本线索抓取 ==========')
    print(f'核验时间（CST）: {fetched_cst}')
    print(f'候选总数: {len(targets)}' + ('（指定重试）' if args.only else ''))
    print()
    print('| 数据集 | 版本线索来源 | SHA/状态 |')
    print('| --- | --- | --- |')
    for cand in targets:
        did = cand['id']
        snap = snapshot_dir(did)
        clues = []
        try:
            for repo in cand.get('github', []):
                clues.append(fetch_github(repo, snap, fetched_at))
            for ds in cand.get('hf', []):
                clues.append(fetch_hf(ds, snap, fetched_at))
            web_results = []
            for url, note in cand.get('webs', []):
                r = check_web(url, note, snap, fetched_at)
                web_results.append(r)
                clues.append(r)
            if web_results:
                write_web_snapshot(snap, web_results, fetched_at)
            write_file_lf(
                os.path.join(EVIDENCE_ROOT, did, f'version_lock_{SNAPSHOT_DATE}.md'),
                render_lock_md(cand, clues, fetched_cst),
            )
            summary = ' / '.join(
                c['sha'][:12] if c.get('sha') else c['status'] for c in clues
            )
            print(f"| {did} | {', '.join(c['source'] for c in clues)} | {summary} |")
        except Exception as e:
            failures.append((did, str(e)[:120]))
            print(f"| {did} | 抓取失败 | ERROR: {str(e)[:60]} |")
    print()
    if failures:
        print('失败项:')
        for did, err in failures:
            print(f'  - {did}: {err}')
        raise SystemExit(1)
    print('结论: PASS —— 全部候选版本线索已锁定并写入证据包')


def run_validate():
    print('========== 阶段 3 版本线索存档校验（离线） ==========')
    print(f'候选总数: {len(CANDIDATES)}')
    print()
    print('| 数据集 | 锁文件 | API 快照 | License 审查 | 状态 |')
    print('| --- | --- | --- | --- | --- |')
    failures = []
    for cand in CANDIDATES:
        did = cand['id']
        ev_dir = os.path.join(EVIDENCE_ROOT, did)
        locks = sorted(glob.glob(os.path.join(ev_dir, 'version_lock_*.md')))
        snaps = sorted(glob.glob(os.path.join(ev_dir, 'api_snapshot_*')))
        license_review = os.path.join(ev_dir, 'license_review.md')
        has_lock = bool(locks)
        has_snap = bool(snaps) or not (cand.get('github') or cand.get('hf'))
        has_license = os.path.isfile(license_review)
        lock_ok = False
        if has_lock:
            with open(locks[-1], 'r', encoding='utf-8') as f:
                text = f.read()
            lock_ok = ('SHA' in text or 'Revision' in text or 'HTTP' in text) and '存档文件' in text
        problems = []
        if not has_lock:
            problems.append('缺 version_lock_*.md')
        elif not lock_ok:
            problems.append('锁文件缺少 SHA/HTTP 或存档指引字段')
        if not has_snap:
            problems.append('缺 api_snapshot_*/')
        if not has_license:
            problems.append('缺 license_review.md')
        status = 'OK' if not problems else 'FAIL: ' + '; '.join(problems)
        if problems:
            failures.append((did, problems))
        print(f"| {did} | {'有' if has_lock else '无'} | {'有' if has_snap else '无'} | "
              f"{'有' if has_license else '无'} | {status} |")
    print()
    if failures:
        print('失败项（Gate 3 版本验收不通过）:')
        for did, problems in failures:
            print(f"  - {did}: {'; '.join(problems)}")
        raise SystemExit(1)
    print('结论: PASS —— 全部候选版本线索存档齐备')


def main():
    parser = argparse.ArgumentParser(description='阶段 3 候选数据集版本线索锁定与校验')
    parser.add_argument('--fetch', action='store_true',
                        help='抓取模式: 在线调用 GitHub/HF API 并写入证据包（默认为离线校验模式）')
    parser.add_argument('--proxy', default=None,
                        help='可选代理，如 http://127.0.0.1:7890；未指定时遵循 HTTP(S)_PROXY 环境变量')
    parser.add_argument('--insecure', action='store_true', help='跳过 TLS 证书校验（仅限调试）')
    parser.add_argument('--only', default=None,
                        help='只抓取指定 dataset_id（用于失败重试，不重跑全部候选）')
    args = parser.parse_args()

    setup_stdout_utf8()
    set_proxy(args.proxy)
    if args.insecure:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
    if args.fetch:
        run_fetch(args)
    else:
        run_validate()


if __name__ == '__main__':
    main()
