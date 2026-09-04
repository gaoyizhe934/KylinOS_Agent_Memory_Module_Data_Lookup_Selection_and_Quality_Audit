# 阶段8 P1 就绪包（A+B，非破坏）— 2026-09-04

- 闸口：#7 KMA→FROZEN 未达成（主仓库仍 CANDIDATE_FOR_FREEZE）；本包为 FROZEN 前就绪物，不重转 processed、不生成正式 labels、不试标。
- 对应：reports/stage8_P1_execution_checklist.md 各批次；FROZEN 到达后按本包直接转正执行。

## P1-1 · Schema 权威收口（候选清单，FROZEN 后执行）
1. schema.json kma_alignment：status → FROZEN（随权威版更新），reference 指向 evidence/.../KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md（已就位）；
2. enum_dictionary.json：按权威候选补全/对齐词表（含检索 forbidden 8 类、conflict_type/preference_scope 等 canonical 值域），保留 eval_or_legacy 分层标注；
3. 检索 gold：落地 memory_id+version_id（retrieval_ref，D9/#4.3 裁定）；
4. 评测层字段显式 eval_ 前缀标注（#10 D 确认）；
5. 校验：python scripts/audit/schema_drift_check.py exit 0 + schema 校验；报告对照。

## P1-2 · 标注手册 v2 定稿（候选动作，FROZEN 后执行）
1. 去除“草案/裁定落点版”措辞 → 定稿版头；
2. §9 保持引用 registry/kappa_agreement_fields.json 单一来源（已就位）；
3. §11 状态表更新（#7 → FROZEN）；核对 §3/§4/§5/§6 与权威候选一致；
4. A/B 双核 + Reviewer 批准定稿。

## P1-3 · 全量重转预案（FROZEN 后执行；现不运行——转换脚本就地写 data/processed，避免副作用）
1. 步骤：convert 脚本 KMA 化（KMA_ENUMS/LEGACY 已内置审计）→ 由 raw/interim 原文重转（raw 只读、evidence 不动、禁 mock）；
2. 对账项：条数 715+、字段/枚举 canonical、timestamp UTC .sssZ、raw_id 溯源、幂等（test_convert）；
3. 交付：conversion_report 更新 + 校验 exit 0；PR 独立批次。

## P1-4 · labels_A/B v2 骨架草稿（示意；正式文件 FROZEN 后由工具生成）
- 设计：reports/stage8_v2_labels_skeleton_design.md（已就位）；字段集单一来源 registry/kappa_agreement_fields.json。
- 结构：sample_id / task_type / gold（canonical 字段）/ evidence；review_status 评测层分离。
- 示例（preference 空骨架，示意）:
  {"sample_id":"pref_000001","task_type":"preference_extraction","gold":{"expression_type":"","preference_scope":"","preference_key":"","preference_value":"","confidence_score":null,"should_persist":null,"is_temporary":null,"memory_status":"","version":1,"evidence_event_ids":[]},"evidence":[]}

## P1-6 · Kappa 工具自测（已 PASS，就绪）
- stage8_kappa.py --format kma：field_source=registry/kappa_agreement_fields.json；冒烟 Kappa=1.0；
- test：9/9 PASS（含 registry loader 含 preference_key）；schema_drift_check exit 0。

## 转正条件与顺序
- #7 FROZEN（主仓库 D/E 签署+合并）→ 权威副本入库确认 → 按 P1-1→P1-6 以独立新 PR 批次执行（不再堆积 #27）。
