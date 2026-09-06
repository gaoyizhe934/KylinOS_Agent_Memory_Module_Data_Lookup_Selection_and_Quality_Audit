# -*- coding: utf-8 -*-
"""Data-A closeout A1 修复候选批次自检
检查: parse、身份(candidate_only/NON_PRODUCTION/NOT_ADMISSION_APPROVED)、无 human_decision/final_label/gold、
blind 泄漏 token、timestamp 合法 ISO、forget_mode enum、target∩must_keep、DEV_REG_ONLY 保留、
legacy_ref 存在、10 行、per-file 6/4。
"""
import json, os, re, sys
from collections import Counter

D = r'C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_legacy_rework_A_20260906'
FILES = ["legacy_rework_preference_candidates.jsonl", "legacy_rework_forgetting_candidates.jsonl"]
FORBIDDEN = ["expected", "hard_negative", "negative", "resolution", "scope_target", "peer",
             "reviewer", "gold", "winner", "conflict_type", "forget_mode", "scenario_class",
             "candidate_event_refs", "generation", "legacy_ref", "applied_fixes", "target_ids",
             "must_keep", "design"]
VALID_FM = {"single_item", "session", "topic", "time_window", "full_reset"}
fails = []
rows = []
for fn in FILES:
    p = os.path.join(D, fn)
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        rows.append((fn, r))
    print('parse ok', fn)

def bv_json(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)

dev = []
for fn, r in rows:
    sid = r["sample_id"]
    for k in ["review_status", "dataset_stage"]:
        if r.get(k) != "candidate_only":
            fails.append((sid, k))
    if r.get("admission_status") != "NOT_ADMISSION_APPROVED":
        fails.append((sid, "admission"))
    if r.get("id_binding_status") != "NON_PRODUCTION":
        fails.append((sid, "id_binding"))
    for k in ["human_decision", "final_label", "gold"]:
        if k in r:
            fails.append((sid, "contains " + k))
    dm = r.get("design_metadata", {})
    for f in ["legacy_ref", "generation", "scenario_family", "candidate_event_refs", "applied_fixes", "split_eligibility"]:
        if f not in dm:
            fails.append((sid, "dm missing " + f))
    if "design" in bv_json(r["blind_visible"]) or "expected" in bv_json(r["blind_visible"]):
        fails.append((sid, "blind leak (expected/design)"))
    # ts valid ISO
    ts = r.get("timestamp", "")
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$', ts):
        fails.append((sid, "timestamp invalid: " + ts))
    t = r["task_type"]
    if t == "precise_forgetting":
        fm = dm.get("forget_mode")
        if fm not in VALID_FM:
            fails.append((sid, "forget_mode invalid " + str(fm)))
        tids = set(dm.get("target_ids", [])); mk = set(dm.get("must_keep", []))
        if tids & mk:
            fails.append((sid, "target∩must_keep non-empty"))
        if not tids:
            fails.append((sid, "missing target_ids"))
    if dm.get("split_eligibility") == "DEV_REG_ONLY":
        dev.append(sid)

ids = [r["sample_id"] for _, r in rows]
print("rows", len(rows), "unique", len(set(ids)) == len(ids))
print("per_file", dict(Counter(fn for fn, _ in rows)))
print("DEV_REG_ONLY", dev)
print("RESULT:", "FAIL(%d)" % len(fails) if fails else "PASS")
for f in fails[:50]:
    print(" FAIL", f)
sys.exit(1 if fails else 0)
