#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Runtime Importer（P2-A 工具 T10，Data-B）
只解析 actual trace/status/side-effect/checkpoint 证据；缺任一关键证据 -> RUNTIME_EVIDENCE_MISSING（fail-closed）。
按 Tool/E2E 类型验证：tool 需 side-effect evidence；e2e 需 checkpoint chain。
Frozen Build 身份必须一致；零日志 -> 不 eligible。
用法：python scripts/v4/runtime_import.py --logs <trace jsonl> --build <frozen_build_manifest.json> [--type tool|e2e] [--out reports/runtime_parse.json]
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
    ap.add_argument("--build", required=True, help="Frozen Build manifest（含 build_hash）")
    ap.add_argument("--type", choices=["tool", "e2e"], default="tool")
    ap.add_argument("--out", default="reports/runtime_parse.json")
    args = ap.parse_args()

    build_path = os.path.join(ROOT, args.build)
    if not os.path.exists(build_path):
        print("RUNTIME_EVIDENCE_MISSING: frozen build manifest missing", build_path)
        sys.exit(2)
    build = json.load(open(build_path, encoding="utf-8"))
    build_hash = build.get("build_hash") or build.get("frozen_build_hash")

    events = []
    missing = []
    total_log_lines = 0
    for pat in args.logs:
        for p in glob.glob(os.path.join(ROOT, pat)):
            try:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        total_log_lines += 1
                        ev = json.loads(line)
                        lacks = []
                        if not build_hash:
                            lacks.append("frozen_build_hash")
                        if not ev.get("trace_id"):
                            lacks.append("trace_id")
                        if not ev.get("tool_call_id"):
                            lacks.append("tool_call_id")
                        if not ev.get("status"):
                            lacks.append("status")
                        if not ev.get("input_ref"):
                            lacks.append("input_ref")
                        if not ev.get("output_ref"):
                            lacks.append("output_ref")
                        if args.type == "tool" and not ev.get("side_effect_evidence"):
                            lacks.append("side_effect_evidence")
                        if args.type == "e2e" and not ev.get("checkpoint_chain"):
                            lacks.append("checkpoint_chain")
                        if lacks:
                            missing.append({"event": ev.get("tool_call_id"), "missing": lacks, "file": os.path.relpath(p, ROOT)})
                        else:
                            events.append(ev)
            except Exception as e:
                missing.append({"file": os.path.relpath(p, ROOT), "error": str(e)})

    if total_log_lines == 0:
        print("RUNTIME_EVIDENCE_MISSING: 零日志匹配")
        sys.exit(2)

    report = {
        "schema": "runtime_parse", "version": "v4.1", "tool": "runtime_import.py",
        "type": args.type, "frozen_build_hash": build_hash,
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
    print("log_lines=%d events=%d missing=%d eligible=%s" % (total_log_lines, len(events), len(missing), report["runtime_eligible"]))
    if missing:
        print("RUNTIME_EVIDENCE_MISSING")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()