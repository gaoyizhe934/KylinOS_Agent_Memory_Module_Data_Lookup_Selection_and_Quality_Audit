# Reviewer 审查清单 — 阶段 0-1-2

审查人：gaoyizhe
分支：clean-branch
审查目标：确认阶段 0-1-2 产出物是否通过，批准后合并到 master

---

## 一、需要你做的 3 件事

1. 检查下方表格中的关键文件
2. 对每个 Gate 做出决定：**批准 / 驳回 / 需修改**
3. 在 GitHub PR 页面点 "Merge pull request" 或留言修改意见

---

## 二、Gate 0 审查（工作区初始化）

| 检查项 | 说明 | 审查方式 | 结论 |
| --- | --- | --- | --- |
| 目录结构是否完整 | 16 个目录（data/raw/interim/processed/gold/registry/evidence/scripts 等） | 看 reports/stage0_checklist.md | ⬜ 通过 / ⬜ 驳回 |
| 分工是否明确 | A=lyf-1213, B=DGXD, Reviewer=gaoyizhe | 看 worklog/owners.md | ⬜ 通过 / ⬜ 驳回 |
| raw 目录只读约定 | 原始数据通过脚本操作，不直接修改 | 已约定 | ⬜ 认可 |

**你需决定：** 分工是否接受？如接受，Gate 0 批准。

---

## 三、Gate 1 审查（需求—数据映射）

| 检查项 | 说明 | 审查方式 | 结论 |
| --- | --- | --- | --- |
| 六项指标是否都有对应子集 | 偏好/检索/冲突/遗忘/Tool/端到端 | 看 reports/requirement_data_mapping_v2.md | ⬜ 通过 / ⬜ 驳回 |
| 指标阈值是否合理 | F1>=85%, Recall@K>=85%, 准确率>=88% 等 | 看文档"二、计算方法与算法" | ⬜ 通过 / ⬜ 驳回 |
| 当前进度 vs 目标是否清晰 | 6 项当前候选数 vs 目标数 | 看文档"四、当前进度 vs 目标" | ⬜ 通过 / ⬜ 驳回 |

**你需决定：** 指标映射是否有遗漏？如无，Gate 1 批准。

---

## 四、Gate 2 审查（候选查找与登记）

| 检查项 | 说明 | 审查方式 | 结论 |
| --- | --- | --- | --- |
| 每类任务是否 ≥2 候选 | 6 类任务全部达标 | 看 reports/stage2_coverage_report.md | ⬜ 通过 / ⬜ 驳回 |
| 新增数据集是否合理 | machine_unlearning_bench_2025（MIT 许可证） | 看 registry/dataset_registry.csv 末行 | ⬜ 通过 / ⬜ 驳回 |
| 登记表信息是否完整 | 12 个数据集都有名称、版本、来源、任务 | 看 registry/dataset_registry.csv | ⬜ 通过 / ⬜ 驳回 |

**重点确认：** 新增的机器遗忘数据集（machine_unlearning_bench_2025）作为精准遗忘的补充候选是否接受？它只是公开基准参考，不是麒麟 OS 场景数据。

**你需决定：** 候选覆盖是否足够？如可接受，Gate 2 批准。

---

## 五、关键决策点汇总

| 序号 | 决策内容 | 你的选择 |
| --- | --- | --- |
| 1 | 分工：A=lyf-1213, B=DGXD, Reviewer=gaoyizhe | ⬜ 接受 / ⬜ 调整 |
| 2 | 指标阈值：F1>=85%, Recall@K>=85%, 准确率>=88% 等 | ⬜ 接受 / ⬜ 调整 |
| 3 | 新增 machine_unlearning_bench 作为遗忘参考候选 | ⬜ 接受 / ⬜ 拒绝 |
| 4 | 当前 12 个候选数据集是否足够启动阶段 3 | ⬜ 可启动 / ⬜ 需补充 |

---

## 六、快速验证方法

如果时间有限，只看这 3 个文件即可：

```powershell
# 1. 看分工表
cat worklog/owners.md

# 2. 看六项指标
cat reports/requirement_data_mapping_v2.md

# 3. 看候选覆盖
cat reports/stage2_coverage_report.md
```

## 七、通过后操作

1. 在 GitHub PR 页面点 **"Merge pull request"** → **"Confirm merge"**
2. 本分支工作结束，可进入阶段 3（来源/License 核验）