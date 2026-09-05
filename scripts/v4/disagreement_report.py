#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Disagreement Report（P2-A 工具 T09，Data-B/R）
只聚类 A/B 差异，不生成 final_label。同类>=3 -> STOP_THE_LINE_GUIDELINE_DEFECT。
用法：python scripts/v4/disagreement_report.py --a <A labels> --b <B labels> [--out reports/reviewer_queue.csv]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(path):
    rows = {}
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        print("FAIL_CLOSED: missing", p)
        sys.exit(3)
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                rows[r["sample_id"]] = r
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", default="reports/reviewer_queue.csv")
    args = ap.parse_args()

    A, B = load(args.a), load(args.b)
    disagreements = []
    for sid in A:
        if sid not in B:
            continue
        if A[sid].get("label") != B[sid].get("label"):
            disagreements.append({"sample_id": sid, "label_a": A[sid].get("label"), "label_b": B[sid].get("label")})
    same_rule = {}
    for d in disagreements:
        key = d["label_a"] + "|" + d["label_b"]
        same_rule.setdefault(key, []).append(d["sample_id"])
    stop_the_line = [k for k, v in same_rule.items() if len(v) >= 3]

    lines = ["sample_id,label_a,label_b"]
    for d in disagreements:
        lines.append("%s,%s,%s" % (d["sample_id"], d["label_a"], d["label_b"]))
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("written:", out)
    print("disagreements=%d stop_the_line_rule_groups=%d" % (len(disagreements), len(stop_the_line)))
    if stop_the_line:
        print("STOP_THE_LINE_GUIDELINE_DEFECT:", stop_the_line)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()