#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B3：Retrieval G4 t2ranking 单源 ≤25% 选择（Data-B，2026-09-06）

口径（Data-R B1/B3）：admitted Retrieval Gold 单源 ≤25%；Retrieval 目标 175 → t2ranking ≤43。
输入：200 条 t2ranking（legacy 可复用候选，license 已批）。
方法：可复现 **全局** farthest-point（max-min）多样性选择（不做稳定分层；如需分层见 B3 报告口径说明）：
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
import collections
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
    queries = [(r.get("input", {}).get("query", ""), r.get("sample_id", ""), r.get("input", {}).get("query_id"), r.get("template_family", "")) for r in rows]
    def qfield(i, idx):
        return queries[i][idx]
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
    src_text = open(path, encoding="utf-8").read()
    canon_src = "\n".join(l.rstrip("\r\n") for l in src_text.split("\n")).rstrip("\n") + "\n"
    input_hash = hashlib.sha256(canon_src.encode("utf-8")).hexdigest()
    out_text = "\n".join(sel_ids) + "\n"
    output_hash = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    # diversity diagnostics (rich, Data-R Round2 Blocking-3)
    import statistics
    sel_q = [queries[i] for i in selected]
    pair_sims = []
    nn_max = []
    for a in range(len(sel_q)):
        mx = 0.0
        for b in range(len(sel_q)):
            if a == b:
                continue
            sim = jac(sel_q[a][0], sel_q[b][0])
            pair_sims.append(sim)
            if sim > mx:
                mx = sim
        nn_max.append(mx)
    pair_sims_sorted = sorted(pair_sims)
    def pct(arr, p):
        if not arr:
            return None
        k = int(round((len(arr) - 1) * p))
        return arr[k]
    # query length bins
    len_bins = collections.Counter()
    for q in sel_q:
        L = len(q[0])
        if L <= 8:
            len_bins["<=8"] += 1
        elif L <= 12:
            len_bins["9-12"] += 1
        elif L <= 16:
            len_bins["13-16"] += 1
        else:
            len_bins[">16"] += 1
    # template family coverage (source vs selected)
    fam_all = collections.Counter(q[3] for q in queries)
    fam_sel = collections.Counter(q[3] for q in sel_q)
    def top_share(counter, total):
        if not total:
            return {}
        return {k: round(v / total, 4) for k, v in counter.most_common(3)}
    # exact duplicate queries in source
    dup = len(queries) - len({q[0] for q in queries})
    result = {
        "diversity_diagnostics": {
            "n_selected": args.n,
            "method_note": "全局 farthest-point(非稳定分层)：score=1-max(sim to selected); seed=%d via random.Random" % args.seed,
            "pairwise_sim": {
                "max": round(max(pair_sims), 4) if pair_sims else None,
                "p95": round(pct(pair_sims_sorted, 0.95), 4) if pair_sims else None,
                "median": round(pct(pair_sims_sorted, 0.5), 4) if pair_sims else None,
                "mean": round(sum(pair_sims) / len(pair_sims), 4) if pair_sims else None,
            },
            "nearest_neighbor_maxsim": {
                "max": round(max(nn_max), 4) if nn_max else None,
                "p95": round(pct(sorted(nn_max), 0.95), 4) if nn_max else None,
                "median": round(pct(sorted(nn_max), 0.5), 4) if nn_max else None,
            },
            "query_length_bins_selected": dict(len_bins),
            "template_family_share_source": top_share(fam_all, len(queries)),
            "template_family_share_selected": top_share(fam_sel, len(sel_q)),
            "source_exact_duplicate_query_count": dup,
            "query_id_sample": [q[2] for q in sel_q[:5]],
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
    # canonical output hash binds FULL result (selected + diagnostics), not just IDs
    result["output_hash_sha256"] = hashlib.sha256(
        json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    outp = os.path.join(ROOT, args.out)
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("selected:", len(sel_ids), "of", total)
    print("sample selected ids:", sel_ids[:8], "...")
    print("output_hash:", output_hash)


if __name__ == "__main__":
    main()
