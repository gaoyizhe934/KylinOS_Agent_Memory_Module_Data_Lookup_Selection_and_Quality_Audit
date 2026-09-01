# msmarco_2021 版本线索锁定（2026-09-01）

- 正式名称：MS MARCO
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（hf）：microsoft/ms_marco

- Revision SHA：a47ee7aae8d7d466ba15f9f0bfac3b3681087b3a
- 最后修改：2024-01-04T16:01:29.000Z
- API 端点：https://huggingface.co/api/datasets/microsoft/ms_marco
- 存档文件：api_snapshot_20260901/hf_dataset_microsoft__ms_marco.json

### 来源 2（web）：https://microsoft.github.io/msmarco/

- 入口说明：官方项目页
- 核验结果：OK 200
- 入口 URL：https://microsoft.github.io/msmarco/
- 存档文件：api_snapshot_20260901/web_check.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
