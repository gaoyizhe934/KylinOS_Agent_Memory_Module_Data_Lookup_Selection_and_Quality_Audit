# 阶段8 B 侧复核：A 候选池重建 + 试标集 v3（DGXD01，2026-09-04）

> 响应：PR #28 A 推送（HEAD bf42099，候选池重建方案/证据 + 试标集 v3）。
> 依据 A 列 B 侧 5 项任务逐项复核；红线：B 不代 A 标注、不代 Reviewer 裁定；本文件仅 B 复核结论与裁定意见。
> 复核环境：本地复跑 A 脚本（stage8_semantic_dedup.py / stage8_kappa.py --format kma，registry 单源）+ 结构/溯源脚本化核验。

---

## 一、复核结果总表

| # | A 布置任务 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 复核去重口径（v1 缺陷可复现；--strict exit 1） | ✅ 通过 | v1 五任务重复率 88%~93% 与 A 报告一致；--strict exit 1 |
| 2 | 复核重建候选池 schema/溯源/枚举 | ✅ 通过（含 1 项报告笔误见 §二.1） | 77 条；schema/raw_id 0 问题；template_family 28 族 |
| 3 | 复核试标集 v3 结构 + 去重 | ✅ 通过 | 40 条 5 任务×8；sample_id 唯一；public 21/team 19；回源 v2 池 CLEAN |
| 4 | Kappa 工具对 v3 骨架就位 | ✅ 通过 | registry 一致字段 v3 骨架全含；冒烟运行 PASS |
| 5 | B 裁定意见（来源占比/语言策略等） | ✅ 出具 | 见 §二.4 |

---

## 二、逐项复核详情

### 1. 去重口径复核（任务 1）

复跑 `stage8_semantic_dedup.py --pool interim --strict`：

| 任务 | 总量 | 语义唯一 | 冗余条数 | 冗余率 (total-unique)/total |
| --- | --- | --- | --- | --- |
| conflict_resolution | 40 | 5 | 40 | 88% |
| end_to_end_session | 15 | 1 | 15 | 93% |
| knowledge_retrieval | 60 | 5 | 60 | 92% |
| precise_forgetting | 40 | 4 | 40 | 90% |
| preference_extraction | 60 | 6 | 60 | 90% |

- `--strict` 检出 DUP → **exit 1**（符合 A 预期：证明 v1 缺陷可被硬校验拦截）。
- 归一化口径评审：剥离"第 N 次/version/v1.1/序号/时间戳"计数器噪音、取任务语义主字段（query/user_message/forget_instruction/scenario+candidates/turns）——口径**合理**，能正确暴露"模板×计数器"复制，且不误伤真实差异样本（multiwoz/t2ranking 真实数据 100% 唯一）。
- ⚠️ 适用范围提示（非缺陷）：对**无 input 的试标集索引文件**（stage8_trial_set_v3.jsonl 仅含 sample_id/task_type/source/template_family）直接跑本脚本会走兜底整条归一化而**误报 DUP**（8 组 29 条）。A 报告采用"sample_id 唯一 + 回源候选池 dedup CLEAN"口径**正确且已通过**；建议脚本头部注明"仅适用含 input 的候选池/processed"，避免 Reviewer/CI 误用。

### 2. 候选池 v2 schema/溯源/枚举复核（任务 2）

逐文件脚本化核验（5 文件合计 77 条）：

| 任务 | 文件实际 source 分布（public/team） |
| --- | --- |
| conflict_resolution | 5 / 6（11） |
| end_to_end_session | 6 / 6（12） |
| knowledge_retrieval | 12 / 8（20） |
| precise_forgetting | 6 / 8（14） |
| preference_extraction | 10 / 10（20） |
| **合计** | **39 / 38（77）** |

- schema 校验：sample_id 前缀与任务匹配（conf_v2_/e2e_v2_/retr_v2_/forg_v2_/pref_v2_）、task_type 一致、input 非空、template_family 非空——**0 问题**。
- 溯源：public_derived 39 条全部带 raw_id + source_file，无缺——✅。
- team_authored evidence 非空——✅。
- template_family 共 28 族（os_* 自建 + lme_*/multiwoz_*/t2ranking_* 真实源），无"模板×计数器"复制——✅。

### 3. 试标集 v3 复核（任务 3）

- 结构：40 条 = 5 任务 × 8 ✅；sample_id 唯一 ✅。
- source 分布：public_derived 21 / team_authored 19（≈53%/47%），与 A 报告一致 ✅。
- template_family 覆盖 19 族，无同文复制 ✅。
- 回源：40 条 sample_id 全部存在于 v2 候选池 ✅；候选池本身 dedup CLEAN（§1）→ 试标集语义全异成立 ✅。

### 4. Kappa 工具就位（任务 4）

- registry/kappa_agreement_fields.json 为一致字段集单一来源（preference 6 字段/retrieval 3/conflict 2/forgetting 3/tool 1/e2e 1）。
- v3 骨架 A/B 各 40 条，**gold 字段全部覆盖 registry 一致字段**（逐任务比对 0 缺失）✅。
- 冒烟：`stage8_kappa.py --a labels_A_trial_v3 --b labels_B_trial_v3 --format kma --fields-json registry/...` 可正常运行（40 条匹配、字段源=fields-json、报告/分歧 csv 生成成功）✅。空骨架 kappa=1.0 仅证明工具链路可用，**非有效 Kappa**；正式 Kappa 待 A/B 独立标注后计算。

---

## 三、B 发现需登记/修正项

1. **报告数字笔误（Low，请 A 更正）**：reports/stage8_candidate_rebuild_report.md §2.1 合计行写 `33（43%）/ 44（57%）`，与文件实际 `39 / 38（≈51%/49%）` 不符（明细行与文件一致，仅合计行笔误）。不影响候选池文件本身。
2. **template_family 命名漂移登记（Low，不阻塞试标）**：v2 候选采用新命名族（os_*/lme_preference_v1/t2ranking_query_v1 等），与 enum_dictionary.json `enum.template_family` 现有词表（conflict_scope_v1/output_style_length_v1/t2ranking_retrieval_v1 等旧命名）不一致。v2 候选为 candidate_only 新增，暂不阻塞；**量产/8.2 收口时需把新命名族登记入 enum_dictionary 或统一命名规范**，防字段漂移。
3. **registry status 状态差提示（既有，非本批引入）**：registry/kappa_agreement_fields.json `status=FREEZE_PROPOSAL`，与 schema.json `kma_alignment.status=FROZEN`（#27 认定）不同步；建议下次 registry 更新时一并置 FROZEN。

---

## 四、B 裁定意见（任务 5，供 Reviewer 决策）

| A 提请裁定项 | B 意见 |
| --- | --- |
| 1. 试标集 v2 废弃 | **同意废弃**：缺陷证据充分（conf 3 对同文/forg 一组 5 同文/e2e version 递增），v2 无权威价值，Kappa 必然虚高。 |
| 2. 来源占比 | **接受当前文件实际 39/38（≈51%/49%）作为试标集**；试标目的是验证标注一致性与流程，非最终覆盖。A 报告 43/57 为笔误请更正。若 Reviewer 要求提高公开占比，建议在 8.2 量产扩充公开源，试标集不必再等。 |
| 3. 语言策略 | **同意保留原文不转写**（真实数据英文 + OS 自建中文，转写有语义漂移风险）。建议手册补充"按原文语义标注、语言差异不作为分歧"规则，label_check 不做语言归一。 |
| 4. tool_result 本轮不产 | **同意**：红线（封存集必须麒麟 VM 真实回放）优先，登记为阶段 10 依赖。 |
| 5. retrieval 版本引用 | **同意** D9/KB 就绪前按标注手册 §4 风险注执行（NOT production 标记）；KB 就绪后回填 version_refs。 |

---

## 五、结论

A 候选池重建（77 条多样化候选）+ 试标集 v3（40 条全异）**通过 B 侧复核**：v1 缺陷可复现（88~93%）、v2 候选 schema/溯源干净、v3 结构正确且语义全异、Kappa 工具（registry 单源）对 v3 骨架就位。复核中发现 1 处报告合计笔误 + 2 项登记项（均不阻塞试标）。

**建议 Reviewer 裁定 §四 5 项后放行 A/B 正式试标 v3（P1-5）**；放行后 A 标 labels_A_trial_v3、B 标 labels_B_trial_v3，各自 label_check exit 0 后跑 stage8_kappa --format kma ≥0.70。
