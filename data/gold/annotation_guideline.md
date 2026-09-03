# 麒麟 OS Memory Gold 标注手册 v1.1（Annotator A 起草版）

- 角色：Annotator A（lyf-1213）· 阶段 8「如何进行数据标注」
- 分支：`feat/A-stage8-annotation`
- 日期：2026-09-02
- 依据：手册第 7 章「自建麒麟 OS Memory Gold 规范」、附录 B、v2.0 重建计划五条红线、现有 `data/interim/gold_candidates_*.jsonl` 候选草稿
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

---

## 3. 知识检索（knowledge_retrieval）

### 字段（手册表 P179）

| 字段 | 规则 |
| --- | --- |
| relevant_ids | ≥1 个相关文档 id，必须可解析到知识库 |
| relevance | `{doc_id: 1..4}` 相关度分级 |
| hard_negative_ids | 词汇相似但语义不满足的文档（>0 更佳） |
| expected_answer_points | 期望答案要点（字符串数组） |

### 标注判定规则

- 每个查询至少 1 个相关文档；`relevant_ids` 必须能在知识库（`kb_*` 文档集合）解析。
- 困难负样本必须在**词汇上相似**（含同义关键词）但**语义不满足**；禁止把不相关文档当困难负样本。
- `expected_answer_points` 从检索结果/知识文档证据中提取，禁止无来源编造。
- 公开集（t2ranking 等）转换的 `hard_negative_ids`/`expected_answer_points` 为空属已知限制，需在后续知识库构建后回填（非本阶段封存标签）。

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

## 8. 试标与一致性

1. **试标规模**：A/B 各独立标 30~50 条（六类任务各若干，覆盖正/负/边界/困难样本）。
2. **禁止先讨论答案**；试标后汇总分歧并按类型聚类（任务定义/偏好-临时边界/作用域/证据不足/冲突优先级/应删应留）。
3. **Kappa 计算**（B 侧执行）：Cohen's Kappa ≥ 0.70 达标；未达标退回修订本手册并回溯重审受影响样本。
4. 修订规则后必须**回溯**受影响样本，不得只对新数据用新口径（手册 7.7）。

## 9. 双人标注与裁决

1. 正式阶段 A/B 独立提交全部样本，脚本只算一致性，不自动覆盖。
2. Reviewer 查看原始证据与两份标签，写出 `final_label` 与 `decision_reason`。
3. LLM 可作为第三意见，但**不能替代 Reviewer**；模型、Prompt、输出归档到 `evidence/ai_outputs/`。

## 10. 质量检查清单（手册表 31，标注者自检）

- [ ] 任务一致性：这条数据真的能验证目标能力吗？（普通问答≠偏好；角色设定≠动态偏好）
- [ ] 证据完整性：Gold 能从原始文本/事件直接证明？（答案正确但无证据 = 不通过）
- [ ] 边界清晰度：临时指令 vs 长期偏好 vs 知识事实区分正确？
- [ ] 冲突可判定：冲突样本有时间/来源/作用域信息且规则一致？
- [ ] 负样本可信：困难负样本确实不相关（不含同义答案）？
- [ ] 遗忘可验证：应删与应留同时明确，含残留检查？

## 11. 评审/复核命令（供 B 侧与 Reviewer）

```
# 一致性计算（B 侧执行，脚本待 B 提供）
python scripts/audit/stage8_kappa.py --a <A标签文件> --b <B标签文件>
# 样本结构/枚举校验（validate 目录，B 侧执行）
python scripts/validate/...
# 裁决产物
data/gold/gold_draft.jsonl + data/gold/disagreement_log.csv
```

---

## 附：A 侧本阶段产出范围（不越权）

| 产出 | 归属 |
| --- | --- |
| 本标注手册（v1.1 起草） | A ✅ |
| 试标标签（A 独立） | A（试标时提交） |
| Kappa 计算、一致性报告 | B |
| final_label、disagreement_log、Gate 8 批准 | Reviewer |