# 阶段 3 证据核验报告（来源、版本与 License）— A 主体工作产出

- 分支：`feat/B-stage3-prep`（PR#7）
- 执行：A（Data Owner 角色授权，AI 辅助执行；最终批准权在 Reviewer）
- 日期：2026-09-01
- 说明：本报告覆盖阶段 3 主体工作——版本线索锁定、License 证据补齐、B 移交包取用。Gate 3 的最终裁决（允许试用/需确认/淘汰）须由 Reviewer 人工标记。

## 一、版本线索锁定（12/12 候选）

核验命令：`python scripts/audit/stage3_version_lock.py --fetch`（离线校验：不带参数运行，退出码 0）
核验时点：2026-09-01 20:41~20:43（Asia/Shanghai）
产出：每候选 `version_lock_20260901.md` + `api_snapshot_20260901/`（API 关键字段 JSON 存档）

| 数据集 | GitHub commit | HF revision / Web | License（证据级） |
| --- | --- | --- | --- |
| longmemeval_cleaned_2025 | 9e0b455f（main，2026-05-11） | 98d7416c（2025-09-19） | MIT（LICENSE 原文） |
| longmemeval_v2_2026 | 2cc8c540（main） | f152293e | Apache-2.0（LICENSE 原文） |
| stabletoolbench_2024 | aa4ed9f4（master） | — | Apache-2.0（LICENSE 原文） |
| toolbench_2024 | d56fdd89（master） | — | Apache-2.0（LICENSE 原文 + README 附加声明） |
| t2ranking_2023 | 3ab0a0de（main，2023-07-03） | 2a369a43（2025-03-06） | Apache-2.0（HF 卡片声明 + 标准文本存档） |
| dureader_retrieval_2022 | c625076b（DuReader）+ e2bfcfcf（RocketQA） | — | **待核验**（见三.1） |
| multiwoz_2_2_2020 | fe0c8e65（master） | — | MIT（LICENSE 原文） |
| personachat_2018 | a29567f7（master） | tgz SHA-256 507cf864...（build.py 存档） | **数据无明确许可**（框架 MIT 不覆盖数据） |
| msmarco_2021 | — | a47ee7aa + 官网 HTTP 200 | Microsoft Terms 原文（非商业限定） |
| trec_tracks_2024 | — | data.html HTTP 200 | NIST 免责声明原文（Track 条款独立） |
| bpmn_2_0_2013 | — | PDF 入口 HTTP 200 | OMG 规范文档号 formal/2013-12-09 |
| machine_unlearning_bench_2025 | — | 86afcc8b | MIT（HF 卡片 + README） |

- 版本锁定语义：SHA 为 2026-09-01 核验时点的官方状态，作为阶段 6「再次下载可得到同一版本」的验收基线；复测 SHA 变化时追加新日期锁文件并交 Reviewer 裁决。
- personachat_2018 附加证据：官方 tgz 的 SHA-256 由 ParlAI 源码 `personachat_build.py` 存档（B 移交包），为 12 候选中唯一具有**数据文件级哈希**的版本线索。

## 二、B 移交包取用记录（按移交说明取用规则）

| 数据集 | 取用文件 | 择优处理 |
| --- | --- | --- |
| msmarco_2021 | msmarco_terms_extracted.md | review 采用 B 深度版；index.html 与已有 page.html 逐字节一致（MD5 相同），未重复取用 |
| personachat_2018 | parlai_LICENSE、personachat_build.py | review 采用 B 深度版（补齐"数据下载页未确认/版本待核验"两处缺口） |
| t2ranking_2023 | t2ranking_HF_card.py | review 采用 B 深度版；旧版 hf_api_metadata（无 revision）被新 api_snapshot 取代 |
| toolbench_2024 | toolbench_LICENSE | review 采用 B 深度版 + 结论对齐 Reviewer 裁决（方法论参考）；README 与已有版一致未重复取用 |
| trec_tracks_2024 | nist_disclaimer.html、nist_disclaimer_extracted.md、trec_data.html | review 采用 B 深度版；trec_data.html（数据门户）与已有 trec_page.html（首页）为不同页面并存 |
| dailydialog_2017 | （未登记候选） | 移入 `evidence/source_unregistered/` 暂存，不参与 Gate 验收；启用须先走阶段 2 登记流程 |
| locomo_2024 | （未登记候选） | 同上 |

- 移交目录 `evidence/source_workpack_handover/` 已按移交规则删除；原始移交说明存档于 `evidence/source_unregistered/README_移交说明.md`。
- 所有并入文件的 review 均含「取用与更新记录」小节，保留 B 核验（2026-08-31）与 A 取用（2026-09-01）的双时间线。

## 三、遗留项（需 Reviewer 决策）

1. **dureader_retrieval_2022 License 缺失**：baidu/DuReader 仓库无 LICENSE 文件（GitHub API `/license` 端点 2026-09-01 返回 404）；RocketQA 仓库为 Apache-2.0 但仅覆盖代码仓库，不覆盖 DuReader 数据本体。数据发布渠道（千言/LUGE）条款需人工注册核验。**建议**：Gate 3 标记「需确认」。
2. **t2ranking_2023 许可声明形式**：GitHub 仓库无独立 LICENSE 文件，许可仅以 HF 官方卡片字段声明（THUIR 官方组织账号发布，与 GitHub 同一发布者）。是否接受卡片声明作为合规证据，由 Reviewer 决定。
3. **machine_unlearning_bench_2025**：B 复核意见（2026-09-01）——发布者为社区组织而非论文官方渠道，建议 Gate 3 从严标记「需确认」。
4. **locomo_2024**（未登记，暂存 source_unregistered）：B 核验显示数据在官方仓库内可直连下载（CC BY-NC 4.0），是长期对话记忆的天然候选；如 Reviewer 认为值得启用，须先补阶段 2 登记卡。
5. **A+B 双角色说明**：用户已获 A（Data Owner）与 B（Annotator）双授权。B 侧产出（移交包、复核报告）与 A 侧产出（本报告版本锁定与取用）在时间线与文件上均可区分；**独立性受损**，Gate 3 审批必须由 Reviewer（gaoyizhe）独立复核，不接受 A/B 角色互批。

## 四、Gate 3 验收命令

```
python scripts/audit/stage3_version_lock.py        # 离线校验（CI 已接入），退出码 0 = 12 候选版本线索齐备
python scripts/oneclick/stage2_check_urls.py       # URL 复测（严格模式），退出码 0
```

CI 接入：`.github/workflows/baseline-validation.yml` 新增「校验阶段3版本线索存档」步骤。

## 五、登记表更新

- `version` 字段：12 行全部更新为带 SHA 的锁定记录（指向各证据包 version_lock_20260901.md）
- `license` 字段：5 行更新（msmarco/personachat/toolbench/trec/dureader——由"待核验"更新为有证据支撑或明确说明缺口）
- 其余字段未动（阶段 2 产出，阶段 3 仅核验 version/license 语义）
