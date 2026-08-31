# 数据集选型决策 v1（2026-08-07）

评分表依据手册附录 B，AI 草稿分由执行脚本按候选元数据生成，最终分由 Data Owner 与 Reviewer 独立评分后取结论。

| dataset_id | 正式名称 | 任务 | AI 草稿分 | 结论 | 状态 |
| --- | --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | LongMemEval (cleaned) | 偏好/检索/冲突/遗忘/端到端辅助 | 88 | 核心候选（待 Reviewer 批准） | 待 Reviewer 批准 |
| longmemeval_v2_2026 | LongMemEval-V2 | Tool Result/知识检索/端到端辅助 | 84 | 核心候选（补充） | 待 Reviewer 批准 |
| t2ranking_2023 | T2Ranking | 知识检索（中文） | 82 | 核心候选（中文检索） | 待 Reviewer 批准 |
| stabletoolbench_2024 | StableToolBench | Tool Result | 80 | 核心候选（补充） | 待 Reviewer 批准 |
| dureader_retrieval_2022 | DuReader Retrieval | 知识检索（中文） | 80 | 核心候选（二选一） | 待 Reviewer 批准 |
| multiwoz_2_2_2020 | MultiWOZ 2.2 | 冲突/任务对话辅助负样本 | 74 | 补充候选（辅助/负样本） | 待 Reviewer 批准 |
| locomo_2024 | LoCoMo | 端到端/长期会话辅助 | 72 | 补充候选（待核验） | 待 Reviewer 批准 |
| toolbench_2024 | ToolBench | Tool Result 辅助 | 68 | 补充候选（不进入首版封存） | 待 Reviewer 批准 |
| personachat_2018 | PersonaChat (ParlAI) | 偏好辅助 | 66 | 补充候选（不进入首版封存） | 待 Reviewer 批准 |
| msmarco_2021 | MS MARCO | 检索辅助 | 64 | 方法论参考（不采用） | 待 Reviewer 批准 |
| dailydialog_2017 | DailyDialog | 自然表达/闲聊负样本辅助 | 62 | 仅补充候选（下载阻塞） | 待 Reviewer 批准 |
| trec_tracks_2024 | TREC (NIST) | 检索方法论参考 | 60 | 方法论参考 | 待 Reviewer 批准 |
| bpmn_2_0_2013 | BPMN 2.0 (OMG 标准) | 工作流知识结构参考 | 58 | 结构参考 | 待 Reviewer 批准 |

## 否决项检查（AI 草稿）

- 来源可追溯：LongMemEval/LongMemEval-V2/T2Ranking/DuReader/MultiWOZ/StableToolBench 已存官方 README/页面；LoCoMo/MS MARCO 待人工复核。
- License 明确：LongMemEval=MIT、LongMemEval-V2=Apache-2.0 已存档；其余待人工/法务确认。
- 无真实敏感信息：候选仅登记元数据，未采集真实个人信息。
- 可离线复现：正式评测使用固定子集与静态缓存；实时 API 不作为依据。
- 标签可解释：自建候选样本带 evidence 与模板族；公开集需人工抽检。
- 切分防泄漏：按用户/会话/模板族切分脚本已就绪。

## 建议

- 核心公开层：LongMemEval cleaned + T2Ranking（或 DuReader Retrieval）+ StableToolBench 静态子集。
- 自建核心层：麒麟 OS Memory Gold（偏好/检索/冲突/遗忘/Tool/端到端），本包已生成候选草稿。
- 真实回放层：麒麟虚拟机执行固定子集并回填指标。