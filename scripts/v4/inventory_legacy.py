#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P01 Legacy Inventory（P2-A 工具 T02，Data-B）——逐样本账本 + 优先级 logical dedup + 严格 fail-closed

identity precedence（明确优先级，非元组全等）：
  L1 稳定 sample_id（若存在）为主，raw_id 漂移不影响同组；
  L2 raw+task+source 组合（仅 sample_id 缺失时进入），防 raw 被多任务复用时误折叠；
  L3 content+evidence 指纹；
  L4 source/raw locator；
每个 logical group 恰好一个 canonical IN_SCOPE；DUPLICATE_FILE 的 duplicate_of 必须解析到该组唯一 canonical。
输出每条含 logical_group_id；结束时强断言（组内 IN_SCOPE==1 且 duplicate_of 可解析）。
repo_ref / scan_repo_ref 记录真实扫描 HEAD；tool_source_commit 记录工具实现 commit（外部传入）。
fail-closed：任一文件 open / JSONL parse / hash / 断言失败 -> exit 2。
用法：python scripts/v4/inventory_legacy.py [--out-dir reports] [--tool-source-commit <sha>]
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
    """优先级身份：L1 sample_id（主）> L2 raw+task+source > L3 content+evidence > L4 locator。"""
    sid = str(r.get("sample_id") or r.get("id") or "").strip()
    raw = str(r.get("raw_id") or r.get("source_event_id") or "").strip()
    task = str(r.get("task_type") or "").strip()
    src = str(r.get("source") or "").strip()
    content = norm(json.dumps(r.get("input", {}), ensure_ascii=False))
    ev = norm(json.dumps(r.get("evidence", []), ensure_ascii=False))
    loc = str(r.get("source_file") or "").strip()
    if sid:
        return ("L1", sid)
    if raw and task and src:
        return ("L2", raw, task, src)
    ck = fingerprint(content + ev)
    if ck:
        return ("L3", ck)
    if loc:
        return ("L4", fingerprint(loc))
    return ("L5", fingerprint(json.dumps(r, ensure_ascii=False)))


LAYERS = [
    ("gold", "data/gold", "**/*.jsonl"),
    ("processed", "data/processed", "*.jsonl"),
    ("interim_v1", "data/interim", "gold_candidates_*.jsonl"),
]
SKIP_PROCESSED = {"multiwoz"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="reports")
    ap.add_argument("--tool-source-commit", default="", help="inventory_legacy.py 实现所在 commit（如 P2-A PR#36）")
    args = ap.parse_args()

    scan_ref = git_head()
    tool_commit = args.tool_source_commit or scan_ref
    records = []
    groups = {}  # identity_key -> canonical record
    group_ids = {}
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
                if ik not in group_ids:
                    group_ids[ik] = "g%05d" % len(group_ids)
                rec = {
                    "repo_ref": scan_ref, "layer": layer, "split": split,
                    "file_path": rel, "file_sha256": fsha, "line_no": line_no,
                    "sample_id": r.get("sample_id", ""), "task_type": r.get("task_type", ""),
                    "source": r.get("source", ""),
                    "sample_fingerprint": fingerprint(json.dumps(r, ensure_ascii=False)),
                    "label_exposed": r.get("label_exposed", "unknown"),
                    "template_family": r.get("template_family", ""),
                    "logical_group_id": group_ids[ik],
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

    # 强 canonical 断言：每组恰好 1 个 IN_SCOPE；duplicate_of 可解析到组内唯一 canonical
    from collections import defaultdict
    by_group = defaultdict(list)
    for r in records:
        by_group[r["logical_group_id"]].append(r)
    for g, recs in by_group.items():
        in_scope = [r for r in recs if r["inventory_status"] == "IN_SCOPE"]
        if len(in_scope) != 1:
            ERRORS.append("canonical-assert: group %s has %d IN_SCOPE (expect 1)" % (g, len(in_scope)))
            continue
        canonical_sid = in_scope[0]["sample_id"]
        for r in recs:
            if r["inventory_status"] == "DUPLICATE_FILE" and r["duplicate_of"] != canonical_sid:
                ERRORS.append("canonical-assert: group %s duplicate_of=%s != canonical=%s" % (g, r["duplicate_of"], canonical_sid))
    if ERRORS:
        print("FAIL_CLOSED:", len(ERRORS))
        for e in ERRORS[:20]:
            print("  ", e)
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
        "tool_source_commit": tool_commit,
        "scan_repo_ref": scan_ref,
        "full_ledger_sha256": full_sha,
        "dedup_policy": "L1 sample_id(主) > L2 raw+task+source > L3 content+evidence > L4 locator; 每组合一 canonical IN_SCOPE",
        "canonical_assertion": "PASS (每组 IN_SCOPE==1, duplicate_of 可解析)",
        "source": "derived_from_full",
        "summary": {
            "total_records": len(records), "in_scope": n_in, "duplicate_file": n_dup,
            "logical_groups": len(group_ids),
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