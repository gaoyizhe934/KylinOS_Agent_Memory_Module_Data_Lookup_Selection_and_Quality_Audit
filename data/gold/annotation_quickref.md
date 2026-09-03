# 标注速查表（六类任务选项一览）

用于标注 `labels_A/B_trial.jsonl` 时对照填写。每条 gold 只填值、不改键名。

---

## 1. 偏好提取 preference_extraction

| 键 | 选项 | 什么时候选 |
|---|---|---|
| preference_type | `output_style` | 输出/回复风格 |
| | `tool_choice` | 用工具的方式（如"删文件前先问我"） |
| | `safety` | 安全/隐私/敏感（密码、付款、凭证） |
| | `app` | 点名某个软件/应用 |
| | `workflow` | 固定工作流程 |
| | `other` | 以上都不贴（兜底，需 Reviewer 批准） |
| scope | `global` | "都/所有"或没指定范围 |
| | `app` | 只某应用内 |
| | `task` | 只某类工作 |
| | `session` | "这次/仅本次" |
| confidence | `high` | 一句话说死，不用猜 |
| | `medium` | 靠多句推断 |
| | `low` | 很模糊 |
| should_store | `true` | 带"以后/以后都" |
| | `false` | "这次"、闲聊、敏感、推测 |
| operation | `create` | 头一回提出 |
| | `update` | "之前…改成…"（value 填新说法） |
| | `revoke` | "取消/不要了" |
| | `no_op` | 临时一下、不用动（通常配 should_store=false） |

**value**：写能执行的具体要求（如"周报用简洁要点，每条<=2行"），禁止空话"喜欢这样"。

---

## 2. 知识检索 knowledge_retrieval

| 键 | 规则 |
|---|---|
| relevant_ids | ≥1 个相关文档 id（硬性） |
| relevance | `{doc_id: 1..4}` 相关度 |
| hard_negative_ids | **≥1 个**（硬性）；见下方禁止召回细分。public_derived 例外可留空 |
| expected_answer_points | 答案要点（从知识文档证据提取） |

### 禁止召回（hard_negative_ids / forbidden_refs）8 类细分（参考 D9 检索集）

按 B 轨 D9 检索集（36 条候选，PR#88 裁决）的 `guardrail_category`，禁止召回可分：

| 类别 | 含义 | 判定 |
| --- | --- | --- |
| `superseded` | 旧版本被替代（is_current=false） | 仅存审计用途，不得作当前正解 |
| `expired` | 已过期（memory_status=expired） | 过期条目不得召回 |
| `removed_or_forgotten` | 已执行遗忘（memory_status=removed） | 已遗忘条目不得返回 |
| `candidate` | 未经人工复核/证据确认 | 不得进入正式正解集合 |
| `unresolved_conflict` | 处于未裁决冲突 | 未裁决条目不得作正解 |
| `cross_user` | 跨用户读取 | 用户隔离边界，一律拒绝 |
| `sensitive_recall_prohibited` | 敏感内容禁止召回 | sensitivity=critical，禁止返回 |
| `deprecated` | 已废弃（仅显式 history/audit 模式可访问） | 标准检索禁召回 |

### 版本级引用（memory_id + version_id）

- 相关文档应区分 **current 当前版** 与 **旧版（superseded/stale）**：
  - 正解 `relevant_ids` 只指向同用户 **active 当前版本**；
  - 旧版（superseded、is_current=false）归禁止召回；
  - 当前版但语义近似的作 `semantic_near_miss`（词汇近似但不禁止，不计 guardrail violation）。
- 参考结构（D9）：`{"memory_id":"d9c-001","version_id":"d9c-001-v1"}`。

### evaluation_role（样本角色）

- `positive_retrieval`：正向检索，有正解。
- `negative_guardrail`：护栏样本，无正解，只验证"禁止召回"（如跨用户/敏感/已遗忘/过期/被替代/未裁决/未审核/废弃）。

### 每条带 rationale（依据说明）

- 标注须写一句 `rationale`：说明正解为何相关、禁止项为何禁止（如"跨用户对用户B 业务禁止""superseded 旧版仅审计用途"）。

---

## 3. 冲突处理 conflict_resolution

| 键 | 选项/规则 |
|---|---|
| conflict_type | `time_update`（新盖旧）/ `scope`（全局 vs 应用）/ `source`（手动 vs 推断）/ `knowledge_version`（旧 vs 新流程）/ `safety`（效率 vs 安全） |
| winner | time→`keep_new`；scope→`app_priority`；source→`explicit_config`；knowledge_version→`new_version`；safety→`safety_priority` |
| resolution_reason | 写依据一句话 |
| keep_ids | 保留对象 id |
| remove_ids | 移除对象 id（无移除填 `[]`） |

---

## 4. 精准遗忘 precise_forgetting

| 键 | 规则 |
|---|---|
| target_ids | 应删对象 id |
| expected_deleted | **= target_ids** |
| must_keep | 必须同时给：不应误删的对象 id |
| checkpoints | `immediate_query` / `after_restart` / `after_full_reindex`（至少 immediate_query） |
| expected_residual_count | 残留数，通常 0 |

---

## 5. Tool Result tool_result

| 键 | 选项/规则 |
|---|---|
| status | `success` / `failed` / `cancelled` / `timeout` / `partial_success` |
| persist_policy | `yes`（可沉淀复用）/ `no` |
| side_effect | 副作用记录 |
| failure_reason | failed 必填失败原因 |

**铁律**：failed 不许写成 success；partial_success 不能整体标 success；cancelled 不许推断副作用已发生。

---

## 6. 端到端会话 end_to_end_session

| 键 | 规则 |
|---|---|
| expected_memory | 期望沉淀的记忆（可含 version/status） |
| expected_response | 期望系统回复 |

---

## 7. evidence 填写

| 键 | 规则 |
|---|---|
| source_event_id | team_authored→input 提供的（如 `evt_pref_3`）；public_derived→query_id |
| span | 抄 input 原话片段（不许编） |
| source_type | `utterance`（team_authored）/ `raw_record`（public_derived） |