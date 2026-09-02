# 数据集最终选型决策 v2.0（Reviewer 签发）

- 签发人：gaoyizhe（Reviewer）
- 签发日期：2026-09-02
- 依据：手册附录 B 100 分评分表；A 侧草案 `reports/stage5_scoring_A.md`；B 侧独立复核 `reports/stage5_scoring_B.md`；registry Gate 3 逐卡标记（PR#16）；阶段 3 证据包（PR#15）
- 说明：本文件为 Reviewer 对 12 个候选数据集的**最终选型结论**，是 Gate 5 的正式产出。评分采纳 B 复核后分数；Gate 3 标记（允许试用/需确认/淘汰）优先于评分档位——**淘汰/方法参考类候选即使评分 ≥65 也不进入正式下载**。

## 一、最终选型结论

| dataset_id | B 复核分 | 评分档位 | Gate 3 | 最终选型定位 |
| --- | --- | --- | --- | --- |
| t2ranking_2023 | 83 | 核心（≥80） | 允许试用 | ✅ **核心候选**，进入阶段6 下载/冻结 |
| longmemeval_cleaned_2025 | 82 | 核心 | 允许试用 | ✅ **核心候选** |
| longmemeval_v2_2026 | 81 | 核心 | 允许试用 | ✅ **核心候选** |
| stabletoolbench_2024 | 75 | 补充（65~79） | 允许试用 | ⏸ **补充候选（条件）**：阶段4 样本缺口（仅3条）闭合后复核并正式冻结 |
| multiwoz_2_2_2020 | 73 | 补充 | 允许试用 | ✅ **补充候选**（辅助/负样本），进入下载/冻结 |
| dureader_retrieval_2022 | 75 | 补充 | 需确认 | ⏸ **补充候选（条件）**：License 缺失，人工/法务核验通过前不下载 |
| machine_unlearning_bench_2025 | 65 | 补充（边界） | 需确认 | ⏸ **仅方法参考**：社区发布者，不进封存、不下载 |
| msmarco_2021 | 68 | （评分≥65） | 淘汰 | ❌ **不采用**（Gate 3 淘汰优先：Terms 非商业、再分发受限） |
| personachat_2018 | 57 | 不采用 | 需确认 | ❌ **不采用**（License 否决项命中） |
| trec_tracks_2024 | 59 | 不采用 | 淘汰 | ❌ **不采用**（方法论参考） |
| toolbench_2024 | 56 | 不采用 | 淘汰 | ❌ **不采用**（离线复现否决项命中） |
| bpmn_2_0_2013 | 49 | 不采用 | 淘汰 | ❌ **不采用**（结构参考） |

## 二、通过名单（进入阶段6 正式下载/冻结流程）

**核心 3**：t2ranking_2023、longmemeval_cleaned_2025、longmemeval_v2_2026
**补充 2**：stabletoolbench_2024（条件：阶段4 样本补齐后复核）、multiwoz_2_2_2020

（与 PR#19 已下载的 v0_subset 名单一致：3 核心 + stabletoolbench + multiwoz。）

## 三、待决/条件名单

- **dureader_retrieval_2022**：License 核验（千言/LUGE 渠道条款）通过后方可试用/下载；
- **machine_unlearning_bench_2025**：仅作精准遗忘方法参考，不进首版封存、不下载；
- **personachat_2018**：数据无明确许可，不采用（如需启用须先解决 License 证据）。

## 四、不采用名单

msmarco_2021（Terms 非商业再分发受限）、trec_tracks_2024（方法论参考）、toolbench_2024（离线复现否决 + 官方入口失效）、bpmn_2_0_2013（结构参考）。以上不进入下载/冻结，仅作为方法/结构参考留档。

## 五、一票否决复核（Reviewer）

| 候选 | 否决项 | 结论 |
| --- | --- | --- |
| toolbench_2024 | 可离线复现（入口 404） | 命中 → 不采用（方法参考） |
| dureader_retrieval_2022 | License 明确 | 命中 → 需确认（条件） |
| personachat_2018 | License 明确 | 命中 → 不采用 |
| 其余 9 个 | 无 | 通过 |

## 六、后续依赖（Gate 6 及以后）

1. stabletoolbench 阶段4 样本补齐 → 复核其 Gate 4/6 条件项；
2. 按 PR#19 B 校验（manifest 为冻结基线）执行正式冻结（frozen 分支/外部存储固化二进制 + 最终 manifest）；
3. 阶段 7 统一 Schema 转换（仅对通过名单中已冻结候选）。

## 七、结论

**Gate 5：通过**（2026-09-02，Reviewer 签发）。
