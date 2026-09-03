# 阶段 8 B 侧工具交付（DGXD01）— 2026-09-03

- 分支：feat/B-stage8-kappa（基于 master = PR #24 合并后基线 ec42d04）
- 依据：标注手册 v1.3（data/gold/annotation_guideline.md，§8 Kappa 口径 / §11 命令）、PR #24 审阅闭环结论、五条红线。

## 一、本 PR 交付（3 脚本 + 1 测试）

| 文件 | 用途 | 对应手册 |
| --- | --- | --- |
| scripts/audit/stage8_kappa.py | A/B 试标一致性计算：总体 + 每任务分层 Cohen's Kappa；按各任务 gold 主字段集判定一致；A/B 标签约定 labels_A/B_trial.jsonl（JSONL：sample_id/task_type/gold/evidence）；输出 kappa 报告 json + 分歧 csv | §8 P1-2 |
| scripts/audit/stage8_trial_sample.py | 试标分层抽样：均衡覆盖可标注任务、固定种子可复现、排除 auxiliary_dialogue（§7.1 不做金标）；tool_result 无池时提示经 --extra/--per-task 补充 | §8.1 |
| scripts/validate/stage7_enum_check.py | 候选草稿枚举/结构一致性校验：sample_id 前缀、task_type/source/template_family/review_status 越界、gold 必填字段、retrieval hard_negative_ids 非空（P1-1 硬性，public_derived 例外）、字典缺失键提示 | §11 P2-8 |
| scripts/audit/test_stage8_kappa.py | Kappa 数学单测：已知案例 kappa=0.8、全一致=1.0、全同=1.0、随机水平=0、list 无序等价、CLI 端到端=0.8 | §8 |

## 二、验证结果（本机捆绑 Python 3 实测）

- test_stage8_kappa.py：ALL TESTS PASSED（6/6）
- stage8_trial_sample.py --total 40 --seed 42：5 个任务各 8 条 = 40；两次运行 SHA256 一致（确定性）；auxiliary_dialogue 0 混入；tool_result 池为空 → 提示待 A 提供受控候选
- stage7_enum_check.py：干净样本 exit 0；含越界样本 exit 1 并逐条报错（前缀/词表/hard_negative 空）

## 三、已知事项 / 风险

1. tool_result 暂无 processed 池：试标阶段需 A 按手册 §8.1 提供受控场景候选（candidate_only），经 --extra + --per-task tool=N 纳入；封存集仍须麒麟 VM 真实回放（禁 mock）。
2. enum_dictionary.json 缺 status/persist_policy/checkpoints/should_store/confidence/winner/expected_residual_count 词表：脚本已按「缺键提示」处理，建议 8.2 生成候选草稿时同步补字典。
3. e2e expected_response 语义等价无法全自动判定：脚本以规范化后精确比较计一致，语义等价差异会进分歧 csv，交由人工/Reviewer 复核。

## 四、下一步（红线顺序）

1. 本 PR 经 Reviewer 审查合并后：A/B 用 stage8_trial_sample.py 生成试标集 → 各自独立标注 labels_A/B_trial.jsonl（禁先讨论答案）。
2. B 跑 stage8_kappa.py 计算总体+分层 Kappa → 产出 reports/stage8_kappa_report_trial.* + disagreement csv。
3. Kappa>=0.70 提请 Reviewer 放行 8.2；<0.70 修订手册并回溯。
