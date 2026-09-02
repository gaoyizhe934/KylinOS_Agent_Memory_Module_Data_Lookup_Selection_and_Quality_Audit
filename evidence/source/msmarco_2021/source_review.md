# msmarco_2021 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31（Annotator B，v1.0 工作包）；2026-09-01 A 取用并入本证据包（feat/B-stage3-prep 分支）。
证据文件：`msmarco_page.html`（官网首页存档，105KB；v2.0 侧已有同名内容存档）、`msmarco_terms_extracted.md`（Terms 原文摘录，本次并入）、`paper_verification_20260901.md`（论文链接核验，v2.0 侧已有）。

## 可从原文直接确认的内容

- 正式名称：MS MARCO（Microsoft）。
- 官方站点：https://microsoft.github.io/msmarco/（B 于 2026-08-31 直连成功并存档首页；A 于 2026-09-01 复测 HTTP 200，见 `version_lock_20260901.md`）。
- Terms and Conditions 位于官网首页（原文已提取存档 `msmarco_terms_extracted.md`），并设"I agree to terms and conditions"勾选框——**数据下载需先同意条款**。
- 数据入口：首页提供 dataset 下载链接（点击同意后可见）；v2.0 登记的数据入口为 HF 官方 `microsoft/ms_marco`（revision 已锁定，见 `version_lock_20260901.md`）。
- 论文：arXiv:1611.09268（NIPS 2016，官方项目页引用，2026-09-01 核验，见 `paper_verification_20260901.md`）。

## 与此前登记表的差异

- v1.0 registry 中"Microsoft Research License/Notice 待核验"：**Terms 原文已捕获并存档**（`msmarco_terms_extracted.md`，2026-08-31）。
- v1.0 registry 中"官网访问失败"已过时，网络当时临时中断。

## v2.0 重建取用记录（2026-09-01，A = Data Owner）

- 本报告主体取自 B 移交包，按移交说明取用规则择优保留。
- `msmarco_index.html`（移交包内）与 v2.0 已有 `msmarco_page.html` 内容逐字节一致（MD5 相同），未重复取用。
- 版本线索已锁定：见 `version_lock_20260901.md`（HF microsoft/ms_marco revision `a47ee7aae8d7...` + 官网 HTTP 200）。

## 待 Reviewer 决策

- 维持"方法论参考（不采用）"定位：条款限制（见 `license_review.md`）使该集不适合本项目正式评测。
