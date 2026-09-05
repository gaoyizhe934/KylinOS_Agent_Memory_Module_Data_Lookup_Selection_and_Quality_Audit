# candidates_v4 — A 侧候选工厂输入包（v4.1）

> 状态：**DRAFT_INPUT_PACKAGE / candidate_only / NOT_ADMISSION_APPROVED**（Data-A 预处理，2026-09-05）
> 性质：全部 `candidate_only`，非 Gold，未通过 Admission G1-G5；不写 human_decision/final_label；不构成任何 Gold / Closure PASS 证据。
> 依据：PR#32 Data-R 评论 A-0（#32 合并前只做规则准备）。

## 目录

- `factory_config.json` — 配额(provisional_max_pool)、来源分层(含 Registry eligibility)、template_family 计划、G9 generation manifest、防泄漏断言
- `scenario_specs/` — OS 场景规格（preference / conflict / forgetting），作为 P20/P22/P23 的 os_controlled_authored 输入
- `exemplar_candidates/` — 每任务 3 条示例候选（结构验证，非量产；双层结构：blind_visible 无答案 + design_metadata 含设计字段）

## 使用方式

1. 候选工厂量产前先确认：C1 Legacy-N 冻结 → P04 动态配额（`candidate_needed = ceil((target - accepted_legacy) × 1.30)`）→ P2-A 工具（admission_gate/validate_labels）。
2. 当前 factory_config 中的 293/163/130 为 **provisional_max_pool（pre-C1 planning number）**，非 P04 最终配额；C1 冻结 + Legacy 重准入后必须重算。
3. 候选结构**必须分层**：`blind_visible`（仅用户原话/必要无答案上下文）与 `design_metadata`（scenario_spec_id / design class / expected / target / must_keep / scope target 等）。P40/validator 断言盲包不得含 design 字段。
4. 按 scenario_spec 生成候选，每条带 `scenario_spec_id` + `generation_id` + `prompt_version` + `seed` + `model`（G9）；`id_binding_status=NON_PRODUCTION`，user/event ID 为设计占位，production binding 时 fail-closed。
5. template_family 单族 ≤ 该任务候选池 25%（G4）；exact dup=0；Jaccard>0.85 送审。
6. scope 按 `reports/v4.1_scope_review_standard_A.md` 复核：**先判任务语义（G2）→ preference eligibility → 仅对合法 preference 赋 scope**，禁默认 tool。
7. 公开来源 eligibility 以 Registry 为准（如 personachat_2018 = SOURCE_PENDING_REVIEW，admission_eligible=false）。

## 阻塞

见 `reports/v4.1_A_readiness_20260905.md` 第三节（当前推进到 C1 Legacy-N 冻结）；Closure 总状态由 **#33** 管理。