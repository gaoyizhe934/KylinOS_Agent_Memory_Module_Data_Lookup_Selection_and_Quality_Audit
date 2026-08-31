# 麒麟 OS Memory Gold 标注手册 v1.0（候选草稿）

## 总原则

- 标签必须能从 input/evidence 直接推导，禁止无证据猜测。
- 区分临时指令（should_store=false）与长期偏好（should_store=true）。
- 冲突样本必须写清 conflict_type、winner 与 resolution_reason。
- 遗忘样本必须同时给出 target_ids 与 must_keep，并检查重启/重建索引后的残留。
- Tool Result 必须区分 success/failed/cancelled/timeout/partial_success，禁止把失败写成成功。
- AI 只能生成候选标签；最终标签必须由双人独立标注 + Reviewer 裁决。

## 试标流程

1. 双人独立标注 30-50 条，禁止先讨论答案。
2. 汇总分歧并按类型聚类：任务定义、偏好/临时边界、作用域、证据不足、冲突优先级、应删/应留。
3. 修订本手册后回溯重审受影响样本。
4. 正式阶段双人独立提交，脚本只计算一致性，不自动覆盖。
5. Reviewer 查看原始证据与两份标签，写出 final_label 与 decision_reason。
