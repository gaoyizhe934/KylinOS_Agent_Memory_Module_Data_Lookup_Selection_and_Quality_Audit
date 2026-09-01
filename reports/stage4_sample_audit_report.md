# 阶段4 小样本质量审计报告（AI 辅助草案）

> **性质声明**: 本报告由脚本自动生成, 仅覆盖结构与可机械检查项; 标签语义可推导性、困难样本覆盖等语义项需人工抽检后才能得出结论。Gate 4 是否通过由 Reviewer 决定。
>
> **运行备注**: 试运行：Gate 3 尚未批准，输入为 v1.0 遗留 v0_sample 文件，本结果仅用于验证脚本可用性与覆盖现有样本概况，不作为 Gate 4 评审依据；正式审计待 Gate 3 批准后按手册下载 50~100 条新样本重跑

- 运行时间: 2026-09-01 15:44:52
- 运行命令: `python scripts\audit\stage4_sample_audit.py --note 试运行：Gate 3 尚未批准，输入为 v1.0 遗留 v0_sample 文件，本结果仅用于验证脚本可用性与覆盖现有样本概况，不作为 Gate 4 评审依据；正式审计待 Gate 3 批准后按手册下载 50~100 条新样本重跑`
- Python: 3.10.11 / 平台: win32
- 审计执行: Annotator B (DGXD01)

## 1. 审计概览

| dataset_id | 状态 | 数据文件 | 记录数 | 唯一ID | 高危敏感 | 低危敏感(合计) | 在线引用 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bpmn_2_0_2013 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| dureader_retrieval_2022 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| longmemeval_cleaned_2025 | ok | 1 | 500 | 500 | 0 | 35 | 59 |
| longmemeval_v2_2026 | ok | 1 | 451 | 451 | 0 | 0 | 1 |
| msmarco_2021 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| multiwoz_2_2_2020 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| personachat_2018 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| stabletoolbench_2024 | ok | 6 | 10 | 3 | 0 | 0 | 0 |
| t2ranking_2023 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| toolbench_2024 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |
| trec_tracks_2024 | 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载 | 0 | 0 | 0 | 0 | 0 | 0 |

异常总数 **30**（高 11 / 中 12 / 低 7）

## 2. 逐数据集审计明细

### bpmn_2_0_2013

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### dureader_retrieval_2022

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### longmemeval_cleaned_2025


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| question | 72 | 192 | 258 | 355 | 21 | 0 |
| answer | 11 | 296 | 515 | 604 | 1 | 0 |

- 类别分布（正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检）: knowledge-update=78, multi-session=133, single-session-assistant=56, single-session-preference=30, single-session-user=70, temporal-reasoning=133

- 低危敏感模式（合成研究数据中常见, 已抽样入清单, 全量计数如下, 判真伪由人工）: email×32, private_ip×3
- 内容中出现 URL 引用 59 处（在线依赖风险需人工评估评测脚本是否运行时抓取）
- 6.3 最低人工抽样量: **50** 条（现有 500 条）

### longmemeval_v2_2026


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| question | 293 | 691 | 1122 | 1971 | 137 | 0 |
| answer | 18 | 132 | 242 | 469 | 1 | 0 |

- 类别分布（正/负/边界/困难覆盖的机械统计，语义覆盖需人工抽检）: dynamic-environment=86, dynamic-environment-abs=41, errors-gotchas=29, procedure=74, procedure-abs=32, static-environment=134, static-environment-abs=55
- 内容中出现 URL 引用 1 处（在线依赖风险需人工评估评测脚本是否运行时抓取）
- 6.3 最低人工抽样量: **50** 条（现有 451 条）

### msmarco_2021

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### multiwoz_2_2_2020

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### personachat_2018

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### stabletoolbench_2024


| 文本字段 | P50 | P95 | P99 | 最长 | 最短 | 零长 |
| --- | --- | --- | --- | --- | --- | --- |
| query | 197 | 228 | 228 | 228 | 0 | 4 |
- 6.3 最低人工抽样量: **10** 条（现有 10 条）

### t2ranking_2023

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### toolbench_2024

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

### trec_tracks_2024

- 状态: 无数据样本（仅清单/管理文件），待 Gate 3 批准后由 A 下载

## 3. 异常类型汇总

| 异常类型 | 数量 |
| --- | --- |
| sensitive_hit | 5 |
| missing_field | 4 |
| missing_label | 4 |
| missing_evidence | 4 |
| length_anomaly | 4 |
| duplicate_id | 3 |
| duplicate_record | 3 |
| null_string | 2 |
| unhandled_type | 1 |

逐条异常明细见 `data/interim/stage4_anomalies.csv`。

## 4. 需人工逐条复核的样本 ID（节选）

- **longmemeval_cleaned_2025**: 031748ae, 031748ae_abs, 50635ada, 5a4f22c0, gpt4_d9af6064, 0f05491a, 18dcd5a5, 311778f1, 57f827a0, 58bf7951, 60bf93ed, 6ae235be, 75f70248, 7a87bd0c, 80ec1f4f_abs, 852ce960, 8fb83627, 95bcc1c8, aae3761f, bc149d6b
- **longmemeval_v2_2026**: 499488a6, d1d8cf9f, 00aa905a, 12f8cfd2, 17a03f9b, 233f9f09, 48a52262, 58c34839, 5b249b5c, 674a6972, 6cb8ce37, 7351cbcc, 73cbefdc, 77db204d, 910135bb, 9ff0ffff, aa4a4b7b, bf98bb38, c4c0e117, c80ca967
- **stabletoolbench_2024**: 1073, 588, 608

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
| 人工抽检 | 每数据集每类别 ≥2 条或 5% | 手册 6.3 分层原则 |

## 7. 初步结论（AI 草案, 待人工）

- **bpmn_2_0_2013**: 待 Gate 3 批准后补充样本
- **dureader_retrieval_2022**: 待 Gate 3 批准后补充样本
- **longmemeval_cleaned_2025**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）
- **longmemeval_v2_2026**: 结构检查通过, 建议进入人工抽检（50~100条新样本到位后重跑）
- **msmarco_2021**: 待 Gate 3 批准后补充样本
- **multiwoz_2_2_2020**: 待 Gate 3 批准后补充样本
- **personachat_2018**: 待 Gate 3 批准后补充样本
- **stabletoolbench_2024**: 存在 11 个高危异常, 建议先修复再进入人工抽检
- **t2ranking_2023**: 待 Gate 3 批准后补充样本
- **toolbench_2024**: 待 Gate 3 批准后补充样本
- **trec_tracks_2024**: 待 Gate 3 批准后补充样本

---

*本文件由 `scripts/audit/stage4_sample_audit.py` 自动生成; 修改需 B 重跑并留痕。*
