# KMA 标准溯源与对齐说明（B 侧，2026-09-04 修订，响应 Reviewer High-1）

## 一、两版文档与关系
| 文件 | 状态 | 来源 | 行数 | 说明 |
| --- | --- | --- | --- | --- |
| KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md | FREEZE_PROPOSAL（KMA-DATA-SCHEMA-001 v1.0，历史存档版） | 本仓库早期经工作区外（Downloads）提供文件存档 | 975 | 早期编码基准；编号/基线为其文件自述，未经主仓库 git 溯源 |
| KMA_UNIFIED_DATA_FORMAT_FREEZE_CANDIDATE_main.md | CANDIDATE_FOR_FREEZE（Canonical Business Schema v1） | 主仓库 Kylin-Agent-Competition/kylinOS-agent-memory docs/architecture/KMA_UNIFIED_DATA_FORMAT_FREEZE_V1.md，commit 889b7553（2026-09-03，E 轨作者），2026-09-04 抓取 | 约 441 | **主仓库当前权威候选**，D/E 轨 FROZEN 核验基准；R-1..R-6 裁定 |

## 二、基线引用纠正（High-1 #3）
- 旧 provenance 声称存档版基线 `main@b70827c5…`：该路径不可用（404），且 KMA-DATA-SCHEMA-001 编号在主仓库无对应 —— 已纠正：存档版仅作为历史参考，**不再作为对齐/核验基准**。
- 本仓库对齐/核验基准改为：主仓库权威候选（上表第 2 行，含 commit/日期/路径）。

## 三、权威版枚举/裁定逐项核对记录（High-1 #2）
已用主仓库候选版核对（抽查核心语义）：
- R-2 expression_type=explicit/implicit（candidate 由 memory_status 表达）：与仓库编码一致 ✅
- R-3 memory_status 六值（active/superseded/deprecated/expired/removed/candidate），is_active/is_outdated/should_decay 仅兼容：与仓库编码一致 ✅
- R-4 processing_status 为 Runtime technical state，与 source_business_status（八值）正交、不得升格业务枚举：与仓库编码一致 ✅
- preference_scope / conflict_type / forget_mode 等具体值域在候选 L1 未逐值展开（依 R-5/R-6 + D3 L2/不裁定清单）→ **登记待 E/D 确认来源**（见 pending 清单 #9）。

## 四、结论
High-1 已闭环（权威版入库 + provenance 纠正 + 核心枚举核对）；preference_scope/conflict_type 来源确认与 D 轨物理映射、E 轨签名另案登记。
