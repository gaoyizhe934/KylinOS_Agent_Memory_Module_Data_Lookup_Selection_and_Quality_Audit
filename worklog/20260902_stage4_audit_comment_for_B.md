## 阶段4 审计问题反馈（供 B 复核，非提交）

> 触发：A 运行 `scripts/audit/stage4_sample_audit.py` 对 4 个"允许试用"数据集样本执行审计（生成 4 个产物：report/anomalies/hash/summary）。
> 目的：请 B 复核以下问题，确认是脚本适配缺陷还是样本问题。

### 审计结果概览

| 数据集 | 记录数 | 唯一ID | 异常数 | 异常类型 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | 100 | 100 | 12 | type_mismatch×10, sensitive_hit(email,low)×2 |
| longmemeval_v2_2026 | 100 | 100 | 1 | null_string×1 |
| multiwoz_2_2_2020 | 100 | **1** | **99** | duplicate_id×99 |
| t2ranking_2023 | 100 | **1** | **99** | duplicate_id×99 |
| stabletoolbench_2024 | 目录不存在 | 0 | 0 | — |

### ⚠️ 需 B 复核：multiwoz / t2ranking 的 99 条 duplicate_id

脚本判定 `unique_ids=1`、`duplicate_id×99`，但 **样本本身 ID 全部唯一**（A 已验证）：

- multiwoz 样本 100 条，`dialogue_id` 全唯一（示例：`MUL2372.json` / `PMUL3314.json` / `SNG01206.json`）
- t2ranking 样本 100 条，`qid` 全唯一（示例：`21096` / `3675` / `828`）

异常清单中 `record_id` 均为空字符串 `''`，说明**脚本未从这两个数据集中识别出 ID 字段**，把 100 条记录都当作 ID 为空，因此全部判为"重复"。

疑似原因：脚本 `ID_FIELD_HINT = (^|_)(id|question_id|query_id|sample_id|uid)$` 未覆盖：
- multiwoz 的 `dialogue_id` 字段
- t2ranking TSV 第一列的 `qid` 字段（且 TSV 列名映射可能未将该列识别为 ID）

### 建议（供 B 判断）

1. 在 `DATASET_CONFIGS` 中为 multiwoz_2_2_2020 显式声明 `id_field='dialogue_id'`、为 t2ranking_2023 声明 `id_field='qid'`
2. 或扩展 `ID_FIELD_HINT` 正则覆盖 `dialogue_id`/`qid`
3. 若为 TSV 首列，确认列名识别逻辑

### 其余数据集结论（供 Reviewer Gate 4）

- **longmemeval_cleaned_2025** / **longmemeval_v2_2026**：结构通过（100 唯一 ID），建议进入人工抽检（各 50 条）
- **stabletoolbench_2024**：目录不存在（样本未补，Low-3 待办）

### 产物文件（已生成）

- `reports/stage4_sample_audit_report.md`
- `data/interim/stage4_anomalies.csv`
- `evidence/hashes/stage4_sample_hash.txt`
- `evidence/audit/stage4_audit_summary.json`