# -*- coding: utf-8 -*-
"""阶段 2: 查询 machine-unlearning-bench 数据集详细卡片与 README（HuggingFace API）。"""
import argparse

from net_utils import fetch_json, fetch_text, set_proxy, setup_stdout_utf8

DATASET_API = 'https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench'
README_URL = 'https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench/raw/main/README.md'


def main():
    parser = argparse.ArgumentParser(description='获取 machine-unlearning-bench 详细卡片信息与 README')
    parser.add_argument('--proxy', default=None,
                        help='可选代理，如 http://127.0.0.1:7890；未指定时遵循 HTTP(S)_PROXY 环境变量')
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--insecure', action='store_true', help='跳过 TLS 证书校验（仅限调试）')
    args = parser.parse_args()

    setup_stdout_utf8()
    set_proxy(args.proxy)

    info = fetch_json(DATASET_API, timeout=args.timeout, insecure=args.insecure)
    card = info.get('cardData', {})
    print('=== 详细卡片信息 ===')
    print(f'  cardData keys: {list(card.keys())}')
    print(f"  license: {card.get('license', 'N/A')}")
    print(f'  tags: {info.get("tags", [])[:15]}')

    print()
    print('=== README 前800字 ===')
    readme = fetch_text(README_URL, timeout=args.timeout, insecure=args.insecure)
    print(readme[:800])
    print()
    print('=== README 总长度 ===')
    print(f'{len(readme)} chars')


if __name__ == '__main__':
    main()
