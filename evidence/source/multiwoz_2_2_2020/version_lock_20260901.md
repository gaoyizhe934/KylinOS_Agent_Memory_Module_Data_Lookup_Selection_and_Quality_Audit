# multiwoz_2_2_2020 版本线索锁定（2026-09-01）

- 正式名称：MultiWOZ 2.2
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：budzianowski/multiwoz

- Commit SHA：fe0c8e65cfcd8462bd33c86e35f21addc84ca82b
- 分支：master
- 提交时间：2025-01-14T17:45:22Z
- 提交标题：Merge pull request #135 from dlwlgus53/patch-1
- API 端点：https://api.github.com/repos/budzianowski/multiwoz/commits/master
- 存档文件：api_snapshot_20260901/github_commit_budzianowski__multiwoz.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
