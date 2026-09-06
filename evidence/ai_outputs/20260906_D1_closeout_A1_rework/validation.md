# Data-A A1 自检与 canonical 验证结果 — 2026-09-06（A-followup #44，Option2）

- 运行：repo 内（scripts/v4/…），Python 3.11。

## 1) repo-relative validator
`python scripts/v4/validate_legacy_rework_A1.py` → ALL PASS
- 10 行 unique（pref6/forg4）；candidate_only/NON_PRODUCTION/NOT_ADMISSION_APPROVED；
- DEV_REG_ONLY 仅 req_pref_000003/000004；template_family == legacy_ref.v1_family；
- blind/answer forbidden-field leakage 0（canonical leak registry 由 leakage_scan 单独管）；
- timestamp ISO / forget enum / target∩must_keep=∅ / scenario+prompt 命中。

## 2) canonical gates
```
provenance_resolver.py   checked=10 unresolved=0   exit0
dedup_scan.py            dedup_status=PASS (exact=0 near=0 template 每族10%) exit0
leakage_scan.py          leak=2  → req_pref_000003/000004（Option2 LEAK_EXPOSED/BLOCKED）exit2(如实)
validate_legacy_rework_leak_expect.py → PASS（hits ⊆ manifest.exposed_lineage_blocked，无意外泄漏）
```
- Option2 说明：两候选按 lineage 继承 template_family（temp_instruction_v1/update_revoke_v1）命中 leak registry 的 template 指纹；改写盲文不影响 template 指纹；如实登记 exposed_lineage_blocked，不计 completion/accepted。不再用 REGISTERED_EXPOSURE_ALLOWED/waiver 口径。

## 3) builder 确定性 + pinned exact-input
```
python scripts/v4/build_legacy_rework_A1.py --check
pref f2048f90… == disk == manifest；forg 30b5edc1… == disk == manifest
input_hash 352a6926… == manifest；repair_plan(raw-bytes) 79e9b8da… == manifest  → MATCH
```
pinned gold/requal = master c21ee694ef…；checkout!=pinned fail-closed；canonical 序列化；source_file repo-relative。

## 4) CI（baseline-validation.yml，hashFiles 条件）
A1 validator / canonical T03 / canonical dedup / canonical leakage+expect / builder --check。
