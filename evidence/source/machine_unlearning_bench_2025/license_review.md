# machine_unlearning_bench_2025 证据包（F1 补齐）

- 补齐人: B = DGXD01（Annotator B）
- 日期: 2026-09-01
- 背景: PR#1 复核（B 复核报告 `reports/b_review_stage1_2.md`）提出 F1 不合格项——登记表 evidence_dir 指向本目录但目录不存在、License 声称（MIT）无证据落地。Reviewer 在 PR#1 审批中指示「machine_unlearning_bench 列为参考候选，其证据补齐作为 Gate 3 前待办」。本目录即该待办的清偿产物。

## 1. 证据清单

| 文件 | 内容 | 证据作用 |
| --- | --- | --- |
| `hf_card_check_output_20260901.txt` | 仓库自带核查脚本 `scripts/oneclick/check_unlearning_detail.py` 的完整输出 | 复现 A 在阶段 2 的核查过程（cardData keys / license: mit / tags） |
| `hf_dataset_metadata_20260901.json` | HF Datasets API（`/api/datasets/machine-unlearning-bench/data-unlearning-bench`）返回的完整元数据 JSON | **License 机器可读证据**: `cardData.license = "mit"`、`tags` 含 `license:mit`、`size_categories:10K<n<100K`、`arxiv:2410.23232` |
| `hf_README_raw_20260901.md` | 数据集仓库 `raw/main/README.md` 原文（2303 字符） | 卡片 YAML front-matter 再次声明 `license: mit`；数据集用途说明（KLOM 遗忘评测） |
| `license_review.md` | 本文件 | B 侧 License 审查结论（草稿，供 Reviewer Gate 3 标记） |

## 2. License 审查结论（B 草稿）

- **许可类型**: MIT（三个独立证据交叉印证: HF API cardData.license 字段 / tags 元数据 / README YAML front-matter）
- **MIT 条款要点**: 允许使用、复制、修改、合并、再分发（含商业），条件为保留版权与许可声明；无非商业限制条款；
- **对本项目的适用性**: 六项评估用途（研究、修改、内部演示、公开展示、再分发）均在 MIT 允许范围内，**无 License 障碍**；
- **注意事项**:
  1. 本数据集是「训练数据遗忘基准」（KLOM: KL-divergence of Margins），**不是 OS Agent 记忆遗忘场景**，仅作精准遗忘任务的方法参考——与登记表 known_issues 字段一致；
  2. README 未提供单独的 LICENSE 文件链接，以卡片 YAML 声明 + HF 平台标注为准（P2 层证据规则: 官方镜像的卡片声明可作为许可证据）；
  3. 若后续实际下载数据（当前未下载），MIT 文本需随分发物保留。

## 3. 来源与版本线索

- **发布者**: HF 组织 `machine-unlearning-bench`（社区发布，非论文一作本人组织——此项在 Gate 3 标记时请 Reviewer 特别注意，属 P2~P3 之间的来源，建议标记「需确认」而非直接「允许试用」）
- **论文**: arXiv:2410.23232 "Attribute-to-Delete: Machine Unlearning via Datamodel Matching"（2026-09-01 实测可达；HF 卡片 tags 中的 arxiv 字段指向一致）
- **版本**: HF main 分支，2026-08-31 访问（登记表既有口径）；本次补齐核验为 2026-09-01
- **规模**: 10K~100K 样本（size_categories 标签）

## 4. B 复核意见

F1 所述「证据零存档」状态已消除。但提醒 Reviewer 在 Gate 3 标记时注意两点:
1. 发布者为社区组织而非论文作者官方渠道，建议按手册 P2/P3 边界从严标记；
2. 本数据集为「训练数据遗忘」基准，与本项目「OS Agent 记忆条目遗忘」任务形态不同，**只能作方法参考，不能直接产生 Gold 样本**（与登记表 conclusion「补充候选（精准遗忘参考）」一致）。
