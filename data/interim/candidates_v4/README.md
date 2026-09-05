# candidates_v4 — A 侧候选工厂输入包（v4.1）

> 状态：**DRAFT_INPUT_PACKAGE / candidate_only / NOT_ADMISSION_APPROVED**（Data-A 预处理，2026-09-05）
> 性质：全部 `candidate_only`，非 Gold，未通过 Admission G1-G5；不写 human_decision/final_label；不构成任何 Gold / Closure PASS 证据。
> 依据：PR#32 Data-R 评论 A-0（#32 合并前只做规则准备）。

## 目录

- `factory_config.json` — 配额(P04)、来源分层、template_family 计划、G9 generation manifest、阻塞清单
- `scenario_specs/` — OS 场景规格（preference / conflict / forgetting），作为 P20/P22/P23 的 os_controlled_authored 输入
- `exemplar_candidates/` — 每任务 3 条示例候选（结构验证，非量产）

## 使用方式

1. 候选工厂量产前先确认：C1 Legacy-N 冻结 → P04 动态配额（`candidate_needed = ceil((target - accepted_legacy) × 1.30)`）→ P2-A 工具（admission_gate/validate_labels）。
2. 当前 factory_config 中的 293/163/130 为 **provisional_max_pool（pre-C1 planning number）**，非 P04 最终配额；C1 冻结 + Legacy 重准入后必须重算。
3. 按 scenario_spec 生成候选，每条带 `scenario_spec_id` + `generation_id` + `prompt_version` + `seed` + `model`（G9）。
4. template_family 单族 ≤ 该任务候选池 25%（G4）；exact dup=0；Jaccard>0.85 送审。
5. scope 按 `reports/v4.1_scope_review_standard_A.md` 复核：**先判任务语义（G2）→ preference eligibility → 仅对合法 preference 赋 scope**，禁默认 tool。

## 阻塞

见 `reports/v4.1_A_readiness_20260905.md` 第三节（当前推进到 C1 Legacy-N 冻结）；Closure 总状态以 `reports/closure_status_v4.1.json` 为唯一真源。