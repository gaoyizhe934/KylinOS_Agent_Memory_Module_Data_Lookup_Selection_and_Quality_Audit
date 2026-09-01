# 阶段计划与分工 v2.0（按实际人力适配）

人力：Annotator A × 1 + Annotator B × 1 + Reviewer × 1

---

## 阶段 0：工作区初始化（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 建目录结构 | A | 空数据包骨架 |
| 初始化 dataset_registry.csv | A | 登记表 |
| 确认分工 | A + B + Reviewer | owners.md |
| 验收 | Reviewer | Gate 0 批准 |

## 阶段 1：需求—数据映射（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 写需求映射文档 | A | reports/requirement_data_mapping_v2.md |
| 核对指标是否全覆盖 | B | 指标检查清单 |
| 验收 | Reviewer | Gate 1 批准 |

## 阶段 2：候选查找与登记（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 去 HuggingFace/GitHub 搜候选数据集 | A | 候选清单 |
| 填写登记卡（名称/版本/来源/任务） | A | 更新 dataset_registry.csv |
| 核对每类任务是否有 ≥2 候选 | B | 候选覆盖检查 |
| 验收 | Reviewer | Gate 2 批准 |

## 阶段 3：来源/版本/License 核验（1 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 打开官方仓库，存档 License 原文 | A | evidence/source/*/ 证据文件 |
| 写来源审查报告 + License 审查报告 | A | source_review.md + license_review.md |
| 核对证据是否齐全、结论是否合理 | B | 审查报告复核 |
| 逐卡标记"允许试用/需确认/淘汰" | **Reviewer** | 更新 dataset_registry.csv |
| 验收 | Reviewer | Gate 3 批准 |

> 红线：任何数据下载前，必须先存档 License 原文并获 Reviewer 标记。

## 阶段 4：小样本抽样审计（1 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 下载 50~100 条小样本 | A | data/raw/ 下样本文件 |
| 跑审计脚本（结构解析、敏感扫描、异常检测） | B | sample_audit_report.md + anomalies.csv |
| 人工抽检样本质量 | A + B | 抽检记录 |
| 验收 | Reviewer | Gate 4 批准 |

## 阶段 5：候选选型与评分（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 按附录 B 十项 100 分制打分 | A | 评分表 |
| 核对分数和结论 | B | 评分复核 |
| 确认最终选型结论 | **Reviewer** | dataset_selection_decision_v2.md |
| 验收 | Reviewer | Gate 5 批准 |

## 阶段 6：正式下载与冻结（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 跑下载脚本 + 镜像路由 | A | data/raw/ 下完整数据 |
| 算 SHA256、写 manifest、确认只读 | B | sha256sum.txt + manifest.json |
| 验收 | Reviewer | Gate 6 批准 |

## 阶段 7：统一 Schema 转换（0.5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 写转换脚本 + 跑转换 | A | data/processed/ 下 JSONL |
| schema 校验 + 幂等性测试 + timestamp 修复 | B | 校验报告 + conversion_report.md |
| 验收 | Reviewer | Gate 7 批准 |

## 阶段 8：标注（8~10 天，最耗时）

### 8.1 试标（1 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 每人独立标 30~50 条 | A + B | 试标结果 |
| 算 Cohen's Kappa | B | Kappa 值 |
| 如果 Kappa < 0.70，修订标注手册 | A + B + Reviewer | 修订版 annotation_guideline.md |
| 验收 | Reviewer | 批准进入量产 |

### 8.2 候选草稿生成（3~4 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 批量生成候选草稿（偏好/检索/冲突/遗忘/Tool/端到端） | A | gold_candidates_*.jsonl |
| 结构化校验 + 模板族统计 | B | 校验报告 |
| 验收 | Reviewer | 候选草稿批准 |

### 8.3 双人标注 + 裁决（4~5 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 双人独立标注全部样本 | A + B | 标注结果 |
| 裁决分歧，写 final_label | **Reviewer** | gold_draft.jsonl + disagreement_log.csv |
| 验收 | Reviewer | Gate 8 批准 |

## 阶段 9：切分封存（1 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 跑 split_and_seal.py 切分 | B | dev/regression/sealed_test |
| 泄漏检查（用户/会话/模板族） | B | 泄漏检查报告 |
| 算 sealed_test 哈希，锁定答案 | B | split_manifest.csv + seal_record.md |
| sealed_test 答案由 Reviewer 持有 | **Reviewer** | 答案文件 |
| 验收 | Reviewer | Gate 9 批准 |

## 阶段 10：麒麟 VM 真实回放（1~2 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 准备回放包（input_manifest.json） | A | data/runtime_replay/ |
| 在麒麟 VM 上执行回放 | A | 原始日志 + 截图 |
| 统计延迟 P50/P95/P99 | B | 延迟报告 |
| 记录环境硬件 + 软件版本 | B | environment_manifest.md |
| 验收 | Reviewer | Gate 10 批准 |

## 阶段 11：报告与数据交接（1 天）

| 任务 | 谁做 | 产出物 |
| --- | --- | --- |
| 跑指标计算脚本，填真实分数 | B | evaluation_report_v2.docx |
| 写数据卡 + 复现文档 | A | data_card_v2.md + reproduction.md |
| 核对所有数字能否追溯到原始文件 | B | 可追溯性检查 |
| 写交接文档 | A | handoff.md |
| 终审所有报告 | **Reviewer** | 全部 Gate 关闭 |
| 验收 | Reviewer | Gate 11 批准 |

---

## 工作量总览

| 角色 | 主要工作 | 最忙的阶段 |
| --- | --- | --- |
| **Annotator A** | 对外搜索、下载、转换、写文档、标注 | 阶段 2/3/6/7/8/10 |
| **Annotator B** | 对内校验、审计、统计、切分、脚本、标注 | 阶段 4/7/8/9/11 |
| **Reviewer** | 审批 Gate、裁决分歧、持有答案 | 每个阶段末尾 |

## 核心原则

- A 和 B 标注时**独立进行，不共享答案**
- Reviewer **只看结果不干活**，保持审批独立性
- Kappa < 0.70 时退回修订，**禁止带病量产**
- **任何阶段未获 Reviewer 批准，不得进入下一阶段**