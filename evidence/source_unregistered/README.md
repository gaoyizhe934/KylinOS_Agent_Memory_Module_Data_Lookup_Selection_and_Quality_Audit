# 未登记候选证据暂存目录（source_unregistered）

本目录存放 **未进入 v2.0 阶段 2 登记表（12 个正式候选）** 的数据集证据，
全部来自 Annotator B（DGXD01）2026-09-01 移交的 v1.0 工作包。

## 目录内容

| 数据集 | 关键证据 | B 侧核验结论（AI 草稿） |
| --- | --- | --- |
| dailydialog_2017 | 双镜像交叉验证 + 审查报告 | CC BY-NC-SA 4.0（两个独立镜像一致声明）；13K 闲聊对话，仅作闲聊负样本辅助 |
| locomo_2024 | CC BY-NC 4.0 LICENSE 原文 + README | LoCoMo（ACL 2024，snap-research）：10 段长对话，QA/幻觉/摘要/事件标注，数据在官方仓库内可直连下载 |

原始移交说明见本目录 `README_移交说明.md`（B 侧 2026-09-01 出具）。

## 处置规则

1. 本目录数据集 **不参与** 阶段 3 主体核验与后续 Gate 验收（未登记 = 非正式候选）。
2. 若 Reviewer 决定启用其中任一候选，须先补走阶段 2 登记流程（登记卡 + 覆盖检查），再进入阶段 3 证据核验。
3. 本目录证据仅作登记前的原始材料留档，不构成任何许可结论。

## 移交包取用记录（2026-09-01，A = Data Owner，feat/B-stage3-prep 分支）

- 移交包中 5 个已登记候选（msmarco_2021 / personachat_2018 / t2ranking_2023 / toolbench_2024 / trec_tracks_2024）的证据已按移交说明取用规则**择优并入** `evidence/source/` 对应目录，详见各包 review 文件的"取用与更新记录"小节。
- 移交包中 t2ranking 旧版 HF API 元数据（无 revision SHA）被 v2.0 新抓取的 `api_snapshot_20260901/` 取代，未重复取用。
- 本目录（dailydialog_2017 / locomo_2024 + 移交说明）为移交包仅存未取用部分，按移交说明"取用后移交目录随之删除"规则，`source_workpack_handover/` 已删除。
