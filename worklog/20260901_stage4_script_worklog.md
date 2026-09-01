# 数据工作日志 2026-09-01（Annotator B: DGXD01）

## 事项：阶段4 审计脚本预写 + 现有 v0 样本试运行

- 前置说明：Gate 0~2 尚待 Reviewer 批准（见 reports/reviewer_checklist.md），Gate 3 未开始。
  本次为 B 职责内**脚本预写**，不构成阶段4正式执行，不改变任何 Gate 状态。

## 完成

- 新增 `scripts/audit/stage4_sample_audit.py`（阶段4 小样本质量审计脚本，预写版）：
  - 结构解析（json/jsonl/csv/.tsv，顶层 dict 按单条处理）；
  - 字段缺失/类型/null字符串化/重复ID/整条重复/异常长度（P99×3 且 >2000，阈值见报告第6节）；
  - ID/引用完整性（longmemeval_cleaned 专用：haystack_session_ids 与 sessions 数量一致、
    answer_session_ids 悬空检查）；
  - 敏感扫描分级：高危模式（密钥/令牌/证件号）逐条上报；低危模式（邮箱/电话/内网IP/路径）
    计数+抽样5条，避免合成研究数据噪声淹没高危信号；
  - 在线依赖（URL 引用计数）、类别覆盖统计、6.3 最低人工抽样量计算；
  - 人工复核清单（全部异常记录 + 分层随机抽检，seed=42 可复现）；
  - 静默丢失风险清单（Prompt 05-R 要求）显式写入报告；
  - 红线遵守：只读 data/raw（含启动时路径断言），产出仅写 4 个指定位置。
- 试运行于 v1.0 遗留 v0_sample 文件（非 Gate 3 批准样本，报告中已显著标注）：
  - longmemeval_cleaned 500 条、longmemeval_v2 451 条、stabletoolbench 10 条可审计；
  - 8 个数据集仅清单无数据文件，报告标注"待 Gate 3 批准后由 A 下载"；
  - 发现并修复脚本两处审计缺陷（试运行的价值所在）：
    1) 敏感扫描原扫 JSON dump 转义串，`文本冒号+换行` 误报为 Windows 路径 8008 次
       → 改为递归提取真实字符串值再扫描；
    2) 低危敏感全量逐条上报产生 491 条噪声 → 改为分级上报。

## 试运行主要发现（供参考，非正式结论）

- stabletoolbench v0 样本 10 条中 11 个高危异常（缺 ID/缺标签/ID 重复），样本文件
  混装了查询文件与轨迹文件，建议 A 补样本时按文件类型分开；
- longmemeval_v2 有 2 条 `image` 字段值为字符串 "None"（疑似 null 字符串化）；
- longmemeval_cleaned 含合成邮箱/路由器默认 IP（10.0.0.1 等），属合成内容，无需处置；
- 无任何高危敏感模式（密钥/令牌/证件号）命中。

## 产出物

- scripts/audit/stage4_sample_audit.py（脚本）
- reports/stage4_sample_audit_report.md（试运行报告，显著标注非正式）
- data/interim/stage4_anomalies.csv（异常清单 30 条）
- evidence/hashes/stage4_sample_hash.txt（抽样哈希）
- evidence/audit/stage4_audit_summary.json（机读摘要）

## 未完成 / 下一步

- 待 Reviewer 批准 Gate 0~2（阶段0-1-2 审查清单已就绪）；
- Gate 3 批准后：A 按手册下载 50~100 条新样本 → B 用本脚本正式运行并出正式报告；
- 本分支（stage4-audit）为脚本预写分支，正式阶段4产出建议另开分支或并入阶段4分支。

## 阻塞

- 无（推送权限已开通，本分支可直接推送）。

# 数据工作日志 2026-09-01（补记：B 复核 + 证据移交）

## 事项：阶段1~2 产出复核 + License 证据移交

- 完成 `reports/b_review_stage1_2.md`：阶段1通过（2 建议），阶段2发现 1 不合格项（F1: machine_unlearning_bench 证据目录不存在、零证据文件，违反"下载前 License 证据先行"红线）+ 2 待确认项
- 整理 `evidence/source_workpack_handover/`：v1.0 时期 AI 辅助核验产出（7 数据集 30 文件）移交 A 用于阶段3
- 覆盖统计独立复算：认可修订后口径（知识检索 4 正式候选，msmarco/trec 为方法论参考）
- 登记表 12 行字段完整性 + evidence_dir 真实性验证：11/12 通过，machine_unlearning_bench_2025 失败
- Gate 状态不变：0~2 仍待 Reviewer 批准；F1 修复建议在 Gate 2 批准前完成

## 产出物

- reports/b_review_stage1_2.md
- evidence/source_workpack_handover/（30 文件 + 移交说明）
