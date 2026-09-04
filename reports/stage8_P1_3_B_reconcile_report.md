# 阶段8 P1-3 B 侧对账报告（DGXD01）— 2026-09-04

- 对象：A 交付 feat/A-stage8-p1-2-3（ed586c3，P1-2 手册 v2 定稿 + P1-3 全量重转 kma_convert.py）
- 命令：python scripts/audit/stage8_reconvert_reconcile.py --canonical；python scripts/audit/schema_drift_check.py

## 一、结果
| 检查 | 结果 |
| --- | --- |
| 行数对账（六任务 canonical，415） | ✅ 40/15/60/200/40/60=415，无缺失/多出 |
| raw_id（public_derived） | ✅ 0 缺失 |
| gold 非空 | ✅ 0 空 |
| 字段登记（schema_drift，canonical gold 字段已补登） | ✅ 0 未登记 / 0 enum 分层缺失（field_mapping 68 行） |
| **时间戳 canonical（UTC .sssZ）** | ❌ **415 条全部非 UTC .sssZ**（当前为 `2026-07-20T10:00:00+08:00`：带 +08:00、无毫秒、无 Z） |

## 二、结论与要求
1. **P1-3 数据质量未达标（时间戳）**：gold 字段 canonical 化与数量对账通过，但 timestamp 未按 canonical UTC `.sssZ` 归一（KMA §3.6：`YYYY-MM-DDTHH:MM:SS.sssZ`，比较前统一 UTC）。
2. 要求 A 修正 kma_convert.py：时间输出归一为 UTC 毫秒 Z（如 `2026-07-20T02:00:00.000Z`），或明确场景时间为 UTC 语义后重转；重转后 B 复跑 reconcile --canonical 至 PASS。
3. B 侧已补：field_mapping 登记 canonical gold 字段（68 行）+ reconcile --canonical 脚本就绪。

## 三、待办
- [ ] A：修 timestamp → UTC .sssZ 后重转（P1-3 修正）；
- [ ] B：复跑 reconcile --canonical（PASS 后）→ P1-4 骨架 → P1-5/6。
