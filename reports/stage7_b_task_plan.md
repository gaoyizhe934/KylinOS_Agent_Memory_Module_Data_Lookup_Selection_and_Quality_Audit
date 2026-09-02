# 阶段 7 B 侧任务方案

- 角色：Annotator B（DGXD01）
- 日期：2026-09-02
- PR：#21 `feat/A-stage7-schema` → `master`
- 依据：PR #21 正文 + worklog/20260902_stage7_A.md + 手册第 7 章

---

## 一、PR #21 概述

A 侧（lyf-1213）完成阶段 7 统一 Schema 转换：
- 升级 `scripts/convert/convert_to_schema.py`（+295 / -24 行）
- 5 类 team_authored JSONL 重新转换（215 条，timestamp 修复）
- 新增 t2ranking 检索子集（200 条）、multiwoz 对话子集（200 条）、枚举字典
- 移除无法溯源的 `tool_result.jsonl`（50 行）
- processed 总计 715 条，audit 自检 0 缺字段 / 0 非法 timestamp / 0 缺 raw_id

## 二、B 侧任务清单

### 任务 1：Schema 校验

**目标**：独立验证 processed 全量 715 条记录符合统一 Schema。

| 检查项 | 方法 | 预期结果 |
| --- | --- | --- |
| 必填字段完整性 | 逐条检查 SCHEMA_REQUIRED 16 字段 | 0 缺字段 |
| timestamp 合法性 | `datetime.fromisoformat()` 验证全部 timestamp | 0 非法 timestamp |
| timestamp 修复正确性 | 对比 v1.0 `2026-07-202T` → v2.0 `2026-07-20T` | 全部修复，无残留 3 位日期 |
| raw_id 溯源（public_derived） | t2ranking 200 + multiwoz 200 + multiwoz_public 100 条 | 500 条全部有 raw_id |
| source_file / source_version | 逐条检查溯源字段 | 全部非空 |
| 行数对账 | team_authored 输入=输出、t2ranking 200、multiwoz 200 | 无静默丢失 |
| enum_dictionary.json 正确性 | 检查 task_type/source/template_family 枚举值 | 与实际数据一致 |
| tool_result.jsonl 已删除 | 确认文件不存在 | 已删除 |

**执行方式**：编写 `scripts/audit/stage7_b_schema_check.py` 校验脚本，独立运行。

### 任务 2：幂等性测试

**目标**：验证重复运行转换脚本输出字节一致。

| 检查项 | 方法 | 预期结果 |
| --- | --- | --- |
| 幂等性 | 运行 `convert_to_schema.py` 两次，比较 SHA256 | 前后哈希一致 |
| EOL 规范化 | 确认输出为 LF（非 CRLF） | 全部 LF |
| audit_processed 结果 | 转换后运行内置 audit | 0 issues |

**执行方式**：
1. 先运行 `python scripts/convert/test_convert.py`（A 侧已有测试脚本）
2. 独立计算 before/after 哈希对比
3. 运行 `convert_to_schema.py` 查看 audit 输出

### 任务 3：conversion_report.md

**目标**：产出 B 侧转换校验报告。

**结构**：
1. 校验范围与依据
2. Schema 校验结果（必填字段、timestamp、raw_id 溯源）
3. 幂等性测试结果
4. 转换对账（输入输出行数、静默丢失检查）
5. enum_dictionary 校验
6. 已知问题与诚实披露
7. Gate 7 建议

**路径**：`reports/conversion_report.md`

## 三、执行步骤

| 步骤 | 内容 | 依赖 | 预期产出 |
| --- | --- | --- | --- |
| 1 | 创建分支 `test/B-stage7-verify` | 无 | 分支就绪 |
| 2 | 切换到 PR #21 分支或 merge 到 B 侧分支 | 步骤 1 | 获取 A 侧转换产出 |
| 3 | 编写 `scripts/audit/stage7_b_schema_check.py` | 步骤 2 | 校验脚本 |
| 4 | 运行 schema 校验脚本 | 步骤 3 | 校验结果 |
| 5 | 运行幂等性测试（`test_convert.py` + 独立哈希对比） | 步骤 2 | 幂等性结果 |
| 6 | 运行 `convert_to_schema.py` 获取 audit 输出 | 步骤 2 | audit 结果 |
| 7 | 编写 `reports/conversion_report.md` | 步骤 4-6 | B 侧报告 |
| 8 | 展示修改清单与 Diff，等待用户审核 | 步骤 7 | 审核材料 |
| 9 | 用户授权后 commit + push + comment | 步骤 8 | PR #21 更新 |

## 四、初始进度

总进度：0/9（0%）

## 五、不修改范围

- 不修改 A 侧 `convert_to_schema.py`（如发现 bug 在报告中记录，不直接改 A 侧代码）
- 不修改 `data/processed/` 数据文件（B 侧只校验不产出数据）
- 不签 Gate 7（Reviewer 职责）
- 不修改 `test_convert.py`（A 侧产出，B 侧独立运行验证）

## 六、已知风险

1. **EOL 差异**：Windows 下 git autocrlf 可能导致 CRLF/LF 混淆，幂等性测试需规范化换行后比较
2. **raw 数据依赖**：t2ranking 和 multiwoz 转换依赖 `data/raw/` 下的 v0_subset 文件，若文件不在仓库中（.gitignore 排除），需确认本地存在
3. **multiwoz_public_sample.jsonl**：PR #21 未修改此文件，可能已在 master 上，需确认其存在且为 100 条
