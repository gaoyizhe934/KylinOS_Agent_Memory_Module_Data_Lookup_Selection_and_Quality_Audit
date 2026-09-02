# 阶段4 小样本质量审计报告（AI 辅助草案）

> **性质声明**: 本报告由脚本自动生成, 仅覆盖结构与可机械检查项; 标签语义可推导性、困难样本覆盖等语义项需人工抽检后才能得出结论。Gate 4 是否通过由 Reviewer 决定。
>
> **运行备注**: A复跑: 同步PR#17(ID修复)后重新审计

- 运行时间: 2026-09-02 19:10:50
- 运行命令: `python scripts/audit/stage4_sample_audit.py --note A复跑: 同步PR#17(ID修复)后重新审计`
- Python: 3.11.9 / 平台: win32
- 审计执行: Annotator B (DGXD01)

## 1. 审计概览

| dataset_id | 状态 | 数据文件 | 记录数 | 唯一ID | 高危敏感 | 低危敏感(合计) | 在线引用 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | ok | 1 | 100 | 100 | 0 | 4 | 22 |
| longmemeval_v2_2026 | ok | 1 | 100 | 100 | 0 | 0 | 1 |
| multiwoz_2_2_2020 | ok | 1 | 100 | 100 | 0 | 0 | 0 |
| stabletoolbench_2024 | 目录不存在 | 0 | 0 | 0 | 0 | 0 | 0 |
| t2ranking_2023 | ok | 1 | 100 | 100 | 0 | 0 | 0 |

异常总数 **3**（高 0 / 中 0 / 低 3）

## 2. 逐数据集审计明细

### longmemeval_cleaned_2025


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| question | 72 | 168 | 287 | 355 | 21 | 0 |
| answer | 12 | 145 | 306 | 395 | 1 | 0 |

- 类别分布（正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检）: knowledge-update=17, multi-session=28, single-session-assistant=6, single-session-preference=3, single-session-user=16, temporal-reasoning=30

- 低危敏感模式（合成研究数据中常见, 已抽样入清单, 全量计数如下, 判真伪由人工）: email×4
- 内容中出现 URL 引用 22 处（在线依赖风险需人工评估评测脚本是否运行时抓取）
- 6.3 最低人工抽样量: **50** 条（现有 100 条）

### longmemeval_v2_2026


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| question | 277 | 643 | 802 | 1206 | 166 | 0 |
| answer | 17 | 116 | 180 | 469 | 1 | 0 |

- 类别分布（正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检）: dynamic-environment=15, dynamic-environment-abs=9, errors-gotchas=4, procedure=12, procedure-abs=8, static-environment=37, static-environment-abs=15
- 内容中出现 URL 引用 1 处（在线依赖风险需人工评估评测脚本是否运行时抓取）
- 6.3 最低人工抽样量: **50** 条（现有 100 条）

### multiwoz_2_2_2020


- 类别分布（正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检）: ['attraction', 'hotel']=6, ['attraction', 'train']=14, ['hotel']=9, ['restaurant', 'attraction']=6, ['restaurant', 'hotel']=9, ['restaurant', 'taxi', 'attraction']=3, ['restaurant', 'taxi', 'hotel']=6, ['restaurant', 'train']=17, ['restaurant']=5, ['taxi', 'attraction', 'hotel']=1, ['taxi']=6, ['train', 'hotel']=16, ['train']=2
- 6.3 最低人工抽样量: **50** 条（现有 100 条）

### stabletoolbench_2024

- 状态: 目录不存在

### t2ranking_2023


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| text | 10 | 17 | 20 | 24 | 5 | 0 |
- 6.3 最低人工抽样量: **50** 条（现有 100 条）

## 3. 异常类型汇总

| 异常类型 | 数量 |
| --- | --- |
| sensitive_hit | 2 |
| null_string | 1 |

逐条异常明细见 `data/interim/stage4_anomalies.csv`。

## 4. 需人工逐条复核的样本 ID

清单构成: 全部异常记录 ID + 分层抽样的正常记录 ID（每个类别至少 2 条，并补足至 6.3 最低人工抽样量）。完整清单见 `evidence/audit/stage4_audit_summary.json`。

- **longmemeval_cleaned_2025**: 共 50 个 ID（异常 2 + 正常抽样 48）｜类别覆盖: knowledge-update×7, multi-session×12, single-session-assistant×4, single-session-preference×2, single-session-user×10, temporal-reasoning×15
  - ID: 031748ae, 031748ae_abs, 0a34ad58, 0bc8ad93, 10d9b85a, 118b2229, 1a8a66a6, 1faac195, 27016adc, 3c1045c8, 57f827a0, 60472f9c, 60bf93ed_abs, 60d45044, 6222b6eb, 6ae235be, 6b168ec8, 72e3ee87, 75499fd8, 852ce960, 88432d0a_abs, 89527b6b, 8cf4d046, 94f70d80, b46e15ee, b5ef892d, b6019101, b86304ba, c14c00dd, c6853660（仅展示前 30）
- **longmemeval_v2_2026**: 共 50 个 ID（异常 1 + 正常抽样 49）｜类别覆盖: dynamic-environment×6, dynamic-environment-abs×4, errors-gotchas×3, procedure×5, procedure-abs×5, static-environment×19, static-environment-abs×8
  - ID: 499488a6, 0401f0c8, 059974dd, 0c0fdcd7, 0fe2c676, 11dac74b, 19367bc7, 2ad054b5, 2fab8b79, 32d04f31, 3a131a42, 3a7a7880, 3b375e30, 3daef058, 436c58d5, 45d1e7f1, 4dffe641, 579557d8, 5d6ecdeb, 5db4899c, 5f100f22, 6517165d, 668f7b74, 7586cf7c, 77258cda, 7a07e9a0, 820d56e2, 83c35034, 86fa86eb, 87711b62（仅展示前 30）
- **multiwoz_2_2_2020**: 共 50 个 ID（异常 0 + 正常抽样 50）｜类别覆盖: ['attraction', 'hotel']×4, ['attraction', 'train']×4, ['hotel']×2, ['restaurant', 'attraction']×4, ['restaurant', 'hotel']×6, ['restaurant', 'taxi', 'attraction']×2, ['restaurant', 'taxi', 'hotel']×3, ['restaurant', 'train']×7, ['restaurant']×3, ['taxi', 'attraction', 'hotel']×1, ['taxi']×4, ['train', 'hotel']×8, ['train']×2
  - ID: MUL0129.json, MUL0142.json, MUL0287.json, MUL0598.json, MUL0602.json, MUL0878.json, MUL1221.json, MUL1549.json, MUL1762.json, MUL2291.json, MUL2670.json, PMUL0142.json, PMUL0294.json, PMUL0508.json, PMUL0596.json, PMUL0623.json, PMUL0653.json, PMUL0858.json, PMUL1345.json, PMUL1518.json, PMUL1591.json, PMUL1684.json, PMUL1747.json, PMUL1791.json, PMUL2282.json, PMUL2314.json, PMUL2386.json, PMUL3072.json, PMUL3169.json, PMUL3215.json（仅展示前 30）
- **t2ranking_2023**: 共 50 个 ID（异常 0 + 正常抽样 50）｜类别覆盖: _×50
  - ID: 1052, 11116, 11236, 11734, 11856, 12049, 12226, 12551, 1436, 14829, 14967, 1515, 15258, 17698, 18223, 19488, 19922, 20410, 20950, 212, 22109, 22323, 22550, 23134, 23241, 2361, 24052, 24071, 24432, 24461（仅展示前 30）

## 5. 静默丢失风险清单（Prompt 05-R 要求）

脚本显式计数以下“可能丢数据”路径, 未静默丢弃任何记录:

| 风险路径 | 处理方式 |
| --- | --- |
| 文件级解析失败（编码/JSON损坏） | 记 parse_error 高危异常, 计入 parse_failed |
| JSONL 单行解析失败 | 记 parse_error 异常, 其余行继续 |
| 空文件（0字节） | 记 empty_file 异常, 不产生记录 |
| 非结构化扩展名（pdf 等） | 记 unhandled_type 异常, 不解析, 需人工 |
| 顶层为 dict 的 JSON | 按单条记录处理, 不丢弃 |
| 敏感/异常命中 | 只标记, 从不删除或修改原始数据 |

**残留限制（需人工补审）**:
- 标签是否真正能从证据**语义推导**（脚本只查证据字段非空）
- 困难负样本、边界样本是否足量（脚本只给类别分布）
- License 是否允许当前用途（见 evidence/source/ 阶段3 证据）
- 模板泄漏需到阶段9泄漏检查专项处理

## 6. 阈值说明（供审查）

| 检查 | 阈值 | 理由 |
| --- | --- | --- |
| 异常长度 | > max(P99×3, 2000) | 分布自适应, 下限防误报长文档 |
| ID/记录重复 | 完全相等 | 零容忍 |
| 敏感-高危（密钥/令牌/证件号） | 命中即逐条上报 | 泄露后果严重, 零容忍 |
| 敏感-低危（邮箱/电话/内网IP/路径） | 计数 + 抽样5条 | 合成研究数据中普遍, 全量上报会淹没高危信号 |
| 人工抽检 | 全部异常 + 每类别 ≥2 条 + 补足至 6.3 最低抽样量（seed=42 可复现） | 手册 6.3 分层与最低样本量 |
| 字段类型 | 已配置字段与期望类型不符即上报（bool 视为类型错误） | Prompt 05 字段类型检查 |

## 7. 初步结论（AI 草案, 待人工）

- **longmemeval_cleaned_2025**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）
- **longmemeval_v2_2026**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）
- **multiwoz_2_2_2020**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）
- **stabletoolbench_2024**: 待 Gate 3 批准后补充样本
- **t2ranking_2023**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）

---

*本文件由 `scripts/audit/stage4_sample_audit.py` 自动生成; 修改需 B 重跑并留痕。*
