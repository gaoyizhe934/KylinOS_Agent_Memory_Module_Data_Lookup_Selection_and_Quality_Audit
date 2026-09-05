# 基于 v4 手册的现有内容漏洞修改方案（DGXD01，2026-09-05）

> ⚠️ **PRE-v4.1 / HISTORICAL ANALYSIS**：本文档形成于 v4.1 规则基线之前，分析 v4 手册（完整版方案 v3）的缺口；**仅作历史追溯，不构成现行执行口径**。
> 现行执行基线 = **v4.1 三件套**（SOP/台账/Prompt Pack，docs PR #32）；v4/完整版方案 = 历史设计基线。
> 对象：数据仓库现有内容（#31 分支 feat/B-stage8-p1-full 及 master 已合内容，供 v4.1 落地参考）。
> 方法：逐项对照 v4 手册要求 → 实证核对现状 → 标注漏洞 → 给修改方案与验收。

---

## 一、漏洞总览（对照 v4 手册）

| # | 漏洞 | v4 手册要求 | 实证现状 | 严重度 |
| --- | --- | --- | --- | --- |
| G1 | processed 五类 team_authored 仍是 v1 模板母体 | 正式 Gold 必须真实可溯源（禁 mock） | processed：conflict 40 / e2e 15 / retrieval 60 / forgetting 40 / preference 60 **全部 team_authored、public=0**（旧模板 88~93% 重复、占位"旧记忆/新指令"） | 🔴 High |
| G2 | scope 语义未人工复核 | Gate「KMA Mapping」：scope 人工复核，未知真值不静默默认 | processed preference 60 条 scope 仍机械映射（"周报→tool"等，30 tool/20 global/10 session），无人工语义复核记录 | 🔴 High |
| G3 | 候选规模远低于 1.3× 目标 | 1.3× candidate 池（Preference 300 / Retrieval Q 230 / Conflict 165 / Forget 130 / Tool 150 / E2E 45 / KB 520） | v3 候选仅 46（pref10/retr12/conf8/forg8/e2e8），tool/e2e 无池 | 🔴 High |
| G4 | KB 缺失 → retrieval knowledge_id 无法闭环 | 400 Memory KB；knowledge_id 可解析 | 无 data/kb；processed retrieval knowledge_id 260/260 缺（High-4 未闭环） | 🔴 High |
| G5 | 盲包仅单一 context，非 A/B 双盲隔离 | blind_context_A/B 不同随机顺序、无对方结果 | 仅 trial_v3_context.jsonl 单一文件 | 🟡 Medium |
| G6 | 流水线工具全部缺失 | run_v4_pipeline / provenance / admission / near_dup / blind_packets / label_console / disagreement / runtime_import / split_grouped / seal / handoff | scripts 内无任何 v4 工具 | 🟡 Medium |
| G7 | Runtime 无证据 | 35 session → 125 Tool + 35 E2E（真实回放，禁静态冒充） | runtime_replay/sessions 空；tool_result 无候选 | 🔴 High |
| G8 | registry 缺 v4 清单 | provenance_registry_v4 / leaked_content_registry / source_registry 完整 | 无 provenance_registry_v4.jsonl、无 leaked_content_registry.json | 🟡 Medium |
| G9 | AI 候选缺生成溯源 | OS 候选记录 generation_id/prompt/seed/model | rebuild_candidates_*.py 无 generation 元数据字段 | 🟡 Medium |
| G10 | P1(#31) 与 P2 边界需澄清 | Table 17：#31 只做 P1，P2-A/P2-B 另立 | #31 已含 46 候选/40 试标/context（P1 校准层 OK）；785 大规模尚未开 P2 | 🟢 边界清晰（执行中） |

---

## 二、修改方案（按优先级/依赖序）

### Phase 1 — 封死 P1 门禁（在 #31 内闭环，不扩大量）
1. **G2 scope 人工复核**（交 A）：对进入试标的 preference 样本逐条判 topic/tool/global/session；不确定输出 NEEDS_REVIEW，禁止默认 tool；
   - 产出：scope_review 清单 + SCOPE_MAP 修正 + 断言测试；B 复核。
2. **G5 双盲包**：由 trial_v3_context.jsonl 生成 blind_context_A / blind_context_B（不同随机顺序）；加"无对方标签/gold"断言。
3. **G1/G4 登记（不 mock）**：processed team_authored 旧模板**标记不进入 v4 Gate**（candidate_only 审计保留）；KB 依赖登记 NOT_PRODUCTION，等 P2-B。
4. 复跑：label_check / schema / reconcile / kappa（40 校准）→ Kappa≥0.70 → #31 可复审。

### Phase 2 — P2-A Data Factory（新 PR，纯工具无 Gold）
5. **G6 工具链**：新建 run_v4_pipeline.py / provenance_resolver.py / candidate_factory_*(6) / admission_gate_v4.py / near_dup_scan.py / build_blind_packets.py / label_console.py / disagreement_report.py / runtime_import.py / split_grouped.py / seal_dataset.py / handoff_pack.py；
6. **G8 registry**：新增 provenance_registry_v4.jsonl、leaked_content_registry.json（旧泄漏 fingerprint 登记）、source_registry 扩展；
7. **G9 溯源字段**：candidate_factory 输出带 generation_id/prompt_version/seed/model/source。

### Phase 3 — P2-B Half-Scale 数据（依赖 P2-A + Runtime；按手册 5 天排程）
8. **G3 候选扩量至 1.3×**：pref 300 / retrQ 230 / conf 165 / forg 130 / tool 150 / e2e 45 / KB 520；真实来源优先 + OS spec 变体（AI 候选带溯源）；
9. **G4 KB**：建 data/kb/memory_kb_v4.jsonl（400）→ 回填 retrieval knowledge_id；
10. **G7 Runtime**：35 session（Data-B 操作 + 麒麟 VM 真实回放，禁 StableToolBench 冒充）→ 125 Tool + 35 E2E；
11. Admission Gate（G1-G5 全过）→ A/B 双盲 785 → Reviewer 100% 分歧裁决 → split 50/20/30 → seal → DATA_RELEASE_v4。

---

## 三、验收（每项闭环须有证据）
- scope：A 复核清单 + SCOPE_MAP diff + 断言测试 exit 0；
- 双盲包：A/B 顺序不同、无对方/gold 字段断言通过；
- 工具链：单测 + 幂等 + fail-closed（缺失即 BLOCKED）；
- 候选：1.3× 池数量达标 + provenance 0 unresolved + dedup 0 + 无泄漏 fingerprint；
- KB：400 条 + retrieval knowledge_id 可解析 100%；
- Runtime：35 session 与 frozen build 对应，Tool/E2E 证据可核验；
- Kappa≥0.70；sealed 仅 R 持有；release 带 SHA256 + compatibility manifest。

---

## 四、需协调/授权项
1. Phase 1（#31 内）scope 复核交 A、双盲包 B 生成——需 A/Reviewer 确认门禁关闭标准；
2. P2-A / P2-B 新建 PR——需用户授权（P2-A 可先立，纯工具）；
3. Runtime 35 session 的主仓冻结 build / Liaison / 麒麟 VM——外部依赖，需协调方与主仓；
4. processed 旧模板处置：标记不进入 v4 Gate（不删除，保留审计）需 Reviewer 认可。

## 五、立即建议动作（可先做、不越红线）
- [ ] P2-A 工具链立项（脚本，无 Gold）——待授权；
- [ ] G5 双盲包脚本（基于 trial_v3_context 生成 A/B）——可在 #31 或 P2-A；
- [ ] G2 scope 复核清单准备（交 A）。
