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

## 3) builder 确定性复现 + pinned exact-input 证明
```
python scripts/v4/build_legacy_rework_A1.py --check
pref  regenerated=9ad487ce…02e == disk == manifest_sha（match）
forg regenerated=30b5edc1…7e1 == disk == manifest_sha（match）
input_hash recomputed=ec1580c3… == manifest   → RESULT: MATCH
```
读取冻结输入（pinned commit c21ee694ef4164fe232a59096caa8c908967fa17，#37 merge master）：
`git show <commit>:<gold_file>` 逐条 10 原始行 + `git show <commit>:reports/legacy_semantic_requal_A.jsonl`（Rev3 fix_fields）；
当前 checkout 与 pinned blob newline-normalized 比对不一致 → fail-closed。
manifest：input_commit/fix_source_commit/source_files_sha256/selected_rows_sha256(ebf5c8e4…)/requal_blob_sha256(c5b217e3…)/**repair_plan_sha256=78fe38c1…（pinned raw bytes，与 B1 contract 一致）**/input_hash/output_sha256；source_file repo-relative。

## 4) canonical dedup / leak（Rev3，A-followup）
- 10 候选补 top-level `template_family`=legacy v1 family（output_style_length_v1 等，每族 10%）。
- dedup_scan → **dedup_status=PASS**（exact=0、near=0、template_concentration_ok=true）——修复此前 100% none BLOCKED。
- leakage_scan → leak=2 = req_pref_000004/000003（DEV_REG_ONLY sealed 暴露候选，命中 leaked-content registry）——**预期且策略允许**（仅 DEV_REG_ONLY，禁再 seal）；B1 leak-gate 应按 REGISTERED_EXPOSURE_ALLOWED 处置（Data-R/B 定）。

## CI（已并入 baseline-validation.yml）
- validate_legacy_rework_A1.py（条件 hashFiles）
- provenance_resolver.py → reports/prov_report_A1_ci.json（10/10）
- build_legacy_rework_A1.py --check
