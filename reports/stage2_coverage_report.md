# 阶段 2：候选查找与登记报告

执行人：Annotator A（lyf-1213）
日期：2026-08-31

## 一、现有数据集体检结果

| 数据集 | 官方URL | 数据URL | 结论 |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ✅ OK | ✅ OK | 保留 |
| longmemeval_v2_2026 | ✅ OK | ✅ OK | 保留 |
| t2ranking_2023 | ✅ OK | ✅ OK | 保留 |
| stabletoolbench_2024 | ✅ OK | ✅ OK | 保留 |
| toolbench_2024 | ✅ OK | ✅ OK | 保留 |
| multiwoz_2_2_2020 | ✅ OK | ✅ OK | 保留 |
| dureader_retrieval_2022 | ✅ OK | ✅ OK | 保留 |
| personachat_2018 | ✅ OK | ✅ OK | 保留 |
| msmarco_2021 | ✅ OK | ✅ OK | 保留 |
| trec_tracks_2024 | ✅ OK | ✅ OK | 保留 |
| bpmn_2_0_2013 | ✅ OK | ✅ OK | 保留 |

**结果：11 个数据集全部可访问，无需剔除。**

## 二、候选覆盖检查

| 任务类型 | 原有候选 | 本次新增 | 现在总数 | 达标 |
| --- | --- | --- | --- | --- |
| 偏好提取 | 2 | 0 | 2 | ✅ |
| 知识检索 | 6 | 0 | 6 | ✅ |
| 冲突处理 | 2 | 0 | 2 | ✅ |
| 精准遗忘 | 1 | +1 (machine-unlearning-bench) | **2** | ✅ |
| Tool Result | 3 | 0 | 3 | ✅ |
| 端到端会话 | 2 | 0 | 2 | ✅ |

## 三、新增数据集详情

machine-unlearning-bench/data-unlearning-bench

- 任务：精准遗忘（辅助参考）
- 来源：HuggingFace
- 许可证：MIT
- 下载量：2567
- 论文：https://arxiv.org/abs/2410.23232
- 说明：基于 KLOM 的机器遗忘评估基准，规模 10K~100K 样本
- 定位：公开基准层（A层），作为精准遗忘场景的参考基准，麒麟 OS 实际遗忘数据仍需自建

## 四、Gate 2 结论

**PASS — 每类任务至少有 2 个候选，待 Reviewer 批准。**