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

## Rev3（A-followup，响应 #40/#44；PR feat/A-v4.1-d1-closeout-fix）
- ① 10 候选补 top-level `template_family`（= pinned Legacy 原行 template_family，lineage 继承）→ canonical dedup PASS（exact/near 0、每族 10%），修复 100% none BLOCKED。
- ② manifest `repair_plan_sha256` = pinned repair_plan **raw-bytes** sha（LF-normalized），统一 hash contract。
- ③ Data-R #44：`req_pref_000003/000004` 采用 **Option2 LEAK_EXPOSED/BLOCKED**（盲文 semantic-preserving rewrite 已入 repair_plan & builder 生成）；因 lineage template_family 命中 registry template 指纹，leak=2 如实登记 exposed_lineage_blocked，**不计 completion/accepted**；删除全部 REGISTERED_EXPOSURE_ALLOWED/waiver 表述。
- 重生成（master 0cbaf26）：pref `f2048f90…` / forg `30b5edc1…` / input_hash `352a6926…` / repair_plan(raw) `79e9b8da…`；validator/T03/dedup/leak-expect/builder --check 均符合预期（leak=2 = Option2 两候选）。
- CI 增 canonical dedup + leakage(expect) 步；待 Data-R 对 template 指纹处置裁决后，B 再以新 SHA 重跑 B1。

## 阻塞（Data-A 到此为止，等他人）
- B1 机器复核 + Data-R 逐条验收签 requalification_status=完成（P04 才逐条计 accepted）。
- M1 FROZEN 后双盲重标为正式 Gold。
- req_forg_000003 PII（客户姓名关联）Data-R 合成/脱敏裁决。
- RELABEL 负例去向（Preference 负例/边界池）Data-R 口径。

## 下一步（等解锁后）
- 若 Data-R 签若干条完成 → 配合台账 03 回填；P04 只按完成条目重算。
- A2：候选工厂 218+ 保持 candidate_only（无新缺口信号前不扩量）。
