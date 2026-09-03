# 阶段 8 A 侧首步交付：tool_result 受控试标候选 — 2026-09-03

- 角色：Annotator A（lyf-1213）
- 依据：工作安排（PR #25）A 侧首步依赖②「A 交付 tool_result 受控候选」；标注手册 v1.3 §8.1（合成场景文本仅试标跑通口径、candidate_only、绝不进封存）
- 说明：tool_result 在阶段 7 移除残留后 processed 无池（B 侧 `stage8_trial_sample.py` 提示经 `--extra` 补充）。本交付为试标提供 tool_result 受控候选。

## 一、交付物

| 文件 | 内容 |
| --- | --- |
| `data/interim/gold_candidates_tool_result.jsonl` | 8 条 tool_result 受控试标候选（`source=team_authored`、`review_status=candidate_only`） |

状态覆盖（B 侧 Kappa 口径 `status+persist_policy`）：
- success ×2、failed ×2、partial_success ×2、cancelled ×1、timeout ×1
- persist_policy：yes ×4、no ×4
- template_family：`tool_status_<status>_v1`（模板族覆盖 5 种状态）

## 二、禁 mock 边界（手册 §8.1）

- 本批为**受控场景文本**，仅用于试标跑通标注口径，**绝不进入封存**（sealed_test 禁 mock）。
- 正式 tool_result / e2e 封存集必须来自麒麟 VM 真实回放（阶段 10）。

## 三、与 B 侧集成验证（本机）

```
python scripts/audit/stage8_trial_sample.py \
  --processed data/processed \
  --extra data/interim/gold_candidates_tool_result.jsonl \
  --per-task "pref=8,retr=8,conf=8,forg=8,e2e=8,tool=8" --seed 42
```
- 结果：48 条（六类各 8），tool_result 8 条全部来自本候选文件；
- 确定性：seed=42 两次运行 SHA256 一致（EAC3EE39…）；
- 说明：试标集正式生成与合并由 B 在 PR #25 执行（`--total 40 --seed 42`），本文件只验证候选可被纳入。

## 四、后续（A 侧待办，按红线顺序）

1. B 在 PR #25 生成正式试标集 → A/B 独立标注 `labels_A/B_trial.jsonl`（禁先讨论答案）；
2. B 算 Kappa（总体+分层）→ Kappa≥0.70 放行 8.2；
3. A 执行 8.2 批量生成 `gold_candidates_*.jsonl`（六类，含 tool/e2e 候选与模板族覆盖）；
4. A 执行 8.3 独立双标全部样本。

## 五、诚实披露

- 8 条中 cancelled/timeout 各 1 条（覆盖不足），如需更均衡试标可在后续批次补充；当前满足"试标跑通口径"的最小覆盖。
- enum_dictionary.json 缺 `status/persist_policy` 等词表键属 B 侧 Low-3 待补（随 8.2 候选草稿），非本交付范围。
