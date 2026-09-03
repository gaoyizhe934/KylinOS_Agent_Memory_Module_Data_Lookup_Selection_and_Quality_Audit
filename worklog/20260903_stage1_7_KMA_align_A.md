# 阶段1/7 KMA 统一格式对齐（Annotator A）— 2026-09-03

- 角色：Annotator A（lyf-1213）
- 分支：`feat/A-schema-kma-align`
- 依据：`KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md`（KMA-DATA-SCHEMA-001 v1.0，FREEZE_PROPOSAL）、`D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl`（B 轨 PR#88 检索集）

## 一、背景

KMA 冻结规范定义跨轨统一业务字段（Preference/Knowledge/Conflict/ForgetPlan/MemorySourceEvent）。数据包评测样本层 KMA 不冻结，但 **gold 业务字段必须对齐 KMA**。经差异分析：偏好/冲突/遗忘/Tool 的枚举、字段名、生命周期、时间、ID 均与 KMA 存在结构性差异。

## 二、本 PR 改动（阶段1 + 阶段7）

### 阶段1：`reports/requirement_data_mapping_v2.md`
- 新增「三、KMA 统一格式对齐」章节：六项指标 gold 字段 → KMA canonical 映射表（含新旧枚举对照、生命周期/用户隔离/时间/ID 规则）。
- 原「三~五」章节顺延为「四~六」。

### 阶段7：`data/processed/schema.json`
- 新增 `kma_alignment` 块（引用/状态/生命周期真值/用户隔离/时间/ID 规则）。
- 新增 `gold_enum_alignment` 块：六类任务 gold 对齐 KMA 枚举（preference_scope、expression_type、knowledge_type、conflict_type、resolution_status、source_business_status、forget_mode、memory_status 等）。
- `field_rules.review_status` 补充说明：仅评测标签审阅状态，不表达业务生命周期。

### 阶段7：`scripts/convert/convert_to_schema.py`
- 新增 `KMA_ENUMS`（KMA 冻结枚举词表）。
- 新增 `KMA_LEGACY_MAP`（旧字段 → KMA 映射参考）。
- 新增 `kma_audit_processed()` + 主流程输出 KMA 审计（当前 420 处旧字段命中：preference 300 / conflict 80 / forgetting 40 / tool 0）。

## 三、对齐结论（诚实披露）

1. **KMA 状态 FREEZE_PROPOSAL（未 FROZEN）**：本 PR 为**参考/定义层对齐**，未破坏性重转 processed 数据。全量重转 gold 字段待 KMA FROZEN 后执行（避免破坏进行中的阶段8试标）。
2. **processed JSONL 未被改动**（转换脚本幂等，仅 enum_dictionary 的 generated_at 时间戳变化）。
3. **阶段8 标注手册/速查表/骨架仍用旧枚举**：需在 KMA FROZEN 后同步重写（当前 `data/gold/annotation_quickref.md` 已按 D9 检索集补充了检索部分，偏好/冲突/Tool 部分仍为旧枚举）。
4. **D9 检索集已对齐 KMA**：其 `knowledge_type/guardrail_category/memory_id+version_id` 与 KMA 一致，作为检索标注新标准。

## 四、遗留/待办

- [ ] KMA FROZEN 后：重写阶段8标注手册枚举 + labels 骨架 → 重新转换 processed gold 字段。
- [ ] `review_status` 与 `memory_status` 职责分离确认（评测层 vs 业务层）。
- [ ] 与 B 协调 processed 重转时间点（避免与试标/Kappa 冲突）。

## 五、验证

```
python scripts/convert/convert_to_schema.py   # exit 0；kma_audit 输出 420 处旧字段命中
```