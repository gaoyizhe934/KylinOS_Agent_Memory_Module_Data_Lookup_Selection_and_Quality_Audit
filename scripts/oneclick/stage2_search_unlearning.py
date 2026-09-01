# -*- coding: utf-8 -*-
"""阶段 2: 检索机器遗忘/精准遗忘相关公开数据集（HuggingFace API）。"""
import argparse
import urllib.parse

from net_utils import fetch_json, set_proxy, setup_stdout_utf8

DATASET_API = 'https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench'


def hf_search(query, limit=10, timeout=20, insecure=False):
    url = 'https://huggingface.co/api/datasets?search=' + urllib.parse.quote(query) + '&limit=' + str(limit)
    return fetch_json(url, timeout=timeout, insecure=insecure)


def main():
    parser = argparse.ArgumentParser(description='检索 HuggingFace 上的机器遗忘相关数据集')
    parser.add_argument('--proxy', default=None,
                        help='可选代理，如 http://127.0.0.1:7890；未指定时遵循 HTTP(S)_PROXY 环境变量')
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--insecure', action='store_true', help='跳过 TLS 证书校验（仅限调试）')
    args = parser.parse_args()

    setup_stdout_utf8()
    set_proxy(args.proxy)

    print('=== machine-unlearning-bench/data-unlearning-bench ===')
    try:
        info = fetch_json(DATASET_API, timeout=args.timeout, insecure=args.insecure)
        desc = info.get('description', '')
        card = info.get('cardData', {})
        print(f'  description: {str(desc)[:200]}')
        print(f'  downloads: {info.get("downloads", 0)}')
        print(f"  license: {card.get('license', 'N/A')}")
        print(f'  siblings: {len(info.get("siblings", []))} files')
    except Exception as e:
        print(f'  [FAIL] {str(e)[:80]}')

    queries = ['machine unlearning', 'unlearning', 'forgetting', 'knowledge unlearning', 'model unlearning']
    for q in queries:
        print(f'\n=== 搜索: {q} ===')
        try:
            results = hf_search(q, timeout=args.timeout, insecure=args.insecure)
            for d in results:
                did = d.get('id', '')
                dl = d.get('downloads', 0)
                if dl > 50:  # 只显示有一定下载量的
                    print(f'  {did} (downloads={dl})')
        except Exception as e:
            print(f'  [FAIL] {str(e)[:80]}')


if __name__ == '__main__':
    main()
