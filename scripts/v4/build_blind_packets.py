#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Blind Packet Builder（P2-A 工具 T07，Data-B/R）
先冻结同一组 fresh sample membership（Admission PASS），再为 A/B 生成不同随机顺序。
断言：set(A_ids)==set(B_ids) 且 order(A)!=order(B)；盲包泄漏断言。
输入必须来自 Admission PASS manifest（T06 admission_result.csv）。
用法：python scripts/v4/build_blind_packets.py --input <glob> --admission <admission_result.csv> --count 40 --seed-a 11 --seed-b 22 [--out-dir data/interim/blind_context_v4]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORBIDDEN = ["expected", "design", "target_ids", "must_keep", "hard_negative", "negative", "resolution",
             "scope_target", "peer", "reviewer", "gold", "winner", "conflict_type", "forget_mode", "scenario_class", "template_family"]


def load_rows(paths):
    rows = {}
    for pat in paths:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        rows[r.get("sample_id")] = r
    return rows


def load_admitted(admission_csv):
    p = os.path.join(ROOT, admission_csv)
    if not os.path.exists(p):
        print("FAIL_CLOSED: admission manifest missing", p)
        sys.exit(3)
    admitted = set()
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("admission") == "PASS":
                admitted.add(row.get("sample_id"))
    if not admitted:
        print("FAIL_CLOSED: admission manifest has 0 PASS")
        sys.exit(2)
    return admitted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--admission", required=True)
    ap.add_argument("--count", type=int, default=40)
    ap.add_argument("--seed-a", type=int, default=11)
    ap.add_argument("--seed-b", type=int, default=22)
    ap.add_argument("--out-dir", default="data/interim/blind_context_v4")
    args = ap.parse_args()

    rows = load_rows(args.input)
    admitted = load_admitted(args.admission)
    pool = [sid for sid in rows if sid in admitted]
    if len(pool) < args.count:
        print("FAIL_CLOSED: admitted pool %d < count %d" % (len(pool), args.count))
        sys.exit(2)

    # 冻结同一组 membership（一次选择）
    frozen = random.Random(args.seed_a + args.seed_b).sample(sorted(pool), args.count)

    def packet(seed):
        order = frozen[:]
        random.Random(seed).shuffle(order)
        out = []
        for sid in order:
            r = rows[sid]
            bv = r.get("blind_visible", r)
            leaked = [t for t in FORBIDDEN if t in json.dumps(bv, ensure_ascii=False)]
            if leaked:
                print("BLIND_LEAK:", sid, leaked)
                sys.exit(2)
            out.append({"sample_id": sid, "task_type": r.get("task_type"), "language": r.get("language"),
                        "input": bv.get("input", bv)})
        return out, order

    pa, ids_a = packet(args.seed_a)
    pb, ids_b = packet(args.seed_b)
    assert set(ids_a) == set(frozen) and set(ids_b) == set(frozen)
    if set(ids_a) != set(ids_b):
        print("BLIND_LEAK: A/B membership differ")
        sys.exit(2)
    if ids_a == ids_b:
        print("BLIND_LEAK: A/B order identical")
        sys.exit(2)

    out_dir = os.path.join(ROOT, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    for name, pkt in (("context_A.jsonl", pa), ("context_B.jsonl", pb)):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            for x in pkt:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    manifest = {
        "schema": "blind_manifest", "version": "v4.1", "count": args.count,
        "frozen_membership_hash": hashlib.sha256(json.dumps(sorted(frozen)).encode("utf-8")).hexdigest(),
        "seed_a": args.seed_a, "seed_b": args.seed_b,
        "hash_a": hashlib.sha256(open(os.path.join(out_dir, "context_A.jsonl"), "rb").read()).hexdigest(),
        "hash_b": hashlib.sha256(open(os.path.join(out_dir, "context_B.jsonl"), "rb").read()).hexdigest(),
        "admission_source": args.admission,
    }
    with open(os.path.join(out_dir, "blind_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("written:", out_dir)
    print(manifest)
    sys.exit(0)


if __name__ == "__main__":
    main()