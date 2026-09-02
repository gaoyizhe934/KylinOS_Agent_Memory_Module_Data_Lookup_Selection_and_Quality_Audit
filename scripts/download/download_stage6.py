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
import hashlib
import os
import ssl
import sys
import urllib.request
from datetime import datetime

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


def fetch(url, out, timeout=90, insecure=False):
    # P0-1: 默认开启证书校验（CERT_REQUIRED），仅当显式 --insecure 才放宽（调试用，不用于正式冻结）。
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    last = None
    for cand in mirror_candidates(url):
        for _ in range(2):
            part = out + ".part"
            try:
                req = urllib.request.Request(cand, headers=UA)
                sha = hashlib.sha256()
                total = 0
                # P2-1: 流式分块写入，避免 277MB/3.6GB 文件 OOM。
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                    with open(part, "wb") as fh:
                        while True:
                            chunk = resp.read(8192)
                            if not chunk:
                                break
                            fh.write(chunk)
                            sha.update(chunk)
                            total += len(chunk)
                os.replace(part, out)
                # P2-3: 下载后立即计算 SHA256（配合 B 侧 manifest/哈希交叉验证）。
                return cand, total, sha.hexdigest()
            except Exception as e:
                last = e
                try:
                    os.remove(part)
                except OSError:
                    pass
    raise last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--proxy", default=None)
    ap.add_argument("--insecure", action="store_true", help="禁用SSL证书校验（仅调试，不用于正式冻结）")
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
        # P1-3/P1-4: 追加模式 + 分隔行，保留历史与人工 NOTE 记录，避免覆盖 B 侧交叉验证痕迹。
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[run {datetime.now().isoformat(timespec='seconds')}] dataset_id={t['dataset_id']} subset={t['subset']}\n")
            for url in t["urls"]:
                fname = os.path.basename(url.split("?")[0]) or "sample"
                out = os.path.join(sub, fname)
                try:
                    used, n, sha = fetch(url, out, insecure=args.insecure)
                    line = f"OK\t{n}\t{sha[:16]}\t{used}\t{url}"
                    print("  OK", fname, n, "bytes via", used, "sha", sha[:16])
                except Exception as e:
                    line = f"FAIL\t{url}\t{str(e)[:120]}"
                    print("  FAIL", url, str(e)[:120])
                log.write(line + "\n")
        print("  log:", log_path)


if __name__ == "__main__":
    main()