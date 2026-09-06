#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Provenance Resolver（P2-A 工具 T03，Data-B）
真实 join source_registry.csv + license_registry.csv；locator 必须可解析（文件真实存在）；0 unresolved 才 PASS。
零匹配 glob / Registry 缺失 -> nonzero（fail-closed）。
退出码：0=PASS；2=存在 unresolved / 空输入 / Registry 缺失；3=环境错误。
用法：python scripts/v4/provenance_resolver.py --input <glob> [--out reports/prov_report.json]
"""
import argparse
import csv
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_CSV = os.path.join(ROOT, "registry", "source_registry.csv")
LIC_CSV = os.path.join(ROOT, "registry", "license_registry.csv")


def read_csv(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return {r["dataset_id"]: r for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--out", default="reports/prov_report.json")
    args = ap.parse_args()

    src_reg = read_csv(SRC_CSV)
    lic_reg = read_csv(LIC_CSV)
    if src_reg is None or lic_reg is None:
        print("FAIL_CLOSED: source/license registry missing")
        sys.exit(3)

    checked = 0
    unresolved = []
    for pat in args.input:
        matched = glob.glob(os.path.join(ROOT, pat))
        if not matched:
            unresolved.append({"pattern": pat, "reason": "glob 零匹配（fail-closed）"})
            continue
        for p in matched:
            try:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        r = json.loads(line)
                        sid = r.get("sample_id")
                        checked += 1
                        gen = r.get("design_metadata", {}).get("generation", {})
                        src = r.get("source") or gen.get("source")
                        sfile = r.get("source_file") or gen.get("source_file")
                        missing = []
                        if not src:
                            missing.append("source")
                        if not sfile:
                            missing.append("source_file")
                        elif not os.path.exists(os.path.join(ROOT, sfile)):
                            missing.append("locator_not_resolvable:" + sfile)
                        if src:
                            ds = os.path.basename(sfile).split(".")[0] if sfile else src
                            if ds not in src_reg:
                                missing.append("dataset_not_in_source_registry")
                            if ds not in lic_reg:
                                missing.append("dataset_not_in_license_registry")
                        if missing:
                            unresolved.append({"sample_id": sid, "missing": missing, "file": os.path.relpath(p, ROOT)})
            except Exception as e:
                unresolved.append({"file": os.path.relpath(p, ROOT), "error": str(e)})

    if checked == 0 and not unresolved:
        unresolved.append({"reason": "零样本输入（fail-closed）"})

    report = {
        "schema": "prov_report", "version": "v4.1", "tool": "provenance_resolver.py",
        "input": args.input, "checked": checked, "unresolved": unresolved, "unresolved_count": len(unresolved),
        "gates": {"G1_provenance_unresolved_zero": len(unresolved) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("checked=%d unresolved=%d" % (checked, len(unresolved)))
    sys.exit(2 if unresolved else 0)


if __name__ == "__main__":
    main()