# #28 Review 打回处理报告（DGXD01 代 A，2026-09-04）

> 响应：Reviewer 对 HEAD bf42099 的 CHANGES_REQUESTED（High-1~4、Medium-1~3）。
> 说明：按 Reviewer 要求不改原 PR 正文；本报告为修改说明，处理分「已完成」「待外部依赖」「待裁定」三类，不 mock、不越权、不删审计证据。

---

## 一、处理总览

| Reviewer 意见 | 结论 | 状态 |
| --- | --- | --- |
| High-1 绕过批次/Gate、以未合并分支为基线 | 承认流程违规；登记待协调方按批次拆分（本仓库单 PR 纪律 vs Reviewer 拆批要求冲突） | ⚠️ 待裁定（见 §五） |
| High-2 候选/v3 含不可核验自建数据（禁 mock） | 承认；44/77 team_authored 自建 + 19/40 v3 关联样本待移出 | ⚠️ 待数据源补足（见 §三） |
| High-3 试标答案泄露 | **已处理**：4 个已跟踪泄露文件 git rm + gitignore；v2 sample_id 废弃登记 | ✅ 已提交 18a0dc7 |
| High-4 KMA 转换字段留空 | evidence_event_ids **已回填**（60 条 0 空，幂等）；knowledge_id 需 KB/D9；scope 语义需逐条人工复核 | 🟡 部分完成（见 §四） |
| Medium-1 无 v3 独立标注上下文包 | 待 High-2 数据源裁定后生成（避免对将移出样本白做） | ⬜ 待数据源 |
| Medium-2 去重表述不匹配 | 承认：现为"规则归一化去重"，非"语义级" | ⬜ 待改表述/增强检测 |
| Medium-3 PR 范围/提交规范 | 本报告即范围披露；后续新提交用规定前缀 | ✅ 本报告 |

---

## 二、已完成（commit 18a0dc7）

1. **High-3 泄露隔离**：git rm 已跟踪泄露文件 4 个
   - `data/interim/review/labels_B_trial_v2.draft.jsonl`（40 条预填 gold）
   - `data/interim/review/P1_5_B_draft_reasons.md`（逐字段答案）
   - `worklog/stage8_P1-5_annotation_guide_all_options.md`（"应填参考"+AI 入口）
   - `worklog/stage8_P1-5_labels_checklist_mc.md`（"参考"答案列）
   - 同步 .gitignore 防再跟踪；AI 参考 labels_A_reference_AI.jsonl 确认未跟踪（gitignore 已含）
   - **v2 sample_id 永久废弃登记**：不用于 Kappa/Gate；后续试标从未泄露、真实可溯源样本抽取
2. **High-4（evidence_event_ids 部分）**：修复 `scripts/convert/kma_convert.py` 硬置空缺陷 → 幂等回填（引用本行 evidence.source_event_id，非新增 mock）；`preference_extraction.jsonl` 60 条全部回填（0 空，与 evidence 逐条一致，二次运行零改动=幂等）

## 三、High-2 处理状态（待真实数据源，不 mock）

- 候选池 77 条中 **44 条 team_authored 自建**（os_* 场景 + 自造 evt_*、conflict "旧记忆/新指令"占位）与 v3 试标 19/40 关联样本：按 Reviewer 应移出，仅保留 public_derived 33 条（带 raw_id/source_file/source_version/证据定位）。
- 移出后每任务不足 8 条 → **P1-5 试标保持阻塞**（与 Reviewer 结论一致），直至补足真实可溯源来源（需 A 数据选型/协调方提供，或按 Gate 纪律等待）。
- 已提交的候选/v3 文件保留作审计证据（git 历史可溯），不在本 PR 删除正式产物；若 Reviewer 要求立即从工作区移出，请指示（破坏性操作需单独授权）。

## 四、High-4 其余部分状态

| 子项 | 状态 | 说明 |
| --- | --- | --- |
| evidence_event_ids | ✅ 已回填 | 上述 commit |
| knowledge_id（检索 260/260 缺） | ⬜ 依赖 KB/D9 | 手册 §4 已允许 KB 就绪前 NOT production 标记；无真实 KB 不能 mock 生成 ID。KB 就绪后由 kma_convert 回填 + B 对账 |
| scope 语义（topic/tool/global 逐条） | ⬜ 需人工语义复核 | 属 A 标注/复核职责，脚本不臆造；复核后更新 SCOPE_MAP 或逐条修正 + 断言测试 |

## 五、High-1 流程：待协调方裁定

Reviewer 要求：#28 不得合并、保留为审计证据、后续按批次从 master 建独立 PR、先 P1-2/3/4 再 P1-5。
本仓库纪律（用户全局记忆）：一个阶段一个 PR、无明确允许禁止新增 PR。
→ 两规则冲突，**需协调方（用户/Reviewer）裁定**：#28 内继续推进 vs 拆批新建 PR。在裁定前不擅自新建 PR、不改写历史（无 rebase）。

## 六、验证

- commit 18a0dc7：7 files changed (+79/-941)；删除 4 泄露文件、回填 60 条 preference
- evidence_event_ids：60/60 非空、与 evidence.source_event_id 一致 0 差异、二次执行 0 改动（幂等）
- kma_convert.py：compile PASS
- processed 其余文件与 HEAD 一致（未误改）

## 七、风险与回滚

- 泄露文件已 git rm：历史提交仍含（GitHub 可审计）；如需彻底抹除历史需协调方决策（涉及改写历史，默认不做）
- 本次未触碰：候选池 v2/v3 文件、其它 processed、schema/enum/registry（避免在数据源裁定前扩大改动）
- 回滚：`git revert 18a0dc7` 可恢复泄露文件（不建议，违反 High-3）

## 八、下一步（建议顺序）

1. 协调方裁定 High-1（#28 vs 拆批）；
2. A/协调方补足真实可溯源候选（High-2 解除阻塞）；
3. KB/D9 就绪后回填 knowledge_id（High-4）；
4. A 人工语义复核 scope（High-4）→ 补 SCOPE_MAP 断言测试；
5. 生成 trial_v3_context.jsonl（Medium-1）+ 去重表述修正（Medium-2）；
6. 全部闭环后重新请求 Reviewer 复审。
