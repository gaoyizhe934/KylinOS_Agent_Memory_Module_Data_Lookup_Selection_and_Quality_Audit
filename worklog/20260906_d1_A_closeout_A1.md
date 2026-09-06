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

## Rev3（A-followup，响应 #40 DGXD/Data-R 发现的 A 侧 2 项；新 PR feat/A-v4.1-d1-closeout-fix）
- ① 10 候选补 top-level `template_family`（= legacy_ref.v1_family），修复 canonical dedup 100% none BLOCKED → dedup PASS（exact/near 0、每族 10%）。
- ② manifest `exact_input_proof.repair_plan_sha256` 由 canonical-parse(9d7d9bd0…) 改为 **pinned repair_plan raw-bytes sha `78fe38c1…`**（与 B1 raw-byte hash contract 一致）。
- 重生成：pref `9ad487ce…` / forg `30b5edc1…` / input_hash `ec1580c3…`；validator/T03/builder --check MATCH；leak=2 = req_pref_000004/000003（DEV_REG_ONLY sealed 暴露，策略允许，待 Data-R/B 定 leak-gate 处置）。
- 交付后 B 以新 SHA 重跑 B1（预期 exit0 通过 canonical + manifest 全收口）。

## 阻塞（Data-A 到此为止，等他人）
- B1 机器复核 + Data-R 逐条验收签 requalification_status=完成（P04 才逐条计 accepted）。
- M1 FROZEN 后双盲重标为正式 Gold。
- req_forg_000003 PII（客户姓名关联）Data-R 合成/脱敏裁决。
- RELABEL 负例去向（Preference 负例/边界池）Data-R 口径。

## 下一步（等解锁后）
- 若 Data-R 签若干条完成 → 配合台账 03 回填；P04 只按完成条目重算。
- A2：候选工厂 218+ 保持 candidate_only（无新缺口信号前不扩量）。
