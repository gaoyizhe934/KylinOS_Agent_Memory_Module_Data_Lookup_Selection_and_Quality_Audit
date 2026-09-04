#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 候选池 v3（仅真实 public_derived）生成（B = DGXD01，2026-09-04）

背景：响应 Reviewer #31 High-2——v2 候选池含 44/77 team_authored 自建，不得进入正式试标/Gate。
本脚本生成 v3 候选池：仅含 public_derived 真实可溯源样本（raw_id/source_file/source_version/证据定位），
并按 Reviewer 要求从仓库 git 跟踪的真实数据（v0_sample）补齐缺口：
  - conflict_resolution:   5 -> 8（longmemeval_cleaned 补 3）
  - precise_forgetting:    6 -> 8（longmemeval_cleaned 补 2）
  - end_to_end_session:    6 -> 8（longmemeval_v2 补 2）
  - preference_extraction: 10（已够，保留）
  - knowledge_retrieval:   12（已够，保留）
v2 候选文件原样保留（审计/开发证据），不覆盖、不删除。

输出：data/interim/gold_candidates_<task>_v3.jsonl
用法：python scripts/convert/rebuild_candidates_v3.py [--dry-run]
"""
import json
import os
import sys

INTERIM = "data/interim"
# 真实数据：git 跟踪的 v0_sample（v2 脚本误指 v0_subset 为空目录，此处修正）
LME_ORACLE = "data/raw/longmemeval_cleaned_2025/v0_sample/longmemeval_oracle.json"
LME_V2_Q = "data/raw/longmemeval_v2_2026/v0_sample/questions.jsonl"
TS = "2026-09-04T08:00:00.000Z"

TASKS = {
    "preference_extraction": {"target": 8, "v2": "preference_extraction"},
    "knowledge_retrieval": {"target": 8, "v2": "knowledge_retrieval"},
    "conflict_resolution": {"target": 8, "v2": "conflict_resolution"},
    "precise_forgetting": {"target": 8, "v2": "precise_forgetting"},
    "end_to_end_session": {"target": 8, "v2": "end_to_end_session"},
}


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_v2_public(task):
    p = os.path.join(INTERIM, f"gold_candidates_{task}_v2.jsonl")
    if not os.path.exists(p):
        return []
    return [r for r in load_jsonl(p) if r.get("source") == "public_derived"]


def base(task, sample_id, raw_id, input_, evidence, tf, src_file, src_ver, lang="en"):
    return {
        "sample_id": sample_id,
        "dataset_version": "kylin_memory_gold_v1.0",
        "task_type": task,
        "language": lang,
        "user_id": f"u_{raw_id[:20]}",
        "conversation_id": f"conv_{sample_id}",
        "timestamp": TS,
        "input": input_,
        "gold": {},
        "evidence": evidence,
        "source": "public_derived",
        "template_family": tf,
        "annotator_a": "",
        "annotator_b": "",
        "review_status": "candidate_only",
        "raw_id": raw_id,
        "source_file": src_file,
        "source_version": src_ver,
    }


def conflict_extra(lme, used, need=3):
    out = []
    for x in lme:
        if x.get("question_id") in used:
            continue
        if x.get("question_type") not in ("knowledge-update", "temporal-reasoning"):
            continue
        users = []
        for sess in x.get("haystack_sessions", []):
            for turn in sess:
                if isinstance(turn, dict) and turn.get("role") == "user":
                    c = str(turn.get("content", "")).strip()
                    if len(c) >= 20:
                        users.append(c)
        if len(users) >= 2 and len(out) < need:
            out.append({
                "raw_id": x["question_id"], "question": x.get("question", ""),
                "old": users[0], "new": users[1],
            })
    return out


def forgetting_extra(lme, used, need=2):
    out = []
    for x in lme:
        if x.get("question_id") in used:
            continue
        for sess in x.get("haystack_sessions", []):
            for turn in sess:
                if isinstance(turn, dict) and turn.get("role") == "user":
                    c = str(turn.get("content", "")).strip()
                    if len(c) >= 25 and len(out) < need:
                        out.append({"raw_id": x["question_id"], "item": c})
                        break
            if len(out) >= need:
                break
        if len(out) >= need:
            break
    return out


def e2e_extra(questions, used, need=2):
    out = []
    for q in questions:
        if q.get("id") in used:
            continue
        if q.get("question_type") not in ("procedure", "dynamic-environment", "errors-gotchas"):
            continue
        if len(out) < need:
            out.append({"raw_id": q.get("id", "?"), "question": q.get("question", ""),
                        "qtype": q.get("question_type", "")})
    return out


def main():
    dry = "--dry-run" in sys.argv
    lme = json.load(open(LME_ORACLE, encoding="utf-8"))
    qs = load_jsonl(LME_V2_Q)
    result = {}
    for task, cfg in TASKS.items():
        v2pub = load_v2_public(cfg["v2"])
        # 统一重编号为 v3 前缀（避免与 v2 候选/泄露样本 id 混淆；raw_id 溯源不变）
        prefix = {"preference_extraction": "pref", "knowledge_retrieval": "retr",
                  "conflict_resolution": "conf", "precise_forgetting": "forg",
                  "end_to_end_session": "e2e"}[task]
        rows = []
        for i, r in enumerate([dict(r) for r in v2pub], start=1):
            r["sample_id"] = f"{prefix}_v3_{i:04d}"
            r["conversation_id"] = f"conv_{r['sample_id']}"
            rows.append(r)
        used = set(r.get("raw_id") for r in rows if r.get("raw_id"))
        if task == "conflict_resolution":
            extra = conflict_extra(lme, used, need=max(0, cfg["target"] - len(rows)))
            n = 1
            for e in extra:
                sid = f"conf_v3_{len(rows)+n:04d}"
                rows.append(base(
                    task, sid, e["raw_id"],
                    {"candidates": {"old": e["old"], "new": e["new"]},
                     "scenario": f"真实会话事件链（question: {e['question'][:60]}）"},
                    [{"source_event_id": e["raw_id"], "span": e["old"][:60]},
                     {"source_event_id": e["raw_id"], "span": e["new"][:60]}],
                    "lme_conflict_chain_v1", "longmemeval_oracle.json",
                    "longmemeval_cleaned_2025_v0_sample"))
                n += 1
        elif task == "precise_forgetting":
            extra = forgetting_extra(lme, used, need=max(0, cfg["target"] - len(rows)))
            n = 1
            for e in extra:
                sid = f"forg_v3_{len(rows)+n:04d}"
                rows.append(base(
                    task, sid, e["raw_id"],
                    {"forget_instruction": f"请忘记这条记录：{e['item'][:80]}（仅此一条，保留其余会话记忆）"},
                    [{"source_event_id": e["raw_id"], "span": e["item"][:60]}],
                    "lme_memory_item_v1", "longmemeval_oracle.json",
                    "longmemeval_cleaned_2025_v0_sample"))
                n += 1
        elif task == "end_to_end_session":
            extra = e2e_extra(qs, used, need=max(0, cfg["target"] - len(rows)))
            n = 1
            for e in extra:
                sid = f"e2e_v3_{len(rows)+n:04d}"
                rows.append(base(
                    task, sid, e["raw_id"],
                    {"turns": [{"role": "user", "content": e["question"][:200]}],
                     "events": [e["qtype"]]},
                    [{"source_event_id": e["raw_id"], "span": e["question"][:60]}],
                    "lme_v2_task_chain_v1", "questions.jsonl",
                    "longmemeval_v2_2026_v0_sample"))
                n += 1
        result[task] = rows

    os.makedirs(INTERIM, exist_ok=True)
    for task, rows in result.items():
        out = os.path.join(INTERIM, f"gold_candidates_{task}_v3.jsonl")
        if dry:
            pub = sum(1 for r in rows if r.get("source") == "public_derived")
            print(f"[dry-run] {task}: total={len(rows)} public={pub}")
            continue
        with open(out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[written] {task}: {len(rows)} -> {out}")
    # 统计
    for task, rows in result.items():
        print(f"  {task}: public={sum(1 for r in rows if r.get('source')=='public_derived')}")


if __name__ == "__main__":
    main()
