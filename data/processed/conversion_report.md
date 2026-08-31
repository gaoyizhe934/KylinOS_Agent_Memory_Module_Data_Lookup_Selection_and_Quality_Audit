# 统一 Schema 转换报告 2026-08-07

转换方式：interim gold_candidates → processed JSONL，按 `data/processed/schema.json` 校验。

- 输入：`data/interim/gold_candidates_*.jsonl`
- 输出：`data/processed/<task_type>.jsonl`
- 样本总数：265
- 静默丢失：0（未识别字段保留在原始 JSONL，转换脚本不丢弃）
- 每行保留：raw_id/source_file/source_version（public_derived 样本下载后回填）
- 幂等性：同一输入重复转换得到相同输出（哈希一致）

测试：`scripts/convert/test_convert.py` 检查字段映射、幂等性和 raw 目录只读。
