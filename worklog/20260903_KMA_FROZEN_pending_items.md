# KMA FROZEN 前必办清单（登记，响应 Reviewer Low-1）

- 登记日期：2026-09-03
- 关联：PR #26（阶段1/7 KMA 对齐）；KMA=FREEZE_PROPOSAL。

| # | 事项 | 责任 | 状态 |
| --- | --- | --- | --- |
| 1 | preference_key 取值策略（模板族约束开放字符串，勿再造枚举） | A/B 定稿 + Reviewer 裁定 | 🟡 A 建议稿已出（worklog/20260904_KMA_FROZEN_1_3_A_recommendation.md），待 B 复核 + Reviewer 裁定 |
| 2 | 旧 scope app/task 语义落点（不机械映射 app→tool、task→topic） | Reviewer 裁定 | 🟡 A 样例已出（worklog/20260903_KMA_confidence_scope_samples_A.md），待裁定 |
| 3 | confidence 高/中/低 → confidence_score [0,1] 固定换算口径 | A/B 定稿 | 🟡 A 定稿建议已出（同 #1 文件，三档主表 0.95/0.70/0.40），待 B 复核 + Reviewer 裁定 |
| 4 | forgetting checkpoints 定位：保留为评测层验证时点，不进业务状态 | Reviewer 裁定 | ⬜ 待裁定 |
| 5 | KMA_LEGACY_MAP 与 B 校验脚本核对（无冲突，需在 #25 合并后补齐 enum_check --kma） | B | ✅ 工具已移植适配至 #27（2026-09-03 进度更新） |
| 6 | D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl 补档入 evidence/source/kma_unified_data_format_FREEZE_V1/ | B 轨 PR#88 / A 提供 | ✅ A 已补档（2026-09-04，证据：evidence/source/kma_unified_data_format_FREEZE_V1/D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl） |
| 7 | KMA 转 FROZEN（签署 + 合并 main） | D/E Reviewer | ⬜ |
| 8 | 全量重转 processed gold + 重建阶段8标注枚举/骨架/试标 | A/B（FROZEN 后） | ⬜ |
| 9 | preference_scope/conflict_type 等权威版未列字段 → D3 契约（L2）核对落点 | A/B + D/E | ⬜（High-1 遗留新增） |

FROZEN 达成前：不做破坏性重转、不打断阶段8试标；每项闭环后在状态列更新为 ✅ 并附证据位置。

## 进度更新
- 2026-09-03（PR #27）：#5 工具复用已落地——自 #25 分支移植 `scripts/audit/stage8_kappa.py`（新增 `--format legacy|kma` 与 `--fields-json` 覆盖；KMA_FIELD_SETS 为 canonical 草案）、`stage8_trial_sample.py`、`test_stage8_kappa.py` 至 `feat/B-stage8-kma`；测试 7/7 PASS。enum_check 的 --kma 适配留待 labels 骨架定稿后随 #27 引入（避免跨 PR 重复文件）。

## 决策登记（2026-09-04）
- **试标时机（Reviewer Medium-决策）＝ 方案②**：等 KMA FROZEN 后直接按 v2 试标（避免 v1.3 试标在 FROZEN 后重做）。正式 30~50 条试标在 FROZEN 达成前不启动。
- **#27 去向**：保持 OPEN（不合并），作为阶段8 v2 工作载体持续累积（KMA 基线已在 master=#26）。
- **Low-1**（v2 手册行尾空格）：已修复提交（style）。
- 后续计划：见 reports/stage8_v2_followup_plan.md。

## P0 进度（2026-09-04）
- B：canonical labels_A/B 骨架设计已起草 → reports/stage8_v2_labels_skeleton_design.md（FROZEN 前只出方案，未生成正式 labels/未改数据）。
- A：D9 补档 #6 闭环（复制至 kma_unified_data_format_FREEZE_V1/）；#1/#3 定稿建议稿 → worklog/20260904_KMA_FROZEN_1_3_A_recommendation.md。

## High-1 响应（2026-09-04，A）
- 主仓库权威版（CANDIDATE_FOR_FREEZE，159 行，E 轨 2026-09-03）已抓取入库：`evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md`。
- `source_provenance.md` 已修订：纠正基线引用错误（b70827c5 该路径 404）、移除无主仓库对应的编号 KMA-DATA-SCHEMA-001、明确两版关系（权威版=对齐基线，975 行旧版=仅枚举明细参考）。
- 一致性核验：R-2/R-3/R-4/R-5（expression_type/memory_status/source_business_status/sensitivity）与本仓库编码一致；preference_scope/conflict_type 等权威版未列字段 → 需 D3（L2）契约核对（新增遗留项）。
- 新增遗留项：#9 preference_scope/conflict_type 与 D3 契约（L2）核对落点。

## 补充遗留项（2026-09-04，B 侧复核补充）
- #10 D 轨物理映射确认（gold 字段 → SQLite/Vector 落库命名，Reviewer Medium-1）→ D（另案登记，不阻塞定义层）。
- #11 E 轨「评测 gold ↔ canonical 映射签名」确认（Reviewer Low-1）→ E。
- #12 schema.json kma_alignment 状态/引用切换至权威候选版后的复核 → B/A。
