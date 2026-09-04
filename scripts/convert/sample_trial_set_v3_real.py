#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 试标集 v3（未泄露·仅真实）重抽（B = DGXD01，2026-09-04）

响应 Reviewer #31 High-2/High-3：旧 v3 含 19/40 team_authored 且 v2 样本已泄露（永久废弃）。
本脚本仅从 v3 候选池（gold_candidates_*_v3.jsonl，全 public_derived 真实可溯源）分层抽样
5 任务 × 8 = 40 条，覆盖 data/interim/stage8_trial_set_v3.jsonl（未泄露真实版）；
旧版内容保留于 git 历史作审计。
用法：python scripts/convert/sample_trial_set_v3_real.py [--dry-run]
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
    path = os.path.join(INTERIM, f"gold_candidates_{task}_v3.jsonl")
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
        cands = [c for c in load_candidates(task) if c.get("source") == "public_derived"]
        if len(cands) < PER_TASK:
            print(f"[error] {task} 真实候选不足: {len(cands)} < {PER_TASK}")
            sys.exit(1)
        picked = random.sample(cands, PER_TASK)
        for c in picked:
            trials.append({
                "sample_id": c["sample_id"],
                "task_type": c["task_type"],
                "source_file": os.path.join("data", "interim", f"gold_candidates_{task}_v3.jsonl"),
                "source": c["source"],
                "template_family": c["template_family"],
                "raw_id": c.get("raw_id"),
            })
            per_source[c["source"]] = per_source.get(c["source"], 0) + 1

    print(f"试标集总数: {len(trials)}（5 任务 × {PER_TASK}）")
    print("source 分布:", per_source)

    if dry:
        for t in trials:
            print(" ", t["sample_id"], "|", t["task_type"], "|", t["raw_id"])
        return

    # 覆盖写（旧版保留于 git 历史）
    with open(OUT, "w", encoding="utf-8") as f:
        for t in trials:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")
    print(f"[written] {OUT}")

    ids = [t["sample_id"] for t in trials]
    if len(ids) != len(set(ids)):
        print("[error] sample_id 重复")
        sys.exit(1)
    if any(t["source"] != "public_derived" for t in trials):
        print("[error] 含非 public_derived")
        sys.exit(1)
    print("TRIAL SET v3 (real): CLEAN")


if __name__ == "__main__":
    main()
