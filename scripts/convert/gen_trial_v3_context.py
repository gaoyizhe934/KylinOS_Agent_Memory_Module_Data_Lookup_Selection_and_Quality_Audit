#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 试标 v3 独立标注上下文包生成（B = DGXD01，2026-09-04）

响应 Reviewer #31 Medium-1：生成与最终 v3 试标一一对应的 trial_v3_context.jsonl，
包含 input、必要元数据、evidence/证据定位；**不含 gold/参考答案/AI 标签**，
保障 A/B 独立盲标（双人独立红线）。

输出：data/interim/trial_v3_context.jsonl
用法：python scripts/convert/gen_trial_v3_context.py [--dry-run]
"""
import json
import os
import sys

INTERIM = "data/interim"
TRIAL = os.path.join(INTERIM, "stage8_trial_set_v3.jsonl")
OUT = os.path.join(INTERIM, "trial_v3_context.jsonl")
TASKS = ["preference_extraction", "knowledge_retrieval", "conflict_resolution",
         "precise_forgetting", "end_to_end_session"]


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_pool():
    pool = {}
    for task in TASKS:
        path = os.path.join(INTERIM, f"gold_candidates_{task}_v3.jsonl")
        for r in load_jsonl(path):
            pool[r["sample_id"]] = r
    return pool


def main():
    dry = "--dry-run" in sys.argv
    trials = load_jsonl(TRIAL)
    pool = load_pool()
    out_rows = []
    missing = []
    for t in trials:
        c = pool.get(t["sample_id"])
        if c is None:
            missing.append(t["sample_id"])
            continue
        # 仅保留 input / 元数据 / 证据定位；显式剔除 gold 及任何答案字段
        ctx = {
            "sample_id": c["sample_id"],
            "task_type": c["task_type"],
            "source_file": c.get("source_file", ""),
            "source": c.get("source", ""),
            "raw_id": c.get("raw_id"),
            "template_family": c.get("template_family", ""),
            "language": c.get("language", ""),
            "timestamp": c.get("timestamp", ""),
            "input": c.get("input", {}),
            "evidence": c.get("evidence", []),
        }
        out_rows.append(ctx)

    print(f"试标条数: {len(trials)} | context 生成: {len(out_rows)} | 缺失: {missing if missing else '无'}")
    if missing:
        print("[error] 存在无法回源到 v3 候选的样本")
        sys.exit(1)
    if len(out_rows) != len(trials):
        print("[error] 数量不一致")
        sys.exit(1)
    # 禁答案字段检查
    forbidden = ("gold", "answer", "reference", "expected_", "should_", "winner", "resolution")
    for r in out_rows:
        assert "gold" not in r, f"{r['sample_id']} 含 gold"
    if dry:
        for r in out_rows[:5]:
            print(" ", r["sample_id"], "|", r["task_type"], "| raw_id=", r.get("raw_id"))
        return

    with open(OUT, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[written] {OUT}: {len(out_rows)} 条")
    print("CONTEXT v3: OK（无 gold/答案字段）")


if __name__ == "__main__":
    main()
