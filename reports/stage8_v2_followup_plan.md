# 阶段8 v2 后续计划（B = DGXD01）— 2026-09-04

## 0. 决策记录
- PR #27：**保持 OPEN、不合并**（Reviewer 已 APPROVED@1d06fc8；作为阶段8 v2 工作载体，后续增量继续并入）。
- 试标时机（Reviewer Medium-决策）＝ **方案②：等 KMA FROZEN 后直接按 v2 试标**（避免 v1.3 试标 FROZEN 后重做）。
- Reviewer Low-1（v2 手册行尾空格）：已修复提交。

## 1. 现状基线（已核验）
- master = KMA 对齐基线（PR #26 已合并：schema gold_enum_alignment、KMA_ENUMS/LEGACY_MAP、KMA 标准+D9 入库）。
- #27（feat/B-stage8-kma）内容：重基线说明、A 六类口径草案、标注手册 v2 草案（P1/P2/minor 已闭环）、工具移植（stage8_kappa --format legacy|kma，字段集单一来源 registry/kappa_agreement_fields.json）、字段漂移审计/映射登记/校验脚本、gate_status 记录、v1.3/v2 互指。

## 2. FROZEN 前置（依赖团队/E-D/Reviewer，B 不代行）
| # | 事项 | 责任 | 状态 |
| --- | --- | --- | --- |
| 1 | KMA CANDIDATE_FOR_FREEZE → FROZEN（主仓库签署+合并） | D/E Reviewer | ⬜ |
| 2 | 权威 KMA 副本（CANDIDATE 版）同步入库本仓库 evidence/ | A/B（FROZEN 后） | ⬜ |
| 3 | 裁定清单#1 preference_key 取值策略 | Reviewer | ⬜ |
| 4 | 裁定清单#2 app/task 语义落点（A 已给样例） | E/Reviewer | ⬜ |
| 5 | 裁定清单#3 confidence 换算（A 表 0.95/0.70/0.40） | A/E | ⬜ |
| 6 | 裁定清单#4 checkpoints 评测层定位 + 版本冲突 conflict_type | E/D | ⬜ |
| 7 | retrieval Gold 是否带 version_id（D9） | E/D | ⬜ |

## 3. P0（FROZEN 前，B 可并行、非破坏）
1. 维护 worklog/20260903_KMA_FROZEN_pending_items.md 状态；
2. 起草 canonical labels_A/B 骨架**设计**（基于 v2 草案 + 单一来源字段集；只出方案不改数据）；
3. 与 A 对齐 v2 草案最终措辞（§9 指向 registry 单一来源等）；
4. 明确红线：FROZEN 前不启动正式 30~50 试标、不重转 processed、不建正式 labels 骨架。

## 4. P1（KMA FROZEN 触发后，按序执行）
1. 同步权威 KMA 副本 → schema.json/enum_dictionary 收口 → 手册 v2 定稿；
2. 全量重转 processed（raw/interim 原文保留、evidence 不动）；
3. canonical labels_A/B 骨架落地 + enum/结构校验（schema_drift_check 适配）；
4. 试标集 v2（沿用样本池或重建）→ A/B 独立试标 30~50 → B 跑 stage8_kappa（registry 单一来源字段集）→ Kappa≥0.70；
5. Reviewer 放行 → 8.2 候选草稿 → 8.3 双标/裁决 → Gate 8。

## 5. 下一步动作（B，非破坏）
- 本计划登记 + Low-1 提交（本 PR）；
- P0 第 2 项 labels 骨架设计文档准备（供 FROZEN 后直接落地）；
- 待 FROZEN/裁定信号后转入 P1。
