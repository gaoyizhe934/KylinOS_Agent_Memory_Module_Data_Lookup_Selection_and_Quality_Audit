#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Admission Gate（P2-A 工具 T06，Data-B/R）
逐样本 join：candidate_id -> G1/G2/G3/G4/G5；五项必须全部显式 PASS 才能 Admission PASS。
缺样本、缺报告、PENDING、NEEDS_REVIEW、near-dup 未裁决均 fail-closed（exit 2）。
用法：
  python scripts/v4/admission_gate.py \
    --candidates <glob> \
    --prov <prov_report.json> --dedup <dedup_report.json> --leak <leak_report.json> \
    --semantic <g2.csv> --annotatable <g3.csv> \
    [--out reports/admission_result.csv]
"""
import argparse
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_json(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_csv_map(rel, gate_col):
    """返回 {sample_id: gate_status}；status 必须是 PASS，否则 fail。"""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    m = {}
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            m[row.get("sample_id", "")] = (row.get(gate_col) or "").strip().upper()
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", nargs="+", required=True)
    ap.add_argument("--prov", required=True)
    ap.add_argument("--dedup", required=True)
    ap.add_argument("--leak", required=True)
    ap.add_argument("--semantic", required=True, help="G2 逐样本 CSV(sample_id,gate2)")
    ap.add_argument("--annotatable", required=True, help="G3 逐样本 CSV(sample_id,gate3)")
    ap.add_argument("--out", default="reports/admission_result.csv")
    args = ap.parse_args()

    prov, dedup, leak = load_json(args.prov), load_json(args.dedup), load_json(args.leak)
    g2, g3 = load_csv_map(args.semantic, "gate2"), load_csv_map(args.annotatable, "gate3")
    missing = [n for n, o in [("prov", prov), ("dedup", dedup), ("leak", leak), ("semantic", g2), ("annotatable", g3)] if o is None]
    if missing:
        print("FAIL_CLOSED: missing reports", missing)
        sys.exit(3)

    # 机器 Gate 全局 fail-closed
    g1_ok = prov.get("unresolved_count", 0) == 0
    g4_ok = (not dedup.get("exact_duplicate_groups", {}) and
             dedup.get("near_duplicate_count", 1) == 0 and
             not dedup.get("template_over_concentration", []))
    g5_ok = leak.get("leak_count", 1) == 0
    if not (g1_ok and g4_ok and g5_ok):
        print("FAIL_CLOSED: machine gates not clean", {"g1": g1_ok, "g4": g4_ok, "g5": g5_ok})
        sys.exit(2)

    # candidate 列表
    cands = []
    for pat in args.candidates:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        cands.append(json.loads(line).get("sample_id"))

    lines = ["sample_id,g1,g2,g3,g4,g5,admission"]
    admitted = 0
    for sid in cands:
        g1 = "PASS"
        g2s = g2.get(sid)
        g3s = g3.get(sid)
        if g2s is None or g2s not in ("PASS",):
            g2s = g2s or "MISSING"
        if g3s is None or g3s not in ("PASS",):
            g3s = g3s or "MISSING"
        g4 = "PASS"
        g5 = "PASS"
        ok = (g2s == "PASS" and g3s == "PASS")
        lines.append("%s,%s,%s,%s,%s,%s,%s" % (sid, g1, g2s, g3s, g4, g5, "PASS" if ok else "FAIL"))
        if ok:
            admitted += 1

    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("written:", out)
    print("candidates=%d admitted=%d" % (len(cands), admitted))
    if admitted != len(cands):
        print("ADMISSION BLOCKED: %d/%d not fully pass" % (len(cands) - admitted, len(cands)))
        sys.exit(2)
    print("ADMISSION PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()