#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B1 v2：10 条 Legacy REWORK/RELABEL 独立机器复核（Data-B，2026-09-06）

响应 Data-R #40 Blocking-1/2/3：
  B1-1) repo-relative + CLI；输入锁定 A exact commit（默认 #39 final SHA d62dafc4…）；
        输出记录 source_commit / source_blob_sha / input_hash。
  B1-2) 脚本自写 canonical JSONL（--out）+ summary（--summary-out）；禁止手工二次整理。
  B1-3) 纳入 canonical provenance T03（os_controlled_authored 契约：source_layer /
        prompt_ref active in prompt_registry / scenario_spec_id exists / source_file 可解析，
        经 git show 读 A commit 的 registry/scenario，与 provenance_resolver 契约一致）；
        状态分级：STRUCTURE_PASS / COMPLETION_BLOCKED（待 Data-R 签 requalification_status）
        / PENDING_RECHECK / FAIL_*；不直接 PASS completion。

用法（repo 内，任何 checkout）：
  python scripts/v4/d1_closeout_b1_machine_check.py \
    --repo <repo_root> --a-commit <A_final_sha> \
    --out reports/v4.1_D1_closeout_B1_machine_check_20260906.jsonl \
    --summary-out reports/v4.1_D1_closeout_B1_summary_20260906.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys

A_REF_DEFAULT = "d62dafc42fd64cb65e086137553efcca8439ad45"
A_PATHS = [
    "data/interim/d1_legacy_rework_A_20260906/legacy_rework_preference_candidates.jsonl",
    "data/interim/d1_legacy_rework_A_20260906/legacy_rework_forgetting_candidates.jsonl",
]
REGISTRY_PATHS = {
    "prompt_registry": "registry/prompt_registry.csv",
    "scenario_pref": "data/interim/candidates_v4/scenario_specs/preference_scenarios.json",
    "scenario_conf": "data/interim/candidates_v4/scenario_specs/conflict_scenarios.json",
    "scenario_forg": "data/interim/candidates_v4/scenario_specs/forgetting_scenarios.json",
}
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
ANSWER_KEYS = ("gold", "winner", "final_label", "human_decision", "proposed_decision")
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


def git_show(repo, commit, path):
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (commit, path)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        return None
    return r.stdout


def git_rev_parse(repo, rev):
    r = subprocess.run(["git", "-C", repo, "rev-parse", rev], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def blob_sha(repo, commit, path):
    r = subprocess.run(["git", "-C", repo, "rev-parse", "%s:%s" % (commit, path)],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def load_rows(repo, commit):
    rows = []
    for p in A_PATHS:
        txt = git_show(repo, commit, p)
        if txt is None:
            continue
        rows.extend(json.loads(l) for l in txt.splitlines() if l.strip())
    return rows


def load_prompt_refs(repo, commit):
    txt = git_show(repo, commit, REGISTRY_PATHS["prompt_registry"])
    refs = {}
    if not txt:
        return refs
    lines = txt.splitlines()
    header = [h.strip() for h in lines[0].split(",")]
    for ln in lines[1:]:
        if not ln.strip():
            continue
        cells = [c.strip() for c in ln.split(",")]
        d = dict(zip(header, cells))
        ref = d.get("prompt_ref") or d.get("prompt_id")
        if ref:
            refs[ref] = d.get("status", "").lower()
    return refs


def load_scenario_ids(repo, commit):
    ids = set()
    for key in ("scenario_pref", "scenario_conf", "scenario_forg"):
        txt = git_show(repo, commit, REGISTRY_PATHS[key])
        if not txt:
            continue
        try:
            data = json.loads(txt)
        except Exception:
            continue
        for item in data if isinstance(data, list) else data.get("scenarios", []):
            sid = item.get("scenario_id") or item.get("id") or item.get("spec_id")
            if sid:
                ids.add(sid)
    return ids


def provenance_t03_ok(row, dm, prompt_refs, scenario_ids):
    """canonical T03 os_controlled_authored 校验（与 provenance_resolver 契约一致）。
    字段位置：source_layer/prompt_ref/prompt_version/source_file 位于 design_metadata.generation；
    scenario_spec_id 位于 design_metadata。"""
    gen = dm.get("generation", {}) or {}
    issues = []
    layer = dm.get("source_layer") or gen.get("source_layer")
    if layer != "os_controlled_authored":
        issues.append("source_layer!=os_controlled_authored(" + str(layer) + ")")
    ref = dm.get("prompt_ref") or gen.get("prompt_ref") or gen.get("prompt_version")
    if ref:
        st = prompt_refs.get(ref)
        if st != "active":
            issues.append("prompt_ref_not_active_or_missing:" + str(ref) + ":" + str(st))
    else:
        issues.append("prompt_ref_missing")
    sid_ss = dm.get("scenario_spec_id")
    if sid_ss:
        if sid_ss not in scenario_ids:
            issues.append("scenario_spec_id_not_found:" + str(sid_ss))
    else:
        issues.append("scenario_spec_id_missing")
    sf = gen.get("source_file")
    if not sf:
        issues.append("source_file_missing")
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--a-commit", default=A_REF_DEFAULT)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-out", required=True)
    args = ap.parse_args()

    repo = args.repo
    commit = args.a_commit
    full = git_rev_parse(repo, commit) or commit
    rows = load_rows(repo, full)
    if len(rows) != 10:
        print("FAIL_CLOSED: loaded rows != 10:", len(rows))
        sys.exit(2)
    prompt_refs = load_prompt_refs(repo, full)
    scenario_ids = load_scenario_ids(repo, full)

    # input hash: canonical bytes of A paths' contents
    input_blob = {}
    h = hashlib.sha256()
    for p in sorted(A_PATHS):
        txt = git_show(repo, full, p) or ""
        h.update(p.encode("utf-8"))
        h.update(b"\0")
        h.update(txt.encode("utf-8"))
        input_blob[p] = blob_sha(repo, full, p)
    input_hash = h.hexdigest()

    out_rows = []
    summary = {
        "schema": "b1_machine_check_summary_v2",
        "version": "v4.1",
        "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)",
        "a_commit": full,
        "source_commit": full,
        "source_blob_sha": input_blob,
        "input_hash_sha256": input_hash,
        "n_rows": len(rows),
    }
    status_count = {}
    for r in sorted(rows, key=lambda x: x.get("sample_id", "")):
        sid = r.get("sample_id", "?")
        dm = r.get("design_metadata", {})
        issues = []
        # structural checks (B1 v1)
        if r.get("dataset_stage") != "candidate_only":
            issues.append("dataset_stage!=candidate_only")
        if r.get("admission_status") != "NOT_ADMISSION_APPROVED":
            issues.append("admission_status!=NOT_ADMISSION_APPROVED")
        if r.get("id_binding_status") != "NON_PRODUCTION":
            issues.append("id_binding_status!=NON_PRODUCTION")
        bv = r.get("blind_visible", {})
        for k in ANSWER_KEYS:
            if k in bv or k in (bv.get("input", {}) or {}):
                issues.append("answer_key_in_blind_visible:" + k)
        if not TS_RE.match(r.get("timestamp") or ""):
            issues.append("timestamp_invalid")
        gen = dm.get("generation", {})
        for k in ("generation_id", "prompt_version", "seed", "model", "source"):
            if not gen.get(k):
                issues.append("generation_missing:" + k)
        se = dm.get("split_eligibility")
        if se not in ("ANY", "DEV_REG_ONLY"):
            issues.append("split_eligibility_invalid")
        if sid in ("req_pref_000004", "req_pref_000003") and se != "DEV_REG_ONLY":
            issues.append("expected_DEV_REG_ONLY")
        fixes = " ".join(json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x for x in (dm.get("applied_fixes") or []))
        fixes += " " + str(dm.get("task_semantic_class") or "") + " " + str(dm.get("preference_scope") or "") + " " + str(dm.get("scope") or "")
        for tok in EXPECT.get(sid, set()):
            if tok.lower() not in fixes.lower():
                issues.append("missing_semantic_token:" + tok)
        # provenance T03
        t03_issues = provenance_t03_ok(r, dm, prompt_refs, scenario_ids)
        if t03_issues:
            issues.append("T03:" + ";".join(t03_issues))
        # readiness grading (no direct PASS of completion)
        if issues:
            readiness = "FAIL_STRUCTURE_OR_T03"
            reasons = issues
        else:
            readiness = "COMPLETION_BLOCKED"  # machine 结构+T03 通过，completion 需 Data-R 签
            reasons = []
        if sid == "req_forg_000002" and not issues:
            readiness = "COMPLETION_BLOCKED_PENDING_RECHECK"
            reasons = ["time_window 边界正式绑定前需校验"]
        if sid == "req_forg_000003" and not issues:
            reasons = ["PII 敏感：正式集需合成/脱敏（Data-R 后续裁决）"]
        status_count[readiness] = status_count.get(readiness, 0) + 1
        out_rows.append({
            "sample_id": sid,
            "task_type": r.get("task_type"),
            "readiness": readiness,
            "reasons": reasons,
            "machine_checks": {
                "structure_status": "PASS" if not issues else "FAIL",
                "provenance_t03": "PASS" if not t03_issues else "FAIL",
                "timestamp": r.get("timestamp"),
                "split_eligibility": se,
                "scenario_spec_id": dm.get("scenario_spec_id"),
                "prompt_ref": gen.get("prompt_ref") or gen.get("prompt_version"),
                "source_layer": gen.get("source_layer"),
            },
            "source_commit": full,
            "input_hash": input_hash,
        })
    summary["status_count"] = status_count
    summary["note"] = "机器复核：结构+T03 通过=COMPLETION_BLOCKED（待 Data-R 逐条签 requalification_status=完成）；不直接 PASS completion"
    with open(args.out, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(args.summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("rows:", len(out_rows), "status:", status_count)
    print("source_commit:", full)
    print("input_hash:", input_hash[:16])


if __name__ == "__main__":
    main()
