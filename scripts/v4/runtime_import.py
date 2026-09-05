#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Runtime Importer（P2-A 工具 T10，Data-B）
只解析 actual trace/status/evidence；缺任一关键证据 -> RUNTIME_EVIDENCE_MISSING / fail-closed。
用法：python scripts/v4/runtime_import.py --logs <trace jsonl> [--out reports/runtime_parse.json]
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", nargs="+", required=True)
    ap.add_argument("--out", default="reports/runtime_parse.json")
    args = ap.parse_args()

    events = []
    missing = []
    for pat in args.logs:
        for p in glob.glob(os.path.join(ROOT, pat)):
            try:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        ev = json.loads(line)
                        need = ["trace_id", "tool_call_id", "status", "input_ref", "output_ref"]
                        lacks = [k for k in need if k not in ev or not ev[k]]
                        if lacks:
                            missing.append({"event": ev.get("tool_call_id"), "missing": lacks, "file": os.path.relpath(p, ROOT)})
                            continue
                        events.append(ev)
            except Exception as e:
                missing.append({"file": os.path.relpath(p, ROOT), "error": str(e)})

    report = {
        "schema": "runtime_parse", "version": "v4.1", "tool": "runtime_import.py",
        "events": events, "event_count": len(events),
        "evidence_missing": missing, "missing_count": len(missing),
        "runtime_eligible": len(missing) == 0,
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("events=%d missing=%d eligible=%s" % (len(events), len(missing), report["runtime_eligible"]))
    if missing:
        print("RUNTIME_EVIDENCE_MISSING")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()