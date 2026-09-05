# 麒麟 OS Agent 记忆模块数据查找、选型与质量审计

本仓库用于沉淀麒麟 OS Agent 记忆模块的数据选型、来源与许可证据、样本审计、统一 Schema、候选 Gold 数据、切分封存和评测复现材料。它面向数据治理与质量审计，不是 Agent 运行时代码仓库。

## 当前内容

- `registry/`：候选数据集登记、来源、许可证和切分清单。
- `evidence/`：来源与许可证审查证据、抽样审计、哈希及运行环境记录。
- `data/`：原始数据索引、处理后数据、候选 Gold、切分与回放材料。
- `scripts/`：下载、审计、转换、校验、切分、评测和一键执行脚本。
- `reports/`：需求映射、数据卡、质量指标、Gate 状态、交接与复现说明。
- `worklog/`：数据工作日志与角色分工记录。

## 使用方式

在仓库根目录运行以下命令以执行已有的一键流程：

```powershell
python scripts\oneclick\run_all.py
```

该流程会重建可再生成的目录、报告与校验产物，不会删除既有证据。更多执行说明见 [README_一键说明.md](README_一键说明.md)。

## 审计状态

仓库包含已产出的数据证据与候选草稿，但部分 Gate 仍需网络下载、麒麟虚拟机真实回放、双人独立标注、分歧裁决和 Reviewer 批准后才能通过。请以 [reports/gate_status.md](reports/gate_status.md) 为准，不要将“待执行”或“待人工”条目视为最终验收结论。

## 相关材料

- 指导手册：`02_麒麟OS_Agent_记忆模块数据查找选型与质量审计指导手册_v1.0_20260729.docx`
- **数据生产标准流程（现行优先）**：`麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环执行SOP.docx`（配套台账 `麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环施工台账.xlsx`、`麒麟OS_Agent_Memory_Data_v4.1_AI_Prompt_Pack.md`）——本 PR 合并仅代表 **v4.1 规则基线生效**，**不等于正式 5 天(D1)已启动**；须 Closure C0-C5 全 PASS + Data-R 冻结后才计 D1。v4 手册保留为历史基线
- v4 手册（历史基线）：`麒麟OS_Agent_Memory_Data_v4_三人五天_30pct缓冲_完整版方案_v3.docx`
- v2.0 重建计划：`麒麟OS_Agent_记忆模块数据包_v2.0_重建计划_修订版.docx`
- 数据卡：[reports/data_card_v1.md](reports/data_card_v1.md)
- 复现说明：[reports/reproduction.md](reports/reproduction.md)

