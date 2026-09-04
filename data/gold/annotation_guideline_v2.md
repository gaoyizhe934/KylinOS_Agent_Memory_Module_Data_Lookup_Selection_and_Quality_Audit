# 麒麟 OS Memory Gold 标注手册 v2（KMA 对齐草案）

- 角色：Annotator A（lyf-1213）· 阶段8 v2
- 分支：`feat/B-stage8-kma`（PR #27）
- 日期：2026-09-03
- 依据：`reports/stage8_kma_gold_annotation_draft_A.md`（六类口径草案）、KMA 标准 `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md`、D9 检索集、B 复核意见
- 性质：**草案**；KMA=FREEZE_PROPOSAL，FROZEN 后据此定稿并重建 labels 骨架/试标/Kappa。本文替代 v1.x 标注手册的旧枚举口径。

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
| preference_scope | `global` / `topic` / `tool` / `session` / `time_window` |
| preference_key | 开放字符串（模板族约束，勿再造枚举；取值策略待裁定） |
| preference_value | 可执行、可比较字符串 |
| confidence_score | float [0,1] |
| should_persist | boolean |
| is_temporary | boolean |
| memory_status | 6 值 |
| version | int>=1（>1 必带 previous_version_id） |
| evidence_event_ids | list 非空 |

判定参考（映射自旧口径，FROZEN 后定稿）：
- "以后都这样"→ explicit、should_persist=true、confidence≈0.95、active
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

判定：正解=同用户 active 当前版本；旧版禁止召回；语义近似作 semantic_near_miss；evaluation_role（positive/negative_guardrail）；每条带 rationale。

## 5. 冲突处理（Conflict）

| 字段 | 枚举/规则 |
| --- | --- |
| conflict_type | `contradiction`/`temporal_inconsistency`/`source_conflict`/`preference_conflict`/`scope_ambiguity` |
| resolution_status | `detected`/`analyzing`/`resolved_auto`/`resolved_manual`/`deferred`/`unresolvable` |
| left_knowledge_id / right_knowledge_id | 冲突双方（left≠right） |
| involved_knowledge_ids | optional |
| resolution_strategy | optional |

判定：时间→temporal_inconsistency；作用域→scope_ambiguity；来源→source_conflict；安全→安全优先；版本→开放待裁定。

## 6. 精准遗忘（ForgetPlan）

| 字段 | 枚举/规则 |
| --- | --- |
| forget_mode | `single_item`/`session`/`topic`/`time_window`/`full_reset` |
| target_type | `knowledge`/`preference`/`event`/`all` |
| target_selector | 模式不变量约束 |
| status | `pending`/`previewing`/`awaiting_confirmation`/`executing`/`completed`/`failed`/`rolled_back` |
| is_cascade / has_vector_cleanup / requires_confirmation | boolean |
| resolved_target_ids + affected_count | preview 结果 |

判定：target_selector 按 forget_mode；checkpoints 保留评测层验证时点（不进业务状态，待裁定）。

## 7. Tool Result（MemorySourceEvent）

| 字段 | 枚举/规则 |
| --- | --- |
| source_business_status | `raw`/`completed`/`success`/`partial`/`failed`/`cancelled`/`timeout`/`ignored` |
| tool_call_id | 必填（tool_result 条件不变量） |
| source_type | `tool_result` |
| content_summary | 敏感过滤后摘要 |

判定：failed 不得写成成功；cancelled 禁止推断副作用；timeout 标未知；partial 拆分。

## 8. 端到端会话（MemorySourceEvent 链）

| 字段 | 枚举/规则 |
| --- | --- |
| expected_memory | 生命周期对齐 memory_status + memory_type |
| expected_response | 评测层字段（KMA 不冻结） |

## 9. 试标与一致性

- 试标 30~50 条/人，Kappa≥0.70（总体 + 每任务分层）。
- 一致字段集（B 侧 stage8_kappa 适配 canonical）：偏好取 expression_type+preference_scope+should_persist+memory_status；检索取 relevant_ids+hard_negative_ids（集合）；冲突取 conflict_type+resolution_status；遗忘取 target_type+target_selector；Tool 取 source_business_status；端到端取 expected_response 语义等价。
- A/B 标签文件：`labels_A/B_trial.jsonl`（sample_id/task_type/gold/evidence）。

## 10. 质量检查清单

- [ ] 任务一致性
- [ ] 证据完整性（span 可溯源原话/raw）
- [ ] 边界清晰度（temporary vs long-term）
- [ ] 冲突可判定（有时间/来源/作用域信息）
- [ ] 负样本可信（禁召回类别正确）
- [ ] 遗忘可验证（删对+不误删）
- [ ] memory_status 与 review_status 不混用

## 11. 争议/待裁定（交 Reviewer）

1. preference_key 取值策略（FROZEN 清单#1）
2. app/task 语义落点（清单#2）
3. confidence 换算口径（清单#3，换算表见 `worklog/20260903_KMA_confidence_scope_samples_A.md`）
4. checkpoints 评测层定位（清单#4）
5. 版本冲突 conflict_type 落点（与清单#4 一并）

## 12. A 不越权声明
- 本文为草案，未重转 processed、未建 labels 骨架、未改 kappa；供 A/B 对齐 + Reviewer 裁定。
