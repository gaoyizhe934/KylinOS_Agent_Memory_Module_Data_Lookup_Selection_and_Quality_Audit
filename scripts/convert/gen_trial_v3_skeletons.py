#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 试标 v3 骨架生成（A = lyf-1213，2026-09-04）

从 stage8_trial_set_v3.jsonl 生成 A/B 独立标注空骨架（gold 字段留空待标注）。
字段集沿用 P1-4 骨架口径（KMA canonical），与 labels_A/B_trial_v2.jsonl 结构一致。

输出：
  data/interim/labels_A_trial_v3.jsonl
  data/interim/labels_B_trial_v3.jsonl
用法：
  python scripts/convert/gen_trial_v3_skeletons.py [--dry-run]
"""
import json
import os
import sys

INTERIM = "data/interim"
TRIAL = os.path.join(INTERIM, "stage8_trial_set_v3.jsonl")

# 各任务 gold 骨架字段（KMA canonical，沿用 P1-4）
GOLD_SKELETON = {
    "preference_extraction": {
        "expression_type": "", "preference_scope": "", "preference_key": "",
        "preference_value": "", "confidence_score": None, "should_persist": None,
        "is_temporary": None, "memory_status": "", "version": None,
        "previous_version_id": None, "evidence_event_ids": [],
    },
    "knowledge_retrieval": {
        "knowledge_type": "", "knowledge_id": "", "memory_status": "",
        "superseded_by_id": None, "relevant_ids": [], "hard_negative_ids": [],
        "expected_answer_points": [], "semantic_near_miss_refs": [],
        "evaluation_role": "", "rationale": "",
    },
    "conflict_resolution": {
        "conflict_type": "", "resolution_status": "",
        "left_knowledge_id": "", "right_knowledge_id": "",
        "involved_knowledge_ids": [], "resolution_strategy": None,
    },
    "precise_forgetting": {
        "forget_mode": "", "target_type": "", "target_selector": {},
        "status": "", "is_cascade": None, "has_vector_cleanup": None,
        "requires_confirmation": None, "resolved_target_ids": [],
        "affected_count": None, "checkpoints": [],
    },
    "end_to_end_session": {
        "expected_memory": {}, "expected_response": "", "sensitivity": None,
    },
    "tool_result": {
        "source_business_status": "", "tool_call_id": "",
        "content_summary": "", "sensitivity": None,
    },
}


def main():
    dry = "--dry-run" in sys.argv
    if not os.path.exists(TRIAL):
        print(f"[error] {TRIAL} 不存在")
        sys.exit(1)
    with open(TRIAL, encoding="utf-8") as f:
        trials = [json.loads(l) for l in f if l.strip()]

    for suffix, annotator in [("A", "A"), ("B", "B")]:
        out_path = os.path.join(INTERIM, f"labels_{suffix}_trial_v3.jsonl")
        lines = []
        for t in trials:
            task = t["task_type"]
            skeleton = json.loads(json.dumps(GOLD_SKELETON.get(task, {})))
            rec = {
                "sample_id": t["sample_id"],
                "task_type": task,
                "gold": skeleton,
                "evidence": [],
                "annotator": annotator,
            }
            lines.append(rec)
        if dry:
            print(f"[dry-run] {out_path}: {len(lines)} 条")
            continue
        with open(out_path, "w", encoding="utf-8") as f:
            for r in lines:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[written] {out_path}: {len(lines)} 条")


if __name__ == "__main__":
    main()