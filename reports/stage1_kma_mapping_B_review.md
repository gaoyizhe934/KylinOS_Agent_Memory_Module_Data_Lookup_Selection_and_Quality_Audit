# 阶段1 KMA 统一格式对齐 — B 侧复核（DGXD01）

- 日期：2026-09-03
- 对象：PR #26（feat/A-schema-kma-align）「阶段1+7 KMA 统一格式对齐」
- 依据：KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md（KMA-DATA-SCHEMA-001 v1.0，FREEZE_PROPOSAL）、reports/requirement_data_mapping_v2.md 三、KMA 统一格式对齐、schema.json kma_alignment / gold_enum_alignment、convert_to_schema.py（KMA_ENUMS / KMA_LEGACY_MAP / kma_audit_processed）
- 结论：**A 侧参考/定义层对齐通过（附条件）**；六项指标全覆盖、职责分离表述成立；差异点见第四节，需 FROZEN 前由 Reviewer 裁定。

## 一、六项指标覆盖核对清单
| 指标/任务 | A 映射表 | 是否覆盖 | 备注 |
| --- | --- | --- | --- |
| 偏好提取 preference_extraction | ✓（Preference） | ✅ | 含 scope/confidence/lifecycle/operation 映射 |
| 知识检索 knowledge_retrieval | ✓（Knowledge） | ✅ | 含 knowledge_type/knowledge_id/forbidden_recall |
| 冲突处理 conflict_resolution | ✓（Conflict） | ✅ | 含 conflict_type/resolution_status |
| 精准遗忘 precise_forgetting | ✓（ForgetPlan） | ✅ | 含 forget_mode/target_type/status |
| Tool Result tool_result | ✓（MemorySourceEvent.source_business_status） | ✅ | 含 status 补 raw/completed/ignored、tool_call_id |
| 端到端会话 end_to_end_session | ✓（MemorySourceEvent 链） | ✅ | expected_response 判为评测层，KMA 不冻结 |
| auxiliary_dialogue | 无（语料非指标） | ⏭️ | 属对话语料（§7.1），不参与六指标，符合手册 |

结论：六类金标任务均有映射表，覆盖无遗漏。

## 二、新旧枚举映射复核（重点项）
### 2.1 preference_type → preference_key + expression_type
- A 映射方向正确：KMA Preference 无内容分类枚举，旧 preference_type（app/output_style/safety/tool_choice/workflow/other）属内容标签，应落为 preference_key（开放 string）+ expression_type（explicit/implicit）。
- B 意见：FROZEN 前需明确 preference_key 取值策略（建议模板族约束的开放字符串，勿再造一套枚举），并确保旧 preference_type 不再作为 canonical 真值。
### 2.2 scope app→tool、task→topic（重点核对）
- KMA PreferenceScope 为 global/topic/tool/session/time_window，无 app/task。
- **B 复核：不建议机械映射**：app（某应用内/应用域偏好）≠ tool（工具使用场景）；task（当前任务/单次）≠ topic（主题域）。
- 建议：FROZEN 前由 Reviewer 对旧值逐一裁定落点（或按语义拆分为 memory_status/scope 组合），映射表勿保留未落地的 placeholder。
### 2.3 其余核对
- confidence → confidence_score（float[0,1]）：方向正确，需给出 高/中/低→数值 的固定换算或标注直接输出分数；
- should_store → should_persist + is_temporary：方向正确；
- operation（create/update/revoke/no_op）→ version + previous_version_id + memory_status：方向正确；
- tool status 5 态 → source_business_status 8 态：需补 raw/completed/ignored 及失败不得写成成功规则；
- forgetting checkpoints → forget_plan status：方向正确，但 checkpoints 是验证时点，建议保留为评测层约束字段而非业务状态。

## 三、review_status vs memory_status 职责分离
- B 确认 A 表述成立：review_status（candidate_only/approved/rejected）＝评测标签审阅状态，只属评测样本层；memory_status（active/superseded/deprecated/expired/removed/candidate）＝业务记忆生命周期真值（KMA §6/§7）。
- 二者不冲突、不替代；gold 表达应沉淀/失效/撤销等业务状态时必须写 gold.memory_status 等 canonical 字段，不得用 review_status 冒充。
- schema.json field_rules 已写明该分离，复核通过；建议阶段8标注手册 v2 增加二者分离 + operation→version/memory_status 映射专节。

## 四、差异点汇总（待 Reviewer 裁定）
| # | 主题 | B 建议 |
| --- | --- | --- |
| 1 | preference_key 取值 | 用模板族约束的开放字符串，勿再造枚举 |
| 2 | app/task 映射 | 不机械映射 app→tool、task→topic，FROZEN 前逐值裁定 |
| 3 | confidence 换算 | 给出 高/中/低→[0,1] 固定口径 |
| 4 | forgetting checkpoints | 作为评测层验证时点保留，不进业务状态 |
| 5 | KMA_LEGACY_MAP | 与 B 校验脚本核对无冲突（详见 reports/stage7_kma_enum_audit_B.md） |

## 五、结论
A 侧参考/定义层对齐通过（附条件），不阻塞本 PR；FROZEN 后按以上差异裁定后执行全量重转。红线确认：FREEZE_PROPOSAL 期间不强制阻断 processed 重转、不打断阶段8试标。
