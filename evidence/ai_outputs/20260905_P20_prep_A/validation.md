# Candidate-Prep 专项校验结果 v4（post-#32 master rebase）

- 脚本：`scripts/v4/validate_candidate_prep.py`
- **rebased HEAD**：`81b7faf3a5fa37e048f542d2bc9920d7ede44ec0`（base = post-#32 master，含 v4.1 规则基线）
- 执行：2026-09-05，Python 3.11
- 结果：**ALL PASS**（json=5 jsonl=3 exemplars=9，files=8），exit 0

## 覆盖检查项
1. parse：candidate json×4 + evidence model.json×1 = json=5；exemplars jsonl×3 ✅
2. 9 exemplars 全部 candidate_only / dataset_stage=candidate_only / NOT_ADMISSION_APPROVED ✅
3. 无 human_decision / final_label / Gold dataset_version ✅
4. blind-visible 泄漏字段扫描（expected/design/target_ids/must_keep/hard_negative/scope_target/winner/reviewer/gold 等）✅
5. KMA enum（conflict_type/forget_mode 仅合法枚举；负例用 scenario_class）✅
6. **source/license 与 Registry 真实对账**（`registry/source_registry.csv` + `registry/license_registry.csv` join，dataset 缺失/不一致→FAIL；license 按 verdict 判定 LICENSE_PENDING 或 REVIEWER_PENDING；未批准→admission_eligible 必须 false）✅
7. NON_PRODUCTION ID binding（id_binding_status / scenario_user_ref）✅
8. scenario planned_total == 明细求和一致 ✅
9. **跨文档 scope 一致性**：OSPREF-01 无固定 preference_scope_target（scope_policy=per_sample_semantic_review）；pref_v41_ex01.design_scope_target=topic（与 scope guideline「以后每周报告都用要点→topic」一致）✅

## 备注
- **base 已改绑 post-#32 master**（#32 已 merge，master 5f90409）；v4.1 规则基线在 master。
- 当前 public source 全部 admission_eligible=false（Registry license 均 Reviewer（待批准）/待核验）。
- CI/Baseline Validation 在本 HEAD（52fce60+）推送后触发。