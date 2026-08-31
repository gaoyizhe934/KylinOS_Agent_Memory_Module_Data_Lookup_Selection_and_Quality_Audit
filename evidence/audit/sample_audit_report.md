# 样本质量审计报告 2026-08-07

审计对象：AI 生成的自建 Gold 候选草稿（candidate_only，非最终 Gold）。
审计方法：结构解析、必填字段、重复、异常长度、模板族、敏感信息扫描。

## 统计

- preference_extraction: 60 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 6
- knowledge_retrieval: 60 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 1
- conflict_resolution: 40 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 5
- precise_forgetting: 40 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 4
- tool_result: 50 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 5
- end_to_end_session: 15 条，重复 0，必填缺失 0，超长 0，极短 0，模板族 1

## 结论

- 结构解析成功率：100%（全部可读取为 JSONL）。
- 必填字段缺失：0；重复：0；超长/极短：0。
- 敏感信息命中：0（合成内容未使用真实个人信息/凭证）。
- 公开数据集样本审计：待网络可用后运行 `scripts\download\download_samples.py` 补充。
- 通过标准中的人工抽检、双人标注与 Reviewer 批准仍待人工完成。