# -*- coding: utf-8 -*-
"""完整指标计算框架 v1.0
用法：
  python scripts/evaluate/evaluate_metrics.py --gold data/processed/*.jsonl --hyp <模型预测结果目录> --report reports/metrics_report_v1.md

输入：
  --gold    Gold 标准 JSONL 文件（data/processed/ 下的文件）
  --hyp     模型预测 JSONL 文件（每行 gold 一样含 sample_id + predicted 字段）
  --report  输出报告路径（可选，默认 stdout）

输出：Markdown 格式指标报告，含公式、按任务/分组/模板族的详细统计。

指标标准与阈值（手册第 2 章 / 附录 B）：
  - 偏好提取 F1 >= 85%
  - 知识检索 Recall@K >= 85%
  - 冲突处理准确率 >= 88%
  - 精准遗忘：删除正确率 >= 95%，误删率 <= 5%，残留数 = 0
  - Tool Result：状态判定准确率 >= 90%
  - 端到端：案例通过率 >= 80%
"""

import argparse, json, sys, os, re
from collections import defaultdict, Counter

# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def safe_divide(n, d):
    return n / d if d > 0 else 0.0


def precision_recall_f1(tp, fp, fn):
    p = safe_divide(tp, tp + fp)
    r = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * p * r, p + r)
    return p, r, f1


# ──────────────────────────────────────────────
# 1. 偏好提取 (preference_extraction)
# ──────────────────────────────────────────────

def eval_preference_extraction(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "preference_extraction",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "missing_in_hyp": len(set(gold_map) - set(hyp_map)),
        "extra_in_hyp": len(set(hyp_map) - set(gold_map)),
        "fields": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}),
        "by_type": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}),
        "by_template": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}),
        "by_scope": defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0}),
        "wrong_operation": 0,
        "operation_total": 0,
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        # 字段级匹配
        for field in ["preference_type", "value", "scope", "confidence", "should_store", "operation"]:
            gv = g_gold.get(field)
            hv = h_gold.get(field)
            if gv is not None and hv is not None:
                results["operation_total"] += 1
                if gv == hv:
                    results["fields"][field]["tp"] += 1
                else:
                    results["fields"][field]["fp"] += 1
                    results["fields"][field]["fn"] += 1

        # 按偏好类型分组
        ptype = g_gold.get("preference_type", "unknown")
        if g_gold.get("preference_type") == h_gold.get("preference_type"):
            results["by_type"][ptype]["tp"] += 1
        else:
            results["by_type"][ptype]["fp"] += 1
            results["by_type"][ptype]["fn"] += 1

        # 按模板族分组
        tf = g.get("template_family", "unknown")
        if g_gold.get("preference_type") == h_gold.get("preference_type"):
            results["by_template"][tf]["tp"] += 1
        else:
            results["by_template"][tf]["fp"] += 1
            results["by_template"][tf]["fn"] += 1

        # 按作用域分组
        sc = g_gold.get("scope", "unknown")
        if g_gold.get("preference_type") == h_gold.get("preference_type"):
            results["by_scope"][sc]["tp"] += 1
        else:
            results["by_scope"][sc]["fp"] += 1
            results["by_scope"][sc]["fn"] += 1

        # operation 操作是否正确
        gop = g_gold.get("operation")
        hop = h_gold.get("operation")
        if gop and hop and gop != hop:
            results["wrong_operation"] += 1

    return results


def format_preference_report(r):
    lines = []
    lines.append("### 偏好提取 (Preference Extraction)")
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    lines.append(f"- 缺失预测: {r['missing_in_hyp']} | 多余预测: {r['extra_in_hyp']}")
    lines.append("")
    lines.append("#### 字段级准确率")
    for field in ["preference_type", "value", "scope", "confidence", "should_store", "operation"]:
        d = r["fields"][field]
        p, rv, f1 = precision_recall_f1(d["tp"], d["fp"], d["fn"])
        lines.append(f"  - {field}: P={p:.2%}  R={rv:.2%}  F1={f1:.2%}  (tp={d['tp']}, fp={d['fp']}, fn={d['fn']})")
    lines.append("")
    lines.append("#### 按偏好类型分组")
    for k in sorted(r["by_type"]):
        d = r["by_type"][k]
        p, rv, f1 = precision_recall_f1(d["tp"], d["fp"], d["fn"])
        lines.append(f"  - {k}: P={p:.2%}  R={rv:.2%}  F1={f1:.2%}  (n={d['tp']+d['fn']})")
    lines.append("")
    lines.append("#### 按模板族分组")
    for k in sorted(r["by_template"]):
        d = r["by_template"][k]
        p, rv, f1 = precision_recall_f1(d["tp"], d["fp"], d["fn"])
        lines.append(f"  - {k}: P={p:.2%}  R={rv:.2%}  F1={f1:.2%}  (n={d['tp']+d['fn']})")
    lines.append("")
    if r["operation_total"] > 0:
        op_acc = 1 - r["wrong_operation"] / r["operation_total"]
        lines.append(f"#### Operation 准确率: {op_acc:.2%}  ({r['wrong_operation']}/{r['operation_total']} 错误)")
    lines.append("")
    # 总体 F1
    total_tp = sum(d["tp"] for d in r["fields"].values())
    total_fp = sum(d["fp"] for d in r["fields"].values())
    total_fn = sum(d["fn"] for d in r["fields"].values())
    p, rv, f1 = precision_recall_f1(total_tp, total_fp, total_fn)
    lines.append(f"**总体 F1={f1:.2%}**  (阈值: >=85%)  {'✅ 通过' if f1 >= 0.85 else '❌ 未通过'}")
    lines.append("")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 2. 知识检索 (knowledge_retrieval)
# ──────────────────────────────────────────────

def eval_knowledge_retrieval(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "knowledge_retrieval",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "recall_at_k": [],
        "mrrs": [],
        "ndcgs": [],
        "by_query_type": defaultdict(list),
        "zero_recall": 0,
        "total_queries": 0,
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        gold_ids = set(g_gold.get("relevant_ids", []))
        hyp_ids = h_gold.get("retrieved_ids", [])  # 模型预测的排序列表
        gold_relevance = g_gold.get("relevance", {})

        if not gold_ids:
            continue

        results["total_queries"] += 1

        # Recall@K (K=1,3,5,10,20)
        gold_set = gold_ids
        for k in [1, 3, 5, 10, 20]:
            retrieved_k = set(hyp_ids[:k])
            hits = len(gold_set & retrieved_k)
            recall = safe_divide(hits, len(gold_set))
            results["recall_at_k"].append((k, recall))

        # MRR
        mrr = 0.0
        for rank, rid in enumerate(hyp_ids, 1):
            if rid in gold_set:
                mrr = 1.0 / rank
                break
        results["mrrs"].append(mrr)

        # nDCG (简化版：binary relevance)
        dcg = 0.0
        idcg = 0.0
        for rank, rid in enumerate(hyp_ids, 1):
            rel = 1 if rid in gold_set else 0
            dcg += rel / (rank + 1)  # log2(rank+1) ≈ rank+1
        for rank in range(1, len(gold_set) + 1):
            idcg += 1.0 / (rank + 1)
        ndcg = safe_divide(dcg, idcg)
        results["ndcgs"].append(ndcg)

        # 按 query_type 分组
        qt = g.get("input", {}).get("query_type", "unknown")
        results["by_query_type"][qt].append({
            "recall_k": results["recall_at_k"][-1][1] if results["recall_at_k"] else 0,
            "mrr": mrr,
            "ndcg": ndcg,
        })

        # 零召回计数
        if len(gold_set & set(hyp_ids)) == 0:
            results["zero_recall"] += 1

    return results


def format_retrieval_report(r):
    lines = []
    lines.append("### 知识检索 (Knowledge Retrieval)")
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    lines.append(f"- 有效查询数: {r['total_queries']} | 零召回查询: {r['zero_recall']}")
    lines.append("")

    # 按 K 汇总 Recall@K
    if r["recall_at_k"]:
        lines.append("#### Recall@K")
        by_k = defaultdict(list)
        for k, rec in r["recall_at_k"]:
            by_k[k].append(rec)
        for k in sorted(by_k):
            avg = sum(by_k[k]) / len(by_k[k])
            lines.append(f"  - Recall@{k}: {avg:.2%}")
        lines.append("")

    # MRR
    if r["mrrs"]:
        avg_mrr = sum(r["mrrs"]) / len(r["mrrs"])
        lines.append(f"**平均 MRR: {avg_mrr:.4f}**")
        lines.append("")

    # nDCG
    if r["ndcgs"]:
        avg_ndcg = sum(r["ndcgs"]) / len(r["ndcgs"])
        lines.append(f"**平均 nDCG: {avg_ndcg:.4f}**")
        lines.append("")

    # 按 query_type 分组
    if r["by_query_type"]:
        lines.append("#### 按查询类型分组")
        for qt in sorted(r["by_query_type"]):
            items = r["by_query_type"][qt]
            avg_recall = sum(x["recall_k"] for x in items) / len(items)
            avg_mrr = sum(x["mrr"] for x in items) / len(items)
            avg_ndcg = sum(x["ndcg"] for x in items) / len(items)
            lines.append(f"  - {qt} (n={len(items)}):  Recall@{k}={avg_recall:.2%}  MRR={avg_mrr:.4f}  nDCG={avg_ndcg:.4f}")

    # 阈值判断
    recall_k5 = by_k.get(5, [])
    avg_r5 = sum(recall_k5) / len(recall_k5) if recall_k5 else 0
    lines.append(f"\n**Recall@5={avg_r5:.2%}**  (阈值: >=85%)  {'✅ 通过' if avg_r5 >= 0.85 else '❌ 未通过'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 3. 冲突处理 (conflict_resolution)
# ──────────────────────────────────────────────

def eval_conflict_resolution(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "conflict_resolution",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "correct": 0,
        "total": 0,
        "by_conflict_type": defaultdict(lambda: {"correct": 0, "total": 0}),
        "by_template": defaultdict(lambda: {"correct": 0, "total": 0}),
        "error_types": Counter(),
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        g_winner = g_gold.get("winner")
        h_winner = h_gold.get("winner")
        g_conflict_type = g_gold.get("conflict_type", "unknown")

        results["total"] += 1
        results["by_conflict_type"][g_conflict_type]["total"] += 1
        results["by_template"][g.get("template_family", "unknown")]["total"] += 1

        if g_winner == h_winner:
            results["correct"] += 1
            results["by_conflict_type"][g_conflict_type]["correct"] += 1
            results["by_template"][g.get("template_family", "unknown")]["correct"] += 1
        else:
            results["error_types"][f"{g_conflict_type}:winner_mismatch"] += 1

    return results


def format_conflict_report(r):
    lines = []
    lines.append("### 冲突处理 (Conflict Resolution)")
    acc = safe_divide(r["correct"], r["total"])
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    lines.append(f"- 正确: {r['correct']} / {r['total']} = **{acc:.2%}**")
    lines.append("")
    lines.append("#### 按冲突类型分组")
    for ct in sorted(r["by_conflict_type"]):
        d = r["by_conflict_type"][ct]
        ca = safe_divide(d["correct"], d["total"])
        lines.append(f"  - {ct}: {d['correct']}/{d['total']} = {ca:.2%}")
    lines.append("")
    lines.append("#### 按模板族分组")
    for tf in sorted(r["by_template"]):
        d = r["by_template"][tf]
        ca = safe_divide(d["correct"], d["total"])
        lines.append(f"  - {tf}: {d['correct']}/{d['total']} = {ca:.2%}")
    lines.append("")
    if r["error_types"]:
        lines.append("#### 错误类型分布")
        for err, cnt in r["error_types"].most_common():
            lines.append(f"  - {err}: {cnt}")
        lines.append("")
    lines.append(f"**准确率={acc:.2%}**  (阈值: >=88%)  {'✅ 通过' if acc >= 0.88 else '❌ 未通过'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 4. 精准遗忘 (precise_forgetting)
# ──────────────────────────────────────────────

def eval_precise_forgetting(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "precise_forgetting",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "deletion_correct": 0,
        "deletion_total": 0,
        "false_deletion": 0,
        "residual_checks": [],
        "residual_errors": 0,
        "by_template": defaultdict(lambda: {"correct": 0, "total": 0}),
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        # 删除正确率: 目标是否被正确删除
        expected_deleted = set(g_gold.get("expected_deleted", []))
        actual_deleted = set(h_gold.get("deleted_ids", []))
        must_keep = set(g_gold.get("must_keep", []))

        # 正确删除: expected_deleted ⊆ actual_deleted
        if expected_deleted:
            results["deletion_total"] += 1
            if expected_deleted.issubset(actual_deleted):
                results["deletion_correct"] += 1
                results["by_template"][g.get("template_family", "unknown")]["correct"] += 1
            results["by_template"][g.get("template_family", "unknown")]["total"] += 1

        # 误删: actual_deleted 中包含了 must_keep 中的元素
        false_deleted = actual_deleted & must_keep
        if false_deleted:
            results["false_deletion"] += len(false_deleted)

        # 残留检查
        expected_residual = g_gold.get("expected_residual_count", 0)
        actual_residual = h_gold.get("residual_count", -1)
        if actual_residual >= 0:
            results["residual_checks"].append({
                "sample_id": sid,
                "expected": expected_residual,
                "actual": actual_residual,
                "ok": actual_residual == expected_residual,
            })
            if actual_residual != expected_residual:
                results["residual_errors"] += 1

    return results


def format_forgetting_report(r):
    lines = []
    lines.append("### 精准遗忘 (Precise Forgetting)")
    del_acc = safe_divide(r["deletion_correct"], r["deletion_total"])
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    lines.append(f"- 删除正确率: {r['deletion_correct']}/{r['deletion_total']} = **{del_acc:.2%}**")
    lines.append(f"- 误删数: {r['false_deletion']}")
    lines.append(f"- 残留检查: {r['residual_errors']} 错误 / {len(r['residual_checks'])} 总检查")
    lines.append("")
    lines.append("#### 按模板族分组")
    for tf in sorted(r["by_template"]):
        d = r["by_template"][tf]
        ca = safe_divide(d["correct"], d["total"])
        lines.append(f"  - {tf}: {d['correct']}/{d['total']} = {ca:.2%}")
    lines.append("")
    lines.append(f"**删除正确率={del_acc:.2%}**  (阈值: >=95%)  {'✅ 通过' if del_acc >= 0.95 else '❌ 未通过'}")
    if r["false_deletion"] > 0:
        lines.append(f"**误删数={r['false_deletion']}**  (阈值: <=5% of total)  {'❌ 存在误删' if r['false_deletion'] > 0 else '✅ 无误删'}")
    residual_ok = r["residual_errors"] == 0
    lines.append(f"**残留检查: {'✅ 全部通过' if residual_ok else '❌ 存在残留错误'}")
    if not residual_ok and r["residual_checks"]:
        lines.append("残留错误详情:")
        for c in r["residual_checks"]:
            if not c["ok"]:
                lines.append(f"  - {c['sample_id']}: 期望={c['expected']}, 实际={c['actual']}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 5. Tool Result (tool_result)
# ──────────────────────────────────────────────

def eval_tool_result(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "tool_result",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "status_correct": 0,
        "status_total": 0,
        "persist_correct": 0,
        "persist_total": 0,
        "by_status": defaultdict(lambda: {"correct": 0, "total": 0}),
        "by_template": defaultdict(lambda: {"correct": 0, "total": 0}),
        "error_details": [],
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        # 状态判定
        g_status = g_gold.get("status")
        h_status = h_gold.get("status")
        if g_status and h_status:
            results["status_total"] += 1
            results["by_status"][g_status]["total"] += 1
            results["by_template"][g.get("template_family", "unknown")]["total"] += 1
            if g_status == h_status:
                results["status_correct"] += 1
                results["by_status"][g_status]["correct"] += 1
                results["by_template"][g.get("template_family", "unknown")]["correct"] += 1
            else:
                results["error_details"].append({
                    "sample_id": sid,
                    "expected": g_status,
                    "predicted": h_status,
                })

        # 持久化策略
        g_persist = g_gold.get("persist_policy")
        h_persist = h_gold.get("persist_policy")
        if g_persist and h_persist:
            results["persist_total"] += 1
            if g_persist == h_persist:
                results["persist_correct"] += 1

    return results


def format_tool_report(r):
    lines = []
    lines.append("### Tool Result")
    status_acc = safe_divide(r["status_correct"], r["status_total"])
    persist_acc = safe_divide(r["persist_correct"], r["persist_total"])
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    lines.append(f"- 状态判定准确率: {r['status_correct']}/{r['status_total']} = **{status_acc:.2%}**")
    lines.append(f"- 持久化策略准确率: {r['persist_correct']}/{r['persist_total']} = **{persist_acc:.2%}**")
    lines.append("")
    lines.append("#### 按状态类型分组")
    for st in sorted(r["by_status"]):
        d = r["by_status"][st]
        ca = safe_divide(d["correct"], d["total"])
        lines.append(f"  - {st}: {d['correct']}/{d['total']} = {ca:.2%}")
    lines.append("")
    if r["error_details"]:
        lines.append("#### 错误详情")
        for e in r["error_details"][:20]:
            lines.append(f"  - {e['sample_id']}: 期望={e['expected']}, 预测={e['predicted']}")
        if len(r["error_details"]) > 20:
            lines.append(f"  ... 还有 {len(r['error_details']) - 20} 条错误")
        lines.append("")
    lines.append(f"**状态判定准确率={status_acc:.2%}**  (阈值: >=90%)  {'✅ 通过' if status_acc >= 0.90 else '❌ 未通过'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 6. 端到端会话 (end_to_end_session)
# ──────────────────────────────────────────────

def eval_end_to_end(gold_list, hyp_list):
    gold_map = {g["sample_id"]: g for g in gold_list}
    hyp_map = {h["sample_id"]: h for h in hyp_list if h.get("sample_id")}

    shared_ids = sorted(set(gold_map) & set(hyp_map))
    results = {
        "task": "end_to_end_session",
        "total_gold": len(gold_list),
        "total_hyp": len(hyp_list),
        "matched": len(shared_ids),
        "memory_coverage": [],
        "response_match": 0,
        "response_total": 0,
        "failed_cases": [],
    }

    for sid in shared_ids:
        g = gold_map[sid]
        h = hyp_map[sid]
        g_gold = g.get("gold", {})
        h_gold = h.get("gold", {})

        # 期望记忆覆盖
        g_memory = g_gold.get("expected_memory", [])
        h_memory = h_gold.get("retrieved_memory", [])
        if g_memory and h_memory:
            g_set = set(g_memory) if isinstance(g_memory, list) else set(g_memory.keys())
            h_set = set(h_memory) if isinstance(h_memory, list) else set(h_memory.keys())
            if g_set:
                coverage = len(g_set & h_set) / len(g_set)
                results["memory_coverage"].append(coverage)

        # 期望响应匹配
        g_response = g_gold.get("expected_response", "")
        h_response = h_gold.get("actual_response", "")
        if g_response and h_response:
            results["response_total"] += 1
            if g_response == h_response:
                results["response_match"] += 1
            else:
                results["failed_cases"].append({
                    "sample_id": sid,
                    "expected": g_response[:100],
                    "actual": h_response[:100],
                })

    return results


def format_end_to_end_report(r):
    lines = []
    lines.append("### 端到端会话 (End-to-End Session)")
    lines.append(f"- Gold 样本数: {r['total_gold']} | 预测样本数: {r['total_hyp']} | 匹配: {r['matched']}")
    if r["memory_coverage"]:
        avg_cov = sum(r["memory_coverage"]) / len(r["memory_coverage"])
        lines.append(f"- 平均记忆覆盖: {avg_cov:.2%}")
    response_acc = safe_divide(r["response_match"], r["response_total"])
    lines.append(f"- 响应匹配准确率: {r['response_match']}/{r['response_total']} = **{response_acc:.2%}**")
    lines.append("")
    if r["failed_cases"]:
        lines.append("#### 失败案例")
        for c in r["failed_cases"][:10]:
            lines.append(f"  - {c['sample_id']}: 期望=`{c['expected']}`, 实际=`{c['actual']}`")
        if len(r["failed_cases"]) > 10:
            lines.append(f"  ... 还有 {len(r['failed_cases']) - 10} 条失败")
        lines.append("")
    lines.append(f"**响应匹配准确率={response_acc:.2%}**  (阈值: >=80%)  {'✅ 通过' if response_acc >= 0.80 else '❌ 未通过'}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────

TASK_EVAL_MAP = {
    "preference_extraction": (eval_preference_extraction, format_preference_report),
    "knowledge_retrieval": (eval_knowledge_retrieval, format_retrieval_report),
    "conflict_resolution": (eval_conflict_resolution, format_conflict_report),
    "precise_forgetting": (eval_precise_forgetting, format_forgetting_report),
    "tool_result": (eval_tool_result, format_tool_report),
    "end_to_end_session": (eval_end_to_end, format_end_to_end_report),
}


def main():
    ap = argparse.ArgumentParser(description="麒麟 OS Agent 记忆模块指标计算框架 v1.0")
    ap.add_argument("--gold", required=True, help="Gold JSONL 文件路径，支持通配符")
    ap.add_argument("--hyp", required=True, help="模型预测 JSONL 目录或文件路径")
    ap.add_argument("--report", default="", help="输出报告 Markdown 路径（默认 stdout）")
    ap.add_argument("--threshold", action="store_true", help="输出通过/未通过判断")
    args = ap.parse_args()

    # 加载 gold
    import glob
    gold_files = sorted(glob.glob(args.gold))
    gold_all = []
    for f in gold_files:
        gold_all.extend(load_jsonl(f))
    print(f"[INFO] 加载 Gold: {len(gold_files)} 个文件, {len(gold_all)} 条", file=sys.stderr)

    # 按 task_type 分组
    gold_by_task = defaultdict(list)
    for g in gold_all:
        gold_by_task[g.get("task_type", "unknown")].append(g)

    # 加载 hyp
    if os.path.isdir(args.hyp):
        hyp_files = sorted(glob.glob(os.path.join(args.hyp, "*.jsonl")))
    else:
        hyp_files = sorted(glob.glob(args.hyp))
    hyp_all = []
    for f in hyp_files:
        hyp_all.extend(load_jsonl(f))
    print(f"[INFO] 加载预测: {len(hyp_files)} 个文件, {len(hyp_all)} 条", file=sys.stderr)

    hyp_by_task = defaultdict(list)
    for h in hyp_all:
        hyp_by_task[h.get("task_type", "unknown")].append(h)

    # 计算指标
    report_lines = []
    report_lines.append("# 麒麟 OS Agent 记忆模块指标报告\n")
    report_lines.append(f"- 生成时间: {__import__('datetime').datetime.now().isoformat()}")
    report_lines.append(f"- Gold 路径: {args.gold}")
    report_lines.append(f"- 预测路径: {args.hyp}")
    report_lines.append(f"- Gold 总条数: {len(gold_all)}")
    report_lines.append(f"- 预测总条数: {len(hyp_all)}")
    report_lines.append("")

    all_pass = True
    for task_type in sorted(TASK_EVAL_MAP):
        eval_fn, fmt_fn = TASK_EVAL_MAP[task_type]
        g_list = gold_by_task.get(task_type, [])
        h_list = hyp_by_task.get(task_type, [])
        if not g_list:
            report_lines.append(f"## {task_type}\n无 Gold 数据，跳过。\n")
            continue
        if not h_list:
            report_lines.append(f"## {task_type}\n⚠️ 无预测数据，无法计算指标。\n")
            all_pass = False
            continue
        result = eval_fn(g_list, h_list)
        section = fmt_fn(result)
        report_lines.append(section)

    # 汇总
    report_lines.append("---\n## 汇总\n")
    report_lines.append(f"**全部指标: {'✅ 全部通过' if all_pass else '❌ 存在未通过项'}**")
    report_lines.append("")
    report_lines.append("### 阈值标准参考")
    report_lines.append("| 指标 | 阈值 | 来源 |")
    report_lines.append("| --- | --- | --- |")
    report_lines.append("| 偏好提取 F1 | >= 85% | 手册第 2 章 |")
    report_lines.append("| 知识检索 Recall@K | >= 85% | 手册第 2 章 |")
    report_lines.append("| 冲突处理准确率 | >= 88% | 手册第 2 章 |")
    report_lines.append("| 精准遗忘删除正确率 | >= 95% | 手册第 2 章 |")
    report_lines.append("| Tool Result 状态判定 | >= 90% | 手册第 2 章 |")
    report_lines.append("| 端到端响应匹配 | >= 80% | 手册第 2 章 |")
    report_lines.append("")
    report_lines.append("> 注意：响应时间指标（P50/P95 <= 500ms）需在麒麟 VM 上使用 `run_runtime_replay.sh` 实测，本脚本不涉及。\n")

    report_text = "\n".join(report_lines)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"[INFO] 报告已写入: {args.report}", file=sys.stderr)
    else:
        print(report_text)


if __name__ == "__main__":
    main()