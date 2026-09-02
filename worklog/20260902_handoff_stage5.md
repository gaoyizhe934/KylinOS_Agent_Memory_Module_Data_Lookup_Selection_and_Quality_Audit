# 交接文档 — 阶段 5 候选选型与评分

给下一个会话 / 协作者的交接说明。当前阶段 0-4 已完成，下一任务为**阶段 5 候选选型与评分**。

## 一、当前状态总览

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| 阶段 0-2 | ✅ Gate 已批准 | 工作区、需求映射、候选登记（12 数据集） |
| 阶段 3 | ✅ Gate 3 已批准 | 来源/版本/License 核验（PR#16） |
| 阶段 4 | 🔶 Gate 4 待收口 | 审计 + 人工抽检完成，待 Reviewer 批准 |
| **阶段 5** | ⏳ **待开始** | 候选选型与评分（本交接文档目标） |

## 二、分工（3 人）

| 角色 | 人员 | stage5 职责 |
| --- | --- | --- |
| Annotator A | lyf-1213 | 按附录 B 十项 100 分制打分 |
| Annotator B | DGXD | 核对分数和结论 |
| Reviewer | gaoyizhe | 确认最终选型结论 + Gate 5 批准 |

## 三、阶段 5 任务（来自 stage_plan_v2_with_roles.md）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 按附录 B 十项 100 分制打分 | A | 评分表 |
| 核对分数和结论 | B | 评分复核 |
| 确认最终选型结论 | **Reviewer** | dataset_selection_decision_v2.md |
| 验收 | Reviewer | Gate 5 批准 |

## 四、附录 B 十项评分（需从手册附录 B 提取具体十项）

**注意**：十项评分维度的具体定义需从手册 `附录 B` 读取（本交接未展开）。执行时请先打开手册定位附录 B，按十项维度评分。

十项通常包含（以手册为准）：来源可追溯、License 明确、数据真实/无敏感信息、离线可复现、标签可解释、任务匹配度、规模、可切分防泄漏、维护与更新、文档完整。

## 五、评分对象（12 候选 + 当前 Gate 3 定位）

| dataset_id | Gate 3 定位 | 说明 |
| --- | --- | --- |
| longmemeval_cleaned_2025 | 允许试用 | 已审计，结构通过 |
| longmemeval_v2_2026 | 允许试用 | 已审计，结构通过 |
| stabletoolbench_2024 | 允许试用 | 样本不足（Low-3，仅 3 样例） |
| t2ranking_2023 | 允许试用 | 已审计，结构通过（含离谱 Web 查询，仅作检索方法参考） |
| multiwoz_2_2_2020 | 允许试用 | 已审计，结构通过 |
| toolbench_2024 | 淘汰 | 数据入口失效，降级方法论参考 |
| msmarco_2021 | 淘汰 | 方法论参考 |
| trec_tracks_2024 | 淘汰 | 方法论参考 |
| bpmn_2_0_2013 | 淘汰 | 结构参考 |
| dureader_retrieval_2022 | 需确认 | License 缺失 |
| personachat_2018 | 需确认 | 数据无明确许可 |
| machine_unlearning_bench_2025 | 需确认 | 社区发布者，仅方法参考 |

## 六、历史评分参考

- 早期评分草稿见 `reports/dataset_selection_decision_v1.md`（v1.0 时代，含 AI 草稿分）
- 阶段 5 需按附录 B **十项 100 分制**重新评分，产出 `dataset_selection_decision_v2.md`

## 七、关键约定与红线（执行时遵守）

1. **Gate 纪律**：Gate 5 未获 Reviewer 批准，不得进入阶段 6
2. **打分门槛**（手册）：核心候选 ≥80 分；补充候选 65~79；<65 淘汰
3. **独立打分**：A 打草案分，B 独立复核，Reviewer 最终确认，不接受 A/B 互批
4. **诚实披露**：每项评分给出理由，不硬凑分；数据缺失/定位限制如实标注

## 八、给下一个会话的第一句话

> 你的任务是推进阶段 5（候选选型与评分）。先读 `reports/gate_status.md` 确认当前状态，读手册附录 B 提取十项评分维度，按 100 分制为 12 个候选打分，产出 `reports/dataset_selection_decision_v2.md`，交 Reviewer 确认后更新 gate_status.md 并 commit 到当前分支。

## 九、产物位置

- 评分产出：`reports/dataset_selection_decision_v2.md`
- 状态更新：`reports/gate_status.md`
- 工作分支：`feat/A-B-stage4`（如 Reviewer 已批准阶段4，则基于最新 master 新开分支）