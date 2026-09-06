#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B1：10 条 Legacy REWORK/RELABEL 独立机器复核（Data-B，2026-09-06）

对 A（PR #39 feat/A-v4.1-d1-closeout）修复后的 10 条（req_pref_*6 + req_forg_*4）
做独立机器复核，逐条输出 completion readiness。不写 human_decision、不产 Gold。

复核维度（对照 Data-R A1/41bf0e2 fix_fields + v4.1 G1-G5/candidate 约束）：
  1) 身份/状态：candidate_only / NOT_ADMISSION_APPROVED / NON_PRODUCTION（不越权）
  2) 双层结构：blind_visible 无答案(gold/winner/final_label/human_decision)
  3) timestamp 合法（YYYY-MM-DDTHH:MM:SS+08:00；B-L2 修复确认）
  4) generation/provenance 保留（design_metadata.generation: id/prompt_version/seed/model/source）
  5) split_eligibility（pref_000004/000003 须 DEV_REG_ONLY 保留）
  6) 语义断言（applied_fixes 含预期 scope/mode/label 语义，per A1 fix_fields）
  7) 结构/枚举可机器校验部分
输出：每样本 readiness=PASS | PENDING_<reason> | FAIL_<reason>（机器可判，终裁归 Data-R）
"""
import json
import re
import subprocess
import sys

REPO = r"F:\麒麟OS记忆\KylinOS_Agent_Memory_Module_Data_Lookup_Selection_and_Quality_Audit"
A_REF = "origin/feat/A-v4.1-d1-closeout"
A_PATHS = [
    "data/interim/d1_legacy_rework_A_20260906/legacy_rework_preference_candidates.jsonl",
    "data/interim/d1_legacy_rework_A_20260906/legacy_rework_forgetting_candidates.jsonl",
]
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
ANSWER_KEYS = ("gold", "winner", "final_label", "human_decision", "proposed_decision")

# expected semantic tokens per sample (per Data-R A1 fix_fields)
EXPECT = {
    "req_pref_000001": {"topic", "persistent"},
    "req_pref_000002": {"global"},
    "req_pref_000005": {"tool"},
    "req_pref_000004": {"update", "withdraw"},
    "req_pref_000006": {"non_storable"},
    "req_pref_000003": {"task_constraint"},
    "req_forg_000001": {"single_item"},
    "req_forg_000002": {"time_window"},
    "req_forg_000003": {"topic", "sensitivity"},
    "req_forg_000004": {"single_item"},
}


def git_show(path):
    r = subprocess.run(["git", "-C", REPO, "show", A_REF + ":" + path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return []
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]


def check(row):
    sid = row.get("sample_id", "?")
    dm = row.get("design_metadata", {})
    issues = []
    # 1) state flags
    if row.get("dataset_stage") != "candidate_only":
        issues.append("dataset_stage!=candidate_only")
    if row.get("review_status") != "candidate_only":
        issues.append("review_status!=candidate_only")
    if row.get("admission_status") != "NOT_ADMISSION_APPROVED":
        issues.append("admission_status!=NOT_ADMISSION_APPROVED")
    if row.get("id_binding_status") != "NON_PRODUCTION":
        issues.append("id_binding_status!=NON_PRODUCTION")
    # 2) no answers in blind_visible
    bv = row.get("blind_visible", {})
    for k in ANSWER_KEYS:
        if k in bv or k in (bv.get("input", {}) or {}):
            issues.append("answer_key_in_blind_visible:" + k)
    # 3) timestamp
    ts = row.get("timestamp") or ""
    if not TS_RE.match(ts):
        issues.append("timestamp_invalid:" + ts)
    # 4) generation
    gen = dm.get("generation", {})
    for k in ("generation_id", "prompt_version", "seed", "model", "source"):
        if not gen.get(k):
            issues.append("generation_missing:" + k)
    # 5) split eligibility
    se = dm.get("split_eligibility")
    if se not in ("ANY", "DEV_REG_ONLY"):
        issues.append("split_eligibility_invalid:" + str(se))
    if sid in ("req_pref_000004", "req_pref_000003") and se != "DEV_REG_ONLY":
        issues.append("expected_DEV_REG_ONLY_but_" + str(se))
    # 6) semantic expectation via applied_fixes
    fixes = " ".join(dm.get("applied_fixes") or [])
    fixes += " " + str(dm.get("task_semantic_class") or "") + " " + str(dm.get("preference_scope") or "") + " " + str(dm.get("scope") or "")
    fixes_l = fixes.lower()
    for tok in EXPECT.get(sid, set()):
        if tok.lower() not in fixes_l:
            issues.append("missing_semantic_token:" + tok)
    return issues


def main():
    rows = []
    for p in A_PATHS:
        rows.extend(git_show(p))
    print("A rows loaded:", len(rows))
    out_rows = []
    for r in sorted(rows, key=lambda x: x.get("sample_id", "")):
        sid = r.get("sample_id", "?")
        issues = check(r)
        if not issues:
            readiness, reasons = "PASS", []
        else:
            readiness = "FAIL"
            reasons = issues
        # special: time_window boundary note (forg_000002) -> PENDING_RECHECK (not machine-fail)
        if sid == "req_forg_000002" and readiness == "PASS":
            readiness = "PENDING_RECHECK"
            reasons = ["time_window 边界格式需正式前校验(A 自述)"]
        out_rows.append({
            "sample_id": sid,
            "task_type": r.get("task_type"),
            "readiness": readiness,
            "reasons": reasons,
            "checks": {
                "timestamp": r.get("timestamp"),
                "split_eligibility": r.get("design_metadata", {}).get("split_eligibility"),
                "admission_status": r.get("admission_status"),
                "applied_fixes": r.get("design_metadata", {}).get("applied_fixes"),
            },
        })
    print(json.dumps(out_rows, ensure_ascii=False, indent=1))
    return out_rows


if __name__ == "__main__":
    main()
