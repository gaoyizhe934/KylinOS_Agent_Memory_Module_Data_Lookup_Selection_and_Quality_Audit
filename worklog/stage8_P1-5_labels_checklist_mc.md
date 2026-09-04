# 40 条标定核对表（选择题版 · Annotator A 自检）

- 用法：看每条"原话"→ 你手标时选一个答案 → 和右侧"AI 参考答案"比对 → 一致=✓，不一致=✗（需要改）
- 判断题大多只有 2~3 个选项，一眼看清
- 核对完：`python scripts/audit/stage8_label_check_v2.py --labels data/interim/labels_A_trial_v2.jsonl --samples data/interim/stage8_trial_set_v2.jsonl` → exit 0

---

## 一、偏好提取（8 条）

### ① pref_000003 — "这次就按英文回复，不用记住"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 这次是长期还是临时？ | A.长期 B.临时 | __ | **B** |
| scope 填什么？ | A.session B.global C.tool | __ | **A session** |
| should_persist？ | A.true B.false | __ | **B false** |
| is_temporary？ | A.true B.false | __ | **A true** |
| memory_status？ | A.active B.candidate C.superseded | __ | **B candidate** |

### ② pref_000007 — "以后项目周报用简洁要点，每条不超过两行"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| "以后"长期还是临时？ | A.长期 B.临时 | __ | **A 长期** |
| scope 填什么？ | A.global B.topic C.tool D.session | __ | **B topic**（周报=主题） |
| should_persist？ | A.true B.false | __ | **A true** |
| memory_status？ | A.active B.candidate | __ | **A active** |
| version？ | A.1 B.2 | __ | **A 1** |

### ③ pref_000017 — "项目管理工具里一律用中文标签，其他工具保持英文"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 点名了工具，scope？ | A.global B.topic C.tool D.session | __ | **C tool** |
| preference_key？ | A.output_style B.app C.tool_choice | __ | **B app**（应用类偏好） |
| should_persist？ | A.true B.false | __ | **A true** |
| memory_status？ | A.active B.candidate | __ | **A active** |

### ④ pref_000023 —（同 017 原文）
> 直接复制 ③ 的答案：tool / app / true / active

### ⑤ pref_000039 — "这次就按英文回复，不用记住"
> 同 ①：B 临时 / session / false / true / candidate

### ⑥ pref_000052 — "之前说报告要详细，以后改成每节只写结论和关键数字"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| "之前…改成…"是什么操作？ | A.新建 B.更新 C.撤销 | __ | **B 更新** |
| version？ | A.1 B.2 | __ | **B 2** |
| previous_version_id？ | A.null B."v1" | __ | **B "v1"** |
| memory_status？ | A.active B.candidate | __ | **A active**（新值生效） |

### ⑦ pref_000055 — "以后项目周报用简洁要点"
> 同 ②：A 长期 / topic / true / active / 1

### ⑧ pref_000059 —（同 017 原文）
> 同 ③：tool / app / true / active

---

## 二、冲突处理（8 条）

### ① conf_000002 — "全局中文 vs 某应用要求英文"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 冲突类型？ | A.temporal_inconsistency B.source_conflict C.scope_ambiguity D.preference_conflict E.contradiction | __ | **C scope_ambiguity**（作用域冲突） |
| resolution_status？ | A.resolved_manual B.resolved_auto | __ | **A resolved_manual** |

### ② conf_000006 — "旧偏好回答详细 → 新偏好以后简短"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 冲突类型？ | A.temporal_inconsistency B.scope_ambiguity C.contradiction | __ | **A temporal_inconsistency**（先后更新） |

### ③ conf_000007 —（同 conf_000002）
> 同①：scope_ambiguity / resolved_manual

### ④ conf_000008 — "用户手动配置 vs 行为推断"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 冲突类型？ | A.temporal_inconsistency B.source_conflict C.scope_ambiguity | __ | **B source_conflict**（来源冲突） |

### ⑤ conf_000009 — "旧安装流程 vs 新版系统流程"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 冲突类型？ | A.contradiction B.temporal_inconsistency C.source_conflict | __ | **B temporal_inconsistency**（新旧版本） |

### ⑥ conf_000015 — "效率偏好跳过确认 vs 安全策略要求确认"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| 冲突类型？ | A.preference_conflict B.source_conflict C.contradiction | __ | **A preference_conflict**（偏好冲突） |

### ⑦ conf_000016 —（同 conf_000006）
> 同②：temporal_inconsistency

### ⑧ conf_000018 —（同 conf_000008）
> 同④：source_conflict

---

## 三、精准遗忘（8 条）

### ① forg_000006 — "删除上周临时记录的文件路径，保留本周的记录"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| forget_mode？ | A.single_item B.topic C.time_window D.session | __ | **C time_window**（"上周"=时间窗） |
| target_type？ | A.knowledge B.preference C.event | __ | **A knowledge**（路径记录） |

### ② forg_000007 — "忘记某个客户姓名的所有关联记录，但保留流程知识"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| forget_mode？ | A.single_item B.topic C.time_window | __ | **B topic**（客户主题） |
| target_type？ | A.knowledge B.preference | __ | **A knowledge**（关联记录） |

### ③ forg_000010/014/018/022 —（同 forg_000006 "删上周留本周"）
> 同①：time_window / knowledge

### ④ forg_000025 — "忘记我在 VSCode 中偏好深色主题，但保留其他开发偏好"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| forget_mode？ | A.single_item B.topic C.time_window | __ | **A single_item**（单条偏好） |
| target_type？ | A.knowledge B.preference | __ | **B preference**（主题偏好） |

### ⑤ forg_000040 — "撤回刚才设置的桌面布局偏好，恢复系统默认"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| forget_mode？ | A.single_item B.topic C.time_window | __ | **A single_item** |
| target_type？ | A.knowledge B.preference | __ | **B preference**（布局偏好） |

> 遗忘样本其余键统一：status=completed / is_cascade=false / has_vector_cleanup=null / requires_confirmation=false

---

## 四、知识检索（8 条）

### ① retr_000004 — "月度备份的流程模板是什么？"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| knowledge_type？ | A.workflow B.template C.case D.fact E.constraint F.failure_experience | __ | **B template**（模板） |
| evaluation_role？ | A.positive_retrieval B.negative_guardrail | __ | **A positive_retrieval** |

### ② retr_t2r_10015 — "雨什么时候念四声"（public_derived）
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| knowledge_type？ | A.workflow B.template C.fact D.case | __ | **C fact**（事实） |
| knowledge_id？ | A.10015 B.kb_template_024 | __ | **A 10015**（query_id） |
| source_type（evidence）？ | A.utterance B.raw_record | __ | **B raw_record** |

### ③ retr_t2r_10034/10044/10072/10138/1014/10151（7 条全同规则）
> 全部：fact / query_id / positive_retrieval / raw_record（knowledge_id=各自 query_id：10034、10044、10072、10138、1014、10151）

---

## 五、端到端会话（8 条）

### ① e2e_000001 — "帮我准备第 1 次项目发布检查" → 助手"先检查版本号、备份和发布清单"
| 判断 | 选项 | 你的答案 | AI 参考 |
|---|---|---|---|
| expected_response？ | A.先检查版本号、备份和发布清单 B.正在准备发布 | __ | **A**（抄助手原话） |
| sensitivity？ | A.none B.low C.medium D.high E.critical | __ | **A none**（无敏感） |

### ②~⑧ e2e_000002/004/007/010/012/013/015（内容全同，仅序号不同）
> 全部：expected_response="先检查版本号、备份和发布清单。" / sensitivity=none

---

## 六、evidence 核对（40 条通用）

| 类别 | source_event_id | span | source_type |
|---|---|---|---|
| 偏好 pref_* | 样本 id（如 pref_000007） | 抄原话片段 | utterance |
| 冲突 conf_* | 样本 id（如 conf_000006） | 抄 scenario | utterance |
| 遗忘 forg_* | 样本 id（如 forg_000025） | 抄 forget_instruction | utterance |
| 端到端 e2e_* | 样本 id（如 e2e_000001） | 抄"帮我准备项目发布检查" | utterance |
| 检索 retr_000004 | kb_template_024 | 抄 query | utterance |
| 检索 retr_t2r_* | query_id（如 10015） | 抄 query | **raw_record** |

---

## 结论判定

- **全部 ✓** → 保存 labels_A，跑校验 exit 0，交 B。
- **有 ✗** → 改回"AI 参考"的答案（或你有把握的更好判断），再跑校验。
- 拿不准的 → 报 sample_id + 你的选择，我帮你分析。