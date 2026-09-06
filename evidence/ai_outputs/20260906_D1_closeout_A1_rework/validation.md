# Data-A A1 自检与 canonical 验证 — 2026-09-06（A-followup #44，双轨 template family 终版）

## 1) validator
`python scripts/v4/validate_legacy_rework_A1.py` → ALL PASS
- 10 行 unique（pref6/forg4）；candidate_only/NON_PRODUCTION/NOT_ADMISSION_APPROVED；
- DEV_REG_ONLY 仅 req_pref_000003/000004；
- 双轨 template_family：非 rewrite == legacy lineage；rewrite == repair_plan.current_template_family（legacy_exposure_rewrite_v1）且 legacy_ref.v1_family 保留原值；
- blind/answer forbidden-field leakage 0；timestamp ISO / forget enum / target∩must_keep=∅ / scenario+prompt 命中。

## 2) canonical gates
```
provenance_resolver.py  checked=10 unresolved=0  exit0
dedup_scan.py           dedup_status=PASS (exact=0 near=0 template 浓度20%<=25%) exit0
leakage_scan.py         checked=10 leak=0        exit0
```
- 历史 lineage template 指纹（temp_instruction_v1/update_revoke_v1）仅登记 manifest.historical_exposure 审计；不删除 leak registry。

## 3) builder 确定性 + pinned exact-input
```
python scripts/v4/build_legacy_rework_A1.py --check
pref 22e70836… == disk == manifest；forg 30b5edc1… == disk == manifest
input_hash 3c6c2816… == manifest；repair_plan(raw) 6a65a264… == manifest  → MATCH
```
pinned gold/requal = master c21ee694ef…；checkout!=pinned fail-closed；canonical 序列化；source_file repo-relative。

## 4) CI（baseline-validation.yml，hashFiles 条件）
A1 validator / canonical T03 / canonical dedup / **canonical leakage（无 `|| true`，须 leak=0 exit0）** / builder --check。
