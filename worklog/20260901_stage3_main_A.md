# 2026-09-01 阶段 3 主体工作日志（A = Data Owner 授权，feat/B-stage3-prep）

## 背景

用户于 2026-09-01 获得计划手册中 A（Data Owner）的全部授权，A 的阶段 3 主体工作（版本线索锁定 + License 证据补齐 + B 移交包取用）在 feat/B-stage3-prep 分支（PR#7）执行。执行前 PR#7 / PR#3 均为 open 等待 Reviewer 批准，master 无新动态。

## 完成事项

### 1. 版本线索锁定脚本（scripts/audit/stage3_version_lock.py）

- 双模式：`--fetch` 在线抓取（GitHub REST API v3 默认分支 HEAD commit + HF Hub API revision + Web 入口 HTTP 状态）；默认离线校验（CI 验收，退出码 0/1）
- 产出：12 候选各 1 份 `version_lock_20260901.md` + `api_snapshot_20260901/`（API 关键字段 JSON 存档，files[].patch 等大字段裁剪并注明）
- `--only <dataset_id>` 参数支持失败重试（首次运行 personachat_2018 触发 GitHub API 403 rate limit，单独重试成功）
- 写出统一 LF 行尾（open + lineterminator 显式 '\n'，吸取 stage4 CRLF 教训）

### 2. 版本锁定结果（12/12）

| 候选 | 锁定内容 |
| --- | --- |
| longmemeval_cleaned_2025 | GH 9e0b455f + HF 98d7416c |
| longmemeval_v2_2026 | GH 2cc8c540 + HF f152293e |
| stabletoolbench_2024 | GH aa4ed9f4 |
| toolbench_2024 | GH d56fdd89 |
| t2ranking_2023 | GH 3ab0a0de + HF 2a369a43 |
| dureader_retrieval_2022 | DuReader c625076b + RocketQA e2bfcfcf |
| multiwoz_2_2_2020 | GH fe0c8e65 |
| personachat_2018 | GH a29567f7 + tgz SHA-256（build.py 存档） |
| msmarco_2021 | HF a47ee7aa + 官网 200 |
| trec_tracks_2024 | data.html HTTP 200 |
| bpmn_2_0_2013 | OMG formal/2013-12-09 + PDF 入口 200 |
| machine_unlearning_bench_2025 | HF 86afcc8b |

### 3. B 移交包取用（按移交说明规则）

- 5 个已登记候选（msmarco/personachat/t2ranking/toolbench/trec）证据择优并入 `evidence/source/`：新增 8 个原始文件（terms 提取、parlai LICENSE、build.py、toolbench LICENSE、NIST 声明×2、trec_data.html、HF card.py）
- review 文件合并：以 B 深度核验版为主体 + 新增「取用与更新记录」小节（双时间线：B 2026-08-31 / A 2026-09-01）
- toolbench 结论由 B 草稿「补充候选」更新为 Reviewer 裁决后的「方法论参考（不采用）」
- 2 个未登记候选（dailydialog/locomo）移入 `evidence/source_unregistered/` 暂存，移交目录删除，原始移交说明一并存档

### 4. License 遗留核验

- dureader_retrieval_2022：GitHub API 实测 baidu/DuReader 无 LICENSE 文件（404）；RocketQA 仓库 Apache-2.0 不覆盖数据本体 → 登记表明确标注待核验缺口
- personachat_2018：确认「数据无明确许可，框架 MIT 不覆盖数据」双证据源结论

### 5. 登记表与 CI

- `registry/dataset_registry.csv`：version 12 行全部更新为 SHA 锁定记录；license 5 行更新为证据支撑描述
- `.github/workflows/baseline-validation.yml` 新增「校验阶段3版本线索存档」步骤（离线校验，不依赖网络）

### 6. 报告与 Gate 状态

- 新增 `reports/stage3_evidence_report.md`（版本锁定表 + 取用记录 + 遗留项 5 项待 Reviewer 决策）
- 更新 `reports/gate_status.md`（Gate 3 进度）

## 遗留项（待 Reviewer）

1. dureader License 缺失（建议「需确认」）
2. t2ranking 卡片声明形式是否可接受
3. machine_unlearning_bench 发布者身份（B 复核建议从严）
4. locomo 是否补登记启用
5. A+B 双角色独立性说明（见报告三.5；Gate 3 必须由 Reviewer 独立复核）

## 环境与命令

- Windows 11（PowerShell）；Python 3.10
- 抓取：`python scripts/audit/stage3_version_lock.py --fetch`（GitHub API 未认证限额 60/h，首次 personachat 403 后 `--only personachat_2018` 重试成功）
- 校验：`python scripts/audit/stage3_version_lock.py` → 退出码 0（12/12 OK）
- 分支：feat/B-stage3-prep（PR#7，阶段 3 内容按「一个阶段一个 PR」规则全部进本 PR）
