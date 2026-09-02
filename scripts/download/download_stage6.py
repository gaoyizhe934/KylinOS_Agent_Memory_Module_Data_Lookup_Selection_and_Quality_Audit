# -*- coding: utf-8 -*-
"""阶段 6（A 侧）：正式下载脚本（镜像路由）— Annotator A（lyf-1213）

下载范围：阶段 5 评审通过、可进入正式下载的候选（核心 + 补充），
按官方版本锁定下载固定评测子集到 data/raw/<dataset>/v0_subset/。

镜像路由策略：
- HuggingFace 官方域受限时回退 hf-mirror.com；
- raw.githubusercontent.com 受限时回退 gh-proxy.com / ghproxy.net；
- 仍失败时可用 --proxy http://127.0.0.1:7890 显式走代理。

不下载（License 待决 / 淘汰 / 方法参考）：dureader_retrieval_2022、
personachat_2018、msmarco_2021、trec_tracks_2024、toolbench_2024、
bpmn_2_0_2013、machine_unlearning_bench_2025。

说明：SHA256 / manifest / 只读冻结由 Annotator B 在阶段 6 校验环节执行，
本脚本只负责下载与镜像路由，产出 data/raw 数据与 download.log。
"""

import argparse
import os
import ssl
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../oneclick")
try:
    from net_utils import set_proxy
except Exception:
    set_proxy = None

UA = {"User-Agent": "Mozilla/5.0"}

# 阶段 5 通过、允许正式下载的候选及其固定子集 URL（按版本锁定）
SUBSETS = [
    {
        "dataset_id": "longmemeval_cleaned_2025",
        "subset": "v0_subset",
        "urls": [
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_oracle.json",
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json",
        ],
        "note": "核心候选；oracle(首选)+S cleaned 固定子集（不取 M 全量）。",
    },
    {
        "dataset_id": "longmemeval_v2_2026",
        "subset": "v0_subset",
        "urls": [
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/resolve/main/questions.jsonl",
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/resolve/main/trajectories.jsonl",
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/resolve/main/SCHEMA.md",
            "https://huggingface.co/datasets/xiaowu0162/longmemeval-v2/resolve/main/LICENSE",
        ],
        "note": "核心候选；questions + trajectories 固定子集 + SCHEMA/LICENSE。",
    },
    {
        "dataset_id": "t2ranking_2023",
        "subset": "v0_subset",
        "urls": [
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/queries.dev.tsv",
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/qrels.retrieval.dev.tsv",
            "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/collection.tsv",
        ],
        "note": "核心候选（中文检索）；dev 查询+qrels+collection 固定子集。",
    },
    {
        "dataset_id": "stabletoolbench_2024",
        "subset": "v0_subset",
        "urls": [
            "https://raw.githubusercontent.com/THUNLP-MT/StableToolBench/master/solvable_queries_example/test_instruction/G1_instruction.json",
        ],
        "note": "补充候选；官方 data_example 固定样例（完整静态子集下载受网络限制时记录阻塞）。",
    },
    {
        "dataset_id": "multiwoz_2_2_2020",
        "subset": "v0_subset",
        "urls": [
            "https://raw.githubusercontent.com/budzianowski/multiwoz/master/data/MultiWOZ_2.2/dev/dialogues_001.json",
        ],
        "note": "补充候选（辅助/负样本）；dev 子集固定样例。",
    },
]


def mirror_candidates(url):
    cands = [url]
    if url.startswith("https://huggingface.co/"):
        cands.append(url.replace("https://huggingface.co/", "https://hf-mirror.com/", 1))
    if url.startswith("https://raw.githubusercontent.com/"):
        cands.append("https://gh-proxy.com/" + url)
        cands.append("https://ghproxy.net/" + url)
    if url.startswith("https://github.com/"):
        cands.append("https://gh-proxy.com/" + url)
    return list(dict.fromkeys(cands))


def fetch(url, out, timeout=90):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    last = None
    for cand in mirror_candidates(url):
        for _ in range(2):
            try:
                req = urllib.request.Request(cand, headers=UA)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    data = resp.read()
                with open(out, "wb") as fh:
                    fh.write(data)
                return cand, len(data)
            except Exception as e:
                last = e
    raise last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--proxy", default=None)
    args = ap.parse_args()

    if args.proxy and set_proxy:
        set_proxy(args.proxy)
        print("[proxy]", args.proxy)

    for t in SUBSETS:
        if args.dataset and t["dataset_id"] != args.dataset:
            continue
        print("=" * 60)
        print("[download]", t["dataset_id"], "-", t["note"])
        sub = os.path.join(args.out, t["dataset_id"], t["subset"])
        os.makedirs(sub, exist_ok=True)
        log_path = os.path.join(sub, "download.log")
        with open(log_path, "w", encoding="utf-8") as log:
            log.write(f"dataset_id={t['dataset_id']}\n")
            log.write(f"subset={t['subset']}\n")
            for url in t["urls"]:
                fname = os.path.basename(url.split("?")[0]) or "sample"
                out = os.path.join(sub, fname)
                try:
                    used, n = fetch(url, out)
                    line = f"OK\t{n}\t{used}\t{url}"
                    print("  OK", fname, n, "bytes via", used)
                except Exception as e:
                    line = f"FAIL\t{url}\t{str(e)[:120]}"
                    print("  FAIL", url, str(e)[:120])
                log.write(line + "\n")
        print("  log:", log_path)


if __name__ == "__main__":
    main()