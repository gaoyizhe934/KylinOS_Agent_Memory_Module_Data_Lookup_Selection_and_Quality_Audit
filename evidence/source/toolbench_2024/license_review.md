# toolbench_2024 License 风险摘要（AI 草稿，供 Reviewer 审批）

依据手册附录 C Prompt 04 生成（Annotator B，2026-08-31）；2026-09-01 A 取用并入并复核。
证据原文：`toolbench_LICENSE`（Apache-2.0 全文，2026-08-31 存档，本次并入本包）+ README 附加声明（`README.md`）。

## License/Terms：Apache-2.0（许可文件原文）+ README 附加"研究教育用途"声明

- 下载：允许（事实）。
- 研究：允许（README 附加声明亦指向研究教育用途）。
- 修改：允许（Apache-2.0）。
- 内部演示：允许。
- 比赛提交：允许，附许可归属。
- 公开展示：允许，注明来源。
- 打包再分发：允许，须随包分发 Apache-2.0 许可证副本与 NOTICE。
- 商业使用：Apache-2.0 允许，但 README 附加声明"research and educational purposes only"与之存在张力 → **需人工确认**。

## 风险点

1. README 附加使用范围声明与 Apache-2.0 宽松条款的适用优先级 → Reviewer/指导老师确认。
2. 官方分发渠道（清华云盘失效、Google Drive 被墙；2026-09-01 复测官方 Drive 入口 404）→ 若采用 HF 社区镜像，需核验镜像与官方版本的完整性（哈希/文件数），否则来源不可追溯（一票否决项）。
3. 工具调用数据含 API Key 形态字段（部分样例）→ 手册 6.5 凭证扫描强制执行。

## 结论（AI 草稿）

方法论参考（不采用）。Reviewer 已于 2026-09-01（PR#1 审批意见第四节第 4 条）裁决：官方数据入口失效，降级为方法论参考，不进入首版封存；数据不再要求获取。
未明确事项一律写"需人工/法务确认"，不得由 AI 给出确定法律结论。

## 取用与更新记录（2026-09-01，A = Data Owner）

- 取自 B 移交包（按移交规则择优保留），`toolbench_LICENSE` 已一并并入本包，v2.0 登记"Apache-2.0（官方 README 声明）"升级为"许可文件原文"级。
- 版本线索见 `version_lock_20260901.md`（master commit `d56fdd89faf8`）；结论已由 B 草稿的"补充候选"更新为 Reviewer 裁决后的"方法论参考（不采用）"。
