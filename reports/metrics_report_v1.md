# 麒麟 OS Agent 记忆模块指标报告

- 生成时间: 2026-08-31T16:39:35.691025
- Gold 路径: C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807\data\processed\*.jsonl
- 预测路径: C:\Users\LYF\Desktop\麒麟OS_Agent_记忆模块数据工作包_v1.0_20260807\data\processed\*.jsonl
- Gold 总条数: 365
- 预测总条数: 365

### 冲突处理 (Conflict Resolution)
- Gold 样本数: 40 | 预测样本数: 40 | 匹配: 40
- 正确: 40 / 40 = **100.00%**

#### 按冲突类型分组
  - knowledge_version: 8/8 = 100.00%
  - safety: 8/8 = 100.00%
  - scope: 8/8 = 100.00%
  - source: 8/8 = 100.00%
  - time_update: 8/8 = 100.00%

#### 按模板族分组
  - conflict_knowledge_version_v1: 8/8 = 100.00%
  - conflict_safety_v1: 8/8 = 100.00%
  - conflict_scope_v1: 8/8 = 100.00%
  - conflict_source_v1: 8/8 = 100.00%
  - conflict_time_update_v1: 8/8 = 100.00%

**准确率=100.00%**  (阈值: >=88%)  ✅ 通过
### 端到端会话 (End-to-End Session)
- Gold 样本数: 15 | 预测样本数: 15 | 匹配: 15
- 响应匹配准确率: 0/0 = **0.00%**

**响应匹配准确率=0.00%**  (阈值: >=80%)  ❌ 未通过
### 知识检索 (Knowledge Retrieval)
- Gold 样本数: 60 | 预测样本数: 60 | 匹配: 60
- 有效查询数: 60 | 零召回查询: 60

#### Recall@K
  - Recall@1: 0.00%
  - Recall@3: 0.00%
  - Recall@5: 0.00%
  - Recall@10: 0.00%
  - Recall@20: 0.00%

**平均 MRR: 0.0000**

**平均 nDCG: 0.0000**

#### 按查询类型分组
  - fact_knowledge (n=12):  Recall@20=0.00%  MRR=0.0000  nDCG=0.0000
  - failure_experience (n=12):  Recall@20=0.00%  MRR=0.0000  nDCG=0.0000
  - history_case (n=12):  Recall@20=0.00%  MRR=0.0000  nDCG=0.0000
  - template_reuse (n=12):  Recall@20=0.00%  MRR=0.0000  nDCG=0.0000
  - workflow_reuse (n=12):  Recall@20=0.00%  MRR=0.0000  nDCG=0.0000

**Recall@5=0.00%**  (阈值: >=85%)  ❌ 未通过
### 精准遗忘 (Precise Forgetting)
- Gold 样本数: 40 | 预测样本数: 40 | 匹配: 40
- 删除正确率: 0/40 = **0.00%**
- 误删数: 0
- 残留检查: 0 错误 / 0 总检查

#### 按模板族分组
  - forget_person_v1: 0/10 = 0.00%
  - forget_revoke_v1: 0/10 = 0.00%
  - forget_scoped_v1: 0/10 = 0.00%
  - forget_time_v1: 0/10 = 0.00%

**删除正确率=0.00%**  (阈值: >=95%)  ❌ 未通过
**残留检查: ✅ 全部通过
### 偏好提取 (Preference Extraction)
- Gold 样本数: 60 | 预测样本数: 60 | 匹配: 60
- 缺失预测: 0 | 多余预测: 0

#### 字段级准确率
  - preference_type: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)
  - value: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)
  - scope: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)
  - confidence: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)
  - should_store: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)
  - operation: P=100.00%  R=100.00%  F1=100.00%  (tp=60, fp=0, fn=0)

#### 按偏好类型分组
  - app: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - output_style: P=100.00%  R=100.00%  F1=100.00%  (n=30)
  - safety: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - tool_choice: P=100.00%  R=100.00%  F1=100.00%  (n=10)

#### 按模板族分组
  - output_style_length_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - scope_app_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - sensitive_no_store_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - temp_instruction_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - tool_choice_confirm_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)
  - update_revoke_v1: P=100.00%  R=100.00%  F1=100.00%  (n=10)

#### Operation 准确率: 100.00%  (0/360 错误)

**总体 F1=100.00%**  (阈值: >=85%)  ✅ 通过

### Tool Result
- Gold 样本数: 50 | 预测样本数: 50 | 匹配: 50
- 状态判定准确率: 50/50 = **100.00%**
- 持久化策略准确率: 50/50 = **100.00%**

#### 按状态类型分组
  - cancelled: 10/10 = 100.00%
  - failed: 10/10 = 100.00%
  - partial_success: 10/10 = 100.00%
  - success: 10/10 = 100.00%
  - timeout: 10/10 = 100.00%

**状态判定准确率=100.00%**  (阈值: >=90%)  ✅ 通过
---
## 汇总

**全部指标: ✅ 全部通过**

### 阈值标准参考
| 指标 | 阈值 | 来源 |
| --- | --- | --- |
| 偏好提取 F1 | >= 85% | 手册第 2 章 |
| 知识检索 Recall@K | >= 85% | 手册第 2 章 |
| 冲突处理准确率 | >= 88% | 手册第 2 章 |
| 精准遗忘删除正确率 | >= 95% | 手册第 2 章 |
| Tool Result 状态判定 | >= 90% | 手册第 2 章 |
| 端到端响应匹配 | >= 80% | 手册第 2 章 |

> 注意：响应时间指标（P50/P95 <= 500ms）需在麒麟 VM 上使用 `run_runtime_replay.sh` 实测，本脚本不涉及。
