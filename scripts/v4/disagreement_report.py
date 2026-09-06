#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Disagreement Report（P2-A 工具 T09，Data-B/R）
只聚类 A/B 差异，不生成 final_label。fail-closed：
- A/B 输入必须非空、sample_id 唯一；
- set(A)==set(B)（缺失/额外 sample 一律 FAIL_CLOSED）；
- 可选 --manifest 绑定 blind_manifest（A/B membership hash 与 manifest 一致）。
同类>=3 -> STOP_THE_LINE_GUIDELINE_DEFECT。
退出码：0=无分歧；2=分歧或 A/B 结构不一致；3=输入缺失。
用法：python scripts/v4/disagreement_report.py --a <A labels> --b <B labels> [--manifest blind_manifest.json] [--out reports/reviewer_queue.csv]
"""
import argparse
import hashlib
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
    seen_dup = False
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                sid = r.get("sample_id")
                if sid in rows:
                    seen_dup = True
                rows[sid] = r
    return rows, seen_dup


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--manifest", default="", help="blind_manifest.json（A/B 冻结 membership）")
    ap.add_argument("--out", default="reports/reviewer_queue.csv")
    args = ap.parse_args()

    A, a_dup = load(args.a)
    B, b_dup = load(args.b)
    if a_dup or b_dup:
        print("FAIL_CLOSED: duplicate sample_id in A/B labels")
        sys.exit(2)
    if not A or not B:
        print("FAIL_CLOSED: A/B labels empty")
        sys.exit(2)
    if set(A.keys()) != set(B.keys()):
        missing = set(A.keys()) - set(B.keys())
        extra = set(B.keys()) - set(A.keys())
        print("FAIL_CLOSED: A/B membership mismatch missing=%s extra=%s" % (sorted(missing), sorted(extra)))
        sys.exit(2)
    if args.manifest:
        mp = os.path.join(ROOT, args.manifest)
        if not os.path.exists(mp):
            print("FAIL_CLOSED: blind manifest missing")
            sys.exit(3)
        man = json.load(open(mp, encoding="utf-8"))
        mhash = man.get("frozen_membership_hash")
        if mhash:
            cur = hashlib.sha256(json.dumps(sorted(A.keys())).encode("utf-8")).hexdigest()
            if cur != mhash:
                print("FAIL_CLOSED: A/B membership != blind manifest frozen membership")
                sys.exit(2)

    disagreements = []
    for sid in A:
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
    print("A=%d B=%d disagreements=%d stop_the_line_groups=%d" % (len(A), len(B), len(disagreements), len(stop_the_line)))
    if stop_the_line:
        print("STOP_THE_LINE_GUIDELINE_DEFECT:", stop_the_line)
        sys.exit(2)
    if disagreements:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()