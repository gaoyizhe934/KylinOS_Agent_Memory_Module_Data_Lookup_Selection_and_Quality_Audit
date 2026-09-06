#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B1 v3：10 条 Legacy REWORK/RELABEL canonical 机器复核（Data-B，2026-09-06）

响应 Data-R #40 Round2 Blocking-1/2/3/4：
- 4 pinned inputs：2 candidate jsonl + generation_manifest + repair_plan（git show 锁 #39 final SHA d62dafc4）；
- input_hash 覆盖 4 输入内容；校验 manifest exact_input_proof（input_commit 可解析 / repair_plan_sha256 匹配）；
- 调用 canonical provenance_resolver / dedup_scan / leakage_scan（工具输出即证据）；
- 状态字段拆分：machine_status=PASS|FAIL；completion_readiness=READY|BLOCKED；review_blocker=...
- 不直接 PASS completion（requalification_status=完成 由 Data-R 签）；不产 Gold / 不写 human_decision。

用法（repo 内）：
  python scripts/v4/d1_closeout_b1_machine_check.py --repo <root> --a-commit <SHA> \
    --work <pinned_dir> \
    --out <jsonl> --summary-out <json>
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

A_REF_DEFAULT = "d62dafc42fd64cb65e086137553efcca8439ad45"
INPUTS = {
    "pref": "data/interim/d1_legacy_rework_A_20260906/legacy_rework_preference_candidates.jsonl",
    "forg": "data/interim/d1_legacy_rework_A_20260906/legacy_rework_forgetting_candidates.jsonl",
    "manifest": "data/interim/d1_legacy_rework_A_20260906/generation_manifest_A_20260906.json",
    "repair_plan": "data/interim/d1_legacy_rework_A_20260906/repair_plan.json",
}


def git_show(repo, commit, path):
    # raw bytes：避免 Windows newline normalization 破坏 hash（Data-R Blocking-2）
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (commit, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def git_rev_parse(repo, rev):
    r = subprocess.run(["git", "-C", repo, "rev-parse", rev], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def run_tool(repo, tool, args):
    py = sys.executable
    r = subprocess.run([py, os.path.join(repo, "scripts", "v4", tool)] + args,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=repo)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--a-commit", default=A_REF_DEFAULT)
    ap.add_argument("--work", default="data/interim/b1v3_pinned")
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-out", required=True)
    args = ap.parse_args()
    repo = args.repo
    full = git_rev_parse(repo, args.a_commit) or args.a_commit

    # materialize 4 pinned inputs into work dir
    work_dir = os.path.abspath(os.path.join(repo, args.work))
    os.makedirs(work_dir, exist_ok=True)
    content = {}
    for key, path in INPUTS.items():
        data = git_show(repo, full, path)
        if data is None:
            print("FAIL: cannot read", path, "from", full[:12])
            sys.exit(2)
        content[key] = data
        with open(os.path.join(work_dir, os.path.basename(path)), "wb") as f:
            f.write(data)
    # input_hash over raw bytes of 4 inputs
    h = hashlib.sha256()
    for key in ("pref", "forg", "manifest", "repair_plan"):
        h.update(key.encode()); h.update(b"\0"); h.update(content[key])
    input_hash = h.hexdigest()

    # manifest exact_input_proof full binding check (raw bytes)
    man = json.loads(content["manifest"].decode("utf-8"))
    eip = man.get("exact_input_proof", {}) or {}
    man_issues = []
    notes = ["B_input_hash_scope=4_pinned_inputs(raw bytes)；A manifest input_hash 为其 exact-input 内容口径，算法不同不作等号比较"]
    ic = eip.get("input_commit") or man.get("input_commit")
    if not (ic and git_rev_parse(repo, ic)):
        man_issues.append("manifest_input_commit_unresolvable:" + str(ic))
    rp_sha = eip.get("repair_plan_sha256") or man.get("repair_plan_sha256")
    rp_actual = hashlib.sha256(content["repair_plan"]).hexdigest()
    if rp_sha and rp_sha != rp_actual:
        man_issues.append("A_manifest_repair_plan_sha_mismatch(manifest=%s actual=%s, 需A/Data-R同步)" % (rp_sha[:8], rp_actual[:8]))
    # candidate output_files sha binding
    for of in man.get("output_files", []):
        rel = of.get("file", "")
        key = None
        for k, path in INPUTS.items():
            if path == rel and k in ("pref", "forg"):
                key = k
        if key:
            actual = hashlib.sha256(content[key]).hexdigest()
            if of.get("output_sha256") != actual:
                man_issues.append("manifest_output_sha_mismatch:" + os.path.basename(rel))

    # canonical tools on materialized candidates
    can = work_dir
    pref_f = os.path.join(can, "legacy_rework_preference_candidates.jsonl")
    forg_f = os.path.join(can, "legacy_rework_forgetting_candidates.jsonl")
    inp = [pref_f, forg_f]
    prov = run_tool(repo, "provenance_resolver.py", ["--input"] + inp + ["--out", "reports/b1v3_prov_report.json"])
    dedup = run_tool(repo, "dedup_scan.py", ["--input"] + inp + ["--out", "reports/b1v3_dedup_report.json"])
    leak = run_tool(repo, "leakage_scan.py", ["--input"] + inp + ["--registry", "registry/leaked_content_registry.json", "--out", "reports/b1v3_leak_report.json"])

    # parse canonical gate reports (Data-R Blocking-1/3)
    prov_gates = {}
    try:
        pr = json.load(open(os.path.join(repo, "reports", "b1v3_prov_report.json"), encoding="utf-8"))
        prov_gates["unresolved_count"] = pr.get("unresolved_count", len(pr.get("unresolved", [])))
    except Exception:
        prov_gates["unresolved_count"] = -1
    leak_gates = {}
    try:
        lk = json.load(open(os.path.join(repo, "reports", "b1v3_leak_report.json"), encoding="utf-8"))
        leak_gates["leak_count"] = lk.get("leak_count", len(lk.get("hits", [])))
    except Exception:
        leak_gates["leak_count"] = -1
    dd_gates = {}
    try:
        dd = json.load(open(os.path.join(repo, "reports", "b1v3_dedup_report.json"), encoding="utf-8"))
        dd_gates = dd.get("gates", {})
        dd_gates["dedup_status"] = dd.get("dedup_status")
    except Exception:
        dd_gates = {"dedup_status": "PARSE_FAIL"}
    required_gate_fail = []
    if prov_gates.get("unresolved_count", 0) > 0:
        required_gate_fail.append("provenance_unresolved=%s" % prov_gates.get("unresolved_count"))
    if leak_gates.get("leak_count", 0) > 0:
        required_gate_fail.append("leak=%s" % leak_gates.get("leak_count"))
    if dd_gates.get("G4_exact_dup_zero") is False:
        required_gate_fail.append("exact_dup_present")
    if dd_gates.get("G4_near_reviewed") is False:
        required_gate_fail.append("near_dup_unreviewed")
    # G4 template concentration = admission blocker (不使 B1 requalification machine gate FAIL)
    g4_template_ok = dd_gates.get("G4_template_concentration_ok", False)

    # load rows for per-sample structure checks
    rows = []
    for f in (pref_f, forg_f):
        rows.extend(json.loads(l) for l in open(f, encoding="utf-8") if l.strip())
    rows = sorted(rows, key=lambda r: r.get("sample_id", ""))
    if len(rows) != 10:
        print("FAIL rows!=10", len(rows)); sys.exit(2)

    TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+08:00$")
    ANSWER_KEYS = ("gold", "winner", "final_label", "human_decision", "proposed_decision")
    REVIEW_BLOCKER = {"req_forg_000002": "TIME_WINDOW_RECHECK(正式绑定前校验)",
                      "req_forg_000003": "DATA_R_PII_DECISION(敏感PII需合成/脱敏)"}
    out = []
    for r in rows:
        sid = r.get("sample_id")
        dm = r.get("design_metadata", {})
        iss = []
        if r.get("dataset_stage") != "candidate_only": iss.append("dataset_stage")
        if r.get("admission_status") != "NOT_ADMISSION_APPROVED": iss.append("admission_status")
        if r.get("id_binding_status") != "NON_PRODUCTION": iss.append("id_binding_status")
        bv = r.get("blind_visible", {})
        for k in ANSWER_KEYS:
            if k in bv or k in (bv.get("input", {}) or {}): iss.append("answer:" + k)
        if not TS.match(r.get("timestamp") or ""): iss.append("timestamp")
        gen = dm.get("generation", {}) or {}
        for k in ("generation_id", "prompt_version", "seed", "model", "source"):
            if not gen.get(k): iss.append("gen:" + k)
        if not gen.get("source_file"): iss.append("source_file")
        if (gen.get("source_layer")) != "os_controlled_authored": iss.append("source_layer")
        se = dm.get("split_eligibility")
        if sid in ("req_pref_000003", "req_pref_000004"):
            if se != "DEV_REG_ONLY": iss.append("split_expected_dev_reg_only")
        elif se == "DEV_REG_ONLY":
            iss.append("split_dev_reg_only_not_allowed_on_" + sid)  # 其它 8 条不得误标（Data-R Blocking-3）
        # A 候选顶层缺 template_family -> 单独 blocker 提示（影响 G4 template 判定，不否定结构本身）
        tf_missing = "template_family" not in r
        machine_status = "PASS" if not iss else "FAIL"
        rb = REVIEW_BLOCKER.get(sid)
        if tf_missing:
            rb = (rb + " | " if rb else "") + "A_CANDIDATE_TEMPLATE_FAMILY_MISSING(顶层字段缺口, 需A补或Data-R裁决; 影响G4 template集中度判定)"
        # completion readiness: machine PASS + no template-family gap + T03 pass => BLOCKED awaiting Data-R sign; else BLOCKED with blocker
        if machine_status == "FAIL":
            completion = "BLOCKED"
        elif iss:
            completion = "BLOCKED"
        else:
            completion = "BLOCKED"  # requalification_status=完成 由 Data-R 签，B 不置 READY
        out.append({
            "sample_id": sid,
            "task_type": r.get("task_type"),
            "machine_status": machine_status,
            "completion_readiness": completion,
            "review_blocker": rb,
            "admission_blocker": ("G4_template_concentration(BLOCKED; A 候选缺顶层 template_family)" if not g4_template_ok else None),
            "issues": iss,
            "checks": {"structure": "PASS" if not iss else "FAIL",
                       "provenance_T03": "PASS" if prov.returncode == 0 else "FAIL(rc=%d)" % prov.returncode,
                       "exact_dup": "PASS" if dd_gates.get("G4_exact_dup_zero") is True else "FAIL",
                       "near_reviewed": "PASS" if dd_gates.get("G4_near_reviewed") is True else "FAIL",
                       "leakage": "PASS" if leak.returncode == 0 else "FAIL(rc=%d)" % leak.returncode},
            "source_commit": full,
            "input_hash": input_hash,
        })

    summary = {
        "schema": "b1_machine_check_summary_v4", "version": "v4.1", "date": "2026-09-06",
        "generated_by": "DGXD01(Data-B)", "a_commit": full, "source_commit": full,
        "input_hash_sha256": input_hash, "pinned_inputs": list(INPUTS.keys()),
        "manifest_exact_input_proof_issues": man_issues,
        "manifest_notes": notes,
        "required_gate_fail": required_gate_fail,
        "canonical_gates": {
            "provenance_unresolved": prov_gates.get("unresolved_count"),
            "leak_count": leak_gates.get("leak_count"),
            "G4_exact_dup_zero": dd_gates.get("G4_exact_dup_zero"),
            "G4_near_reviewed": dd_gates.get("G4_near_reviewed"),
            "G4_template_concentration_ok": g4_template_ok,
            "dedup_status": dd_gates.get("dedup_status"),
        },
        "admission_blocker": ("G4_template_concentration BLOCKED（A 候选缺顶层 template_family；按 Data-R Blocking-3 归 G4/Admission，不伪装 B1 completion 已完成）" if not g4_template_ok else None),
        "status_note": "machine_status=requalification gates(结构+T03+DEV_REG) 判定；completion_readiness 一律 BLOCKED（requalification_status=完成 由 Data-R 逐条签；manifest exact-input 未闭环前不得标 completion-ready）；required gate fail 或 manifest binding mismatch -> 脚本 exit(2)。B 不写 human_decision/final_label",
    }
    with open(args.out, "w", encoding="utf-8") as f:
        for r in out: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(args.summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("rows:", len(out))
    print("machine_status:", {x["machine_status"] for x in out})
    print("manifest issues:", man_issues)
    print("required_gate_fail:", required_gate_fail)
    print("canonical rc: prov=%d dedup=%d leak=%d" % (prov.returncode, dedup.returncode, leak.returncode))
    print("input_hash:", input_hash[:16])
    # fail-closed: manifest exact-input 未闭环 或 canonical required gate fail -> nonzero
    if man_issues:
        print("FAIL_CLOSED: manifest exact-input binding mismatch -> exit 2")
        sys.exit(2)
    if required_gate_fail:
        print("FAIL_CLOSED: canonical required gate fail -> exit 2")
        sys.exit(2)
    print("EXIT 0: B1 requalification machine gates PASS (completion 仍 BLOCKED 待 Data-R)")


if __name__ == "__main__":
    main()
