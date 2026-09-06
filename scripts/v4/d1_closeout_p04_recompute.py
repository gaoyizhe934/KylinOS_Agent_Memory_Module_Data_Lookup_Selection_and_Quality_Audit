#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B2：P04 动态配额重算 v4（Data-B，2026-09-06）

规则（v4.1 SOP §7/Q7 + 台账 04）：
  accepted_legacy_task = REUSE/REWORK/RELABEL 且 requalification_status=完成（且非 Runtime 静态）
  new_needed = max(target - accepted_legacy, 0)；candidate = ceil(new_needed * 1.3)（Runtime ×1.0 不可抵）

v4（响应 Data-R #45 Blocking-1/2/3）：
  - mapping-aware：Data-R 签署对象是 req_* rework candidate，P04 计 legacy pref_*/forg_*；
    锁 #44 approved A SHA（默认 7c59633…）从 design_metadata.legacy_ref.legacy_sample_id 复算 mapping；
    断言 completed mapping == 复算 mapping（缺 lineage/多对一/重复/不一致 -> exit nonzero）。
  - fail-closed：unknown/duplicate/非 requal/decision∉ACCEPT/Runtime/signed≠effective -> exit nonzero；
    requal source 锁 sha（--requal-sha，缺省仅 preview）。
  - 输出 quota_plan_v4.1.csv + quota_plan_v4.1_summary.json（authority + rework/legacy/mapping sha）。
"""
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys

A_REF_DEFAULT = "7c59633f81b3e4474be8a422450dcc3401940749"
A_PATHS = ["data/interim/d1_legacy_rework_A_20260906/legacy_rework_preference_candidates.jsonl",
           "data/interim/d1_legacy_rework_A_20260906/legacy_rework_forgetting_candidates.jsonl"]
TARGET = {"preference_extraction": 225, "knowledge_retrieval": 175, "conflict_resolution": 125,
          "precise_forgetting": 100, "tool_result": 125, "end_to_end_session": 35}
RUNTIME = {"tool_result", "end_to_end_session"}
ACCEPT = {"REUSE", "REWORK", "RELABEL"}


def git_show(repo, commit, path):
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (commit, path)], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


def expected_mapping(repo, commit):
    mapping = {}
    for p in A_PATHS:
        txt = git_show(repo, commit, p)
        if txt is None:
            print("FAIL: cannot git show %s:%s" % (commit[:12], p)); sys.exit(2)
        for l in txt.splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            lr = (r.get("design_metadata", {}) or {}).get("legacy_ref", {}) or {}
            sid, lsid = r.get("sample_id"), lr.get("legacy_sample_id")
            if sid and lsid:
                if sid in mapping:
                    print("FAIL: duplicate rework sid", sid); sys.exit(2)
                mapping[sid] = lsid
    return mapping


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--requal", required=True)
    ap.add_argument("--requal-sha", default="")
    ap.add_argument("--completed", required=True)
    ap.add_argument("--a-commit", default=A_REF_DEFAULT)
    ap.add_argument("--out-csv", default="reports/quota_plan_v4.1.csv")
    ap.add_argument("--out-json", default="reports/quota_plan_v4.1_summary.json")
    args = ap.parse_args()

    requal_raw = open(args.requal, "rb").read()
    requal_sha = hashlib.sha256(requal_raw).hexdigest()
    if args.requal_sha and args.requal_sha != requal_sha:
        print("FAIL: requal sha mismatch"); sys.exit(2)
    rows = [json.loads(l) for l in requal_raw.decode("utf-8").splitlines() if l.strip()]
    by_sid = {r.get("sample_id"): r for r in rows}

    comp = json.load(open(args.completed, encoding="utf-8"))
    rework_ids = comp.get("completed_rework_ids", [])
    mapping = comp.get("mapping", {})
    # 1) mapping proof vs #44 approved A SHA
    exp_map = expected_mapping(args.repo, args.a_commit)
    issues = []
    if len(rework_ids) != 10:
        issues.append("rework_count!=10:%d" % len(rework_ids))
    if sorted(rework_ids) != sorted(mapping.keys()):
        issues.append("rework_ids_vs_mapping_keys_mismatch")
    if mapping != exp_map:
        diff = {k: (mapping.get(k), exp_map.get(k)) for k in set(mapping) | set(exp_map) if mapping.get(k) != exp_map.get(k)}
        issues.append("mapping_mismatch_vs_44A:" + json.dumps(diff))
    # 2) legacy ids unique + in requal + decision ACCEPT + non-runtime
    seen_legacy = set()
    for rid, lsid in mapping.items():
        if lsid in seen_legacy:
            issues.append("duplicate_legacy:" + lsid)
        seen_legacy.add(lsid)
        r = by_sid.get(lsid)
        if r is None:
            issues.append("legacy_not_in_requal:" + lsid)
            continue
        if r.get("proposed_decision") not in ACCEPT:
            issues.append("decision_not_accepted:" + lsid)
        if r.get("task_type") in RUNTIME:
            issues.append("runtime_static:" + lsid)
    if issues:
        print("FAIL_CLOSED:")
        for i in issues:
            print("  ", i)
        sys.exit(2)
    if not args.requal_sha:
        print("PREVIEW ONLY: 未提供 requal-sha")

    # accepted by legacy ids
    acc_by_task = {}
    for rid, lsid in mapping.items():
        tt = by_sid[lsid]["task_type"]
        acc_by_task[tt] = acc_by_task.get(tt, 0) + 1

    def sha_ids(ids):
        return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()
    rework_sha = sha_ids(list(mapping.keys()))
    legacy_sha = sha_ids(list(mapping.values()))
    mapping_sha = hashlib.sha256(json.dumps(mapping, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

    out = []
    for tt, target in TARGET.items():
        acc = acc_by_task.get(tt, 0)
        if tt in RUNTIME:
            acc_eff, new_need, mult = 0, target, 1.0
        else:
            acc_eff = acc
            new_need = max(target - acc, 0)
            mult = 1.3
        cand = math.ceil(new_need * mult)
        out.append({"task": tt, "target": target, "accepted_legacy": acc_eff, "new_needed": new_need, "candidate_needed": cand})
    tot_gold = sum(TARGET.values()); tot_new = sum(o["new_needed"] for o in out); tot_cand = sum(o["candidate_needed"] for o in out)
    total_accepted = sum(o["accepted_legacy"] for o in out)
    if total_accepted != len(mapping):
        print("FAIL: accepted!=mapping count"); sys.exit(2)
    print("TOTAL target=%d accepted_eff=%d new=%d cand=%d" % (tot_gold, total_accepted, tot_new, tot_cand))
    print("rework_sha:", rework_sha[:16], "legacy_sha:", legacy_sha[:16], "mapping_sha:", mapping_sha[:16])

    if args.requal_sha:
        doc = {"schema": "quota_plan_v4.1_summary", "version": "v4.1", "generated_by": "DGXD01(Data-B)",
               "generated_at": "2026-09-06T16:45:00+08:00", "script": "d1_closeout_p04_recompute.py (v4)",
               "authority_pr": "40", "authority_review_id": "5124685158",
               "authority_head": "20b575e7fd9ca0b195a214ac3487e79d613a00ca",
               "completion_authority_head": "20b575e7fd9ca0b195a214ac3487e79d613a00ca",
               "a_source_commit": args.a_commit,
               "requal_source": "reports/legacy_semantic_requal_A.jsonl", "requal_sha256": requal_sha,
               "completed_rework_ids": sorted(mapping.keys()),
               "legacy_sample_ids": sorted(mapping.values()),
               "mapping": mapping,
               "rework_set_sha256": rework_sha, "legacy_set_sha256": legacy_sha, "mapping_sha256": mapping_sha,
               "accepted_legacy_effective": total_accepted, "accepted_by_task": acc_by_task,
               "tasks": out,
               "totals": {"gold_target": tot_gold, "new_needed": tot_new, "candidate_needed": tot_cand,
                          "kb": {"target": 400, "candidate_pool": 520}, "runtime_sessions": 35, "scripts": 45,
                          "fresh_calibration": 40},
               "g4_status": "BLOCKED",
               "note": "accepted 仅 Data-R #40 签署 10 req_*（经 #44 mapping 到 legacy pref_*/forg_*）；P04 merge ≠ Gold ≠ Admission；Data-R 冻结"}
        json.dump(doc, open(args.out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(args.out_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["task", "target", "accepted_legacy", "new_needed", "candidate_needed"])
            for o in out:
                w.writerow([o["task"], o["target"], o["accepted_legacy"], o["new_needed"], o["candidate_needed"]])
            w.writerow(["TOTAL", tot_gold, total_accepted, tot_new, tot_cand])
        print("written", args.out_csv, "and", args.out_json)


if __name__ == "__main__":
    main()
