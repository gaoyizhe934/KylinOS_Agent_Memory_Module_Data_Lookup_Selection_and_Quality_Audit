#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Admission Gate（P2-A 工具 T06，Data-B/R）

逐样本 join：candidate_id -> G1/G2/G3/G4/G5；五项必须全部显式 PASS。
候选集必须非空且 sample_id 唯一；prov/dedup/leak 报告必须输出 checked_sample_ids/input_set_hash；
断言 candidate_set == prov_set == dedup_set == leak_set；缺任一样本证据 => FAIL_CLOSED。
G1/G4/G5 来自报告逐样本 samples 映射（不再 blanket PASS）；unresolved_count 关键字段缺失不能默认 0。
退出码：0=PASS；2=FAIL_CLOSED；3=缺报告/环境。
用法：见脚本内注释。
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

    # 关键字段缺失不能默认 0
    for name, rpt, field in [("prov", prov, "unresolved_count"), ("leak", leak, "leak_count")]:
        if field not in rpt:
            print("FAIL_CLOSED: %s missing field %s" % (name, field))
            sys.exit(2)
    # dedup schema（与 T04 输出一致）
    for field in ["exact_duplicate_groups", "near_duplicate_pairs", "near_duplicate_decisions", "near_blocked",
                  "template_over_concentration", "samples", "checked_sample_ids"]:
        if field not in dedup:
            print("FAIL_CLOSED: dedup missing required field %s" % field)
            sys.exit(2)

    # 候选集
    cands = []
    for pat in args.candidates:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        cands.append(json.loads(line).get("sample_id"))
    if not cands:
        print("FAIL_CLOSED: candidate set empty")
        sys.exit(2)
    if len(set(cands)) != len(cands):
        print("FAIL_CLOSED: candidate sample_id not unique")
        sys.exit(2)
    cset = set(cands)

    # 报告集合一致性
    pset = set(prov.get("checked_sample_ids", []))
    dset = set(dedup.get("checked_sample_ids", []))
    lset = set(leak.get("checked_sample_ids", []))
    if not pset or not dset or not lset:
        print("FAIL_CLOSED: report checked_sample_ids empty/missing")
        sys.exit(2)
    if not (cset == pset == dset == lset):
        print("FAIL_CLOSED: set mismatch candidates=%d prov=%d dedup=%d leak=%d" % (len(cset), len(pset), len(dset), len(lset)))
        sys.exit(2)

    # G4 显式判定（不硬编码）：exact / near / template 三项
    dgates = dedup.get("gates", {})
    if not (dgates.get("G4_exact_dup_zero") and dgates.get("G4_near_reviewed") and dgates.get("G4_template_concentration_ok")):
        print("FAIL_CLOSED: dedup G4 gates not clean", dgates)
        sys.exit(2)
    dedup_s = dedup.get("samples", {})

    # 逐样本 join
    prov_s = prov.get("samples", {})
    leak_s = leak.get("samples", {})
    lines = ["sample_id,g1,g2,g3,g4,g5,admission"]
    admitted = 0
    for sid in sorted(cset):
        g1 = "PASS" if prov_s.get(sid, {}).get("ok") else "FAIL"
        g5 = "PASS" if leak_s.get(sid, {}).get("ok") else "FAIL"
        g4 = "PASS" if dedup_s.get(sid, {}).get("ok") else "FAIL"
        g2s = g2.get(sid) or "MISSING"
        g3s = g3.get(sid) or "MISSING"
        ok = (g1 == "PASS" and g2s == "PASS" and g3s == "PASS" and g4 == "PASS" and g5 == "PASS")
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