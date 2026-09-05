#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Grouped Split（P2-A 工具 T11，Data-B/R）
按 group_key(user/session/scenario_family/source_group) 整组切分 50/20/30；0 group 跨 split 才 PASS。
用法：python scripts/v4/split_grouped.py --input <glob> [--out reports/split_manifest.csv]
"""
import argparse
import glob
import hashlib
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def group_key(r):
    raw = json.dumps({
        "user": r.get("scenario_user_ref") or r.get("user_id"),
        "session": r.get("conversation_id"),
        "family": r.get("design_metadata", {}).get("scenario_family") or r.get("template_family"),
        "source": r.get("source"),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--seed", type=int, default=20260905)
    ap.add_argument("--out", default="reports/split_manifest.csv")
    args = ap.parse_args()

    rows = []
    for pat in args.input:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))

    groups = {}
    for r in rows:
        g = group_key(r)
        groups.setdefault(g, []).append(r.get("sample_id"))
    gids = list(groups.keys())
    rnd = random.Random(args.seed)
    rnd.shuffle(gids)
    n = len(gids)
    n_dev = int(round(n * 0.5))
    n_reg = int(round(n * 0.2))
    assign = {}
    for i, g in enumerate(gids):
        assign[g] = "dev" if i < n_dev else ("regression" if i < n_dev + n_reg else "sealed_test")

    lines = ["group_key,split,sample_count"]
    cross = 0
    seen = {}
    for r in rows:
        g = group_key(r)
        s = assign[g]
        if r.get("sample_id") in seen and seen[r["sample_id"]] != s:
            cross += 1
        seen[r["sample_id"]] = s
        lines.append("%s,%s,%d" % (g, s, len(groups[g])))

    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("written:", out)
    print("groups=%d cross_split=%d" % (len(gids), cross))
    sys.exit(2 if cross else 0)


if __name__ == "__main__":
    main()