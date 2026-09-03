# 阶段 8 标注手册 v1.1 审阅意见（Annotator B = DGXD01）— PR #24

- 审查人：Annotator B（DGXD01）
- 审查对象：PR #24 `feat/A-stage8-annotation` → master
  - `data/gold/annotation_guideline.md`（v1.0 候选草稿 18 行 → v1.1 完整执行手册 224 行）
  - `worklog/20260902_stage8_A.md`（新增）
- 审查日期：2026-09-03
- 依据：v2.0 重建计划五条红线、`data/processed/schema.json`、`reports/conversion_report.md`（715 条构成）、`reports/stage_plan_v2_with_roles.md`、Gate 8 验收要求（Kappa≥0.70 / 分歧有裁决 / 全标签有 evidence）

## 一、审查结论

**附条件通过（建议 Reviewer 采纳）**：手册结构完整，六类任务字段/枚举/判定规则/证据要求/试标与裁决流程齐全；五条红线覆盖到位；职责边界清晰（A 不越权）。存在 **P1×3 必改**、**P2×5 建议澄清**；P1 闭环后即可进入 A/B 独立试标。

## 二、P1（必改，影响试标落地）

1. **§3 知识检索**：`hard_negative_ids` 仅写“>0 更佳”，未设最低要求，与检索指标（Recall@K / 困难负样本）无法挂钩。建议：试标与量产明确**每个查询 ≥1 个困难负样本**为硬性要求（公开集缺口回填规则可保留）。
2. **§8 试标与一致性**：未定义 **Kappa 一致性口径**——按样本还是按字段？六类是否分层各算？“一致”以哪些字段为准？A/B 标签文件格式与列名未约定 → B 侧 `stage8_kappa.py` 无法落地。建议补充：总体 + 每任务分层 Cohen's Kappa；一致以 gold 主字段（或指定字段集）为准；约定 A/B 标签文件列名。
3. **§8.1 与 worklog 待办 3**：“试标阶段先用**合成场景文本**”与红线“禁 mock / 任何层级不得包含模拟或合成伪装的真实数据”存在表述张力，易被误读为允许 mock。建议显式写明：合成文本**仅限试标阶段跑通标注口径**，`source=team_authored`、`review_status=candidate_only`，**绝不进入封存**（与 `reports/conversion_report.md` 既有口径一致）。

## 三、P2（建议澄清，便于量产与裁决）

4. **§1 evidence 规范**：仅给出 `evidence[].source_event_id + span`，未给统一结构示例；**公开集（t2ranking / multiwoz 共 500 条 public_derived）的 evidence 如何从 raw_id 映射**未说明。建议补 evidence 结构示例 + public_derived / team_authored 两条溯源路径。
5. **§2 vs §4 边界**：偏好 `operation=update/revoke`（旧值保留可回溯）与冲突处理 `time_update` 的判定边界未划——何时进 preference_extraction、何时进 conflict_resolution？建议补一条判定分流规则。
6. **auxiliary_dialogue 处置**：schema 中含 `auxiliary_dialogue`（multiwoz 300 条），手册六类任务未说明该批语料在阶段 8 如何处置（作为困难负样本/冲突语料来源？或直接不标注？）。建议补一节说明。
7. **§9/§11 裁决产物格式**：`disagreement_log.csv`、`gold_draft.jsonl`、`final_label` 的列结构未定义（Reviewer 裁决需固定格式）。建议补充列结构：sample_id / 字段 / 分歧类型 / A 标签 / B 标签 / 裁决 / final_label / decision_reason。
8. **§11 校验命令**：候选草稿（8.2）生成后需**同步校验 enum_dictionary / schema 一致性**（tool_result 重建后尤其必要）。建议 8.2 结构化校验脚本纳入 enum 字典比对（B 侧落地）。

**格式小项**：`annotation_guideline.md` 与 `worklog/20260902_stage8_A.md` 文件末尾均无换行符（`\ No newline at end of file`），建议补上。

## 四、闭环后 B 侧后续（本意见被采纳后）

1. A / Reviewer 处理 P1（必要时修订手册定稿）。
2. B 搭建 `scripts/audit/stage8_kappa.py`（总体 + 分层 Cohen's Kappa、分歧聚类、disagreement 输出）。
3. A / B 独立试标 30~50 条 → B 计算 Kappa 并产出 `reports/stage8_kappa_report.md`。
4. Kappa≥0.70 后进入 8.2 候选草稿批量生成（A）+ B 结构化校验。
