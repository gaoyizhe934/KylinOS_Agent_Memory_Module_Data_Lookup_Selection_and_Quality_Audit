# 阶段8 P1 执行任务清单（FROZEN 触发，新 PR 批次）— 2026-09-04

## 0. 前置闸口（唯一阻塞）
- [ ] #7 KMA→FROZEN：主仓库 D/E 签署 + PR 合并（协调方在主仓库推进，数据包仓库等信号）。
- [ ] 触发确认：主仓库 FROZEN 记录/权威副本入库更新后，启动 P1。

## P1 批次（每批独立 PR，独立 review/合并；不再堆积 #27）

### 批次 P1-1 · Schema 权威收口（A+B）
- [ ] schema.json / enum_dictionary.json 按权威候选 FROZEN 最终收口（状态切换、补缺键、检索 ref=memory_id+version_id、eval_ 前缀标注）；
- [ ] 校验适配：schema_drift_check / schema 校验 exit 0；enum 无越界；
- [ ] 报告：收口对照 + 校验输出；PR→Reviewer。

### 批次 P1-2 · 标注手册 v2 定稿（A，B 复核）
- [ ] 手册 v2 “裁定落点版”→ 定稿（去草案措辞，核对 §3/§4/§5/§6/§9/§11，引用 registry 单源与权威候选）；
- [ ] A/B 双核 + Reviewer 批准；labels 骨架字段与手册一致。

### 批次 P1-3 · 全量重转 processed（A 转换 + B 校验）
- [ ] convert 脚本 KMA 化后由 raw/interim 原文重转（raw 只读、evidence 不动、禁 mock）；
- [ ] 对账：条数/字段/枚举 canonical、timestamp UTC ms、raw_id 溯源、幂等；校验 exit 0；
- [ ] 报告 conversion_report 更新；PR→Reviewer。

### 批次 P1-4 · labels_A/B v2 骨架落地（B）
- [ ] 按 registry 单源字段集 + 手册 v2 生成 labels_A/B_trial_v2 骨架（样本池沿用，48 条口径）;
- [ ] 覆盖/字段/evidence 校验（schema_drift_check / label_check 适配）exit 0；PR→Reviewer。

### 批次 P1-5 · 试标 v2（A+B 独立）
- [ ] trial set v2 生成并固定；
- [ ] A/B 独立标注 48 条（禁先讨论答案）→ 各自提交 labels_A/B_trial_v2.jsonl；
- [ ] 提交前 label_check（只交自己文件）。

### 批次 P1-6 · Kappa 与放行（B + Reviewer）
- [ ] B 跑 stage8_kappa.py --format kma（registry 单源）→ 总体+分层 Kappa≥0.70、分歧聚类；
- [ ] Reviewer 放行 8.2；未达标→修订手册/规则并回溯。

## 阶段8 后续（P1 之后，独立批次）
- [ ] 8.2 候选草稿生成（A）+ 结构化/enum 校验（B）→ Reviewer 放行；
- [ ] 8.3 双人独立标注全量 + 裁决（Reviewer）→ gold_draft/disagreement_log；
- [ ] Gate 8 收口（Kappa≥0.70 / 分歧有裁决 / 全标签 evidence）→ 关闭 Gate 8。

## 验证总纲
- 每批完成跑对应校验/测试并附 exit code；批次合并独立（Low-2 分批纪律）。
