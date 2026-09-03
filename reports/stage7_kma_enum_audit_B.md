# 阶段7 KMA 枚举/格式 B 侧审计（DGXD01，非破坏性）

- 日期：2026-09-03
- 依据：PR #26 KMA 对齐（FREEZE_PROPOSAL）；红线：不重转 processed、不打断阶段8试标

## 一、审计结果

| 检查项 | 结果 |
| --- | --- |
| processed 总条数 | 715 |
| 旧字段命中（偏好/冲突/遗忘/Tool） | {'preference_extraction': 300, 'conflict_resolution': 80, 'precise_forgetting': 40} |
  - preference_extraction: 300 处（示例：pref_000001:preference_type, pref_000001:scope, pref_000001:confidence）
  - conflict_resolution: 80 处（示例：conf_000001:conflict_type, conf_000001:winner, conf_000002:conflict_type）
  - precise_forgetting: 40 处（示例：forg_000001:checkpoints, forg_000002:checkpoints, forg_000003:checkpoints）
| 时间戳不满足 UTC .sssZ | 715 条
  - 示例：conf_000001:2026-07-20T10:00:00+08:00, conf_000002:2026-07-20T10:00:00+08:00, conf_000003:2026-07-20T10:00:00+08:00, conf_000004:2026-07-20T10:00:00+08:00, conf_000005:2026-07-20T10:00:00+08:00
| public_derived 缺 raw_id | 0 条
| Low-3 补全的 legacy 枚举键（值个数） | {'status': 5, 'persist_policy': 2, 'checkpoints': 3, 'confidence': 3, 'winner': 5} |
| enum_dictionary 仍缺键 | 无 |

## 二、与 A 的 KMA_LEGACY_MAP 交叉核对
- B 侧 stage7_enum_check.py（位于 #25 分支）只做枚举合法性（旧词表）与结构检查，不重写/不阻断 processed；与 A 的 KMA_LEGACY_MAP 参考层无冲突。
- 本 PR（#26）由本脚本 stage7_kma_b_audit.py 承担 KMA 映射层审计（避免跨 PR 依赖 #25 未合入文件）；enum_check 的 --kma 升级待 #25 合并后同步补齐。

## 三、结论与建议
- KMA=FREEZE_PROPOSAL：本审计为参考层报告，exit 0，不阻断。
- FROZEN 后：按 reports/stage1_kma_mapping_B_review.md 差异裁定 → 重写 enum_dictionary → 重转 processed gold → 重建阶段8标注枚举/骨架。
