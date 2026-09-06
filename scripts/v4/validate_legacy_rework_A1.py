# -*- coding: utf-8 -*-
"""Data-A Closeout A1 修复候选批次自检（repo-relative）
用法：python scripts/v4/validate_legacy_rework_A1.py [--repo ROOT]
校验：10 行(6/4)、unique、身份字段(candidate_only/NON_PRODUCTION/NOT_ADMISSION_APPROVED)、
无 human_decision/final_label/gold、blind 泄漏、timestamp 合法 ISO、forget_mode enum、
target_ids∩must_keep=∅、DEV_REG_ONLY 保留、scenario_spec_id ∈ scenario_specs、prompt_version ∈ active prompt_registry、
legacy_ref 存在。任一 FAIL exit 1。
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
D = os.path.join("data", "interim", "d1_legacy_rework_A_20260906")
FILES = ["legacy_rework_preference_candidates.jsonl", "legacy_rework_forgetting_candidates.jsonl"]
FORBIDDEN = ["expected", "hard_negative", "negative", "resolution", "scope_target", "peer",
             "reviewer", "gold", "winner", "conflict_type", "forget_mode", "scenario_class",
             "candidate_event_refs", "generation", "legacy_ref", "applied_fixes", "target_ids",
             "must_keep", "design", "legacy_ref"]
VALID_FM = {"single_item", "session", "topic", "time_window", "full_reset"}


def load_prompt_active(root):
    p = os.path.join(root, "registry", "prompt_registry.csv")
    active = set()
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("status") or "").strip().lower() == "active":
                active.add((r.get("prompt_ref") or "").strip())
    return active


def load_scenario_ids(root):
    ids = set()
    for sf in glob.glob(os.path.join(root, "data", "interim", "candidates_v4", "scenario_specs", "*.json")):
        spec = json.load(open(sf, encoding="utf-8"))
        for sc in spec.get("scenarios", []):
            if sc.get("scenario_id"):
                ids.add(sc["scenario_id"])
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=ROOT)
    args = ap.parse_args()
    root = os.path.abspath(args.repo)
    prompt_active = load_prompt_active(root)
    scenario_ids = load_scenario_ids(root)
    fails = []
    rows = []
    for fn in FILES:
        p = os.path.join(root, D, fn)
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append((fn, json.loads(line)))

    def bv(o):
        return json.dumps(o, ensure_ascii=False, sort_keys=True)

    dev = []
    for fn, r in rows:
        sid = r["sample_id"]
        for k in ["review_status", "dataset_stage"]:
            if r.get(k) != "candidate_only":
                fails.append((sid, k))
        if r.get("admission_status") != "NOT_ADMISSION_APPROVED":
            fails.append((sid, "admission_status"))
        if r.get("id_binding_status") != "NON_PRODUCTION":
            fails.append((sid, "id_binding"))
        for k in ["human_decision", "final_label", "gold"]:
            if k in r:
                fails.append((sid, "contains " + k))
        dm = r.get("design_metadata", {})
        for f in ["scenario_spec_id", "legacy_ref", "generation", "candidate_event_refs", "applied_fixes", "split_eligibility"]:
            if f not in dm:
                fails.append((sid, "dm missing " + f))
        gen = dm.get("generation", {})
        if gen.get("source") != "os_controlled_authored":
            fails.append((sid, "generation.source != os_controlled_authored"))
        if not gen.get("prompt_version") or gen["prompt_version"] not in prompt_active:
            fails.append((sid, "prompt_version not active: %s" % gen.get("prompt_version")))
        if dm.get("scenario_spec_id") not in scenario_ids:
            fails.append((sid, "scenario_spec_id not in specs: %s" % dm.get("scenario_spec_id")))
        bl = bv(r.get("blind_visible", {}))
        for tok in FORBIDDEN:
            if tok in bl:
                fails.append((sid, "blind leak token: " + tok))
        ts = r.get("timestamp", "")
        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$", ts):
            fails.append((sid, "timestamp invalid: " + ts))
        if r["task_type"] == "precise_forgetting":
            if dm.get("forget_mode") not in VALID_FM:
                fails.append((sid, "forget_mode invalid"))
            tids = set(dm.get("target_ids", []))
            mk = set(dm.get("must_keep", []))
            if tids & mk:
                fails.append((sid, "target_ids ∩ must_keep non-empty"))
            if not tids:
                fails.append((sid, "missing target_ids"))
        if dm.get("split_eligibility") == "DEV_REG_ONLY":
            dev.append(sid)

    ids = [r["sample_id"] for _, r in rows]
    from collections import Counter
    per = dict(Counter(fn for fn, _ in rows))
    print("rows=%d unique=%s per_file=%s DEV_REG_ONLY=%s" % (len(rows), len(ids) == len(set(ids)), per, dev))
    if len(rows) != 10 or per.get(FILES[0]) != 6 or per.get(FILES[1]) != 4:
        fails.append(("count", "expected 6/4 got %s" % per))
    if set(dev) != {"req_pref_000004", "req_pref_000003"}:
        fails.append(("dev_reg", "expected 2 DEV_REG_ONLY, got %s" % dev))
    if fails:
        print("RESULT: FAIL (%d)" % len(fails))
        for f in fails[:60]:
            print(" FAIL", f)
        sys.exit(1)
    print("RESULT: ALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
