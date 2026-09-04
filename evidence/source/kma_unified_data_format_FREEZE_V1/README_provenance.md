# 标准溯源说明 — KMA 统一格式冻结规范 v1 & D9 检索集存档

- 建档：Annotator A（lyf-1213）· 2026-09-03
- 目的：响应 Reviewer Medium-1（`feat/A-schema-kma-align` PR）——将阶段1/7 KMA 对齐所依据的外部标准入库，确保对齐正确性可独立核验。

## 一、KMA 统一格式冻结规范 v1

| 项 | 内容 |
| --- | --- |
| 存档路径 | `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md` |
| 文档编号 | KMA-DATA-SCHEMA-001 |
| 版本 | v1.0 |
| 状态 | FREEZE_PROPOSAL（合并 `main` 且经 D/E 非作者 Reviewer 签署后转 FROZEN） |
| 基线仓库 | `Kylin-Agent-Competition/kylinOS-agent-memory` |
| 基线参考 | `main@b70827c5e9c9e014ae2c025eb01d0adfaabd4ef9` |
| 获取方式 | 主仓库工作区提供的外部标准文档（非本仓库 Git 历史生成） |
| 访问日期 | 2026-09-03 |
| 用途 | 本数据包 gold 业务字段对齐的 canonical 依据（`schema.json` 的 `kma_alignment`/`gold_enum_alignment`、`scripts/convert/convert_to_schema.py` 的 `KMA_ENUMS`/`KMA_LEGACY_MAP`） |

### 与所编码枚举的对照
| 概念 | KMA 文档章节 | 本仓库编码位置 |
| --- | --- | --- |
| PreferenceScope | §5.8 | schema.json gold_enum_alignment.preference_extraction.preference_scope |
| ExpressionType | §5.7 | 同上 expression_type |
| MemoryStatus | §5.11 | 同上 memory_status / kma_alignment.lifecycle_truth |
| KnowledgeType | §5.9 | gold_enum_alignment.knowledge_retrieval.knowledge_type |
| ConflictType | §5.12 | gold_enum_alignment.conflict_resolution.conflict_type |
| ResolutionStatus | §5.13 | 同上 resolution_status |
| ForgetMode / ForgetPlanStatus / TargetType | §5.14/5.15/5.16 | gold_enum_alignment.precise_forgetting.* |
| SourceBusinessStatus | §5.3 | gold_enum_alignment.tool_result.source_business_status |
| 时间格式 | §3.6 | kma_alignment.time_format |
| ID 规则 | §3.7 | kma_alignment.id_rule |

## 二、D9 检索查询集候选 v2（36 条）

| 项 | 内容 |
| --- | --- |
| 存档路径 | `evidence/source/d9_retrieval_queryset/D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl`（另有副本 `evidence/source/kma_unified_data_format_FREEZE_V1/D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl`，FROZEN 清单 #6 指定位置，2026-09-04 补档） |
| 内容 | 36 条知识检索查询集候选（positive_retrieval × 20 + negative_guardrail × 16），含版本级引用 `relevant_refs/forbidden_refs/semantic_near_miss_refs`、`guardrail_category`（8 类）、`rationale` |
| 来源 | B 轨工作产物（2026-08-31，B 轨裁决 PR#88），主仓库既有数据 |
| 用途 | 阶段8 知识检索标注规则升级依据（版本级引用 + 禁止召回 8 类细分 + evaluation_role + rationale），已并入 `data/gold/annotation_quickref.md` 与 `annotation_guideline.md` §3 |
| 获取方式/访问日期 | 主仓库工作区提供，2026-09-03 建档 |

## 三、独立核验方式

1. Reviewer 可打开 `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md` 逐条核对 §5 枚举与 `schema.json` 的 `gold_enum_alignment` 是否一致。
2. Reviewer 可打开 `evidence/source/d9_retrieval_queryset/D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl`（或 `evidence/source/kma_unified_data_format_FREEZE_V1/` 副本）核对检索标注规则（`knowledge_type`/`guardrail_category`/版本级引用）。
3. 已编码内容若有出入，请以 `evidence/source/` 内存档为准发起修正（走 ADR 流程）。

## 四、FROZEN 前必办（登记自 B 复核 Low-1）

- [ ] preference_key 取值规范确认
- [ ] app→tool / task→topic 非机械映射裁定
- [ ] confidence（high/medium/low）→ confidence_score 换算规则
- [ ] checkpoints → ForgetPlan status 阶段定位
- [ ] `KMA_LEGACY_MAP` 与 B 侧校验脚本交叉核对