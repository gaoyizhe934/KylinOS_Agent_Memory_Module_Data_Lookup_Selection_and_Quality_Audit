# KMA 裁定支撑样例：confidence 换算表 + app/task 语义样例（Annotator A）

- 角色：Annotator A（lyf-1213）
- 目的：为 Reviewer 裁定 FROZEN 清单 #2（app/task 语义落点）、#3（confidence 高/中/低→[0,1] 换算口径）提供样例与候选换算表。
- KMA 状态：FREEZE_PROPOSAL；本文为建议稿，最终裁定归 Reviewer。

---

## 一、confidence 高/中/低 → confidence_score [0,1] 换算建议

| 旧（v1.x） | 语义 | 建议 confidence_score | 依据 |
| --- | --- | --- | --- |
| high | 一句话说死，无需推断 | 0.95 | 证据充分、显式 |
| medium | 靠多句/行为推断 | 0.70 | 多次一致行为 |
| low | 模糊、低证据 | 0.40 | 单次弱证据 |

**可选档位（更细）**：
- 显式且唯一 → 0.95~1.0
- 显式但有歧义 → 0.85
- 两次一致行为 → 0.75
- 单次行为 → 0.60
- 极弱 → 0.30~0.40

**规则**：建议固定三档为主（0.95/0.70/0.40）避免标注方差；如需细分用 0.85/0.75/0.60 作为中间档，但**必须在标注手册固定档位表**（防 A/B 自由发挥导致 Kappa 下降）。

### 样例换算
| 用户原文 | 旧 confidence | 新 confidence_score |
| --- | --- | --- |
| "以后周报必须用要点，别废话" | high | 0.95 |
| 连续 3 次手动改回简洁（无口头声明） | medium | 0.70 |
| "嗯……可能简洁点吧……" | low | 0.40 |

---

## 二、app/task 语义落点建议（旧 scope 映射）

旧 scope：`global / app / task / session`；KMA：`global / topic / tool / session / time_window`。

**不机械映射**（B 复核意见）：app≠tool、task≠topic 需按语义裁决。候选落点：

| 旧值 | 典型场景 | 候选落点 | 说明 |
| --- | --- | --- | --- |
| app | "项目管理工具里用中文标签" | `tool` | 指向具体工具/应用 → KMA `tool` |
| app | "麒麟 OS 桌面助手默认……" | `tool` 或 `global` | 助手整体 → 待裁定（工具 vs 全局） |
| task | "做周报时用简洁要点" | `topic` | 指向某类工作主题 → KMA `topic` |
| task | "发邮件时用签名 X" | `tool` | 指向工具行为 |
| session | "这次就按英文回复" | `session` | 一致，不变 |
| global | "以后都先问我确认" | `global` | 一致，不变 |

**建议**：优先语义映射——"针对某工具/应用的行为"→`tool`；"针对某类工作主题"→`topic`；"整体系统"→`global`；"仅本次"→`session`；"某时间窗"→`time_window`。最终由 Reviewer 定一份固定对照表入标注手册。

### 样例
| 用户原文 | 旧 scope | 建议 KMA preference_scope |
| --- | --- | --- |
| 在这个项目管理工具里一律用中文标签 | app | tool |
| 做周报时用简洁要点 | task | topic |
| 发邮件时默认带签名 | app | tool |
| 这次就用英文回复 | session | session |
| 以后都先问我确认 | global | global |

---

## 三、附注

- 以上为 A 侧建议稿，供 Reviewer 裁定 FROZEN 清单 #2/#3；
- 裁定后：换算表与 scope 对照表固定入 `annotation_guideline_v2.md` §3/§5；
- A 未据此改动 labels 骨架或重转 processed（FROZEN 前边界）。
