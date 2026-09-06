# B2 P04 动态配额重算（Data-B，2026-09-06）

- 脚本：`scripts/v4/d1_closeout_p04_recompute.py`
- 规则：v4.1 SOP §7/Q7 + 台账 04 —— `accepted_legacy = REUSE/REWORK/RELABEL 且 requalification_status=完成`（非 Runtime）；`new_needed = max(target-accepted,0)`；`candidate = ceil(new_needed×1.3)`（Runtime ×1.0 不可抵）。
- 用法：
  - 当前（Data-R 签 0）：`python scripts/v4/d1_closeout_p04_recompute.py --requal reports/legacy_semantic_requal_A.jsonl` → effective=0、Gold new=785、candidate=974（与台账一致）
  - Data-R 签后：`--completed <签完成 sample_id 清单>` → 按完成条目重算 accepted 与配额
- 状态：B2 prep；正式 P04 冻结需 Data-R 逐条签 `requalification_status=完成` 后执行（B 不代签、不产 Gold）。
