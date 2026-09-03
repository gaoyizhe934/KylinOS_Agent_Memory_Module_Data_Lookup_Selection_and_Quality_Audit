# KMA FROZEN 前必办清单（登记，响应 Reviewer Low-1）

- 登记日期：2026-09-03
- 关联：PR #26（阶段1/7 KMA 对齐）；KMA=FREEZE_PROPOSAL。

| # | 事项 | 责任 | 状态 |
| --- | --- | --- | --- |
| 1 | preference_key 取值策略（模板族约束开放字符串，勿再造枚举） | A/B 定稿 + Reviewer 裁定 | ⬜ |
| 2 | 旧 scope app/task 语义落点（不机械映射 app→tool、task→topic） | Reviewer 裁定 | ⬜ |
| 3 | confidence 高/中/低 → confidence_score [0,1] 固定换算口径 | A/B 定稿 | ⬜ |
| 4 | forgetting checkpoints 定位：保留为评测层验证时点，不进业务状态 | Reviewer 裁定 | ⬜ |
| 5 | KMA_LEGACY_MAP 与 B 校验脚本核对（无冲突，需在 #25 合并后补齐 enum_check --kma） | B | ⬜ |
| 6 | D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl 补档入 evidence/source/kma_unified_data_format_FREEZE_V1/ | B 轨 PR#88 / A 提供 | ⬜ |
| 7 | KMA 转 FROZEN（签署 + 合并 main） | D/E Reviewer | ⬜ |
| 8 | 全量重转 processed gold + 重建阶段8标注枚举/骨架/试标 | A/B（FROZEN 后） | ⬜ |

FROZEN 达成前：不做破坏性重转、不打断阶段8试标；每项闭环后在状态列更新为 ✅ 并附证据位置。
