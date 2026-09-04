# 阶段8 v2 canonical labels_A/B 骨架设计（B = DGXD01，P0 草案）— 2026-09-04

## 0. 目的与边界
- 目的：为 KMA FROZEN 后直接落地的 canonical 试标 labels 骨架提供设计（结构/字段/校验/落地流程）。
- 性质：**设计草案，不改任何数据**；FROZEN 前不生成正式 labels 文件、不重转 processed。
- 依据：标注手册 v2（data/gold/annotation_guideline_v2.md）、registry/kappa_agreement_fields.json（一致字段集单一来源）、registry/field_mapping.json（漂移映射）、schema.json gold_enum_alignment、KMA 标准/D9。

## 1. 目标文件与结构
- 文件：`data/interim/labels_A_trial_v2.jsonl` / `labels_B_trial_v2.jsonl`（与 v1.3 模板文件名区分；FROZEN 后由工具生成）。
- 记录结构（沿用手册 §2 骨架）：sample_id / task_type / gold（canonical 业务字段）/ evidence（数组）。
- 评测层字段：review_status（candidate_only/approved/rejected）在骨架上层或由流程统一填，不混入 gold 业务生命周期。

## 2. 各任务 canonical gold 字段骨架（依据 v2 §3–§8 + registry 单源）
### preference_extraction
- expression_type: explicit | implicit
- preference_scope: global | topic | tool | session | time_window（app/task 落点待裁定）
- preference_key: 开放字符串（取值策略待裁定 #1）
- preference_value: 可执行字符串
- confidence_score: float [0,1]（档位换算待裁定 #3）
- should_persist / is_temporary: boolean
- memory_status: active/superseded/deprecated/expired/removed/candidate
- version: int>=1（>1 必带 previous_version_id）
- evidence_event_ids: list[string] 非空
### knowledge_retrieval（KB/D9 就绪前部分可执行）
- knowledge_type: workflow/case/template/fact/constraint/failure_experience
- knowledge_id / memory_status / superseded_by_id / 版本引用(memory_id+version_id, D9 裁定) / evaluation_role（评测层）
- 正解/禁止召回 id 集（字段命名随 D9 裁定；待 #7）
### conflict_resolution
- conflict_type: contradiction/temporal_inconsistency/source_conflict/preference_conflict/scope_ambiguity
- resolution_status: detected/analyzing/resolved_auto/resolved_manual/deferred/unresolvable
- left_knowledge_id / right_knowledge_id（left≠right）/ involved_knowledge_ids（可选）
- resolution_strategy（可选）
### precise_forgetting
- forget_mode / target_type / target_selector（模式不变量）
- status: ForgetPlanStatus 7 值
- is_cascade/has_vector_cleanup/requires_confirmation（DEFERRED 项，评测层可选）
- resolved_target_ids + affected_count（preview 语义，随裁决）
### tool_result
- source_business_status 8 值 / tool_call_id（必填）/ source_type=tool_result / content_summary
### end_to_end_session
- expected_memory（memory_status/memory_type 对齐）/ expected_response（评测层）

## 3. 一致字段集（Kappa，直接引用 registry/kappa_agreement_fields.json）
- 与 v2 §9/脚本同源：preference=expression_type+preference_scope+should_persist+is_temporary+memory_status；retrieval=evaluation_role+knowledge_type+memory_status；conflict=conflict_type+resolution_status；forgetting=forget_mode+target_type+status；tool=source_business_status；e2e=expected_response。
- 落地时由工具自动读取该文件生成骨架字段顺序与必填标记，禁止再手写第二份。

## 4. 生成与校验（FROZEN 后执行）
1. 由 stage8_trial_sample.py 沿用样本池输出 sample_id 清单 → 生成 v2 空骨架（每任务按第 2 节字段）；
2. 校验：schema_drift_check/schema 校验适配 canonical 字段名与枚举；enum_dictionary 收口后比对；
3. 提交前 label_check 适配；Kappa 用 stage8_kappa.py --format kma（registry 单源）。

## 5. 与 v1.3 模板差异（迁移说明）
- 字段替换：preference_type→preference_key(+expression_type)；scope→preference_scope；confidence→confidence_score；should_store→should_persist+is_temporary；operation→version+memory_status；conflict_type/winner→canonical 枚举 + resolution_status；tool status→source_business_status；persist_policy 移出业务字段（评测层可选）。
- 保留评测层：sample_id/evidence/template_family/review_status。

## 6. 未决（FROZEN/裁定后回填，设计留位）
| # | 事项 | 影响骨架字段 | 裁定方 |
| --- | --- | --- | --- |
| 1 | preference_key 取值策略 | preference_key 约束 | Reviewer |
| 2 | app/task 落点 | preference_scope 值映射 | E/Reviewer |
| 3 | confidence 换算档位 | confidence_score 取值 | A/E |
| 4 | checkpoints + 版本冲突 conflict_type | forgetting/conflict | E/D |
| 7 | retrieval version(D9) | retrieval 引用字段 | E/D |

## 7. 落地流程（FROZEN 触发）
裁定回填 → 生成工具产出 v2 骨架文件 → A/B 独立试标 → stage8_kappa --format kma → Kappa≥0.70 → 8.2/8.3 → Gate 8。
