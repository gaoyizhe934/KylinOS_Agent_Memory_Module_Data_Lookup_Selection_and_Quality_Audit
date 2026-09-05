#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Blind Packet Builder（P2-A 工具 T07，Data-B/R）
从 Admission PASS 抽 fresh N，剥离 gold/candidate label/peer/reviewer/old-trial，生成 A/B 不同随机顺序，记录 seed/hash。
盲包泄漏断言：blind packet 禁止出现 expected/design/target/negative/resolution/scope_target/peer/reviewer/gold。
用法：python scripts/v4/build_blind_packets.py --input <glob> --count 40 --seed-a 11 --seed-b 22 [--out-dir data/interim/blind_context_v4]
"""
import argparse
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
    rows = []
    for pat in paths:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--count", type=int, default=40)
    ap.add_argument("--seed-a", type=int, default=11)
    ap.add_argument("--seed-b", type=int, default=22)
    ap.add_argument("--out-dir", default="data/interim/blind_context_v4")
    args = ap.parse_args()

    rows = load_rows(args.input)
    if len(rows) < args.count:
        print("FAIL_CLOSED: input rows %d < count %d" % (len(rows), args.count))
        sys.exit(2)

    def make_packet(seed):
        rnd = random.Random(seed)
        idx = rnd.sample(range(len(rows)), args.count)
        packet = []
        for i in idx:
            r = rows[i]
            bv = r.get("blind_visible", r)
            # 泄漏断言：blind-visible 不得含设计字段
            leaked = [t for t in FORBIDDEN if t in json.dumps(bv, ensure_ascii=False)]
            if leaked:
                print("BLIND_LEAK:", r.get("sample_id"), leaked)
                sys.exit(2)
            packet.append({"sample_id": r.get("sample_id"), "task_type": r.get("task_type"), "language": r.get("language"),
                           "input": bv.get("input", bv)})
        return packet

    pa = make_packet(args.seed_a)
    pb = make_packet(args.seed_b)
    if [x["sample_id"] for x in pa] == [x["sample_id"] for x in pb]:
        print("BLIND_LEAK: identical order A/B")
        sys.exit(2)

    out_dir = os.path.join(ROOT, args.out_dir)
    os.makedirs(out_dir, exist_ok=True)
    for name, pkt in (("context_A.jsonl", pa), ("context_B.jsonl", pb)):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            for x in pkt:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    manifest = {
        "schema": "blind_manifest", "version": "v4.1", "seed_a": args.seed_a, "seed_b": args.seed_b,
        "count": args.count,
        "hash_a": hashlib.sha256(open(os.path.join(out_dir, "context_A.jsonl"), "rb").read()).hexdigest(),
        "hash_b": hashlib.sha256(open(os.path.join(out_dir, "context_B.jsonl"), "rb").read()).hexdigest(),
    }
    with open(os.path.join(out_dir, "blind_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("written:", out_dir)
    print(manifest)
    sys.exit(0)


if __name__ == "__main__":
    main()