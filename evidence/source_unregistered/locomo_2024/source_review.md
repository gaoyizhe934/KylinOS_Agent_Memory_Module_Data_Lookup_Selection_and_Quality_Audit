# locomo_2024 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31。证据文件：`locomo_README.MD`、`locomo_LICENSE.txt`（本目录）。

## 可从原文直接确认的内容

- 正式名称：LoCoMo — Data and Code for the ACL 2024 Paper "Evaluating Very Long-Term Conversational Memory of LLM Agents"（README.MD 第 1 行）。
- 官方发布者：snap-research 组织仓库（https://github.com/snap-research/locom）。README 作者署名为论文作者团队（佐治亚理工 + Snap Research），与论文一致。
- 版本：本次发布 locomo10 = 10 段对话，为 2024 年 3 月 arXiv v1 版 50 段对话中"最长、标注质量最高"的子集（README.MD 原文）。README 同时给出 MSC personas（`data/msc_personas_all.json`）。
- 数据文件列表（README.MD）：`./data/locomo10.json`（约 2.8MB）、`./data/msc_personas_all.json`。**数据文件直接位于官方仓库内，可经 raw.githubusercontent.com 下载，不依赖 Google Drive**。
- 图片不随数据发布（仅含 URL / BLIP caption / 检索词，README.MD 原文）。
- 标注任务（README.MD）：QA（含 evidence 定位）、幻觉检测、事件摘要、会话开场；含多类时序推理与知识更新题。
- 评测脚本：README.MD 提供 LLM Judge 调用方式（手册 6.4 节要求 LLM Judge 的 Prompt/模型需归档）。

## 修正此前登记表的错误

- registry v1.0 中"官方数据经 Google Drive 分发，体积大且不稳定"**不成立**：数据在仓库内，经 gh-proxy 镜像实测可下载（locomo10.json HTTP 200，2,805,274 字节）。
- registry v1.0 中"仓库未声明明确 License（API 显示 NOASSERTION）"**不成立**：仓库存在 `LICENSE.txt`，全文已存档，为 CC BY-NC 4.0。

## 推断（需人工确认）

- 第一作者 Adyasha Maharana 在 HF 有 `adymaharana/locomo`，但该 repo 仅含 33 字节 README（声明 license: cc-by-nc-4.0），无数据文件；其余 HF 命名空间下的 locomo 均为第三方转存。推断：GitHub 仓库为唯一官方数据入口。
- arXiv 编号未在 README.MD 中直接给出，论文链接需人工到 ACL Anthology 核对（ACL 2024）。

## 待 Reviewer 决策

- 是否允许试用（建议：允许试用，补充候选/高难质检集，用途受 CC BY-NC 4.0 约束）。
- 最终批准状态由 Reviewer 填写。
