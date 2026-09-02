# 阶段 6 冻结基线声明（Reviewer 确认，2026-09-02）

- 确认人：gaoyizhe（Reviewer）
- 依据：PR#19 预下载证据（download.log + B 侧校验）+ `evidence/hashes/stage6_manifest.json` + `evidence/hashes/stage6_subset_hash.txt` + `reports/stage6_b_verify_report.md` + 各候选 `version_lock_20260901.md`
- 前置：Gate 5 已批准（PR#20，2026-09-02）

## 一、冻结基线定义

本仓库正式冻结基线 = **stage6_manifest.json（文件级 SHA256 + 大小 + 只读）+ 各候选版本锁定（version_lock_20260901.md）**。

- 二进制数据文件按仓库策略不入 git（.gitignore 排除）；manifest 为冻结的权威校验依据；
- 正式封存时通过 frozen 分支/外部存储固化二进制，仓库内以 manifest + 版本锁定实现"再次下载可得到同一版本"的可复现校验。

## 二、冻结确认（4/5 数据集）

| 数据集 | 冻结文件 | SHA256（前16位） | 版本锁定 | Gate 6 结论 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | longmemeval_oracle.json | 821a2034d219ab45 | HF rev 98d7416c + commit 9e0b455f | ✅ 冻结确认 |
| longmemeval_cleaned_2025 | longmemeval_s_cleaned.json | d6f21ea9d60a0d56 | 同上 | ✅ 冻结确认 |
| longmemeval_v2_2026 | questions.jsonl | 0a3ae5ebea938c24 | HF rev f152293e + commit 2cc8c540 | ✅ 冻结确认 |
| t2ranking_2023 | queries.dev.tsv | 1df544dd04bf9b6d | HF rev 2a369a43 | ✅ 冻结确认 |
| t2ranking_2023 | qrels.retrieval.dev.tsv | 17f31db546ce3a5f | 同上 | ✅ 冻结确认 |
| multiwoz_2_2_2020 | dialogues_001.json | e7ddb563e4da5766 | commit fe0c8e65 | ✅ 冻结确认 |

**Gate 6：4/5 通过**（6 个文件冻结基线确认，2026-09-02，Reviewer）。

## 三、条件项

- **stabletoolbench_2024**（G1_instruction.json，f8faf3d6…）：文件已下载并校验，但其阶段 4 审计样本缺口（仅 3 条）未闭合，冻结**条件待补**——待阶段 4 样本补齐后复核并纳入正式冻结。

## 四、复检程序（再次下载可得到同一版本）

1. 按各候选 `version_lock_20260901.md` 的锁定 URL（GitHub commit/HF revision/Web）重下固定子集；
2. 走 `scripts/download/download_stage6.py` 镜像路由（或直连）下载；
3. 计算 SHA256 并与 `stage6_manifest.json` 比对，全部一致即复检通过；
4. 任一不一致 → 暂停并上报 Reviewer（版本上游变动时按 version_lock 语义追加新日期锁并裁决）。

## 五、说明

- 本声明确认冻结基线，**不替代** stabletoolbench 补齐后的复核；
- processed（阶段 7）仅允许基于已冻结确认的数据集转换；stabletoolbench 相关 processed 待其条件闭合后再产出。
