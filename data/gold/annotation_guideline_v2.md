# 麒麟 OS Memory Gold 标注手册 v2（KMA 对齐，P1 定稿版）

- 角色：Annotator A（lyf-1213）· 阶段8 v2
- 分支：`feat/A-stage8-p1-2-3`（P1-2 批次）
- 日期：2026-09-03（起草）；2026-09-04（按 Reviewer 裁定 #1-#4 落点）；2026-09-04（P1-2 定稿）
- 依据：`reports/stage8_kma_gold_annotation_draft_A.md`（六类口径）、KMA 权威候选 `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md`、D9 检索集、Reviewer 裁定 `worklog/20260904_KMA_FROZEN_adjudications_1_4_R.md`（#1-#4、#9、#10）、B 复核意见
- 性质：**P1 定稿版**（本仓库 #7 KMA→FROZEN 认定达成，df8cdf6；§3-§11 已按裁定固定；本文为阶段8 v2 现行标注标准，替代 v1.x 标注手册的旧枚举口径）
- **版本互指（Reviewer Low-1）**：v2 定稿后阶段8 试标/标注以本 v2 为准；v1.3（`data/gold/annotation_guideline.md`）仅作旧口径回溯参考。

---

## 0. 核心原则

1. **标签必须能从 input/evidence 直接推导**，禁止无证据猜测。
2. **禁 mock**：封存集必须来自麒麟 VM 真实回放（Tool Result / 端到端尤其）。
3. **先标后产**：试标 Kappa≥0.70 后量产；未达标修订并回溯。
4. **双人独立**：A/B 独立标注，脚本只算一致性；Reviewer 裁决。
5. **gold 业务字段对齐 KMA**：枚举用 KMA §5；生命周期用 `memory_status`；`review_status` 仅评测标签审阅。

---

## 1. review_status 与 memory_status 职责分离（专节）

| 字段 | 职责 | 取值 | 谁决定 |
| --- | --- | --- | --- |
| `review_status` | 评测标签审阅状态（数据包层） | `candidate_only` / `approved` / `rejected` | 标注者→Reviewer |
| `memory_status` | 业务记忆生命周期真值（gold 内） | `active`/`superseded`/`deprecated`/`expired`/`removed`/`candidate` | 标注者按 KMA §5.11 |

**铁律**：
- 评测标签从 `candidate_only` → `approved` 由 Reviewer 裁决，表达"这条标签可进封存"，**不表达**业务记忆该不该存在。
- 业务记忆该不该存在（生命周期）只能由 `gold.memory_status` 表达。
- 禁止用 `review_status` 代替 `memory_status` 判断遗忘/过期/替代等业务语义。

---

## 2. 统一样本骨架（六类任务通用）

```json
{
  "sample_id": "pref_000001",
  "dataset_version": "kylin_memory_gold_v1.0",
  "task_type": "preference_extraction",
  "language": "zh-CN",
  "user_id": "u_...",
  "conversation_id": "conv_...",
  "created_at": "2026-09-03T08:30:12.315Z",
  "updated_at": "2026-09-03T09:00:00.315Z",
  "input": {},
  "gold": {
    "...": "KMA canonical 业务字段（见 §3~§8）"
  },
  "evidence": [{"source_event_id": "...", "span": "...", "source_type": "utterance|raw_record"}],
  "source": "team_authored | public_derived | runtime_replay",
  "template_family": "...",
  "annotator_a": "A",
  "annotator_b": "B",
  "review_status": "candidate_only"
}
```

- 时间字段统一 `created_at/updated_at`，UTC 毫秒 `YYYY-MM-DDTHH:MM:SS.sssZ`。
- `sample_id` 前缀为评测层标识（pref_/retr_/conf_/forg_/tool_/e2e_），非业务 ID。

---

## 3. 偏好提取（Preference）

| 字段 | 枚举/规则 |
| --- | --- |
| expression_type | `explicit` / `implicit` |
| preference_scope | `global` / `topic` / `tool` / `session` / `time_window`（对照表见下） |
| preference_key | **受控开放字符串** `prefix[:object]`（Reviewer #1 裁定：前缀=受控词表 output_style/tool_choice/safety/app/workflow/other；object=小写 snake_case ≤32 字符可空） |
| preference_value | 可执行、可比较字符串 |
| confidence_score | float [0,1]（档位表见下，Reviewer #3 裁定） |
| should_persist | boolean |
| is_temporary | boolean |
| memory_status | 6 值 |
| version | int>=1（>1 必带 previous_version_id） |
| evidence_event_ids | list 非空 |

### preference_key 规则（Reviewer #1 裁定，2026-09-04）
- 格式：`preference_key := <prefix>[:<object>]`；前缀为受控词表（沿用旧模板族），`object` 开放短标识（小写 snake_case，≤32 字符，可空）。
- 示例：`output_style:report`、`tool_choice:delete_confirm`、`app:project_mgmt_lang`。
- **不造第二套枚举**（KMA §7）；`preference_key`=匹配键、`preference_value`=完整值。
- Kappa 一致判定：按 `preference_key` 全串精确比对（已纳入 `registry/kappa_agreement_fields.json`）。

### preference_scope 对照表（Reviewer #2 裁定）
| 旧 scope | 语义 | KMA preference_scope | 样例 |
| --- | --- | --- | --- |
| app | 针对具体工具/应用的行为 | `tool` | "项目管理工具里用中文标签"→tool |
| app | 麒麟 OS 助手作为系统整体 | `global` | "以后都先问我确认"→global |
| task | 针对某类工作主题 | `topic` | "做周报时用简洁要点"→topic |
| task | 针对工具行为的任务 | `tool` | "发邮件时带签名 X"→tool |
| session | 仅本次会话 | `session` | "这次用英文回复"→session |
| global | 全局习惯 | `global` | 一致 |
| — | 时间窗 | `time_window` | "会议期间勿扰"→time_window |

**判定顺序**：先判"是否系统整体(global)/仅本次(session)/时间窗(time_window)"，再按"具体工具→tool、工作主题→topic"细分。

### confidence_score 档位表（Reviewer #3 裁定）
| 旧 | 语义 | confidence_score | 可选中间档 |
| --- | --- | --- | --- |
| high | 显式、无需推断 | 0.95 | 0.85（显式有歧义） |
| medium | 多句/行为推断 | 0.70 | 0.75（两次一致行为）/0.60（单次行为） |
| low | 模糊、低证据 | 0.40 | 0.30~0.40（极弱） |

- **默认只用三档**（0.95/0.70/0.40）保 A/B 一致；中间档仅当本表明示时使用。
- 换算只在标注/转换映射层；`gold.confidence_score` 直接写数值。

判定参考（映射自旧口径，按裁定定稿）：
- "以后都这样"→ explicit、should_persist=true、confidence_score=0.95、active
- "这次/仅本次"→ is_temporary=true、should_persist=false、candidate
- "之前…改成…"→ 新 version（previous_version_id 指向旧版）
- "不要了"→ 旧版 superseded
- 敏感 → should_persist=false、candidate

## 4. 知识检索（Knowledge）

| 字段 | 枚举/规则 |
| --- | --- |
| knowledge_type | `workflow`/`case`/`template`/`fact`/`constraint`/`failure_experience` |
| knowledge_id | opaque string |
| memory_status | 6 值 |
| superseded_by_id | optional |
| 版本引用 | memory_id + version_id |
| 禁止召回 8 类 | superseded/expired/removed_or_forgotten/candidate/unresolved_conflict/cross_user/sensitive_recall_prohibited/deprecated |

判定（Reviewer #4.3 裁定：采用 D9 口径）：
- 正解 = 同用户 **active 当前版本**（memory_id+version_id 版本级引用）；
- superseded 旧版（非当前）→ **forbidden（禁止召回）**；
- 语义近似当前版 → **semantic_near_miss**（不计 guardrail violation）；
- evaluation_role = positive_retrieval / negative_guardrail；每条带 rationale。

> ⚠ **风险注（P2）**：检索 v2 依赖知识库（KB）与 D9 检索集（`memory_id+version_id` 版本引用）。当前无 KB、试标池多为 public t2r（`retr_t2r_*`）。**KB/D9 就绪前，检索 v2 部分（版本引用/禁止召回 8 类/semantic_near_miss/rationale/evaluation_role）不可完整执行**；相关字段显式标评测层（NOT production，见 §9.1），待 KB/D9 就绪后补齐。

## 5. 冲突处理（Conflict）

| 字段 | 枚举/规则 |
| --- | --- |
| conflict_type | `contradiction`/`temporal_inconsistency`/`source_conflict`/`preference_conflict`/`scope_ambiguity` |
| resolution_status | `detected`/`analyzing`/`resolved_auto`/`resolved_manual`/`deferred`/`unresolvable` |
| left_knowledge_id / right_knowledge_id | 冲突双方（left≠right） |
| involved_knowledge_ids | optional |
| resolution_strategy | optional |

判定（Reviewer #4.2 裁定，2026-09-04）：
- **时间先后更新**（新覆盖旧，明确先后）→ `temporal_inconsistency`
- **同层矛盾**（不可同时为真，需裁决取舍）→ `contradiction`
- 作用域 → `scope_ambiguity`；来源 → `source_conflict`；安全 → 安全优先
- **能由版本链消解的**（superseded + version_id）→ 用版本/生命周期表达，不进 conflict 标签；conflict 用于"需在两条冲突信息间裁决"的样本
- 口诀：先后更新→temporal_inconsistency；同时矛盾→contradiction；版本链可消解→superseded/version。

## 6. 精准遗忘（ForgetPlan）

| 字段 | 枚举/规则 |
| --- | --- |
| forget_mode | `single_item`/`session`/`topic`/`time_window`/`full_reset` |
| target_type | `knowledge`/`preference`/`event`/`all` |
| target_selector | 模式不变量约束 |
| status | `pending`/`previewing`/`awaiting_confirmation`/`executing`/`completed`/`failed`/`rolled_back` |
| is_cascade | boolean |
| has_vector_cleanup / requires_confirmation | boolean（**DEFERRED：不新增为业务真值**，评测层可选、不进业务 canonical，见 §9.1） |
| resolved_target_ids + affected_count | preview 结果 |

判定（Reviewer #4.1 裁定）：
- target_selector 按 forget_mode；
- **checkpoints = 评测层验证时点**（immediate_query/after_restart/after_full_reindex），**不进业务状态**；业务状态用 `ForgetPlan.status`/`memory_status` 表达；gold 中 checkpoints 留在评测层字段，不写入 canonical 业务状态。

## 7. Tool Result（MemorySourceEvent）

| 字段 | 枚举/规则 |
| --- | --- |
| source_business_status | `raw`/`completed`/`success`/`partial`/`failed`/`cancelled`/`timeout`/`ignored` |
| tool_call_id | 必填（tool_result 条件不变量） |
| source_type | `tool_result` |
| content_summary | 敏感过滤后摘要 |
| sensitivity | `none`/`low`/`medium`/`high`/`critical`（**R-5 FROZEN，#10 裁定**：事件层敏感样本必填，非敏感可空） |

判定：failed 不得写成成功；cancelled 禁止推断副作用；timeout 标未知；partial 拆分。

## 8. 端到端会话（MemorySourceEvent 链）

| 字段 | 枚举/规则 |
| --- | --- |
| expected_memory | 生命周期对齐 memory_status + memory_type |
| expected_response | 评测层字段（KMA 不冻结） |
| sensitivity | `none`/`low`/`medium`/`high`/`critical`（**R-5 FROZEN，#10 裁定**：事件层敏感样本必填，非敏感可空） |

## 9. 试标与一致性

- 试标 30~50 条/人，Kappa≥0.70（总体 + 每任务分层）。
- **一致字段集单一来源（P1-1）**：以 `registry/kappa_agreement_fields.json` 的 `kappa_agreement_fields` 为准；本手册与 `scripts/audit/stage8_kappa.py`（`--fields-json registry/kappa_agreement_fields.json`）共同引用，**禁止在手册/脚本各自维护第二套**（防字段漂移）。
  - preference_extraction：`expression_type, preference_scope, should_persist, is_temporary, memory_status`
  - knowledge_retrieval：`evaluation_role, knowledge_type, memory_status`
  - conflict_resolution：`conflict_type, resolution_status`
  - precise_forgetting：`forget_mode, target_type, status`
  - tool_result：`source_business_status`
  - end_to_end_session：`expected_response`（语义等价）
- A/B 标签文件：`labels_A/B_trial.jsonl`（sample_id/task_type/gold/evidence）。

### 9.1 评测层与业务层字段边界（P2）

- `relevant_ids / hard_negative_ids / semantic_near_miss_refs / rationale / expected_answer_points / checkpoints / expected_deleted / must_keep / persist_policy / side_effect / failure_reason / expected_response / expected_memory` 均为**评测层字段**（评测层边界登记见 B 侧 `registry/field_mapping.json`），**NOT production**，KMA 不冻结。
- `has_vector_cleanup / requires_confirmation`：漂移任务已注明 **DEFERRED，不新增为业务真值**；评测层可选、不进业务 canonical（见 B 侧 `registry/field_mapping.json`）。
- `semantic_near_miss_refs / rationale / evaluation_role`：显式标**评测层（NOT production）**。

### 9.2 evidence.source_type 映射（P2）

- 评测层 `source_type=utterance/raw_record` 与 KMA SourceType 不同名：
  - `utterance` → 对应 KMA `SourceType=chat`（对话事件）；
  - `raw_record` → 评测来源层标注（public_derived 原始记录），非 KMA SourceType，仅评测内部使用。
  - 映射登记见 B 侧 `registry/field_mapping.json` 的 `source_type_mapping`。

## 10. 质量检查清单

- [ ] 任务一致性
- [ ] 证据完整性（span 可溯源原话/raw）
- [ ] 边界清晰度（temporary vs long-term）
- [ ] 冲突可判定（有时间/来源/作用域信息）
- [ ] 负样本可信（禁召回类别正确）
- [ ] 遗忘可验证（删对+不误删）
- [ ] memory_status 与 review_status 不混用

## 11. 裁定记录（Reviewer gaoyizhe，2026-09-04，见 worklog/20260904_KMA_FROZEN_adjudications_1_4_R.md）

1. **preference_key 取值策略（#1）**：✅ 已裁定——受控开放字符串 `prefix[:object]`，Kappa 全串比对（§3）
2. **app/task 语义落点（#2）**：✅ 已裁定——语义映射固定对照表（§3 preference_scope 对照表）
3. **confidence 换算口径（#3）**：✅ 已裁定——三档主表 0.95/0.70/0.40 + 受控中间档（§3 confidence_score 档位表）
4. **checkpoints 评测层定位（#4.1）**：✅ 已裁定——评测层验证时点，不进业务状态（§6）
5. **版本冲突 conflict_type 落点（#4.2）**：✅ 已裁定——先后→temporal_inconsistency；同时→contradiction；版本链可消解→superseded/version（§5）
6. **retrieval 版本引用 D9（#4.3）**：✅ 已裁定——采用 D9 口径（§4）
7. **preference_scope/conflict_type 来源（#9）**：✅ D3(L2) 核对 + D/E 盖章（见 reports/stage8_frozen_items_9_12_B.md）
8. **sensitivity 收口（#10，R-5）**：✅ 已裁定（2026-09-04，B 侧 P1-1 对齐 + 本手册 §7/§8）——tool_result/e2e 事件层敏感样本 `gold.sensitivity` 必填（五级枚举），非敏感可空；knowledge_retrieval 不补；preference 敏感沿用 should_store=false+memory_status=candidate+safety（可选标 sensitivity）
9. **KMA FROZEN（#7）**：✅ 本仓库 #27 已认定 FROZEN（2026-09-04，D/E 联合授权 + 主仓库 PR#137 合并；schema kma_alignment.status=FROZEN）；主仓库在线文档仍 CANDIDATE_FOR_FREEZE（差异协调中，以本仓库认定推进 P1）

## 12. A 不越权声明
- 本文为 P1-2 定稿版；P1-1 收口（schema/enum/sensitivity）已完成；后续 P1-3 全量重转由 A 执行（禁 mock）、P1-4 骨架由 B 生成、P1-5 试标 A/B 独立、P1-6 Kappa 由 B 计算，均按 P1 工作流批次纪律推进。
