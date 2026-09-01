# Gate 状态 2026-09-01（clean-branch）

依据 v2.0 重建计划修订版，每阶段 Gate 未获 Reviewer 人工确认不得进入下一阶段。

| Gate | 阶段 | 要求 | 当前状态 | 产出物 |
| --- | --- | --- | --- | --- |
| Gate 0 | 阶段 0 | 目录可用，负责人明确，raw 目录只读/不直接修改 | ⚠️ 待 Reviewer 批准 | worklog/owners.md, reports/stage0_checklist.md, 目录骨架 |
| Gate 1 | 阶段 1 | 每项要求至少对应一个子集和一个可计算指标 | ⚠️ 待 Reviewer 批准 | reports/requirement_data_mapping_v2.md |
| Gate 2 | 阶段 2 | 所有候选有正式名称、版本线索、官方来源和任务说明 | ⚠️ 待 Reviewer 批准 | registry/dataset_registry.csv, reports/stage2_coverage_report.md |
| Gate 3 | 阶段 3 | Reviewer 明确标记允许试用/需确认/淘汰 | ⏳ 下一阶段 |
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
- [x] 阶段 2：候选查找与登记 — 12 个数据集登记，六类任务候选覆盖检查通过（每类 ≥2 正式候选，方法论/结构参考不计入；复查命令 `python scripts/oneclick/stage2_coverage_check.py`）。URL 体检 2026-09-01 复查：官方 URL 12/12 可访问，数据 URL 7/12 已登记且可访问、5/12 未登记（详见 reports/stage2_coverage_report.md 修订说明）
- [ ] 阶段 3~11：待后续分支推进

## 说明

`已完成` 表示本分支已产出对应证据/产物；`待 Reviewer 批准` 表示需要人工确认后才能标记为通过。