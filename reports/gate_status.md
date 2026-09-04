# Gate 状态 2026-09-01（master，PR#1 合并后更新）

依据 v2.0 重建计划修订版，每阶段 Gate 未获 Reviewer 人工确认不得进入下一阶段。

| Gate | 阶段 | 要求 | 当前状态 | 产出物 |
| --- | --- | --- | --- | --- |
| Gate 0 | 阶段 0 | 目录可用，负责人明确，raw 目录只读/不直接修改 | ✅ Reviewer 已批准（PR#1，2026-09-01） | worklog/owners.md, reports/stage0_checklist.md, 目录骨架 |
| Gate 1 | 阶段 1 | 每项要求至少对应一个子集和一个可计算指标 | ✅ Reviewer 已批准（PR#1，2026-09-01） | reports/requirement_data_mapping_v2.md |
| Gate 2 | 阶段 2 | 所有候选有正式名称、版本线索、官方来源和任务说明 | ✅ Reviewer 已批准（PR#1，2026-09-01，含 5 项裁决） | registry/dataset_registry.csv, reports/stage2_coverage_report.md |
| Gate 3 | 阶段 3 | Reviewer 明确标记允许试用/需确认/淘汰 | ✅ Reviewer 已逐卡标记（2026-09-02）：允许试用 5 / 需确认 3 / 淘汰 4（不下载）；详见 registry conclusion 列 | registry/dataset_registry.csv（12 候选 Gate 3 标记）, reports/stage3_evidence_report.md |
| Gate 4 | 阶段 4 | 样本可解析，标签定义可理解，人工抽检通过 | ✅ Reviewer 已批准（2026-09-02，PR#17）：4/5 通过（longmemeval_cleaned / longmemeval_v2 / multiwoz / t2ranking）；stabletoolbench 条件待补 | reports/stage4_sample_audit_report.md, reports/stage4_manual_inspection_report.md, reports/stage4_manual_spotcheck_A.md |
| Gate 5 | 阶段 5 | 核心候选 >= 80 分；补充候选 >= 65 分 | ✅ Reviewer 已批准（2026-09-02）：签发 dataset_selection_decision_v2.md（核心 3 + 补充 2，其余条件/不采用） | reports/dataset_selection_decision_v2.md, reports/stage5_scoring_A.md, reports/stage5_scoring_B.md |
| Gate 6 | 阶段 6 | 再次下载可得到同一版本；文件数量和哈希完整 | ✅ Reviewer 已确认冻结基线（2026-09-02）：4/5 通过（manifest + 版本锁定）；stabletoolbench 条件待补 | reports/stage6_freeze_baseline.md, evidence/hashes/stage6_manifest.json, reports/stage6_b_verify_report.md |
| Gate 7 | 阶段 7 | 每条 processed 样本可追溯到 raw_id | ✅ Reviewer 已批准（2026-09-02，PR#21）：715/715 processed 可溯源（raw_id 500/500 public_derived，0 缺字段/0 非法 ts） | data/processed/*.jsonl, reports/conversion_report.md |
| Gate 8 | 阶段 8 | Kappa >= 0.70，分歧有裁决，所有标签有 evidence | ⏳ 下一阶段 |
| Gate 9 | 阶段 9 | 无用户/会话/模板泄漏；封存集哈希固定 | ⏳ 下一阶段 |
| Gate 10 | 阶段 10 | 命令、环境、原始日志、失败样本和统计脚本齐全 | ⏳ 下一阶段 |
| Gate 11 | 阶段 11 | 另一名同事可从文档复现；报告数字均能回到原始文件 | ⏳ 下一阶段 |

## 当前分支完成状态

- [x] 阶段 0：工作区初始化 — 目录验证 + 分工表更新
- [x] 阶段 1：需求—数据映射 — v2.0 六项指标映射完成
- [x] 阶段 2：候选查找与登记 — 12 个数据集登记，六类任务候选覆盖检查通过（每类 ≥2 正式候选，方法论/结构参考不计入；复查命令 `python scripts/oneclick/stage2_coverage_check.py`，退出码 0，登记完整性五项字段全部齐备）。URL 体检 2026-09-01 第二轮复测：官方 URL 12/12 可访问，数据 URL 11/12 已登记且可访问，toolbench_2024 官方 Drive 数据入口失效（404，核验记录见 evidence/audit/stage2_url_check_output_20260901.md，待 Reviewer 裁决处置）；`stage2_check_urls.py` 严格模式退出码 1 如实反映该项失败（详见 reports/stage2_coverage_report.md）
- [x] 阶段 3：来源、版本与 License 核验 — Reviewer 已逐卡标记（2026-09-02：允许试用 5 / 需确认 3 / 淘汰 4），Gate 3 通过
- [x] 阶段 4：小样本审计与人工抽检 — Reviewer 已批准（4/5，PR#17），stabletoolbench 条件待补
- [x] 阶段 5：候选选型与评分 — Reviewer 已签发 dataset_selection_decision_v2.md（Gate 5 通过）
- [x] 阶段 6：正式下载与冻结基线 — Reviewer 已确认（4/5，PR#19 证据 + stage6_freeze_baseline.md），stabletoolbench 条件待补
- [x] 阶段 7：统一 Schema 转换 — Reviewer 已批准（PR#21，715 条可溯源），Gate 7 通过
- [ ] 阶段 8~11：待后续推进（试标/双标 → 切分封存 → 麒麟 VM 回放 → 报告）

## 阶段8 候选池重建记录（2026-09-04，A = lyf-1213，feat/B-stage8-p1 分支）

- 背景：试标母体 gold_candidates（v1.0 AI 模板生成）语义级 88%~93% 重复（审计脚本 `scripts/audit/stage8_semantic_dedup.py`，证据 `evidence/audit/stage8_candidate_semantic_dedup_20260904.json`），Kappa 虚高、不具权威数据价值。
- 产出：重建候选池 77 条（5 任务，public_derived 43% + team_authored 57%，全部语义去重通过）+ 试标集 v3（40 条全异）+ A/B 骨架 v3；方案 `reports/stage8_candidate_rebuild_plan.md`，报告 `reports/stage8_candidate_rebuild_report.md`。
- 状态：⏳ 待 B 复核（去重口径/候选 schema/试标集结构）+ Reviewer 裁定（试标集 v2 废弃/来源占比/语言策略/tool_result 依赖/retrieval 版本引用），裁定前不量产、不正式试标。
- 红线遵守：重建候选仅 candidate_only，不触碰封存集；Gate 纪律未越权。

## Gate 3 待办清偿记录（2026-09-01，B = DGXD01，feat/B-stage3-prep 分支）

PR#1 审批意见（第四节）遗留三项待办，本分支逐一清偿：

| # | 待办 | 处置 | 证据 |
| --- | --- | --- | --- |
| 1 | toolbench_2024 降级执行（裁决: 降为方法论参考，不进首版封存） | 登记表 conclusion 已更新为「方法论参考（不采用）」并注明裁决依据；`stage2_check_urls.py` 增加方法论参考候选 data_url 跳过逻辑（official_url 仍验收），严格模式复跑**退出码 0**（Reviewer 要求「届时退出码应转为 0」达成） | evidence/audit/stage2_url_check_output_20260901_toolbench_downgraded.md |
| 2 | msmarco_2021 论文链接核验 | 核验通过: arXiv:1611.09268（NIPS 2016，MS MARCO 原始论文），官方项目页首段直接引用该链接，arXiv 摘要页 2026-09-01 实测可达；登记表 paper 字段由「待核验」更新 | evidence/source/msmarco_2021/paper_verification_20260901.md |
| 3 | machine_unlearning_bench 证据补齐（即 B 复核报告 F1 不合格项） | 证据包从零建立: 核查脚本输出 + HF API 元数据（cardData.license = "mit"）+ README 原文 + license_review.md（含 B 复核意见: 发布者为社区组织非论文官方，建议 Gate 3 从严标记） | evidence/source/machine_unlearning_bench_2025/（4 个文件） |

另: B 侧 workpack 移交包（7 个数据集 31 个 License 证据文件，2026-08-31 产出于 b-review-stage12 分支）已并入 `evidence/source_workpack_handover/`，供阶段 3 直接取用（移交说明见该目录 README）。

## Gate 3 主体工作记录（2026-09-01，A = Data Owner 授权，feat/B-stage3-prep 分支）

用户获 A（Data Owner）全部授权后执行阶段 3 主体工作，产出明细见 `reports/stage3_evidence_report.md` 与 `worklog/20260901_stage3_main_A.md`：

| # | 工作 | 结果 |
| --- | --- | --- |
| 1 | 版本线索锁定 | 12/12 候选锁定（GitHub commit SHA / HF revision / Web 核验），每候选新增 version_lock_20260901.md + api_snapshot_20260901/；校验命令 `python scripts/audit/stage3_version_lock.py` 退出码 0，已接入 CI |
| 2 | B 移交包取用 | 5 个已登记候选证据择优并入 evidence/source/（新增 8 个原始文件 + 10 个 review 合并版）；2 个未登记候选（dailydialog/locomo）暂存 evidence/source_unregistered/；移交目录按规则删除 |
| 3 | 登记表更新 | version 字段 12 行、license 字段 5 行更新为证据支撑描述 |

**Gate 3 裁决记录（2026-09-02，Reviewer = gaoyizhe）**：dureader=需确认（License 缺失）；t2ranking=允许试用（接受 HF 官方 THUIR 卡片）；machine_unlearning_bench=需确认（社区发布者，仅方法参考）；locomo=不启用（未登记，启用须先补阶段 2 登记卡）；A+B 独立性=Reviewer 独立复核确认。逐卡标记已写入 registry conclusion 列。

## 说明

`已完成` 表示本分支已产出对应证据/产物；`待 Reviewer 批准` 表示需要人工确认后才能标记为通过。

## Schema 漂移自检（追加 2026-09-04，B = DGXD01）

- 依据：数据包_B轨字段漂移自检修复任务说明_20260904.md（对照 KMA Canonical/D3，主仓库 CANDIDATE_FOR_FREEZE）。
- 产出：reports/schema_drift_audit_B_20260904.md、registry/field_mapping.json（30 行映射登记）、scripts/audit/schema_drift_check.py（exit 0：0 未登记字段 / 0 分层缺失）、data/processed/enum_dictionary.json 增加 _meta 分层（NOT production shared enum）。
- 性质：扫描+登记+只读映射，未改既有 Gold 字段值、未重转；未冻结项（§四清单）待 E/D 裁定。
