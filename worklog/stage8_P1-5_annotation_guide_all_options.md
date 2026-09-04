# 麒麟 OS Memory Gold 标定指南（全选项版）— P1-5

- 角色：Annotator A（lyf-1213）手标参考
- 依据：`data/processed/schema.json`（gold_enum_alignment）、`data/gold/annotation_guideline_v2.md`（P1 定稿）、KMA 权威候选
- 用途：40 条试标（5 任务 × 8）手标时对照全部可能取值；**只填值、不改键名**
- AI 参考版（标完比对用）：`worklog/stage8_P1-5_labels_A_reference_AI.jsonl`

---

## 0. 填写通用规则

1. **枚举键**：只能选下列表格中的值，禁止自造。
2. **开放键**（preference_value、target_selector、rationale、span）：写可执行/可溯源内容。
3. **evidence**：每条至少 1 项 `{source_event_id, span, source_type}`；span 抄 input 原话片段。
4. **提交前校验**：`python scripts/audit/stage8_label_check_v2.py --labels data/interim/labels_A_trial_v2.jsonl --samples data/interim/stage8_trial_set_v2.jsonl` → exit 0。

---

## 1. 偏好提取 preference_extraction（8 条）

### gold 键与全部可能取值

| 键 | 全部可能值 | 判定要点 |
| --- | --- | --- |
| `expression_type` | `explicit` / `implicit` | 明说=explicit；靠推断=implicit |
| `preference_scope` | `global` / `topic` / `tool` / `session` / `time_window` | 全局/主题/工具/本次/时间窗 |
| `preference_key` | 受控前缀：`output_style` / `tool_choice` / `safety` / `app` / `workflow` / `other`（可加 `[:object]`） | 模板族前缀 |
| `preference_value` | 开放字符串（可执行） | 记住什么，能执行能比较 |
| `confidence_score` | `0.95` / `0.70` / `0.40`（主表）；可选 `0.85/0.75/0.60/0.30` | high=0.95 / medium=0.70 / low=0.40 |
| `should_persist` | `true` / `false` | 长期记= true |
| `is_temporary` | `true` / `false` | "这次/仅本次"= true |
| `memory_status` | `active` / `superseded` / `deprecated` / `expired` / `removed` / `candidate` | 生命周期 |
| `version` | integer >= 1 | update=2（带 previous_version_id），create=1 |
| `previous_version_id` | string 或 null | version>1 必填 |
| `evidence_event_ids` | string[] | 溯源事件 id |

### 40 条中的偏好样本判定

| sample_id | 原文 | 应填（参考） |
| --- | --- | --- |
| pref_000003 | 这次就按英文回复，不用记住 | scope=session、should_persist=false、is_temporary=true、memory_status=candidate |
| pref_000007 | 以后项目周报用简洁要点 | scope=topic、should_persist=true、active |
| pref_000017 | 项目管理工具里用中文标签 | scope=tool、preference_key=app |
| pref_000023 | （同 017） | 同 017 |
| pref_000039 | 这次就按英文回复 | 同 003 |
| pref_000052 | 之前报告要详细→改成只写结论 | version=2、previous_version_id=v1 |
| pref_000055 | 以后项目周报用简洁要点 | 同 007 |
| pref_000059 | 项目管理工具里用中文标签 | 同 017 |

---

## 2. 冲突处理 conflict_resolution（8 条）

### gold 键与全部可能取值

| 键 | 全部可能值 | 判定要点 |
| --- | --- | --- |
| `conflict_type` | `contradiction` / `temporal_inconsistency` / `source_conflict` / `preference_conflict` / `scope_ambiguity` | 同时矛盾/先后更新/来源冲突/偏好冲突/作用域歧义 |
| `resolution_status` | `detected` / `analyzing` / `resolved_auto` / `resolved_manual` / `deferred` / `unresolvable` | 本批统一 resolved_manual |
| `left_knowledge_id` | 字符串（opaque） | 冲突一方（≠right） |
| `right_knowledge_id` | 字符串（opaque） | 冲突另一方 |
| `involved_knowledge_ids` | string[] | 涉及集合 |
| `resolution_strategy` | 开放字符串或空 | 裁定策略 |

### 40 条中的冲突样本判定

| sample_id | 场景 | conflict_type |
| --- | --- | --- |
| conf_000002 / 007 | 全局中文 vs 某应用英文 | `scope_ambiguity` |
| conf_000006 / 016 | 旧详细 → 新简短 | `temporal_inconsistency` |
| conf_000008 / 018 | 手动配置 vs 行为推断 | `source_conflict` |
| conf_000009 | 旧安装流程 vs 新系统流程 | `temporal_inconsistency` |
| conf_000015 | 效率跳过确认 vs 安全要求确认 | `preference_conflict` |

---

## 3. 精准遗忘 precise_forgetting（8 条）

### gold 键与全部可能取值

| 键 | 全部可能值 | 判定要点 |
| --- | --- | --- |
| `forget_mode` | `single_item` / `session` / `topic` / `time_window` / `full_reset` | 单条/会话/主题/时间窗/全清 |
| `target_type` | `knowledge` / `preference` / `event` / `all` | 删什么类型 |
| `target_selector` | 开放字符串/对象（按模式不变量） | 具体删哪个 |
| `status` | `pending` / `previewing` / `awaiting_confirmation` / `executing` / `completed` / `failed` / `rolled_back` | 本批统一 completed |
| `is_cascade` | `true` / `false` | 级联删 |
| `has_vector_cleanup` | `true` / `false` / null（DEFERRED） | 本批 null |
| `requires_confirmation` | `true` / `false` | 需确认 |
| `resolved_target_ids` | string[] | 实际删除对象 |
| `affected_count` | integer | = len(resolved_target_ids) |

### 40 条中的遗忘样本判定

| sample_id | 指令 | 判定 |
| --- | --- | --- |
| forg_000006/010/014/018/022 | 删上周临时记录，留本周 | forget_mode=time_window、target_type=knowledge、resolved=[kb_path_009] |
| forg_000007 | 忘客户姓名，留流程知识 | forget_mode=topic、target_type=knowledge、resolved=[kb_person_012] |
| forg_000025 | 忘VSCode深色主题，留其他偏好 | forget_mode=single_item、target_type=preference、resolved=[pref_ui_theme_001] |
| forg_000040 | 撤桌面布局偏好，恢复默认 | forget_mode=single_item、target_type=preference、resolved=[pref_ui_layout_021] |

---

## 4. 知识检索 knowledge_retrieval（8 条）

### gold 键与全部可能取值

| 键 | 全部可能值 | 判定要点 |
| --- | --- | --- |
| `knowledge_type` | `workflow` / `case` / `template` / `fact` / `constraint` / `failure_experience` | 流程/案例/模板/事实/约束/失败经验 |
| `knowledge_id` | 字符串（opaque） | 相关文档 id |
| `memory_status` | 6 值（同偏好） | 本批统一 active |
| `superseded_by_id` | string 或 null | 被替代 id |
| `retrieval_ref` | 对象 `{memory_id, version_id}` 或 null | D9 版本级引用（KB 就绪前 null） |
| `evaluation_role` | `positive_retrieval` / `negative_guardrail` | 正向/护栏 |
| `rationale` | 开放字符串 | 依据说明 |

### 40 条中的检索样本判定

| sample_id | 判定 |
| --- | --- |
| retr_000004 | knowledge_type=template、knowledge_id=kb_template_024、evaluation_role=positive_retrieval |
| retr_t2r_10015/10034/10044/10072/10138/1014/10151 | knowledge_type=fact、knowledge_id=query_id、evaluation_role=positive_retrieval |

---

## 5. 端到端会话 end_to_end_session（8 条）

### gold 键与全部可能取值

| 键 | 全部可能值 | 判定要点 |
| --- | --- | --- |
| `expected_memory` | 对象（可含 version/status/events） | 期望沉淀记忆 |
| `expected_response` | 开放字符串 | 期望回复 |
| `memory_status` | 6 值 | 生命周期 |
| `memory_type` | `short_term` / `medium_term` / `long_term` / `ephemeral` | 记忆时长类型 |
| `sensitivity` | `none` / `low` / `medium` / `high` / `critical` | 敏感级别（#10） |

### 40 条中的端到端样本判定
| sample_id | 判定 |
| --- | --- |
| e2e_000001/002/004/007/010/012/013/015 | expected_response="先检查版本号、备份和发布清单。"；sensitivity=none |

---

## 6. evidence 填写（全部 40 条）

| 场景 | source_type | source_event_id | span |
| --- | --- | --- | --- |
| team_authored | `utterance` | 样本 id 或 evt 编号 | input 原话片段 |
| public_derived（retr_t2r_*） | `raw_record` | query_id | query 原文 |

---

## 7. 比对说明

标完 40 条后，对照 AI 参考版 `worklog/stage8_P1-5_labels_A_reference_AI.jsonl` 逐条比对：
- 一致的 ✓；不一致的 → 看是"枚举选错"还是"value 措辞差异"（枚举错需改，措辞等价可保留）。
- 提交前务必跑 `stage8_label_check_v2.py` exit 0。
