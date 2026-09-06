# Data-A A1 自检与 canonical 验证结果 — 2026-09-06

- 运行环境：repo 内（scripts/v4/…），Python 3.11，无本机路径依赖。

## 1) repo-relative validator
```
python scripts/v4/validate_legacy_rework_A1.py
rows=10 unique=True per_file={'legacy_rework_preference_candidates.jsonl':6,'legacy_rework_forgetting_candidates.jsonl':4}
DEV_REG_ONLY=['req_pref_000004','req_pref_000003']  → RESULT: ALL PASS (exit 0)
```
检查：身份字段、无 human_decision/final_label/gold、blind 泄漏 0、timestamp ISO、forget_mode enum、
target_ids∩must_keep=∅、scenario_spec_id ∈ scenario_specs、prompt_version ∈ active prompt_registry、DEV_REG_ONLY 保留。

## 2) canonical provenance T03（真实文件）
```
python scripts/v4/provenance_resolver.py --input "data/interim/d1_legacy_rework_A_20260906/*.jsonl" --out reports/prov_report_A1.json
checked=10 unresolved=0 → exit 0（G1_provenance_unresolved_zero=true）
```
10/10 os_controlled_authored，source_file 可解析，prompt P10-A1-rework-v4.1 active，scenario_spec_id 全命中。

## 3) builder 确定性复现
```
python scripts/v4/build_legacy_rework_A1.py --check
pref  regenerated=3c108717…aa6 == disk == manifest_sha（match）
forg regenerated=9269da40…f17 == disk == manifest_sha（match）
input_hash recomputed=e01610d1… == manifest   → RESULT: MATCH
```
读取冻结输入：data/gold 原行（按 sample_id 定位）+ reports/legacy_semantic_requal_A.jsonl（Rev3 fix_fields）；
输出记录 input_commit / fix_source_commit / input_hash / output_sha256；source_file 为 repo-relative（跨平台可复现，CI 修正）。

## CI（已并入 baseline-validation.yml）
- validate_legacy_rework_A1.py（条件 hashFiles）
- provenance_resolver.py → reports/prov_report_A1_ci.json（10/10）
- build_legacy_rework_A1.py --check
