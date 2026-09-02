# personachat_2018 版本线索锁定（2026-09-01）

- 正式名称：PersonaChat (ParlAI)
- 核验时间：2026-09-01 20:43:00（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（github）：facebookresearch/ParlAI

- Commit SHA：a29567f7ce76992fd1f03c51ba9e3b155a37ea51
- 分支：main
- 提交时间：2026-07-30T21:27:01Z
- 提交标题：Replace jQuery CDN link with jsDelivr version
- API 端点：https://api.github.com/repos/facebookresearch/ParlAI/commits/main
- 存档文件：api_snapshot_20260901/github_commit_facebookresearch__ParlAI.json

### 来源 2（web）：http://parl.ai/downloads/personachat/personachat.tgz

- 入口说明：官方 tgz 数据入口
- 核验结果：OK 200
- 入口 URL：http://parl.ai/downloads/personachat/personachat.tgz
- 存档文件：api_snapshot_20260901/web_check.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
