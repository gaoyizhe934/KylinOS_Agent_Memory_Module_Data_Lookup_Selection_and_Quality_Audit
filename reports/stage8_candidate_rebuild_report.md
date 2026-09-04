# 阶段8 候选池重建证据报告（A = lyf-1213，2026-09-04）

> 对应：`reports/stage8_candidate_rebuild_plan.md`（重建方案）；PR#28 提请 B 复核 + Reviewer 裁定。
> 性质：A 侧产出（候选重建 + 试标重抽 + 去重证据），不代 B 做校验/审计、不代 Reviewer 裁定。

---

## 一、缺陷量化证据（语义去重审计）

脚本：`scripts/audit/stage8_semantic_dedup.py`（对 input 语义主字段归一化 hash；剥离计数器噪音）
证据文件：`evidence/audit/stage8_candidate_semantic_dedup_20260904.json`

### 1.1 v1.0 候选母体（gold_candidates_v1）

| 任务 | 总量 | 语义唯一 input | 重复组 | 重复率 |
| --- | --- | --- | --- | --- |
| conflict_resolution | 40 | 5 | 5×8 | 88% |
| end_to_end_session | 15 | 1 | 1×15 | 93% |
| knowledge_retrieval | 60 | 5 | 5×12 | 92% |
| precise_forgetting | 40 | 4 | 4×10 | 90% |
| preference_extraction | 60 | 6 | 6×10 | 90% |

> 说明：preference 的 `context: 第 N 次会话上下文` 计数器被归一化剥离后，60 条只剩 6 个语义；e2e 的 `version: v1.1..v1.15` 剥离后只剩 1 个语义。字符串哈希会因计数器差异显示"唯一"，但**语义全同**。

### 1.2 processed 全量（同源缺陷传导）

processed 中 team_authored 五类同样 88%~93% 重复；**真实下载数据无此问题**：
- `knowledge_retrieval_t2ranking.jsonl`: 200 条 / unique 200 ✅
- `multiwoz_public_sample.jsonl`: 100 条 / unique 100 ✅
- `multiwoz_dialogues_sample.jsonl`: 193 条被判重为 auxiliary 元数据口径（input 仅含 dialogue_id/services/n_turns 元数据，非语义重复；判定为**辅助对话元数据**，非本审计目标，不视为缺陷）

### 1.3 结论

v1.0 模板母体不可作权威数据种子：试标 Kappa 必然虚高、量产无法靠模板复制。判定为红线「数据质量硬校验 + 禁 mock」违规残留。

---

## 二、候选池重建（A 侧产出）

脚本：`scripts/convert/rebuild_candidates_v2.py`（真实数据接地 + 自建多样化）
产出：`data/interim/gold_candidates_{task}_v2.jsonl`（新文件，不覆盖 v1 母体）

### 2.1 各任务来源构成

| 任务 | 总数 | public_derived 真实数据 | team_authored 自建 OS 场景 |
| --- | --- | --- | --- |
| preference_extraction | 20 | 6 longmemeval 偏好句 + 4 multiwoz 用户句 | 10（截图/删除确认/邮件语言/终端 shell/通知/壁纸/备份/下载目录/更新/演示） |
| knowledge_retrieval | 20 | 12 t2ranking 真实 query | 8（workflow/case/template/failure/fact/constraint） |
| conflict_resolution | 11 | 5 longmemeval 真实事件链 | 6（作用域/时间更新/来源/知识版本/安全/语言） |
| precise_forgetting | 14 | 6 longmemeval 真实记忆条目 | 8（single_item/time_window/topic/session） |
| end_to_end_session | 12 | 6 longmemeval_v2 真实任务链 | 6（发布/入职/远程/演示/磁盘/更新） |
| **合计** | **77** | **33（43%）** | **44（57%）** |

### 2.2 多样化与溯源
- 全部语义去重通过：77 条 unique_input=77，dup_groups=0 ✅
- public_derived 均带 `raw_id/source_file/source_version` 溯源 ✅
- 模板族 21 个（vs v1 仅 6 个），覆盖 KMA preference_key 前缀族（output_style/tool_choice/app/workflow/safety/other）✅
- 语言：真实数据英文保留原文（candidate_only），OS 场景中文 ✅

---

## 三、试标集 v3 重抽（A 侧产出）

脚本：`scripts/convert/sample_trial_set_v3.py`
产出：`data/interim/stage8_trial_set_v3.jsonl`（40 条，5 任务 × 8）
骨架：`data/interim/labels_A/B_trial_v3.jsonl`（KMA canonical 字段，留空待标注）

### 3.1 试标集构成
- 总数 40，语义全异（sample_id 唯一 + 回源候选池 dedup CLEAN）✅
- source 分布：public_derived 21 / team_authored 19
- 模板族 21 个全覆盖，无"模板×计数器"复制

### 3.2 与 v2 试标集对比

| 维度 | v2（缺陷） | v3（重建） |
| --- | --- | --- |
| 语义唯一 input | 40 条中大量重复（conf 3 对同文 / forg 5 条同文） | 40 条全异 ✅ |
| 数据来源 | 全 team_authored 模板 | 21 public_derived + 19 team_authored ✅ |
| Kappa 意义 | 虚高（假达标） | 真实可判定 ✅ |

---

## 四、待复核/裁定（不越权）

1. **试标集 v2 处置**：建议废弃（语义重复样本无权威价值）；请 Reviewer 裁定
2. **来源占比**：当前 43% 公开数据 / 57% 自建；请 Reviewer 确认是否需提高公开数据占比
3. **语言策略**：真实数据英文原文保留 + OS 中文自建；转写有语义漂移风险，建议保留原文
4. **tool_result**：本轮不产试标候选（红线：封存集必须麒麟 VM 真实回放），登记阶段 10 依赖
5. **retrieval 版本引用**：KB/D9 就绪前，v3 试标检索字段按标注手册 §4 风险注执行（NOT production 标记）

---

## 五、下一步（待裁定后）

- Reviewer 裁定重建方案 → A 进入正式标注（labels_A_trial_v3）
- B 独立标注 labels_B_trial_v3 → stage8_kappa --format kma ≥0.70
- 达标 → 8.2 按此多样化方法量产（目标 400~500）