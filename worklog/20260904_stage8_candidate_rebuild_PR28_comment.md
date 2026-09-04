# PR#28 评论：候选池重建完成，提请 B 复核 + Reviewer 裁定

> 发起：Annotator A（lyf-1213）
> 日期：2026-09-04
> 定位：本 PR 新增「候选池重建方案 + 重建证据 + 试标集 v3」，供 B 复核、Reviewer 裁定后进入正式试标。

---

## 一句话

v1.0 模板母体存在**语义级 88%~93% 重复**（实测证据见下），不能作权威数据种子。A 已完成候选池重建（77 条多样化候选，全部语义去重通过）+ 试标集 v3 重抽（40 条全异）。**请 B 复核、Reviewer 裁定后，A/B 再进入正式试标。**

## 产出清单（本 PR 新增）

| 文件 | 内容 |
| --- | --- |
| `reports/stage8_candidate_rebuild_plan.md` | 重建方案（原则/来源/去重/Gate/待裁定） |
| `reports/stage8_candidate_rebuild_report.md` | 重建证据报告 |
| `scripts/audit/stage8_semantic_dedup.py` | 语义去重审计脚本（可复跑，strict 模式 exit 1） |
| `evidence/audit/stage8_candidate_semantic_dedup_20260904.json` | 缺陷量化证据 |
| `scripts/convert/rebuild_candidates_v2.py` | 候选池重建脚本（幂等，真实数据接地） |
| `data/interim/gold_candidates_*_v2.jsonl` | 重建候选池（77 条，5 任务） |
| `scripts/convert/sample_trial_set_v3.py` | 试标集重抽脚本（分层抽样 + 去重校验） |
| `data/interim/stage8_trial_set_v3.jsonl` | 试标集 v3（40 条全异） |
| `scripts/convert/gen_trial_v3_skeletons.py` | 试标 v3 骨架生成 |
| `data/interim/labels_A/B_trial_v3.jsonl` | A/B 空骨架（40 条，KMA canonical 字段） |

## 缺陷证据摘要

| 任务 | v1 总量 | 语义唯一 | 重复率 |
| --- | --- | --- | --- |
| conflict_resolution | 40 | 5 | 88% |
| end_to_end_session | 15 | 1 | 93% |
| knowledge_retrieval | 60 | 5 | 92% |
| precise_forgetting | 40 | 4 | 90% |
| preference_extraction | 60 | 6 | 90% |

试标集 v2 的 40 条中 conf 3 对同文、forg 一组 5 条同文、e2e 靠 version 号递增——**Kappa 必然虚高**。

## 需要 Reviewer 裁定（5 项）

1. **试标集 v2 处置**：建议废弃（语义重复无权威价值）；
2. **来源占比**：重建后 public_derived 43% / team_authored 57%，是否需提高公开数据占比；
3. **语言策略**：真实数据（longmemeval/multiwoz）英文原文保留 + OS 中文自建，不转写（防语义漂移）；
4. **tool_result**：本轮不产试标候选，登记阶段 10 麒麟 VM 回放依赖；
5. **retrieval 版本引用**：KB/D9 就绪前按标注手册 §4 风险注执行（NOT production 标记）。

## B 侧任务（DGXD01）

1. **复核去重口径**：`python scripts/audit/stage8_semantic_dedup.py --pool interim --strict`（应 exit 1，证明缺陷被检出）+ 复核 `--json` 证据的归一化口径是否合理；
2. **复核重建候选池**：schema 校验（sample_id 前缀/必填字段/evidence/raw_id 溯源）、枚举一致性（template_family 与 enum_dictionary）；
3. **复核试标集 v3**：结构校验（40 条 5 任务 × 8、source 分布、sample_id 唯一）+ 去重复跑（应 CLEAN）；
4. **就位 Kappa 工具**：确认 `stage8_kappa.py --format kma --fields-json registry/kappa_agreement_fields.json` 对 v3 骨架可直接运行（v3 字段集与 registry 一致）；
5. **给出 B 侧裁定意见**：来源占比 / 语言策略是否接受。

## A 侧后续（待 B/Reviewer 放行）

1. 用 `labels_A_trial_v3.jsonl` 独立标注 40 条（对照 `worklog/stage8_P1-5_labels_checklist_mc.md` 核对表 + 标注手册 v2）；
2. 提交前跑 `stage8_label_check_v2.py --labels data/interim/labels_A_trial_v3.jsonl --samples data/interim/stage8_trial_set_v3.jsonl` exit 0。

## Gate 纪律

**本方案未获 Reviewer 裁定前，A 不正式量产、不重抽正式试标**；重建候选池仅作 candidate_only 提交，不触碰封存集（红线：封存集必须麒麟 VM 真实回放）。