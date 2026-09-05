#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P01 Legacy Inventory（P2-A 工具 T02，Data-B）——逐样本账本 + 严格 fail-closed

输出 reports/legacy_inventory_v4_full.jsonl（逐样本账本）+ legacy_inventory_v4.json（summary 由 full 自动派生）。
逐样本字段：repo_ref / layer / split / file_path(repo-relative) / file_sha256 / line_no /
           sample_id / task_type / source / sample_fingerprint / label_exposed / template_family / inventory_status。
logical dedup：同一逻辑样本（stable sample_id/raw identity → content+evidence fingerprint → raw locator → session/scenario）
仅保留一个 IN_SCOPE，其余标 DUPLICATE_FILE（不删除历史文件）。
fail-closed：任一文件 open 失败 / JSONL parse 失败 / hash 失败 → 记录 error 并退出码 2。
退出码：0=PASS；2=扫描/解析异常（fail-closed）。
用法：python scripts/v4/inventory_legacy.py [--out-dir reports]
"""
import argparse
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LAYERS = [
    ("gold", "data/gold", "*.jsonl"),
    ("processed", "data/processed", "*.jsonl"),
    ("interim_v1", "data/interim", "gold_candidates_*.jsonl"),
]
SKIP_PROCESSED = {"multiwoz"}  # multiwoz 样本非正式 Gold 母体
ERRORS = []


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


def fingerprint_text(s):
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


def normalize(text):
    import re
    s = text.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def logical_key(row):
    r = row[1]
    sid = r.get("sample_id") or r.get("id") or ""
    raw = r.get("raw_id") or r.get("source_event_id") or ""
    content = json.dumps(r.get("input", {}), ensure_ascii=False, sort_keys=True)
    ev = json.dumps(r.get("evidence", []), ensure_ascii=False, sort_keys=True)
    return (sid, raw, normalize(content), normalize(ev))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="reports")
    args = ap.parse_args()

    records = []
    seen = {}
    for layer, rel_dir, pattern in LAYERS:
        for p in sorted(glob.glob(os.path.join(ROOT, rel_dir, pattern))):
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            fsha = sha256_file(p)
            if fsha is None:
                continue  # already recorded error
            rows = read_jsonl(p)
            if ERRORS and ERRORS[-1].startswith("open:"):
                continue
            base = os.path.basename(p)
            if layer == "processed" and any(s in base for s in SKIP_PROCESSED):
                continue
            split = ""
            if layer == "gold":
                split = os.path.basename(os.path.dirname(p))
            for line_no, r in rows:
                k = logical_key((line_no, r))
                if k in seen:
                    seen[k]["inventory_status"] = "DUPLICATE_FILE"
                    records.append({
                        "repo_ref": "not_applicable(scan)", "layer": layer, "split": split,
                        "file_path": rel, "file_sha256": fsha, "line_no": line_no,
                        "sample_id": r.get("sample_id", ""), "task_type": r.get("task_type", ""),
                        "source": r.get("source", ""), "sample_fingerprint": fingerprint_text(json.dumps(r, ensure_ascii=False)),
                        "label_exposed": r.get("label_exposed", "unknown"),
                        "template_family": r.get("template_family", ""),
                        "inventory_status": "DUPLICATE_FILE",
                        "duplicate_of": seen[k]["sample_id"],
                    })
                    continue
                rec = {
                    "repo_ref": "not_applicable(scan)", "layer": layer, "split": split,
                    "file_path": rel, "file_sha256": fsha, "line_no": line_no,
                    "sample_id": r.get("sample_id", ""), "task_type": r.get("task_type", ""),
                    "source": r.get("source", ""), "sample_fingerprint": fingerprint_text(json.dumps(r, ensure_ascii=False)),
                    "label_exposed": r.get("label_exposed", "unknown"),
                    "template_family": r.get("template_family", ""),
                    "inventory_status": "IN_SCOPE",
                }
                seen[k] = rec
                records.append(rec)

    if ERRORS:
        print("FAIL_CLOSED:", len(ERRORS), "errors")
        for e in ERRORS[:20]:
            print("  ", e)
        sys.exit(2)

    full_path = os.path.join(ROOT, args.out_dir, "legacy_inventory_v4_full.jsonl")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    n_in = sum(1 for r in records if r["inventory_status"] == "IN_SCOPE")
    n_dup = sum(1 for r in records if r["inventory_status"] == "DUPLICATE_FILE")
    summary = {
        "schema": "legacy_inventory_v4", "version": "v4.1", "tool": "inventory_legacy.py",
        "generated_by": "DGXD01(Data-B)", "date": "2026-09-05",
        "status": "NOT_FROZEN",
        "source": "derived_from_full",
        "summary": {
            "total_records": len(records), "in_scope": n_in, "duplicate_file": n_dup,
            "note": "N 为盘点结果非假设；IN_SCOPE 边界最终由 Data-R 判定；inventory_status=IN_SCOPE 为逻辑样本计数",
        },
    }
    out = os.path.join(ROOT, args.out_dir, "legacy_inventory_v4.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("written:", os.path.relpath(full_path, ROOT), os.path.relpath(out, ROOT))
    print(json.dumps(summary["summary"], ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()