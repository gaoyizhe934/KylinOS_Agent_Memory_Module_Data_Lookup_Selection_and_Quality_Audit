# 阶段 5 候选评分表（Annotator B 复核）

- 角色：Annotator B（DGXD01）· 独立复核分
- 分支：`feat/A-B-stage4`
- 日期：2026-09-02
- 依据：手册《附录 B 100 分质量评分表》、A 侧草案 `reports/stage5_scoring_A.md`、B 侧阶段 4 审计结果（200 条抽检 × 6 项 = 1200 次检查，0 FAIL）
- 说明：本文件为 B 侧独立复核，基于阶段 4 审计数据对 A 侧草案逐项校验。最终选型结论由 Reviewer 签发。

## 复核方法

1. 逐条比对 A 侧自评分与 B 侧审计结果（结构检查 + 语义检查 + 敏感检查）
2. 对 4 个已审计数据集（longmemeval_cleaned / longmemeval_v2 / multiwoz / t2ranking）以审计实测数据校验
3. 对 8 个未审计数据集以 Gate 3 登记表和 A 侧证据包校验
4. 标记"同意"或"建议调整"，给出调整依据

## 复核结果汇总

| dataset_id | A 自评分 | B 复核分 | 差异 | 档位 | B 结论 |
| --- | --- | --- | --- | --- | --- |
| t2ranking_2023 | 84 | 83 | -1 | 核心 | 同意核心，标签质量微调 |
| longmemeval_cleaned_2025 | 82 | 82 | 0 | 核心 | 同意 |
| longmemeval_v2_2026 | 81 | 81 | 0 | 核心 | 同意 |
| stabletoolbench_2024 | 75 | 75 | 0 | 补充 | 同意（样本不足降级合理） |
| dureader_retrieval_2022 | 75 | 75 | 0 | 补充（待决） | 同意（License 否决项命中，暂记分） |
| multiwoz_2_2_2020 | 72 | 73 | +1 | 补充 | 同意补充，数据干净程度微调 |
| msmarco_2021 | 68 | 68 | 0 | 不采用 | 同意（Gate 3 淘汰） |
| machine_unlearning_bench_2025 | 65 | 65 | 0 | 补充（边界） | 同意（仅方法参考） |
| trec_tracks_2024 | 59 | 59 | 0 | 不采用 | 同意 |
| personachat_2018 | 57 | 57 | 0 | 不采用 | 同意（License 否决项命中） |
| toolbench_2024 | 56 | 56 | 0 | 不采用 | 同意（离线复现否决项命中） |
| bpmn_2_0_2013 | 49 | 49 | 0 | 不采用 | 同意（结构参考） |

**B 复核与 A 草案差异：仅 2 项微调（t2ranking -1、multiwoz +1），均不改变档位。**

## 调整明细

### 调整 1：t2ranking_2023 — 标签质量 13→12（总分 84→83）

| 维度 | 满分 | A 自评分 | B 复核分 | 调整理由 |
| --- | --- | --- | --- | --- |
| 标签质量 | 15 | 13 | 12 | B 侧阶段 4 审计中 qrels 文件未核验（查询集不含 relevance 标注，标注在独立 qrels 文件中），标签完整性尚需人工核 qrels 后确认；A 注明"TREC qrels 格式、relevance 4 级"基于文档描述，非实测验证 |

- 档位不变：83 仍 ≥ 80，维持核心候选；
- 后续行动：人工核 qrels 文件后，若标签完整可恢复 13/15；

### 调整 2：multiwoz_2_2_2020 — 数据干净程度 4→5（总分 72→73）

| 维度 | 满分 | A 自评分 | B 复核分 | 调整理由 |
| --- | --- | --- | --- | --- |
| 数据干净程度 | 5 | 4 | 5 | B 侧阶段 4 审计结果：100 条记录 0 parse_error / 0 duplicate / 0 type_mismatch / 0 sensitive_hit / 0 null_string / 0 length_anomaly，是 4 个已审计数据集中唯一 0 WARN 的数据集（其余 3 个分别有 50/47/50 条 WARN）；A 评分 4/5 可能基于通用判断，但实测数据完全干净 |

- 档位不变：73 仍在 65~79 区间，维持补充候选；

## 已审计 4 数据集审计结果与评分交叉验证

| 数据集 | 审计异常 | 高危 | 中危 | 低危 | A 评分 | B 评分 | 一致性 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | 2 | 0 | 0 | 2(email,合成) | 82 | 82 | 一致 |
| longmemeval_v2_2026 | 1 | 0 | 0 | 1(null_string,abstention) | 81 | 81 | 一致 |
| multiwoz_2_2_2020 | 0 | 0 | 0 | 0 | 72 | 73 | +1（干净程度） |
| t2ranking_2023 | 0 | 0 | 0 | 0 | 84 | 83 | -1（qrels 未核） |

- 审计异常全部为低危或 0，与 A 侧 4~5/5 的数据干净程度评分区间一致；
- 3 条低危异常（email×2 / null_string×1）经语义复核确认为合成数据/abstention 设计特性；

## 否决项复核

| 数据集 | 否决项 | A 判定 | B 判定 | 一致性 |
| --- | --- | --- | --- | --- |
| toolbench_2024 | 可离线复现 | ⚠ 命中 | ⚠ 命中 | 一致（官方数据入口 404） |
| dureader_retrieval_2022 | License 明确 | ⚠ 命中 | ⚠ 命中 | 一致（License 缺失） |
| personachat_2018 | License 明确 | ⚠ 命中 | ⚠ 命中 | 一致（数据无明确许可） |
| 其余 9 个 | 无 | 通过 | 通过 | 一致 |

## 诚实披露

1. B 复核基于阶段 4 审计实测数据（200 条抽检 × 6 项 = 1200 次检查），对 4 个已审计数据集的评分有实测支撑；
2. 对 8 个未审计数据集（stabletoolbench / dureader / toolbench / personachat / msmarco / trec / bpmn / machine_unlearning_bench），B 复核基于 Gate 3 登记表和 A 侧证据包，未独立下载验证；
3. B 侧 2 项微调（t2ranking -1 / multiwoz +1）均不改变档位，对最终选型结论无实质影响；
4. 本表为 B 独立复核，**未经 Reviewer 确认**，不得作为最终选型结论。最终选型结论由 Reviewer 出具 `reports/dataset_selection_decision_v2.md`。
