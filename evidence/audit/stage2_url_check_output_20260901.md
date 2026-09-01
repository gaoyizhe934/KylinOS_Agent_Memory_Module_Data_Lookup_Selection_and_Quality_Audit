
# 阶段 2 URL 可访问性检查 — 原始输出存档

- 日期: 2026-09-01
- 命令: python scripts/oneclick/stage2_check_urls.py（仓库根目录执行）
- 环境: Windows 11, Python 3.12, 直连（未使用代理，遵循环境变量）, TLS 证书校验开启
- 脚本版本: 修正版（路径从仓库根目录解析，代理为可选配置）
========== 现有数据集 URL 可访问性检查 ==========
登记表: registry\dataset_registry.csv
数据集总数: 12

| 数据集 | 官方URL | 状态 | 下载URL | 状态 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | https://github.com/xiaowu0162/LongMemEval | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmem | OK:200 |
| longmemeval_v2_2026 | https://github.com/xiaowu0162/LongMemEval-V2 | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmem | OK:200 |
| stabletoolbench_2024 | https://github.com/THUNLP-MT/StableToolBench | OK:200 | https://github.com/THUNLP-MT/StableToolBench | OK:200 |
| toolbench_2024 | https://github.com/OpenBMB/ToolBench | OK:200 |  | EMPTY:无URL |
| t2ranking_2023 | https://github.com/THUIR/T2Ranking | OK:200 | https://huggingface.co/datasets/THUIR/T2Ranking | OK:200 |
| dureader_retrieval_2022 | https://github.com/baidu/DuReader/tree/master/DuRe | OK:200 | https://github.com/PaddlePaddle/RocketQA/tree/main | OK:200 |
| multiwoz_2_2_2020 | https://github.com/budzianowski/multiwoz/tree/mast | OK:200 | https://github.com/budzianowski/multiwoz | OK:200 |
| personachat_2018 | https://github.com/facebookresearch/ParlAI | OK:200 |  | EMPTY:无URL |
| msmarco_2021 | https://microsoft.github.io/msmarco/ | OK:200 |  | EMPTY:无URL |
| trec_tracks_2024 | https://trec.nist.gov/ | OK:200 |  | EMPTY:无URL |
| bpmn_2_0_2013 | https://www.omg.org/spec/BPMN/ | OK:200 |  | EMPTY:无URL |
| machine_unlearning_bench_2025 | https://huggingface.co/datasets/machine-unlearning | OK:200 | https://huggingface.co/datasets/machine-unlearning | OK:200 |

统计（12 个数据集 x 官方/下载两列，共 24 项）: OK=19  EMPTY=5  ERROR=0  TIMEOUT=0
说明: OK=可访问, EMPTY=登记表未填写该 URL（不代表可访问）, ERROR=不可访问, TIMEOUT=超时
注意: 部分站点对自动化请求返回 403/429，不一定代表数据不可用，需人工确认。

