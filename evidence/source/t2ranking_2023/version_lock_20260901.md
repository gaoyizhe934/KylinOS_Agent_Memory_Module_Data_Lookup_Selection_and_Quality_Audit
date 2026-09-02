# t2ranking_2023 版本线索锁定（2026-09-01）

- 正式名称：T2Ranking
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：THUIR/T2Ranking

- Commit SHA：3ab0a0de72dd50bf84d852a985f6188334781403
- 分支：main
- 提交时间：2023-07-03T08:47:00Z
- 提交标题：Update README.md
- API 端点：https://api.github.com/repos/THUIR/T2Ranking/commits/main
- 存档文件：api_snapshot_20260901/github_commit_THUIR__T2Ranking.json

### 来源 2（hf）：THUIR/T2Ranking

- Revision SHA：2a369a430a70979223f1b9a41b1919774d46b432
- 最后修改：2025-03-06T09:34:07.000Z
- License（HF 卡片机读声明）：apache-2.0
- API 端点：https://huggingface.co/api/datasets/THUIR/T2Ranking
- 存档文件：api_snapshot_20260901/hf_dataset_THUIR__T2Ranking.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
