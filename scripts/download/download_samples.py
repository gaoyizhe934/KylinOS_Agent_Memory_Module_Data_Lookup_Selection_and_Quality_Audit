# -*- coding: utf-8 -*-
"""Public dataset sample downloader. Usage: python download_samples.py --limit 100"""
import argparse
import json
import os
import ssl
import sys
import time
import urllib.request

TARGETS = [
    {
        "dataset_id": "longmemeval_cleaned_2025",
        "urls": [
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_oracle.json",
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json"
        ],
        "note": "只下载 oracle（首选）或 S cleaned；不要下载 M 全量。"
    },
    {
        "dataset_id": "t2ranking_2023",
        "urls": [
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/queries.dev.tsv",
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/qrels.retrieval.dev.tsv",
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/collection.tsv"
        ],
        "note": "collection 较大，可先用 dev 查询+qrels 作为小样本。"
    },
    {
        "dataset_id": "multiwoz_2_2_2020",
        "urls": [
            "https://raw.githubusercontent.com/budzianowski/multiwoz/master/data/MultiWOZ_2.2/dev/dialogues_001.json"
        ],
        "note": "dev 子集已下载并抽样 100 条；如需更多样本可下载 dialogues_002.json 或 train/test。"
    },
    {
        "dataset_id": "dureader_retrieval_2022",
        "urls": [],
        "note": "按百度官方 README/千言渠道下载，抽样 50-100 条。"
    },
    {
        "dataset_id": "stabletoolbench_2024",
        "urls": [
            "https://raw.githubusercontent.com/THUNLP-MT/StableToolBench/master/solvable_queries_example/test_instruction/G1_instruction.json"
        ],
        "note": "data_example 为官方样例；完整静态子集按官方发布渠道下载。"
    }
]

def mirror_candidates(url):
    cands = [url]
    if url.startswith('https://huggingface.co/'):
        cands.append(url.replace('https://huggingface.co/', 'https://hf-mirror.com/', 1))
    if url.startswith('https://raw.githubusercontent.com/'):
        cands.append('https://gh-proxy.com/' + url)
        cands.append('https://ghproxy.net/' + url)
    if url.startswith('https://github.com/'):
        cands.append('https://gh-proxy.com/' + url)
    return list(dict.fromkeys(cands))

def fetch(url, out, timeout=90):
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    last = None
    for cand in mirror_candidates(url):
        for attempt in range(2):
            try:
                req = urllib.request.Request(cand, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    data = resp.read()
                    with open(out, 'wb') as fh: fh.write(data)
                return len(data)
            except Exception as e:
                last = e
    raise last

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default=None)
    ap.add_argument('--limit', type=int, default=100)
    ap.add_argument('--out', default='data/raw')
    args = ap.parse_args()
    for t in TARGETS:
        if args.dataset and t['dataset_id'] != args.dataset: continue
        print('[download]', t['dataset_id'], t['note'])
        if not t['urls']:
            print('  官方渠道需人工确认 URL，跳过。')
            continue
        for url in t['urls'][:2]:
            fname = os.path.basename(url.split('?')[0]) or 'sample'
            out = os.path.join(args.out, t['dataset_id'], 'v0_sample', fname)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            try:
                n = fetch(url, out)
                print('  OK', fname, n, 'bytes')
            except Exception as e:
                print('  FAIL', url, str(e)[:120])
    print('[done] Run sha256 and update manifests after downloads.')

if __name__ == '__main__':
    main()
