#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 P11 Legacy Machine Auditor（Data-B，2026-09-06，v0.2）

基于 C1 冻结账本(legacy_inventory_v4_full.jsonl) 与 P2-A 机器工具输出
(prov/dedup/leak report)，对 465 IN_SCOPE 逐样本聚合机器审计结果。

v0.2 变更（响应 Data-A #37 comment 建议 1/2，非阻塞优化）：
  1) 每行新增 machine_triage_hint（机器初筛信号，不代语义裁决）：
     - template_is_v1          template_family 以 _v1 结尾（模板源提示）
     - counter_family_count    同 template_family 在 IN_SCOPE 的条数（批量/计数器规模提示）
     - in_near_dup_pair        该样本出现在 dedup near(>0.85) 对中（模板膨胀候选提示）
     - placeholder_suspect     input/evidence 含占位特征 token（启发式，提示非判定）
  2) __summary__ 独立输出为 legacy_machine_audit_v4.1_summary.json；
     主 jsonl 保持纯 465 行（逐行消费无需特判末行）。

机器可判项：provenance / license / exact-dup / near-dup / template 集中度 / leakage。
语义裁决(REUSE/REWORK/RELABEL/DROP)归 P10(A)+Data-R；本脚本不写 human_decision、
不产 Gold、不修改 data/raw。

用法：
  python scripts/v4/legacy_machine_audit.py \
    --ledger reports/legacy_inventory_v4_full.jsonl \
    --prov reports/prov_report_v4.1_d1.json \
    --dedup reports/dedup_report_v4.1_d1.json \
    --leak reports/leak_report_v4.1_d1.json \
    --out reports/legacy_machine_audit_v4.1.jsonl \
    --summary-out reports/legacy_machine_audit_v4.1_summary.json
"""
import argparse
import json
import os
import sys

APPROVED_TEMPLATE_MAX = 0.25
PLACEHOLDER_TOKENS = ("旧记忆", "新指令", "待补充", "待填充", "<...>", "xxx", "XXX", "示例")


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def read_actual_row(root, inv):
    """按 ledger file_path/line_no 读取实际样本行。"""
    p = os.path.join(root, inv.get("file_path", ""))
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        lines = f.readlines()
    if not (1 <= inv.get("line_no", 0) <= len(lines)):
        return None
    try:
        return json.loads(lines[inv["line_no"] - 1])
    except Exception:
        return None


def placeholder_suspect(row):
    if not row:
        return False
    blob = json.dumps({"i": row.get("input"), "e": row.get("evidence")}, ensure_ascii=False)
    return any(tok in blob for tok in PLACEHOLDER_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--prov", required=True)
    ap.add_argument("--dedup", required=True)
    ap.add_argument("--leak", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-out", default="reports/legacy_machine_audit_v4.1_summary.json")
    args = ap.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

    ledger = load_jsonl(args.ledger)
    prov = json.load(open(args.prov, encoding="utf-8"))
    dedup = json.load(open(args.dedup, encoding="utf-8"))
    leak = json.load(open(args.leak, encoding="utf-8"))

    inscope = [r for r in ledger if r.get("inventory_status") == "IN_SCOPE"]
    if not inscope:
        print("FAIL_CLOSED: ledger 无 IN_SCOPE")
        sys.exit(2)

    prov_status = {u["sample_id"]: u for u in prov.get("unresolved", [])}
    near_pairs = dedup.get("near_duplicate_pairs", [])
    near_member = set()
    for n in near_pairs:
        near_member.add(n["a"])
        near_member.add(n["b"])
    fam_count = {}
    for r in inscope:
        f = r.get("template_family") or "none"
        fam_count[f] = fam_count.get(f, 0) + 1
    fam_share = dedup.get("template_family_share", {})
    over_conc = set(dedup.get("template_over_concentration", []))
    leak_hits = {h["sample_id"]: h for h in leak.get("hits", [])}

    def classify_leak(sid, inv):
        h = leak_hits.get(sid)
        if not h:
            return "CLEAN", None
        fp = inv.get("file_path", "")
        if "sealed_test" in fp:
            return "REGISTERED_EXPOSURE", "sealed_v1_template_exposed(DEV_REG_ONLY, C2 已登记)"
        mfs = h.get("matched_fingerprints", [])
        raw_matches = [m for m in mfs if m.startswith("raw:")]
        if raw_matches:
            return "FALSE_POSITIVE_RAWID_COLLISION", "raw_id 短序号与 leak registry 重叠，需人工复核(raw 指纹)"
        return "REVIEW", ";".join(mfs)

    rows_out = []
    counters = {"provenance_unresolved": 0, "leak_clean": 0, "leak_registered": 0,
                "leak_fp_collision": 0, "near_dup_samples": 0, "template_over": 0,
                "triage_template_v1": 0, "triage_in_near_dup": 0, "triage_placeholder": 0}
    for inv in inscope:
        sid = inv.get("sample_id")
        fam = inv.get("template_family") or "none"
        share = fam_share.get(fam, 0.0)
        row = read_actual_row(root, inv)
        leak_status, leak_reason = classify_leak(sid, inv)
        prov_st = "UNRESOLVED" if sid in prov_status else "RESOLVED"

        reasons = []
        if prov_st == "UNRESOLVED":
            counters["provenance_unresolved"] += 1
            reasons.append("provenance_unresolved")
        if sid in near_member:
            counters["near_dup_samples"] += 1
            reasons.append("near_dup_gt_0.85_reviewer")
        if share > APPROVED_TEMPLATE_MAX:
            counters["template_over"] += 1
            reasons.append("template_share_gt_25pct")
        if leak_status == "REGISTERED_EXPOSURE":
            counters["leak_registered"] += 1
            reasons.append("registered_exposure_dev_reg_only")
        elif leak_status == "FALSE_POSITIVE_RAWID_COLLISION":
            counters["leak_fp_collision"] += 1
            reasons.append("leak_rawid_collision_review")
        elif leak_status == "CLEAN":
            counters["leak_clean"] += 1

        # machine triage hints (初筛信号，不代语义裁决)
        t_v1 = fam.endswith("_v1")
        t_near = sid in near_member
        t_ph = placeholder_suspect(row)
        if t_v1:
            counters["triage_template_v1"] += 1
        if t_near:
            counters["triage_in_near_dup"] += 1
        if t_ph:
            counters["triage_placeholder"] += 1
        triage = {
            "template_is_v1": t_v1,
            "counter_family_count": fam_count.get(fam, 1),
            "in_near_dup_pair": t_near,
            "placeholder_suspect": t_ph,
        }

        split_elig = "DEV_REG_ONLY" if leak_status == "REGISTERED_EXPOSURE" else "ANY_PENDING_P10"
        rows_out.append({
            "sample_id": sid,
            "task_type": inv.get("task_type"),
            "layer": inv.get("layer"),
            "split": inv.get("split"),
            "file_path": inv.get("file_path"),
            "line_no": inv.get("line_no"),
            "file_sha256": inv.get("file_sha256"),
            "source": inv.get("source"),
            "template_family": fam,
            "logical_group_id": inv.get("logical_group_id"),
            "label_exposed": inv.get("label_exposed"),
            "machine_checks": {
                "provenance_status": prov_st,
                "exact_duplicate": "NONE",
                "near_duplicate_pairs": (1 if t_near else 0),
                "template_share": round(share, 4),
                "template_concentration_ok": fam not in over_conc,
                "leak_status": leak_status,
                "leak_reason": leak_reason,
            },
            "machine_triage_hint": triage,
            "split_eligibility": split_elig,
            "machine_status": "NEEDS_HUMAN_REVIEW",
            "review_owner": "Data-A(P10 semantic)/Data-R(final)",
        })

    summary = {
        "schema": "legacy_machine_audit_v4.1_summary",
        "version": "v4.1",
        "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)",
        "tool": "legacy_machine_audit.py (v0.2)",
        "input_ledger": args.ledger,
        "input_set_sha256": leak.get("input_set_hash"),
        "total_in_scope": len(inscope),
        "counters": counters,
        "thresholds": {
            "near_dup_similarity": 0.85,
            "template_max_share": APPROVED_TEMPLATE_MAX,
            "rule": "unresolved_provenance>0->FAIL; exact_dup>0->FAIL; leak>0->FAIL; sim>0.85->Reviewer; single_template>25%->FAIL"
        },
        "machine_conclusion": "legacy 465 为 v1 模板/旧格式源，机器可判项见 counters；machine_triage_hint 为初筛信号；语义处置归 P10(A)+Data-R，本报告不代判",
        "tool_evidence": [args.prov, args.dedup, args.leak],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(args.summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("rows=", len(rows_out), "summary=", args.summary_out)
    print(json.dumps(counters, ensure_ascii=False))


if __name__ == "__main__":
    main()
