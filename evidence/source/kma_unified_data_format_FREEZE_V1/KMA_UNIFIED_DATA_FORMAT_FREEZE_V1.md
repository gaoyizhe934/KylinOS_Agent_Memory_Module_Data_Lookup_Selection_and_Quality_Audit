# 麒麟 OS Agent 记忆系统统一数据格式冻结规范 v1

- **文档编号**：KMA-DATA-SCHEMA-001
- **版本**：v1.0
- **状态**：FREEZE_PROPOSAL（合并 `main` 且经 D/E 非作者 Reviewer 签署后转 `FROZEN`）
- **适用范围**：A/B/C/D/E 全轨道；Memory Service、OS Agent Integration、IPC Adapter、SQLite、Vector/FTS 投影、Evaluation/Dataset
- **基线仓库**：`Kylin-Agent-Competition/kylinOS-agent-memory`
- **基线参考**：`main@b70827c5e9c9e014ae2c025eb01d0adfaabd4ef9`
- **目的**：冻结跨轨共享的业务字段名称、类型、枚举、空值、时间、ID、版本与兼容规则，消除同一概念在不同轨道重复定义或语义漂移。
- **不替代**：IPC envelope 物理协议、SQLite DDL、Vector Collection 物理布局、C++ 类型布局、具体算法与宿主能力验证。

---

## 1. 冻结结论

自本规范生效后，项目采用一套 **Canonical Business Schema（统一业务数据格式）**。

统一原则：

1. **业务语义只有一套**：同名字段在 A/B/C/D/E 不得出现不同业务含义。
2. **物理表示允许分层**：Python、C++、SQLite、IPC 可采用各自适合的技术表示，但必须可无损映射到本规范。
3. **不得再创建第二套同义字段**：已有 canonical 字段能表达的概念，不得新增别名字段。
4. **过渡字段不得继续扩散**：`is_active`、`is_outdated`、`should_decay` 等只保留兼容读取，不再作为新的业务真值。
5. **统一生命周期真值**：记忆生命周期统一由 `memory_status` 表达。
6. **统一用户隔离真值**：所有用户归属对象必须直接携带 `user_id`；`user_id` 不得由 LLM/模型生成。
7. **格式冻结不等于宿主能力验证**：字段格式可冻结，但 `HOST_VERIFIED` 仍必须由银河麒麟真实环境证据支持。

---

## 2. 权威性与分层边界

### 2.1 本规范负责冻结

- 字段命名；
- 字段业务语义；
- JSON 基础类型；
- required / optional / conditional；
- 枚举值；
- 时间格式；
- ID 规则；
- 空值规则；
- 跨字段不变量；
- 兼容和版本演进规则。

### 2.2 各层继续保留自己的物理真源

| 层 | 物理真源 | 与本规范关系 |
|---|---|---|
| 业务语义 | **本规范** | 新的跨轨统一业务字段基线 |
| Python Runtime | `memory-service/pipeline/schemas.py`、`memory-service/domain/*.py` | 必须对齐本规范 |
| SQLite | `memory-service/db/schema.py` | DB 物理 Schema 单一真相；字段语义必须对齐本规范 |
| Alembic | `migrations/versions/*.py` | 只负责物理迁移，不自行发明业务字段语义 |
| C++ Event | `os-agent-integration/contracts/memory_event_contract_v1.*` | 通过 Adapter 映射到本规范 |
| IPC | `deliverables/D4_IPC_PROTOCOL_FORMAL_FREEZE_20260817.md` + ADR | envelope/route 独立冻结；payload 业务字段必须映射本规范 |
| Retrieval | `memory-service/retrieval/contracts.py` | 只消费本规范已有业务字段，不创建第二套业务枚举 |

### 2.3 冲突处理优先级

若出现冲突：

1. **业务字段名称/含义/枚举冲突** → 以本规范为准；
2. **SQLite 列类型/索引/约束冲突** → 以 `db/schema.py` + 已批准 ADR 为物理真源，并提交 ADR 使其与本规范重新对齐；
3. **IPC envelope 冲突** → 以 FRZ-IPC 为准；
4. **宿主字段无法映射** → 不得猜测，标记 `BLOCKED_BY_HOST_MAPPING`；
5. **任何无法无损映射的差异** → 必须走 ADR，不得通过 Adapter 静默丢字段或改变语义。

---

## 3. 通用数据格式

### 3.1 编码

跨模块 JSON 数据统一：

```text
UTF-8 JSON
```

禁止把 Python repr、Qt 调试字符串、SQLite 自定义拼接文本作为跨模块正式协议。

### 3.2 命名

| 对象 | 规则 | 示例 |
|---|---|---|
| 业务对象 | PascalCase | `MemorySourceEvent` |
| JSON / Python 字段 | snake_case | `source_event_id` |
| C++ 成员 | lowerCamelCase | `sourceEventId` |
| 时间字段 | `*_at` | `created_at` |
| 标识字段 | `*_id` | `knowledge_id` |
| 布尔字段 | `is_` / `has_` / `should_` / `requires_` | `is_temporary` |
| 枚举字段 | `*_type` / `*_status` / `*_scope` / `*_mode` / `*_strategy` | `memory_status` |

禁止新增以下无业务语义字段：

```text
data
info
value1
value2
flag
flags
extra
extra_data
```

> IPC envelope 中已冻结的顶层 `data` 不受本条影响；本条仅约束业务对象内部字段。

### 3.3 字符串

- ID、枚举、required 文本字段必须是 JSON `string`；
- required 字符串不得为 `""` 或纯空白；
- 不使用字符串 `"null"`、`"None"`、`"unknown"` 代替缺失值；
- 枚举值大小写敏感，统一小写 `snake_case`。

### 3.4 数值

- integer 必须为 JSON integer 语义，不接受 `"123"` 字符串代替；
- boolean 不得按 integer 使用；
- 置信度统一为 strict float，范围：

```text
0.0 <= score <= 1.0
```

### 3.5 布尔

仅接受：

```json
true
false
```

不得接受：

```text
0 / 1
"true" / "false"
yes / no
```

作为业务 API 的等价输入。

SQLite 可使用 `0/1` 物理存储，但 Repository/Adapter 必须恢复为 boolean 语义。

### 3.6 时间

Canonical 时间统一使用带时区 ISO 8601 / RFC 3339 字符串。

写出时统一规范化为 UTC 毫秒：

```text
YYYY-MM-DDTHH:MM:SS.sssZ
```

示例：

```text
2026-09-03T08:30:12.315Z
```

要求：

- 禁止无时区时间作为跨模块 canonical 时间；
- 比较前统一转 UTC；
- SQLite 可存 TEXT，但必须保持上述 canonical 语义；
- `created_at`、`updated_at` 等系统时间不得由 LLM 生成。

### 3.7 ID

所有 `*_id`：

- 为 opaque string；
- 非空、非纯空白；
- 消费方不得依赖 ID 字符串前缀解析业务含义；
- `user_id`、宿主 `session_id`、宿主 `turn_id`、真实 `tool_call_id` 不得由 LLM 生成；
- DB 内部整数主键不直接替代跨模块业务 ID，除非已有正式 ADR 明确映射。

### 3.8 optional / null / 空集合

统一规则：

1. optional 字段没有值时，**canonical JSON 优先省略 key**；
2. 不用 `""` 表示缺失；
3. 只有物理 DB 明确 nullable 时才允许落库 `NULL`；
4. required list 语义允许“合法为空”时使用 `[]`；
5. `[]` 与“未提供字段”不是同义；
6. 涉及过滤范围时，空集合必须有明确确定性语义，不允许由 Provider 自行解释为“取消过滤”。

### 3.9 未知字段

Canonical Runtime 边界默认：

```text
extra = forbid
```

即：

- 未声明字段 → 拒绝；
- 不允许未知字段静默进入业务对象；
- C++/外部旧版本兼容层若采用“宽读”，必须在进入 Canonical Domain 前经过 Adapter 收敛；
- Adapter 不得把未知字段重新输出到 canonical 对象。

---

## 4. 版本规则

### 4.1 业务规范版本

本规范版本：

```text
KMA Canonical Business Schema v1.0
```

版本格式：

```text
MAJOR.MINOR
```

规则：

- 增加 optional 字段且不改变旧语义：MINOR；
- 新增枚举值若旧消费者可能 fail-close：至少需 ADR，并评估 MINOR/MAJOR；
- 删除字段、改类型、改变 required 性、改变空数组语义、改变枚举既有值语义：MAJOR；
- 字段改名视为删除旧字段 + 新增字段：MAJOR。

### 4.2 与既有 `schema_version` / `protocol_version` 的关系

三者不得混用：

| 名称 | 含义 |
|---|---|
| `KMA Canonical Business Schema v1.0` | 本文档定义的跨轨业务字段标准 |
| `schema_version` | 某个事件/对象 payload 自身结构版本 |
| `protocol_version` | D 轨 IPC envelope 协议版本 |

现有：

```text
event.ingest schema_version = "0.1"
IPC protocol_version = "1.0"
```

均继续有效。

**本规范不要求为了“统一数字”强行修改现有线上/候选接口版本。**
已有接口通过 Adapter 映射到 Canonical v1。

---

# 5. Canonical 枚举

以下值冻结，不得创建同义枚举。

## 5.1 SourceType

```text
chat
tool_result
manual_config
recollect
file
meeting
voice
```

## 5.2 EventType

```text
user_message
agent_response
system_message
```

## 5.3 SourceBusinessStatus

```text
raw
completed
success
partial
failed
cancelled
timeout
ignored
```

## 5.4 ProcessingStatus

```text
pending
extracting
extracted
embedded
stored
```

> 属内部处理状态，不得与来源执行结果 `source_business_status` 混用。

## 5.5 ConsentScope

```text
memory_only
memory_and_analytics
none
```

## 5.6 Sensitivity

```text
none
low
medium
high
critical
```

## 5.7 ExpressionType

```text
explicit
implicit
```

`candidate` 不属于 `expression_type`，候选状态由 `memory_status=candidate` 表达。

## 5.8 PreferenceScope

```text
global
topic
tool
session
time_window
```

## 5.9 KnowledgeType

```text
workflow
case
template
fact
constraint
failure_experience
```

`primary_category` 是开放分类标签，不得替代 `knowledge_type`。

## 5.10 MemoryType

```text
short_term
medium_term
long_term
ephemeral
```

## 5.11 MemoryStatus

```text
active
superseded
deprecated
expired
removed
candidate
```

该字段是记忆生命周期的 **唯一 canonical 真值**。

## 5.12 ConflictType

```text
contradiction
temporal_inconsistency
source_conflict
preference_conflict
scope_ambiguity
```

## 5.13 ResolutionStatus

```text
detected
analyzing
resolved_auto
resolved_manual
deferred
unresolvable
```

## 5.14 ForgetMode

```text
single_item
session
topic
time_window
full_reset
```

## 5.15 ForgetPlanStatus

```text
pending
previewing
awaiting_confirmation
executing
completed
failed
rolled_back
```

## 5.16 TargetType

```text
knowledge
preference
event
all
```

---

# 6. Canonical 对象

## 6.1 MemorySourceEvent

### 必填

| 字段 | 类型 | 约束 |
|---|---|---|
| `event_id` | string | 非空；事件身份 |
| `user_id` | string | 非空；用户隔离真值；禁止模型生成 |
| `actor_id` | string | 非空；实际发起者 |
| `source_type` | enum | SourceType |
| `schema_version` | string | 由具体事件入口契约规定 |
| `event_type` | enum | EventType |
| `idempotency_key` | string | 非空 |
| `occurred_at` | timestamp | 宿主实际发生时间 |
| `captured_at` | timestamp | 采集时间 |
| `session_id` | string | 非空；宿主来源 |

### 可选

| 字段 | 类型 | 约束 |
|---|---|---|
| `trace_id` | string | 调试/链路追踪引用 |
| `source_reference` | string | 受控引用，不承载正文 |
| `consent_scope` | enum | 默认由入口策略提供 |
| `source_business_status` | enum | 来源业务结果 |
| `memory_type` | enum | 无法判断时省略 |
| `raw_payload_ref` | string | 受控引用 |
| `content_summary` | string | 必须经过敏感过滤 |
| `turn_id` | string | 宿主 Turn 引用 |
| `tool_call_id` | string | Tool 事件时 conditional required |
| `sensitivity` | enum | 最终定级不得由 LLM 覆写 |
| `requires_embedding` | boolean | 是否需要 embedding |
| `has_structured_payload` | boolean | 是否存在结构化载荷 |
| `language_tag` | string | 建议 BCP 47 |

### 不作为 Canonical 外部输入真值

以下字段属于 Pipeline / Security / Persistence 派生状态，不允许外部调用者任意指定为最终真值：

```text
processing_status
is_sensitive_matched
should_ignore
payload_security_checked
content_fingerprint
dedup_group
duplicate_of
admission_decision
```

它们可以存在于内部 `NormalizedEvent` / DB 行，但不改变 `MemorySourceEvent` 的来源事实。

### 条件不变量

```text
source_type == tool_result
→ tool_call_id 必填
```

敏感/安全拒绝事件不得通过 deterministic hash 旁路泄露敏感正文身份。

---

## 6.2 Preference

### Canonical 必填

| 字段 | 类型 |
|---|---|
| `preference_id` | string |
| `user_id` | string |
| `expression_type` | ExpressionType |
| `preference_scope` | PreferenceScope |
| `preference_key` | string |
| `preference_value` | string |
| `confidence_score` | float [0,1] |
| `memory_status` | MemoryStatus |
| `is_temporary` | boolean |
| `should_persist` | boolean |
| `evidence_event_ids` | list[string], 非空 |
| `version` | integer >= 1 |
| `created_at` | timestamp |
| `updated_at` | timestamp |
| `requires_confirmation` | boolean |

### 可选

```text
decay_after_at
previous_version_id
extracted_entities
```

### 版本不变量

```text
version == 1
→ previous_version_id 必须缺失

version > 1
→ previous_version_id 必填
```

### 临时偏好不变量

```text
is_temporary == true
或 should_persist == false
→ memory_status 只能是 candidate / expired
```

### 时间不变量

```text
updated_at >= created_at
```

### 兼容字段

以下字段不再作为 Canonical 真值：

```text
is_active
should_decay
```

规则：

- 允许旧模型/旧 DB Adapter 读取；
- 新业务逻辑不得以它们代替 `memory_status`；
- 不得在新接口继续扩散；
- 后续完成兼容迁移后删除。

---

## 6.3 Knowledge

### Canonical 必填

| 字段 | 类型 |
|---|---|
| `knowledge_id` | string |
| `user_id` | string |
| `knowledge_type` | KnowledgeType |
| `memory_type` | MemoryType |
| `memory_status` | MemoryStatus |
| `source_event_id` | string |
| `content_summary` | string |
| `confidence_score` | float [0,1] |
| `requires_embedding` | boolean |
| `created_at` | timestamp |
| `updated_at` | timestamp |

### 通用可选

```text
content_ref
primary_category
language_tag
superseded_by_id
access_count
last_accessed_at
extracted_entities
conditions
evidence
```

### 六类结构化字段

```text
workflow:
  steps
  expected_result

case:
  problem
  outcome
  reproducible

template:
  template_body
  parameters

constraint:
  priority

failure_experience:
  failure_reason
  avoid_condition
  alternative
```

这些字段均为 optional，不允许为了“字段齐全”用空字符串伪造。

### 不变量

```text
updated_at >= created_at

last_accessed_at 存在时
→ last_accessed_at >= created_at
```

### 兼容字段

```text
is_outdated
```

不再作为 lifecycle 真值；统一由 `memory_status` 表达。

---

## 6.4 Conflict

### 必填

| 字段 | 类型 |
|---|---|
| `conflict_id` | string |
| `user_id` | string |
| `conflict_type` | ConflictType |
| `left_knowledge_id` | string |
| `right_knowledge_id` | string |
| `conflict_summary` | string |
| `resolution_status` | ResolutionStatus |
| `is_auto_resolvable` | boolean |
| `detected_at` | timestamp |

### 可选

```text
involved_knowledge_ids
resolution_strategy
resolution_confidence
resolved_at
resolved_by
```

### 不变量

```text
left_knowledge_id != right_knowledge_id
```

```text
resolution_status in {resolved_auto, resolved_manual}
→ resolved_at 必填
→ resolved_by 必填
```

```text
resolved_at 存在时
→ resolved_at >= detected_at
```

冲突检测阈值、相似度算法不属于 Schema，不在本文冻结。

---

## 6.5 ForgetPlan

### 必填

| 字段 | 类型 |
|---|---|
| `forget_plan_id` | string |
| `user_id` | string |
| `forget_mode` | ForgetMode |
| `target_selector` | string |
| `target_type` | TargetType |
| `status` | ForgetPlanStatus |
| `is_cascade` | boolean |
| `has_vector_cleanup` | boolean |
| `requires_confirmation` | boolean |
| `created_at` | timestamp |

### 可选 / 条件

```text
resolved_target_ids
target_id
target_session_id
target_topic
target_time_range
executed_at
affected_count
rollback_plan_id
```

### 模式不变量

```text
single_item → 仅 target_id
session     → 仅 target_session_id
topic       → 仅 target_topic
time_window → 仅 target_time_range
full_reset  → 不允许具体 selector 字段
```

### 预览结果不变量

```text
resolved_target_ids 存在
→ affected_count 必填
→ resolved_target_ids 不得重复
→ affected_count == len(resolved_target_ids)
```

### 执行状态不变量

```text
status in {completed, failed, rolled_back}
→ executed_at 必填
```

```text
executed_at 存在
→ executed_at >= created_at
```

Forget Preview / Execute 的 confirmation credential、hash、TTL、`delete_mode` 属 D 轨执行/IPC 持久化契约，不作为通用业务对象自由输入字段。

---

# 7. 字段真值与禁止重复建模

以下语义冻结为单一字段：

| 语义 | Canonical 字段 | 禁止新增/继续作为真值 |
|---|---|---|
| 用户归属 | `user_id` | 从正文/LLM 推断 owner |
| 生命周期 | `memory_status` | `is_active` / `is_outdated` / `should_decay` |
| 知识类型 | `knowledge_type` | 用 `primary_category` 替代 |
| 偏好表达来源 | `expression_type` | 把 `candidate` 当 expression type |
| 事件来源 | `source_type` | 把 `event_type` 当来源类别 |
| 事件消息角色 | `event_type` | 把 `source_type` 当消息角色 |
| 来源业务结果 | `source_business_status` | 用 `processing_status` 代替 |
| 内部处理阶段 | `processing_status` | 用 Tool success/failure 代替 |
| Tool 身份 | `tool_call_id` | 模型文本推断出的 Tool ID |
| 事件身份 | `event_id` | 用幂等键代替 |
| 幂等身份 | `idempotency_key` | 用 event_id 代替 |

---

# 8. Adapter 规则

Adapter 的职责是 **表示转换，不是业务重解释**。

允许：

```text
QString ↔ string
QDateTime ↔ canonical UTC timestamp
SQLite INTEGER 0/1 ↔ boolean
DB internal integer id ↔ 已批准的 canonical ID 映射
legacy event.ingest 0.1 ↔ Canonical v1 业务字段
```

禁止：

- 自动把未知枚举降级成某个已知枚举；
- 缺 `user_id` 时从正文猜测；
- 缺 required ID 时自动生成并冒充宿主 ID；
- 空数组自动解释为“取消过滤”；
- 用 `is_active` 覆盖 `memory_status`；
- 把失败 Tool 结果映射成成功知识；
- 丢弃无法映射字段后仍报告转换成功。

无法无损映射时：

```text
FAIL-CLOSED
→ INVALID_REQUEST / CONTRACT_MISMATCH / BLOCKED_BY_HOST_MAPPING
```

具体错误码按所在层冻结契约映射。

---

# 9. Runtime 校验最低要求

所有进入 Canonical Domain 的对象至少校验：

1. required 字段存在；
2. strict 基础类型；
3. 非空字符串；
4. 枚举合法；
5. float 范围；
6. timestamp 带时区；
7. unknown field fail-close；
8. 用户隔离字段存在；
9. conditional 字段满足；
10. 跨字段不变量满足。

Python 推荐继续使用：

```text
Pydantic v2
ConfigDict(extra="forbid")
Field(...)
field_validator
model_validator
```

C++ 必须提供等价校验，不得只依赖 Qt 默认值。

SQLite CHECK/UNIQUE/Trigger 是最后一道持久化防线，但不能替代 Domain 校验。

---

# 10. Schema 漂移 Gate

建议新增一个确定性 L0 Gate，对以下来源做字段矩阵比较：

```text
Canonical Freeze Doc
        ↓
Pydantic Domain
        ↓
DB schema.py
        ↓
IPC / C++ Adapter
```

至少检查：

- 字段名；
- required/optional；
- enum；
- 基础类型；
- nullable；
- 生命周期字段；
- 用户隔离字段；
- 时间字段；
- deprecated 字段是否重新扩散。

出现差异：

```text
CONTRACT_DRIFT
```

默认阻断合并，除非 PR 同时包含获批 ADR。

---

# 11. 过渡与迁移策略

## Phase 1：立即生效

- 新代码、新接口、新测试统一引用本规范；
- 禁止新增第二套业务枚举；
- 新逻辑以 `memory_status` 为生命周期真值；
- PR Review 增加 Schema Drift 检查。

## Phase 2：兼容收口

逐步清理：

```text
Preference.is_active
Preference.should_decay
Knowledge.is_outdated
```

在删除前：

- 保留旧数据读取 Adapter；
- 写路径不再产生新依赖；
- 增回归测试证明 `memory_status` 可独立表达业务状态。

## Phase 3：机器可读 Schema Registry

后续可从现有 Pydantic 模型生成或维护：

```text
contracts/schema/
  memory_source_event.v1.schema.json
  preference.v1.schema.json
  knowledge.v1.schema.json
  conflict.v1.schema.json
  forget_plan.v1.schema.json
```

JSON Schema 是本规范的机器可读投影，**不得反过来未经 Review 改变本文业务语义**。

---

# 12. 变更控制

本规范生效后，下列改动必须 ADR + D/E 交叉 Review：

- 删除字段；
- 改字段名；
- 改字段类型；
- required ↔ optional；
- 修改 enum；
- 修改空数组语义；
- 修改 `user_id` 隔离语义；
- 修改 `memory_status` 生命周期语义；
- 修改 ID 真值来源；
- 修改时间 canonical 规则；
- 新建已有字段可表达的同义字段。

仅以下情况可作为兼容 MINOR 更新：

- 增加完全 optional 且旧消费者可安全忽略的字段；
- 增加说明、示例、映射文档；
- 增加不改变既有合法数据集合的更明确校验说明。

---

# 13. Reviewer Freeze Checklist

正式转 `FROZEN` 前确认：

- [ ] D Reviewer 确认与 DB / IPC 冻结无不可实现冲突
- [ ] E Reviewer 确认业务字段语义、枚举和生命周期
- [ ] A 确认 `MemorySourceEvent` / Candidate 输入可映射
- [ ] B 确认 Retrieval 不再创建第二套枚举
- [ ] C 确认 C++ Event 可通过 Adapter 无损映射
- [ ] `db/schema.py` 现有关键 CHECK 与 canonical enum 对齐
- [ ] 过渡字段已明确标记，不再作为新业务真值
- [ ] `schema_version` 与 `protocol_version` 未混用
- [ ] 无任何 `HOST_VERIFIED` 能力被本格式冻结文档虚构升级

---

# 14. 签署

| 角色 | 结论 | 日期 |
|---|---|---|
| 规范提出 | 待填写 | |
| D Reviewer | 待签署 | |
| E Reviewer | 待签署 | |

签署并合并 `main` 后：

```text
STATUS: FROZEN
SCHEMA: KMA Canonical Business Schema v1.0
```

之后所有跨轨共享字段以本文为统一业务语义基线；层级物理契约通过 Adapter 与本文对齐。
