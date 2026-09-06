# D1 A 候选批自检结果（2026-09-06）

- 脚本：`evidence/ai_outputs/20260906_D1_candidate_factory_A/validate_batch.py`
- 执行：2026-09-06，Python 3.11
- 结果：**ALL PASS**（parse OK，3 文件 / 218 行）

## 覆盖检查项
1. jsonl parse：preference 98 / conflict 64 / forgetting 56 = **218**，均 == 对应 scenario_spec planned_total 分项 ✅
2. 身份字段：review_status/dataset_stage=candidate_only、admission_status=NOT_ADMISSION_APPROVED、id_binding_status=NON_PRODUCTION、dataset_version=kylin_memory_candidate_v4.1 ✅
3. 无 human_decision / final_label / gold ✅
4. blind-visible 泄漏扫描（expected/design/target_ids/must_keep/hard_negative/negative/resolution/scope_target/peer/reviewer/gold/winner/conflict_type/forget_mode/scenario_class/candidate_event_refs/generation）0 命中 ✅
5. KMA enum：design_conflict_type ∈ 合法集；forget_mode ∈ {single_item,session,topic,time_window,full_reset}；负例用 scenario_class 且不带 selector/type 字段 ✅
6. target_ids ∩ must_keep = ∅（Forgetting 全批）✅
7. exact duplicate（blind_visible 全序规范化）= 0 ✅
8. 字符 bigram Jaccard > 0.85 送审对 = 0（跨 218 条两两比对）✅
9. 每 scenario 数量 == planned_candidates ✅

## 备注（供 B/Data-R 复核）
- OSPREF-05（implicit_repeated_behavior）10 条输入为事件日志式行为证据，隐含偏好低置信 → G2 需 NEEDS_REVIEW。
- OSCONF-04（scope_ambiguity）8 条均判定 non_conflict_hard_negative（不同 scope 可共存），附 design_reason。
- OSCONF-06 10 条亦为 non_conflict_hard_negative；OSCONF-07 8 条 version 语义标 temporal_inconsistency。
- design_scope_target 为 A 侧设计提案，正式 scope 走 G2 逐条人工复核。
- 候选文件不落入 `data/interim/candidates_v4/`（#34 输入包 validator exemplar_count=9 不受影响）。
- 本批不含 public_derived/改写变体；剩余缺口 BLOCKED（Registry license 未批准 + P04 未冻结）。
