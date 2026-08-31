# multiwoz_2_2_2020 来源核验报告

- 正式名称：MultiWOZ 2.2
- 数据任务对应：冲突/任务对话辅助负样本
- 官方发布者：Google 修正版（budzianowski/multiwoz 仓库托管）
- 官方仓库/项目页：https://github.com/budzianowski/multiwoz/tree/master/data/MultiWOZ_2.2
- 数据下载页：https://github.com/budzianowski/multiwoz
- 论文：https://arxiv.org/abs/2007.12720
- 版本/Commit/Release：2.2 dev 子集；dialogues_001.json（11.7MB）已下载；仓库 LICENSE/README/schema 已存档
- License/Terms：MIT（仓库 LICENSE 原文已存档）
- 允许用途：研究、修改、内部演示、公开展示、再分发（以 LICENSE 原文为准）
- 数据规模与格式：10K dialogues；belief state 全标注
- 标签/证据：goal、turns、belief_state、dialogue acts
- 已知问题：不是长期记忆集，不能直接评偏好版本和遗忘；仅作辅助/负样本
- 抽样审计：已下载 dev 样本 dialogues_001.json（100 条抽样审计）
- 结论（AI 草稿）：补充候选（辅助/负样本）
- 核验状态：已核验；最终批准：待 Reviewer

证据材料：本包 `evidence/source/common/` 下保存的官方 README/LICENSE/页面存档。
