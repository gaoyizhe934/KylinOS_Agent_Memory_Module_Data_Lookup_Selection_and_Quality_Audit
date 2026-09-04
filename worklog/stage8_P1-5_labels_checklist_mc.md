# 40 条标定核对表（逐字段选择题版 · 完整）

- 用途：手标时**每个字段**逐项选择，与 AI 参考比对；全部 ✓ 后跑校验 exit 0。
- 核对：`python scripts/audit/stage8_label_check_v2.py --labels data/interim/labels_A_trial_v2.jsonl --samples data/interim/stage8_trial_set_v2.jsonl`
- 标注：每条「你的答案」填 A/B/C…；与「参考」列一致 = ✓

---

# 一、偏好提取（8 条 × 11 字段）

## 1.1 pref_000003 — "这次就按英文回复，不用记住"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | expression_type | A.explicit B.implicit | __ | **A explicit**（明说） |
| 2 | preference_scope | A.global B.topic C.tool D.session E.time_window | __ | **D session**（这次） |
| 3 | preference_key | A.output_style B.tool_choice C.safety D.app E.workflow F.other | __ | **A output_style** |
| 4 | preference_value | A.本次会话英文回复 B.以后都用英文 | __ | **A**（临时） |
| 5 | confidence_score | A.0.95 B.0.70 C.0.40 | __ | **A 0.95**（明说） |
| 6 | should_persist | A.true B.false | __ | **B false**（不用记住） |
| 7 | is_temporary | A.true B.false | __ | **A true** |
| 8 | memory_status | A.active B.superseded C.deprecated D.expired E.removed F.candidate | __ | **F candidate**（临时） |
| 9 | version | A.1 B.2 C.3 | __ | **A 1** |
| 10 | previous_version_id | A.null B."v1" | __ | **A null** |
| 11 | evidence_event_ids | A.["pref_000003"] B.[] | __ | **A** |

## 1.2 pref_000007 — "以后项目周报用简洁要点，每条不超过两行"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | expression_type | A.explicit B.implicit | __ | **A explicit** |
| 2 | preference_scope | A.global B.topic C.tool D.session E.time_window | __ | **B topic**（周报主题） |
| 3 | preference_key | A.output_style B.tool_choice C.safety D.app E.workflow F.other | __ | **A output_style** |
| 4 | preference_value | A.周报用简洁要点，每条<=2行 B.写周报 | __ | **A**（可执行） |
| 5 | confidence_score | A.0.95 B.0.70 C.0.40 | __ | **A 0.95** |
| 6 | should_persist | A.true B.false | __ | **A true**（以后） |
| 7 | is_temporary | A.true B.false | __ | **B false** |
| 8 | memory_status | A.active B.candidate C.superseded | __ | **A active**（长期） |
| 9 | version | A.1 B.2 | __ | **A 1** |
| 10 | previous_version_id | A.null B."v1" | __ | **A null** |
| 11 | evidence_event_ids | A.["pref_000007"] B.[] | __ | **A** |

## 1.3 pref_000017 — "项目管理工具里一律用中文标签，其他工具保持英文"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | expression_type | A.explicit B.implicit | __ | **A explicit** |
| 2 | preference_scope | A.global B.topic C.tool D.session E.time_window | __ | **C tool**（点名工具） |
| 3 | preference_key | A.output_style B.tool_choice C.safety D.app E.workflow F.other | __ | **D app**（应用偏好） |
| 4 | preference_value | A.项目管理工具用中文标签 B.用中文 | __ | **A**（可执行） |
| 5 | confidence_score | A.0.95 B.0.70 C.0.40 | __ | **A 0.95** |
| 6 | should_persist | A.true B.false | __ | **A true** |
| 7 | is_temporary | A.true B.false | __ | **B false** |
| 8 | memory_status | A.active B.candidate | __ | **A active** |
| 9 | version | A.1 B.2 | __ | **A 1** |
| 10 | previous_version_id | A.null B."v1" | __ | **A null** |
| 11 | evidence_event_ids | A.["pref_000017"] B.[] | __ | **A** |

## 1.4 pref_000023 —（原文同 1.3）
> 全部答案同 1.3，仅 evidence_event_ids 填 `["pref_000023"]`，evidence source_event_id=pref_000023

## 1.5 pref_000039 —（原文同 1.1 "这次就按英文回复，不用记住"）
> 全部答案同 1.1，仅 evidence_event_ids 填 `["pref_000039"]`

## 1.6 pref_000052 — "之前说报告要详细，以后改成每节只写结论和关键数字"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | expression_type | A.explicit B.implicit | __ | **A explicit** |
| 2 | preference_scope | A.global B.topic C.tool D.session E.time_window | __ | **B topic**（报告主题） |
| 3 | preference_key | A.output_style B.tool_choice C.safety D.app E.workflow F.other | __ | **A output_style** |
| 4 | preference_value | A.报告每节只写结论和关键数字 B.报告要详细 | __ | **A**（新值） |
| 5 | confidence_score | A.0.95 B.0.70 C.0.40 | __ | **A 0.95** |
| 6 | should_persist | A.true B.false | __ | **A true** |
| 7 | is_temporary | A.true B.false | __ | **B false** |
| 8 | memory_status | A.active B.candidate C.superseded | __ | **A active**（新值生效） |
| 9 | version | A.1 B.2 C.3 | __ | **B 2**（更新） |
| 10 | previous_version_id | A.null B."v1" | __ | **B "v1"** |
| 11 | evidence_event_ids | A.["pref_000052"] B.[] | __ | **A** |

## 1.7 pref_000055 —（原文同 1.2 "以后周报用简洁要点"）
> 全部答案同 1.2，仅 evidence_event_ids 填 `["pref_000055"]`

## 1.8 pref_000059 —（原文同 1.3 "项目管理工具用中文"）
> 全部答案同 1.3，仅 evidence_event_ids 填 `["pref_000059"]`

---

# 二、冲突处理（8 条 × 6 字段）

## 2.1 conf_000002 — "全局中文 vs 某应用要求英文"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | conflict_type | A.contradiction B.temporal_inconsistency C.source_conflict D.preference_conflict E.scope_ambiguity | __ | **E scope_ambiguity** |
| 2 | resolution_status | A.detected B.analyzing C.resolved_auto D.resolved_manual E.deferred F.unresolvable | __ | **D resolved_manual** |
| 3 | left_knowledge_id | A.old_mem B.new_cmd C.global D.app | __ | **A old_mem**（旧=全局） |
| 4 | right_knowledge_id | A.old_mem B.new_cmd | __ | **B new_cmd**（新=应用） |
| 5 | involved_knowledge_ids | A.[old_mem,new_cmd] B.[] | __ | **A** |
| 6 | resolution_strategy | A.manual B.auto | __ | **A manual** |

## 2.2 conf_000006 — "旧偏好回答详细 → 新偏好以后简短"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | conflict_type | A.contradiction B.temporal_inconsistency C.source_conflict D.preference_conflict E.scope_ambiguity | __ | **B temporal_inconsistency**（先后更新） |
| 2~6 | 其余字段 | 同 2.1（resolved_manual / old_mem / new_cmd / [old_mem,new_cmd] / manual） | __ | 同 2.1 |

## 2.3 conf_000007 —（同 2.1 场景）
> 同 2.1：scope_ambiguity / resolved_manual / old_mem / new_cmd

## 2.4 conf_000008 — "用户手动配置 vs 行为推断"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | conflict_type | A.contradiction B.temporal_inconsistency C.source_conflict D.preference_conflict E.scope_ambiguity | __ | **C source_conflict**（来源） |
| 2~6 | 其余 | 同 2.1 | __ | 同 2.1 |

## 2.5 conf_000009 — "旧安装流程 vs 新版系统流程"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | conflict_type | A.contradiction B.temporal_inconsistency C.source_conflict D.preference_conflict E.scope_ambiguity | __ | **B temporal_inconsistency**（新旧版本） |
| 2~6 | 其余 | 同 2.1 | __ | 同 2.1 |

## 2.6 conf_000015 — "效率偏好跳过确认 vs 安全策略要求确认"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | conflict_type | A.contradiction B.temporal_inconsistency C.source_conflict D.preference_conflict E.scope_ambiguity | __ | **D preference_conflict** |
| 2~6 | 其余 | 同 2.1 | __ | 同 2.1 |

## 2.7 conf_000016 —（同 2.2 场景）
> 同 2.2：temporal_inconsistency / 其余同 2.1

## 2.8 conf_000018 —（同 2.4 场景）
> 同 2.4：source_conflict / 其余同 2.1

---

# 三、精准遗忘（8 条 × 9 字段）

## 3.1 forg_000006 — "删除上周临时记录的文件路径，保留本周的记录"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | forget_mode | A.single_item B.session C.topic D.time_window E.full_reset | __ | **D time_window**（上周） |
| 2 | target_type | A.knowledge B.preference C.event D.all | __ | **A knowledge**（路径记录） |
| 3 | target_selector | A.lastweek_temp_paths B.kb_path_009 | __ | **A lastweek_temp_paths** |
| 4 | status | A.pending B.previewing C.awaiting_confirmation D.executing E.completed F.failed G.rolled_back | __ | **E completed** |
| 5 | is_cascade | A.true B.false | __ | **B false** |
| 6 | has_vector_cleanup | A.true B.false C.null(DEFERRED) | __ | **C null** |
| 7 | requires_confirmation | A.true B.false | __ | **B false** |
| 8 | resolved_target_ids | A.[kb_path_009] B.[] | __ | **A** |
| 9 | affected_count | A.0 B.1 C.2 | __ | **B 1** |

## 3.2 forg_000007 — "忘记某个客户姓名的所有关联记录，但保留流程知识"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | forget_mode | A.single_item B.session C.topic D.time_window E.full_reset | __ | **C topic**（客户主题） |
| 2 | target_type | A.knowledge B.preference C.event D.all | __ | **A knowledge** |
| 3 | target_selector | A.customer_name B.kb_person_012 | __ | **A customer_name** |
| 4~7 | status/is_cascade/has_vector_cleanup/requires_confirmation | 同 3.1 | __ | completed/false/null/false |
| 8 | resolved_target_ids | A.[kb_person_012] B.[] | __ | **A** |
| 9 | affected_count | A.0 B.1 | __ | **B 1** |

## 3.3 forg_000010 / 014 / 018 / 022 —（原文同 3.1 "删上周留本周"）
> 全部同 3.1：time_window / knowledge / completed / [kb_path_009] / 1

## 3.4 forg_000025 — "忘记我在 VSCode 中偏好深色主题，但保留其他开发偏好"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | forget_mode | A.single_item B.session C.topic D.time_window E.full_reset | __ | **A single_item** |
| 2 | target_type | A.knowledge B.preference C.event D.all | __ | **B preference**（偏好） |
| 3 | target_selector | A.pref_ui_theme_001 B.vscode_theme | __ | **A pref_ui_theme_001** |
| 4~7 | 状态字段 | 同 3.1 | __ | completed/false/null/false |
| 8 | resolved_target_ids | A.[pref_ui_theme_001] B.[] | __ | **A** |
| 9 | affected_count | A.1 B.0 | __ | **A 1** |

## 3.5 forg_000040 — "撤回刚才设置的桌面布局偏好，恢复系统默认"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | forget_mode | A.single_item B.session C.topic D.time_window E.full_reset | __ | **A single_item** |
| 2 | target_type | A.knowledge B.preference C.event D.all | __ | **B preference** |
| 3 | target_selector | A.pref_ui_layout_021 B.desktop_layout | __ | **A pref_ui_layout_021** |
| 4~7 | 状态字段 | 同 3.1 | __ | completed/false/null/false |
| 8 | resolved_target_ids | A.[pref_ui_layout_021] B.[] | __ | **A** |
| 9 | affected_count | A.1 B.0 | __ | **A 1** |

---

# 四、知识检索（8 条 × 7 字段）

## 4.1 retr_000004 — "月度备份的流程模板是什么？"

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | knowledge_type | A.workflow B.case C.template D.fact E.constraint F.failure_experience | __ | **C template**（模板） |
| 2 | knowledge_id | A.kb_template_024 B.10015 | __ | **A kb_template_024** |
| 3 | memory_status | A.active B.superseded C.candidate | __ | **A active** |
| 4 | superseded_by_id | A.null B."v1" | __ | **A null** |
| 5 | retrieval_ref | A.null B.{memory_id,version_id} | __ | **A null**（KB 未就绪） |
| 6 | evaluation_role | A.positive_retrieval B.negative_guardrail | __ | **A positive_retrieval** |
| 7 | rationale | A.月度备份流程模板正解 B.（留空） | __ | **A** |

## 4.2~4.8 retr_t2r_10015/10034/10044/10072/10138/1014/10151 —（7 条全同规则，public_derived）

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | knowledge_type | A.workflow B.case C.template D.fact E.constraint F.failure_experience | __ | **D fact**（事实类） |
| 2 | knowledge_id | A.各 query_id B.kb_template_024 | __ | **A**（如 10015） |
| 3 | memory_status | A.active B.candidate | __ | **A active** |
| 4 | superseded_by_id | A.null B."v1" | __ | **A null** |
| 5 | retrieval_ref | A.null B.{memory_id,version_id} | __ | **A null** |
| 6 | evaluation_role | A.positive_retrieval B.negative_guardrail | __ | **A positive_retrieval** |
| 7 | rationale | A.公开检索正解：同用户 active 当前版本 B.（留空） | __ | **A** |

> knowledge_id 对应：10015、10034、10044、10072、10138、1014、10151（各自 query_id）

---

# 五、端到端会话（8 条 × 3 字段）

## 5.1~5.8 e2e_000001/002/004/007/010/012/013/015 —（8 条内容全同，仅序号不同）

| # | 字段 | 选项 | 你的答案 | 参考 |
|---|---|---|---|---|
| 1 | expected_memory | A.{release_workflow:version_check_backup_deploy, events:[release_check,backup,deploy]} B.{} | __ | **A** |
| 2 | expected_response | A.先检查版本号、备份和发布清单。 B.正在准备发布 | __ | **A**（抄助手原话） |
| 3 | sensitivity | A.none B.low C.medium D.high E.critical | __ | **A none** |

---

# 六、evidence（40 条通用，每条至少 1 条）

| 场景 | source_event_id 选项 | span 选项 | source_type 选项 |
|---|---|---|---|
| 偏好 pref_* | A.样本id（如 pref_000007） B.留空 | A.抄原话 B.留空 | A.utterance B.raw_record → **A utterance** |
| 冲突 conf_* | A.样本id B.留空 | A.抄 scenario B.留空 | A.utterance |
| 遗忘 forg_* | A.样本id B.留空 | A.抄 forget_instruction B.留空 | A.utterance |
| 端到端 e2e_* | A.样本id B.留空 | A.抄"帮我准备项目发布检查" B.留空 | A.utterance |
| 检索 retr_000004 | A.kb_template_024 B.留空 | A.抄 query B.留空 | A.utterance |
| 检索 retr_t2r_* | A.query_id B.留空 | A.抄 query B.留空 | **B raw_record** |

---

# 判定

- 全部 ✓ → 保存 labels_A，跑校验 exit 0，交 B。
- 有 ✗ → 改回参考答案（或你有把握的更好判断）。
- 拿不准 → 报 sample_id + 你的选择。
