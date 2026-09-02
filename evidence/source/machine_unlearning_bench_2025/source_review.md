# machine_unlearning_bench_2025 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-09-01（Annotator A = lyf-1213，补写 A 侧缺失来源核验）。
证据文件：`hf_dataset_metadata_20260901.json`（HF Datasets API 完整元数据）、`hf_README_raw_20260901.md`（README 原文 2303 字符）、`hf_card_check_output_20260901.txt`（核查脚本输出）、`hf_file_list_20260901.txt`（文件清单）、`license_review.md`（B 侧 License 审查草稿）。

## 背景说明

本数据集由 B（DGXD01）在 Gate 3 前待办中补齐证据包（见 `license_review.md` 背景），但其目录此前缺失 A 侧的 `source_review.md`。本报告作为 A 的来源核验补齐，使 12 个已登记候选的 evidence 三件套（source_review / license_review / version_lock）全部齐备，供 Reviewer Gate 3 逐卡裁决。

## 可从原文直接确认的内容

- 正式名称：Data Unlearning Bench（数据集 `data-unlearning-bench`，所属 HF 组织 `machine-unlearning-bench`）。
- 官方数据页：https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench（A 于 2026-09-01 通过 HF Datasets API 核验，HTTP 可达，见 api_snapshot）。
- 发布者：HF 组织 `machine-unlearning-bench`——**社区组织，非论文一作本人发布渠道**（此项在 Gate 3 标记时请 Reviewer 从严）。
- 论文：arXiv:2410.23232 "Attribute-to-Delete: Machine Unlearning via Datamodel Matching"（HF 卡片 tags 中 arxiv 字段 `arxiv:2410.23232` 指向一致，2026-09-01 可达）。
- 许可证：MIT（三重证据交叉印证：HF API `cardData.license = "mit"` / tags 含 `license:mit` / README YAML front-matter 声明 `license: mit`）。
- 规模：10K~100K 样本（size_categories 标签），usedStorage 约 10.6GB。
- 用途：数据遗忘（data-unlearning）技术评测，方法为 KLOM（KL-divergence of Margins）。
- 数据格式：用于训练/重训/遗忘/评测的 forget set 与 retain set（依据 hf_file_list 与 README 描述，具体 schema 以数据仓库 README 为准）。

## 与此前登记表的关系

- 阶段 2 登记时结论为「补充候选（精准遗忘参考）」，quality_score_draft 75，evidence_dir 指向本目录但当时为空——B 已补齐（license_review.md），A 本次补 source_review.md，目录证据完整。

## 已知问题与定位说明

1. **发布者为社区组织而非论文官方**：P2~P3 边界，建议 Reviewer 标记「需确认」而非直接「允许试用」。
2. **任务形态不同**：本数据集是「训练数据遗忘」基准（从模型权重/训练分布中遗忘），**不是**麒麟 OS Agent「记忆条目遗忘」（删除某条用户记忆并防残留）。只能作精准遗忘任务的**方法/评测思路参考**，不能直接产生本项目 Gold 样本。
3. **未下载实际数据**：当前仅存档元数据/卡片证据，未下载 10.6GB 全量数据（红线 #2 License 先行已满足：MIT 证据已存档，方可在后续需要时下载）。

## v2.0 取用记录（2026-09-01，A = lyf-1213）

- 本 source_review.md 由 A 基于已存档的 B 侧证据包（hf_dataset_metadata / hf_README / hf_card_check_output）撰写，与 license_review.md、version_lock_20260901.md 配套。
- 12 候选 evidence 三件套齐备性复核：本报告补齐后 machine_unlearning_bench_2025 与其他 11 个候选一致（source_review + license_review + version_lock 均齐）。

## 待 Reviewer 决策

- machine_unlearning_bench_2025 是否作为「补充候选（精准遗忘参考）」通过 Gate 3？发布者社区身份 + 任务形态差异，建议标记「需确认」或「允许试用（仅方法参考）」。
