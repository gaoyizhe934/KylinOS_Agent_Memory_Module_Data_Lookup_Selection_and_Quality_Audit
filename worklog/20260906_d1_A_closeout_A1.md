# Data-A Closeout：A1 10 条 Legacy 实际改造 — 2026-09-06

- 角色：Data-A（lyf-1213）| 分支：feat/A-v4.1-d1-closeout | 载体：#38 分工确认（comment 5556891865）
- 依据：41bf0e2（accepted candidates=10）+ quota amendment（effective=0）+ requal Rev3 fix_fields + a7189f9 §3 A1

## 做了什么
1. 从 data/gold 原始行读出 10 代表全量内容（只读，不改 data/raw/gold）。
2. 按 fix_fields 真实重构为 10 条修复后候选（candidate_only/NON_PRODUCTION/NOT_ADMISSION_APPROVED）：
   - pref 6：topic/global/tool scope remap、update-withdraw、RELABEL non_storable/task_constraint；
   - forg 4：single_item/time_window(+边界)/topic(+PII)/single_item(revoke)；
   - timestamp 10/10 归一合法 ISO（B-L2）；DEV_REG_ONLY 保留 2。
3. 双层结构 + legacy_ref + generation + applied_fixes；自检 validate_rework.py PASS。

## Rev4（#44 终版，Data-R Option b 双轨 template family）
- `req_pref_000003/000004`：top-level `template_family` → `current_template_family=legacy_exposure_rewrite_v1`（共享族，20%）；`legacy_ref.v1_family` 保留原值（历史 lineage 审计，DEV_REG_ONLY，不再 seal）；盲文 repair_plan 驱动 rewrite。
- 其余 8 条 template_family = pinned Legacy 原行 lineage。
- manifest：`template_family_policy=current_generation_with_legacy_lineage_preserved`；`historical_exposure` 审计（含 lineage leak_key）；repair_plan(raw) sha `6a65a264…`。
- 门禁：validator(双轨) PASS；T03 10/10；dedup PASS；**canonical leakage leak=0 exit0**（去掉 ||true/leak-expect）；builder --check MATCH。hashes: pref `22e70836…` / forg `30b5edc1…` / input_hash `3c6c2816…`。
- 10 候选保持 active；`req_forg_000002` PENDING_RECHECK / `req_forg_000003` DATA_R_PII_DECISION；accepted_legacy_effective=0。

## 阻塞（Data-A 到此为止，等他人）
- B1 机器复核 + Data-R 逐条验收签 requalification_status=完成（P04 才逐条计 accepted）。
- M1 FROZEN 后双盲重标为正式 Gold。
- req_forg_000003 PII（客户姓名关联）Data-R 合成/脱敏裁决。
- RELABEL 负例去向（Preference 负例/边界池）Data-R 口径。

## 下一步（等解锁后）
- 若 Data-R 签若干条完成 → 配合台账 03 回填；P04 只按完成条目重算。
- A2：候选工厂 218+ 保持 candidate_only（无新缺口信号前不扩量）。
