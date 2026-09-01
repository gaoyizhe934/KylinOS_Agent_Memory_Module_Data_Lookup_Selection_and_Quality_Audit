# t2ranking_2023 License 风险摘要（AI 草稿，供 Reviewer 审批）

依据 Prompt 04 生成。证据：HF 官方卡片 `cardData.license = apache-2.0`（`t2ranking_hf_api_metadata.json`，2026-08-31 经 hf-mirror API 存档）。

## License/Terms：Apache-2.0（以 HF 官方卡片声明为准）

- 下载：允许（事实）。
- 研究：允许（Apache-2.0 无用途限制）。
- 修改：允许。
- 内部演示：允许。
- 比赛提交：允许，附 NOTICE/LICENSE 归属即可。
- 公开展示：允许（展示引用数据需注明来源与许可）。
- 打包再分发：允许，须随包分发 Apache-2.0 许可证副本与 NOTICE 声明。
- 商业使用：允许，同上义务。

## 风险点

1. **声明形式缺口**：GitHub 仓库无独立 LICENSE 文件，许可仅以 HF 卡片字段声明。建议 Reviewer 决定是否要求补充证据（如向 THUIR 发 issue 确认）。
2. 段落文本来自真实网页，可能含个人信息 → 手册 6.5 敏感扫描仍需执行（阶段4）。
3. Apache-2.0 的 NOTICE 条款义务需在交付包中履行（交付清单 05_split_and_seal 里保留许可证副本）。

## 结论（AI 草稿）

核心候选（中文检索）。合规证据链完整度：来源官方（THUIR 双渠道）+ 许可声明形式待 Reviewer 认可。
