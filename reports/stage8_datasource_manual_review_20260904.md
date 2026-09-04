# 手册数据源地址检索与符合性判定（DGXD01，2026-09-04）

> 目的：按用户指示，从指导手册（02_...指导手册_v1.0_20260729.docx，附录D/推荐数据源与定位表）与重建计划检索全部数据源地址，逐项判定「符合手册需求」的数据源，作为后续真实数据补足与拆批 PR 的依据。
> 边界：本报告为只读分析与判定；**High-2 不做任何数据操作**（不移出/不删除现有候选与 v3 样本）；不含下载执行。

---

## 一、判定标准（依据手册）

手册决策原则（TABLE 2）：来源可追溯 > License 清晰 > 与赛题匹配 > 标签可信 > 规模大。
Gate 纪律：依次通过来源 → 合规 → 抽样质量 → 任务匹配 → 泄漏 → 封存；一票否决项（来源不可追溯 / License 不明确 / 敏感无法脱敏 / 无法离线复现 / 标签不可解释 / 明显泄漏）。

「符合手册需求」定义（本报告）：**官方来源可追溯 + License 明确允许目标用途 + 与六类任务匹配 + 有可核验样本/版本锁定**。三者缺一即判「待核验/淘汰」。

---

## 二、手册检索到的数据源地址（含 registry 官方/数据链接）

| # | dataset_id（仓库登记） | 手册定位（任务） | 官方来源（official_url） | 数据地址（data_url） | License（登记） | Registry 结论 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | longmemeval_cleaned_2025 | 偏好/检索/冲突/遗忘/端到端辅助 | https://github.com/xiaowu0162/LongMemEval | https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned | MIT（原文存档） | ✅ 核心候选，Gate3 允许试用（88 分） |
| 2 | longmemeval_v2_2026 | Tool Result/知识检索/端到端辅助 | https://github.com/xiaowu0162/LongMemEval-V2 | https://huggingface.co/datasets/xiaowu0162/longmemeval-v2 | Apache-2.0（原文存档） | ✅ 核心候选（补充），Gate3 允许试用（84 分） |
| 3 | stabletoolbench_2024 | Tool Result | https://github.com/THUNLP-MT/StableToolBench | 同上（仓库内 data_example） | Apache-2.0（原文存档） | ✅ 核心候选（补充），Gate3 允许试用（80 分） |
| 4 | toolbench_2024 | Tool Result 辅助 | https://github.com/OpenBMB/ToolBench | Google Drive（2026-09-01 失效） | Apache-2.0 + README 声明 | ⚠️ 方法论参考（Reviewer 裁决淘汰，不下载） |
| 5 | t2ranking_2023 | 知识检索（中文） | https://github.com/THUIR/T2Ranking | https://huggingface.co/datasets/THUIR/T2Ranking | Apache-2.0（HF 卡片） | ✅ 核心候选，Gate3 允许试用（82 分） |
| 6 | dureader_retrieval_2022 | 知识检索（中文） | https://github.com/baidu/DuReader | 千言/LUGE（需注册） | ⚠️ 仓库无 LICENSE（待人工核验） | ⚠️ 二选一候选，Gate3 需确认 |
| 7 | multiwoz_2_2_2020 | 冲突/任务对话辅助负样本 | https://github.com/budzianowski/multiwoz | 仓库 data/MultiWOZ_2.2 | MIT（原文存档） | ✅ 补充候选（辅助/负样本），Gate3 允许试用（74 分） |
| 8 | personachat_2018 | 偏好辅助 | https://parl.ai/projects/personachat/（已归档） | http://parl.ai/downloads/personachat/personachat.tgz | ⚠️ 数据无明确许可 | ⚠️ 补充候选，Gate3 需确认（不首版封存） |
| 9 | msmarco_2021 | 检索辅助 | https://microsoft.github.io/msmarco/ | https://huggingface.co/datasets/microsoft/ms_marco | ⚠️ Terms 非商业限定 | ⚠️ 方法论参考（淘汰，不下载） |
| 10 | trec_tracks_2024 | 检索方法论参考 | https://trec.nist.gov/data.html | 同上 | NIST 免责声明（Track 各自独立） | ⚠️ 方法论参考（淘汰，不下载） |
| 11 | bpmn_2_0_2013 | 工作流知识结构参考 | https://www.omg.org/spec/BPMN/ | OMG 官方 PDF | OMG 标准条款 | ⚠️ 结构参考（非数据集） |
| 12 | machine_unlearning_bench_2025 | 精准遗忘（辅助参考） | https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench | 同上 | MIT（HF 卡片） | ⚠️ 补充候选（社区发布者非官方，Gate3 需确认） |
| 13 | （手册附录可选，未入库）LoCoMo | 超长多会话/时间/证据链 | https://github.com/snap-research/locomo | 仓库 | 待核验 | 未登记（手册：小规模高难质检/演示） |
| 14 | （手册附录可选，未入库）LoCoMo-Plus | 隐式约束认知记忆 | https://github.com/xjtuleeyf/Locomo-Plus | 仓库 | 待核验 | 未登记（新兴候选，须先独立审计） |
| 15 | （手册附录）DailyDialog | 自然表达/闲聊负样本 | https://aclanthology.org/I17-1099/ | ACL Anthology | ⚠️ 站点条款待核验 | 未下载（安全软件拦截） |

---

## 三、符合手册需求的数据源判定

### ✅ 判定「符合手册需求」（可作真实数据源，全部 Gate3 已批准/允许试用）
1. **longmemeval_cleaned_2025**（MIT，88 分）— 覆盖偏好/冲突/遗忘/端到端；已有 oracle.json 真实样本 → **六类任务中最优先真实来源**
2. **longmemeval_v2_2026**（Apache-2.0，84 分）— Tool/检索/端到端轨迹；已有 questions.jsonl/SCHEMA/trajectories → **e2e/tool 链真实来源**
3. **t2ranking_2023**（Apache-2.0，82 分）— 中文检索 300K+ 查询 → **knowledge_retrieval 真实来源（当前 A 重建 12 条即用此）**
4. **stabletoolbench_2024**（Apache-2.0，80 分）— 静态工具调用样例 → **tool_result 候选来源（需改造标签）**
5. **multiwoz_2_2_2020**（MIT，74 分）— 任务对话辅助/负样本 → **preference/conflict 辅助来源**

### ⚠️ 判定「需先核验」方可使用（License 或来源问题）
- dureader_retrieval_2022（缺 LICENSE）、personachat_2018（数据无许可）、machine_unlearning_bench_2025（社区发布者）、DailyDialog（条款待核验）

### ⚠️ 判定「不采用/仅方法参考」（Reviewer 已裁决或非数据）
- toolbench_2024（入口失效）、msmarco_2021（非商业）、trec_tracks_2024（方法参考）、bpmn_2_0_2013（标准非数据）、LoCoMo / LoCoMo-Plus / locomo_2024（未登记或 License 待核验）

---

## 四、对六类任务的真实数据源覆盖结论（回应 High-2 阻塞）

| 任务 | 真实来源（符合手册） | 当前候选可用量 | 能否支撑 8/任务试标 |
| --- | --- | --- | --- |
| preference_extraction | longmemeval_cleaned（lme 偏好句）+ multiwoz（用户句） | A 重建 10 条 public_derived | 足够（>8） |
| knowledge_retrieval | t2ranking（真实 query）+ longmemeval_v2 | A 重建 12 条 public_derived | 足够（>8） |
| conflict_resolution | longmemeval_cleaned（真实事件链） | A 重建 5 条 public_derived | 不足（需补 3+ 或降批） |
| precise_forgetting | longmemeval_cleaned（真实记忆条目） | A 重建 6 条 public_derived | 不足（需补 2+ 或降批） |
| end_to_end_session | longmemeval_v2（真实任务链） | A 重建 6 条 public_derived | 不足（需补 2+ 或降批） |
| tool_result | stabletoolbench（静态样例） | 0（需改造标签） | 不足（本轮按 Reviewer 不产试标） |

> 结论：**纯真实数据源在 conflict/forgetting/e2e 三类不足以每任务 8 条**；preference/retrieval 两类足够。补齐路径：从 longmemeval_cleaned（真实会话）按"事件链/记忆条目"抽取 conflict/forgetting，从 longmemeval_v2 按"任务链"补 e2e——均可离线完成，无需新增外部网络下载（数据已在本仓库 raw/evidence）。tool_result 需 stabletoolbench 标签改造或麒麟 VM 回放（红线）。

---

## 五、回答：Medium 项是否需要数据源才能完全处理

### Medium-1（trial_v3_context.jsonl 独立标注上下文包）
- **生成动作本身不需要新数据源**：context 包 = 从现有试标集/候选池取 input+元数据+证据定位（不含 gold），现有 v3 集与 gold_candidates_*_v2 已含全部 input。
- **但产出是否"有效"依赖 High-2 裁定**：若 High-2 最终要求移出 team_authored 19 条，则 context 包需对"仅真实"样本生成，此时 conflict/forgetting/e2e 不足 8 条 → context 包只能按 21 条 public 生成，P1-5 需降批或补数据。
- **结论：Medium-1 可先行生成（基于现有集），是否需要真实数据源补足取决于 High-2 最终裁定**；数据源就绪不是 Medium-1 的前置硬条件，但决定其最终可用性。

### Medium-2（去重能力与表述）
- **不需要数据源**：纯代码/文档修改（脚本注释+报告措辞改"规则归一化去重"，或补改写检测测试）。可立即处理。

### Medium-3（PR 范围/提交规范）
- **不需要数据源**：中文修改报告已发布（commit de57380 + PR comment）。

### 总结
- Medium-2/3 完全不需要数据源，可立即闭环；
- Medium-1 技术上不需要数据源即可生成，但其**最终有效性**取决于 High-2（是否保留 team_authored）——若 High-2 移出则需真实数据补足 conflict/forgetting/e2e 三类（可离线从 longmemeval_cleaned/v2 抽取，见 §四）。

---

## 六、待用户/协调方裁定（未执行）
1. High-2 是否最终移出 team_authored（本报告未动任何数据）；
2. 是否按 §四 从 longmemeval 真实会话离线抽取 conflict/forgetting/e2e 补齐候选（A 职责）；
3. 拆批 PR 结构（High-1）——用户已允许拆批，具体批次划分待定。
