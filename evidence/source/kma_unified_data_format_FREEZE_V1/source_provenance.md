# KMA 标准溯源与对齐说明（v2 修订，响应 Reviewer High-1）

- 建档：2026-09-03；修订：2026-09-04（响应 Reviewer High-1：跨轨基线引用纠正 + 权威版补入）
- 目的：KMA 对齐依据入库可独立核验；纠正旧版基线引用错误。

## 一、主仓库当前权威文档（CANDIDATE_FOR_FREEZE）— 最新，以此为对齐基线

| 项 | 值 |
| --- | --- |
| 文档 | `KMA_UNIFIED_DATA_FORMAT_FREEZE_V1_MAIN_CANDIDATE.md`（本目录已入库，从主仓库抓取） |
| 主仓库路径 | `docs/architecture/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md` |
| 版本 / 状态 | v1 / `CANDIDATE_FOR_FREEZE`（2026-09-03，E 轨作者，D Reviewer 审查） |
| 结构 | R-1..R-6 六项裁定 + 字段别名/映射边界表 + 物理结构边界 + 明确不裁定清单 |
| 基线仓库 | `Kylin-Agent-Competition/kylinOS-agent-memory`（main 分支） |
| 获取方式/日期 | raw.githubusercontent 抓取（`main` 分支，未锁定 commit SHA；2026-09-04 访问） |
| 编号说明 | **主仓库该文档无 `KMA-DATA-SCHEMA-001` 编号**；旧存档版编号为本地自拟，已纠正 |

### 权威版关键裁定（R-1..R-6）
- R-1：`captured_at` canonical（`collected_at` 仅 legacy transport alias）
- R-2：`expression_type` 仅 `explicit/implicit`（`candidate` 由 `memory_status=candidate` 表达）
- R-3：`memory_status` 六值生命周期唯一真值（`is_active/is_outdated/should_decay` 仅 compatibility）
- R-4：`processing_status` 仅 Runtime technical state，与 `source_business_status`（八值）正交
- R-5：`sensitivity` canonical（`sensitivity_level` 仅注解层 1:1 alias）
- R-6：业务 Canonical 与 C++/IPC/SQLite 物理结构非 1:1 同形，差异经 Adapter/Mapping

### 与本仓库编码的一致性核验
| 本仓库编码字段 | 权威版裁定 | 一致性 |
| --- | --- | --- |
| memory_status（6 值） | R-3 ✅ | 一致 |
| source_business_status（8 值） | R-4 ✅ | 一致（八值业务结果） |
| expression_type（explicit/implicit） | R-2 ✅ | 一致 |
| sensitivity | R-5 ✅ | 一致 |
| preference_scope / conflict_type / knowledge_type / resolution_status / forget_mode | 权威版 **未逐项列出**（落于 D3 L2 或"不裁定清单"） | 🟡 需 D3 契约核对（FROZEN 前裁定项，已在清单登记） |

> 注：旧存档版（975 行，FREEZE_PROPOSAL）含更全的枚举明细（§5），作为**参考明细**保留；**对齐基线以主仓库权威版（CANDIDATE_FOR_FREEZE）为准**，两版差异见下节。

## 二、与旧存档版（975 行 FREEZE_PROPOSAL）的关系

| 项 | 旧存档版 `KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md`（975 行） | 主仓库权威版（159 行） |
| --- | --- | --- |
| 来源 | 项目组本地 Downloads（工作区外） | 主仓库 main `docs/architecture/`（2026-09-04 抓取） |
| 状态 | FREEZE_PROPOSAL | CANDIDATE_FOR_FREEZE |
| 编号 | KMA-DATA-SCHEMA-001（自拟，主仓库无对应） | 无编号 |
| 内容 | 详尽的 §1-§14 完整规范（枚举/对象/校验） | 精简的 R-1..R-6 裁定 + 边界/不裁定清单 |
| 角色 | **参考明细**（提供更全枚举清单） | **对齐基线**（权威裁定） |

**裁决**：对齐依据以主仓库权威版为准；旧存档版仅作枚举明细参考，不视为 FROZEN 核验依据。若两版对同一字段定义冲突，以权威版为准。

## 三、D9 检索集
- 已补档：`D9_RETRIEVAL_QUERYSET_CANDIDATE_V2_36.jsonl`（本目录 + `evidence/source/d9_retrieval_queryset/`，2026-09-04）。
- 作为检索标注规则参考（knowledge_type / guardrail_category / 版本级引用）。

## 四、遗留（FROZEN 前必办，已在 worklog/20260903_KMA_FROZEN_pending_items.md 登记）
1. preference_scope / conflict_type 等权威版未列字段 → 需与 D3 契约（L2）核对落点（FROZEN 清单补充项）。
2. KMA 转 FROZEN（主仓库 D Reviewer 签署 + 合并 main）后，权威副本（FROZEN 版）再次同步入库。
3. Medium-1：D 轨对"gold 字段 → SQLite/Vector 落库命名"做一次映射确认（不阻塞本 PR 定义层）。
