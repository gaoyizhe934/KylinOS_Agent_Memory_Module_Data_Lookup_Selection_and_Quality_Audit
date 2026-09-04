#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 候选池规则归一化去重审计（A = lyf-1213，2026-09-04）

用途：
- 对 gold_candidates / processed / 试标集的 input 做"规则归一化"去重检测，
  暴露 v1.0 时代模板×计数器批量生成的重复缺陷。
- 归一化口径：提取任务相关的语义主字段（query/user_message/turns/forget_instruction/
  candidates 等），剥离 context/version/序号等计数器噪音后做规范化 hash。

用法：
  python scripts/audit/stage8_semantic_dedup.py                 # 默认扫描 interim 候选池
  python scripts/audit/stage8_semantic_dedup.py --pool processed  # 扫描 processed
  python scripts/audit/stage8_semantic_dedup.py --files a.jsonl b.jsonl
  python scripts/audit/stage8_semantic_dedup.py --json          # 输出 JSON 证据

退出码：
  0 = 无重复组；1 = 存在重复组（供 CI 硬校验）
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, OrderedDict


# ---------------------------------------------------------------- 归一化工具

_COUNTER_RE = re.compile(r"(第\s*\d+\s*次|v?\d+(\.\d+)?|#?\d{1,6}|_\d{3,}|时间?戳|\d{4}-\d{2}-\d{2})", re.I)
_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[，。；：？！、,.;:?!\"'“”‘’()\[\]{}<>《》【】\-\—_/\\|]")


def _norm_text(text):
    """归一化：小写、去标点/空白、剥离计数器噪音。"""
    t = _COUNTER_RE.sub("", text)
    t = _PUNCT_RE.sub("", t)
    t = _SPACE_RE.sub("", t)
    return t.lower()


def _extract_semantic_key(record, task_type):
    """提取任务主字段，用于去重比对。"""
    inp = record.get("input")
    if inp is None:
        return _norm_text(json.dumps(record, ensure_ascii=False))
    if isinstance(inp, str):
        return _norm_text(inp)
    if isinstance(inp, dict):
        inp = dict(inp)
    else:
        return _norm_text(json.dumps(inp, ensure_ascii=False))

    if task_type == "knowledge_retrieval":
        q = inp.get("query", "") or inp.get("query_text", "")
        return _norm_text(str(q))
    if task_type == "preference_extraction":
        m = inp.get("user_message", "") or inp.get("message", "") or inp.get("utterance", "")
        return _norm_text(str(m))
    if task_type == "precise_forgetting":
        f = inp.get("forget_instruction", "") or inp.get("instruction", "")
        return _norm_text(str(f))
    if task_type == "conflict_resolution":
        # 取场景（scenario）+ 候选双方 + conflict_type
        parts = []
        if inp.get("scenario"):
            parts.append(str(inp["scenario"]))
        cand = inp.get("candidates")
        if isinstance(cand, dict):
            parts.extend(str(v) for v in cand.values())
        if inp.get("conflict_type"):
            parts.append(str(inp["conflict_type"]))
        return _norm_text(" | ".join(parts))
    if task_type == "end_to_end_session":
        turns = inp.get("turns") or []
        if isinstance(turns, list):
            contents = []
            for t in turns:
                if isinstance(t, dict):
                    contents.append(str(t.get("content", "")))
                else:
                    contents.append(str(t))
            return _norm_text(" | ".join(contents))
        if inp.get("events"):
            return _norm_text(" | ".join(str(e) for e in inp["events"]))
        return _norm_text(json.dumps(inp, ensure_ascii=False))
    # 兜底：整个 input 归一化
    return _norm_text(json.dumps(inp, ensure_ascii=False))


# ---------------------------------------------------------------- 扫描逻辑

def _read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def scan_files(files):
    """返回 {path: {总条数, 唯一数, 重复组, 重复条数, 明细[]}}"""
    result = OrderedDict()
    for path in files:
        rows = list(_read_lines(path))
        buckets = {}
        for r in rows:
            task = r.get("task_type", "unknown")
            key = _extract_semantic_key(r, task)
            buckets.setdefault(key, []).append(r.get("sample_id", "?"))
        counter = Counter(len(v) for v in buckets.values())
        dup_groups = {k: v for k, v in buckets.items() if len(v) > 1}
        detail = []
        for k, v in dup_groups.items():
            detail.append({"normalized_key": k, "sample_ids": v, "count": len(v)})
        result[path] = {
            "total": len(rows),
            "unique_input": len(buckets),
            "dup_groups": len(dup_groups),
            "dup_records": sum(len(v) for v in dup_groups.values()),
            "detail": detail,
        }
    return result


def _json_safe(o):
    return json.dumps(o, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="候选池规则归一化去重审计")
    parser.add_argument("--pool", choices=["interim", "processed"], default="interim")
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--json", action="store_true", help="输出 JSON 证据")
    parser.add_argument("--strict", action="store_true", help="存在重复即退出码 1")
    args = parser.parse_args()

    if args.files:
        files = args.files
    elif args.pool == "processed":
        files = [os.path.join("data", "processed", fn)
                 for fn in sorted(os.listdir("data/processed")) if fn.endswith(".jsonl")]
    else:
        files = [os.path.join("data", "interim", fn)
                 for fn in sorted(os.listdir("data/interim")) if fn.startswith("gold_candidates") and fn.endswith(".jsonl")]

    result = scan_files(files)
    any_dup = any(v["dup_groups"] > 0 for v in result.values())

    if args.json:
        print(_json_safe(result))
    else:
        for path, v in result.items():
            print(f"[{path}] total={v['total']} unique={v['unique_input']} "
                  f"dup_groups={v['dup_groups']} dup_records={v['dup_records']}")
            for d in v["detail"]:
                print(f"    x{d['count']}: {d['sample_ids']} | {d['normalized_key'][:60]}")
        print()
        print("RESULT:", "DUP_FOUND" if any_dup else "CLEAN")

    if any_dup and args.strict:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()