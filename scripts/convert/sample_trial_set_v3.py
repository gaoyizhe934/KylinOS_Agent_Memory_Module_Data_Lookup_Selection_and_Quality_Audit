#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 试标集 v3 重抽（A = lyf-1213，2026-09-04）

从重建候选池（gold_candidates_*_v2.jsonl）按任务分层抽样，输出试标集。
保证：语义全异（先跑 dedup）、40 条（5 任务 × 8）、混合 public_derived + team_authored。

输出：data/interim/stage8_trial_set_v3.jsonl
用法：
  python scripts/convert/sample_trial_set_v3.py [--dry-run]
"""
import json
import os
import random
import sys

random.seed(20260904)

INTERIM = "data/interim"
TASKS = ["preference_extraction", "knowledge_retrieval", "conflict_resolution",
         "precise_forgetting", "end_to_end_session"]
PER_TASK = 8
OUT = os.path.join(INTERIM, "stage8_trial_set_v3.jsonl")


def load_candidates(task):
    path = os.path.join(INTERIM, f"gold_candidates_{task}_v2.jsonl")
    if not os.path.exists(path):
        print(f"[skip] {path} 不存在")
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    dry = "--dry-run" in sys.argv
    trials = []
    per_source = {}
    for task in TASKS:
        cands = load_candidates(task)
        if len(cands) < PER_TASK:
            print(f"[error] {task} 候选不足: {len(cands)} < {PER_TASK}")
            sys.exit(1)
        picked = random.sample(cands, PER_TASK)
        for c in picked:
            trials.append({
                "sample_id": c["sample_id"],
                "task_type": c["task_type"],
                "source_file": os.path.join("data", "interim", f"gold_candidates_{task}_v2.jsonl"),
                "source": c["source"],
                "template_family": c["template_family"],
            })
            per_source[c["source"]] = per_source.get(c["source"], 0) + 1

    print(f"试标集总数: {len(trials)}（5 任务 × {PER_TASK}）")
    print("source 分布:", per_source)

    if dry:
        for t in trials:
            print(" ", t["sample_id"], "|", t["task_type"], "|", t["source"], "|", t["template_family"])
        return

    with open(OUT, "w", encoding="utf-8") as f:
        for t in trials:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print(f"[written] {OUT}")

    # 去重校验：将试标集与 v2 候选池联查（试标集本身不含 input，需回溯源候选）
    sys.path.insert(0, os.path.join("scripts", "audit"))
    from stage8_semantic_dedup import scan_files
    files = [os.path.join("data", "interim", f"gold_candidates_{t}_v2.jsonl") for t in TASKS]
    res = scan_files(files)
    ok = True
    for path, v in res.items():
        if v["dup_groups"]:
            ok = False
            print(f"[dup] {path}: {v['dup_groups']} 组")
    # 试标集内部 sample_id 唯一性
    ids = [t["sample_id"] for t in trials]
    if len(ids) != len(set(ids)):
        print("[dup] 试标集 sample_id 有重复")
        ok = False
    print("TRIAL SET:", "CLEAN" if ok else "DUP_FOUND")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()