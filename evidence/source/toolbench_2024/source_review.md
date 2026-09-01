# toolbench_2024 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31（Annotator B，v1.0 工作包）；2026-09-01 A 取用并入本证据包（feat/B-stage3-prep 分支）。
证据文件：`README.md`（已存档）、`toolbench_LICENSE`（Apache-2.0 全文，2026-08-31 存档，本次并入）、`api_snapshot_20260901/`（GitHub API 元数据，A 补充）。

## 可从原文直接确认的内容

- 正式名称：ToolBench（OpenBMB）。
- 官方仓库：`OpenBMB/ToolBench`（master）。
- 论文：arXiv:2402.01030（README 引用）。
- License：仓库根目录 `LICENSE` 为 **Apache License 2.0**，全文已存档为 `toolbench_LICENSE`（首行 "Apache License... Version 2.0, January 2004"）。
- README 附加声明（原文）：仅限研究与教育用途；数据不应被视为反映创建者/所有者/贡献者观点。
- 数据渠道（README 原文）：Google Drive 与清华云盘两个官方入口。**实测（2026-08-31）**：清华云盘外链已失效（"该外链不存在"）；Google Drive 国内不可达。GitHub raw 的 `data.zip` 为 1.76GB，脚本仅宜抽小样本。
- **数据渠道复测（2026-09-01，v2.0 阶段 2）**：官方 Drive 数据入口 404 失效（多 URL 形式，核验记录见 `evidence/audit/stage2_url_check_output_20260901.md`）；Reviewer 已据此裁决降级（见下）。
- 数据结构（README）：G1/G2/G3 三级（单工具/多工具/工具规划）instruction 与 answer 文件；`test_query_ids/` 为官方测试集划分。

## 与此前登记表的差异

- v1.0 registry 中"Apache-2.0（官方 README 声明）"：已补充 **LICENSE 原文存档**（`toolbench_LICENSE`），合规证据升级为"许可文件原文"级。
- v1.0 registry 中"data.zip 需手动/大文件下载"：确认官方云盘入口已失效，正式获取需依赖 HF 社区镜像（Adorg/ToolBench、Yhyu13/ToolBench_toolllama_G123_dfs 等，均为第三方再上传，**版本需人工核验与官方一致性**）。

## v2.0 重建取用记录（2026-09-01，A = Data Owner）

- 本报告主体取自 B 移交包，按移交说明取用规则择优保留；`toolbench_LICENSE` 已一并并入本包。
- 版本线索已锁定：见 `version_lock_20260901.md`（GitHub OpenBMB/ToolBench master commit `d56fdd89faf8...`）。

## Reviewer 裁决（2026-09-01，PR#1 审批意见第四节第 4 条）

- **降级为方法论参考（不采用）**：官方数据入口失效，不进入首版封存；数据不再要求获取。
- B 草稿结论"维持补充候选或降级淘汰"的两项待决策选项中，Reviewer 已选择降级为方法论参考。
- 登记表 conclusion 已同步为"方法论参考（不采用）"。

## 推断（需人工确认）

- 已定位为方法论参考（不采用数据），风险可控；若未来升级用途，必须先核验镜像与官方版本的哈希一致性。
