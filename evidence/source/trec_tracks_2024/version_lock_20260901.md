# trec_tracks_2024 版本线索锁定（2026-09-01）

- 正式名称：TREC (NIST)
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（web）：https://trec.nist.gov/data.html

- 入口说明：官方数据门户
- 核验结果：OK 200
- 入口 URL：https://trec.nist.gov/data.html
- 存档文件：api_snapshot_20260901/web_check.json

## 备注

NIST 无单一 repo/release；版本线索以门户核验时点 + HTTP 状态存档；具体 Track 子集版本在子集选定后单独锁定

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
