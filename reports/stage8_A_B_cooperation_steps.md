# 阶段8 B ↔ A 配合步骤表（2026-09-04）

- 说明：B（DGXD01）不再代行 A 轨；A 轨动作由 Annotator A（lyf-1213）执行。当前 P0 已收口，P1 受 #7 KMA→FROZEN 闸口约束。

| # | 步骤 | A 动作 | B 动作 | 触发/依赖 | 验收 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | KMA FROZEN（#7） | （如参与主仓库协调）确认权威状态 | 记录信号、同步证据/权威副本 | 主仓库 D/E 签署+合并 | 权威版=FROZEN | ⏳ 待主仓库 |
| 1 | 权威收口准备 | 复核权威版差异 | B 就绪工具（5 项已就绪） | #0 后 | 就绪物齐 | ✅ 已就绪/待触发 |
| 2 | P1-1 Schema 收口 | A 更新 schema/enum_dictionary/检索 ref | B 校验 schema_drift_check/schema exit 0、报告 | #0 | 校验通过 | ⬜ 待 FROZEN |
| 3 | P1-2 手册 v2 定稿 | A 去草案措辞定稿（§3/4/5/6/9/11） | B 复核与 registry 单源一致 | #0 | A/B 双核+Reviewer 批准 | ⬜ 待 FROZEN |
| 4 | P1-3 全量重转 | A 跑 KMA 化转换（raw→processed） | B 对账/幂等/报告 | #0 | conversion_report+校验 exit0 | ⬜ 待 FROZEN |
| 5 | P1-4 labels v2 骨架 | A 确认字段口径 | B 用 stage8_labels_skeleton_v2.py 生成骨架 | #2/#3 | 骨架+label_check_v2 | ⬜ 待 FROZEN |
| 6 | P1-5 试标 v2 | A 独立标注 labels_A | B 独立标注 labels_B；各跑 label_check_v2 | #5；A/B 独立禁共享 | 各自文件通过 QA | ⬜ 待 FROZEN+真人 |
| 7 | P1-6 Kappa | 配合修订规则（未达标） | B 跑 stage8_kappa --format kma（registry 单源）→≥0.70 | #6 | Kappa 报告 | ⬜ 待 FROZEN |
| 8 | 8.2 候选草稿 | A 批量生成候选草稿 | B 结构化/enum 校验 | Reviewer 放行 | 校验 exit0 | ⬜ |
| 9 | 8.3 双标/裁决 | A 全量独立标注 | B 一致性+证据包 | A/B 完成 | gold_draft/disagreement | ⬜ |
| 10 | Gate 8 收口 | 配合澄清 | B 汇总证据更新 gate_status | #9 | Reviewer 批准 Gate8 | ⬜ |

## B 已就绪工具（FROZEN 到达即用）
- P1-1 收口清单 / P1-2 定稿清单（reports/stage8_P1_readiness_20260904.md）
- P1-4 骨架生成器 scripts/audit/stage8_labels_skeleton_v2.py
- P1-5 QA scripts/audit/stage8_label_check_v2.py
- P1-6 stage8_kappa.py --format kma（registry 单源；test 9/9）
