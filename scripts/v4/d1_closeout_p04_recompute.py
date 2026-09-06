#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B2：P04 动态配额重算 v2（Data-B，2026-09-06）

规则（v4.1 SOP §7/Q7 + 台账 04）：
  accepted_legacy_task = REUSE/REWORK/RELABEL 且 requalification_status=完成（且非 Runtime 静态）
  new_needed = max(target - accepted_legacy, 0)；candidate = ceil(new_needed * 1.3)（Runtime ×1.0 不可抵）

fail-closed（Data-R #45 comment）：
  - unknown / duplicate / 不在 frozen requal 集 / proposed_decision∉{REUSE,REWORK,RELABEL}
    / Tool-E2E(Runtime) id / signed count 与实际 accepted 不一致 → exit nonzero
  - requal source 须锁 ref/hash（--requal-sha；不提供 sha 则只允许 preview 模式，不出正式 P04）
输出：accepted_by_task + completed_sample_ids_sha256 + new_needed/candidate；JSON+CSV

正式模式：--requal <frozen requal> --requal-sha <sha256> --completed <signed> --authority <Data-R review ref> --out <prefix>
"""
import argparse
import csv
import hashlib
import json
import math
import sys

TARGET = {"preference_extraction": 225, "knowledge_retrieval": 175, "conflict_resolution": 125,
          "precise_forgetting": 100, "tool_result": 125, "end_to_end_session": 35}
RUNTIME = {"tool_result", "end_to_end_session"}
ACCEPT = {"REUSE", "REWORK", "RELABEL"}


def load_completed(p):
    if p.endswith(".json"):
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict):
            return d.get("completed_sample_ids", [])
        return list(d)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requal", required=True)
    ap.add_argument("--requal-sha", default="", help="frozen requal 文件 sha256（正式 P04 必须；缺省仅 preview）")
    ap.add_argument("--completed", required=True)
    ap.add_argument("--authority", default="Data-R #40 Review 5124685158 (20b575e)")
    ap.add_argument("--out-prefix", default="")
    args = ap.parse_args()

    requal_raw = open(args.requal, "rb").read()
    requal_sha = hashlib.sha256(requal_raw).hexdigest()
    if args.requal_sha and args.requal_sha != requal_sha:
        print("FAIL: requal sha mismatch given=%s actual=%s" % (args.requal_sha[:12], requal_sha[:12]))
        sys.exit(2)
    rows = [json.loads(l) for l in requal_raw.decode("utf-8").splitlines() if l.strip()]
    by_sid = {r.get("sample_id"): r for r in rows}
    completed = load_completed(args.completed)
    # fail-closed checks
    issues = []
    seen = set()
    for sid in completed:
        if sid in seen:
            issues.append("duplicate_completed:" + sid)
        seen.add(sid)
        r = by_sid.get(sid)
        if r is None:
            issues.append("unknown_or_not_in_requal:" + sid)
            continue
        if r.get("proposed_decision") not in ACCEPT:
            issues.append("decision_not_accepted:" + sid + ":" + str(r.get("proposed_decision")))
        if r.get("task_type") in RUNTIME:
            issues.append("runtime_static_in_accepted:" + sid)
    if issues:
        print("FAIL_CLOSED:")
        for i in issues:
            print("  ", i)
        sys.exit(2)
    if not args.requal_sha:
        print("PREVIEW ONLY: 未提供 requal-sha，不生成正式 P04（Data-R #45 要求）")

    acc_by_task = {}
    for sid in completed:
        tt = by_sid[sid]["task_type"]
        acc_by_task[tt] = acc_by_task.get(tt, 0) + 1
    signed_sha = hashlib.sha256("\n".join(sorted(completed)).encode("utf-8")).hexdigest()
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
        out.append({"task": tt, "target": target, "accepted_legacy": acc_eff,
                    "new_needed": new_need, "candidate_needed": cand})
        print("%-28s target=%4d accepted=%3d new=%4d cand=%4d" % (tt, target, acc_eff, new_need, cand))
    tot_gold = sum(TARGET.values()); tot_new = sum(o["new_needed"] for o in out); tot_cand = sum(o["candidate_needed"] for o in out)
    total_accepted = sum(o["accepted_legacy"] for o in out)
    if total_accepted != len(completed):
        print("FAIL: signed count=%d != effective accepted=%d" % (len(completed), total_accepted))
        sys.exit(2)
    print("TOTAL Gold target=%d accepted_eff=%d new_needed=%d candidate=%d" % (tot_gold, total_accepted, tot_new, tot_cand))
    print("completed_sample_ids_sha256:", signed_sha)
    print("(独立对象：KB 400 -> 候选520；Runtime sessions 35；scripts 45；fresh40 从 Admission PASS)")
    if args.out_prefix and args.requal_sha:
        doc = {"schema": "p04_formal_v4.1", "date": "2026-09-06", "generated_by": "DGXD01(Data-B)",
               "authority": args.authority, "requal_sha256": requal_sha,
               "completed_count": len(completed), "completed_sample_ids_sha256": signed_sha,
               "accepted_legacy_effective": total_accepted,
               "tasks": out,
               "totals": {"gold_target": tot_gold, "new_needed": tot_new, "candidate_needed": tot_cand,
                          "kb": {"target": 400, "candidate_pool": 520}, "runtime_sessions": 35, "scripts": 45},
               "g4_status": "BLOCKED", "accepted_note": "仅 Data-R #40 签署 10 条；#45 merge ≠ Legacy 完成重准入 ≠ Gold"}
        json.dump(doc, open(args.out_prefix + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(args.out_prefix + ".csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["task", "target", "accepted_legacy", "new_needed", "candidate_needed"])
            for o in out:
                w.writerow([o["task"], o["target"], o["accepted_legacy"], o["new_needed"], o["candidate_needed"]])
            w.writerow(["TOTAL", tot_gold, total_accepted, tot_new, tot_cand])
        print("written", args.out_prefix + ".json/.csv")


if __name__ == "__main__":
    main()
