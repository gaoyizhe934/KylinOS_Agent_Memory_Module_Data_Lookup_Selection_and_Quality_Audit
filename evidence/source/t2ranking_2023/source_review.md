# t2ranking_2023 来源核验报告

- 正式名称：T2Ranking
- 数据任务对应：知识检索（中文）
- 官方发布者：THUIR（清华）
- 官方仓库/项目页：https://github.com/THUIR/T2Ranking
- 数据下载页：https://huggingface.co/datasets/THUIR/T2Ranking
- 论文：https://arxiv.org/abs/2304.03679
- 版本/Commit/Release：dev 2023；queries.dev.tsv + qrels.retrieval.dev.tsv 已下载
- License/Terms：待核验（HF Data Card 未下载）
- 允许用途：待人工/法务确认
- 数据规模与格式：300K+ queries；2.3M passages；TREC qrels 格式
- 标签/证据：qid/query/pid/passage/qrels relevance 4 级
- 已知问题：Web 检索域与 OS 记忆域有差距；全量过大，只取固定小规模子集
- 抽样审计：已下载 dev queries+qrels（官方 HF 镜像）
- 结论（AI 草稿）：核心候选（中文检索）
- 核验状态：已核验；最终批准：待 Reviewer

证据材料：本包 `evidence/source/common/` 下保存的官方 README/LICENSE/页面存档。
