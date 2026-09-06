#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Candidate-Prep 专项校验 v3（Data-A，2026-09-05）
覆盖 Data-R review P1-7 + R3 要求：
- parse（candidate json/jsonl + evidence model.json）
- candidate_only / 无 human_decision·final_label / 无 Gold 身份
- blind-visible 泄漏字段扫描
- KMA enum（conflict_type/forget_mode 仅合法枚举；负例用 scenario_class）
- source/license 与 Registry 真实对账（source_registry.csv / license_registry.csv）fail-closed
- NON_PRODUCTION ID binding
- scenario planned_total 一致
- 跨文档 scope 一致性（scenario / exemplar / scope guideline）
fail-closed：任一 FAIL 返回退出码 1。
"""
import csv
import json
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CAND = os.path.join(ROOT, "data", "interim", "candidates_v4")
EVIDENCE = os.path.join(ROOT, "evidence", "ai_outputs", "20260905_P20_prep_A")
SRC_CSV = os.path.join(ROOT, "registry", "source_registry.csv")
LIC_CSV = os.path.join(ROOT, "registry", "license_registry.csv")

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


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return {r["dataset_id"]: r for r in csv.DictReader(f)}


# ---- 1. parse ----
json_files = sorted(glob.glob(os.path.join(CAND, "**", "*.json"), recursive=True) + [os.path.join(EVIDENCE, "model.json")])
jsonl_files = sorted(glob.glob(os.path.join(CAND, "**", "*.jsonl"), recursive=True))
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

# ---- 2. candidate_only ----
check(len(exemplars) == 9, "exemplar_count", "expected 9, got %d" % len(exemplars))
for ex in exemplars:
    check(ex.get("review_status") == "candidate_only", ex["sample_id"], "review_status != candidate_only")
    check(ex.get("dataset_stage") == "candidate_only", ex["sample_id"], "dataset_stage != candidate_only")
    check(ex.get("admission_status") == "NOT_ADMISSION_APPROVED", ex["sample_id"], "admission_status != NOT_ADMISSION_APPROVED")
    check("gold" not in ex or ex["gold"] == {}, ex["sample_id"], "contains gold")
    check(ex.get("dataset_version") != "kylin_memory_gold_v4.1", ex["sample_id"], "uses Gold dataset_version")
    check("human_decision" not in ex, ex["sample_id"], "contains human_decision")
    check("final_label" not in ex, ex["sample_id"], "contains final_label")

# ---- 3. blind-visible leakage ----
for ex in exemplars:
    bv = json.dumps(ex.get("blind_visible", {}), ensure_ascii=False)
    for token in FORBIDDEN_IN_BLIND:
        check(token not in bv, ex["sample_id"], "blind_visible leaks field/token: %s" % token)
    check("design_metadata" in ex, ex["sample_id"], "missing design_metadata layer")

# ---- 4. KMA enum ----
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

# ---- 5. source/license 与 Registry 真实对账 ----
src_reg = read_csv(SRC_CSV)
lic_reg = read_csv(LIC_CSV)
fc = json.load(open(os.path.join(CAND, "factory_config.json"), encoding="utf-8"))
pub_sources = fc.get("source_layer_map", {}).get("public_direct", {}).get("candidates", [])
check(len(pub_sources) == 4, "public_sources_count", "expected 4, got %d" % len(pub_sources))
for src in pub_sources:
    ds = src["dataset"]
    check(ds in src_reg, ds, "dataset not in source_registry.csv")
    check(ds in lic_reg, ds, "dataset not in license_registry.csv")
    if ds not in src_reg or ds not in lic_reg:
        continue
    sr, lr = src_reg[ds], lic_reg[ds]
    expect_src = "SOURCE_VERIFIED" if sr["status"] == "已核验" else "SOURCE_PENDING_REVIEW"
    check(src.get("source_registry_status") == expect_src, ds,
          "source_registry_status mismatch: got %s want %s (registry status=%s)" % (src.get("source_registry_status"), expect_src, sr["status"]))
    if "待" in str(lr.get("verdict", "")):
        expect_lic = "LICENSE_PENDING"
    elif "待批准" in lr["reviewer"]:
        expect_lic = "REVIEWER_PENDING"
    else:
        expect_lic = "LICENSE_PENDING"
    check(src.get("license_status") == expect_lic, ds,
          "license_status mismatch: got %s want %s (reviewer=%s)" % (src.get("license_status"), expect_lic, lr["reviewer"]))
    approved = "批准" in lr["reviewer"] and not lr["reviewer"].startswith("Reviewer（待")
    check(src.get("admission_eligible") is (False if not approved else True), ds,
          "admission_eligible mismatch: registry approved=%s" % approved)

# ---- 6. NON_PRODUCTION ID ----
for ex in exemplars:
    check(ex.get("id_binding_status") == "NON_PRODUCTION", ex["sample_id"], "id_binding_status != NON_PRODUCTION")
    check("user_id" not in ex, ex["sample_id"], "uses canonical user_id (must be scenario_user_ref)")

# ---- 7. planned_total ----
for sf in glob.glob(os.path.join(CAND, "scenario_specs", "*.json")):
    spec = json.load(open(sf, encoding="utf-8"))
    total = spec.get("planned_total")
    s = sum(sc.get("planned_candidates", 0) for sc in spec.get("scenarios", []))
    check(total == s, os.path.basename(sf), "planned_total %s != sum %s" % (total, s))

# ---- 8. 跨文档 scope 一致性 ----
pref_spec = json.load(open(os.path.join(CAND, "scenario_specs", "preference_scenarios.json"), encoding="utf-8"))
ospref01 = next((s for s in pref_spec["scenarios"] if s["scenario_id"] == "OSPREF-01"), None)
check(ospref01 is not None, "OSPREF-01", "scenario missing")
if ospref01:
    check("preference_scope_target" not in ospref01, "OSPREF-01",
          "must not carry fixed preference_scope_target (per_sample_semantic_review)")
    check(ospref01.get("scope_policy") == "per_sample_semantic_review", "OSPREF-01",
          "must set scope_policy=per_sample_semantic_review")
pref_ex = [e for e in exemplars if e["task_type"] == "preference_extraction"]
pref_ex01 = next((e for e in pref_ex if e["sample_id"] == "pref_v41_ex01"), None)
check(pref_ex01 is not None, "pref_v41_ex01", "exemplar missing")
if pref_ex01:
    dm = pref_ex01.get("design_metadata", {})
    check(dm.get("design_scope_target") == "topic", "pref_v41_ex01",
          "design_scope_target must be topic per scope guideline ('以后每周报告都用要点'→topic), got %s" % dm.get("design_scope_target"))

if failures:
    print("\nRESULT: FAIL (%d issues)" % len(failures))
    sys.exit(1)
print("\nRESULT: ALL PASS (json=%d jsonl=%d exemplars=%d, files=%d)" % (len(json_files), len(jsonl_files), len(exemplars), len(json_files) + len(jsonl_files)))
sys.exit(0)