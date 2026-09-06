#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 D1 Closeout B2：P04 动态配额重算（Data-B，2026-09-06）

规则（v4.1 SOP §7/Q7 + 台账 04）：
  accepted_legacy_task = REUSE/REWORK/RELABEL 且 requalification_status=完成（且非 Runtime 静态）
  new_needed  = max(target - accepted_legacy, 0)
  candidate   = ceil(new_needed * 1.3)  # Runtime(Tool/E2E) 用 1.0 且 legacy 不可抵扣
输入：
  --requal   A P10 requal jsonl（含 sample_id/task_type/proposed_decision）
  --completed  Data-R 已签 requalification_status=完成的 sample_id 清单（JSON list 或每行一个 id 的 txt/jsonl）
输出：每任务 accepted/new_needed/candidate + 合计（不产 Gold、不代 Data-R 签）
"""
import argparse
import json
import math
import sys

TARGET = {
    "preference_extraction": 225,
    "knowledge_retrieval": 175,
    "conflict_resolution": 125,
    "precise_forgetting": 100,
    "tool_result": 125,
    "end_to_end_session": 35,
}
RUNTIME = {"tool_result", "end_to_end_session"}
ACCEPT = {"REUSE", "REWORK", "RELABEL"}


def load_completed(p):
    if p.endswith(".json"):
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, dict):
            return list(d.get("completed_sample_ids", []))
        return list(d)
    return [l.strip() for l in open(p, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--requal", required=True)
    ap.add_argument("--completed", default="", help="Data-R 签完成的 sample_id 清单（缺省=无，effective=0）")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.requal, encoding="utf-8") if l.strip()]
    completed = set(load_completed(args.completed)) if args.completed else set()
    print("requal rows:", len(rows), "| completed signed:", len(completed))

    acc_by_task = {}
    for r in rows:
        sid = r.get("sample_id")
        tt = r.get("task_type")
        if sid in completed and r.get("proposed_decision") in ACCEPT and tt not in RUNTIME:
            acc_by_task[tt] = acc_by_task.get(tt, 0) + 1
    # also count accepted even if not completed? NO: only completed counts (effective)
    out = []
    for tt, target in TARGET.items():
        acc = acc_by_task.get(tt, 0)
        if tt in RUNTIME:
            new_need, mult, acc_eff = target, 1.0, 0
        else:
            new_need = max(target - acc, 0)
            mult = 1.3
            acc_eff = acc
        cand = math.ceil(new_need * mult)
        out.append({"task": tt, "target": target, "accepted_legacy_effective": acc_eff,
                    "new_needed": new_need, "candidate_needed": cand})
        print("%-28s target=%4d accepted_eff=%3d new=%4d cand=%4d" % (tt, target, acc_eff, new_need, cand))
    tot_gold = sum(TARGET.values()); tot_new = sum(o["new_needed"] for o in out); tot_cand = sum(o["candidate_needed"] for o in out)
    print("TOTAL Gold target=%d new_needed=%d candidate=%d" % (tot_gold, tot_new, tot_cand))
    print("(KB 400 -> 520 x1.3; Runtime sessions 35/45; fresh40 从 Admission PASS)")
    if args.out:
        json.dump({"schema": "p04_recompute_v4.1", "completed_signed": len(completed),
                   "tasks": out, "totals": {"gold": tot_gold, "new_needed": tot_new, "candidate": tot_cand}},
                  open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
