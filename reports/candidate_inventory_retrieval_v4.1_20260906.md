# v4.1 D1 Closeout：Retrieval/KB Candidate Inventory（B 侧，DGXD01）— 2026-09-06（v2，Data-R #49 P0/P1 分层）

> 基线：master `78349334`（#45 P04 frozen / #46 / #48 P70 已入）
> 主产物：`reports/candidate_inventory_retrieval_v4.1.json`（分层 fail-closed 口径）

## Retrieval（verified=0）
- **verified_v4.1_candidate_count = 0**（无 canonical v4.1 retrieval candidate-only artifact / requal-completion / Admission 证据）；
- historical gold5（retr_000001..5）：`REQUALIFICATION_REQUIRED / NOT_COUNTED`——历史 kylin_memory_gold_v1.0 candidate_only 文件（第 6 条起重复前 5 模板），不可抵扣 228；
- t2ranking：`source_file`=200 条原文件；`selection_manifest`=#40 select JSON（43 selected，selection_ids_sha256=`25000489…`）；**materialized_v4.1_subset=false**（未 materialize 前不计 verified）；43 全 t2ranking_retrieval_v1，非 G4 PASS；
- **deficit**：verified **228**；t2ranking43 完成 v4.1 normalization+machine precheck 后 conditional **185**；**180 不批准**（历史 gold5 不可计）。

## KB（gross target）
- verified_candidate_count=0；gross_pool_target=520；
- seed_inventory_not_counted（历史/已有 KB 对象待规范化，不减少生成量）；M1-KB BLOCKED → local_candidate_id。

## 请
Data-R 复审 #49（v2 分层口径）；后续：materialize t2ranking43 v4.1 子集 + 补 Retrieval/KB candidate-only → 分批 G1/G3/G4/G5 → P30。
