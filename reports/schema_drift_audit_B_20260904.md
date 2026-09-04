# 数据包字段漂移自检与修复报告（B = DGXD01）— 2026-09-04

- 依据：《数据包_B轨字段漂移自检修复任务说明_20260904.md》（Reviewer 转 B 轨任务）
- 基准（只读）：KMA Canonical / D3（主仓库 main，PR #137，CANDIDATE_FOR_FREEZE，R-1..R-6）；本仓库入库副本 evidence/source/kma_unified_data_format_FREEZE_V1/（FREEZE_PROPOSAL 版，差异见 §4 注）
- 范围：仅本仓库数据侧字段扫描/登记/映射；未改主仓库代码；未改既有 Gold 字段值；未重转 processed。

## 一、扫描对象（§三）
1. data/processed/schema.json（顶层/field_rules）
2. data/processed/enum_dictionary.json（13 枚举键 + _meta 分层）
3. data/processed/*.jsonl gold.*（preference/conflict/forgetting/retrieval/e2e/aux）
4. scripts/convert/convert_to_schema.py + scripts/audit/*（映射/校验层）
5. registry/、reports/data_card_v1.md、requirement_data_mapping_v2.md（口径声明）

## 二、漂移清单与映射登记（证据：registry/field_mapping.json，30 行）
| 任务 | 数据字段 | Canonical 基准 | 类别 | 处置/登记 |
| --- | --- | --- | --- | --- |
| preference | preference_type | expression_type + preference_key（无同枚举） | A/C | 评测层主题分类；NOT production shared enum（enum _meta） |
| preference | scope (app/global/session) | preference_scope 五值 | D | 值域分叉；app/task 落点待 E 裁定（FROZEN#2）；不擅自改 Gold |
| preference | confidence (high) | confidence_score float[0,1] | C | DEFERRED(HD-SCHEMA-03)；评测归一化待 E 判定 |
| preference | should_store | should_persist + is_temporary | A/C | 登记映射，非生产枚举 |
| preference | operation | version + memory_status | A/C | 标注操作属评测层，不入业务枚举 |
| preference | value / old_value | preference_value / previous_version_value | A | 评测层映射 |
| retrieval | relevant_ids | retrieval_ref=(memory_id,version_id) D9 | C | 是否带版本/接入 D9 待 E/D 裁定 |
| retrieval | hard_negative_ids / relevance / expected_answer_points | guardrail/评测层 | A | 评测层，NOT production |
| conflict | conflict_type（旧5轴） | ConflictType 五值（FROZEN） | C | 评测分类；NOT production；冻结 Canonical 唯一 |
| conflict | winner | resolution_status/resolved_by | A/C | 评测判定标签；NOT production |
| conflict | keep_ids/remove_ids/resolution_reason | left/right/involved_knowledge_ids | A | 评测层映射 |
| forgetting | target_ids/expected_deleted | ForgetPlan target_selector/resolved_target_ids | A | 评测输入↔遗忘选择器映射 |
| forgetting | must_keep/checkpoints | （评测层） | A | 保留评测层；checkpoints 定位待裁定(FROZEN#4) |
| forgetting | expected_residual_count | affected_count | A | 评测层映射 |
| tool | status（5态）/persist_policy | source_business_status(8)/派生布尔 | A/C | 评测/旧版标签；NOT production（enum _meta） |
| tool | side_effect/failure_reason | content_summary | A | 评测层 |
| e2e | expected_memory/expected_response | （评测期望层，Canonical 无同名对象） | A | 保留评测期望层 |
| aux | goals/services | （语料原生） | A | 保留，不参与六类金标 |
| 顶层 | source | （数据治理） | A | 数据治理层，不改 |

### 证据样例（数据侧）
- data/processed/preference_extraction.jsonl：gold.confidence=high、gold.scope∈{app,global,session}、gold.operation∈{create,update,no_op}（样本 pref_000001 等）
- data/processed/conflict_resolution.jsonl：gold.conflict_type∈{time_update,scope,source,knowledge_version,safety}（40/40），gold.winner 5 值
- data/processed/precise_forgetting.jsonl / end_to_end_session.jsonl / knowledge_retrieval*.jsonl：字段如 §一 扫描
- data/processed/enum_dictionary.json：13 键 + _meta 分层标注（NOT production shared enum 清单）

## 三、合规修复（本 PR 落地）
1. enum_dictionary.json 增加 _meta 分层标注：eval_or_legacy_keys（preference_type/scope/operation/conflict_type/status/persist_policy/checkpoints/confidence/winner/review_status）显式 NOT production shared enum；governance_keys（task_type/source/template_family）；lifecycle 以 gold.memory_status 为准（§6.3/6.4 合规）。
2. registry/field_mapping.json：canonical ↔ 数据字段 30 行，标注 alias/评测归一化/待确认/owner/td 引用（§六.2）。
3. scripts/audit/schema_drift_check.py：字段名与 Canonical 值域/登记一致性校验（§六.6）；结果 exit 0、0 未登记、0 分层缺失。
4. 未新增任何与 Canonical 同名的第二套生产枚举；未改任何既有 Gold 字段值（非破坏）。

## 四、未冻结/待确认清单（§5.2，不改行为）
- confidence_score 量化/标签分级（HD-SCHEMA-03，A/E）；memory_type 边界（HD-SCHEMA-07，D）；conflict_type 阈值（HD-SCHEMA-04，B/E+D）；processing_status（A/B/D）；collected_at→captured_at（TD-060，C/D）；过渡布尔移除（TD-016，D）；检索 Gold 版本化（E/D）；scope=app 对齐（E）。
- 注：本仓库入库 KMA 文档为 FREEZE_PROPOSAL 版；任务说明称主仓库 main 已 CANDIDATE_FOR_FREEZE（R-1..R-6）。差异登记，待主仓库权威副本同步到本仓库 evidence/ 后再行对齐复核。

## 五、完成记录（§八 回填）
- 扫描范围：data/processed（715 条 gold）全字段 + enum_dictionary + registry 口径。
- 交付路径：reports/schema_drift_audit_B_20260904.md（本文件）、registry/field_mapping.json、scripts/audit/schema_drift_check.py、reports/schema_drift_check_output_20260904.txt、data/processed/enum_dictionary.json（_meta）。
- 测试命令与结果：python scripts/audit/schema_drift_check.py → mapping 30 行、unregistered=0、enum meta issues=0、exit 0。
- Reviewer 复核点：① scope app/task 落点(E)；② retrieval Gold 是否带 version(D9, E/D)；③ confidence 归一化口径(A/E)；④ checkpoints 评测层定位(E/D)；⑤ 本仓库 KMA 副本升级至 CANDIDATE_FOR_FREEZE 后重跑复核。

## 六、边界确认
未改主仓库代码；未改既有 Gold 字段值；未把评测层枚举并入生产；vector_index_entries.is_active 等与生命周期布尔不混用（TD-016 §3）。
