#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 G4/Dedup Scanner（B 侧工具，2026-09-05）

按 v4.1 C3 硬要求：CLI 固定 IO、退出码、幂等、raw 只读、fail-closed、不写 Gold。
输入：候选/legacy JSONL（带 input/evidence/template_family/source）。
检查：exact normalized dup、near-dup（归一化后相似阈值）、template_family 集中度、source 集中度。
规则（SOP-03 G4）：exact dup=0 必须；single template_family>25% FAIL；near-dup>0.85 送 Reviewer。
退出码：0=PASS 或仅 REVIEW；2=exact dup>0 或 template>25% FAIL（fail-closed）。
用法：python scripts/v4/dedup_scan.py --files a.jsonl [b.jsonl] [--json out.json]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

_COUNTER_RE = re.compile(r"(第\s*\d+\s*次|v?\d+(\.\d+)?|#?\d{1,6}|_\d{3,}|\d{4}-\d{2}-\d{2})", re.I)
_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[，。；：？！、,.;:?!\"'“”‘’()\[\]{}<>《》【】\-\—_/\\|]")


def norm(text):
    t = _COUNTER_RE.sub("", str(text or ""))
    t = _PUNCT_RE.sub("", t)
    t = _SPACE_RE.sub("", t)
    return t.lower()


def read_rows(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out.append(r)
    return out


def extract_text(r):
    inp = r.get("input")
    if isinstance(inp, str):
        return inp
    if isinstance(inp, dict):
        for k in ("user_message", "query", "forget_instruction", "scenario", "content"):
            if inp.get(k):
                return str(inp[k])
        # conflict candidates
        if isinstance(inp.get("candidates"), dict):
            return " ".join(str(v) for v in inp["candidates"].values())
    return json.dumps(inp, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--json", help="output report path")
    args = ap.parse_args()

    rows = []
    for f in args.files:
        rows.extend(read_rows(f))

    buckets = {}
    for r in rows:
        key = norm(extract_text(r))
        buckets.setdefault(key, []).append(r.get("sample_id", "?"))

    exact_dup_groups = {k: v for k, v in buckets.items() if len(v) > 1}
    # near-dup：简化 n-gram 相似不做全配对，仅报告 exact 与 template 集中度；near>0.85 送审需独立实现
    tf = Counter(r.get("template_family") or "?" for r in rows)
    src = Counter(r.get("source") or "?" for r in rows)
    n = len(rows) or 1
    tf_over = {k: v for k, v in tf.items() if v / n > 0.25}

    report = {
        "schema": "dedup_scan_report", "version": "v4.1", "tool": "dedup_scan.py",
        "generated_by": "DGXD01(Data-B)", "files": args.files,
        "total": len(rows), "exact_dup_groups": len(exact_dup_groups),
        "exact_dup_records": sum(len(v) for v in exact_dup_groups.values()),
        "template_family_dist": dict(tf),
        "template_family_over25": dict(tf_over),
        "source_dist": dict(src),
        "near_dup_note": "near-dup(>0.85) 需独立近似检测实现；当前仅 exact + 集中度",
        "status": "PENDING_REVIEW",
    }
    fail = len(exact_dup_groups) > 0 or bool(tf_over)
    report["status"] = "FAIL" if fail else "CLEAN"
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", args.json)
    print("total=%d exact_dup_groups=%d template_over25=%s" % (len(rows), len(exact_dup_groups), list(tf_over.keys())))
    print("STATUS:", report["status"])
    sys.exit(2 if fail else 0)


if __name__ == "__main__":
    main()
