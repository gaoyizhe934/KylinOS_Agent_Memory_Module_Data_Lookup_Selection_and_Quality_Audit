# Stage 0 工作区初始化检查清单（v2.0）

生成日期：2026-08-31
依据：手册第 9 章目录结构 + v2.0 重建计划阶段 0

## 目录结构验证

| 目录 | 要求 | 状态 |
| --- | --- | --- |
| data/raw/ | 原始下载，只读不直接修改 | ✅ 已创建，各数据集 v0_sample/v0_pending 子目录齐备 |
| data/interim/ | 中间候选（gold_candidates_*.jsonl） | ✅ 已创建，含 6 个候选文件 + 筛选记录 |
| data/processed/ | 统一 Schema 转换后 | ✅ 已创建，含 6 个 JSONL + schema.json |
| data/gold/dev/ | 50% 开发集 | ✅ 已创建 |
| data/gold/regression/ | 20% 回归集 | ✅ 已创建 |
| data/gold/sealed_test/ | 30% 封存测试集 | ✅ 已创建 |
| data/runtime_replay/ | 麒麟 VM 回放准备包 | ✅ 已创建 |
| registry/ | 登记表 | ✅ 已创建（dataset_registry.csv / source_registry.csv / license_registry.csv / split_manifest.csv）|
| evidence/source/ | 来源证据 | ✅ 已创建，11 个数据集证据目录 |
| evidence/ai_outputs/ | AI 输出存档 | ✅ 已创建 |
| evidence/audit/ | 审计报告 | ✅ 已创建 |
| evidence/hashes/ | SHA256 封存记录 | ✅ 已创建 |
| evidence/runtime/ | 运行环境证据 | ✅ 已创建 |
| reports/ | 报告 | ✅ 已创建 |
| scripts/ | 脚本 | ✅ 已创建（download/convert/split/validate/evaluate/oneclick）|
| worklog/ | 工作日志 | ✅ 已创建 |

## 分工确认

| 角色 | 姓名 | 状态 |
| --- | --- | --- |
| Annotator A（兼数据收集/转换） | lyf-1213 | ✅ |
| Annotator B（兼校验/审计/脚本） | DGXD | ✅ |
| Reviewer（兼裁决/审批） | gaoyizhe | ✅ |

## Gate 0 通过条件

| 条件 | 状态 |
| --- | --- |
| 目录可用 | ✅ 16 个目录已创建 |
| 负责人明确 | ⚠️ 3 个角色待指定 |
| raw 目录只读/不直接修改 | ✅ 约定已建立，修改通过 ingest 脚本 |
| registry 初始化 | ✅ dataset_registry.csv 已填写 11 个数据集 |

## 结论

**Gate 0 待 Reviewer 批准** — 目录结构就绪，但负责人尚未指定。