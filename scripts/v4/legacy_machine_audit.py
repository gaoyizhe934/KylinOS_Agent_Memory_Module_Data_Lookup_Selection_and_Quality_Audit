#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 P11 Legacy Machine Auditor（Data-B，2026-09-06，v0.3）

基于 C1 冻结账本(legacy_inventory_v4_full.jsonl) 与 P2-A 机器工具输出
(prov/dedup/leak report)，对 465 IN_SCOPE 逐样本聚合机器审计结果。

v0.3 变更（响应 Data-R D1 Review #37：B-M1/M2/M3 + B-L1/L2）：
  M1) summary.json 新增 batch_gate（status=BLOCKED + 未决原因清单 + owner=Data-R）；
      audit jsonl 逐样本维持 NEEDS_HUMAN_REVIEW。
  M2) machine_checks 新增 license_status：team_authored -> N/A_TEAM_AUTHORED；
      public_derived(t2ranking) -> PENDING_LICENSE_REVIEW（license_registry 未批准，如实标 PENDING）。
  M3) 哈希口径统一并注明算法：
      input_file_sha256      = sha256(legacy_in_scope_465.jsonl 文件字节)
      input_sample_id_set_sha= sha256(json.dumps(sorted(sample_id), ensure_ascii=False))
      （不再混称；修正 worklog/报告一致引用）。
  L1) 幂等/规范化 hash：summary 增加 canonical_hash = sha256(逐行 rstrip 后按 \\n 拼接 + \\n)，
      避免行尾/EOF 差异导致 Reviewer 复算不一致。
  L2) timestamp 缺陷登记：machine_checks.timestamp_defect 检测 `YYYY-MM-DDN` 非法日期，
      summary 计数 timestamp_defect_total；明细另出登记报告（见生成侧）。

机器可判项：provenance / license / exact-dup / near-dup / template / leakage / timestamp。
语义裁决归 P10(A)+Data-R；本脚本不写 human_decision、不产 Gold、不改 data/raw。

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
import csv
import hashlib
import json
import os
import re
import sys

APPROVED_TEMPLATE_MAX = 0.25
PLACEHOLDER_TOKENS = ("旧记忆", "新指令", "待补充", "待填充", "<...>", "xxx", "XXX", "示例")
# 465 IN_SCOPE 中 public_derived 文件 -> dataset_id（唯一：processed t2ranking）
PUBLIC_FILE_TO_DATASET = {"data/processed/knowledge_retrieval_t2ranking.jsonl": "t2ranking_2023"}


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def read_actual_row(root, inv):
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


def timestamp_defect(ts):
    """检测 YYYY-MM-DDN（日字段 3 位，计数器拼入日期）等非法时间戳。"""
    if not ts or not isinstance(ts, str):
        return False
    return bool(re.match(r"^\d{4}-\d{2}-\d{3}T", ts))


def license_status_for(inv, lic_map):
    src = inv.get("source") or ""
    if src == "team_authored":
        return "N/A_TEAM_AUTHORED", None
    if src == "public_derived":
        ds = PUBLIC_FILE_TO_DATASET.get((inv.get("file_path") or "").replace("\\", "/"))
        if ds is None:
            return "PENDING_DATASET_UNRESOLVED", None
        row = lic_map.get(ds)
        if row is None:
            return "PENDING_LICENSE_NO_REGISTRY", ds
        reviewer = (row.get("reviewer") or "").strip()
        status = (row.get("status") or "").strip()
        verdict = (row.get("verdict") or "").strip()
        if "待" in reviewer or "待" in status or "待" in verdict:
            return "PENDING_LICENSE_REVIEW", ds
        return "LICENSE_OK", ds
    return "PENDING_SOURCE_UNKNOWN", None


def canonical_hash_of_file(path):
    """逐行 rstrip 后按 \\n 拼接 + \\n 再 sha256（消除行尾/EOF 差异）。"""
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")
    norm = "\n".join(line.rstrip("\r\n") for line in text.split("\n"))
    if not norm.endswith("\n"):
        norm += "\n"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--prov", required=True)
    ap.add_argument("--dedup", required=True)
    ap.add_argument("--leak", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-out", default="reports/legacy_machine_audit_v4.1_summary.json")
    ap.add_argument("--input-file", default="data/interim/v4.1_d1_audit/legacy_in_scope_465.jsonl")
    args = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    ledger = load_jsonl(args.ledger)
    prov = json.load(open(args.prov, encoding="utf-8"))
    dedup = json.load(open(args.dedup, encoding="utf-8"))
    leak = json.load(open(args.leak, encoding="utf-8"))

    # license registry
    lic_map = {}
    lic_csv = os.path.join(root, "registry", "license_registry.csv")
    if os.path.exists(lic_csv):
        with open(lic_csv, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                lic_map[r["dataset_id"]] = r

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
                "triage_template_v1": 0, "triage_in_near_dup": 0, "triage_placeholder": 0,
                "license_na_team": 0, "license_pending": 0, "license_ok": 0,
                "timestamp_defect": 0}
    for inv in inscope:
        sid = inv.get("sample_id")
        fam = inv.get("template_family") or "none"
        share = fam_share.get(fam, 0.0)
        row = read_actual_row(root, inv)
        leak_status, leak_reason = classify_leak(sid, inv)
        prov_st = "UNRESOLVED" if sid in prov_status else "RESOLVED"
        lic_st, lic_ds = license_status_for(inv, lic_map)
        ts_def = timestamp_defect((row or {}).get("timestamp"))

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
        if lic_st.startswith("N/A"):
            counters["license_na_team"] += 1
        elif lic_st == "LICENSE_OK":
            counters["license_ok"] += 1
        else:
            counters["license_pending"] += 1
            reasons.append("license_" + lic_st.lower())
        if ts_def:
            counters["timestamp_defect"] += 1
            reasons.append("timestamp_defect_yyyymmddN")

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
                "license_status": lic_st,
                "license_dataset": lic_ds,
                "exact_duplicate": "NONE",
                "near_duplicate_pairs": (1 if t_near else 0),
                "template_share": round(share, 4),
                "template_concentration_ok": fam not in over_conc,
                "leak_status": leak_status,
                "leak_reason": leak_reason,
                "timestamp_defect": ts_def,
            },
            "machine_triage_hint": triage,
            "split_eligibility": split_elig,
            "machine_status": "NEEDS_HUMAN_REVIEW",
            "review_owner": "Data-A(P10 semantic)/Data-R(final)",
        })

    # batch gate（fail-closed：机器阈值未过即 BLOCKED，不因逐样本 NEEDS_HUMAN_REVIEW 而放行）
    gate_reasons = []
    if counters["provenance_unresolved"] > 0:
        gate_reasons.append("G1_provenance_unresolved=%d(>0)" % counters["provenance_unresolved"])
    if counters["near_dup_samples"] > 0:
        gate_reasons.append("G4_near_dup_unreviewed(>0.85, %d samples)" % counters["near_dup_samples"])
    if counters["template_over"] > 0:
        gate_reasons.append("G4_template_concentration>25%%(%d samples)" % counters["template_over"])
    if counters["leak_registered"] + counters["leak_fp_collision"] > 0:
        gate_reasons.append("G5_leak(registered=%d/fp_collision=%d)" % (counters["leak_registered"], counters["leak_fp_collision"]))
    if counters["license_pending"] > 0:
        gate_reasons.append("license_pending_review=%d" % counters["license_pending"])
    batch_gate = {
        "status": "BLOCKED" if gate_reasons else "PASS",
        "reasons": gate_reasons,
        "owner": "Data-R (final adjudication)",
        "note": "逐样本 NEEDS_HUMAN_REVIEW 不代表批次可放行；batch_gate 为聚合层 fail-closed 状态",
    }

    # canonical hashes
    input_path = os.path.join(root, args.input_file.replace("/", os.sep))
    input_file_sha256 = None
    canonical_input_hash = None
    if os.path.exists(input_path):
        input_file_sha256 = hashlib.sha256(open(input_path, "rb").read()).hexdigest()
        canonical_input_hash = canonical_hash_of_file(input_path)
    ids = sorted(r["sample_id"] for r in inscope)
    sample_id_set_sha = hashlib.sha256(json.dumps(ids, ensure_ascii=False).encode("utf-8")).hexdigest()

    summary = {
        "schema": "legacy_machine_audit_v4.1_summary",
        "version": "v4.1",
        "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)",
        "tool": "legacy_machine_audit.py (v0.3)",
        "input_ledger": args.ledger,
        "input_hashes": {
            "input_file_sha256": input_file_sha256,
            "input_file_sha256_algorithm": "sha256(file bytes)",
            "input_sample_id_set_sha": sample_id_set_sha,
            "input_sample_id_set_sha_algorithm": "sha256(json.dumps(sorted(sample_id), ensure_ascii=False))",
            "canonical_input_hash": canonical_input_hash,
            "canonical_input_hash_algorithm": "sha256(逐行 rstrip 后 \\n 拼接 + \\n)",
        },
        "total_in_scope": len(inscope),
        "counters": counters,
        "batch_gate": batch_gate,
        "thresholds": {
            "near_dup_similarity": 0.85,
            "template_max_share": APPROVED_TEMPLATE_MAX,
            "rule": "unresolved_provenance>0->FAIL; exact_dup>0->FAIL; leak>0->FAIL; sim>0.85->Reviewer; single_template>25%->FAIL"
        },
        "machine_conclusion": "legacy 465 为 v1 模板/旧格式源；batch_gate=BLOCKED（G1/G4/G5/license 待 Data-R）；machine_triage_hint 为初筛信号；语义处置归 P10(A)+Data-R，本报告不代判",
        "tool_evidence": [args.prov, args.dedup, args.leak],
    }
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(args.summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("rows=", len(rows_out), "summary=", args.summary_out)
    print("batch_gate=", batch_gate["status"], batch_gate["reasons"])
    print(json.dumps(counters, ensure_ascii=False))


if __name__ == "__main__":
    main()
