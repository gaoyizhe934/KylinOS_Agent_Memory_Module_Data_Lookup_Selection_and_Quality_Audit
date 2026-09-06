# Prompt: P20/P22/P23 候选工厂输入包（Data-A 预处理）

## 角色
Data-A（lyf-1213）的 AI 辅助，v4.1 基线。

## 任务
- 依据 v4.1 SOP（PR#32）与 KMA Canonical v1，构建 Preference/Conflict/Forgetting 候选工厂输入包：
  1. `data/interim/candidates_v4/factory_config.json`
  2. `data/interim/candidates_v4/scenario_specs/*.json`（3 个任务场景规格）
  3. `data/interim/candidates_v4/exemplar_candidates/*.jsonl`（每任务 3 条结构验证候选）
  4. `reports/v4.1_scope_review_standard_A.md`（G2 scope 复核标准）
  5. `reports/v4.1_A_readiness_20260905.md`（就绪与阻塞报告）

## 边界（严格）
- 全部 candidate_only；gold 为空；不写 human_decision / final_label。
- 每条候选带 scenario_spec_id / generation_id / prompt_version / seed / model（G9）。
- 不生成正式 Gold、不做盲标、不看 B 标签。
- 阻塞（C1 Legacy-N 未冻结等）如实登记，不宣称完成。

## 输入
- PR#33 最新分支（feat/B-stage8-v4.1-closure）：B 的 P01/P03/P00 产出。
- v4.1 SOP/台账/Prompt Pack（PR#32）。
- KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md。
- 阶段8 候选重建 v2 格式（rebuild_candidates_v2.py 产出）。