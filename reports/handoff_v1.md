# 交接说明 v1（2026-08-07）

## 已完成

- 数据包目录、登记表（dataset/source/license/split）。
- 需求-数据映射、候选来源核验、License 风险摘要。
- 自建 Gold 候选草稿 265 条（candidate_only，非最终 Gold）。
- 统一 Schema、转换脚本与测试、切分与泄漏审计、封存哈希。
- 麒麟回放准备包、复现文档、数据卡、评测报告初稿。

## 待完成（明确属于人工/环境 Gate）

- 公开数据集样本下载与 50-100 条审计（网络受限，脚本已就绪）。
- 双人独立标注、分歧裁决、Reviewer 批准 Gold。
- 麒麟虚拟机真实回放与指标回填。
- Gate 3/5/8/9/10/11 的 Reviewer 签字。

## 风险与下一步

- 网络：HuggingFace/GitHub 大文件下载不稳定，恢复后优先下载 LongMemEval oracle 与 T2Ranking dev 子集。
- 安全：DailyDialog 下载被安全软件拦截，未使用；任何重下必须走官方渠道并重新审计。
- 标注：正式标注前不得共享答案；标注手册见 `data/gold/annotation_guideline.md`。
- 联系人：Data Owner / Reviewer 待团队指定（见 `worklog/owners.md`）。
