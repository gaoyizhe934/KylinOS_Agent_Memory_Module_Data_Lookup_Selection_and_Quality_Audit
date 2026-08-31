# 数据卡 v1（2026-08-07）

## 数据体系

| 类别 | 主要场景 | 关键标签 | 本包候选草稿数 | 构建方式 |
| --- | --- | --- | --- | --- |
| 偏好记忆 | 输出风格、工具选择、确认习惯、应用偏好、作用域 | type/value/scope/confidence/evidence/should_store | 60 | 自建为主，LongMemEval 辅助 |
| 知识记忆 | 事实、流程、历史案例、可复用模板、失败经验 | knowledge_type/content/source/version/valid_time/relations | 60 | T2Ranking/DuReader 辅助+自建 OS 知识 |
| Tool Result | 成功、失败、取消、超时、部分成功、副作用 | status/tool/args/result/side_effect/persist_policy | 50 | 自建+真实回放 |
| 冲突处理 | 新旧版本、来源、时间、作用域、用户覆盖 | conflict_type/candidates/winner/resolution_reason | 40 | 自建为主，MultiWOZ 负样本辅助 |
| 精准遗忘 | 按对象、类型、时间、作用域删除和重建残留 | target_ids/scope/expected_deleted/must_keep | 40 | 自建为主 |
| 端到端会话 | 跨会话复用、冲突、工具、遗忘、重启恢复 | turns/events/expected_memory/expected_response | 15 | 麒麟环境生成 |

## 公开候选登记

| dataset_id | 正式名称 | 定位 | License 状态 | 下载状态 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | LongMemEval (cleaned) | 核心候选（待 Reviewer 批准） | MIT（仓库 LICENSE 原文已存档） | 已下载 longmemeval_oracle.json（手动下载） |
| longmemeval_v2_2026 | LongMemEval-V2 | 核心候选（补充） | Apache-2.0（仓库 LICENSE 原文已存档） | 已下载 questions.jsonl + SCHEMA/checksums（手动下载） |
| locomo_2024 | LoCoMo | 补充候选（待核验） | 待核验 | 网络受限，未下载 |
| stabletoolbench_2024 | StableToolBench | 核心候选（补充） | Apache-2.0（仓库 LICENSE 原文已存档） | 已下载官方 data_example 样例（5 个文件） |
| toolbench_2024 | ToolBench | 补充候选（不进入首版封存） | Apache-2.0（官方 README 声明） | 官方说明已存档（Apache-2.0）；data.zip 需手动/大文件下载 |
| t2ranking_2023 | T2Ranking | 核心候选（中文检索） | 待核验（HF Data Card 未下载） | 已下载 dev queries+qrels（官方 HF 镜像） |
| dureader_retrieval_2022 | DuReader Retrieval | 核心候选（二选一） | 待核验 | 官方说明已存档；数据需在千言/百度渠道注册下载 |
| multiwoz_2_2_2020 | MultiWOZ 2.2 | 补充候选（辅助/负样本） | MIT（仓库 LICENSE 原文已存档） | 已下载 dev 样本 dialogues_001.json（100 条抽样审计） |
| dailydialog_2017 | DailyDialog | 仅补充候选（下载阻塞） | 站点条款待核验 | 安全软件拦截，未使用 |
| personachat_2018 | PersonaChat (ParlAI) | 补充候选（不进入首版封存） | 待核验 | 网络受限，未下载 |
| msmarco_2021 | MS MARCO | 方法论参考（不采用） | Microsoft Research License/Notice 待核验 | 网络受限，未下载 |
| trec_tracks_2024 | TREC (NIST) | 方法论参考 | NIST 官方条款待核验 | 未下载 |
| bpmn_2_0_2013 | BPMN 2.0 (OMG 标准) | 结构参考 | OMG 标准使用条款 | 已下载官方规范 PDF（结构参考） |

## 规模口径

首版封存目标按手册表 11：偏好 400-500、检索 600-1000 知识/300-400 查询、冲突 200-300、遗忘 150-250、Tool 200-300、端到端 50-80。本包先交付候选草稿并遵循“宁少勿假”原则，在双人标注与 Reviewer 批准后按真实标注量回填。