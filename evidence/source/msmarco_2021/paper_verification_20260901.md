# msmarco_2021 论文链接核验证据

- 核验人: B = DGXD01（Annotator B）
- 核验日期: 2026-09-01
- 核验背景: PR#1 审批意见将「msmarco_2021 登记表 paper 字段为『待核验』」列为 Gate 3 前待办，本文档为清偿该待办的证据存档。

## 1. 核验结论

| 项目 | 内容 |
| --- | --- |
| 论文标题 | MS MARCO: A Human Generated MAchine Reading COmprehension Dataset |
| 论文链接 | https://arxiv.org/abs/1611.09268 （官方项目页引用形式: https://arxiv.org/pdf/1611.09268.pdf） |
| 作者 | Payal Bajaj, Daniel Campos, Nick Craswell, Li Deng, Jianfeng Gao, Xiaodong Liu, Rangan Majumder, Andrew McNamara, Bhaskar Mitra, Tri Nguyen, Mir Rosenberg, Xia Song, Alina Stoica, Sauraj Tiwary, Tong Wang（Microsoft） |
| 发表 | NIPS 2016（项目页原文: "Starting with a paper released at NIPS 2016"）；arXiv v1 提交 2016-11-28，v3 修订 2018-10-31 |
| 可达性 | 2026-09-01 实测 HTTP 200，摘要页与 PDF 均可访问 |
| 链接来源 | 官方项目页 https://microsoft.github.io/msmarco/ 首段直接引用该 arXiv 链接（发布者 = Microsoft，与登记表 publisher 一致） |

## 2. 来源交叉印证

1. **官方项目页**（microsoft.github.io/msmarco）首段: "Starting with a paper released at NIPS 2016" → 链接指向 arxiv.org/pdf/1611.09268.pdf，与登记表 official_url 同源；
2. **arXiv 摘要页**（arxiv.org/abs/1611.09268）: 标题、作者列表、摘要内容（1,010,916 问题 / 8,841,823 段落的规模描述）与项目页描述一致；
3. **DBLP 收录**: dblp.uni-trier.de 收录 corr1611 条目，作者列表一致。

## 3. 登记表更新

`registry/dataset_registry.csv` 中 msmarco_2021 的 paper 字段由「待核验」更新为:
`arXiv:1611.09268（NIPS 2016，官方项目页引用，2026-09-01 核验）`

## 4. 备注

- 本核验仅确认论文链接的有效性与出处（来源核验层面），**不改变 msmarco_2021 的 conclusion**（方法论参考/不采用，Terms 限定非商业研究用途，该限制仍由阶段 3 License 审查层面持有）；
- 论文许可为 arXiv 非独占分发许可（nonexclusive-distrib/1.0），与数据集 Terms 分属不同对象，互不影响。
