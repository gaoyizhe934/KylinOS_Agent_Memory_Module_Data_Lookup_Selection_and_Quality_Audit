# -*- coding: utf-8 -*-
"""阶段 2: 检查登记表数据集 URL 可访问性（Gate 2 URL 验收命令）。

用法（在仓库根目录执行）:
    python scripts/oneclick/stage2_check_urls.py
    python scripts/oneclick/stage2_check_urls.py --proxy http://127.0.0.1:7890

路径从脚本位置（仓库根目录）自动解析，不依赖绝对路径；
代理默认遵循 HTTP_PROXY/HTTPS_PROXY 环境变量，可用 --proxy 显式指定。

退出码（默认严格模式）:
    0  = 全部 URL 可访问（无 EMPTY / ERROR / TIMEOUT）
    1  = 存在未登记（EMPTY）或不可访问（ERROR / TIMEOUT）的 URL
加 --report-only 仅输出报告、退出码恒为 0（用于人工核对，不作验收）。
"""
import argparse
import csv
import os

from net_utils import check_url, set_proxy, setup_stdout_utf8

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_registry(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description='检查 dataset_registry.csv 中各数据集官方/数据 URL 可访问性')
    parser.add_argument('--registry', default=os.path.join(REPO_ROOT, 'registry', 'dataset_registry.csv'),
                        help='登记表路径（默认: 仓库根目录下 registry/dataset_registry.csv）')
    parser.add_argument('--proxy', default=None,
                        help='可选代理，如 http://127.0.0.1:7890；未指定时遵循 HTTP(S)_PROXY 环境变量')
    parser.add_argument('--timeout', type=int, default=8, help='单个 URL 超时秒数（默认 8）')
    parser.add_argument('--insecure', action='store_true', help='跳过 TLS 证书校验（仅限调试）')
    parser.add_argument('--report-only', action='store_true',
                        help='仅输出报告，不按失败条件设置退出码（不作验收使用）')
    args = parser.parse_args()

    setup_stdout_utf8()
    set_proxy(args.proxy)
    rows = load_registry(args.registry)

    # 豁免列表：已裁决不参与 URL 验收的数据集
    # 精确匹配，只有 toolbench_2024 被裁决为数据入口失效
    # 仅豁免结论为"方法论参考"的数据集不强制验收（仍需检查并输出报告）
    SKIP_DATA_URL_DATASETS = {'toolbench_2024'}

    print('========== 现有数据集 URL 可访问性检查 ==========')
    print(f'登记表: {os.path.relpath(args.registry, REPO_ROOT)}')
    print(f'数据集总数: {len(rows)}')
    print(f'豁免 data_url 检查（已裁决数据入口失效）: {sorted(SKIP_DATA_URL_DATASETS) if SKIP_DATA_URL_DATASETS else "无"}')
    print()
    print('| 数据集 | 官方URL | 状态 | 下载URL | 状态 |')
    print('| --- | --- | --- | --- | --- |')
    counts = {'OK': 0, 'EMPTY': 0, 'ERROR': 0, 'TIMEOUT': 0}
    failures = []
    for row in rows:
        did = row['dataset_id']
        official = (row.get('official_url') or '').strip()
        data_url = (row.get('data_url') or '').strip()
        # 检查官方 URL（不可跳过，必须存在）
        s1 = check_url(official, timeout=args.timeout, insecure=args.insecure)
        # 豁免已裁决数据入口失效的数据集的 data_url 检查
        if did in SKIP_DATA_URL_DATASETS:
            s2 = ('EMPTY', '已裁决数据入口失效，豁免检查')
        else:
            s2 = check_url(data_url, timeout=args.timeout, insecure=args.insecure)
        counts[s1[0]] += 1
        counts[s2[0]] += 1
        print(f'| {did} | {official[:50]} | {s1[0]}:{s1[1]} | {data_url[:50]} | {s2[0]}:{s2[1]} |')
        for field, status in ((f'{did} official_url', s1), (f'{did} data_url', s2)):
            if status[0] != 'OK':
                failures.append((field, status))

    total = len(rows)
    print()
    print(f'统计（{total} 个数据集 x 官方/下载两列，共 {total * 2} 项）: '
          f"OK={counts['OK']}  EMPTY={counts['EMPTY']}  ERROR={counts['ERROR']}  TIMEOUT={counts['TIMEOUT']}")
    print('说明: OK=可访问, EMPTY=登记表未填写该 URL, ERROR=不可访问, TIMEOUT=超时')

    if failures:
        print()
        print('失败项（URL 验收失败条件，须逐项处置后方可通过）:')
        for field, status in failures:
            print(f'  - {field}: {status[0]} {status[1]}')
        if not args.report_only:
            print()
            print('结论: FAIL —— 存在未登记或不可访问的 URL')
            raise SystemExit(1)
    elif not args.report_only:
        print()
        print('结论: PASS —— 全部 URL 均可访问')


if __name__ == '__main__':
    main()
