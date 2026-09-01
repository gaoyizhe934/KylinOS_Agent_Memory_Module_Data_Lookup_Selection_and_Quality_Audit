# trec_tracks_2024 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31（Annotator B，v1.0 工作包）；2026-09-01 A 取用并入本证据包（feat/B-stage3-prep 分支）。
证据文件：`trec_data.html`（官方数据门户存档，本次并入）、`trec_page.html`（官方首页存档，v2.0 侧已有）、`nist_disclaimer_extracted.md`（NIST 版权与免责声明正文，本次并入）、`nist_disclaimer.html`（声明页原始存档，本次并入）。

## 可从原文直接确认的内容

- 正式名称：TREC（Text REtrieval Conference，NIST 主办）。
- 官方数据门户：https://trec.nist.gov/data.html（B 于 2026-08-31 直连 200 已存档；A 于 2026-09-01 复测 HTTP 200，见 `version_lock_20260901.md`）。
- data.html 页脚链接 NIST 官方 Copyrights & Disclaimers 页（https://www.nist.gov/disclaimer），正文已存档（`nist_disclaimer_extracted.md`）。
- NIST 声明关键句：部分材料/软件/数据**可能有其自身独立的 disclaimer**，需联系具体页面的 point of contact——即**每个 TREC Track 的数据条款独立，不能一概而论**。
- data.html 按年份列出各 Track 的 topics/qrels 入口。

## v2.0 重建取用记录（2026-09-01，A = Data Owner）

- 本报告主体取自 B 移交包，按移交说明取用规则择优保留；`trec_data.html`（数据门户）与 v2.0 已有 `trec_page.html`（首页）为不同页面，两者并存；`nist_disclaimer.html` / `nist_disclaimer_extracted.md` 已一并并入。
- 存档修订注记（移交说明 2026-09-01）：`nist_disclaimer.html` 第 47 行页面自带 Mapbox 公开访问令牌被 GitHub Push Protection 拦截，已替换为 `pk.[REDACTED_BY_PUSH_PROTECTION]`；该令牌为 NIST 网页前端第三方公开 key，非本项目凭据，打码不影响条款文本存档的完整性。
- 版本线索已锁定：见 `version_lock_20260901.md`（官方数据门户 2026-09-01 复测 HTTP 200；NIST 无单一 repo/release，Track 子集版本在选定后单独锁定）。

## 推断（需人工确认）

- TREC 是"系列会议评测集合"而非单一数据集（与手册 4.4 节"BPMN/TREC 这类标准或系列不能写成单一数据集"一致）；如需采用某 Track 数据，必须单独核验该 Track 页面条款。

## 待 Reviewer 决策

- 维持"方法论参考"定位：本项目仅参考其 qrels/评测协议设计，不直接采用其数据，无需进入 Gate 4 之后流程。
