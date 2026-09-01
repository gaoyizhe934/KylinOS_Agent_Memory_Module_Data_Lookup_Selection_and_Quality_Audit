# t2ranking_2023 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31。证据文件：`t2ranking_hf_README.md`、`t2ranking_HF_card.py`、`t2ranking_hf_api_metadata.json`（本目录，均来自 hf-mirror.com 官方卡片 API）。

## 可从原文直接确认的内容

- 正式名称：T2Ranking: A Large-scale Chinese Benchmark for Passage Ranking（THUIR 清华大学信息检索组）。
- 官方渠道：GitHub `THUIR/T2Ranking` + HuggingFace `THUIR/T2Ranking`（**THUIR 组织官方上传**，hf API 返回的卡片元数据 downloads=824）。
- 论文：https://arxiv.org/abs/2304.03679。
- License 声明：HF 官方卡片 `cardData.license = apache-2.0`（API 元数据，已存档 `t2ranking_hf_api_metadata.json`）。
- 数据规模（HF 卡片/README）：300K+ 查询、2.3M 段落，TREC qrels 格式；本次已下载 dev 查询集与 qrels（`data/raw/t2ranking_2023/v0_sample/`）。
- HF 仓库文件清单（API 返回，共 19 个文件）：collection.tsv、queries.dev/test/train.tsv、qrels.*.tsv 等，与 GitHub 官方 README 描述一致。

## 与此前登记表的差异

- registry v1.0 中"License 待核验（HF Data Card 未下载）"：**本次已下载卡片与 README，卡片声明 apache-2.0**。
- GitHub 仓库根目录无独立 LICENSE 文件（raw 404）——许可声明以 HF 官方卡片为准。**需 Reviewer 决定是否接受"卡片声明"作为合规证据，或进一步要求作者书面确认**。

## 推断（需人工确认）

- HF 卡片由 THUIR 官方组织账号发布，与 GitHub 仓库为同一发布者，一致性高，但两渠道声明形式不同（卡片字段 vs 文件）。
- Web 检索域与 OS 记忆域差距仍存在（README 未涉及 OS 场景）。

## 待 Reviewer 决策

- apache-2.0 卡片声明是否足以批准进入核心候选（当前评分草稿 82 分，核心候选-中文检索）。
