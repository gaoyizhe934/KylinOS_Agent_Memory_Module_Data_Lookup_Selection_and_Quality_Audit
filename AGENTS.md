# AGENTS.md — 麒麟 OS Agent 记忆模块数据包

本文件供 AI Agent / 协作者快速了解项目上下文、当前进展、约定规范和下一步工作。

## 项目一句话

为麒麟 OS Agent 的记忆模块构建一份高质量、可追溯、真实回放的评测数据集（Gold Data），支持偏好提取、知识检索、冲突处理、精准遗忘、Tool Result、端到端会话六类任务。

## 关键背景文档（务必先读）

| 文件 | 内容 |
| --- | --- |
| `02_麒麟OS_Agent_记忆模块数据查找选型与质量审计指导手册_v1.0_20260729.docx` | 总纲手册，定义目录、Gate、评分、标注、切分、评测全部流程 |
| `麒麟OS_Agent_记忆模块数据包_v2.0_重建计划_修订版.docx` | v2.0 计划，含五条改进红线（Gate 纪律、License 先行、先标后产、禁 mock、硬校验） |
| `reports/requirement_data_mapping_v2.md` | 六项指标映射（通俗版 + 技术算法版） |
| `reports/gate_status.md` | 当前 Gate 状态总表 |
| `reports/reviewer_checklist.md` | Reviewer 审查清单 |

## 当前进展（2026-09-01）

- [x] 阶段 0：工作区初始化（目录 + 分工 + raw 只读）
- [x] 阶段 1：需求—数据映射（六项指标）
- [x] 阶段 2：候选查找与登记（12 个数据集，六类任务均 ≥2 候选）
- [ ] 阶段 3~11：未开始

当前工作分支：`clean-branch`（等待 Reviewer 批准后合并 master）

## 分工（3 人精简版）

| 角色 | 人员 | 职责 |
| --- | --- | --- |
| Annotator A | lyf-1213 | 数据收集/转换/标注/文档 |
| Annotator B | DGXD | 校验/审计/脚本/标注 |
| Reviewer | gaoyizhe | 审批 Gate/裁决分歧/持有封存答案 |

## 五条红线（违反即退回）

1. **Gate 纪律**：每阶段 Gate 未获 Reviewer 人工批准不得进入下一阶段
2. **License 先行**：任何数据下载前，先存档 License 原文并获 Reviewer 标记
3. **先定标再量产**：30~50 条试标，Kappa ≥ 0.70 后才允许规模化标注
4. **全链路禁 mock**：任何层级不得包含 mock/模拟/合成数据；端到端与 Tool Result 封存集必须来自麒麟 VM 真实回放
5. **数据质量硬校验**：timestamp 必须 ISO-8601；processed 全部可溯源 raw_id；relevant_ids 可解析到知识库；模板族与分布随包交付

## 数据管线（重要）

```
data/raw/       ← 原始下载，只读，不直接修改（通过 ingest 脚本）
data/interim/   ← 中间候选（gold_candidates_*.jsonl）
data/processed/ ← 统一 Schema 转换后（6 个 JSONL + schema.json）
data/gold/      ← dev(50%) / regression(20%) / sealed_test(30%)
registry/       ← 登记表（dataset/source/license/split）
evidence/       ← 来源证据、审计报告、哈希、AI 输出
reports/        ← 全部报告
scripts/        ← download/convert/split/validate/evaluate/oneclick
```

统一 Schema 字段（`data/processed/schema.json`）：
`sample_id, dataset_version, task_type, language, user_id, conversation_id, timestamp, input, gold, evidence, source, template_family, annotator_a, annotator_b, review_status`

## 六类任务与 Gold 标签

| 任务 | sample_id 前缀 | gold 关键字段 |
| --- | --- | --- |
| preference_extraction | `pref_` | preference_type, value, scope, confidence, should_store, operation |
| knowledge_retrieval | `retr_` | relevant_ids, relevance, hard_negative_ids, expected_answer_points |
| conflict_resolution | `conf_` | conflict_type, winner, resolution_reason, keep_ids, remove_ids |
| precise_forgetting | `forg_` | target_ids, expected_deleted, must_keep, checkpoints |
| tool_result | `tool_` | status, persist_policy, side_effect, failure_reason |
| end_to_end_session | `e2e_` | expected_memory, expected_response |

## 常用命令

```powershell
# 一键重建（幂等，不删已有证据）
python scripts/oneclick/run_all.py

# 指标计算（gold vs 模型预测）
python scripts/evaluate/evaluate_metrics.py --gold "data/processed/*.jsonl" --hyp <预测目录>

# 候选覆盖检查
python scripts/oneclick/stage2_coverage_check.py
```

## Git 工作约定

- 不要直接 push master，改到 `clean-branch` 或新建分支，交 PR
- commit message 格式：`阶段X: 简述`
- 大文件已被 .gitignore 排除，不要手动 add 大文件
- 修改后提交并 push 到当前分支即可

## 当前待办（阶段 3 起）

### 阶段 3：来源/版本/License 核验
- 迁移 26 份审查报告 + 42 个证据文件
- Reviewer 逐卡批准 12 个数据集
- 重点裁决遗留问题：
  1. T2Ranking 卡片声明效力
  2. ToolBench 附加声明与 Apache-2.0 的张力
  3. machine_unlearning_bench_2025（新增）是否接受

### 后续阶段速览
- 阶段 4：小样本抽样审计（50~100 条/数据集）
- 阶段 5：候选选型评分（附录 B 十项 100 分制）
- 阶段 6：正式下载与冻结（SHA256 + manifest）
- 阶段 7：统一 Schema 转换（timestamp 修复 + raw_id 溯源）
- 阶段 8：试标 → 双标 → 裁决（最耗时，8~10 天）
- 阶段 9：切分封存（泄漏检查 + 哈希锁定）
- 阶段 10：麒麟 VM 真实回放
- 阶段 11：报告与交接

## 已知问题与风险

| 风险 | 状态 | 预案 |
| --- | --- | --- |
| 网络受限 | 有代理(127.0.0.1:7890) | 下载脚本带镜像路由 gh-proxy/hf-mirror |
| 麒麟 VM 未就绪 | 待确认 | 阶段 10 独立后移；封存集不接受模拟数据 |
| 标注人力 | 2 标注 + 1 裁决 | 降量保质，Kappa 未达标退回试标 |
| 精准遗忘数据缺口 | 已补 1 个公开候选 | 实际遗忘数据仍需自建 |

## 给新 Agent 的第一句话

> 你的任务是推进阶段 X。先读 `reports/gate_status.md` 确认当前状态，读 `reports/requirement_data_mapping_v2.md` 理解指标，遵守五条红线，产出物放到规定目录，完成后更新 gate_status.md 并 commit 到 clean-branch。
