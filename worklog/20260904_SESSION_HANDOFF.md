# 会话交接文档（2026-09-02 ~ 2026-09-04）— 下个会话优先阅读

> 本文件总结整个会话的全部工作、当前状态、已知问题与下一步，供下一个会话直接承接。
> 会话角色：**Annotator A（lyf-1213）**，项目：麒麟 OS Agent 记忆模块评测数据工作包。

---

## 0. 一句话现状

阶段 8（标注）P1-5 试标。发现母数据（gold_candidates）模板重复缺陷后，**已完成候选池重建（77 条多样化候选）+ 试标集 v3 重抽（40 条全异）+ 去重审计证据**，正待 B 复核 + Reviewer 裁定后进入正式试标。工作分支 `feat/B-stage8-p1`（PR #28，新增重建产物待提交）。

---

## 一、本会话完成的工作（按阶段）

### 阶段 5（候选选型评分）— 已完成 ✅
- 产出 `reports/stage5_scoring_A.md`（A 侧草案）：按附录 B 十项 100 分制对 12 候选打分
- A 草案：核心 3（t2ranking 84 / longmemeval_cleaned 82 / longmemeval_v2 81）、补充 4、不采用 5
- Reviewer 最终选型：`reports/dataset_selection_decision_v2.md`（Gate 5 收口，PR#20）
- 选型结论：3 核心 + 2 补充（t2ranking/longmemeval_cleaned/longmemeval_v2 + stabletoolbench/multiwoz）

### 阶段 6（正式下载与镜像路由）— 已完成 ✅
- 产出 `scripts/download/download_stage6.py` + 5 数据集 v0_subset 固定子集下载
- 镜像实测：hf-mirror.com ✅ / gh-proxy.com ✅ / 直连 HF、raw.githubusercontent、ghproxy.net、代理 127.0.0.1:7890 ❌
- 经历 Reviewer 审查（High-1/2、Medium-1/2/3）：修复 SSL 默认校验、流式写入+SHA256、log 追加模式、.gitignore 通配覆盖

### 阶段 7（统一 Schema 转换）— 已完成 ✅（后被 KMA 对齐重构）
- 升级 `convert_to_schema.py`：timestamp 修复、raw_id 溯源、公开子集固定规模、幂等
- 产出 `data/processed/` 715 条 + enum_dictionary.json
- 移除无法溯源的 v1.0 残留 `processed/tool_result.jsonl`

### 阶段 8（标注）— 进行中 🔶（见"当前状态"）

---

## 二、KMA 对齐（贯穿阶段 1/7/8 的重大变更）

### 关键背景
- 主仓库（`Kylin-Agent-Competition/kylinOS-agent-memory`）有 **KMA Canonical Business Schema v1**（跨轨统一业务字段标准）
- 数据包 gold 业务字段必须对齐 KMA，否则评测答案与真实系统行为不一致
- **两版 KMA 文档**（务必区分）：
  - 主仓库权威版（159 行，`CANDIDATE_FOR_FREEZE`，R-1..R-6 裁定）→ `evidence/source/kma_unified_data_format_FREEZE_V1/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md` = **对齐基线**
  - 旧存档版（975 行，FREEZE_PROPOSAL，KMA-DATA-SCHEMA-001 编号）→ 仅作枚举明细参考，**不作为核验依据**

### 关键裁定（Reviewer gaoyizhe，2026-09-04）
- **#1** preference_key：受控开放字符串 `prefix[:object]`（前缀沿用模板族：output_style/tool_choice/safety/app/workflow/other），Kappa 全串比对
- **#2** scope 映射：app→tool、task→topic（不机械映射，语义对照表固定）
- **#3** confidence：三档主表 high=0.95 / medium=0.70 / low=0.40（+可选中间档 0.85/0.75/0.60/0.30）
- **#4.1** checkpoints：评测层验证时点，不进业务状态
- **#4.2** 版本冲突：先后→temporal_inconsistency；同时→contradiction；版本链可消解→superseded/version
- **#4.3** retrieval D9：正解=active 当前版、superseded 旧版禁止召回、语义近似=semantic_near_miss
- **#9** preference_scope/conflict_type 来源：D3(L2) FROZEN_BUSINESS_SEMANTIC ✅
- **#10** sensitivity（R-5）：tool_result/e2e 事件层敏感样本必填（五级），检索不补，偏好可选
- **#7** KMA FROZEN：本仓库 #27 认定达成（D/E 联合授权 + 主仓库 PR#137）；**主仓库在线文档仍 CANDIDATE**（差异协调中，以本仓库认定推进 P1）

### 阶段 1/7 KMA 对齐产物
- `reports/requirement_data_mapping_v2.md`（KMA 对齐章节）
- `data/processed/schema.json`（kma_alignment + gold_enum_alignment + sensitivity）
- `scripts/convert/kma_convert.py`（P1-3 KMA 化转换，415 条 canonical 化 + 时间戳 UTC ms Z）
- `registry/kappa_agreement_fields.json`（一致字段集单一来源）
- `registry/field_mapping.json`（B 侧数据字段↔KMA 映射登记，30+68 行）

---

## 三、阶段 8 P1 工作流当前状态

### 工作流（B 侧发布 `reports/stage8_A_B_cooperation_steps.md`）
| 批次 | 内容 | 状态 |
| --- | --- | --- |
| P1-1 | Schema/enum 收口 + sensitivity(#10) | ✅ 已合（#27） |
| P1-2 | 标注手册 v2 定稿 | ✅ 已合（P1-2/3 分支） |
| P1-3 | 全量重转（KMA 化 + 时间戳 UTC ms） | ✅ B 对账通过（时间戳修正后） |
| P1-4 | labels_A/B v2 骨架 | ✅ B 生成（40 条） |
| **P1-5** | **试标 v2（A/B 独立标注 40 条）** | 🔶 **卡在母数据缺陷** |
| P1-6 | Kappa（--format kma，registry 单源） | ⬜ |
| 8.2 | 候选草稿生成（A 职责） | ⬜ 需修母数据 |
| 8.3 | 双标/裁决 | ⬜ |
| Gate8 | 收口 | ⬜ |

### 当前分支
- `feat/B-stage8-p1` = PR #28（当前，工作区干净）
- 相关分支：`feat/A-stage8-p1-2-3`（P1-2/3，已并入 PR#28 一部分）、`feat/B-stage8-kma`（#27 已合并 master）、`feat/B-stage8-p1-3-validate`

### A 侧关键产物（P1-5）
- `data/gold/annotation_guideline_v2.md`（标注手册 v2，P1 定稿版）
- `worklog/stage8_P1-5_annotation_guide_all_options.md`（全选项标注指南）
- `worklog/stage8_P1-5_labels_checklist_mc.md`（逐字段选择题核对表，40 条 35 字段全覆盖）
- `worklog/stage8_P1-5_labels_A_reference_AI.jsonl`（AI 参考版，**已 gitignore**，仅比对用）
- `data/interim/labels_A_trial_v2.jsonl`（A 手标文件，当前为空骨架待填）

---

## 四、⚠️ 关键问题：母数据模板重复缺陷（已返工）

### 问题（已量化，2026-09-04）
- 试标母数据 `gold_candidates_*.jsonl` 是 **v1.0 时代 AI 按模板批量生成**的（语义级重复 88%~93%：preference 60→6、retrieval 60→5、conflict 40→5、forgetting 40→4、e2e 15→1）
- 审计脚本：`scripts/audit/stage8_semantic_dedup.py`；证据：`evidence/audit/stage8_candidate_semantic_dedup_20260904.json`

### 已执行的返工（A 侧，2026-09-04）
1. **重建方案**：`reports/stage8_candidate_rebuild_plan.md`（真实数据接地 + 自建多样化 + 语义去重 + Gate 分工）
2. **候选池重建**：`scripts/convert/rebuild_candidates_v2.py` → `data/interim/gold_candidates_*_v2.jsonl`（77 条，5 任务，43% public_derived + 57% team_authored，全部语义去重通过）
3. **试标集重抽**：`scripts/convert/sample_trial_set_v3.py` → `data/interim/stage8_trial_set_v3.jsonl`（40 条全异）
4. **骨架**：`scripts/convert/gen_trial_v3_skeletons.py` → `labels_A/B_trial_v3.jsonl`
5. **证据报告**：`reports/stage8_candidate_rebuild_report.md`；PR#28 评论：`worklog/20260904_stage8_candidate_rebuild_PR28_comment.md`

### ⏳ 待 B/Reviewer
- B 复核：去重口径 / 候选 schema / 试标集结构 / Kappa 工具就位
- Reviewer 裁定：试标集 v2 废弃 / 来源占比 / 语言策略 / tool_result 依赖 / retrieval 版本引用
- **裁定前不量产、不正式试标（Gate 纪律）**

---

## 五、红线与约定（全程遵守）

1. **Gate 纪律**：每阶段未获 Reviewer 批准不得进入下一阶段
2. **License 先行**、**先标后产**（Kappa≥0.70 才量产）、**禁 mock**
3. **禁 mock 边界**：封存集必须麒麟 VM 真实回放；合成候选只作 candidate_only，绝不进封存
4. **A 不越权**：不代 B 做校验/Kappa/审计；不代 Reviewer 做裁定/Gate
5. **双人独立**：A/B 独立标注，不共享答案；脚本只算一致性
6. **推送目标**：origin = gaoyizhe934/...（共享仓库）；**不要自建分支推 PR，并入 B 的分支（如 PR#28）**
7. **仓库整洁**：外部参考 docx、AI 参考标签、过时旧口径文档已 gitignore

---

## 六、常用命令

```powershell
# 切换 PR#28 分支（当前 A 工作分支）
git checkout feat/B-stage8-p1

# 标注提交前校验（P1-5）
python scripts/audit/stage8_label_check_v2.py --labels data/interim/labels_A_trial_v2.jsonl --samples data/interim/stage8_trial_set_v2.jsonl

# KMA 化转换（P1-3，幂等）
python scripts/convert/kma_convert.py

# 一致字段集单源
registry/kappa_agreement_fields.json
```

---

## 七、下一步（下个会话优先）

### 首要：B 复核 + Reviewer 裁定（见 PR#28 comment）
- [ ] Reviewer 裁定重建方案 5 项（试标集 v2 废弃/来源占比/语言策略/tool_result 依赖/retrieval 版本引用）
- [ ] B 复核去重口径 + 候选 schema + 试标集 v3 结构 + Kappa 工具就位

### 裁定后：正式试标 v3
- [ ] A 手标 `labels_A_trial_v3.jsonl` 40 条（对照选择题核对表 + 全选项指南）
- [ ] 提交前跑 label_check_v2 exit 0
- [ ] B 收齐后跑 stage8_kappa --format kma ≥0.70

---

## 八、重要文件索引

| 文件 | 内容 |
| --- | --- |
| `reports/gate_status.md` | Gate 状态总表（看最新 Gate） |
| `reports/stage8_A_B_cooperation_steps.md` | P1 批次分工表 |
| `reports/stage8_v2_followup_plan.md` | P1 后续计划 |
| `reports/stage8_P1_3_conversion_report.md` | P1-3 转换对账 |
| `data/gold/annotation_guideline_v2.md` | 标注手册 v2（P1 定稿） |
| `worklog/stage8_P1-5_labels_checklist_mc.md` | 逐字段选择题核对表 |
| `worklog/20260904_KMA_FROZEN_adjudications_1_4_R.md` | Reviewer 裁定 #1-#4 |
| `registry/kappa_agreement_fields.json` | 一致字段集单一来源 |
| `evidence/source/kma_unified_data_format_FREEZE_V1/` | KMA 标准（权威版+旧版+溯源） |
