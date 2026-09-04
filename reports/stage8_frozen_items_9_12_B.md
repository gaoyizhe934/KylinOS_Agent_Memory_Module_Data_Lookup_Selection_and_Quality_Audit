# FROZEN 清单 #9–#12 处理记录（B = DGXD01）— 2026-09-04

## #9 preference_scope / conflict_type 来源核对（D3 L2）
- 证据：主仓库 D3_MEMORY_BUSINESS_CONTRACT_V1.md（CANDIDATE_FOR_FREEZE，543 行）：
  - L194：`preference_scope` = FROZEN_BUSINESS_SEMANTIC（五值业务语义冻结；A Provider 草稿 scope 差异见冲突登记 #5）；
  - L242：`conflict_type` = FROZEN_BUSINESS_SEMANTIC（五值业务语义冻结）；
  - L254/L316：`contradiction`/`temporal_inconsistency` 判定阈值算法 REJECTED→DEFERRED（待 B，HD-SCHEMA-04）——E 轨不可冻结。
- 核对结论：本仓库编码的 preference_scope（global/topic/tool/session/time_window）与 conflict_type（contradiction/temporal_inconsistency/source_conflict/preference_conflict/scope_ambiguity）**来源已落点 D3(L2) FROZEN_BUSINESS_SEMANTIC**，与权威候选一致；判定阈值算法属 B 轨实现层（DEFERRED，不在数据包冻结）。
- 状态：#9 ✅ B 核对完成 → 待 E/D 终裁盖章。

## #10 D 轨物理映射确认单（Medium-1，另案）
- 原则建议：数据包 gold/评测层字段**不进入生产 SQLite/Vector 物理落库命名空间**；评测侧建议 `eval_` 前缀命名空间隔离，避免与物理列冲突（候选 §4 不冻结宿主物理字段）。
- 待办：请 D 轨确认“评测层字段 ↔ 物理落库命名”不冲突；不阻塞 #27 定义层。
- 状态：#10 🟡 材料已备 → 待 D 确认。

## #11 E 轨映射签名确认单（Low-1）
- 请 E 轨签名对象：registry/field_mapping.json（30 行 gold↔canonical 映射）+ registry/kappa_agreement_fields.json（Kappa 一致字段集单一来源）+ reports/schema_drift_audit_B_20260904.md（漂移清单）。
- 状态：#11 🟡 材料已备 → 待 E 签名。

## #12 schema.json kma_alignment 切换复核
- 已更新 data/processed/schema.json kma_alignment：status → CANDIDATE_FOR_FREEZE（主仓库权威，2026-09-03，main@889b7553；尚未 FROZEN）；reference/main_authoritative_candidate 指向 evidence/.../KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md。
- 校验：schema.json JSON 合法；未改任何 enum/gold 值。
- 状态：#12 ✅ 已完成。
