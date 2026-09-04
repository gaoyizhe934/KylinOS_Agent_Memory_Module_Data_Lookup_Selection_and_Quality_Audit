# P1（#31）Reviewer 路线裁定执行报告（B = DGXD01，2026-09-04）

> 响应：Reviewer 对 PR #31 的 CHANGES_REQUESTED 路线裁定（2026-09-04 14:33）。
> 范围：High-2 数据真实性处理、High-3 未泄露重抽、Medium-1 context、Medium-2 表述；High-4 knowledge_id/scope 按分工转 A（不 mock、不越权）。

## 一、执行结果总览

| # | Reviewer 要求 | 处理 | 状态 |
| --- | --- | --- | --- |
| High-2 | 移出 team_authored（44/77 候选 + 19/40 v3），仅真实可溯源进 Gate | 生成 v3 候选池（仅 public_derived 46 条）；重抽 v3 试标 40 条全真实 | ✅ |
| High-2 | conflict 补 ≥3 / forgetting 补 ≥2 / e2e 补 ≥2（真实源离线） | conflict 5→8、forgetting 6→8、e2e 6→8（从 git 跟踪的 v0_sample 真实数据抽取，raw_id 溯源） | ✅ |
| High-2 | 重建候选池 + 未泄露 v3 试标集 | gold_candidates_*_v3.jsonl（46 条）+ stage8_trial_set_v3.jsonl（40 条全 public_derived，`*_v3_*` 前缀） | ✅ |
| High-3 | v2 泄露 sample 永久废弃、不复用 | v3 试标全部 `*_v3_*` 新 id；无旧 v2 裸 id；context 无答案字段 | ✅ |
| High-4 evidence_event_ids | 已闭环 | 维持（60/60 回填、0 空、幂等） | ✅（不变） |
| High-4 knowledge_id | KB/D9 就绪后回填 | 登记：NOT production，待 KB | ⬜ 转 A/依赖 |
| High-4 scope | A 人工逐条复核 | 登记：待 A 复核后更新 SCOPE_MAP + 断言 | ⬜ 转 A |
| Medium-1 | 生成 trial_v3_context.jsonl（仅 input/元数据/证据，无 gold） | 40 条一一对应，无 gold/答案字段 | ✅ |
| Medium-2 | 表述改"规则归一化去重"或增强检测 | 脚本/4 份报告表述统一为"规则归一化去重" | ✅ |
| Medium-3 | PR 范围披露 | 维持 | ✅ |

## 二、数据变更明细

### v3 候选池（新增 5 文件，仅 public_derived，raw_id 溯源）
| 任务 | 数量 | 来源 |
| --- | --- | --- |
| preference_extraction | 10 | longmemeval 偏好 + multiwoz 用户句（v0_sample 真实） |
| knowledge_retrieval | 12 | t2ranking 真实 query |
| conflict_resolution | 8（5+3） | longmemeval 真实事件链（补 3） |
| precise_forgetting | 8（6+2） | longmemeval 真实记忆条目（补 2） |
| end_to_end_session | 8（6+2） | longmemeval_v2 真实任务链（补 2） |
| **合计** | **46** | 全 public_derived |

### v3 试标集（覆盖重抽为未泄露真实版）
- 40 条 = 5 任务 × 8；source 全 public_derived；sample_id 全 `*_v3_*`（无旧 v2 裸 id）；raw_id 全有。
- 旧 v3（含 19 team_authored）保留于 git 历史（审计）。

### A/B 骨架 v3（重生成，与试标一一对应）
- labels_A/B_trial_v3.jsonl 各 40 条，与试标 sample_id 完全一致（校验 True）。

### trial_v3_context.jsonl（Medium-1）
- 40 条一一对应试标；字段 = input/元数据/evidence/raw_id/template_family/language/timestamp；**无 gold/答案字段**（校验 0 含 gold）。

## 三、验证证据
1. 脚本 compile：rebuild_candidates_v3.py / sample_trial_set_v3_real.py / gen_trial_v3_context.py / stage8_semantic_dedup.py 全部 PASS。
2. 规则归一化去重：v3 候选 5 文件 dup_groups=0，RESULT CLEAN（exit 0）。
3. 一一对应：labels_A/B_trial_v3 ↔ stage8_trial_set_v3 = True；trial_v3_context ↔ 试标 = True（40=40）。
4. raw_id 溯源：试标 40 条全有 raw_id；context 全带 raw_id。
5. 泄露隔离：试标无旧 v2 裸 id（conf_000002 等）；context 无 gold 键。
6. 旧 v2 候选（gold_candidates_*_v2.jsonl，含 team_authored）未删除、未改动（保留审计/开发证据）。

## 四、新增脚本
- `scripts/convert/rebuild_candidates_v3.py`：真实候选池 v3 生成（仅 public_derived，补齐缺口）
- `scripts/convert/sample_trial_set_v3_real.py`：v3 试标未泄露真实版重抽
- `scripts/convert/gen_trial_v3_context.py`：trial_v3_context.jsonl 生成（无答案）

## 五、登记/待办（不 mock、不越权）
- High-4 knowledge_id：检索 260/260 仍缺，依赖 KB/D9；就绪后回填 + 重转 + 对账（转 A/依赖）。
- High-4 scope：A 按真实输入语义逐条复核 topic/tool/global，复核后更新 SCOPE_MAP + 断言测试 + 重转（转 A）。
- tool_result：本轮不产试标候选（红线：麒麟 VM 真实回放），登记阶段 10 依赖。
- P1-5：A/B 独立盲标 labels_A/B_trial_v3（用 trial_v3_context）→ label_check exit 0 → Kappa ≥0.70。

## 六、请 Reviewer
- 复核本轮 High-2/High-3/Medium-1/Medium-2 处理；High-4 剩余两项按分工由 A/KB 闭环后 B 配合校验。
