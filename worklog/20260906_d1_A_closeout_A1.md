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

## 响应 Data-R Review #39（Blocking-1/2/3）canonical 化（rev2）
- 改 source_layer=os_controlled_authored + 每样本 scenario_spec_id + 新增 active prompt_ref `P10-A1-rework-v4.1`（prompt_registry.csv）+ legacy_ref lineage。
- builder/validator 迁至 scripts/v4（repo-relative，确定性）：builder 读 data/gold 原行 + requal Rev3 fix_fields + repair_plan；--check 复现 MATCH（input_hash e01610d1…）。
- canonical T03：provenance_resolver checked=10 unresolved=0；CI baseline-validation.yml 新增 3 步（A1 validator / T03 / builder --check）。
- 删除原 evidence 下硬编码本机路径的 build_rework/validate_rework 脚本。

## 阻塞（Data-A 到此为止，等他人）
- B1 机器复核 + Data-R 逐条验收签 requalification_status=完成（P04 才逐条计 accepted）。
- M1 FROZEN 后双盲重标为正式 Gold。
- req_forg_000003 PII（客户姓名关联）Data-R 合成/脱敏裁决。
- RELABEL 负例去向（Preference 负例/边界池）Data-R 口径。

## 下一步（等解锁后）
- 若 Data-R 签若干条完成 → 配合台账 03 回填；P04 只按完成条目重算。
- A2：候选工厂 218+ 保持 candidate_only（无新缺口信号前不扩量）。
