# D1 开工登记 — B 侧 Legacy 机器审计（P11）— 2026-09-06

- 角色：DGXD01（Data-B）
- 基线：master 5895a42（#32/#33/#34/#36 merged；Closure DATA_R_FROZEN 09:59；D1 启动 09:59）
- 分支：feat/B-stage8-v4.1-d1

## 今日 D1 任务范围（B 侧）
- [x] P11 Legacy 机器审计：465 IN_SCOPE（provenance/dedup/template/leakage）
- [ ] KB/Retrieval 候选准备（M1-KB BLOCKED 前仅 local_candidate_id，后续）
- 不做：不产 Gold、不写 human_decision、不代 A（P10 语义归 A）、不改 raw、不伪造 knowledge_id

## 执行记录
- 抽取 465 IN_SCOPE → data/interim/v4.1_d1_audit/legacy_in_scope_465.jsonl（sha256 4698f5ca6bff06ce751da8e65bed4b13fd69a7ef3b0e4723b2fc8324f36c8c2f）
- provenance_resolver：465/465 UNRESOLVED（rc=2，符合 legacy 无新契约溯源预期）
- dedup_scan：exact dup=0；near 1250 对/265 样本；template 集中度 t2ranking 43% FAIL（rc=2）
- leakage_scan：checked=465；38 sealed 命中（C2 已登记 DEV_REG_ONLY）；2 t2ranking raw_id 碰撞（假阳性）；425 CLEAN（rc=2）
- 聚合：scripts/v4/legacy_machine_audit.py → reports/legacy_machine_audit_v4.1.jsonl（465 行 + summary）

## 结果登记
- 465 全部 machine_status=NEEDS_HUMAN_REVIEW（不代判）
- 产出与阈值判定见 reports/v4.1_D1_B_legacy_machine_audit_20260906.md
- 待 A(P10 语义) + Data-R(t2ranking 43%/near-dup/raw 指纹口径)

## 阻塞/外部依赖
- M1（schema_snapshot）deadline D1 10:30 仍 BLOCKED（主仓 Liaison）；M1 PASS 前 production_truth_allowed=false → B 侧仅做非 Gold 审计/准备
