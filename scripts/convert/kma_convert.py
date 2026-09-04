# -*- coding: utf-8 -*-
"""P1-3 KMA 化转换：把 processed gold 旧字段映射到 KMA canonical 字段。

依据：
- 标注手册 v2（data/gold/annotation_guideline_v2.md，P1 定稿版）
- Reviewer 裁定 #1-#4/#10（worklog/20260904_KMA_FROZEN_adjudications_1_4_R.md）
- registry/kappa_agreement_fields.json（一致字段集单源）

原则：
- 禁 mock：只做字段/枚举映射，不改原文与证据；
- 无损：旧字段保留在 input 或单独 legacy 字段（不删），canonical 字段新增；
- 幂等：重复运行输出一致；
- 输出：data/processed/*.jsonl（覆盖，canonical 化），legacy 字段保留在 gold.legacy。
"""
import glob
import json
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(ROOT, "data/processed")
INTERIM = os.path.join(ROOT, "data/interim")

# Reviewer 裁定 #2：旧 scope → KMA preference_scope 对照表
SCOPE_MAP = {
    "global": "global",
    "app": "tool",   # 具体工具/应用行为 → tool（裁定：非机械，按语义）
    "task": "topic",  # 工作主题 → topic
    "session": "session",
}

# Reviewer 裁定 #3：confidence → confidence_score 三档主表
CONFIDENCE_MAP = {"high": 0.95, "medium": 0.70, "low": 0.40}

# Reviewer 裁定：operation → version + memory_status
OPERATION_TO_MEMORY = {
    "create": "active",
    "update": "active",     # 新版本 active
    "revoke": "superseded",  # 旧版 superseded
    "no_op": "candidate",    # 临时 → candidate
}

# Reviewer 裁定：conflict_type 旧值 → KMA 枚举
CONFLICT_TYPE_MAP = {
    "time_update": "temporal_inconsistency",
    "scope": "scope_ambiguity",
    "source": "source_conflict",
    "knowledge_version": "temporal_inconsistency",
    "safety": "preference_conflict",
}

# Reviewer 裁定：winner → resolution_status
WINNER_MAP = {
    "keep_new": "resolved_manual",
    "app_priority": "resolved_manual",
    "explicit_config": "resolved_manual",
    "new_version": "resolved_manual",
    "safety_priority": "resolved_manual",
}

# 语义：should_store + 临时 → should_persist + is_temporary + memory_status
def map_preference(g):
    legacy = dict(g)
    scope_old = g.get("scope", "global")
    conf_old = g.get("confidence", "medium")
    op = g.get("operation", "create")
    should_store = g.get("should_store", True)
    ptype = g.get("preference_type", "other")
    out = {
        "expression_type": "explicit" if conf_old == "high" else "implicit",
        "preference_scope": SCOPE_MAP.get(scope_old, scope_old),
        "preference_key": ptype,  # 受控前缀；object 段留空（可后续按模板族补）
        "preference_value": g.get("value", ""),
        "confidence_score": CONFIDENCE_MAP.get(conf_old, 0.5),
        "should_persist": bool(should_store),
        "is_temporary": not bool(should_store),
        "memory_status": OPERATION_TO_MEMORY.get(op, "active"),
        "version": 2 if op == "update" else 1,
    }
    out["previous_version_id"] = "v1" if op == "update" else None
    out["evidence_event_ids"] = []
    out["legacy"] = legacy
    return out

def map_conflict(g):
    legacy = dict(g)
    ct_old = g.get("conflict_type", "time_update")
    winner = g.get("winner", "keep_new")
    out = {
        "conflict_type": CONFLICT_TYPE_MAP.get(ct_old, ct_old),
        "resolution_status": WINNER_MAP.get(winner, "resolved_manual"),
        "left_knowledge_id": (g.get("keep_ids") or ["left"])[0],
        "right_knowledge_id": (g.get("remove_ids") or ["right"])[0],
        "involved_knowledge_ids": list((g.get("keep_ids") or []) + (g.get("remove_ids") or [])),
        "resolution_strategy": None,
        "resolution_reason": g.get("resolution_reason", ""),
    }
    out["legacy"] = legacy
    return out

def map_tool(g):
    legacy = dict(g)
    status_old = g.get("status", "success")
    out = {
        "source_business_status": status_old,  # 旧值已对齐 KMA 8 值（success/failed/cancelled/timeout/partial_success 均为 KMA 值）
        "tool_call_id": "",  # 由事件层回填（当前受控候选无真实 tool_call_id）
        "source_type": "tool_result",
        "content_summary": g.get("side_effect", ""),
        "sensitivity": None,  # #10：敏感样本必填；当前候选非敏感 → 可空
        "failure_reason": g.get("failure_reason", ""),
    }
    out["legacy"] = legacy
    return out

def map_forgetting(g):
    legacy = dict(g)
    targets = g.get("target_ids") or []
    out = {
        "forget_mode": "single_item" if len(targets) <= 1 else "topic",
        "target_type": "preference" if any("pref_" in t for t in targets) else "knowledge",
        "target_selector": {"target_id": targets[0]} if targets else {},
        "status": "completed",
        "is_cascade": False,
        "has_vector_cleanup": None,  # DEFERRED
        "requires_confirmation": False,
        "resolved_target_ids": targets,
        "affected_count": len(targets),
        "must_keep": g.get("must_keep", []),
        "checkpoints": g.get("checkpoints", ["immediate_query"]),  # 评测层验证时点
        "expected_residual_count": g.get("expected_residual_count", 0),
    }
    out["legacy"] = legacy
    return out

def map_retrieval(g):
    # 检索：canonical 需 memory_id+version_id（D9），当前公开集/自建无 KB → 保留评测层字段 + 标记
    legacy = dict(g)
    out = {
        "knowledge_type": "template",  # 自建检索样本默认 template（待 KB 后细分）
        "evaluation_role": "positive_retrieval",
        "memory_status": "active",
        "relevant_ids": g.get("relevant_ids", []),
        "hard_negative_ids": g.get("hard_negative_ids", []),
        "expected_answer_points": g.get("expected_answer_points", []),
        "version_refs": None,  # D9 memory_id+version_id，待 KB 就绪回填
    }
    out["legacy"] = legacy
    return out

def map_e2e(g):
    legacy = dict(g)
    out = {
        "expected_memory": g.get("expected_memory", {}),
        "expected_response": g.get("expected_response", ""),
        "memory_status": "active",
        "memory_type": "long_term",
        "sensitivity": None,
    }
    out["legacy"] = legacy
    return out

TASK_MAPPER = {
    "preference_extraction": map_preference,
    "knowledge_retrieval": map_retrieval,
    "conflict_resolution": map_conflict,
    "precise_forgetting": map_forgetting,
    "tool_result": map_tool,
    "end_to_end_session": map_e2e,
}

def _is_canonical(task, gold):
    """判断 gold 是否已是 canonical（避免重复映射、保证幂等）。"""
    keys = {
        "preference_extraction": ["expression_type", "preference_scope", "confidence_score"],
        "knowledge_retrieval": ["knowledge_type", "evaluation_role"],
        "conflict_resolution": ["conflict_type", "resolution_status", "left_knowledge_id"],
        "precise_forgetting": ["forget_mode", "target_type", "resolved_target_ids"],
        "tool_result": ["source_business_status"],
        "end_to_end_session": ["memory_status", "expected_response"],
    }.get(task, [])
    return all(k in (gold or {}) for k in keys)


def main():
    stats = {"rows": 0, "fixed": 0, "skip": 0, "already": 0, "files": []}
    for path in sorted(glob.glob(os.path.join(PROCESSED, "*.jsonl"))):
        fname = os.path.basename(path)
        rows = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                task = r.get("task_type")
                mapper = TASK_MAPPER.get(task)
                if mapper:
                    if _is_canonical(task, r.get("gold") or {}):
                        stats["already"] += 1
                    else:
                        r["gold"] = mapper(r.get("gold") or {})
                        stats["fixed"] += 1
                else:
                    stats["skip"] += 1
                rows.append(r)
                stats["rows"] += 1
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        stats["files"].append((fname, len(rows)))
    print("== P1-3 KMA 化转换 ==")
    print("rows:", stats["rows"], "fixed:", stats["fixed"], "already:", stats["already"], "skip(aux):", stats["skip"])
    print("files:", stats["files"])
    print("note: 旧字段保留在 gold.legacy；禁 mock（仅字段/枚举映射）")
    print("== done ==")

if __name__ == "__main__":
    main()
