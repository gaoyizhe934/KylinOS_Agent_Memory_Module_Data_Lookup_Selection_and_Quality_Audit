
# 阶段 2 候选覆盖检查 — 原始输出存档

- 日期: 2026-09-01
- 命令: python scripts/oneclick/stage2_coverage_check.py（仓库根目录执行）
- 环境: Windows 11, Python 3.12, 只读本地登记表，不访问网络
- 退出码: 0（覆盖达标）
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

## 二、Gate 2 登记完整性（正式名称/版本线索/官方来源/任务说明）

| 数据集 | 正式名称 | 版本线索 | 官方来源 | 任务说明 | 定位 |
| --- | --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ✅ | ✅ | ✅ | ✅ | 核心候选（待 Reviewer 批准） |
| longmemeval_v2_2026 | ✅ | ✅ | ✅ | ✅ | 核心候选（补充） |
| stabletoolbench_2024 | ✅ | ✅ | ✅ | ✅ | 核心候选（补充） |
| toolbench_2024 | ✅ | ✅ | ✅ | ✅ | 补充候选（不进入首版封存） |
| t2ranking_2023 | ✅ | ✅ | ✅ | ✅ | 核心候选（中文检索） |
| dureader_retrieval_2022 | ✅ | ✅ | ✅ | ✅ | 核心候选（二选一） |
| multiwoz_2_2_2020 | ✅ | ✅ | ✅ | ✅ | 补充候选（辅助/负样本） |
| personachat_2018 | ✅ | ⚠️待核验 | ✅ | ✅ | 补充候选（不进入首版封存） |
| msmarco_2021 | ✅ | ✅ | ✅ | ✅ | 方法论参考（不采用） |
| trec_tracks_2024 | ✅ | ✅ | ✅ | ✅ | 方法论参考 |
| bpmn_2_0_2013 | ✅ | ✅ | ✅ | ✅ | 结构参考 |
| machine_unlearning_bench_2025 | ✅ | ✅ | ✅ | ✅ | 补充候选（精准遗忘参考） |

待人工核验项（不阻塞覆盖结论，Gate 2 批准前需 Reviewer 确认）: personachat_2018.version=⚠️待核验

总体结论: 覆盖达标；Gate 2 最终状态待 Reviewer 批准。

