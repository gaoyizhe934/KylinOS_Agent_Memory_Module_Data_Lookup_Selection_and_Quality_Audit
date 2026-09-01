# Gate 状态 2026-09-01（master，PR#1 合并后更新）

依据 v2.0 重建计划修订版，每阶段 Gate 未获 Reviewer 人工确认不得进入下一阶段。

| Gate | 阶段 | 要求 | 当前状态 | 产出物 |
| --- | --- | --- | --- | --- |
| Gate 0 | 阶段 0 | 目录可用，负责人明确，raw 目录只读/不直接修改 | ✅ Reviewer 已批准（PR#1，2026-09-01） | worklog/owners.md, reports/stage0_checklist.md, 目录骨架 |
| Gate 1 | 阶段 1 | 每项要求至少对应一个子集和一个可计算指标 | ✅ Reviewer 已批准（PR#1，2026-09-01） | reports/requirement_data_mapping_v2.md |
| Gate 2 | 阶段 2 | 所有候选有正式名称、版本线索、官方来源和任务说明 | ✅ Reviewer 已批准（PR#1，2026-09-01，含 5 项裁决） | registry/dataset_registry.csv, reports/stage2_coverage_report.md |
| Gate 3 | 阶段 3 | Reviewer 明确标记允许试用/需确认/淘汰 | 🔶 进行中（PR#1 审批遗留三项待办已清偿，见下） | evidence/source/*（12 候选证据包） |
| Gate 4 | 阶段 4 | 样本可解析，标签定义可理解，人工抽检通过 | ⏳ 下一阶段 |
| Gate 5 | 阶段 5 | 核心候选 >= 80 分；补充候选 >= 65 分 | ⏳ 下一阶段 |
| Gate 6 | 阶段 6 | 再次下载可得到同一版本；文件数量和哈希完整 | ⏳ 下一阶段 |
| Gate 7 | 阶段 7 | 每条 processed 样本可追溯到 raw_id | ⏳ 下一阶段 |
| Gate 8 | 阶段 8 | Kappa >= 0.70，分歧有裁决，所有标签有 evidence | ⏳ 下一阶段 |
| Gate 9 | 阶段 9 | 无用户/会话/模板泄漏；封存集哈希固定 | ⏳ 下一阶段 |
| Gate 10 | 阶段 10 | 命令、环境、原始日志、失败样本和统计脚本齐全 | ⏳ 下一阶段 |
| Gate 11 | 阶段 11 | 另一名同事可从文档复现；报告数字均能回到原始文件 | ⏳ 下一阶段 |

## 当前分支完成状态

- [x] 阶段 0：工作区初始化 — 目录验证 + 分工表更新
- [x] 阶段 1：需求—数据映射 — v2.0 六项指标映射完成
- [x] 阶段 2：候选查找与登记 — 12 个数据集登记，六类任务候选覆盖检查通过（每类 ≥2 正式候选，方法论/结构参考不计入；复查命令 `python scripts/oneclick/stage2_coverage_check.py`，退出码 0，登记完整性五项字段全部齐备）。URL 体检 2026-09-01 第二轮复测：官方 URL 12/12 可访问，数据 URL 11/12 已登记且可访问，toolbench_2024 官方 Drive 数据入口失效（404，核验记录见 evidence/audit/stage2_url_check_output_20260901.md，待 Reviewer 裁决处置）；`stage2_check_urls.py` 严格模式退出码 1 如实反映该项失败（详见 reports/stage2_coverage_report.md）
- [ ] 阶段 3：来源、版本与 License 核验 — 进行中（feat/B-stage3-prep 分支）
- [ ] 阶段 4~11：待后续分支推进

## Gate 3 待办清偿记录（2026-09-01，B = DGXD01，feat/B-stage3-prep 分支）

PR#1 审批意见（第四节）遗留三项待办，本分支逐一清偿：

| # | 待办 | 处置 | 证据 |
| --- | --- | --- | --- |
| 1 | toolbench_2024 降级执行（裁决: 降为方法论参考，不进首版封存） | 登记表 conclusion 已更新为「方法论参考（不采用）」并注明裁决依据；`stage2_check_urls.py` 增加方法论参考候选 data_url 跳过逻辑（official_url 仍验收），严格模式复跑**退出码 0**（Reviewer 要求「届时退出码应转为 0」达成） | evidence/audit/stage2_url_check_output_20260901_toolbench_downgraded.md |
| 2 | msmarco_2021 论文链接核验 | 核验通过: arXiv:1611.09268（NIPS 2016，MS MARCO 原始论文），官方项目页首段直接引用该链接，arXiv 摘要页 2026-09-01 实测可达；登记表 paper 字段由「待核验」更新 | evidence/source/msmarco_2021/paper_verification_20260901.md |
| 3 | machine_unlearning_bench 证据补齐（即 B 复核报告 F1 不合格项） | 证据包从零建立: 核查脚本输出 + HF API 元数据（cardData.license = "mit"）+ README 原文 + license_review.md（含 B 复核意见: 发布者为社区组织非论文官方，建议 Gate 3 从严标记） | evidence/source/machine_unlearning_bench_2025/（4 个文件） |

另: B 侧 workpack 移交包（7 个数据集 31 个 License 证据文件，2026-08-31 产出于 b-review-stage12 分支）已并入 `evidence/source_workpack_handover/`，供阶段 3 直接取用（移交说明见该目录 README）。

## 说明

`已完成` 表示本分支已产出对应证据/产物；`待 Reviewer 批准` 表示需要人工确认后才能标记为通过。