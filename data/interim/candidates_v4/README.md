# candidates_v4 — A 侧候选工厂输入包（v4.1）

> 状态：**DRAFT_INPUT_PACKAGE**（Data-A 预处理，2026-09-05）
> 性质：全部 `candidate_only`，非 Gold，不写 human_decision/final_label。

## 目录

- `factory_config.json` — 配额(P04)、来源分层、template_family 计划、G9 generation manifest、阻塞清单
- `scenario_specs/` — OS 场景规格（preference / conflict / forgetting），作为 P20/P22/P23 的 os_controlled_authored 输入
- `exemplar_candidates/` — 每任务 3 条示例候选（结构验证，非量产）

## 使用方式

1. 候选工厂量产前先确认：C1 Legacy-N 冻结 → P04 动态配额定稿 → P2-A 工具（admission_gate/validate_labels）。
2. 按 scenario_spec 生成候选，每条带 `scenario_spec_id` + `generation_id` + `prompt_version` + `seed` + `model`（G9）。
3. template_family 单族 ≤ 该任务候选池 25%（G4）；exact dup=0；Jaccard>0.85 送审。
4. scope 按 `reports/v4.1_scope_review_standard_A.md` 人工复核，禁默认 tool。

## 阻塞

见 `reports/v4.1_A_readiness_20260905.md` 第三节（当前推进到 C1 Legacy-N 冻结）。