#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P01 Legacy Inventory（P2-A 工具 T02，Data-B）——逐样本账本 + 优先级 logical dedup + 严格 fail-closed

输出 reports/legacy_inventory_v4_full.jsonl（逐样本账本）+ legacy_inventory_v4.json（summary 由 full 派生）。
logical dedup（明确优先级，非四字段全等）：
  L1 stable sample/raw identity（sample_id 或 raw_id）→ 优先
  L2 content+evidence fingerprint（input+evidence 归一化 hash）
  L3 source/raw locator
每个 logical group 恰好一个 canonical IN_SCOPE，其余 DUPLICATE_FILE 且 duplicate_of 指向 canonical sample_id。
repo_ref 记录真实扫描 HEAD。
fail-closed：任一文件 open / JSONL parse / hash 失败 -> exit 2。
退出码：0=PASS；2=扫描/解析异常。
用法：python scripts/v4/inventory_legacy.py [--out-dir reports]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ERRORS = []


def git_head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, encoding="utf-8").stdout.strip() or "n/a"
    except Exception:
        return "n/a"


def sha256_file(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        ERRORS.append("sha256:%s: %s" % (p, e))
        return None


def fingerprint(s):
    try:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()
    except Exception as e:
        ERRORS.append("fingerprint: %s" % e)
        return None


def read_jsonl(p):
    rows = []
    try:
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    rows.append((i, json.loads(line)))
                except Exception as e:
                    ERRORS.append("jsonl-parse:%s:%d: %s" % (p, i, e))
        return rows
    except Exception as e:
        ERRORS.append("open:%s: %s" % (p, e))
        return []


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def identity(r):
    """返回优先级身份键：L1 sample/raw identity > L2 content+evidence > L3 raw locator。"""
    sid = str(r.get("sample_id") or r.get("id") or "").strip()
    raw = str(r.get("raw_id") or r.get("source_event_id") or "").strip()
    content = norm(json.dumps(r.get("input", {}), ensure_ascii=False))
    ev = norm(json.dumps(r.get("evidence", []), ensure_ascii=False))
    loc = str(r.get("source_file") or "").strip()
    if sid or raw:
        return ("L1", sid, raw)
    ck = fingerprint(content + ev)
    if ck:
        return ("L2", ck, "")
    if loc:
        return ("L3", fingerprint(loc), "")
    return ("L0", fingerprint(json.dumps(r, ensure_ascii=False)), "")


LAYERS = [
    ("gold", "data/gold", "**/*.jsonl"),
    ("processed", "data/processed", "*.jsonl"),
    ("interim_v1", "data/interim", "gold_candidates_*.jsonl"),
]
SKIP_PROCESSED = {"multiwoz"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="reports")
    args = ap.parse_args()

    ref = git_head()
    records = []
    groups = {}  # identity_key -> canonical record
    for layer, rel_dir, pattern in LAYERS:
        for p in sorted(glob.glob(os.path.join(ROOT, rel_dir, pattern), recursive=True)):
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            base = os.path.basename(p)
            if layer == "processed" and any(s in base for s in SKIP_PROCESSED):
                continue
            fsha = sha256_file(p)
            if fsha is None:
                continue
            rows = read_jsonl(p)
            if ERRORS and ERRORS[-1].startswith("open:"):
                continue
            split = os.path.basename(os.path.dirname(p)) if layer == "gold" else ""
            for line_no, r in rows:
                ik = identity(r)
                rec = {
                    "repo_ref": ref, "layer": layer, "split": split,
                    "file_path": rel, "file_sha256": fsha, "line_no": line_no,
                    "sample_id": r.get("sample_id", ""), "task_type": r.get("task_type", ""),
                    "source": r.get("source", ""),
                    "sample_fingerprint": fingerprint(json.dumps(r, ensure_ascii=False)),
                    "label_exposed": r.get("label_exposed", "unknown"),
                    "template_family": r.get("template_family", ""),
                    "inventory_status": "IN_SCOPE", "duplicate_of": "",
                }
                if ik in groups:
                    rec["inventory_status"] = "DUPLICATE_FILE"
                    rec["duplicate_of"] = groups[ik]["sample_id"]
                else:
                    groups[ik] = rec
                records.append(rec)

    if ERRORS:
        print("FAIL_CLOSED:", len(ERRORS))
        for e in ERRORS[:20]:
            print("  ", e)
        sys.exit(2)

    # 断言：每个 duplicate group 恰好 1 个 canonical IN_SCOPE
    dup_groups = {}
    for r in records:
        if r["inventory_status"] == "DUPLICATE_FILE":
            dup_groups.setdefault(r["duplicate_of"], []).append(r["sample_id"])
    bad = [d for d, v in dup_groups.items() if not v]
    if bad:
        print("FAIL_CLOSED: duplicate group without canonical", bad)
        sys.exit(2)

    full = os.path.join(ROOT, args.out_dir, "legacy_inventory_v4_full.jsonl")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    n_in = sum(1 for r in records if r["inventory_status"] == "IN_SCOPE")
    n_dup = sum(1 for r in records if r["inventory_status"] == "DUPLICATE_FILE")
    by_task = {}
    for r in records:
        if r["inventory_status"] == "IN_SCOPE":
            by_task[r["task_type"]] = by_task.get(r["task_type"], 0) + 1
    full_sha = sha256_file(full)
    summary = {
        "schema": "legacy_inventory_v4", "version": "v4.1", "tool": "inventory_legacy.py",
        "generated_by": "DGXD01(Data-B)", "date": "2026-09-05", "status": "NOT_FROZEN",
        "generator_commit": ref, "scan_repo_ref": ref,
        "full_ledger_sha256": full_sha,
        "dedup_policy": "L1 sample/raw identity > L2 content+evidence > L3 raw locator; 每组合一 canonical IN_SCOPE",
        "source": "derived_from_full",
        "summary": {
            "total_records": len(records), "in_scope": n_in, "duplicate_file": n_dup,
            "duplicate_groups": len(dup_groups),
            "in_scope_by_task": by_task,
            "note": "N 为盘点结果非假设；IN_SCOPE 边界最终由 Data-R 判定",
        },
    }
    out = os.path.join(ROOT, args.out_dir, "legacy_inventory_v4.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("written:", os.path.relpath(full, ROOT), os.path.relpath(out, ROOT))
    print(json.dumps(summary["summary"], ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()