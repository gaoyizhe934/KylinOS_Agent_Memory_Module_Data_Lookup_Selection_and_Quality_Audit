# personachat_2018 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31（Annotator B，v1.0 工作包）；2026-09-01 A 取用并入本证据包（feat/B-stage3-prep 分支）。
证据文件：`parlai_LICENSE`（MIT）、`personachat_build.py`（含官方下载 URL 与 SHA-256）。

## 可从原文直接确认的内容

- 正式名称：PersonaChat（ParlAI 任务 personachat）。
- 官方发布者：Facebook AI Research；数据经 ParlAI 框架分发。
- **官方数据 URL**：`https://parl.ai/downloads/personachat/personachat.tgz`（302 → `https://dl.fbaipublicfiles.com/parlai/personachat/personachat.tgz`），实测国内直连可达（CloudFront 香港节点），213MB，Last-Modified 2019-01-17。
- **官方 SHA-256**（写在 ParlAI 源码 `parlai/tasks/personachat/build.py` 中，已存档本包 `personachat_build.py`）：`507cf8641d333240654798870ea584d854ab5261071c5e3521c20d8fa41d5622`。
- 论文：arXiv:1801.07243（ParlAI 页面引用）。
- ParlAI 项目页声明（原文大意）：页面 2020-08 归档，"You may continue to use the data without issue"。

## License 核验结论（两个独立证据源）

- `parlai_LICENSE`（MIT）**仅覆盖 ParlAI 框架代码，不覆盖数据**：tar 包内无 LICENSE/README（经 tar 条目清单验证）。
- 数据本身**无明确许可**：论文无数据许可声明；HF 官方旧目录对 PersonaChat 系数据（conv_ai_2）标注 `licenses: unknown`。
- HF 镜像 `awsaf49/persona-chat`（21 个与官方 tar 同名文件，内容比对一致）卡片自称 MIT，但仓库内无 LICENSE 文件 → 转存者推断，**不可作为许可证据**。

## 推断（需人工确认）

- 数据经 FAIR 官方 CDN 持续分发且带 SHA-256，可推断官方允许研究使用；但无条款授权再分发/商用。
- 本项目定位"偏好辅助、不进首版封存"，使用风险主要在再分发环节。

## v2.0 重建取用记录（2026-09-01，A = Data Owner）

- 本报告主体取自 B 移交包（原 `evidence/source_workpack_handover/personachat_2018/`，2026-08-31 核验），按移交说明取用规则择优保留（较 v2.0 占位版信息更全，v2.0 版"数据下载页未确认/版本待核验"两处缺口由本版补齐）。
- 版本线索已锁定：见 `version_lock_20260901.md`（GitHub facebookresearch/ParlAI master commit `a29567f7ce76`；官方 tgz 入口 2026-09-01 复测 HTTP 200）。
- 数据 SHA-256 由 `personachat_build.py` 存档（见上），供阶段 6 可重复下载验收直接使用。

## 待 Reviewer 决策

- 维持"补充候选（不进入首版封存）"，登记为"License 未明确（研究使用；框架 MIT 不覆盖数据）"。
