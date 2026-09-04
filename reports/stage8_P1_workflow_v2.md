# 阶段8 P1 衔接工作流（2026-09-04 发布，B = DGXD01）

## 0. 状态基线（已核验）
- #27 已合并 master（e1608b6）：P0 收口（口径/手册 v2/工具/单源/漂移/签署）+ P1-1（schema/enum 收口 + #10 sensitivity）已入库；
- 本仓库 #7 KMA→FROZEN 认定达成（df8cdf6，schema kma_alignment.status=FROZEN；主仓库在线文档仍 CANDIDATE——以本仓库认定推进，差异已协调）。

## 1. 工作流（P1 按批次、独立新 PR 推进；不再使用巨型长开 PR）
| 批次 | 内容 | A 动作 | B 动作 | Reviewer | 状态 |
| --- | --- | --- | --- | --- | --- |
| P1-1 | Schema/enum 收口 + sensitivity(#10) | 完成（b6a13c3） | 校验/对账通过 | 已合 #27 | ✅ |
| P1-2 | 标注手册 v2 定稿 | 去草案措辞、§3-§11 复核 | 与 registry 单源一致性复核 | 批次 PR 批准 | ⬜ 待 A |
| P1-3 | 全量重转 processed（KMA 化） | 跑转换（raw→processed，禁 mock） | 对账（条数/枚举/时间戳 UTC .sssZ/raw_id/幂等）报告 | 批次 PR 批准 | ⬜ 待 A |
| P1-4 | labels_A/B v2 骨架 | 确认字段口径 | stage8_labels_skeleton_v2.py 生成 + label_check_v2 | 批次 PR 批准 | ⬜ 待 P1-2/3 |
| P1-5 | 试标 v2（30~50/人） | 独立标注 labels_A | 独立标注 labels_B | 监督独立性 | ⬜ 待 P1-4 |
| P1-6 | Kappa | 未达标配合修订 | stage8_kappa --format kma（registry 单源）→≥0.70 | 放行 8.2 | ⬜ 待 P1-5 |
| 8.2 | 候选草稿 | A 批量生成 | B 结构化/enum 校验 | 放行 | ⬜ |
| 8.3 | 双标/裁决 | A 全量独立标注 | B 一致性+证据包 | 裁决 gold_draft/disagreement | ⬜ |
| Gate8 | 收口 | 配合澄清 | B 汇总证据更新 gate_status | 批准 Gate8 | ⬜ |

## 2. 批次纪律与验收
- 每批 = 独立分支 + PR（基于 master，批间按序合并），diff 小、独立 review；
- 每批交付含校验/测试 exit 码；数据批（P1-3）附对账报告；
- 红线：A/B 独立标注禁共享答案；禁 mock（封存=麒麟 VM 真实回放）；FROZEN 后不回归旧口径；
- 本 PR 为 P1 衔接工作流入口（轻量，不承载大批改动）；后续批次 PR 在本 PR comment 登记链接。

## 3. B 就绪工具（master 已含，供各批次直接调用）
- stage8_kappa.py --format kma（registry 单源）、stage8_trial_sample.py、stage8_labels_skeleton_v2.py、stage8_label_check_v2.py、schema_drift_check.py；test 9/9 PASS。
