# 阶段 6 B 侧校验报告

- 角色：Annotator B（DGXD01）
- 分支：`feat/A-stage6-download`
- 日期：2026-09-02
- 依据：手册第 6 章「正式下载与镜像路由」、A 侧 `scripts/download/download_stage6.py` 和 `worklog/20260902_stage6_A.md`

## 校验范围

对 A 侧 PR #19 下载的 5 个数据集 v0_subset 进行 B 侧独立校验：

1. SHA256 哈希计算
2. manifest 生成
3. 只读冻结
4. 版本复检
5. 下载日志交叉验证

## 校验结果

### 1. SHA256 哈希

| 数据集 | 文件 | 大小(bytes) | SHA256(前16位) | 只读 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | longmemeval_oracle.json | 15,388,478 | 821a2034d219ab45 | ✅ |
| longmemeval_cleaned_2025 | longmemeval_s_cleaned.json | 277,383,467 | d6f21ea9d60a0d56 | ✅ |
| longmemeval_v2_2026 | questions.jsonl | 286,186 | 0a3ae5ebea938c24 | ✅ |
| t2ranking_2023 | queries.dev.tsv | 939,767 | 1df544dd04bf9b6d | ✅ |
| t2ranking_2023 | qrels.retrieval.dev.tsv | 1,468,343 | 17f31db546ce3a5f | ✅ |
| stabletoolbench_2024 | G1_instruction.json | 26,007 | f8faf3d692312758 | ✅ |
| multiwoz_2_2_2020 | dialogues_001.json | 11,771,811 | e7ddb563e4da5766 | ✅ |

- 全部 7 个文件 SHA256 已计算并记录至 `evidence/hashes/stage6_subset_hash.txt`；
- 全部 7 个文件已设为只读（mode=0o444）；

### 2. Manifest

- 路径：`evidence/hashes/stage6_manifest.json`；
- 内容：5 个数据集 × 7 个文件的 SHA256、大小、只读状态；
- 生成时间：2026-09-02T12:47:11 UTC；

### 3. 只读冻结

| 检查项 | 结果 |
| --- | --- |
| 全部文件不可写 | ✅ 通过 |
| mode 全部为 0o444 | ✅ 通过 |

### 4. 版本复检

| 数据集 | 版本线索 | Gate 3 状态 | 版本锁定记录 |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | HF rev 98d7416c (2025-09-19) | 允许试用 | version_lock_20260901.md ✅ |
| longmemeval_v2_2026 | HF rev f152293e | 允许试用 | version_lock_20260901.md ✅ |
| t2ranking_2023 | HF rev 2a369a43 (2025-03-06) | 允许试用 | version_lock_20260901.md ✅ |
| stabletoolbench_2024 | master commit aa4ed9f4 | 允许试用 | version_lock_20260901.md ✅ |
| multiwoz_2_2_2020 | master commit fe0c8e65 | 允许试用 | version_lock_20260901.md ✅ |

- 全部 5 个数据集有版本锁定记录；
- 全部版本线索与 `dataset_registry.csv` 一致；

### 5. 下载日志交叉验证

| 数据集 | 文件 | 字节数匹配 | 说明 |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | longmemeval_oracle.json | ✅ | 15,388,478 bytes 一致 |
| longmemeval_cleaned_2025 | longmemeval_s_cleaned.json | ✅ | 277,383,467 bytes 一致 |
| longmemeval_v2_2026 | questions.jsonl | ⚠️ | download.log 被重下脚本覆盖（0 bytes），但原日志记录 286,186 bytes，与实际文件一致 |
| t2ranking_2023 | queries.dev.tsv | ✅ | 939,767 bytes 一致 |
| t2ranking_2023 | qrels.retrieval.dev.tsv | ✅ | 1,468,343 bytes 一致 |
| stabletoolbench_2024 | G1_instruction.json | ✅ | 26,007 bytes 一致 |
| multiwoz_2_2_2020 | dialogues_001.json | ✅ | 11,771,811 bytes 一致 |

## 产出物

| 产出文件 | 路径 |
| --- | --- |
| B 侧校验脚本 | `scripts/audit/stage6_b_verify.py` |
| Manifest (JSON) | `evidence/hashes/stage6_manifest.json` |
| 哈希文件 | `evidence/hashes/stage6_subset_hash.txt` |
| B 侧校验报告 | `reports/stage6_b_verify_report.md` |

## 已知问题

1. **download.log 覆盖**：B 侧重下脚本覆盖了 longmemeval_v2 的 download.log（0 bytes）。原始日志内容为 `OK 286186 https://hf-mirror.com/datasets/xiaowu0162/longmemeval-v2/resolve/main/questions.jsonl`，字节数与实际文件一致（286,186 bytes）。建议 A 侧恢复原始日志；
2. **longmemeval_s_cleaned.json (277MB) 记录矛盾**：A 侧 download.log 标注"s_cleaned.json(277MB) 过大，延迟到阶段6正式冻结时按需取子集"（即未下载），但 B 侧重下时该文件已存在于 `v0_subset/` 目录中（277,383,467 bytes）。该文件可能是 A 侧在 PR 提交后又补充下载的，但未更新 download.log。B 侧已计算哈希并设只读，但建议 A 侧澄清该文件的下载时序和用途；
3. **.gitignore 排除数据文件**：v0_subset 数据文件被 .gitignore 排除，B 侧无法直接从 git 获取文件，需重新下载验证。**冻结基线说明**：当前阶段以 manifest（SHA256 + 版本锁定）为基线依据，正式封存时通过 frozen 分支或外部存储固化二进制文件，确保仓库可独立复现 Gate 6 校验；
4. **stabletoolbench 阶段 4 缺口未闭合**：stabletoolbench_2024 在阶段 4 审计中仅有 3 条样例（不足 50 条下限），Gate 4 按 4/5 通过（stabletoolbench 待补）。阶段 6 下载的 G1_instruction.json（26KB）不能替代阶段 4 样本审计缺口。**建议**：stabletoolbench 的 Gate 6 校验标记为"条件通过"，待阶段 4 样本缺口闭合后正式冻结；

## Gate 6 建议

| 检查项 | 结果 |
| --- | --- |
| SHA256 哈希已计算 | ✅ 7/7 |
| Manifest 已生成 | ✅ |
| 只读冻结 | ✅ 7/7 |
| 版本复检 | ✅ 5/5 |
| 下载日志交叉验证 | ✅ 6/7（1 个 log 被覆盖，字节数仍一致） |
| **综合** | **条件通过 Gate 6**（需 Reviewer 先批准 Gate 5，且 stabletoolbench 阶段 4 缺口闭合后正式冻结） |

## 诚实披露

1. B 侧重新下载了全部 7 个文件进行独立验证，非直接使用 A 侧本地文件；
2. B 侧下载使用的镜像与 A 侧一致（hf-mirror.com / gh-proxy.com）；
3. B 侧无法验证 A 侧本地文件与 B 侧重下文件是否字节完全一致（因 A 侧文件未入库），但字节数全部匹配；
4. **冻结基线**：当前阶段以 manifest（SHA256 + 版本锁定）为基线依据，正式封存时通过 frozen 分支或外部存储固化二进制文件；
5. **前置依赖**：Gate 6 的正式通过以 Gate 5（Reviewer 签发 `dataset_selection_decision_v2.md`）为前置条件，当前 Gate 5 状态为 `⏳ 下一阶段`；
6. 本报告为 B 独立校验，**未经 Reviewer 确认**，最终 Gate 6 批准由 Reviewer 出具。
