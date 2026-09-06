# B2 P04 动态配额重算（Data-B，2026-09-06）— v2 正式版

- 脚本：`scripts/v4/d1_closeout_p04_recompute.py`（v2：fail-closed + 正式输出）
- 规则：v4.1 SOP §7/Q7 + 台账 04 —— `accepted_legacy = REUSE/REWORK/RELABEL 且 requalification_status=完成`（非 Runtime）；`new_needed = max(target-accepted,0)`；`candidate = ceil(new_needed×1.3)`（Tool/E2E ×1.0 不可抵）。

## 正式 P04（Data-R #40 Review 5124685158 签署 10 条）
- authority：Data-R #40 APPROVE（20b575e）Requalification Completion Signature（10 条 `requalification_status=完成`）
- requal source：master `reports/legacy_semantic_requal_A.jsonl`（sha256 `c5b217e3d93119e4cb56b06ae46772039698a56b62dc16b4c33ddfe0c1cfafd7`）
- completed 10 条 sha256：`58c838ad1611cb3ec57adfd49800c64851cb806cb5c6d473b5cd13aae82d4752`

| task | target | accepted | new_needed | candidate |
|---|---:|---:|---:|---:|
| Preference | 225 | 6 | 219 | 285 |
| Retrieval | 175 | 0 | 175 | 228 |
| Conflict | 125 | 0 | 125 | 163 |
| Forgetting | 100 | 4 | 96 | 125 |
| Tool | 125 | 0 | 125 | 125 |
| E2E | 35 | 0 | 35 | 35 |
| **合计** | **785** | **10** | **775** | **961** |

- 独立对象：KB 400 → 候选 520；Runtime sessions 35；scripts 45；fresh40 从 Admission PASS
- 产物（v4.1 P04 规范名）：`reports/quota_plan_v4.1.csv` + `reports/quota_plan_v4.1_summary.json`（authority_pr=40/review_id=5124685158/head=20b575e + signed ids + requal sha）

## fail-closed（v2）
unknown/duplicate/不在 requal 集/decision 非 ACCEPT/Tool-E2E/signed 与 effective 不一致 → exit nonzero；正式 P04 须 `--requal-sha`（否则仅 preview）。

## 待 Data-R
冻结 P04 quota plan（B 不自行写 Reviewer final authority）。
