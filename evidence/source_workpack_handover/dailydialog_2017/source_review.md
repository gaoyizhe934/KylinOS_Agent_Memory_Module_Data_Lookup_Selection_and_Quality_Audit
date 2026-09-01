# dailydialog_2017 来源核验报告（AI 草稿，供 Reviewer 审查）

核验时间：2026-08-31。证据文件：`dailydialog_license_crosscheck.md`（本次新增）。

## 可从原文直接确认的内容

- 正式名称：DailyDialog（Li et al., ACL-IJCNLP 2017）。
- 官方站点：http://yanran.li/dailydialog/。
- **官方下载现状（本次实测）**：`http://yanran.li/files/ijcnlp_dailydialog.zip` 返回的是 JS 指纹反爬拦截页（1.1KB HTML，非 zip），与 registry v1.0 记录的"安全软件拦截"结论不同——**根因是站点反爬，不是本地安全软件**。已按手册失败路由改为论文 + 镜像交叉定位。
- 交叉印证（证据已存档）：HF 镜像 `li2017dailydialog/daily_dialog`（downloads=5166，卡片含 emotion/dialog-act 标签，与论文任务一致）与 `ConvLab/dailydialog`（ConvLab 为清华 CoAI 机构镜像）**两个独立来源一致声明 license = cc-by-nc-sa-4.0**。
- 规模：13K 对话（论文声明）；HF 卡片 size_categories: 10K<n<100K 相符。

## 推断（需人工确认）

- 两个独立镜像 + 机构镜像一致，推断数据许可为 CC BY-NC-SA 4.0（署名-非商业-相同方式共享）。
- 数据本体如需下载：HF 镜像 `li2017dailydialog/daily_dialog` 的原始 txt 文件可经 hf-mirror 获取；**正式采用前建议联系作者（论文页邮箱）确认官方分发渠道**。

## 待 Reviewer 决策

- 恢复"补充候选"地位（此前因下载阻塞暂缓）：允许试用与否、是否值得为 13K 闲聊数据投入（本集仅作闲聊负样本辅助）。
