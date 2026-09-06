# Data-A Day-1 会话交接文档（v4.1）

> 生成：2026-09-06（lyf-1213 / Data-A）｜原因：上一会话上下文接近上限，移交新会话继续 A 的 Day1 工作。
> 交接性质：**Data-A 单角色**（已去除 B/Data-R 权限）。本会话只做 A 轨语义/候选/scope/盲标；不碰 tooling/registry/merge/裁决。

---

## 0. 新会话第一步：先读这三个文件（用户指定）

1. `麒麟OS_Agent_Memory_Data_v4_三人五天_30pct缓冲_完整版方案_v3.docx`（v3 完整方案：角色模型/五天排程/候选池策略/3000 字设计基线）
2. `麒麟OS_Agent_Memory_Data_v4_新人AI机械化施工台账_v4.xlsx`（v4 台账：14 sheet 控制台）
3. `麒麟OS_Agent_Memory_Data_v4_新人AI机械化执行SOP_v4.docx`（v4 SOP：Runbook）

> ⚠ 重要：以上三个是 **v4 历史基线**（设计/角色/流程骨架），供理解背景。**现行执行基线是 v4.1**（Closure C0-C5 + Legacy-N + 动态配额 + 人工独立性），已替代 v4。不要用 v4 里"265 条 / 无 Closure / 阶段 0-11"等旧口径指导 Day1。
> v4.1 三件套（权威）在仓库 master（5895a42 已合并）：`麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环执行SOP.docx`、`...施工台账.xlsx`、`...AI_Prompt_Pack.md`。若本地没有，用 `git show origin/master:"文件名"` 取出。

---

## 1. 一句话项目状态

**麒麟 OS Agent Memory Data v4.1**：为 OS Agent 记忆模块造评测 Gold。Closure C0-C5 已全部 DATA_R_FROZEN（2026-09-06 09:59），**正式 5 天 D1 已启动**；C1=LEGACY_SET_FROZEN（IN_SCOPE=465）。当前在 **PR#37（feat/B-stage8-v4.1-d1）** 上推进 D1。

## 2. 角色与仓库真源

| 角色 | 人员 | 职责 |
| --- | --- | --- |
| Data-A（本会话） | lyf-1213 | 语义/Pref/Conf/Forget/scope/Annotator A |
| Data-B | DGXD | tooling/审计/KB/Retrieval/Annotator B |
| Data-R | gaoyizhe934 | 终裁/final_label/sealed/Release |

远程：`gaoyizhe934/KylinOS_Agent_Memory_Module_Data_Lookup_Selection_and_Quality_Audit`
GitHub CLI 未登录；推送用 git credential（lyf-1213 token）。API 调评论/PR 时从 `git credential fill` 取 token。

## 3. 版本/PR 演进（全部已 merge，除 #37）

| PR | 内容 | merge |
| --- | --- | --- |
| #32 | v4.1 规则基线（SOP/台账/Prompt 三件套） | master `5f90409` |
| #34 | Data-A Candidate-Prep（candidates_v4 输入包 + scope 标准 + validator） | master `714cb0c` |
| #33 | Closure C0-C5 证据 + 冻结 | master `5895a42` |
| #36 | P2-A 12 工具（scripts/v4/*，C3 依赖） | master `f3cdd2a` |
| #37 | **D1 执行**：B=P11 机器审计（已交付）；A=P10 语义提案（已交付） | OPEN，分支 `feat/B-stage8-v4.1-d1` |

分支约定：改到独立分支（不要直接动 master）；D1 数据工作集中在 PR#37 分支，或按 Data-R 建议另开 Data PR。

## 4. Closure 终态（重要锚点）

- closure_status_v4.1.json：C0-C5 全 PASS；`reports/closure_freeze_record.json` 已由 Data-R 签 → **DATA_R_FROZEN / formal_day1_started=true（09:59）**。
- C1 `legacy_inventory_v4_full.jsonl`：**IN_SCOPE=465**（Data-R 已签 LEGACY_SET_FROZEN），tool_source/scan=f3cdd2a，ledger SHA `541aa9d3...`。
- 主仓 Gate（未绿，禁 production truth）：
  - **M1**（schema_snapshot）：BLOCKED（deadline D1 10:30 已过仍未提供）→ **production_truth_allowed=false**
  - M1-KB（kb_import_contract）：BLOCKED（deadline D2 12:00）
  - M2（Data RC）：PENDING（D3 12:00）
  - M3（Runtime/Frozen Build）：BLOCKED_EXTERNAL（D3 18:00）
- 含义：D1 只能做 **Inventory/Prov/候选草案/语义提案**；正式 Gold 业务真值、production knowledge_id、Runtime Gold 一律禁止。

## 5. D1 进度（2026-09-06）

| 项 | 状态 |
| --- | --- |
| B：P11 Legacy 机器审计 | ✅ PR#37 交付：465 NEED_HUMAN_REVIEW；prov 全 unresolved；near-dup 1250 对/265 样本；t2ranking 模板 43%>25%；leak 38 登记+2 碰撞 |
| **A：P10 Legacy 语义提案** | ✅ PR#37 commit `c85bbad`（见 §6） |
| R：M1 | 🔴 BLOCKED（deadline 过） |
| A：P20/P22/P23 候选工厂 | ⬜ 下一步 A 任务 |

## 6. A 已完成：P10 Legacy 语义重准入（commit c85bbad）

产物：
- `reports/legacy_semantic_requal_A.jsonl`（465 逐样本 proposal：semantic_status/proposed_decision/reason_codes/target_task_type/split_eligibility）
- `reports/v4.1_D1_A_legacy_semantic_requal_20260906.md`（汇总）
- 均已在 PR#37 分支；PR#37 上还有 DGXD 三提交（840ea60/6945e94/ddfa4e7）。

P10 结论（只 proposal，human_decision 归 Data-R）：
- **DROP 195**：conflict 40 全占位（`candidates={"旧记忆","新指令"}` 无真实内容）；tool 50 RUNTIME_STATIC_ONLY（command_N 编造）；e2e 15 静态；pref/forg ×10 重复。
- **REWORK 8**：pref_000001/2/5/4（周报要点/删除确认/中文标签/报告改版）+ forg_000001..4（VSCode 深色/删上周路径/忘客户姓名/撤回桌面布局）。
- **RELABEL 2**：pref_000006（支付密码→non_storable_negative）、pref_000003（本次英文→task_constraint）。
- **PENDING 260**：retrieval（M1-KB 未冻结，无法绑 KB/qrel）。
- sealed 样本 split_eligibility=DEV_REG_ONLY。

关键诊断：**Legacy-N 主体 = v1 模板×计数器膨胀**（pref 60=6句×10、forg 40=4句×10、conflict 40=5族×8 占位、tool/e2e 静态）。**accepted_legacy 上限≈10** → 非 Runtime 配额缺口≈全额（Pref225/Conf125/Forget100/Retr175）。

## 7. A 的 Day1 下一步：P20/P22/P23 候选工厂

- 依据 v4.1 SOP §14 / 台账 15 / DGXD ddfa4e7（D1 执行步骤 Data-A 部分）。
- Preference 目标 225 / Conflict 125 / Forgetting 100；候选 `new_needed=max(target-accepted_legacy,0)×1.30`（provisional：Pref 293/Conf 163/Forget 130，P04 冻结后以 accepted_legacy 重算）。
- **M1 未绿**：候选只做 candidate_only + 标 NON_PRODUCTION；不写 final Gold。
- 候选结构必须带：`blind_visible`(无答案) + `design_metadata`(scenario_spec_id/generation_id/prompt_version/seed/model/source_layer)；public 需 dataset_id+Registry join；OS 需 scenario_spec_id 真实存在（场景规格在 `data/interim/candidates_v4/scenario_specs/`）。
- 候选校验用 `scripts/v4/validate_candidate_prep.py`（#34 merge 后已在 master）。
- 候选防泄漏：盲包禁 design/expected/scope_target 等字段（P40）。
- 提交到 PR#37 分支（或另开 Data PR 供 B/Data-R 复核）。

## 8. 红线（Data-A 必须遵守）

1. 不写 human_decision / final_label；AI 不充当第二 Annotator。
2. M1 未 PASS 前不产 production business truth；M1-KB 未冻结不伪造 knowledge_id（只用 local_candidate_id）。
3. 不 mock；Runtime 只认真实回放（M3 未绿 Tool/E2E=BLOCKED_EXTERNAL）。
4. A/B 独立盲标；A 不看 B 标签。
5. 工具缺失/不存在 → NEEDS_IMPLEMENTATION，不假装执行。
6. 不改 raw；AI 会话落盘 evidence/ai_outputs + 台账 17 登记。
7. 当前只做非盲标环节（P10/P20/P22/P23 proposal/candidate_only、scope 复核、G2 语义）。

## 9. 常用文件/路径/命令速查

- Closure 状态真源：`reports/closure_status_v4.1.json`、`reports/closure_freeze_record.json`
- Legacy 冻结账本：`reports/legacy_inventory_v4_full.jsonl`（IN_SCOPE 465）
- P11 审计：`reports/legacy_machine_audit_v4.1.jsonl`（B 交付，A 的 P10 输入）
- P10 提案：`reports/legacy_semantic_requal_A.jsonl`（A 已产）
- 候选 schema/规格：`data/interim/candidates_v4/`（factory_config/scenario_specs/exemplar_candidates）
- P2-A 工具：`scripts/v4/`（provenance/dedup/leakage/admission/...；merge 于 master f3cdd2a）
- 命令：`python scripts/v4/inventory_legacy.py`、`python scripts/v4/validate_candidate_prep.py`、`python scripts/v4/test_v4_tools.py`
- 主仓 Gate 表：`reports/main_dependency_gate.json`
- 动态配额 P04：先有 accepted_legacy（Data-R 终裁 P10 后）→ `new_needed=max(target-accepted,0)`, 候选 ×1.30。

## 10. 建议给下一个新会话的开场提示词（可复制）

```
你是 Data-A（lyf-1213）的 AI 助手，只做 A 轨（语义/候选/scope/盲标辅助）。
先读交接文档 worklog/20260906_dataA_day1_session_handoff.md，
以及项目里三个 v4 文件（完整版方案_v3.docx / 施工台账_v4.xlsx / 机械化执行SOP_v4.docx）作为背景；
但当前执行基线是 v4.1（Closure 已冻结，D1 运行中，C1=LEGACY_SET_FROZEN IN_SCOPE=465）。
当前仓库基线 master=5895a42；D1 工作分支=PR#37 feat/B-stage8-v4.1-d1。
M1/M1-KB/M3 BLOCKED -> production_truth_allowed=false；只做 P10/P20/P22/P23 proposal/candidate_only。
A 已完成 P10（legacy_semantic_requal_A.jsonl，DROP195/REWORK8/RELABEL2/PENDING260）。
下一步：P20/P22/P23 候选工厂（candidate_only + NON_PRODUCTION，结构带 blind_visible/design_metadata，用 validate_candidate_prep.py 校验）。
遵守红线：不写 human_decision/final_label、禁 mock、工具缺失回 NEEDS_IMPLEMENTATION、AI 输出落盘 evidence/ai_outputs。
```

---

## 附：本交接文档需同步登记

- 本交接为 Data-A 会话元信息；建议在 PR#37（或 A 的 Day1 Data PR）commit 一份以留痕。
- AI 会话日志（台账 17 / evidence/ai_outputs）应登记：operator=lyf-1213, role=Data-A, prompt=P10(已) + P20/P22/P23(下一步), model 记录, output 路径如上。
