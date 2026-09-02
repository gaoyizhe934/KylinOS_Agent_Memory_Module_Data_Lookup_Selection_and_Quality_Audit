# 阶段4 人工抽检记录（Annotator A = lyf-1213）

日期：2026-09-02
触发：B 审计脚本结构检查通过后（异常 211→3），按手册阶段4 要求进行人工抽检标签可解释性。

## 一、审计复跑结果（同步 PR#17 ID 修复后）

| 数据集 | 记录数 | 唯一ID | 异常数 | 结论 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | 100 | 100 | 2 | 结构通过 |
| longmemeval_v2_2026 | 100 | 100 | 1 | 结构通过 |
| multiwoz_2_2_2020 | 100 | 100 | 0 | 结构通过 |
| stabletoolbench_2024 | 目录不存在 | 0 | 0 | 样本未补（Low-3） |
| t2ranking_2023 | 100 | 100 | 0 | 结构通过 |

异常 3 条（高 0 / 中 0 / 低 3）：longmemeval_cleaned email×2（低危）、longmemeval_v2 null_string×1。

## 二、人工抽检：标签可解释性

从各数据集 manual_review 清单抽样，检查"gold 标签能否从 evidence 语义推导"。

### longmemeval_cleaned_2025 ✅
| sample_id | question_type | 抽检结论 |
| --- | --- | --- |
| 031748ae | knowledge-update | ✅ question 可从 2 会话（12 turns）推导 answer |
| 60472f9c | multi-session | ✅ answer 可从 3 会话推导 |
| b46e15ed | temporal-reasoning | ✅ answer 可从 4 会话推导 |
| gpt4_2312f94c | temporal-reasoning | ✅ answer 可从 2 会话推导 |
| 0bc8ad93 | temporal-reasoning | ✅ answer 可从 3 会话推导 |

### longmemeval_v2_2026 ✅
| sample_id | question_type | 抽检结论 |
| --- | --- | --- |
| 499488a6 | static-environment | ✅ answer + eval_function 可判定 |
| 7586cf7c | errors-gotchas | ✅ answer + llm_gotchas_checker 可判定 |
| 87711b62 | dynamic-environment | ✅ answer + norm_phrase_set_match 可判定 |

### 标签可解释性结论
- **longmemeval_cleaned / longmemeval_v2**：标签可由证据语义推导，且有 eval_function 判定规则 ✅
- **multiwoz / t2ranking**：为辅助数据，标签即对话本体/查询文本，无需额外推导 ✅

## 三、DailyDialog 下载包被拦截问题核验

| 检查项 | 结果 |
| --- | --- |
| 官方页 http://yanran.li/dailydialog/ | HTTP 200（页面可达） |
| 下载 zip http://yanran.li/files/ijcnlp_dailydialog.zip | HTTP 200 |
| 实际下载 | **980 bytes，为 HTML 停车页（`<!DOCTYPE html>`），非 zip（无 PK 头）** |

**结论**：域名 yanran.li 返回 200 但**下载链接实际返回的是 HTML 停车/占位页**（与之前核验一致），**不是有效 zip**。DailyDialog 官方下载渠道已失效，无法下载。该数据集本已降级为"仅补充候选"，数据不可获取。若需使用，须找官方镜像/存档（如 HF 上第三方转载），但需重新核验来源与 License。

## 四、Gate 4 结论（供 Reviewer）

- ✅ 样本可解析：4 个允许试用数据集全部结构解析通过（各 100 条）
- ✅ 标签定义可理解：人工抽检 longmemeval_cleaned/v2 标签可由证据推导
- ⚠️ 未命中否决项：剩 email×2 低危 + null_string×1，属合成数据常见，需 Reviewer 判真伪
- ⚠️ stabletoolbench 样本未补（Low-3），DailyDialog 下载失效

## 五、待办

- [ ] stabletoolbench 样本补齐（Low-3）
- [ ] Reviewer 确认 email/null_string 低危异常处置
- [ ] DailyDialog 如需使用，寻官方存档并重核 License
- [ ] Reviewer Gate 4 批准