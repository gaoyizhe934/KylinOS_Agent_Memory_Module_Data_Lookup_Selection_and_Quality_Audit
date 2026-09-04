# 阶段8 v2 试标 B 侧可检查草稿（40 条）— 填写原因/来源

说明：gold=候选基线(手册/裁定映射)取模板字段；null=条件可空/待KB；来源列给依据。最终标签须人工复核，A 独立标注。

### 1. conf_000002（conflict_resolution）
- input 摘要：{"conflict_type":"scope","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"全局中文 vs 某应用要求英文"}
  - conflict_type = "scope_ambiguity" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "scope_app_priority" ｜ 候选映射(手册/裁定)

### 2. conf_000006（conflict_resolution）
- input 摘要：{"conflict_type":"time_update","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"旧偏好“回答详细” → 新偏好“以后简短”"}
  - conflict_type = "temporal_inconsistency" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "keep_new_override" ｜ 候选映射(手册/裁定)

### 3. conf_000007（conflict_resolution）
- input 摘要：{"conflict_type":"scope","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"全局中文 vs 某应用要求英文"}
  - conflict_type = "scope_ambiguity" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "scope_app_priority" ｜ 候选映射(手册/裁定)

### 4. conf_000008（conflict_resolution）
- input 摘要：{"conflict_type":"source","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"用户手动配置 vs 行为推断"}
  - conflict_type = "source_conflict" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "explicit_config_priority" ｜ 候选映射(手册/裁定)

### 5. conf_000009（conflict_resolution）
- input 摘要：{"conflict_type":"knowledge_version","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"旧安装流程 vs 新版系统流程"}
  - conflict_type = "temporal_inconsistency" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "version_keep_new" ｜ 候选映射(手册/裁定)

### 6. conf_000015（conflict_resolution）
- input 摘要：{"conflict_type":"safety","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"效率偏好跳过确认 vs 安全策略要求确认"}
  - conflict_type = "preference_conflict" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "safety_priority" ｜ 候选映射(手册/裁定)

### 7. conf_000016（conflict_resolution）
- input 摘要：{"conflict_type":"time_update","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"旧偏好“回答详细” → 新偏好“以后简短”"}
  - conflict_type = "temporal_inconsistency" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "keep_new_override" ｜ 候选映射(手册/裁定)

### 8. conf_000018（conflict_resolution）
- input 摘要：{"conflict_type":"source","candidates":{"old":"旧记忆","new":"新指令"},"scenario":"用户手动配置 vs 行为推断"}
  - conflict_type = "source_conflict" ｜ 候选映射(手册/裁定)
  - resolution_status = "resolved_manual" ｜ 候选映射(手册/裁定)
  - left_knowledge_id = "keep_001" ｜ 候选映射(手册/裁定)
  - right_knowledge_id = "remove_001" ｜ 候选映射(手册/裁定)
  - involved_knowledge_ids = ["keep_001","remove_001"] ｜ 候选映射(手册/裁定)
  - resolution_strategy = "explicit_config_priority" ｜ 候选映射(手册/裁定)

### 9. e2e_000001（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 1 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.1","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 10. e2e_000002（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 2 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.2","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 11. e2e_000004（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 4 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.4","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 12. e2e_000007（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 7 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.7","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 13. e2e_000010（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 10 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.10","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 14. e2e_000012（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 12 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.12","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 15. e2e_000013（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 13 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.13","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 16. e2e_000015（end_to_end_session）
- input 摘要：{"turns":[{"role":"user","content":"帮我准备第 15 次项目发布检查"},{"role":"assistant","content":"先检查版本号、备份和发布清单。"}],"events":["release_check","backup","deploy"]}
  - expected_memory = {"version":"v1.15","status":"pending_review"} ｜ 候选映射(手册/裁定)
  - expected_response = "发布前需完成备份与回归测试" ｜ 候选映射(手册/裁定)
  - sensitivity = null ｜ 可选/待人工复核

### 17. retr_000004（knowledge_retrieval）
- input 摘要：{"query":"月度备份的流程模板是什么？","query_type":"template_reuse"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["kb_template_024"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = ["kb_template_091"] ｜ 候选映射(手册/裁定)
  - expected_answer_points = ["备份范围","校验和步骤"] ｜ 候选映射(手册/裁定)
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 18. retr_t2r_10015（knowledge_retrieval）
- input 摘要：{"query":"雨什么时候念四声","query_id":"10015"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["114538","15675","306752","657963","721546","727240"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 19. retr_t2r_10034（knowledge_retrieval）
- input 摘要：{"query":"没删除不聊天没交集","query_id":"10034"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["375307","65655"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 20. retr_t2r_10044（knowledge_retrieval）
- input 摘要：{"query":"男朋友说和我住在一起什么心情","query_id":"10044"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["335319","525681","671480"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 21. retr_t2r_10072（knowledge_retrieval）
- input 摘要：{"query":"苹果公司恶心","query_id":"10072"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["207855"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 22. retr_t2r_10138（knowledge_retrieval）
- input 摘要：{"query":"星座书上说我们不合歌词是什么意思","query_id":"10138"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["15869","329238","481858","59959","742007"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 23. retr_t2r_1014（knowledge_retrieval）
- input 摘要：{"query":"苹果11插卡没信号","query_id":"1014"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["1474","333174","51936","549550","636380","66318","89845"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 24. retr_t2r_10151（knowledge_retrieval）
- input 摘要：{"query":"2016款天籁0到100公里时速的时间","query_id":"10151"}
  - knowledge_type = "template" ｜ 候选映射(手册/裁定)
  - evaluation_role = "positive_retrieval" ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - relevant_ids = ["15886"] ｜ 候选映射(手册/裁定)
  - hard_negative_ids = [] ｜ 待人工判定
  - expected_answer_points = [] ｜ 待人工判定
  - superseded_by_id = null ｜ 待人工判定
  - retrieval_ref = null ｜ 待KB/条件可空(D9)
  - rationale = null ｜ 可选/待人工复核

### 25. forg_000006（precise_forgetting）
- input 摘要：{"forget_instruction":"删除上周临时记录的文件路径，保留本周的记录"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_path_009"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_path_009"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 26. forg_000007（precise_forgetting）
- input 摘要：{"forget_instruction":"忘记某个客户姓名的所有关联记录，但保留流程知识"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_person_012"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_person_012"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 27. forg_000010（precise_forgetting）
- input 摘要：{"forget_instruction":"删除上周临时记录的文件路径，保留本周的记录"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_path_009"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_path_009"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 28. forg_000014（precise_forgetting）
- input 摘要：{"forget_instruction":"删除上周临时记录的文件路径，保留本周的记录"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_path_009"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_path_009"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 29. forg_000018（precise_forgetting）
- input 摘要：{"forget_instruction":"删除上周临时记录的文件路径，保留本周的记录"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_path_009"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_path_009"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 30. forg_000022（precise_forgetting）
- input 摘要：{"forget_instruction":"删除上周临时记录的文件路径，保留本周的记录"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "knowledge" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"kb_path_009"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["kb_path_009"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 31. forg_000025（precise_forgetting）
- input 摘要：{"forget_instruction":"忘记我在 VSCode 中偏好深色主题，但保留其他开发偏好"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "preference" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"pref_ui_theme_001"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["pref_ui_theme_001"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 32. forg_000040（precise_forgetting）
- input 摘要：{"forget_instruction":"撤回刚才设置的桌面布局偏好，恢复系统默认"}
  - forget_mode = "single_item" ｜ 候选映射(手册/裁定)
  - target_type = "preference" ｜ 候选映射(手册/裁定)
  - target_selector = {"target_id":"pref_ui_layout_021"} ｜ 候选映射(手册/裁定)
  - status = "completed" ｜ 候选映射(手册/裁定)
  - is_cascade = false ｜ 候选映射(手册/裁定)
  - has_vector_cleanup = null ｜ 可选/待人工复核
  - requires_confirmation = false ｜ 候选映射(手册/裁定)
  - resolved_target_ids = ["pref_ui_layout_021"] ｜ 候选映射(手册/裁定)
  - affected_count = 1 ｜ 候选映射(手册/裁定)

### 33. pref_000003（preference_extraction）
- input 摘要：{"user_message":"这次就按英文回复，不用记住。","context":"第 3 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "session" ｜ 候选映射(手册/裁定)
  - preference_key = "output_style" ｜ 候选映射(手册/裁定)
  - preference_value = "本次会话英文回复" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = false ｜ 候选映射(手册/裁定)
  - is_temporary = true ｜ 候选映射(手册/裁定)
  - memory_status = "candidate" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_3"] ｜ 候选映射(手册/裁定)

### 34. pref_000007（preference_extraction）
- input 摘要：{"user_message":"以后项目周报用简洁要点，每条不超过两行，不要长篇段落。","context":"第 7 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "output_style" ｜ 候选映射(手册/裁定)
  - preference_value = "周报用简洁要点，每条<=2行" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_7"] ｜ 候选映射(手册/裁定)

### 35. pref_000017（preference_extraction）
- input 摘要：{"user_message":"在这个项目管理工具里一律用中文标签，其他工具保持英文。","context":"第 17 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "app" ｜ 候选映射(手册/裁定)
  - preference_value = "项目管理工具用中文标签" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_17"] ｜ 候选映射(手册/裁定)

### 36. pref_000023（preference_extraction）
- input 摘要：{"user_message":"在这个项目管理工具里一律用中文标签，其他工具保持英文。","context":"第 23 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "app" ｜ 候选映射(手册/裁定)
  - preference_value = "项目管理工具用中文标签" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_23"] ｜ 候选映射(手册/裁定)

### 37. pref_000039（preference_extraction）
- input 摘要：{"user_message":"这次就按英文回复，不用记住。","context":"第 39 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "session" ｜ 候选映射(手册/裁定)
  - preference_key = "output_style" ｜ 候选映射(手册/裁定)
  - preference_value = "本次会话英文回复" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = false ｜ 候选映射(手册/裁定)
  - is_temporary = true ｜ 候选映射(手册/裁定)
  - memory_status = "candidate" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_39"] ｜ 候选映射(手册/裁定)

### 38. pref_000052（preference_extraction）
- input 摘要：{"user_message":"之前说报告要详细，以后改成每节只写结论和关键数字。","context":"第 52 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "output_style" ｜ 候选映射(手册/裁定)
  - preference_value = "报告每节只写结论和关键数字" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 2 ｜ 候选映射(手册/裁定)
  - previous_version_id = "v1" ｜ 候选映射(手册/裁定)
  - evidence_event_ids = ["evt_pref_52"] ｜ 候选映射(手册/裁定)

### 39. pref_000055（preference_extraction）
- input 摘要：{"user_message":"以后项目周报用简洁要点，每条不超过两行，不要长篇段落。","context":"第 55 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "output_style" ｜ 候选映射(手册/裁定)
  - preference_value = "周报用简洁要点，每条<=2行" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_55"] ｜ 候选映射(手册/裁定)

### 40. pref_000059（preference_extraction）
- input 摘要：{"user_message":"在这个项目管理工具里一律用中文标签，其他工具保持英文。","context":"第 59 次会话上下文","scene":"麒麟 OS 桌面助手"}
  - expression_type = "explicit" ｜ 候选映射(手册/裁定)
  - preference_scope = "tool" ｜ 候选映射(手册/裁定)
  - preference_key = "app" ｜ 候选映射(手册/裁定)
  - preference_value = "项目管理工具用中文标签" ｜ 候选映射(手册/裁定)
  - confidence_score = 0.95 ｜ 候选映射(手册/裁定)
  - should_persist = true ｜ 候选映射(手册/裁定)
  - is_temporary = false ｜ 候选映射(手册/裁定)
  - memory_status = "active" ｜ 候选映射(手册/裁定)
  - version = 1 ｜ 候选映射(手册/裁定)
  - previous_version_id = null ｜ 待KB/条件可空(D9)
  - evidence_event_ids = ["evt_pref_59"] ｜ 候选映射(手册/裁定)
