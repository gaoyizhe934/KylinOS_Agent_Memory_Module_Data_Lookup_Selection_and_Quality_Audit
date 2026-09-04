# 阶段8 P1-3 全量重转对账报告（Annotator A）— 2026-09-04

- 角色：Annotator A（lyf-1213）· P1-3 批次
- 分支：`feat/A-stage8-p1-2-3`
- 目的：KMA 化全量重转 processed（raw/interim → processed），禁 mock；附对账。

## 一、转换内容

脚本：`scripts/convert/kma_convert.py`（新增，P1-3 KMA 化执行层）

将 processed 的 gold 旧字段映射到 KMA canonical 字段（依据手册 v2 定稿 + Reviewer 裁定 #1-#4/#10）：

| 任务 | 旧 → 新（canonical） |
| --- | --- |
| preference_extraction | preference_type→preference_key(+expression_type)；scope→preference_scope（#2 对照表 app→tool）；confidence→confidence_score（#3 三档）；should_store→should_persist+is_temporary；operation→version+memory_status |
| knowledge_retrieval | 保留 relevant_ids/hard_negative/answer_points + 增 knowledge_type/evaluation_role/memory_status（version_refs 待 KB） |
| conflict_resolution | conflict_type 旧值→KMA 枚举（#4.2：time_update→temporal_inconsistency 等）；winner→resolution_status；keep/remove→left/right_knowledge_id |
| precise_forgetting | target_ids→target_type+resolved_target_ids+forget_mode；checkpoints 保留评测层；must_keep 保留 |
| tool_result | status→source_business_status；+sensitivity(#10)/tool_call_id 占位 |
| end_to_end_session | expected_memory/response 保留 + memory_status/memory_type/sensitivity(#10) |

**无损**：旧字段保留在 `gold.legacy`（不删）；**禁 mock**：仅字段/枚举映射，不改原文与证据。

## 二、对账结果

| 指标 | 值 |
| --- | --- |
| 总行数 | 715 |
| 六类任务映射（fixed） | 415 |
| auxiliary_dialogue（skip，非六类） | 300 |
| 幂等性 | ✅ 重复运行 SHA256 一致（已修复：gold 已 canonical 则跳过） |
| 旧字段保留 | ✅ gold.legacy |

## 三、验证命令

```
python scripts/convert/kma_convert.py        # 转换（幂等，exit 0）
python scripts/convert/kma_convert.py        # 再跑 → already=415，SHA 一致
# schema 校验 / schema_drift_check（B 侧执行）
```

## 四、诚实披露

1. **convert_to_schema.py（旧脚本）与 kma_convert.py 冲突**：两者都写 data/processed/*.jsonl。P1-3 后 **canonical 为金标准**，`convert_to_schema.py` 仅用于生成（会还原旧格式）；建议 B 侧校验以 canonical 为准，或后续将 convert_to_schema 的 KMA 映射层替换为 kma_convert。
2. **tool_result 无样本**（阶段7 移除残留后为 0）：映射函数就绪，待阶段8.2 生成 tool gold 后应用。
3. **version_refs（D9 memory_id+version_id）待 KB**：检索 canonical 的版本级引用字段留空，KB/D9 就绪后回填（FROZEN 清单 #7）。
4. **sensitivity 当前候选均为 null**：现有候选非敏感，符合 #10"敏感样本必填、非敏感可空"。
5. **auxiliary_dialogue 300 条不参与**（非六类，手册 §7.1 不金标）。

## 五、交付物
- `scripts/convert/kma_convert.py`（P1-3 KMA 化转换）
- `data/processed/*.jsonl`（canonical 化）
- 本对账报告

## 六、待 B/Reviewer
- B 侧对账复核（条数/枚举/时间 UTC/raw_id/幂等）+ schema_drift_check exit 0
- Reviewer 放行 P1-4（labels 骨架）
