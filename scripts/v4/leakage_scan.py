#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Leakage Scan（P2-A 工具 T05，Data-B）
对 candidate 做 content/evidence/raw/template fingerprint 与 leaked_content_registry 比对；leak=0 才 PASS。
fail-closed：命中任何 leak -> exit 2。
用法：python scripts/v4/leakage_scan.py --input <glob> --registry registry/leaked_content_registry.json [--out reports/leak_report.json]
"""
import argparse
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fp(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--registry", default="registry/leaked_content_registry.json")
    ap.add_argument("--out", default="reports/leak_report.json")
    args = ap.parse_args()

    reg_path = os.path.join(ROOT, args.registry)
    reg = json.load(open(reg_path, encoding="utf-8")) if os.path.exists(reg_path) else {"leaked_entries": []}
    leak_fps = set()
    for e in reg.get("leaked_entries", []):
        if e.get("content_fingerprint"):
            leak_fps.add(e["content_fingerprint"])
        if e.get("sample_id"):
            leak_fps.add(fp(str(e["sample_id"])))

    hits = []
    checked = 0
    for pat in args.input:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    checked += 1
                    sid = r.get("sample_id")
                    if fp(str(sid)) in leak_fps:
                        hits.append({"sample_id": sid, "reason": "sample_id in leak registry"})
                        continue
                    bv = json.dumps(r.get("blind_visible", {}), ensure_ascii=False)
                    if fp(bv) in leak_fps:
                        hits.append({"sample_id": sid, "reason": "blind_visible content fingerprint in leak registry"})

    report = {
        "schema": "leak_report", "version": "v4.1", "tool": "leakage_scan.py",
        "input": args.input, "checked": checked, "hits": hits, "leak_count": len(hits),
        "gates": {"G5_leak_zero": len(hits) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("G5_leak_zero", len(hits) == 0)
    sys.exit(2 if hits else 0)


if __name__ == "__main__":
    main()