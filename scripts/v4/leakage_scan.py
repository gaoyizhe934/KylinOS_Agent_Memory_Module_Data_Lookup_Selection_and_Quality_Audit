#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Leakage Scan（P2-A 工具 T05，Data-B）
对 candidate 做 content/evidence/raw-span/template/sample-id 全指纹比对 leaked_content_registry；leak=0 才 PASS。
Registry 缺失/解析失败/零 glob 匹配 -> nonzero（fail-closed）。
指纹算法与 leak registry 统一（normalize + sha256）。
用法：python scripts/v4/leakage_scan.py --input <glob> --registry registry/leaked_content_registry.json [--out reports/leak_report.json]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def fp(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def gen_fingerprints(r):
    """统一指纹：sample-id / content / evidence / raw-span / template。"""
    out = set()
    out.add("sid:" + fp(str(r.get("sample_id") or "")))
    out.add("content:" + fp(norm(json.dumps(r.get("blind_visible", {}).get("input", {}), ensure_ascii=False))))
    out.add("evidence:" + fp(norm(json.dumps(r.get("blind_visible", {}).get("inventory_context", r.get("evidence", [])), ensure_ascii=False))))
    out.add("raw:" + fp(norm(json.dumps(r.get("evidence", []), ensure_ascii=False))))
    out.add("template:" + fp(norm(str(r.get("template_family") or ""))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--registry", default="registry/leaked_content_registry.json")
    ap.add_argument("--out", default="reports/leak_report.json")
    args = ap.parse_args()

    reg_path = os.path.join(ROOT, args.registry)
    if not os.path.exists(reg_path):
        print("FAIL_CLOSED: registry missing", reg_path)
        sys.exit(3)
    try:
        reg = json.load(open(reg_path, encoding="utf-8"))
    except Exception as e:
        print("FAIL_CLOSED: registry parse error", e)
        sys.exit(3)

    leak_fps = set()
    for e in reg.get("leaked_entries", []):
        if e.get("content_fingerprint"):
            leak_fps.add("content:" + e["content_fingerprint"])
        if e.get("sample_id"):
            leak_fps.add("sid:" + fp(str(e["sample_id"])))
        if e.get("template_family"):
            leak_fps.add("template:" + fp(norm(e["template_family"])))
        if e.get("evidence_fingerprint"):
            leak_fps.add("evidence:" + e["evidence_fingerprint"])

    checked = 0
    hits = []
    for pat in args.input:
        matched = glob.glob(os.path.join(ROOT, pat))
        if not matched:
            print("FAIL_CLOSED: glob 零匹配", pat)
            sys.exit(2)
        for p in matched:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    checked += 1
                    sid = r.get("sample_id")
                    fgrps = gen_fingerprints(r)
                    hit = fgrps & leak_fps
                    if hit:
                        hits.append({"sample_id": sid, "matched_fingerprints": sorted(hit)})

    if checked == 0:
        print("FAIL_CLOSED: 零样本输入")
        sys.exit(2)

    report = {
        "schema": "leak_report", "version": "v4.1", "tool": "leakage_scan.py",
        "input": args.input, "checked": checked, "hits": hits, "leak_count": len(hits),
        "fingerprint_coverage": ["content", "evidence", "raw", "template", "sample_id"],
        "gates": {"G5_leak_zero": len(hits) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("checked=%d leak=%d" % (checked, len(hits)))
    sys.exit(2 if hits else 0)


if __name__ == "__main__":
    main()