# 阶段 2 候选覆盖检查输出存档

- 存档时间: 2026-09-01（第二轮复审修复后复跑）
- 命令: `python scripts/oneclick/stage2_coverage_check.py`
- 退出码: 0
- 环境: Windows 11，仓库 clean-branch 分支

```
========== 阶段 2 候选覆盖检查（Gate 2 快速验证）==========
登记表: registry\dataset_registry.csv
登记数据集总数: 12

## 一、六类任务候选覆盖

| 任务类型 | 正式候选数 | 达标 | 候选数据集 | 另含参考类（不计入） |
| --- | --- | --- | --- | --- |
| 偏好提取 | 2 | ✅ | longmemeval_cleaned_2025, personachat_2018 | — |
| 知识检索 | 4 | ✅ | longmemeval_cleaned_2025, longmemeval_v2_2026, t2ranking_2023, dureader_retrieval_2022 | msmarco_2021, trec_tracks_2024 |
| 冲突处理 | 2 | ✅ | longmemeval_cleaned_2025, multiwoz_2_2_2020 | — |
| 精准遗忘 | 2 | ✅ | longmemeval_cleaned_2025, machine_unlearning_bench_2025 | — |
| Tool Result | 3 | ✅ | longmemeval_v2_2026, stabletoolbench_2024, toolbench_2024 | — |
| 端到端会话 | 2 | ✅ | longmemeval_cleaned_2025, longmemeval_v2_2026 | — |

覆盖标准: 每类任务 >= 2 个正式候选（方法论/结构参考不计入）
覆盖结论: 达标
未归入六类任务的登记项（参考类）: bpmn_2_0_2013

## 二、Gate 2 登记完整性（正式名称/版本线索/官方来源/任务说明/数据入口）

| 数据集 | 正式名称 | 版本线索 | 官方来源 | 任务说明 | 数据入口 | 定位 |
| --- | --- | --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ✅ | ✅ | ✅ | ✅ | ✅ | 核心候选（待 Reviewer 批准） |
| longmemeval_v2_2026 | ✅ | ✅ | ✅ | ✅ | ✅ | 核心候选（补充） |
| stabletoolbench_2024 | ✅ | ✅ | ✅ | ✅ | ✅ | 核心候选（补充） |
| toolbench_2024 | ✅ | ✅ | ✅ | ✅ | ✅ | 补充候选（数据入口失效，待裁决） |
| t2ranking_2023 | ✅ | ✅ | ✅ | ✅ | ✅ | 核心候选（中文检索） |
| dureader_retrieval_2022 | ✅ | ✅ | ✅ | ✅ | ✅ | 核心候选（二选一） |
| multiwoz_2_2_2020 | ✅ | ✅ | ✅ | ✅ | ✅ | 补充候选（辅助/负样本） |
| personachat_2018 | ✅ | ✅ | ✅ | ✅ | ✅ | 补充候选（不进入首版封存） |
| msmarco_2021 | ✅ | ✅ | ✅ | ✅ | ✅ | 方法论参考（不采用） |
| trec_tracks_2024 | ✅ | ✅ | ✅ | ✅ | ✅ | 方法论参考 |
| bpmn_2_0_2013 | ✅ | ✅ | ✅ | ✅ | ✅ | 结构参考 |
| machine_unlearning_bench_2025 | ✅ | ✅ | ✅ | ✅ | ✅ | 补充候选（精准遗忘参考） |

登记完整性: 全部字段齐备

总体结论: 覆盖达标；登记完整性通过；Gate 2 最终状态待 Reviewer 批准。
数据入口可访问性验证: python scripts/oneclick/stage2_check_urls.py（按失败条件退出）
```
