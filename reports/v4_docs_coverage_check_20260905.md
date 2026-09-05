# v4 三份新文档覆盖度检查：能否解决项目现有问题（DGXD01，2026-09-05）

> 检查对象：
> - 《麒麟OS_Agent_Memory_Data_v4_新人AI机械化施工台账_v4.xlsx》（14 sheet 控制台）
> - 《麒麟OS_Agent_Memory_Data_v4_新人AI机械化执行SOP_v4.docx》
> - 《麒麟OS_Agent_Memory_Data_v4_AI_Prompt_Pack_v4.md》（P00–P99）
> 对照基准：项目现有问题清单 + v3 完整版方案手册。

## 一、现有问题 vs 新文档覆盖

### ✅ 已覆盖/新增解决
| 问题 | 解决来源 |
| --- | --- |
| v1 模板重复/存量旧数据无处置 | SOP-01 Legacy 265 重准入（decision tree → REUSE/REWORK/RELABEL/DROP；不保 265/265）；台账 02_Legacy265 |
| preference 任务专精度（普通请求/单次条件当偏好） | SOP §4.1；P10（persistent/temporary/task_constraint/ordinary_request/non_preference） |
| scope 机械映射 | SOP-03 G2 人审 100%；KMA Mapping 人工复核；禁默认补值 |
| conflict 伪冲突 | SOP §4.3（先问可同时成立否；须左右证据+why+时间/版本） |
| forgetting 无 must_keep | SOP §4.4（inventory+target+must_keep+checkpoints） |
| retrieval 无 KB 锚点 | SOP §4.2（KB+Query 拆分；relevant_ids 来自 frozen KB/qrel） |
| 盲包非 A/B 隔离 | SOP-04；P40/P41（不同随机序、禁答案；AI_LABEL_FORBIDDEN） |
| 重复/单一无 Gate | SOP-03 G4/G5；P30/P80（exact dup=0；Jaccard>0.85 送审；单 template>25% FAIL；leak=0） |
| AI 无溯源 | SOP §1.1；P00；台账 11/12（prompt/model/input/output/adoption） |
| 工具缺 fail-closed | SOP §12.1（NEEDS_IMPLEMENTATION；禁假装成功） |
| 停止线 | S1–S7 |

### ❌ 仍未解决（问题清单 Q1–Q8）
1. Q1 Legacy 265 范围/来源未与仓库存量对齐（gold dev177+reg50+sealed38=265？processed 215 team v1 模板？interim v1 215？未定义）。
2. Q2 sealed_test 已封存数据若含 v1 模板/旧泄漏 → 无回滚重封流程。
3. Q3 SOP 全部工具未在仓库实现 → 需 P2-A 立项。
4. Q4 KB 400/knowledge_id 依赖主仓 kb_import_contract + SchemaSnapshot FROZEN（未确认何时冻结）。
5. Q5 Runtime 35 依赖 M1/M2/M3（主仓 Frozen Build/VM）外部未承诺。
6. Q6 40 Calibration 是否复用 #31 现有 40 试标/双盲包未定义。
7. Q7 265 DROP/RELABEL 后与 785 目标/1.3×池联动算式未给。
8. Q8 单人/AI 同时代 A+B 与双盲独立性冲突（流程无法自解，需人工分派或 Reviewer 豁免）。

## 二、结论
- 新三件套把 v3 手册的"计划"升级为"可执行 Runbook"，已设计出 v1 存量处置（Legacy265）、六类语义判定、盲包隔离、去重/泄漏 Gate、AI 溯源与停止线——**主要数据质量问题有解法**。
- 但落地仍依赖：Legacy265 样本映射、sealed 回滚、工具实现（P2-A）、主仓 KB/Runtime 冻结、Calibration 衔接、总量联动、以及**双盲独立性人工分派**。
