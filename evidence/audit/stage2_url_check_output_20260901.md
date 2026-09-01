# 阶段 2 URL 可访问性检查输出存档

- 存档时间: 2026-09-01（第二轮复审修复后复跑，登记表 5 项 data_url 补齐后）
- 命令: `python scripts/oneclick/stage2_check_urls.py`（严格模式，无代理直连）
- 退出码: 1（存在 1 个不可访问数据入口：toolbench_2024 data_url，官方 Google Drive 入口已失效）
- 环境: Windows 11，仓库 clean-branch 分支

```
========== 现有数据集 URL 可访问性检查 ==========
登记表: registry\dataset_registry.csv
数据集总数: 12

| 数据集 | 官方URL | 状态 | 下载URL | 状态 |
| --- | --- | --- | --- | --- |
| longmemeval_cleaned_2025 | https://github.com/xiaowu0162/LongMemEval | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned | OK:200 |
| longmemeval_v2_2026 | https://github.com/xiaowu0162/LongMemEval-V2 | OK:200 | https://huggingface.co/datasets/xiaowu0162/longmemeval-v2 | OK:200 |
| stabletoolbench_2024 | https://github.com/THUNLP-MT/StableToolBench | OK:200 | https://github.com/THUNLP-MT/StableToolBench | OK:200 |
| toolbench_2024 | https://github.com/OpenBMB/ToolBench | OK:200 | https://drive.google.com/drive/folders/1TysbSWYpP8EioFu9xPJtpbJZMLLmwAmL | ERROR:HTTP 404 |
| t2ranking_2023 | https://github.com/THUIR/T2Ranking | OK:200 | https://huggingface.co/datasets/THUIR/T2Ranking | OK:200 |
| dureader_retrieval_2022 | https://github.com/baidu/DuReader/tree/master/DuReader-Retrieval | OK:200 | https://github.com/PaddlePaddle/RocketQA/tree/main/research/DuReader-Retrieval-Baseline | OK:200 |
| multiwoz_2_2_2020 | https://github.com/budzianowski/multiwoz/tree/master/data/MultiWOZ_2.2 | OK:200 | https://github.com/budzianowski/multiwoz | OK:200 |
| personachat_2018 | https://github.com/facebookresearch/ParlAI | OK:200 | http://parl.ai/downloads/personachat/personachat.tgz | OK:200 |
| msmarco_2021 | https://microsoft.github.io/msmarco/ | OK:200 | https://huggingface.co/datasets/microsoft/ms_marco | OK:200 |
| trec_tracks_2024 | https://trec.nist.gov/ | OK:200 | https://trec.nist.gov/data.html | OK:200 |
| bpmn_2_0_2013 | https://www.omg.org/spec/BPMN/ | OK:200 | https://www.omg.org/spec/BPMN/2.0/PDF | OK:200 |
| machine_unlearning_bench_2025 | https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench | OK:200 | https://huggingface.co/datasets/machine-unlearning-bench/data-unlearning-bench | OK:200 |

统计（12 个数据集 x 官方/下载两列，共 24 项）: OK=23  EMPTY=0  ERROR=1  TIMEOUT=0
说明: OK=可访问, EMPTY=登记表未填写该 URL, ERROR=不可访问, TIMEOUT=超时

失败项（URL 验收失败条件，须逐项处置后方可通过）:
  - toolbench_2024 data_url: ERROR HTTP 404

结论: FAIL —— 存在未登记或不可访问的 URL
```

## toolbench_2024 数据入口失效的核验记录（2026-09-01）

对官方 README（master）给出的数据入口逐一复测：

| 入口 | URL 形式 | 结果 |
| --- | --- | --- |
| data.zip 文件夹（README 数据入口） | `https://drive.google.com/drive/folders/1TysbSWYpP8EioFu9xPJtpbJZMLLmwAmL` | HTTP 404 |
| 同上（embeddedfolderview，公开文件夹免 JS 视图） | `https://drive.google.com/embeddedfolderview?id=1TysbSWYpP8EioFu9xPJtpbJZMLLmwAmL` | HTTP 404 |
| 同上（/file/d/view 形式） | `https://drive.google.com/file/d/1TysbSWYpP8EioFu9xPJtpbJZMLLmwAmL/view` | HTTP 403 |
| data.zip 文件（README wget 直链） | `https://drive.google.com/uc?export=download&id=1XFjDxVZdUY7TXYF2yvzx3pJlS2fy78jk&confirm=yes` | HTTP 404 |
| 同上（usercontent/download 形式） | `https://drive.usercontent.google.com/download?id=1XFjDxVZdUY7TXYF2yvzx3pJlS2fy78jk&export=download` | HTTP 404 |
| 同上（open?id / docs.google.com/uc 形式） | 两种形式 | 均 HTTP 404 |
| 对照：同 README 内另一公开文件（RapidAPI server codes） | `https://drive.google.com/file/d/1JdbHkL2D8as1docfHyfLWhrhlSP9rZhf/view` | HTTP 200（对照组证明 Drive 对本机自动检查可用，404 为真实失效而非反爬） |
| GitHub Releases | `api.github.com/repos/OpenBMB/ToolBench/releases` | 空（无任何 release） |
| HuggingFace 官方组织 | `huggingface.co/api/datasets?author=OpenBMB` | 空（OpenBMB 无官方 HF 数据集） |

结论：ToolBench 官方数据分发入口已失效，数据当前不可通过官方渠道获取。
处置建议（待 Reviewer 裁决，Gate 3 范畴）：降级为方法论参考或淘汰；
Tool Result 任务仍有 StableToolBench（官方入口可访问）与 LongMemEval-V2 两个候选，覆盖不受影响。
