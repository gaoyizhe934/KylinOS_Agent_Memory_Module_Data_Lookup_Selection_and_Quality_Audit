# 2026-09-01 阶段 3 准备工作日志（B = DGXD01，feat/B-stage3-prep）

## 背景

PR#1（阶段 0-2）已由 Reviewer（gaoyizhe）批准合并，Gate 0/1/2 关闭，阶段 3 获准启动。PR#1 审批意见第四节遗留三项 Gate 3 前待办，本分支（feat/B-stage3-prep，基于最新 master）逐一清偿，并并入 B 侧 License 证据移交包。

## 完成事项

### 1. toolbench_2024 降级执行（Reviewer 裁决落地）

- 登记表 `conclusion`: 「补充候选（数据入口失效，待裁决）」→「方法论参考（不采用。Reviewer 裁决 2026-09-01: 官方数据入口失效，降级为方法论参考，不进入首版封存；依据 PR#1 审批意见第四节第 4 条）」
- `known_issues` 同步补充裁决记录
- `scripts/oneclick/stage2_check_urls.py` 增强: conclusion 以「方法论参考」开头的数据集，其 data_url 标记 SKIPPED 不计入验收（official_url 仍验收——来源核验不受降级影响）。SKIPPED 状态在输出表格、统计行、说明行中均可见，不静默
- 复跑严格模式: **退出码 0**（OK=21, SKIPPED=3: toolbench_2024 / msmarco_2021 / trec_tracks_2024，EMPTY=0 ERROR=0 TIMEOUT=0）——Reviewer 要求「届时退出码应转为 0」达成
- 输出存档: `evidence/audit/stage2_url_check_output_20260901_toolbench_downgraded.md`
- 注: msmarco_2021 与 trec_tracks_2024 在 master 上 conclusion 已是「方法论参考」，本次脚本语义增强使它们的失效/受限数据入口同样不再阻塞验收——与 Reviewer 对 toolbench 的裁决语义一致

### 2. msmarco_2021 论文链接核验

- 官方项目页（microsoft.github.io/msmarco）首段引用 → arXiv:1611.09268（NIPS 2016，MS MARCO 原始论文，Bajaj et al., Microsoft）
- arXiv 摘要页 2026-09-01 实测可达（HTTP 200）；标题/作者/规模描述与项目页交叉印证一致；DBLP 收录一致
- 登记表 `paper`: 「待核验」→「arXiv:1611.09268（NIPS 2016，官方项目页引用，2026-09-01 核验）」
- 证据: `evidence/source/msmarco_2021/paper_verification_20260901.md`

### 3. machine_unlearning_bench_2025 证据补齐（B 复核报告 F1 项）

- 证据目录从零建立（此前 evidence_dir 悬空，F1 不合格项）:
  - `hf_card_check_output_20260901.txt` — 仓库自带核查脚本的完整输出（复现 A 的核查过程）
  - `hf_dataset_metadata_20260901.json` — HF API 元数据，`cardData.license = "mit"`（siblings 32881 条文件列表剥离为独立文件 `hf_file_list_20260901.txt`，元数据从 3MB 精简至 1.3KB）
  - `hf_README_raw_20260901.md` — README 原文（YAML front-matter 再次声明 license: mit）
  - `license_review.md` — B 侧审查结论草稿 + 复核意见（发布者为社区组织而非论文官方渠道，建议 Gate 3 从严标记「需确认」；训练数据遗忘基准 ≠ OS Agent 记忆遗忘，仅方法参考）

### 4. B 侧移交包并入

- `evidence/source_workpack_handover/`（31 文件，7 个数据集）从 b-review-stage12 分支 checkout 并入:
  dailydialog_2017 / locomo_2024 / msmarco_2021 / personachat_2018 / t2ranking_2023 / toolbench_2024 / trec_tracks_2024
- 含 License 原文（locomo LICENSE.txt、parlai LICENSE、toolbench LICENSE、NIST disclaimer）、HF 卡片存档、交叉核验与审查报告——阶段 3 证据包组装的直接素材

### 5. gate_status.md 更新

- Gate 0/1/2 标记为 Reviewer 已批准（PR#1）
- Gate 3 标记为进行中，新增「Gate 3 待办清偿记录」表（三项待办 + 移交包并入）

## 环境与命令

- 操作系统: Windows 11（PowerShell）；Python 3.10
- 复核/验收命令:
  - `python scripts/oneclick/stage2_check_urls.py`（严格模式，退出码 0）
  - HF API: `https://huggingface.co/api/datasets/machine-unlearning-bench/data-unlearning-bench`
- 分支: feat/B-stage3-prep（基于 origin/master b1b0c23）
