# B 复核报告：阶段 1~2 产出 + License 证据移交（2026-09-01）

执行人：Annotator B（DGXD01）
性质：B 职责内的复核（阶段1"指标核对"、阶段2"候选覆盖核对"均标注由 B 执行）；**不改变 Gate 状态**，全部结论供 Reviewer 审批参考。

---

## 一、复核范围与方法

- 阶段1：`reports/requirement_data_mapping_v2.md` 逐节核对（六项指标公式/阈值/数据需求 vs 手册 1.1/2.2 节）
- 阶段2：`registry/dataset_registry.csv` 12 行字段完整性 + `evidence_dir` 路径真实性 + `reports/stage2_coverage_report.md` 结论可复算性
- License 证据：本地 workpack（v1.0 时期 AI 辅助产出）与仓库 `evidence/source/` 的文件级差异盘点

---

## 二、阶段1 复核结论：通过（2 处小建议）

**核对通过项**：
- 六项指标齐全（偏好 F1/检索 Recall@K 与延迟/冲突准确率/遗忘三指标/Tool 状态准确率/端到端完成率+延迟），公式与手册 2.2 一致
- 阈值与手册一致：F1≥85%、Recall@5≥85%、P50/P95≤500ms、冲突≥88%
- 三时点残留检查、分组报告、规则优先/LLM Judge 兜底等通用纪律均与手册一致
- "当前进度 vs 目标"差距表与 v1.0 遗留数据实际数量一致（偏好 60/检索 60/冲突 40/遗忘 40/Tool 0/端到端 15）

**建议（不阻塞）**：
1. 【S1】"及格线 Recall@5 ≥ 85%" 建议补充 K 的取值说明（K=5 与指标名 Recall@K 混用；手册原文是 Recall@K，若比赛材料固定 K=5 应注明依据）
2. 【S2】端到端"响应匹配率 ≥ 80%"未标注来源（其余五项均有手册出处）——若是团队自设线，建议注明

## 三、阶段2 复核结论：基本通过，发现 1 个不合格项 + 2 个待确认项

### 🔴 不合格项（必须修复后 Gate 2 才能批准）

**【F1】machine_unlearning_bench_2025：evidence_dir 指向不存在的目录，零证据文件。**
- 登记表写 `evidence/source/machine_unlearning_bench_2025`，实际该目录不存在
- 报告声称"MIT（2026-09-01 复查确认：check_unlearning_detail.py 输出 license=mit）"，但脚本输出未存档为证据文件（evidence/ 全树无任何 unlearn 相关文件）
- 手册红线："任何数据下载前，必须先存档 License 原文"——该数据集当前不满足 Gate 3 的证据前置条件
- **修复建议（A 执行）**：运行 `python scripts/oneclick/check_unlearning_detail.py` 并把输出 + HF 卡片 license 字段截图/存档到 `evidence/source/machine_unlearning_bench_2025/`

### ⚠️ 待确认项

**【C1】覆盖统计口径修正后仍成立**：知识检索正式候选 4 个（msmarco/trec 降为方法论参考后），六类均 ≥2，达标结论可复算，认可。
**【C2】3 个候选的 data_url 未登记**（toolbench 经 Google Drive、personachat ParlAI 入口、msmarco）：报告已如实标注，但登记表 data_url 为空——建议 Gate 2 批准条件中加入"阶段4下载前补齐"。

### ✅ 核对通过项

- 12 行关键字段（formal_name/task/publisher/official_url/version/license/conclusion/evidence_dir）全部非空
- 其余 11 个数据集 evidence_dir 路径全部真实存在
- stage2 报告修订说明（"11 个 URL 全部可访问"的错误口径修正）诚实且清晰

---

## 四、License 证据盘点：workpack 比仓库多 12 个文件 + 2 个整目录

仓库 `evidence/source/` 缺失但 workpack 已有的材料（建议 A 在阶段3直接取用）：

| 数据集 | workpack 独有文件 | 对仓库的价值 |
| --- | --- | --- |
| **dailydialog_2017** | 整目录（license_review + source_review + 双镜像交叉验证） | 仓库登记表无此数据集（未登记≠不用；若阶段3扩充候选可直接启用） |
| **locomo_2024** | 整目录（含 CC BY-NC 4.0 LICENSE 原文 18.9KB） | 同上；偏好提取候选扩容时的现成证据包 |
| msmarco_2021 | terms 提取文 + 首页存档 | 直接消除"待核验"状态 |
| personachat_2018 | parlai_LICENSE + personachat_build.py | 直接消除"待核验"（数据无许可结论的支撑证据） |
| t2ranking_2023 | HF API metadata.json + HF_card.py | Apache-2.0 结论的机读证据（卡片声明 vs 许可原文的张力材料） |
| toolbench_2024 | toolbench_LICENSE（Apache-2.0 全文） | 登记表只写"README 声明"，有原文更强 |
| trec_tracks_2024 | NIST disclaimer 提取文 + data 页存档 | NIST 条款待核验的支撑材料 |

**注意**：这些是 v1.0 时期的 AI 辅助产出（当时作为阶段3预研），按手册附录 C 纪律，审查报告结论仍是"AI 草稿，供 Reviewer 审批"，移交后 Reviewer 需重新标记。同名文件内容可能存在差异（如 t2ranking 的 APACHE_2.0_LICENSE.txt vs t2ranking_hf_README.md 来源不同），**A 取用时应对比后择优，不要盲目覆盖仓库现有版本**。

---

## 五、处置建议汇总

| 编号 | 类型 | 内容 | 建议处理人 | 时机 |
| --- | --- | --- | --- | --- |
| F1 | 不合格 | machine_unlearning 证据缺失 | A | Gate 2 批准前 |
| C1 | 确认 | 覆盖统计口径（认可） | Reviewer | Gate 2 |
| C2 | 待办 | 3 个 data_url 空缺 | A | 阶段4 下载前 |
| S1 | 建议 | Recall@K 的 K 值注明 | A | 顺手修 |
| S2 | 建议 | 80% 阈值来源注明 | A | 顺手修 |
| — | 移交 | 12 文件 + 2 目录 License 证据 | A 取用 / B 已就绪 | 阶段3 |

---

## 六、B 侧后续

- 本报告提交至 `b-review-stage12` 分支（不修改任何已有文件，纯新增）
- workpack 证据包已在本地就绪，A 确认取用清单后即可拷贝（或由 B 拷贝后提 PR）

*复核方法说明：登记表逐字段扫描 + evidence_dir 存在性验证 + 报告结论独立复算（覆盖统计、URL 口径）；阶段1文档逐节与手册 1.1/2.2 比对。*
