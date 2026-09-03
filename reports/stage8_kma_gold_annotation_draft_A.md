# 阶段8 v2：六类任务 KMA canonical gold 标注口径草案（Annotator A）

- 角色：Annotator A（lyf-1213）
- 分支：`feat/B-stage8-kma`（PR #27）
- 日期：2026-09-03
- 依据：`reports/stage8_kma_rebaseline.md`（B 侧重基线，§二 目标 gold 对象）、`data/processed/schema.json`（gold_enum_alignment）、KMA 标准 `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md`、D9 检索集
- 性质：**草案（先行对齐口径）**，KMA 仍 FREEZE_PROPOSAL，不做破坏性重转、不打断试标；FROZEN 后据此重建阶段8标注产物（手册 v2 / labels 骨架 / 试标 / Kappa）

---

## 0. 通用约定（六类任务共用）

| 项 | 规则 |
| --- | --- |
| `user_id` | 直接携带，禁止模型生成/从正文推断（KMA §6/§7） |
| `memory_status` | 业务生命周期真值：`active/superseded/deprecated/expired/removed/candidate`；`review_status` 仅评测标签审阅（candidate_only/approved/rejected），二者职责分离 |
| 时间 | `created_at/updated_at` 用 UTC 毫秒 `YYYY-MM-DDTHH:MM:SS.sssZ`；系统时间不得由 LLM 生成 |
| ID | `*_id` 为 opaque string，非空非空白；不依赖前缀解析业务含义 |
| 版本 | `version` integer>=1；version>1 必须带 `previous_version_id` |
| 证据 | `evidence_event_ids`（list 非空）；每条 evidence 含 `source_event_id/span/source_type` |

---

## 1. preference_extraction → Preference

### canonical gold 字段
| 字段 | 枚举/规则 | 说明 |
| --- | --- | --- |
| `expression_type` | `explicit` / `implicit` | 显式声明 vs 隐式推断 |
| `preference_scope` | `global` / `topic` / `tool` / `session` / `time_window` | 替代旧 scope(app/task) |
| `preference_key` | 开放字符串（模板族约束，勿再造枚举） | 替代旧 preference_type |
| `preference_value` | 可执行、可比较字符串 | 替代旧 value |
| `confidence_score` | float [0,1] | 替代旧 confidence(high/medium/low) |
| `should_persist` | boolean | 替代旧 should_store |
| `is_temporary` | boolean | 新增 |
| `memory_status` | 6 值 | 生命周期 |
| `version` | int>=1 | 替代旧 operation |
| `evidence_event_ids` | list 非空 | 溯源 |

### 标注判定（映射旧→新，待 FROZEN 裁定项 1/2/3）
- 显式"以后都这样"→ `expression_type=explicit`、`should_persist=true`、`confidence_score≈0.95`
- "这次/仅本次"→ `is_temporary=true`、`should_persist=false`、`memory_status=candidate`
- "之前…改成…"→ 新版本 `version=n+1` + `previous_version_id`（替代旧 operation=update）
- "之前的不要了"→ 旧版本 `memory_status=superseded`
- 敏感内容 → `should_persist=false`、`memory_status=candidate`
- ⚠ `app/task` 语义落点：**不机械映射**（待 Reviewer 裁定，见 FROZEN 清单#2）

---

## 2. knowledge_retrieval → Knowledge

### canonical gold 字段
| 字段 | 枚举/规则 |
| --- | --- |
| `knowledge_type` | `workflow` / `case` / `template` / `fact` / `constraint` / `failure_experience` |
| `knowledge_id` | opaque string |
| `memory_status` | 6 值 |
| `superseded_by_id` | optional（版本链） |
| 版本引用 | `memory_id + version_id`（D9 口径） |
| 禁止召回 | 8 类：`superseded/expired/removed_or_forgotten/candidate/unresolved_conflict/cross_user/sensitive_recall_prohibited/deprecated` |

### 标注判定
- 相关正解：同用户 **active 当前版本**
- 旧版（superseded/is_current=false）→ 禁止召回
- 语义近似当前版 → `semantic_near_miss`（不计 guardrail violation）
- `evaluation_role`：`positive_retrieval` / `negative_guardrail`
- 每条带 `rationale`（依据可解释）

---

## 3. conflict_resolution → Conflict

### canonical gold 字段
| 字段 | 枚举/规则 |
| --- | --- |
| `conflict_type` | `contradiction` / `temporal_inconsistency` / `source_conflict` / `preference_conflict` / `scope_ambiguity` |
| `resolution_status` | `detected` / `analyzing` / `resolved_auto` / `resolved_manual` / `deferred` / `unresolvable` |
| `left_knowledge_id` / `right_knowledge_id` | 冲突双方（left≠right） |
| `involved_knowledge_ids` | optional，涉及集合 |
| `resolution_strategy` | optional |
| 不变量 | resolved_auto/manual → `resolved_at`/`resolved_by` 必填 |

### 标注判定
- 时间更新冲突 → `temporal_inconsistency` + `resolution_status=resolved_manual`（或 auto 规则）
- 作用域冲突 → `scope_ambiguity` + 应用级在该应用内优先
- 来源冲突 → `source_conflict` + 显式配置优先
- 版本冲突 → `temporal_inconsistency` 或 `contradiction`（按版本语义）→ 裁定项
- 安全冲突 → 安全策略优先，`resolved_manual`

---

## 4. precise_forgetting → ForgetPlan

### canonical gold 字段
| 字段 | 枚举/规则 |
| --- | --- |
| `forget_mode` | `single_item` / `session` / `topic` / `time_window` / `full_reset` |
| `target_type` | `knowledge` / `preference` / `event` / `all` |
| `target_selector` | string（模式不变量约束） |
| `status` | `pending` / `previewing` / `awaiting_confirmation` / `executing` / `completed` / `failed` / `rolled_back` |
| `is_cascade` / `has_vector_cleanup` / `requires_confirmation` | boolean |
| `resolved_target_ids` | preview 结果（+ `affected_count` 必填） |

### 标注判定
- `target_selector` 按 forget_mode 约束（single_item→target_id；session→target_session_id；topic→target_topic；time_window→target_time_range；full_reset→无具体 selector）
- `expected_deleted`/`must_keep` 语义保留到 `resolved_target_ids` 与受保护对象集合
- ⚠ `checkpoints`：保留为评测层验证时点（immediate_query/after_restart/after_full_reindex），**不进业务状态**（待 Reviewer 裁定，FROZEN 清单#4）

---

## 5. tool_result → MemorySourceEvent.source_business_status

### canonical gold 字段
| 字段 | 枚举/规则 |
| --- | --- |
| `source_business_status` | `raw` / `completed` / `success` / `partial` / `failed` / `cancelled` / `timeout` / `ignored` |
| `tool_call_id` | **tool_result 时必填**（KMA 条件不变量） |
| `source_type` | `tool_result` |
| `event_type` | `user_message` / `agent_response` / `system_message` |
| `content_summary` | 敏感过滤后摘要 |
| `requires_embedding` / `has_structured_payload` | 派生 |

### 标注判定
- success 视副作用/价值决定沉淀；failed 不得写成成功；cancelled 禁止推断副作用已发生；timeout 标未知；partial 拆分成功/失败
- ⚠ 封存集必须麒麟 VM 真实回放（禁 mock）

---

## 6. end_to_end_session → MemorySourceEvent 链

### canonical gold 字段
| 字段 | 枚举/规则 |
| --- | --- |
| `expected_memory` | 生命周期对齐 `memory_status`（6 值）+ `memory_type`（short_term/medium_term/long_term/ephemeral） |
| `expected_response` | 评测层字段（KMA 不冻结），保留 |

### 标注判定
- 覆盖跨会话复用/冲突/工具/遗忘/重启恢复
- `expected_memory`/`expected_response` 从事件链证据推导
- 封存集必须麒麟 VM 真实回放（禁 mock）

---

## 7. 争议/待裁定提示（本草案不擅自定）

1. `preference_key` 取值策略（开放字符串 vs 受控词表）→ FROZEN 清单#1
2. 旧 `scope` 的 app/task 语义落点（不机械映射）→ FROZEN 清单#2
3. confidence 高/中/低 → [0,1] 固定换算口径 → FROZEN 清单#3
4. forgetting `checkpoints` 保留评测层 → FROZEN 清单#4

## 8. 后续（FROZEN 后）
- 手册 v2（本文稿定稿）→ labels_A/B 骨架（canonical）→ 试标/Kappa（B 侧一致字段集适配）→ 全量重转 processed

## 9. A 不越权声明
- 未重转 processed、未改 labels 骨架、未改 stage8_kappa；本文仅为标注口径草案，供 A/B 对齐与 Reviewer 裁定。
