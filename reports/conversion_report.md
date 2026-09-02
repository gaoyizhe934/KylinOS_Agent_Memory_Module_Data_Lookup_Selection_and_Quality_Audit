# 阶段 7 B 侧转换校验报告

- 角色：Annotator B（DGXD01）
- 分支：`feat/A-stage7-schema`
- 日期：2026-09-02
- 依据：手册第 7 章「统一 Schema 转换」、A 侧 `scripts/convert/convert_to_schema.py` 和 `worklog/20260902_stage7_A.md`、`data/processed/schema.json`

## 校验范围

对 A 侧 PR #21 转换的 8 个 JSONL 文件（715 条记录）进行 B 侧独立校验：

1. 必填字段完整性（schema.json 15 字段）
2. timestamp 合法性 + 3 位日期残留检查
3. raw_id 溯源（public_derived 样本）
4. source_file / source_version 溯源
5. 行数对账（无静默丢失）
6. enum_dictionary.json 正确性
7. tool_result.jsonl 已删除
8. 幂等性测试

## 校验结果

### 1. 必填字段完整性

| 检查项 | 结果 |
| --- | --- |
| 缺字段数 | ✅ 0 |
| 检查范围 | 715 条 × 15 必填字段 = 10,725 检查点 |

### 2. timestamp 合法性

| 检查项 | 结果 |
| --- | --- |
| 非法 timestamp | ✅ 0 |
| 3 位日期残留（`2026-07-202T` 格式） | ✅ 0（已全部修复为 `2026-07-20T`） |
| A 侧修复数 | 215 条 team_authored 记录全部修复（fixed_ts=215, unfixed_ts=0） |

### 3. raw_id 溯源（public_derived）

| 检查项 | 结果 |
| --- | --- |
| public_derived 缺 raw_id | ✅ 0 |
| 涉及文件 | knowledge_retrieval_t2ranking.jsonl (200)、multiwoz_dialogues_sample.jsonl (200)、multiwoz_public_sample.jsonl (100) |
| total public_derived | 500 条全部有 raw_id |

### 4. source_file / source_version 溯源

| 检查项 | 结果 |
| --- | --- |
| 缺 source_file | ✅ 0 |
| 缺 source_version | ✅ 0 |

### 5. 行数对账

| 文件 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| conflict_resolution.jsonl | 40 | 40 | ✅ |
| end_to_end_session.jsonl | 15 | 15 | ✅ |
| knowledge_retrieval.jsonl | 60 | 60 | ✅ |
| knowledge_retrieval_t2ranking.jsonl | 200 | 200 | ✅ |
| multiwoz_dialogues_sample.jsonl | 200 | 200 | ✅ |
| multiwoz_public_sample.jsonl | 100 | 100 | ✅ |
| precise_forgetting.jsonl | 40 | 40 | ✅ |
| preference_extraction.jsonl | 60 | 60 | ✅ |
| **总计** | **715** | **715** | ✅ |

- team_authored：输入 215 = 输出 215，0 静默丢失；
- t2ranking：24,831 → 200（固定子集，全量保留在 raw）；
- multiwoz dialogues：512 → 200（固定子集，全量保留在 raw）；

### 6. enum_dictionary.json 校验

| 检查项 | 结果 |
| --- | --- |
| task_type 枚举一致 | ✅ 6 种（auxiliary_dialogue, conflict_resolution, end_to_end_session, knowledge_retrieval, precise_forgetting, preference_extraction） |
| source 枚举一致 | ✅ 2 种（public_derived, team_authored） |
| template_family 枚举一致 | ✅ 20 个 |
| template_family 分布一致 | ✅ |

### 7. tool_result.jsonl 已删除

| 检查项 | 结果 |
| --- | --- |
| 文件是否存在 | ✅ 已删除（v1.0 拟留，interim 源缺失无法溯源） |

### 8. 幂等性测试

| 检查项 | 结果 |
| --- | --- |
| test_convert.py | ✅ PASS（idempotent, no field drop） |
| 重复转换哈希一致 | ✅ before/after SHA256 一致 |
| EOL 规范化 | ✅ LF（CRLF→LF 规范化后比较） |

### 9. A 侧内置 audit

```
[audit] total= 715 issues= {'missing_field': [], 'invalid_ts': [], 'missing_raw_id_public': []}
```

## 产出物

| 产出文件 | 路径 |
| --- | --- |
| B 侧 schema 校验脚本 | `scripts/audit/stage7_b_schema_check.py` |
| B 侧转换校验报告 | `reports/conversion_report.md` |

## 已知问题

1. **t2ranking hard_negative_ids / expected_answer_points 为空**：公开集不提供困难负样本和答案点，属后续任务，不影响 Gate 7 可溯源性要求；
2. **tool_result.jsonl 已删除**：v1.0 拟留文件无法溯源（interim 源 gold_candidates_tool_result.jsonl 从未提交），违反红线 5（processed 全部可溯源 raw_id）。A 侧已删除并在诚实披露中记录，tool_result gold 候选将在阶段 8.2 产出；
3. **公开子集固定规模**：t2ranking 200/24,831、multiwoz 200/512，按手册「只取固定小规模子集」执行，全量保留在 data/raw；
4. **team_authored 215 条为候选草稿（Medium-1）**：user_id 为 `u_synthetic_*`、review_status=`candidate_only`，系模板生成候选草稿转换，**不冒充最终金标**。阶段 8 双标验证后转正为 gold；

## Gate 7 建议

| 检查项 | 结果 |
| --- | --- |
| 每条 processed 样本可追溯到 raw_id | ✅ 715/715 |
| 必填字段完整 | ✅ 0 缺字段 |
| timestamp 合法 | ✅ 0 非法 |
| 无静默丢失 | ✅ 输入=输出 |
| 幂等性 | ✅ 重复转换一致 |
| 前置 Gate 6 已收口 | ✅ PR #22 已合并，Gate 6 = ✅（4/5 冻结基线确认） |
| **综合** | **建议通过 Gate 7**（前置 Gate 6 已由 PR #22 收口，stabletoolbench 条件待补不影响已冻结的 4/5 数据集转换） |

## 诚实披露

1. B 侧独立运行 schema 校验脚本和幂等性测试，非直接使用 A 侧 audit 输出；
2. B 侧校验覆盖范围与 A 侧 audit 一致（715 条、15 必填字段、timestamp、raw_id），但使用独立脚本实现；
3. 本报告为 B 独立校验，**未经 Reviewer 确认**，最终 Gate 7 批准由 Reviewer 出具；
