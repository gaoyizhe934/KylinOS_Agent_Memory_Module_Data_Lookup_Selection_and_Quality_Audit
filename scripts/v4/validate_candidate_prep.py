#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Candidate-Prep 专项校验（Data-A，2026-09-05）
覆盖 Data-R review P1-7 要求：parse / candidate_only / 无 human_decision·final_label /
blind-visible 泄漏扫描 / KMA enum / source·license eligibility / NON_PRODUCTION ID / planned_total 一致。
fail-closed：任一 FAIL 返回退出码 1。
"""
import json
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAND = os.path.join(ROOT, "data", "interim", "candidates_v4")
REPORTS = os.path.join(ROOT, "reports")

VALID_CONFLICT_TYPE = {"contradiction", "temporal_inconsistency", "source_conflict", "preference_conflict", "scope_ambiguity"}
VALID_FORGET_MODE = {"single_item", "session", "topic", "time_window", "full_reset"}
FORBIDDEN_IN_BLIND = ["expected", "design", "target_ids", "must_keep", "hard_negative", "negative", "resolution",
                      "scope_target", "peer", "reviewer", "gold", "winner", "conflict_type", "forget_mode", "scenario_class"]

failures = []


def fail(item, reason):
    failures.append((item, reason))
    print("FAIL | %s | %s" % (item, reason))


def check(cond, item, reason):
    if not cond:
        fail(item, reason)


# 1. JSON/JSONL parse
json_files = glob.glob(os.path.join(CAND, "**", "*.json"), recursive=True)
jsonl_files = glob.glob(os.path.join(CAND, "**", "*.jsonl"), recursive=True)
for f in json_files:
    try:
        json.load(open(f, encoding="utf-8"))
    except Exception as e:
        fail(os.path.relpath(f, ROOT), "JSON parse: %s" % e)
exemplars = []
for f in jsonl_files:
    try:
        rows = [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]
        exemplars.extend(rows)
    except Exception as e:
        fail(os.path.relpath(f, ROOT), "JSONL parse: %s" % e)

# 2. exemplars candidate_only
check(len(exemplars) == 9, "exemplar_count", "expected 9, got %d" % len(exemplars))
for ex in exemplars:
    check(ex.get("review_status") == "candidate_only", ex["sample_id"], "review_status != candidate_only")
    check(ex.get("dataset_stage") == "candidate_only", ex["sample_id"], "dataset_stage != candidate_only")
    check(ex.get("admission_status") == "NOT_ADMISSION_APPROVED", ex["sample_id"], "admission_status != NOT_ADMISSION_APPROVED")
    check("gold" not in ex or ex["gold"] == {}, ex["sample_id"], "contains gold")
    check("dataset_version" not in ex or ex.get("dataset_version") != "kylin_memory_gold_v4.1",
          ex["sample_id"], "uses Gold dataset_version")

# 3. no human_decision / final_label
for ex in exemplars:
    check("human_decision" not in ex, ex["sample_id"], "contains human_decision")
    check("final_label" not in ex, ex["sample_id"], "contains final_label")

# 4. blind-visible leakage scan
for ex in exemplars:
    bv = json.dumps(ex.get("blind_visible", {}), ensure_ascii=False)
    for token in FORBIDDEN_IN_BLIND:
        check(token not in bv, ex["sample_id"], "blind_visible leaks field/token: %s" % token)
    check("design_metadata" in ex, ex["sample_id"], "missing design_metadata layer")

# 5. KMA enum check in scenario_specs
for sf in glob.glob(os.path.join(CAND, "scenario_specs", "*.json")):
    spec = json.load(open(sf, encoding="utf-8"))
    for sc in spec.get("scenarios", []):
        sid = sc["scenario_id"]
        ct = sc.get("conflict_type")
        fm = sc.get("forget_mode")
        if ct is not None:
            check(ct in VALID_CONFLICT_TYPE, sid, "illegal conflict_type: %s" % ct)
        if fm is not None:
            check(fm in VALID_FORGET_MODE, sid, "illegal forget_mode: %s" % fm)

# 6. source/license eligibility (no vague "registered")
fc = json.load(open(os.path.join(CAND, "factory_config.json"), encoding="utf-8"))
for src in fc.get("source_layer_map", {}).get("public_direct", {}).get("candidates", []):
    check("license" not in src or src.get("license") != "registered", src["dataset"], "uses vague license=registered")
    check("source_registry_status" in src and "license_status" in src and "admission_eligible" in src,
          src["dataset"], "missing eligibility fields")
    if src.get("dataset") == "personachat_2018":
        check(src.get("admission_eligible") is False, src["dataset"], "personachat must be admission_eligible=false")

# 7. NON_PRODUCTION ID binding
for ex in exemplars:
    check(ex.get("id_binding_status") == "NON_PRODUCTION", ex["sample_id"], "id_binding_status != NON_PRODUCTION")
    check("user_id" not in ex, ex["sample_id"], "uses canonical user_id (must be scenario_user_ref)")

# 8. scenario planned_total == sum(planned_candidates)
for sf in glob.glob(os.path.join(CAND, "scenario_specs", "*.json")):
    spec = json.load(open(sf, encoding="utf-8"))
    total = spec.get("planned_total")
    s = sum(sc.get("planned_candidates", 0) for sc in spec.get("scenarios", []))
    check(total == s, os.path.basename(sf), "planned_total %s != sum %s" % (total, s))

if failures:
    print("\nRESULT: FAIL (%d issues)" % len(failures))
    sys.exit(1)
print("\nRESULT: ALL PASS (json=%d jsonl=%d exemplars=%d)" % (len(json_files), len(jsonl_files), len(exemplars)))
sys.exit(0)