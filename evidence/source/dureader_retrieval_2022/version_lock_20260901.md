# dureader_retrieval_2022 版本线索锁定（2026-09-01）

- 正式名称：DuReader Retrieval
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：baidu/DuReader

- Commit SHA：c625076b06da8f56d59f19c41c73bd580a98a347
- 分支：master
- 提交时间：2022-05-26T09:30:46Z
- 提交标题：Update README.md
- API 端点：https://api.github.com/repos/baidu/DuReader/commits/master
- 存档文件：api_snapshot_20260901/github_commit_baidu__DuReader.json

### 来源 2（github）：PaddlePaddle/RocketQA

- Commit SHA：e2bfcfcfa902ac6cef7f0d359606a9da05b795ac
- 分支：main
- 提交时间：2022-12-03T15:48:43Z
- 提交标题：add survey paper
- API 端点：https://api.github.com/repos/PaddlePaddle/RocketQA/commits/main
- 存档文件：api_snapshot_20260901/github_commit_PaddlePaddle__RocketQA.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
