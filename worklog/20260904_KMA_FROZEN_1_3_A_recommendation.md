# KMA FROZEN 清单 #1/#3 A 侧定稿建议（Annotator A）— 2026-09-04

- 角色：Annotator A（lyf-1213）
- 分支：`feat/B-stage8-kma`（PR #27）
- 目的：响应 FROZEN 必办清单 #1（preference_key 取值策略）、#3（confidence 换算口径）——责任"A/B 定稿"，A 出建议稿，B 复核后交 Reviewer 裁定。
- 性质：建议稿，非最终裁定。

---

## 一、清单 #1：preference_key 取值策略

### 问题
旧 `preference_type`（output_style/tool_choice/safety/app/workflow/other）是枚举；KMA `preference_key` 为开放字符串。需定取值策略，避免（a）再造第二套枚举（KMA §7 禁止）；（b）标注自由发挥导致 Kappa 下降。

### A 建议：受控开放字符串 = 模板族 + 冒号 + 短标识

```
preference_key := <template_family>[:<object>]
```

- `<template_family>` 沿用现有模板族命名（`output_style`/`tool_choice`/`safety`/`app`/`workflow`/`other`），**作为受控前缀**而非枚举值；
- `<object>` 为可选开放短标识，描述具体对象（如 `report`/`delete_confirm`/`project_mgmt_lang`）；
- 示例：`output_style:report`、`tool_choice:delete_confirm`、`app:project_mgmt_lang`。

### 理由
1. **不再造枚举**：前缀是分类标签，不替代 KMA 的 `knowledge_type`/`expression_type`；
2. **可解释**：`preference_value` 是完整值，`preference_key` 是检索/匹配键；
3. **可控**：前缀词表固定（可作 enum_dictionary 受控前缀），开放段限制长度与字符集，Kappa 按 `prefix:object` 整体比对或按前缀比对（裁定点）。

### 规则草案
| 项 | 建议 |
| --- | --- |
| 前缀词表 | `output_style/tool_choice/safety/app/workflow/other`（与旧模板族对齐，免迁移） |
| 开放段 | 小写 snake_case，≤32 字符 |
| Kappa 一致判定 | 按 `preference_key` 全串精确比对（B 侧 stage8_kappa 字段集含它） |
| 模板族对应 | `template_family` 与 `preference_key` 前缀保持一致（标注自查项） |

---

## 二、清单 #3：confidence 换算口径

### 问题
旧 `confidence` 为 high/medium/low；KMA `confidence_score` 为 float [0,1]。需固定换算避免方差。

### A 建议：三档主表 + 两中间档（可选）

| 旧值 | 语义 | confidence_score（主） | 可选中间档 |
| --- | --- | --- | --- |
| high | 显式、无需推断 | 0.95 | 0.85（显式但有歧义） |
| medium | 多句/行为推断 | 0.70 | 0.75（两次一致行为） |
| low | 模糊、低证据 | 0.40 | 0.60（单次行为） |

### 规则
1. **主表固定**（0.95/0.70/0.40）：默认只用三档，保证 A/B 一致性；
2. 中间档**仅在标注手册明确列出时使用**，防自由发挥；
3. 换算只在转换/标注映射层进行，`gold.confidence_score` 直接写数值。

---

## 三、待 B 复核 / Reviewer 裁定

- [ ] B 复核两建议是否与 `registry/kappa_agreement_fields.json`、`annotation_guideline_v2.md` 兼容；
- [ ] Reviewer 裁定 #1 preference_key 前缀词表是否沿用旧模板族；#3 是否接受三档主表。

## 四、A 不越权
- 本文为建议稿，未改手册/schema/labels/脚本；裁定归 Reviewer。
