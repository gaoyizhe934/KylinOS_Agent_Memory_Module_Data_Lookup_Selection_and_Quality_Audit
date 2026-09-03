# KMA 标准溯源与对齐说明（响应 Reviewer Medium-1）

- 建档：2026-09-03（PR #26 复核）
- 目的：将 KMA 对齐依据入库，保证 Reviewer 可独立核验枚举/字段映射正确性。

## 一、KMA 标准文档
| 项 | 值 |
| --- | --- |
| 文档 | KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md（本目录已入库） |
| 文档编号 | KMA-DATA-SCHEMA-001 |
| 版本 | v1.0 |
| 状态 | FREEZE_PROPOSAL（未 FROZEN，未签署） |
| 基线仓库 | Kylin-Agent-Competition/kylinOS-agent-memory |
| 基线提交 | main@b70827c5e9c9e014ae2c025eb01d0adfaabd4ef9 |
| 获取方式 | 项目组本地提供（本仓库工作区外，Downloads 目录） |
| 访问/建档日期 | 2026-09-03 |

## 二、仓库所编码 KMA 内容的对照
- scripts/convert/convert_to_schema.py：KMA_ENUMS / KMA_LEGACY_MAP / kma_audit_processed 与本文 §5 枚举、§6 对象、§7 字段真值对照编码；
- data/processed/schema.json：kma_alignment / gold_enum_alignment 与本文 §5/§6 对照；
- reports/requirement_data_mapping_v2.md「三、KMA 统一格式对齐」与本文 §1/§5/§6/§7 对照。
- 复核结论：本仓库所编码枚举（preference_scope/expression_type/memory_status/knowledge_type/conflict_type/resolution_status/forget_mode/target_type/forget_plan_status/source_business_status 等）与 KMA §5 枚举值一致（差异见 reports/stage1_kma_mapping_B_review.md 第四节，均标为 FROZEN 前裁定项，非编码不一致）。

## 三、D9 检索集（待补档，开放项）
- 引用处：reports/requirement_data_mapping_v2.md（hard_negative_ids/禁止召回 8 类，标注“D9 检索集口径”）、worklog/20260903_stage1_7_KMA_align_A.md（D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl，B 轨 PR#88）。
- 现状：该文件不在本仓库、也未经本工作区提供，**无法在本 PR 归档**。
- 处置：登记为 FROZEN 前必办（见 worklog/20260903_KMA_FROZEN_pending_items.md #6），由持有方（B 轨 PR#88 / A）提供后补入本目录，Reviewer 再核验检索部分。

## 四、结论
KMA 对齐依据已可独立追溯（本文档 + 编码对照）；D9 检索集待持有方补档后完成检索侧核验。
