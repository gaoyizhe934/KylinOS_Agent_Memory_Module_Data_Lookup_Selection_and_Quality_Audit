#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Leakage Scan（P2-A 工具 T05，Data-B）

统一 leak fingerprint contract：sample_id + content + evidence + raw identity/span + template。
Registry loader 装载全部指纹键（含 raw_id/raw_fingerprint/raw_span）。
Registry 缺失/解析失败/零 glob/零样本 -> nonzero。
输出含 checked_sample_ids + input_set_hash（供 T06 join）。
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
FINGERPRINT_CONTRACT = ["sample_id", "content", "evidence", "raw_identity_span", "template"]


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def fp(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def gen_fingerprints(r):
    out = set()
    sid = str(r.get("sample_id") or "")
    raw = str(r.get("raw_id") or r.get("source_event_id") or "")
    out.add("sid:" + fp(sid))
    out.add("content:" + fp(norm(json.dumps(r.get("blind_visible", {}).get("input", {}), ensure_ascii=False))))
    out.add("evidence:" + fp(norm(json.dumps(r.get("blind_visible", {}).get("inventory_context", r.get("evidence", [])), ensure_ascii=False))))
    out.add("raw:" + fp(norm(raw)))
    out.add("template:" + fp(norm(str(r.get("template_family") or ""))))
    return out


def input_set_hash(ids):
    return hashlib.sha256(json.dumps(sorted(ids)).encode("utf-8")).hexdigest()


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
        if e.get("evidence_fingerprint"):
            leak_fps.add("evidence:" + e["evidence_fingerprint"])
        if e.get("sample_id"):
            leak_fps.add("sid:" + fp(str(e["sample_id"])))
        if e.get("template_family"):
            leak_fps.add("template:" + fp(norm(e["template_family"])))
        # raw identity / span / raw_fingerprint
        raw_id = e.get("raw_id") or e.get("source_event_id")
        if raw_id:
            leak_fps.add("raw:" + fp(norm(str(raw_id))))
        if e.get("raw_fingerprint"):
            leak_fps.add("raw:" + e["raw_fingerprint"])
        if e.get("raw_span"):
            leak_fps.add("raw:" + fp(norm(e["raw_span"])))

    checked = []
    hits = []
    samples = {}
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
                    sid = r.get("sample_id")
                    checked.append(sid)
                    hit = gen_fingerprints(r) & leak_fps
                    samples[sid] = {"ok": not hit, "hit": sorted(hit)}
                    if hit:
                        hits.append({"sample_id": sid, "matched_fingerprints": sorted(hit)})

    if not checked:
        print("FAIL_CLOSED: 零样本输入")
        sys.exit(2)

    report = {
        "schema": "leak_report", "version": "v4.1", "tool": "leakage_scan.py",
        "input": args.input, "checked": len(checked),
        "checked_sample_ids": sorted(set(checked)), "input_set_hash": input_set_hash(set(checked)),
        "fingerprint_contract": FINGERPRINT_CONTRACT, "fingerprint_algo": "normalize+sha256",
        "samples": samples, "hits": hits, "leak_count": len(hits),
        "gates": {"G5_leak_zero": len(hits) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("checked=%d leak=%d" % (len(checked), len(hits)))
    sys.exit(2 if hits else 0)


if __name__ == "__main__":
    main()