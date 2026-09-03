# 麒麟 OS Memory Gold 标注手册 v1.2（Annotator A 起草版，B 审阅 P1/P2 闭环）

- 角色：Annotator A（lyf-1213）· 阶段 8「如何进行数据标注」
- 分支：`feat/A-stage8-annotation`
- 日期：2026-09-02（v1.1 起草）；2026-09-03（v1.2 按 B 审阅 P1×3/P2×5 修订）
- 依据：手册第 7 章「自建麒麟 OS Memory Gold 规范」、附录 B、v2.0 重建计划五条红线、现有 `data/interim/gold_candidates_*.jsonl` 候选草稿、B 审阅意见 `worklog/20260903_stage8_B_review_PR24.md`
- 说明：本文为 A 侧起草的**标注执行手册**，说明六类任务各自的标注字段、判定规则、证据要求与质量检查。**试标结果/Kappa/裁决由 B 与 Reviewer 完成**，A 不越权。

---

## 0. 总原则（红线）

1. **标签必须能从 input/evidence 直接推导**，禁止无证据猜测、禁止按模型输出反推。
2. **禁 mock**：任何层级不得包含模拟/合成伪装的真实数据；端到端与 Tool Result 封存集必须来自麒麟 VM 真实回放（阶段 10）。
3. **先标后产**：先做 30~50 条试标，Kappa ≥ 0.70 后才允许规模化标注；未达标退回修订本手册。
4. **双人独立**：A/B 独立标注、不共享答案；脚本只算一致性，不自动覆盖；Reviewer 裁决分歧并写 `final_label`。
5. **证据可溯源**：每条 gold 必须有 `evidence[].source_event_id` 与 `span`；`review_status` 默认 `candidate_only`，批准后才可进入封存。

---

## 1. 统一样本骨架（六类任务通用）

```json
{
  "sample_id": "pref_000001",
  "dataset_version": "kylin_memory_gold_v1.0",
  "task_type": "preference_extraction",
  "language": "zh-CN",
  "user_id": "u_synthetic_001",
  "conversation_id": "conv_0001",
  "timestamp": "2026-07-20T10:00:00+08:00",
  "input": {},
  "gold": {},
  "evidence": [{"source_event_id": "evt_001", "span": "..."}],
  "source": "team_authored",
  "template_family": "output_style_length_v1",
  "annotator_a": "A",
  "annotator_b": "B",
  "review_status": "candidate_only"
}
```

- `sample_id` 前缀：`pref_` / `retr_` / `conf_` / `forg_` / `tool_` / `e2e_`。
- `timestamp` 必须 ISO-8601 合法（如 `2026-07-20T10:00:00+08:00`），禁止 `2026-07-202T…` 类非法格式。
- `annotator_a` / `annotator_b` 在双人标注后填写本人代号；`review_status` 由 Reviewer 最终裁决。

### 1.1 evidence 结构示例与溯源路径（P2-4）

统一结构：
```json
"evidence": [
  {"source_event_id": "evt_001", "span": "以后项目周报用简洁要点", "source_type": "utterance"},
  {"source_event_id": "raw_t2r_0", "span": "qid=0", "source_type": "raw_record"}
]
```

两条溯源路径：
- **team_authored**：`source_event_id=evt_*`（对话事件编号），`span` 抄用户原话片段，`source_type=utterance`。
- **public_derived**：`source_event_id=<raw_id>`（如 t2ranking `qid` / multiwoz `dialogue_id`），`span` 写 `qid=<id>` 或 `dialogue_id=<id>`，`source_type=raw_record`；必须能从 `raw_id` 反查 `data/raw/` 原始文件。
- 判定规则不变：**span 必须指向可验证的原始内容**，禁止无来源编造。

---

## 2. 偏好提取（preference_extraction）

### 字段与枚举（手册表 34）

| 字段 | 枚举/规则 |
| --- | --- |
| preference_type | `output_style` / `tool_choice` / `safety` / `app` / `workflow` / `other`（新增需 Reviewer 批准） |
| value | 可执行、可比较；禁止只写"喜欢这样" |
| scope | `global` / `app` / `task` / `session`（"这次""当前文件"通常不是 global） |
| confidence | `high` / `medium` / `low`（基于证据强度，不由模型概率决定） |
| should_store | `true/false`（临时指令、闲聊、推测、敏感内容通常为 false） |
| operation | `create` / `update` / `revoke` / `no_op`（update/revoke 必须带旧值） |

### 标注判定规则

- **显式偏好**：用户明确"以后都这样" → `should_store=true`, `confidence=high`。
- **隐式重复行为**：≥2 次一致行为可推断 → `confidence=medium/high`，evidence 需覆盖多次事件。
- **单次临时要求**："这次/仅本次" → `should_store=false`, `scope=session` 或 `no_op`。
- **相互矛盾表达**：先"要详细"后"要简短" → 新偏好 `operation=update`（记录 old_value），旧偏好保留可回溯。
- **撤销偏好**："之前的不要了" → `operation=revoke`。
- **作用域**：仅某应用生效 → `scope=app`；全局 → `scope=global`。
- **敏感内容**：密码/支付/凭证等 → `should_store=false`, 属 safety。
- **边界**：普通问答/闲聊 ≠ 长期偏好；角色设定 ≠ 动态偏好（手册表 31）。
- **与冲突处理的边界（P2-5）**：同一偏好"先详细→后简短"且能明确判定新旧版本、单条偏好线内演化 → 标 `preference_extraction`（`operation=update/revoke`，保留 old_value 可回溯）；**只有**当矛盾涉及多对象取舍（保留哪个/移除哪个）、或需按来源/作用域/版本/安全策略裁决 → 标 `conflict_resolution`。分流口诀：**一条偏好自己变了 → preference；两条以上要选边 → conflict**。

---

## 3. 知识检索（knowledge_retrieval）

### 字段（手册表 P179）

| 字段 | 规则 |
| --- | --- |
| relevant_ids | **≥1 个相关文档 id（硬性）**，必须可解析到知识库 |
| relevance | `{doc_id: 1..4}` 相关度分级 |
| hard_negative_ids | **≥1 个困难负样本 id（硬性，P1-1）**；词汇相似但语义不满足 |
| expected_answer_points | 期望答案要点（字符串数组） |

### 标注判定规则

- 每个查询至少 1 个相关文档；`relevant_ids` 必须能在知识库（`kb_*` 文档集合）解析。
- **困难负样本为硬性要求**：每个查询必须标注 **≥1 个** `hard_negative_ids`，以支撑 Recall@K / 困难负样本指标（B 侧 Kappa 与校验以该字段非空为合格线）。困难负样本必须在**词汇上相似**（含同义关键词）但**语义不满足**；禁止把完全不相关文档当困难负样本。
- `expected_answer_points` 从检索结果/知识文档证据中提取，禁止无来源编造。
- **公开集回填规则（保留）**：公开集（t2ranking 等）转换的 `hard_negative_ids`/`expected_answer_points` 为空属已知限制，需在后续知识库构建后回填；该部分样本以 `review_status=candidate_only` 标记，**不进入本阶段封存**，不计入 Kappa 合格线。

---

## 4. 冲突处理（conflict_resolution）

### 字段

| 字段 | 规则 |
| --- | --- |
| conflict_type | `time_update` / `scope` / `source_conflict` / `knowledge_version` / `safety` |
| winner | `keep_new` / `app_priority` / `explicit_wins` / `version_selected` / `safety_priority` 等 |
| resolution_reason | 写明依据（时间/作用域/来源/版本/安全） |
| keep_ids / remove_ids | 保留与移除的对象 id，均须可解析 |

### 判定规则（手册表 35）

| 冲突类型 | Gold 决策依据 |
| --- | --- |
| 时间更新 | 新显式、同作用域、时间更晚 → 新胜；旧版本保留可回溯 |
| 作用域冲突 | 应用级在该应用内优先；全局不被删除 |
| 来源冲突 | 显式配置通常优先于行为推断；规则须固定 |
| 知识版本 | 按系统版本、有效期、可信来源选择 |
| 安全冲突 | 安全策略优先，记录拒绝/降级 |

- 禁止"无时间/来源/作用域信息却决定新旧"（手册表 31 冲突可判定检查）。
- **与偏好提取的边界（P2-5）**：见 §2 分流口诀——单条偏好演化用 preference（update/revoke），多对象取舍或需来源/作用域/版本/安全裁决才用 conflict。

---

## 5. 精准遗忘（precise_forgetting）

### 字段（手册表 P185）

| 字段 | 规则 |
| --- | --- |
| target_ids | 应删除对象 id |
| expected_deleted | 与 target_ids 一致 |
| must_keep | 不应误删的对象 id（必须同时给） |
| checkpoints | `immediate_query` / `after_restart` / `after_full_reindex` |
| expected_residual_count | 残留数（通常 0） |

### 判定规则

- **删对 + 不误删**：target 必须删、must_keep 必须留；两者同时明确（手册表 31 遗忘可验证）。
- 所有样本至少含一次即时查询；关键样本含重启与全量重建后的残留检查。
- `expected_residual_count`：目标删除后期望残留 = 0；误删保护对象不得列入 expected_deleted。

---

## 6. Tool Result（tool_result）

### 字段（手册表 36）

| 字段 | 枚举/规则 |
| --- | --- |
| status | `success` / `failed` / `cancelled` / `timeout` / `partial_success` |
| persist_policy | `yes` / `no`（是否沉淀为可复用知识） |
| side_effect | 副作用记录 |
| failure_reason | 失败原因（failed 时必填） |

### 判定规则

| status | 记忆处理 |
| --- | --- |
| success | 视副作用与业务价值决定是否沉淀；敏感结果先过滤 |
| failed | 可沉淀失败原因与已验证排查步骤，**不得把失败写成成功** |
| cancelled | 记录用户取消与未执行，禁止推断副作用已发生 |
| timeout | 标记未知状态，必要时触发状态核验 |
| partial_success | 拆分成功/失败部分，**不能整体标记成功** |

- **红线**：端到端与 Tool Result 封存集必须来自麒麟 VM 真实回放，禁 mock。

---

## 7. 端到端会话（end_to_end_session）

### 字段

| 字段 | 规则 |
| --- | --- |
| expected_memory | 期望沉淀的记忆（可含 version/status） |
| expected_response | 期望的系统回复 |

### 判定规则

- 覆盖跨会话复用、冲突、工具、遗忘、重启恢复等场景。
- `expected_memory`/`expected_response` 必须能从会话事件链证据推导。
- 封存集必须来自麒麟 VM 真实回放（阶段 10），禁 mock。

---

## 7.1 auxiliary_dialogue 语料处置（P2-6）

`data/processed/multiwoz_dialogues_sample.jsonl`（200 条）+ `multiwoz_public_sample.jsonl`（100 条）为 `auxiliary_dialogue`（public_derived）。

- **处置**：该批语料**不做六类任务的金标标注**，仅作为：
  1. 偏好/冲突样本的**任务型对话场景来源**（抽取有效片段）；
  2. 检索的**负面/干扰语料来源**；
  3. 语言多样性对照（en）。
- **标签**：保留 `gold.goals/services` 原值，`review_status=candidate_only`；不参与 Kappa 一致性计算，不进封存。
- **转换产物**：由 `convert_to_schema.py` 生成，阶段 8 无需重新人工标注。

---

## 8. 试标与一致性

1. **试标规模**：A/B 各独立标 30~50 条（六类任务各若干，覆盖正/负/边界/困难样本）。
2. **禁止先讨论答案**；试标后汇总分歧并按类型聚类（任务定义/偏好-临时边界/作用域/证据不足/冲突优先级/应删应留）。
3. **Kappa 一致性口径（P1-2，B 侧 `stage8_kappa.py` 按此落地）**：
   - **统计维度**：同时输出 **总体 Cohen's Kappa** 与 **每任务分层 Cohen's Kappa**（preference/retrieval/conflict/forgetting/tool/e2e 各算一个）。
   - **一致判定字段集**：以每类任务的 **gold 主字段集** 判定一致——偏好取 `preference_type+scope+should_store+operation`（value 允许语义等价，单独标记不一致但不算整体不一致）；检索取 `relevant_ids+hard_negative_ids`（集合相等）；冲突取 `conflict_type+winner`；遗忘取 `expected_deleted+must_keep`（集合相等）；Tool 取 `status+persist_policy`；端到端取 `expected_response` 语义等价。
   - **达标线**：总体 Kappa ≥ 0.70 为进入量产的唯一门槛；单任务 < 0.70 时对应任务批次退回修订并回溯，不阻塞其他任务。
   - **A/B 标签文件约定**：均输出 JSONL，字段为 `sample_id, task_type, gold, evidence`；文件列名固定 `sample_id` / `task_type` / `gold` / `evidence`；A 侧文件名 `labels_A_trial.jsonl`，B 侧 `labels_B_trial.jsonl`；`gold` 为 JSON 对象，`evidence` 为数组。
4. 修订规则后必须**回溯**受影响样本，不得只对新数据用新口径（手册 7.7）。

## 8.1 试标语料口径（禁 mock 澄清，P1-3）

- 试标阶段可先用**受控场景文本**（`source=team_authored`、`review_status=candidate_only`）跑通标注口径，**仅限试标阶段验证规则，绝不进入封存**。
- 该口径不构成对红线「禁 mock / 任何层级不得包含模拟或合成伪装的真实数据」的例外：**封存集**（sealed_test 与 Tool Result/端到端正式标签）必须来自麒麟 VM 真实回放，试标候选一律 `candidate_only`，不得升级为 approved。

## 9. 双人标注与裁决

1. 正式阶段 A/B 独立提交全部样本，脚本只算一致性，不自动覆盖。
2. Reviewer 查看原始证据与两份标签，写出 `final_label` 与 `decision_reason`。
3. LLM 可作为第三意见，但**不能替代 Reviewer**；模型、Prompt、输出归档到 `evidence/ai_outputs/`。
4. **裁决产物列结构（P2-7）**：
   - `disagreement_log.csv` 列：`sample_id, task_type, field, disagreement_type, label_a, label_b, reviewer_decision, final_label, decision_reason, status`。
   - `gold_draft.jsonl`：完整样本对象（统一骨架），`gold` 为 Reviewer 裁决后的 `final_label`，`review_status=approved`（裁决通过）或 `rejected`（裁决剔除）。

## 10. 质量检查清单（手册表 31，标注者自检）

- [ ] 任务一致性：这条数据真的能验证目标能力吗？（普通问答≠偏好；角色设定≠动态偏好）
- [ ] 证据完整性：Gold 能从原始文本/事件直接证明？（答案正确但无证据 = 不通过）
- [ ] 边界清晰度：临时指令 vs 长期偏好 vs 知识事实区分正确？
- [ ] 冲突可判定：冲突样本有时间/来源/作用域信息且规则一致？
- [ ] 负样本可信：困难负样本确实不相关（不含同义答案）？
- [ ] 遗忘可验证：应删与应留同时明确，含残留检查？

## 11. 评审/复核命令（供 B 侧与 Reviewer）

```
# 一致性计算（B 侧执行）
python scripts/audit/stage8_kappa.py --a <A标签文件> --b <B标签文件>
# 样本结构/枚举校验（validate 目录，B 侧执行）
python scripts/validate/...
# 枚举字典一致性校验（P2-8）：候选草稿生成后与 data/processed/enum_dictionary.json 比对，
# 确保 preference_type/conflict_type/status/scope/operation 等取值不越出既有词表
python scripts/validate/stage7_enum_check.py --gold <gold_draft> --enum data/processed/enum_dictionary.json
# 裁决产物
data/gold/gold_draft.jsonl + data/gold/disagreement_log.csv
```

---

## 附：A 侧本阶段产出范围（不越权）

| 产出 | 归属 |
| --- | --- |
| 本标注手册（v1.1 起草 → v1.2 修订，P1/P2 闭环） | A ✅ |
| 试标标签（A 独立） | A（试标时提交） |
| Kappa 计算、一致性报告、enum 校验 | B |
| final_label、disagreement_log、Gate 8 批准 | Reviewer |
