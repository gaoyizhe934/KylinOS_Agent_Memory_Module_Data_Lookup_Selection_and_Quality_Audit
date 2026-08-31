# 泄漏审计报告 2026-08-07

切分规则：按 template_family 整体分配，dev 50% / regression 20% / sealed_test 30%。
检查项：sample_id、user_id、conversation_id、template_family 跨集合重复。

| 任务 | 集合 A | 集合 B | 样本重复 | 用户重复 | 会话重复 | 模板族重复 | 结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| preference_extraction | dev | regression | 0 | 0 | 0 | 0 | PASS |
| preference_extraction | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| preference_extraction | regression | dev | 0 | 0 | 0 | 0 | PASS |
| preference_extraction | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| preference_extraction | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| preference_extraction | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | dev | regression | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | regression | dev | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| knowledge_retrieval | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | dev | regression | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | regression | dev | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| conflict_resolution | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | dev | regression | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | regression | dev | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| precise_forgetting | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |
| tool_result | dev | regression | 0 | 0 | 0 | 0 | PASS |
| tool_result | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| tool_result | regression | dev | 0 | 0 | 0 | 0 | PASS |
| tool_result | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| tool_result | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| tool_result | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | dev | regression | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | dev | sealed_test | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | regression | dev | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | regression | sealed_test | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | sealed_test | dev | 0 | 0 | 0 | 0 | PASS |
| end_to_end_session | sealed_test | regression | 0 | 0 | 0 | 0 | PASS |

结论：自建候选草稿按构造无跨集合泄漏；公开数据子集下载后需运行
`scripts/split/leakage_check.py` 对 user/conversation/workflow/template 重新审计。
