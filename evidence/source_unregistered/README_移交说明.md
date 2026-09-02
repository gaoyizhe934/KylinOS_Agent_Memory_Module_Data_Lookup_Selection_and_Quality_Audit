# Workpack License 证据移交包（2026-09-01，B→A 移交）

来源：v1.0 数据工作包时期（2026-08-31~09-01）的 AI 辅助来源核验产出，
由 Annotator B（DGXD01）于 2026-09-01 整理移交。

## 性质声明

- 全部 `license_review.md` / `source_review.md` 为 **AI 草稿**（依据手册附录 C Prompt 03/04 生成），结论仅供 Reviewer 审批参考，不构成最终许可结论
- 原始文件（LICENSE 原文、README、页面存档）为客观存档，可直接作为阶段3证据
- 移交原因：仓库 `evidence/source/` 缺以下材料；A 在阶段3可直接取用，避免重复抓取

## 目录清单（7 个数据集，30 个文件）

| 数据集 | 关键文件 | 填补的缺口 |
| --- | --- | --- |
| dailydialog_2017 | 双镜像交叉验证 + 审查报告 | 仓库未登记此候选（CC BY-NC-SA 4.0） |
| locomo_2024 | CC BY-NC 4.0 LICENSE 原文 | 仓库未登记此候选 |
| msmarco_2021 | Terms 提取文 + 首页存档 | 登记表"待核验"状态的支撑证据 |
| personachat_2018 | parlai_LICENSE + build 脚本 | 同上（数据无许可的结论依据） |
| t2ranking_2023 | HF API metadata + HF 卡片 | Apache-2.0 声明的机读证据 |
| toolbench_2024 | LICENSE 原文（Apache-2.0） | 登记表仅"README 声明"的补强 |
| trec_tracks_2024 | NIST disclaimer 提取 + data 页 | NIST 条款待核验的支撑材料 |

## 取用规则

1. A 取用时**先与仓库 evidence/source/ 同名文件 diff**，择优保留（两处来源时间戳不同，仓库版本可能更新）
2. 取用后文件应并入 `evidence/source/<dataset_id>/`，本移交目录随之删除
3. dailydialog / locomo 若要启用为正式候选，须先补登记卡（阶段2流程）
4. 一切许可结论最终由 Reviewer 在 Gate 3 标记

## 存档修订记录

- 2026-09-01: nist_disclaimer.html 第47行页面自带 Mapbox 公开访问令牌被 GitHub Push Protection 拦截，已替换为 `pk.[REDACTED_BY_PUSH_PROTECTION]`。该令牌为 NIST 网页前端脚本的第三方公开 key，非本项目凭据，打码不影响条款文本存档的完整性。
