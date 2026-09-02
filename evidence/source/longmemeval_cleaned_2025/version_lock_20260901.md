# longmemeval_cleaned_2025 版本线索锁定（2026-09-01）

- 正式名称：LongMemEval (cleaned)
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：xiaowu0162/LongMemEval

- Commit SHA：9e0b455f4ef0e2ab8f2e582289761153549043fc
- 分支：main
- 提交时间：2026-05-11T22:49:24Z
- 提交标题：Update README.md
- API 端点：https://api.github.com/repos/xiaowu0162/LongMemEval/commits/main
- 存档文件：api_snapshot_20260901/github_commit_xiaowu0162__LongMemEval.json

### 来源 2（hf）：xiaowu0162/longmemeval-cleaned

- Revision SHA：98d7416c24c778c2fee6e6f3006e7a073259d48f
- 最后修改：2025-09-19T23:48:16.000Z
- License（HF 卡片机读声明）：mit
- API 端点：https://huggingface.co/api/datasets/xiaowu0162/longmemeval-cleaned
- 存档文件：api_snapshot_20260901/hf_dataset_xiaowu0162__longmemeval-cleaned.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
