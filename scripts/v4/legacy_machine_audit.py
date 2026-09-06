#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 P11 Legacy Machine Auditor（Data-B，2026-09-06）

基于 C1 冻结账本(legacy_inventory_v4_full.jsonl) 与 P2-A 机器工具输出
(prov/dedup/leak report)，对 465 IN_SCOPE 逐样本聚合机器审计结果，
输出 legacy_machine_audit_v4.1.jsonl（P11 输出契约）+ summary。

机器可判项：provenance / license / exact-dup / near-dup(>0.85 -> Reviewer) /
template 集中度 / leakage。语义裁决(REUSE/REWORK/RELABEL/DROP)归 P10(A)+Data-R，
本脚本不写 human_decision、不产 Gold、不修改 data/raw。

用法：
  python scripts/v4/legacy_machine_audit.py \
    --ledger reports/legacy_inventory_v4_full.jsonl \
    --prov reports/prov_report_v4.1_d1.json \
    --dedup reports/dedup_report_v4.1_d1.json \
    --leak reports/leak_report_v4.1_d1.json \
    --out reports/legacy_machine_audit_v4.1.jsonl
"""
import argparse
import json
import os
import sys

APPROVED_TEMPLATE_MAX = 0.25


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--prov", required=True)
    ap.add_argument("--dedup", required=True)
    ap.add_argument("--leak", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ledger = load_jsonl(args.ledger)
    prov = json.load(open(args.prov, encoding="utf-8"))
    dedup = json.load(open(args.dedup, encoding="utf-8"))
    leak = json.load(open(args.leak, encoding="utf-8"))

    inscope = [r for r in ledger if r.get("inventory_status") == "IN_SCOPE"]
    if not inscope:
        print("FAIL_CLOSED: ledger 无 IN_SCOPE")
        sys.exit(2)

    prov_status = {u["sample_id"]: u for u in prov.get("unresolved", [])}
    dedup_samples = dedup.get("samples", {})
    near_pairs = dedup.get("near_duplicate_pairs", [])
    near_by_sid = {}
    for n in near_pairs:
        near_by_sid.setdefault(n["a"], []).append(n)
        near_by_sid.setdefault(n["b"], []).append(n)
    fam_share = dedup.get("template_family_share", {})
    over_conc = set(dedup.get("template_over_concentration", []))
    leak_hits = {h["sample_id"]: h for h in leak.get("hits", [])}

    # 归因 leak 命中类型
    def classify_leak(sid, inv):
        h = leak_hits.get(sid)
        if not h:
            return "CLEAN", None
        fp = inv.get("file_path", "")
        if "sealed_test" in fp:
            return "REGISTERED_EXPOSURE", "sealed_v1_template_exposed(DEV_REG_ONLY, C2 已登记)"
        # 非 sealed 命中：检查是否 raw 序号碰撞（raw_id 过短）
        mfs = h.get("matched_fingerprints", [])
        raw_matches = [m for m in mfs if m.startswith("raw:")]
        if raw_matches:
            return "FALSE_POSITIVE_RAWID_COLLISION", "raw_id 短序号与 leak registry 重叠，需人工复核(raw 指纹)"
        return "REVIEW", ";".join(mfs)

    rows_out = []
    counters = {"provenance_unresolved": 0, "leak_clean": 0, "leak_registered": 0,
                "leak_fp_collision": 0, "near_dup_samples": 0, "template_over": 0}
    for inv in inscope:
        sid = inv.get("sample_id")
        fam = inv.get("template_family") or "none"
        share = fam_share.get(fam, 0.0)
        near = near_by_sid.get(sid, [])
        leak_status, leak_reason = classify_leak(sid, inv)
        prov_st = "UNRESOLVED" if sid in prov_status else "RESOLVED"
        # 机器行判定（仅标注，不代替人工语义裁决）
        reasons = []
        if prov_st == "UNRESOLVED":
            counters["provenance_unresolved"] += 1
            reasons.append("provenance_unresolved")
        if near:
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

        if leak_status == "REGISTERED_EXPOSURE":
            split_elig = "DEV_REG_ONLY"
        else:
            split_elig = "ANY_PENDING_P10"
        machine_status = "NEEDS_HUMAN_REVIEW"
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
                "near_duplicate_pairs": len(near),
                "template_share": round(share, 4),
                "template_concentration_ok": fam not in over_conc,
                "leak_status": leak_status,
                "leak_reason": leak_reason,
            },
            "split_eligibility": split_elig,
            "machine_status": machine_status,
            "review_owner": "Data-A(P10 semantic)/Data-R(final)",
        })
    summary = {
        "schema": "legacy_machine_audit_v4.1",
        "version": "v4.1",
        "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)",
        "input_ledger": args.ledger,
        "input_set_sha256": leak.get("input_set_hash"),
        "total_in_scope": len(inscope),
        "counters": counters,
        "thresholds": {
            "near_dup_similarity": 0.85,
            "template_max_share": APPROVED_TEMPLATE_MAX,
            "rule": "unresolved_provenance>0->FAIL; exact_dup>0->FAIL; leak>0->FAIL; sim>0.85->Reviewer; single_template>25%->FAIL"
        },
        "machine_conclusion": "legacy 465 为 v1 模板/旧格式源，机器可判项见 counters；语义处置归 P10(A)+Data-R，本报告不代判",
        "tool_evidence": [args.prov, args.dedup, args.leak],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.write(json.dumps({"__summary__": summary}, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
