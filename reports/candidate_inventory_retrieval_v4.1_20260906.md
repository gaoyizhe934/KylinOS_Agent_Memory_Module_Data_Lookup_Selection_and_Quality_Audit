# v4.1 D1 Closeout：Retrieval/KB Candidate Inventory（B 侧，DGXD01）— 2026-09-06

> 基线：master `ad4781f`（#45 P04 frozen 5124879366、#48 P70 快照封存）
> 目的：Data-R #48 建议"先盘存再补池"，不把 P04 的 228/520 当从零新增量
> 主产物：`reports/candidate_inventory_retrieval_v4.1.json`

## Retrieval 盘存
| 来源 | 计数 | v4.1 eligibility |
| --- | ---: | --- |
| v4.1 candidate-only 新批 | **0** | master 无独立 retrieval candidate-only jsonl（A P20-23 无 retrieval；P21 未产出） |
| t2ranking 43（G4 select） | 43 | review_status=candidate_only；license t2ranking_2023 已批；**source-cap prep（非 G4 PASS）**，P30 admitted 验证 |
| gold 5 真查询 | 5 | A3 可复用（retr_000001..5） |
| 历史 D9 queryset 36 | 不计 | 非 v4.1 candidate-only 批 |
| **可复用基础** | **48** | — |
| **候选池目标** | **228** | 缺口：保守 ≈228（只算新批）或 ≈180（48 经 P30 验证计入）——口径待 Data-R |

## KB 盘存
- KB candidate-only：**0**（无 KB candidate jsonl）→ 候选池目标 520 缺口 ≈520；
- M1-KB BLOCKED → 仅 `local_candidate_id + PRODUCTION_BINDING_PENDING`；生成 prep 条件待 Data-R（已在 #48 comment 提请）。

## 边界
- public-derived 仅消费已批源（t2ranking_2023）；其余 12 license 未批只能 prep；
- t2ranking 43 非 G4 PASS；P30 admitted Retrieval 全集复算 source/template/near；
- M1/M1-KB/M3 BLOCKED → production_truth_allowed=false；本 inventory 为 candidate-only prep 非 Gold。

## 请
1. Data-R：定 Retrieval deficit 口径（228/180）与 KB 520 prep 生成授权（见 #48 comment 决策项）；
2. 后续：按 deficit 生成 Retrieval/KB candidate-only → 分批 G1/G3/G4/G5 → P30。
