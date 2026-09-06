#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B3：Retrieval G4 t2ranking 单源 ≤25% 分层选择（Data-B，2026-09-06）

口径（Data-R B1/B3）：admitted Retrieval Gold 单源 ≤25%；Retrieval 目标 175 → t2ranking ≤43。
输入：200 条 t2ranking（legacy 可复用候选，license 已批）。
方法：可复现 max-min 多样性选择（farthest-point sampling）：
  1) query 归一化 + token（bigram/字符）Jaccard 相似度；
  2) 贪心：seed 固定，首条取 query_id 中位；每次取与已选集最小最大相似度最大的样本；
     tie 按 query_id 升序 → 完全确定性；
  3) 选 N=43 代表；其余 157 保留 Candidate/History（不删除）。
输出：选择包 json（含 seed/algo/input_hash/output_hash/sample 清单）。
G4 结论保持 fail-closed：不因本选择将 G4 改 PASS（t2ranking 集中度最终在 admitted 集复算）。
"""
import argparse
import hashlib
import json
import math
import os
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

    # first: query_id median index
    mid = sorted(range(total), key=lambda i: int(queries[i][2]))[total // 2]
    selected = [mid]
    # tie-breaker deterministic: prefer larger min-distance; tie by original index asc (already query_id sorted)
    for _ in range(1, args.n):
        best_i, best_score = -1, -1.0
        for i in range(total):
            if i in selected:
                continue
            # min similarity to selected
            mn = min(jac(queries[i][0], queries[j][0]) for j in selected)
            # maximize min-distance (1 - similarity) => minimize max similarity; maximize (1-mn)
            score = 1.0 - mn
            if score > best_score + 1e-12:
                best_score, best_i = score, i
            elif abs(score - best_score) <= 1e-12 and best_i != -1:
                # tie: lower query_id first (already sorted -> keep earlier)
                pass
        selected.append(best_i)

    chosen = [queries[i] for i in selected]
    chosen_sorted = sorted(chosen, key=lambda c: int(c[2]))
    sel_ids = [c[1] for c in chosen_sorted]

    # hashes
    src_raw = open(path, "rb").read()
    input_hash = hashlib.sha256(src_raw).hexdigest()
    out_text = "\n".join(sel_ids) + "\n"
    output_hash = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    result = {
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
    }
    outp = os.path.join(ROOT, args.out)
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("selected:", len(sel_ids), "of", total)
    print("sample selected ids:", sel_ids[:8], "...")
    print("output_hash:", output_hash)


if __name__ == "__main__":
    main()
