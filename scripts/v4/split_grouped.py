#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Grouped Split（P2-A 工具 T11，Data-B/R）
按 group_key(user/session/scenario_family/source_group) 整组切分 50/20/30；0 group 跨 split 才 PASS。
输出 split_manifest.csv（group_key,split,sample_count）与 split_samples.csv（sample_id,group_key,split）机器映射（供 T12）。
用法：python scripts/v4/split_grouped.py --input <glob> [--seed 20260905] [--out reports/split_manifest.csv]
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
    ap.add_argument("--samples-out", default="reports/split_samples.csv")
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

    # 校验 0 group 跨 split
    sample_split = {}
    for r in rows:
        sample_split[r.get("sample_id")] = assign[group_key(r)]
    group_split_seen = {}
    cross = 0
    for g, sids in groups.items():
        s = assign[g]
        for sid in sids:
            if group_split_seen.get(g) is None:
                group_split_seen[g] = s
            elif group_split_seen[g] != s:
                cross += 1

    lines = ["group_key,split,sample_count"]
    for g in gids:
        lines.append("%s,%s,%d" % (g, assign[g], len(groups[g])))
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    slines = ["sample_id,group_key,split"]
    for sid, g in sorted((sid, group_key(next(r for r in rows if r.get("sample_id") == sid))) for sid in sample_split):
        slines.append("%s,%s,%s" % (sid, g, sample_split[sid]))
    sout = os.path.join(ROOT, args.samples_out)
    os.makedirs(os.path.dirname(sout), exist_ok=True)
    with open(sout, "w", encoding="utf-8") as f:
        f.write("\n".join(slines) + "\n")
    print("written:", os.path.relpath(out, ROOT), os.path.relpath(sout, ROOT))
    print("groups=%d samples=%d cross_split=%d" % (len(gids), len(sample_split), cross))
    sys.exit(2 if cross else 0)


if __name__ == "__main__":
    main()