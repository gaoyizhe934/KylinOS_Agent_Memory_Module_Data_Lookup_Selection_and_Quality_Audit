# Prompt: D1 P20/P22/P23 候选工厂（Data-A，OS-authored 切片）

## 角色
Data-A（lyf-1213）的 AI 辅助，v4.1 基线，D1 进行中（formal_day1_started 09:59，C1=LEGACY_SET_FROZEN IN_SCOPE=465）。

## 会话目标（只做不依赖冻结的部分）
按三份 scenario_spec 的 planned_candidates 量产 os_controlled_authored 候选：
- Preference（P20）98 条 = preference_scenarios.json（OSPREF-01..10）
- Conflict（P22）64 条 = conflict_scenarios.json（OSCONF-01..07）
- Forgetting（P23）56 条 = forgetting_scenarios.json（OSFORG-01..08）
public_derived / 改写变体 / 按 P04 补齐的缺口一律不做，标 BLOCKED，等 Data-R 冻结/裁决。

## 边界（严格，v4.1 红线）
- 全部 candidate_only + NON_PRODUCTION + NOT_ADMISSION_APPROVED；gold 为空；不写 human_decision / final_label。
- 候选双层结构：blind_visible（无答案/无设计字段）+ design_metadata（scenario_spec_id/family/class/scope 提案/generation）。
- 每条带 generation manifest：generation_id / prompt_version / seed / model / source / scenario_spec_id（G9）。
- M1/M1-KB/M3 未绿 → 不产 production business truth / production knowledge_id。
- 不 mock；不改 data/raw；候选不写入 #34 已合并的 candidates_v4 输入包（其 validator exemplar_count=9 保持有效）。
- 本会话 AI 产物全部落盘 evidence/ai_outputs。

## 结构依据
- exemplar schema：data/interim/candidates_v4/exemplar_candidates/*.jsonl
- KMA enum：conflict_type ∈ {contradiction,temporal_inconsistency,source_conflict,preference_conflict,scope_ambiguity}；forget_mode ∈ {single_item,session,topic,time_window,full_reset}；负例用 scenario_class。
- scope 标准：reports/v4.1_scope_review_standard_A.md（先判任务语义→eligibility→scope，禁默认 tool，负例不赋 scope）。
- P22：先问左右能否同时成立；不能 → conflict_basis/type；能 → non_conflict_hard_negative。
- P23：memory_inventory + target + must_keep + checkpoints + expected_residual；负例(ambiguous selector)无 selector 字段。
