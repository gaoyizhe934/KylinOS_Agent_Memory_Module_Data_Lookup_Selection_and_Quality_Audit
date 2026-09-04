# KMA FROZEN 清单 #1-#4 Reviewer 裁定记录（2026-09-04，gaoyizhe）

依据：A 建议稿（worklog/20260904_KMA_FROZEN_1_3_A_recommendation.md、worklog/20260903_KMA_confidence_scope_samples_A.md）、标注手册 v2 草案、KMA 权威候选 + D3(L2)、D9 检索集。D/E 联合授权背景下以 Reviewer 身份裁定（#1-#3 与数据包标注层直接相关；#4 含 E 语义/D9 口径）。

## #1 preference_key 取值策略 → 裁定：接受"受控开放字符串"（模板族前缀 + 冒号 + 开放对象段）

- 格式：`preference_key := <prefix>[:<object>]`；前缀为受控词表（沿用旧模板族：output_style/tool_choice/safety/app/workflow/other），`object` 为开放短标识（小写 snake_case，≤32 字符，可空）。
- 理由：不造第二套枚举（KMA §7）、可解释（key=匹配键、value=完整值）、可控（前缀词表固定；开放段限长/字符集）。
- Kappa：按 `preference_key` 全串精确比对（B stage8_kappa 字段集含它）。
- 落点：固定入 annotation_guideline_v2 §3 preference_key 规则。

## #2 旧 scope app/task 语义落点 → 裁定：语义映射固定对照表（不机械映射）

| 旧 scope | 语义 | KMA preference_scope | 样例 |
| --- | --- | --- | --- |
| app | 针对具体工具/应用的行为 | `tool` | "项目管理工具里用中文标签"→tool |
| app | 麒麟 OS 助手作为系统整体 | `global` | "以后都先问我确认"→global |
| task | 针对某类工作主题 | `topic` | "做周报时用简洁要点"→topic |
| task | 针对工具行为的任务 | `tool` | "发邮件时带签名 X"→tool |
| session | 仅本次会话 | `session` | "这次用英文回复"→session |
| global | 全局习惯 | `global` | 一致 |
| — | 时间窗 | `time_window` | "会议期间勿扰"→time_window |

- 原则：先判"是否系统整体(global)/是否仅本次(session)/是否时间窗(time_window)"，再按"具体工具→tool、工作主题→topic"细分。
- 落点：固定入 annotation_guideline_v2 §5 preference_scope 对照表。

## #3 confidence 换算 → 裁定：三档主表 + 受控中间档

- 主表固定：high=0.95 / medium=0.70 / low=0.40（默认只用三档，保 A/B 一致）。
- 中间档（可选，仅当手册 v2 明示档位表时使用）：显式有歧义=0.85、两次一致行为=0.75、单次行为=0.60、极弱=0.30~0.40；不列入手册则不使用。
- 换算只在标注/转换映射层进行；`gold.confidence_score` 直接写数值。
- 落点：固定入 annotation_guideline_v2 §5 confidence_score 档位表。

## #4 遗留裁定项 → 裁定

### 4.1 forgetting checkpoints 定位 → 裁定：保留为评测层验证时点，不进业务状态
- `checkpoints`（immediate_query/after_restart/after_full_reindex）是**评测验证手段**（删除后何时查残留），非业务记忆状态；业务状态用 `ForgetPlan.status`/`memory_status` 表达。gold 中 checkpoints 留在评测层字段，不写入 canonical 业务状态。
- 落点：annotation_guideline_v2 §7 明确"checkpoints=评测层验证时点"。

### 4.2 版本冲突 conflict_type 判定 → 裁定
- 时间先后更新（新覆盖旧，明确先后）→ `temporal_inconsistency`；
- 同层矛盾（不可同时为真，需裁决取舍）→ `contradiction`；
- 业务表达优先用版本/生命周期（superseded + version_id），评测 conflict 标签用于"需在两条冲突信息间裁决"的样本；
- 口诀：先后更新→temporal_inconsistency；同时矛盾→contradiction；能由版本链消解的→用 superseded/version 表达。

### 4.3 retrieval 版本引用（D9 口径）→ 裁定：采用 D9
- 正解 = 同用户 active 当前版本（memory_id+version_id 版本级引用）；
- superseded 旧版（非当前）→ forbidden（禁止召回）；
- 语义近似当前版 → semantic_near_miss（不计 guardrail violation）；
- evaluation_role = positive_retrieval / negative_guardrail；每条带 rationale。

---
签署：Reviewer（gaoyizhe），D/E 联合授权背景下，2026-09-04。


---

## 补充裁定 #10（R-5 sensitivity 收口，2026-09-04，gaoyizhe）

- 问题：A 复核发现权威版 R-5（canonical 用 `sensitivity`，sensitivity_level 仅注解层 alias）在本仓库 gold_enum_alignment/手册 v2 未体现。
- 裁定：**评测 gold 补 `sensitivity` 字段（对齐 canonical R-5）**：
  1. **tool_result / end_to_end_session（事件层）**：凡涉及敏感内容判定的样本，`gold.sensitivity` 必填（取值 KMA Sensitivity 枚举）；不涉及敏感判定的样本可空（不强制）；
  2. **knowledge_retrieval**：不补（D9 检索集无敏感字段，正确）；
  3. **preference_extraction**：敏感"不存储"决策沿用 `should_store=false + memory_status=candidate + safety` 表达；R-5 的 `sensitivity` 是事件/记忆条目的敏感级别标注，与"不存储敏感"决策互补（偏好样本如涉及敏感内容可标 sensitivity，非强制）；
  4. 落点：schema.json gold_enum_alignment（tool_result/e2e 补 sensitivity + Sensitivity 枚举）、annotation_guideline_v2 §5/§6 补规则、enum_dictionary 补词表——**P1-1 收口执行**。
- 依据：主仓库权威候选 R-5（CANDIDATE_FOR_FREEZE）§5.6 Sensitivity。
