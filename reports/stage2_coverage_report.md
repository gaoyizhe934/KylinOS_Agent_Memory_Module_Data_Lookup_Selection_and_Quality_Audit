# 阶段 2：候选查找与登记报告

执行人：Annotator A（lyf-1213）
日期：2026-08-31（2026-09-01 两轮修订：第一轮修正 URL 统计口径与 Gate 2 结论表述；第二轮按 Reviewer 第二轮复审意见补齐 5 项 data_url、将 URL 可访问性纳入检查失败条件、ToolBench 官方数据入口失效如实上报）

## 一、现有数据集 URL 体检结果

复查命令（仓库根目录执行；脚本从仓库根目录解析路径，代理为可选配置，
**严格模式：存在 EMPTY/ERROR/TIMEOUT 任一情形即退出码 1**）：

```powershell
python scripts/oneclick/stage2_check_urls.py
```

原始输出存档：`evidence/audit/stage2_url_check_output_20260901.md`（2026-09-01 实测，直连、TLS 校验开启，退出码 1）

| 数据集 | 官方URL | 数据URL | 结论 |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ✅ OK(200) | ✅ OK(200) | 保留 |
| longmemeval_v2_2026 | ✅ OK(200) | ✅ OK(200) | 保留 |
| stabletoolbench_2024 | ✅ OK(200) | ✅ OK(200) | 保留 |
| toolbench_2024 | ✅ OK(200) | ❌ 官方数据入口失效（Google Drive 文件夹 404，详见下方核验记录与证据存档） | 待 Reviewer 裁决处置 |
| t2ranking_2023 | ✅ OK(200) | ✅ OK(200) | 保留 |
| dureader_retrieval_2022 | ✅ OK(200) | ✅ OK(200) | 保留 |
| multiwoz_2_2_2020 | ✅ OK(200) | ✅ OK(200) | 保留 |
| personachat_2018 | ✅ OK(200) | ✅ OK(200)（官方入口 http://parl.ai/downloads/personachat/personachat.tgz，ParlAI build.py 提供官方 SHA256；版本线索已确认为 v1.0） | 保留 |
| msmarco_2021 | ✅ OK(200) | ✅ OK(200)（HF 官方 microsoft 组织页面；官方 Azure blob 直链自动检查 409，已在登记表备注） | 保留（方法论参考） |
| trec_tracks_2024 | ✅ OK(200) | ✅ OK(200)（数据门户 data.html；/data/ 目录自动检查 403，已在登记表备注） | 保留（方法论参考） |
| bpmn_2_0_2013 | ✅ OK(200) | ✅ OK(200)（官方规范 PDF 入口） | 保留（结构参考） |
| machine_unlearning_bench_2025 | ✅ OK(200) | ✅ OK(200) | 保留（本次新增） |

**统计口径与实测结果（2026-09-01 第二轮复测）：**

- 官方 URL：12/12 可访问（HTTP 200）
- 数据 URL：**11/12 已登记且可访问；1/12（toolbench_2024）已登记但官方入口失效（HTTP 404）**
- `stage2_check_urls.py` 严格模式退出码 1，如实反映 toolbench_2024 数据入口失效
- toolbench_2024 失效核验记录（7 种 URL 形式 + 对照文件 + GitHub Releases + HF 官方组织查询）见
  `evidence/audit/stage2_url_check_output_20260901.md` 末节；对照组（同 README 内另一公开 Drive 文件返回 200）证明 404 为真实失效而非反爬
- 处置建议（Gate 3 范畴，待 Reviewer 裁决）：toolbench_2024 降级为方法论参考或淘汰；Tool Result 任务仍有 stabletoolbench_2024、longmemeval_v2_2026 两个正式候选，覆盖不受影响
- 修订说明（第二轮）：5 个此前未登记 data_url 的数据集已全部补齐官方数据入口并复测（personachat→ParlAI 官方 tgz、msmarco→HF 官方 microsoft/ms_marco、trec→数据门户 data.html、bpmn→官方规范 PDF、toolbench→官方 README 给出的 Drive 文件夹）；其中 toolbench 官方入口经多形式复测确认为已失效，不再以"需手动下载"掩盖

## 二、候选覆盖检查

复查命令（仓库根目录执行）：

```powershell
python scripts/oneclick/stage2_coverage_check.py
```

原始输出存档：`evidence/audit/stage2_coverage_check_output_20260901.md`（2026-09-01 复跑，退出码 0）

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

**Gate 2 登记完整性（第二轮修订后）**：五项字段（正式名称/版本线索/官方来源/任务说明/数据入口）12 个数据集全部齐备，无 ❌缺失；此前待人工核验的 personachat 版本线索已通过 ParlAI 官方 build.py 确认为 v1.0（含官方 SHA256）。

仍待 Reviewer 确认项（不阻塞覆盖结论）：

- msmarco_2021 论文链接待人工核验（paper 字段）
- toolbench_2024 处置（数据入口失效，见第一节）

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

**Gate 2：待 Reviewer 批准**（不标记为 PASS）。待确认事项：

1. toolbench_2024 数据入口失效的处置裁决（降级为方法论参考 / 淘汰；Gate 3 范畴）——裁决后需同步更新登记表 conclusion 并复跑 `stage2_check_urls.py`，届时退出码应转为 0
2. 新增 machine_unlearning_bench_2025 作为精准遗忘参考候选是否接受
3. msmarco_2021 论文链接人工核验

（修订说明：此前版本将 Gate 2 标记为 PASS 且声称"11 个数据集 URL 全部可访问"，与登记表实际字段不符；第一轮修订修正口径；第二轮修订补齐全部数据入口并将 URL 可访问性纳入检查失败条件——当前 toolbench_2024 一项失败如实呈现，待 Reviewer 裁决。）
