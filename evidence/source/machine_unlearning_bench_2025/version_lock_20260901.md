# machine_unlearning_bench_2025 版本线索锁定（2026-09-01）

- 正式名称：Data Unlearning Bench (KLOM)
- 核验时间：2026-09-01 20:41:52（Asia/Shanghai）
- 核验人：A（Data Owner，AI 辅助执行；最终批准权在 Reviewer）
- 核验命令：`python scripts/audit/stage3_version_lock.py --fetch`

## 版本线索

### 来源 1（hf）：machine-unlearning-bench/data-unlearning-bench

- Revision SHA：86afcc8b5737bc3b8f437e1c5ffccde3ecf7df75
- 最后修改：2025-05-20T16:10:52.000Z
- License（HF 卡片机读声明）：mit
- API 端点：https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench
- 存档文件：api_snapshot_20260901/hf_dataset_machine-unlearning-bench__data-unlearning-bench.json

## 使用说明

上游 SHA 会随官方更新而变化；本文件锁定核验时点版本，
作为阶段 6「再次下载可得到同一版本」的验收基线。
复测发现 SHA 变化时，应追加新日期的锁文件（保留本文件作历史）并交 Reviewer 裁决。
