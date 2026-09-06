# AGENTS.md — 麒麟 OS Agent Memory Data v4.1

本文件供 AI Agent / 协作者快速了解项目上下文、当前进展、约定规范和下一步工作。

## 项目一句话

为麒麟 OS Agent 的记忆模块构建高质量、可追溯、真实回放的评测数据集（Gold Data）。当前执行基线为 **v4.1**：正式目标 **785 Gold + 400 Memory KB + 35 Gold-eligible Runtime Sessions**，支持偏好提取、知识检索、冲突处理、精准遗忘、Tool Result、端到端会话六类任务。

## 关键背景文档（务必先读）

| 文件 | 内容 |
| --- | --- |
| `麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环执行SOP.docx` | **现行基线** Runbook：C0-C5 闭环 → 正式5天（D1-D5），Legacy-N 盘点、Seal 撤销、P2-A 工具、动态配额、人工独立性 |
| `麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环施工台账.xlsx` | 日常状态真源：Closure Q1-Q8、LegacyInventory、动态配额、Seal 撤销、P2-A Tooling、主仓 Gate、五天施工、Dashboard |
| `麒麟OS_Agent_Memory_Data_v4.1_AI_Prompt_Pack.md` | P00-P99 提示词（新增 P01-P06，更新 P10-P99），复制给 AI 时按需使用 |
| `麒麟OS_Agent_Memory_Data_v4_三人五天_30pct缓冲_完整版方案_v3.docx` | v4 完整版方案（历史基线，设计依据与角色模型） |
| `麒麟OS_Agent_Memory_Data_v4_新人AI机械化执行SOP_v4.docx` | v4 手册（历史基线，已被 v4.1 替代，不再单独指导开工） |
| `02_麒麟OS_Agent_记忆模块数据查找选型与质量审计指导手册_v1.0_20260729.docx` | 总纲手册（Gate、评分、标注、切分、评测） |
| `reports/gate_status.md` | Gate 状态总表（含 v4.1 Closure 状态） |
| `reports/v4_gap_fix_plan_20260905.md` | v4 漏洞清单（G1-G10）与 Phase 1/2/3 修改方案 |
| `reports/v4_docs_coverage_check_20260905.md` | v4 三件套覆盖度检查（Q1-Q8） |
| `reports/v4.1_execution_entry_20260905.md` | v4.1 执行入口：Closure C0-C5 立项说明 |

## 当前状态（2026-09-05）

### 旧计划（v1.0/v2.0 阶段制）已推进到阶段 8
- Gate 0-7 已 Reviewer 批准；`data/processed` 715 条可溯源（KMA 化 415 条）；`data/gold` 265 条（dev/reg/sealed）。
- 阶段 8 候选池曾被查出 88~93% 语义重复 → 重建 77 候选 + 试标集 v3(40 条) + A/B 骨架 v3。
- **旧 PR#31 试标 40 条按 v4.1 C4 规则 = HISTORY_ONLY**，不复用为新正式 Calibration。

### v4.1 执行状态（2026-09-05 晚）
- **Closure 证据 6/6 content-accepted → READY_FOR_DATA_R_FREEZE**，正式 5 天时钟未启动（待 Data-R 签 `reports/closure_freeze_record.json`，formal_day1_started=false）。
- **C0-C5 当前状态只由 `reports/closure_status_v4.1.json` 维护**（Data-R review §9 / R5 Blocking-6）；本文件不独立维护 PASS/PENDING 数字。
- **Closure 证据落盘（closure_content_commit=737ef19，基于最新 master f3cdd2a 含 #34+#36）**：
  - C0 `reports/independence_manifest.json`；C1 `reports/legacy_inventory_v4_full.jsonl`（**tool_source/scan=f3cdd2a**，895：IN_SCOPE 465/DUP 430/465 组，canonical PASS；inventory 仍 NOT_FROZEN，LEGACY_SET_FROZEN 待 Data-R Freeze）；C2 `reports/seal_audit_v4.1.json`（seal-v1 REVOKED）；C3 `reports/tooling_bootstrap_report.json`（P2-A #36 merged f3cdd2a）；C4 `reports/trial40_reuse_audit.json`（HISTORY_ONLY）+ leak registry（81 条）；C5 `reports/main_dependency_gate.json`（依赖已登记，M1/M3=BLOCKED）。
  - 各 Gate evidence_path/commit(40-char)/SHA256 以 closure_status_v4.1.json / closure_freeze_record.json 为准。
- **历史评论级声明（HISTORICAL_COMMENT_ONLY / NOT_HEAD_EVIDENCE）**：早期 PR comment 中「P01 N=265 已盘点」「P03 12 工具已完成 13/14 测试」「C1 250 IN_SCOPE」等均非当前 HEAD 证据，已由本分支真实账本/审计取代。
- 已核验：B 的 inventory/tooling/preflight JSON 产出均为仓库相对路径（无本机绝对路径），跨仓可移植性 OK。
- 当前工作分支：v4.1 执行 = PR#33 `feat/B-stage8-v4.1-closure`（已 rebase 到 post-#32 master；HEAD 不在此硬编码，以 `reports/closure_status_v4.1.json` 的 closure_head 为准）；docs = PR#32（已 merge）；P2-A = PR#36 `feat/B-stage8-p2a-tools`；Candidate-Prep = PR#34（已 merge）。

## 分工（v4.1 三人独立数据团队，与主仓 Main A-E 完全独立）

| 角色 | 人员 | 生产职责 | 标注职责 | 权限/禁止 |
| --- | --- | --- | --- | --- |
| Data-A | lyf-1213 | 来源语义、Preference/Conflict/Forget 候选工厂、OS scenario spec、scope 人工复核(G2) | Annotator A：785 Case 独立盲标 | 无最终裁决权；不得看 B 标签；不得改主仓 |
| Data-B | DGXD | 自动化流水线、Provenance、Mini KB、Retrieval、Runtime importer | Annotator B：785 Case 独立盲标 | 无最终裁决权；不得看 A 标签；不得改主仓 |
| Data-R | gaoyizhe | Gate、分歧裁决、规则冻结、切分、sealed、release、跨仓接口 | 不参加 A/B 首轮盲标；独立抽验/裁决 | 唯一 final_label 裁决者与 sealed 持有人；不得提前透露 |

### Data-A 具体职责与权限（v4.1）
- **任务 Owner**：Preference(225)、Conflict(125)、Forgetting(100)（v4.1 台账 10_任务判定矩阵 Owner 列）。
- **D1**：Legacy-N 语义重准入（P10 提议，不写 human_decision）+ Preference/Conflict/Forget 候选工厂（P20/P22/P23，candidate_only）。
- **D2**：fresh 40 Calibration 独立盲标（P41 只做结构辅助）+ Bulk Wave1。
- **D3**：Bulk 主体。**D4**：完成动态 Gold 缺口 + Runtime 语义核验。**D5**：语义 QA/回溯/文档。
- **AI 边界**：AI 可做候选生成/语义预审/证据定位/格式校验；**不得**给 A 当前样本最终标签、不得充当第二人工标注者、不得看 B 标签、不得写 final_label。

## v4.1 红线（违反即退回/不计 Gold）

1. **Closure 先闭环**：C0-C5 未全 PASS 不启动正式 5 天时钟。
2. **Legacy 先盘点**：不先假设 265；Data-R 签 `LEGACY_SET_FROZEN` 后才做重准入。
3. **人工独立性硬门槛（Q8/C0）**：A/B 必须两个不同人工，R 第三人；AI 不能补人数；任何兼任 → 不计正式双盲 Gold。
4. **全链路禁 mock**：Runtime 只认真实回放；M3 未 PASS 则 Tool/E2E 标 `BLOCKED_EXTERNAL`，禁止静态样本冒充。
5. **工具不伪造**：目标脚本不存在 → `NEEDS_IMPLEMENTATION`（P2-A），禁假装执行成功。
6. **Gate 纪律 + 数据硬校验**：Admission G1-G5 任一 FAIL 不入盲包；provenance unresolved/leak/exact dup >0 即 FAIL；候选必须带 generation_id/prompt/seed/model 溯源。

## v4.1 正式目标与动态配额（Q7）

| 任务 | 正式目标 | Legacy 可抵扣 | 候选规则 |
| --- | --- | --- | --- |
| Preference | 225 | 是 | 缺口×1.30 |
| Retrieval Query | 175 | 是 | 缺口×1.30 |
| Conflict | 125 | 是 | 缺口×1.30 |
| Forgetting | 100 | 是 | 缺口×1.30 |
| Tool Result | 125 | 否 | 真实 Runtime 事件 |
| E2E | 35 | 否 | Gold-eligible session |
| Memory KB | 400 | 独立对象 | 候选池约 520 |
| Runtime Gold-eligible sessions | 35 | 否 | 准备 45 个 script，执行到 35 eligible |

`new_needed = max(target - accepted_legacy, 0)`；`candidate_needed = ceil(new_needed * 1.30)`。
accepted_legacy 仅统计 REUSE/REWORK/RELABEL 且重准入完成的样本。

## Closure C0-C5（正式 5 天启动条件）

| Gate | 内容 | 负责人 | 输出 |
| --- | --- | --- | --- |
| C0 | 人工独立性：A/B/R 三人确认 | Data-R | independence_manifest.json（P06） |
| C1 | Legacy-N 盘点冻结（不先假设 265） | Data-B/R | legacy_inventory_v4_full.jsonl + legacy_inventory_v4.json(summary)（P01） |
| C2 | 旧 sealed 审计/撤销重封 | Data-R | seal_audit_v4.1.json（P02，primary）+ revocation/reseal |
| C3 | P2-A Tooling Bootstrap（12 工具） | Data-B/R | tooling_bootstrap_report.json（P03，引用 P2-A PR） |
| C4 | PR31 旧 40 = HISTORY_ONLY；fresh 40 计划 | Data-R | trial40_reuse_audit.json（P05） |
| C5 | 主仓 M1/M1-KB/M2/M3 依赖登记 | Data-R | main_dependency_gate.json（P70） |

## 数据管线（v4.1）

```
data/raw/       ← 只读，不直接修改
data/interim/   ← candidates_v4 / blind_context_A / blind_context_B / legacy_requalification
data/processed/ ← 统一 Schema 转换
data/gold/      ← dev(~393) / regression(~157) / sealed_test(~235)，按 group 整组切分
data/kb/        ← memory_kb_v4.jsonl（400）
data/runtime_replay/ ← sessions/（真实回放）
registry/       ← source_registry / provenance_registry_v4 / leaked_content_registry / prompt_registry / split_manifest
interfaces/     ← main_to_data/（SchemaSnapshot、KB Contract、Runtime Runner、Frozen Build）
evidence/       ← ai_outputs/（AI 会话必须落盘可追溯）/ audit / runtime / hashes
release/        ← DATA_RELEASE_v4.1_manifest.json / SHA256SUMS
```

## 常用命令

```powershell
# 候选覆盖检查（旧计划遗留）
python scripts/oneclick/stage2_coverage_check.py

# 指标计算
python scripts/evaluate/evaluate_metrics.py --gold "data/processed/*.jsonl" --hyp <预测目录>

# v4.1 目标工具（P2-A，未实现前返回 NEEDS_IMPLEMENTATION，禁止假装成功）
# preflight.py / inventory_legacy.py / provenance_resolver.py / dedup_scan.py / leakage_scan.py
# admission_gate.py / build_blind_packets.py / validate_labels.py / disagreement_report.py
# runtime_import.py / split_grouped.py / seal_release.py
```

## Git 工作约定

- 不要直接 push master，改到 `clean-branch` 或新建分支，交 PR
- commit message 格式：`阶段X: 简述` 或 `v4.1: 简述`
- 大文件已被 .gitignore 排除，不要手动 add 大文件
- 修改后提交并 push 到当前分支即可

## 当前待办（v4.1）

### Closure 阶段（当前）
1. C0-C5 由 Data-B/R 推进；Data-A 不越线代签。
2. Data-A 待命任务（Closure 通过后 D1 启动）：
   - Legacy-N 语义重准入（P10，仅 proposal，等待 C1 冻结）
   - Preference/Conflict/Forget 候选工厂（P20/P22/P23，等待动态配额）
   - scope 人工复核（G2，Preference 逐条 topic/tool/global/session，禁止默认 tool）

### 后续阶段速览
- 正式 5 天：D1 Legacy 重准入+候选 → D2 fresh 40 Calibration(Kappa≥0.70)+Bulk → D3 Bulk 主体+KB → D4 动态缺口+35 Runtime+16:45 冻结 → D5 QA/Split/Seal/Release。

## 已知问题与风险

| 风险 | 状态 | 预案 |
| --- | --- | --- |
| 主仓 M1/M1-KB/M2/M3 未冻结 | PENDING（外部依赖） | 未绿则显式 BLOCKED；非 Runtime Gold/KB 可继续 |
| 麒麟 VM 未就绪 | 待确认 | M3 不绿 → 160 Runtime Gold 标 BLOCKED_EXTERNAL |
| v4.1 工具链（P2-A 12 工具）未实现 | PENDING | NEEDS_IMPLEMENTATION；先 P2-A，禁伪造 |
| 双盲独立性 | A/B/R 为三个不同人工 | 任何兼任 → 不计正式 Gold（Q8 硬门槛） |
| 标注人力 | 2 标注 + 1 裁决 | 25 条微批 + WIP≤2 + Kappa 未达标退回 |

## 给新 Agent 的第一句话

> 你的任务是推进 v4.1。先读 `麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环执行SOP.docx` 与 `reports/gate_status.md`，遵守红线（Closure 未闭环不启动正式 5 天、Legacy 不先假设 265、人工独立性、禁 mock、工具缺失返回 NEEDS_IMPLEMENTATION），AI 只做非盲标环节，产出物按 SOP 目录存放并在台账 AI 会话日志登记。完成后更新 gate_status.md 并 commit 到分支。
