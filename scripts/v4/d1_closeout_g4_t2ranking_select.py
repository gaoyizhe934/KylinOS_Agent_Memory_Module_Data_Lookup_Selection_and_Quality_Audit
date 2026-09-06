#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B3：Retrieval G4 t2ranking 单源 ≤25% 分层选择（Data-B，2026-09-06）

口径（Data-R B1/B3）：admitted Retrieval Gold 单源 ≤25%；Retrieval 目标 175 → t2ranking ≤43。
输入：200 条 t2ranking（legacy 可复用候选，license 已批）。
方法：可复现 max-min 多样性选择（farthest-point sampling）：
  1) query 归一化 + token（bigram/字符）Jaccard 相似度；
  2) 贪心（正确 farthest-point）：每次取 score = 1 - max(与已选集的相似度) 最大者
     （即真正最小化“到最近已选点”的相似度 / 最大化 min-distance）；
     seed 通过 random.Random(seed) 决定首条随机选择与 tie 打破 → 完全确定性可复现；
  3) 选 N=43 代表；其余 157 保留 Candidate/History（不删除）。
输出：选择包 json（含 seed/algo/input_hash/output_hash/sample 清单）。
G4 结论保持 fail-closed：不因本选择将 G4 改 PASS（t2ranking 集中度最终在 admitted 集复算）。
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = "data/processed/knowledge_retrieval_t2ranking.jsonl"


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def toks(s):
    out = []
    for t in re.split(r"[\s_\-/]+", norm(s)):
        if not t:
            continue
        if re.search(r"[\u4e00-\u9fff]", t):
            out.extend(list(t))
        else:
            out.append(t)
    return out


def jac(a, b):
    sa, sb = set(toks(a)), set(toks(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=43)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--out", default="reports/v4.1_D1_closeout_G4_t2ranking_select_20260906.json")
    args = ap.parse_args()

    path = os.path.join(ROOT, SRC)
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    if len(rows) < args.n:
        print("FAIL: source rows", len(rows), "< n", args.n)
        sys.exit(2)

    # stable order by query_id then sample_id
    rows = sorted(rows, key=lambda r: (int(r.get("input", {}).get("query_id", -1)), r.get("sample_id", "")))
    queries = [(r.get("input", {}).get("query", ""), r.get("sample_id", ""), r.get("input", {}).get("query_id")) for r in rows]
    total = len(queries)

    rng = random.Random(args.seed)
    # first: seeded random start (deterministic given seed)
    selected = [rng.randrange(total)]
    # farthest-point: score = 1 - max(similarity to selected)  (minimize max-sim)
    for _ in range(1, args.n):
        best_i, best_score = -1, -1.0
        best_tie = []
        for i in range(total):
            if i in selected:
                continue
            mx = max(jac(queries[i][0], queries[j][0]) for j in selected)
            score = 1.0 - mx
            if score > best_score + 1e-12:
                best_score, best_i, best_tie = score, i, [i]
            elif abs(score - best_score) <= 1e-12:
                best_tie.append(i)
        # tie-break by seeded shuffle
        if len(best_tie) > 1:
            rng.shuffle(best_tie)
            best_i = best_tie[0]
        selected.append(best_i)

    chosen = [queries[i] for i in selected]
    chosen_sorted = sorted(chosen, key=lambda c: int(c[2]))
    sel_ids = [c[1] for c in chosen_sorted]

    # hashes
    src_raw = open(path, "rb").read()
    input_hash = hashlib.sha256(src_raw).hexdigest()
    out_text = "\n".join(sel_ids) + "\n"
    output_hash = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    # diversity diagnostics
    import statistics
    sel_idx_set = set(selected)
    pair_max = []
    pair_mean = []
    sel_queries = [queries[i][0] for i in selected]
    for a in range(len(sel_queries)):
        for b in range(a + 1, len(sel_queries)):
            sim = jac(sel_queries[a], sel_queries[b])
            pair_max.append(sim)
            pair_mean.append(sim)
    sims = sorted(pair_max, reverse=True)
    result = {
        "diversity_diagnostics": {
            "n_selected": args.n,
            "pairwise_sim_max": round(max(pair_max), 4) if pair_max else None,
            "pairwise_sim_top5": [round(x, 4) for x in sims[:5]],
            "pairwise_sim_mean": round(sum(pair_mean) / len(pair_mean), 4) if pair_mean else None,
            "query_len_min_max": [min(len(q) for q in sel_queries), max(len(q) for q in sel_queries)],
            "query_id_coverage": "分散抽样于 source（见 selected_sample_ids 对应 query_id）",
            "algorithm": "farthest-point: score=1-max(sim to selected); seed=%d via random.Random" % args.seed,
        },
    }
    result.update({
        "schema": "g4_t2ranking_select",
        "version": "v4.1",
        "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)",
        "basis": "Data-R B1/B3：admitted Retrieval Gold 单源≤25%（175→≤43）",
        "method": "max-min diversity (farthest-point sampling); seed=%d" % args.seed,
        "n_selected": len(sel_ids),
        "total_source": total,
        "kept_as_candidate_history": total - len(sel_ids),
        "input_file": SRC,
        "input_hash_sha256": input_hash,
        "output_hash_sha256": output_hash,
        "selected_sample_ids": sel_ids,
        "note": "G4 仍 fail-closed：最终 template 集中度在 admitted 集复算；剩余 157 保留 Candidate/History 不删除",
    })
    outp = os.path.join(ROOT, args.out)
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("selected:", len(sel_ids), "of", total)
    print("sample selected ids:", sel_ids[:8], "...")
    print("output_hash:", output_hash)


if __name__ == "__main__":
    main()
