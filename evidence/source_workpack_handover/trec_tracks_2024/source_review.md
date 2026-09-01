# trec_tracks_2024 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31。证据文件：`trec_data.html`（官方数据门户存档）、`nist_disclaimer_extracted.md`（NIST 版权与免责声明正文）。

## 可从原文直接确认的内容

- 正式名称：TREC（Text REtrieval Conference，NIST 主办）。
- 官方数据门户：https://trec.nist.gov/data.html（本次直连 200，已存档）。
- data.html 页脚链接 NIST 官方 Copyrights & Disclaimers 页（https://www.nist.gov/disclaimer），正文已存档。
- NIST 声明关键句：部分材料/软件/数据**可能有其自身独立的 disclaimer**，需联系具体页面的 point of contact——即**每个 TREC Track 的数据条款独立，不能一概而论**。
- data.html 按年份列出各 Track 的 topics/qrels 入口。

## 推断（需人工确认）

- TREC 是"系列会议评测集合"而非单一数据集（与手册 4.4 节"BPMN/TREC 这类标准或系列不能写成单一数据集"一致）；如需采用某 Track 数据，必须单独核验该 Track 页面条款。

## 待 Reviewer 决策

- 维持"方法论参考"定位：本项目仅参考其 qrels/评测协议设计，不直接采用其数据，无需进入 Gate 4 之后流程。
