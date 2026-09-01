# 阶段 2：候选查找与登记报告

执行人：Annotator A（lyf-1213）
日期：2026-08-31（2026-09-01 修订：按 Reviewer 审查意见修正 URL 统计口径与 Gate 2 结论表述）

## 一、现有数据集 URL 体检结果

复查命令（仓库根目录执行；脚本已修正为从仓库根目录解析路径，代理为可选配置）：

```powershell
python scripts/oneclick/stage2_check_urls.py
```

原始输出存档：`evidence/audit/stage2_url_check_output_20260901.md`（2026-09-01 实测，直连、TLS 校验开启）

| 数据集 | 官方URL | 数据URL | 结论 |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ✅ OK(200) | ✅ OK(200) | 保留 |
| longmemeval_v2_2026 | ✅ OK(200) | ✅ OK(200) | 保留 |
| stabletoolbench_2024 | ✅ OK(200) | ✅ OK(200) | 保留 |
| toolbench_2024 | ✅ OK(200) | ⚠️ 未登记（data.zip 需经 Google Drive 手动下载） | 保留 |
| t2ranking_2023 | ✅ OK(200) | ✅ OK(200) | 保留 |
| dureader_retrieval_2022 | ✅ OK(200) | ✅ OK(200) | 保留 |
| multiwoz_2_2_2020 | ✅ OK(200) | ✅ OK(200) | 保留 |
| personachat_2018 | ✅ OK(200) | ⚠️ 未登记（ParlAI 数据入口待人工核验） | 保留 |
| msmarco_2021 | ✅ OK(200)（2026-09-01 复查通过，此前失败为网络环境问题） | ⚠️ 未登记 | 保留（方法论参考） |
| trec_tracks_2024 | ✅ OK(200) | ⚠️ 未登记（多 Track，无单一数据入口） | 保留（方法论参考） |
| bpmn_2_0_2013 | ✅ OK(200) | ⚠️ 未登记（标准规范文档，非数据集） | 保留（结构参考） |
| machine_unlearning_bench_2025 | ✅ OK(200) | ✅ OK(200) | 保留（本次新增） |

**统计口径与实测结果（2026-09-01）：**

- 官方 URL：12/12 可访问（HTTP 200）
- 数据 URL：7/12 已登记且可访问；5/12 登记表未提供数据 URL
  - 其中 msmarco、trec、bpmn 为方法论/结构参考，定位上不需要数据 URL，不计入"数据 URL 可访问"统计
  - toolbench、personachat 为补充候选，数据入口待人工补充核验（前者经 Google Drive 手动下载，后者 ParlAI 数据入口待核验）
- 修订说明：本报告此前版本声称"11 个数据集的官方 URL 和数据 URL 均可访问"，与登记表 data_url 字段实际为空的事实不符，统计口径错误，已按上表修正。MS MARCO 官网曾记录"连接被重置"，2026-09-01 复查为可访问（HTTP 200），登记表 version 字段已同步更新。

## 二、候选覆盖检查

复查命令（仓库根目录执行）：

```powershell
python scripts/oneclick/stage2_coverage_check.py
```

原始输出存档：`evidence/audit/stage2_coverage_check_output_20260901.md`

统计口径：正式候选 = 登记表 conclusion 不含"方法论参考/结构参考"；覆盖标准 = 每类任务 ≥2 正式候选（手册 3.4 候选搜索停止条件）。

| 任务类型 | 正式候选数 | 候选数据集 | 另含参考类（不计入） | 达标 |
| --- | --- | --- | --- | --- |
| 偏好提取 | 2 | longmemeval_cleaned_2025, personachat_2018 | — | ✅ |
| 知识检索 | 4 | longmemeval_cleaned_2025, longmemeval_v2_2026, t2ranking_2023, dureader_retrieval_2022 | msmarco_2021, trec_tracks_2024 | ✅ |
| 冲突处理 | 2 | longmemeval_cleaned_2025, multiwoz_2_2_2020 | — | ✅ |
| 精准遗忘 | 2 | longmemeval_cleaned_2025, machine_unlearning_bench_2025（本次新增） | — | ✅ |
| Tool Result | 3 | longmemeval_v2_2026, stabletoolbench_2024, toolbench_2024 | — | ✅ |
| 端到端会话 | 2 | longmemeval_cleaned_2025, longmemeval_v2_2026 | — | ✅ |

修订说明：此前版本的"知识检索 6 个候选"将 msmarco、trec 两个方法论参考计入，口径已修正为 4 个正式候选（仍满足 ≥2 标准）。BPMN 为结构参考，不归入六类任务。

登记完整性待人工核验项（不阻塞覆盖结论，Gate 2 批准前需 Reviewer 确认）：

- personachat_2018：version 待核验，data_url 未登记
- msmarco_2021：paper 待核验（version 已于 2026-09-01 复查更新为可访问），data_url 未登记
- toolbench_2024：data_url 未登记

## 三、新增数据集详情

machine-unlearning-bench/data-unlearning-bench

- 任务：精准遗忘（辅助参考）
- 来源：HuggingFace
- 许可证：MIT（2026-09-01 复查确认：`python scripts/oneclick/check_unlearning_detail.py` 输出 license=mit，与登记一致）
- 下载量：2567（2026-08-31 查询）
- 论文：https://arxiv.org/abs/2410.23232
- 说明：基于 KLOM 的机器遗忘评估基准，规模 10K~100K 样本
- 定位：公开基准层（A层），作为精准遗忘场景的参考基准，麒麟 OS 实际遗忘数据仍需自建

## 四、Gate 2 结论

**候选覆盖达标：六类任务每类 ≥2 正式候选（方法论/结构参考不计入），覆盖检查脚本退出码 0。**

**Gate 2：待 Reviewer 批准**（不再标记为 PASS）。待确认事项：

1. 登记 integrity 待人工核验项（personachat 版本线索、msmarco 论文链接，见第二节）
2. toolbench/personachat 数据 URL 待人工补充
3. 新增 machine_unlearning_bench_2025 作为精准遗忘参考候选是否接受

（修订说明：此前版本将 Gate 2 标记为 PASS 且声称"11 个数据集 URL 全部可访问"，与登记表实际字段不符；按 Reviewer 审查意见修正为以上表述。）
