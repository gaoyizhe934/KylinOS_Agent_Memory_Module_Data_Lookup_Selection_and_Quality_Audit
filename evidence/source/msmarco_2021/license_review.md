# msmarco_2021 License 风险摘要（AI 草稿，供 Reviewer 审批）

依据手册附录 C Prompt 04 生成（Annotator B，2026-08-31）；2026-09-01 A 取用并入并复核。
证据原文：`msmarco_terms_extracted.md`（官网首页 Terms and Conditions 全段，2026-08-31 提取存档）。

## Terms 原文关键句（引用）

1. "intended for non-commercial research purposes only"
2. "made available free of charge **without extending any license or other intellectual property rights**"
3. "provided 'as is' without warranty and usage of the data has risks since we may not own the underlying rights in the documents"
4. "Upon violation of any of these terms, your rights to use the dataset will end automatically"

## 逐用途核对（依据原文）

- 下载：允许（需先同意条款，勾选后开放链接）。
- 研究：允许，**仅限非商业研究**。
- 修改：条款未授予修改权 → **需人工/法务确认**。
- 内部演示：非商业演示可能允许 → 需人工确认。
- 比赛提交：**需人工确认**（若比赛含商业性质则超出条款）。
- 公开展示：条款明示不授予任何 IP 权利，展示数据摘录有风险 → 需人工确认。
- 打包再分发：**条款未授权再分发**；且微软不保证底层文档权利 → 高风险。
- 商业使用：**禁止**（non-commercial only）。

## 结论（AI 草稿）

方法论参考（不采用）。条款明确"不授予任何许可或知识产权 + 非商业限定 + 底层权利不保证"，不适合进入正式评测或封存包；仅可引用其评测方法学（qrels 设计等）。
未明确事项一律写"需人工/法务确认"，不得由 AI 给出确定法律结论。

## 取用与更新记录（2026-09-01，A = Data Owner）

- 取自 B 移交包（按移交规则择优保留），`msmarco_terms_extracted.md` 已一并并入本包，v2.0 登记"Microsoft Research License/Notice 待核验"状态自此有了原文级支撑。
- 版本线索见 `version_lock_20260901.md`；结论与 v2.0 登记表一致（方法论参考，不采用）。
