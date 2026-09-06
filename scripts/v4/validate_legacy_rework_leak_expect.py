# -*- coding: utf-8 -*-
"""Data-A A1 leak expectation checker（Option2，响应 Data-R #44）
断言 canonical leakage 的 hits 恰好 ⊆ manifest.exposed_lineage_blocked 登记的 leak_key；
不引入新的未登记泄漏；命中条目不得视为 completion-ready（B1 必须给 BLOCKED）。
用法：python scripts/v4/validate_legacy_rework_leak_expect.py --leak reports/leak_report.json \
      --manifest data/interim/d1_legacy_rework_A_20260906/generation_manifest_A_20260906.json
"""
import argparse
import json
import sys

P = __file__
ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leak", required=True)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args()
    leak = json.load(open(args.leak, encoding="utf-8"))
    mf = json.load(open(args.manifest, encoding="utf-8"))
    allowed = set((it.get("leak_key") for it in mf.get("exposed_lineage_blocked", {}).get("items", [])))
    hits = set()
    for h in leak.get("hits", []):
        hits |= set(h.get("matched_fingerprints", []))
    unexpected = sorted(hits - allowed)
    missing = sorted(allowed - hits)
    print("leak_count=%d hits_in_manifest=%d unexpected=%s missing_expected=%s" % (leak.get("leak_count"), len(hits & allowed), unexpected, missing))
    ok = leak.get("leak_count", 0) == len(hits) and not unexpected and not missing
    print("RESULT:", "PASS (no unexpected leak; hits == manifest exposed_lineage_blocked)" if ok else "FAIL")
    if not ok:
        sys.exit(1)
    print("NOTE: matched candidates are LEAK_EXPOSED/BLOCKED (Option2) and are NOT completion-ready / accepted_legacy.")
    sys.exit(0)


if __name__ == "__main__":
    main()
