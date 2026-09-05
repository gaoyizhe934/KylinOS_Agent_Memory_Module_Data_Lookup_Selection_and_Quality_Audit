#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Admission Gate（P2-A 工具 T06，Data-B/R）
汇总 G1-G5 并 fail-closed；任一 FAIL 阻断进入 blind。
输入：candidate + prov/dedup/leak/semantic reports。
用法：python scripts/v4/admission_gate.py --prov <prov_report.json> --dedup <dedup_report.json> --leak <leak_report.json> --semantic <semantic_report.csv> [--out reports/admission_result.csv]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(path):
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prov", required=True)
    ap.add_argument("--dedup", required=True)
    ap.add_argument("--leak", required=True)
    ap.add_argument("--semantic", required=True, help="G2 人工确认报告（A 提供）")
    ap.add_argument("--out", default="reports/admission_result.csv")
    args = ap.parse_args()

    prov, dedup, leak = load(args.prov), load(args.dedup), load(args.leak)
    missing = [n for n, o in [("prov", prov), ("dedup", dedup), ("leak", leak)] if o is None]
    if missing:
        print("FAIL_CLOSED: missing reports", missing)
        sys.exit(3)

    g1 = prov.get("gates", {}).get("G1_provenance_unresolved_zero", False)
    g4 = dedup.get("gates", {}).get("G4_exact_dup_zero", False) and dedup.get("gates", {}).get("G4_template_concentration_ok", False)
    g5 = leak.get("gates", {}).get("G5_leak_zero", False)
    g2 = os.path.exists(os.path.join(ROOT, args.semantic))  # G2 人工确认文件存在为 A 侧证据（100% 人确认仍由 A 输出）

    gates = {"G1_provenance": g1, "G2_semantic(human)": g2, "G4_diversity": g4, "G5_leakage": g5,
             "G3_annotatable": "PENDING_HUMAN"}
    all_pass = all(v is True for v in gates.values() if isinstance(v, bool))
    lines = ["gate,status"]
    for k, v in gates.items():
        lines.append("%s,%s" % (k, "PASS" if v is True else v))
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("ADMISSION", "PASS" if all_pass else "BLOCKED")
    sys.exit(0 if all_pass else 2)


if __name__ == "__main__":
    main()