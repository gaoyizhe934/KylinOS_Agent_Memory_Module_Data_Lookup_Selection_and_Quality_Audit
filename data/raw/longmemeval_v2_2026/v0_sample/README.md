---
language:
- en
license: apache-2.0
pretty_name: LongMemEval-V2
task_categories:
- image-text-to-text
tags:
- benchmark
- agents
- memory
- retrieval
- question-answering
- web-agents
- enterprise-agents
---

# LongMemEval-V2 Data

[**Project Page**](https://xiaowu0162.github.io/longmemeval-v2/) | [**Paper**](https://huggingface.co/papers/2605.12493) | [**GitHub**](https://github.com/xiaowu0162/LongMemEval-V2)

LongMemEval-V2 (LME-V2) is an evaluation benchmark for long-term memory in web and enterprise agents. It contains 451 manually curated questions and 1,870 task trajectories drawn from customized WebArena-style and ServiceNow-style environments.

The benchmark evaluates five core memory abilities:
- **Static state recall**: remembers important landmarks and page layouts.
- **Dynamic state tracking**: understands how states change over time.
- **Workflow knowledge**: knows the steps needed for recurring tasks.
- **Environment gotchas**: recognizes recurring local failure modes.
- **Premise awareness**: detects assumptions valid elsewhere but wrong here.

## Files

- `questions.jsonl`: normalized benchmark questions.
- `trajectories.jsonl`: normalized task trajectories with text observations and screenshot paths.
- `haystacks/lme_v2_small.json`: LME-V2-Small haystack mapping.
- `haystacks/lme_v2_medium.json`: LME-V2-Medium haystack mapping.
- `question_screenshots/`: images referenced by multimodal questions.
- `trajectory_screenshots/`: trajectory screenshot archives. On Hugging Face, these remain `.tar.gz` bundles. On Kaggle, uploaded screenshot tarballs are exposed as expanded directories named `web_screenshots/` and `enterprise_screenshots_base/`.
- `SCHEMA.md`: public schema description.
- `DATA_CARD.md`: dataset documentation.
- `checksums.sha256`: checksums for core JSON/documentation files and question screenshots.

## Sample Usage (Data Preparation)

To download and prepare the data as described in the official repository:

```bash
# Download the data
python data/download_data.py --data-root data/longmemeval-v2
export DATA_ROOT="$(pwd)/data/longmemeval-v2"

# Prepare screenshots (extracts and links)
python data/prepare_data.py --data-root "$DATA_ROOT" --mode symlink

# Validate the setup
python data/validate_data.py --data-root "$DATA_ROOT" --tier small
```

### Preparing Screenshots Manually

The trajectory JSON uses screenshot paths shaped as `screenshots/<trajectory_id>/<step>.png`. To materialize those paths after downloading from Hugging Face:

```bash
cd <downloaded-dataset-root>
mkdir -p screenshots
tar -xzf trajectory_screenshots/web_screenshots.tar.gz -C screenshots
tar -xzf trajectory_screenshots/enterprise_screenshots_base.tar.gz -C screenshots
```

## Release Notes

The public files intentionally remove construction provenance, local source paths, original task ids, answer-bearing annotation labels, URL-pattern labels, and annotation pipeline tags.

## Citation

```bibtex
@article{wu2026longmemevalv2,
      title={LongMemEval-V2: Evaluating Long-Term Agent Memory Toward Experienced Colleagues}, 
      author={Di Wu and Zixiang Ji and Asmi Kawatkar and Bryan Kwan and Jia-Chen Gu and Nanyun Peng and Kai-Wei Chang},
      year={2026},
      eprint={2605.12493},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.12493}, 
}
```

## License

This dataset is released under the Apache License 2.0. See `LICENSE`.