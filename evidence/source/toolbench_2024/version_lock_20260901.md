# toolbench_2024 版本线索锁定（2026-09-01）

- 正式名称：ToolBench
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：OpenBMB/ToolBench

- Commit SHA：d56fdd89faf8c91fa135090b212bb9057ee5cfc2
- 分支：master
- 提交时间：2025-05-21T15:46:57Z
- 提交标题：update missing google drive link
- API 端点：https://api.github.com/repos/OpenBMB/ToolBench/commits/master
- 存档文件：api_snapshot_20260901/github_commit_OpenBMB__ToolBench.json

## 备注

方法论参考（Reviewer 裁决 2026-09-01，PR#1 审批意见第四节第 4 条）；版本线索仍锁定，保证已存档 README 可追溯到具体仓库状态

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
