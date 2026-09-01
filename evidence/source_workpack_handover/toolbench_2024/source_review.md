# toolbench_2024 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31。证据文件：`README.md`（已存档）、`toolbench_LICENSE`（Apache-2.0 全文，本次新增存档）。

## 可从原文直接确认的内容

- 正式名称：ToolBench（OpenBMB）。
- 官方仓库：`OpenBMB/ToolBench`（master）。
- 论文：arXiv:2402.01030（README 引用）。
- License：仓库根目录 `LICENSE` 为 **Apache License 2.0**，全文已存档为 `toolbench_LICENSE`（首行 "Apache License... Version 2.0, January 2004"）。
- README 附加声明（原文）：仅限研究与教育用途；数据不应被视为反映创建者/所有者/贡献者观点。
- 数据渠道（README 原文）：Google Drive 与清华云盘两个官方入口。**实测**：清华云盘外链已失效（"该外链不存在"）；Google Drive 国内不可达。GitHub raw 的 `data.zip` 为 1.76GB，脚本仅宜抽小样本。
- 数据结构（README）：G1/G2/G3 三级（单工具/多工具/工具规划）instruction 与 answer 文件；`test_query_ids/` 为官方测试集划分。

## 与此前登记表的差异

- registry v1.0 中"Apache-2.0（官方 README 声明）"：本次已补充 **LICENSE 原文存档**，合规证据升级为"许可文件原文"级。
- registry v1.0 中"data.zip 需手动/大文件下载"：确认官方云盘入口已失效，正式获取需依赖 HF 社区镜像（Adorg/ToolBench、Yhyu13/ToolBench_toolllama_G123_dfs 等，均为第三方再上传，**版本需人工核验与官方一致性**）。

## 推断（需人工确认）

- 本项目定位为"辅助、不进首版封存"，若维持该定位，风险可控；若升级用途，必须先核验镜像与官方版本的哈希一致性。

## 待 Reviewer 决策

- 维持"补充候选（不进入首版封存）"或降级淘汰。
