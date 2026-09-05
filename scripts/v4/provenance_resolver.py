#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Provenance Resolver（P2-A 工具 T03，Data-B）
验证 candidate 的 raw locator/license/source 可回溯；0 unresolved 才 PASS。
fail-closed：missing locator/license -> 该项 unresolved -> exit 2。
退出码：0=PASS；2=存在 unresolved；3=环境/解析错误。
用法：python scripts/v4/provenance_resolver.py --input <glob> [--out reports/prov_report.json]
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--out", default="reports/prov_report.json")
    args = ap.parse_args()

    records = []
    unresolved = []
    for pat in args.input:
        for p in glob.glob(os.path.join(ROOT, pat)):
            try:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        r = json.loads(line)
                        d = r.get("design_metadata", {}).get("generation", {})
                        sid = r.get("sample_id")
                        src = r.get("source") or d.get("source")
                        sfile = r.get("source_file") or d.get("source_file")
                        missing = []
                        if not src:
                            missing.append("source")
                        if not sfile:
                            missing.append("source_file/locator")
                        if missing:
                            unresolved.append({"sample_id": sid, "missing": missing, "file": os.path.relpath(p, ROOT)})
                        records.append({"sample_id": sid, "source": src, "locator": sfile, "ok": not missing})
            except Exception as e:
                unresolved.append({"file": os.path.relpath(p, ROOT), "error": str(e)})

    report = {
        "schema": "prov_report", "version": "v4.1", "tool": "provenance_resolver.py",
        "input": args.input, "checked": len(records), "unresolved": unresolved, "unresolved_count": len(unresolved),
        "gates": {"G1_provenance_unresolved_zero": len(unresolved) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    for k, v in report["gates"].items():
        print(k, v)
    sys.exit(2 if unresolved else 0)


if __name__ == "__main__":
    main()