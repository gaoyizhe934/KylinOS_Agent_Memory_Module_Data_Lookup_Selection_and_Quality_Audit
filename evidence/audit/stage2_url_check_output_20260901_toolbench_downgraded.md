========== 现有数据集 URL 可访问性检查 ==========
登记表: registry\dataset_registry.csv
数据集总数: 12
验收范围: 全部数据集的 official_url（来源核验必备）; data_url 仅验收正式候选,
          conclusion 标记「方法论参考」的数据集不要求数据可获取（Reviewer PR#1 裁决语义）

| 数据集 | 官方URL | 状态 | 下载URL | 状态 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | https://github.com/xiaowu0162/LongMemEval | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmem | OK:200 |
| longmemeval_v2_2026 | https://github.com/xiaowu0162/LongMemEval-V2 | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmem | OK:200 |
| stabletoolbench_2024 | https://github.com/THUNLP-MT/StableToolBench | OK:200 | https://github.com/THUNLP-MT/StableToolBench | OK:200 |
| toolbench_2024 | https://github.com/OpenBMB/ToolBench | OK:200 | https://drive.google.com/drive/folders/1TysbSWYpP8 | SKIPPED:方法论参考, 数据入口不验收 |
| t2ranking_2023 | https://github.com/THUIR/T2Ranking | OK:200 | https://huggingface.co/datasets/THUIR/T2Ranking | OK:200 |
| dureader_retrieval_2022 | https://github.com/baidu/DuReader/tree/master/DuRe | OK:200 | https://github.com/PaddlePaddle/RocketQA/tree/main | OK:200 |
| multiwoz_2_2_2020 | https://github.com/budzianowski/multiwoz/tree/mast | OK:200 | https://github.com/budzianowski/multiwoz | OK:200 |
| personachat_2018 | https://github.com/facebookresearch/ParlAI | OK:200 | http://parl.ai/downloads/personachat/personachat.t | OK:200 |
| msmarco_2021 | https://microsoft.github.io/msmarco/ | OK:200 | https://huggingface.co/datasets/microsoft/ms_marco | SKIPPED:方法论参考, 数据入口不验收 |
| trec_tracks_2024 | https://trec.nist.gov/ | OK:200 | https://trec.nist.gov/data.html | SKIPPED:方法论参考, 数据入口不验收 |
| bpmn_2_0_2013 | https://www.omg.org/spec/BPMN/ | OK:200 | https://www.omg.org/spec/BPMN/2.0/PDF | OK:200 |
| machine_unlearning_bench_2025 | https://huggingface.co/datasets/machine-unlearning | OK:200 | https://huggingface.co/datasets/machine-unlearning | OK:200 |

统计（12 个数据集 x 官方/下载两列，共 24 项）: OK=21  EMPTY=0  ERROR=0  TIMEOUT=0  SKIPPED=3
说明: OK=可访问, EMPTY=登记表未填写该 URL, ERROR=不可访问, TIMEOUT=超时, SKIPPED=方法论参考候选的 data_url 不验收
不验收 data_url 的方法论参考候选: toolbench_2024, msmarco_2021, trec_tracks_2024

结论: PASS —— 全部 URL 均可访问
