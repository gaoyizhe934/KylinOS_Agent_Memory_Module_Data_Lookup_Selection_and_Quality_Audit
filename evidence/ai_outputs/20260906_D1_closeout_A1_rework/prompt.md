# Prompt: Data-A Closeout A1 — 10 条 Legacy REWORK/RELABEL 实际改造

## 角色
Data-A（lyf-1213）AI 辅助；v4.1 基线；分支 feat/A-v4.1-d1-closeout（master c21ee694，PR#37 已合并）。

## 任务（分工文档 a7189f9 §3 A1）
按 requal Rev3 fix_fields，把 10 个代表样本（pref_000001/2/5/4/6/3 + forg_000001..4）从 data/gold 原始行
**真实重构**为 v4.1 修复后候选（candidate_only / NON_PRODUCTION），非换字段：
- timestamp YYYY-MM-DDN → 合法 ISO（B-L2）；
- scope/mode/RELABEL 按 fix_fields 与 Round3 §D D1–D4；
- 保留 DEV_REG_ONLY（pref_000003/000004 sealed 暴露）；
- 双层结构：blind_visible（无答案）+ design_metadata（legacy_ref/generation/applied_fixes/split_eligibility）。

## 边界（严格）
- 不写 human_decision / final_label / gold；不改 data/raw 与 data/gold；
- 候选需 G2 可追溯（scenario_family/scope 提案 + legacy_ref + generation manifest + template_family 溯源）；
- 不产 production knowledge_id；不做盲标；不看 B 标签。

## 输入
- data/gold/{dev,regression,sealed_test}/{preference_extraction,precise_forgetting}.jsonl（10 原始行）
- reports/legacy_semantic_requal_A.jsonl（Rev3 fix_fields）
- reports/v4.1_D1_closeout_ABR_roles_20260906.md（a7189f9）
- 41bf0e2 终裁 + quota_accepted_amendment
