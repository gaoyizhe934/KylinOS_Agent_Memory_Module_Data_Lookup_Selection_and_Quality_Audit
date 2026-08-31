# 需求—数据映射 v1（2026-08-07）

依据手册第 1/2/5 章生成，覆盖比赛要求、系统能力、数据子集、Gold 标签、指标与证据。

| 比赛要求 | 系统能力 | 数据子集 | Gold 标签 | 指标 | 证据文件 | 构建方式 |
| --- | --- | --- | --- | --- | --- | --- |
| 多源接入（工具执行结果、用户行为、手动配置） | 数据接入与统一解析 | tool_result / preference | source_event_id、status、tool、args、result、side_effect | 解析成功率、字段完整率 | evidence/audit/sample_audit_report.md | 自建+真实回放 |
| 偏好动态捕捉与版本更新 | 偏好提取/更新/撤销 | preference | preference_type、value、scope、confidence、operation | Precision / Recall / F1 >= 85% | data/gold/dev/*.jsonl | 自建为主，LongMemEval 辅助 |
| 知识结构化整合与关联检索 | 知识检索 | retrieval | relevant_ids、relevance、hard_negative_ids、expected_answer_points | Recall@K >= 85%，MRR/nDCG | data/gold/dev/retrieval.jsonl | T2Ranking/DuReader 辅助+自建 OS 知识 |
| 冲突处理 | 冲突识别与决策 | conflict | conflict_type、candidates、winner、resolution_reason | 决策准确率 >= 88% | data/gold/dev/conflict.jsonl | 自建为主，MultiWOZ 负样本辅助 |
| 敏感信息过滤与精准遗忘 | 精准遗忘/安全 | forgetting | forget_instruction、target_ids、must_keep、checkpoints | 删除正确率、误删率、残留数=0 | data/gold/dev/forgetting.jsonl | 自建为主，LongMemEval abstention 辅助 |
| 短中长期记忆流转与工具结果沉淀 | Tool Result / 记忆分层 | tool_result | status、persist_policy、side_effect、failure_reason | 状态判定正确率，失败/超时覆盖 | data/gold/dev/tool_result.jsonl | 自建+StableToolBench 静态子集辅助 |
| 端侧延迟与性能 | 检索响应时间 | retrieval + runtime_replay | fixed corpus + query set | P50/P95 <= 500ms，冷/热启动 | evidence/runtime/environment_manifest.md | 麒麟虚拟机真实回放 |
| 跨会话复用、重启恢复与端到端演示 | 端到端会话 | end_to_end | turns、events、expected_memory、expected_response | 端到端案例通过率 | data/gold/dev/end_to_end.jsonl | 麒麟环境生成+LoCoMo 辅助 |

## 数据缺口与优先级

1. 高优先：偏好提取、精准遗忘、Tool Result 必须自建，公开数据仅辅助。
2. 高优先：中文知识检索选用 T2Ranking 或 DuReader Retrieval 之一，必须加入麒麟 OS 场景。
3. 中优先：冲突处理以自建为主，MultiWOZ 2.2 只作辅助/负样本。
4. 中优先：端到端会话在麒麟环境生成，LoCoMo 仅作高难质检参考。
5. 待人工确认：LongMemEval-V2、LoCoMo-Plus 等新兴候选先完成独立质量与复现审计。

## 需人工确认

- 各公开数据集 License 中未明确的项目（再分发、商业使用、公开展示）。
- DailyDialog 官方下载被本机安全软件拦截，需确认官方渠道后重下。
- MS MARCO Terms 页访问失败，需人工打开官网核对。