# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# TODO: Address all TODOs and remove all explanatory comments

import datasets
import json
from typing import List
import pandas as pd
import csv

_LICENSE = "http://www.apache.org/licenses/LICENSE-2.0"
_HOMEPAGE='https://hf-mirror.com/datasets/THUIR/T2Ranking'

_DESCRIPTION = 'T2Ranking: A large-scale Chinese benchmark for passage retrieval.'
_CITATION = """
@misc{xie2023t2ranking,
      title={T2Ranking: A large-scale Chinese Benchmark for Passage Ranking}, 
      author={Xiaohui Xie and Qian Dong and Bingning Wang and Feiyang Lv and Ting Yao and Weinan Gan and Zhijing Wu and Xiangsheng Li and Haitao Li and Yiqun Liu and Jin Ma},
      year={2023},
      eprint={2304.03679},
      archivePrefix={arXiv},
      primaryClass={cs.IR}
}
"""

_URLS_DICT = {
    "collection": "data/collection.tsv",
    "qrels.train": "data/qrels.train.tsv",
    "qrels.dev": "data/qrels.dev.tsv",
    "qrels.retrieval.train": "data/qrels.retrieval.train.tsv",
    "qrels.retrieval.dev": "data/qrels.retrieval.dev.tsv",
    "queries.train": "data/queries.train.tsv",
    "queries.test": "data/queries.test.tsv",
    "queries.dev": "data/queries.dev.tsv",
    "train.bm25.tsv": "data/train.bm25.tsv",
    "train.mined.tsv": "data/train.mined.tsv",
}

_FEATURES_DICT = {
    'collection': {
        "pid": datasets.Value("int64"),
        "text": datasets.Value("string"),
    },
    'qrels.train': {
        "qid": datasets.Value("int64"),
        "-": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
        "rel": datasets.Value("int64"),
    },
    'qrels.retrieval.train': {
        "qid": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
    },
    'qrels.dev': {
        "qid": datasets.Value("int64"),
        "-": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
        "rel": datasets.Value("int64"),
    },
    'qrels.retrieval.dev': {
        "qid": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
    },
    'queries.train': {
        "qid": datasets.Value("int64"),
        "text": datasets.Value("string"),
    },
    'queries.dev': {
        "qid": datasets.Value("int64"),
        "text": datasets.Value("string"),
    },
    'queries.test': {
        "qid": datasets.Value("int64"),
        "text": datasets.Value("string"),
    },
    "train.bm25.tsv": {
        "qid": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
        "index": datasets.Value("int64"),
    },
    "train.mined.tsv": {
        "qid": datasets.Value("int64"),
        "pid": datasets.Value("int64"),
        "index": datasets.Value("int64"),
        "score": datasets.Value("float32"),
    },
}

class T2RankingConfig(datasets.BuilderConfig):
    """BuilderConfig for T2Ranking."""

    def __init__(self, splits, **kwargs):
        super().__init__(version=datasets.Version("1.0.0"), **kwargs)
        self.splits = splits


class T2Ranking(datasets.GeneratorBasedBuilder):
    """The T2Ranking benchmark."""

    BUILDER_CONFIGS = [
        T2RankingConfig(
            name="collection",
            splits=['train'],
        ),
        T2RankingConfig(
            name="qrels.train",
            splits=['train'],
        ),
        T2RankingConfig(
            name="qrels.dev",
            splits=['train'],
        ),
        T2RankingConfig(
            name="queries.train",
            splits=['train'],
        ),
        T2RankingConfig(
            name="queries.dev",
            splits=['train'],
        ),       
        T2RankingConfig(
            name="queries.test",
            splits=['train'],
        ),
        T2RankingConfig(
            name="qrels.retrieval.train",
            splits=['train'],
        ),
        T2RankingConfig(
            name="qrels.retrieval.dev",
            splits=['train'],
        ),
        T2RankingConfig(
            name="train.bm25.tsv",
            splits=['train'],
        ),
        T2RankingConfig(
            name="train.mined.tsv",
            splits=['train'],
        ),
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(_FEATURES_DICT[self.config.name]),
            homepage=_HOMEPAGE,
            citation=_CITATION,
            license=_LICENSE,
        )

    def _split_generators(self, dl_manager: datasets.DownloadManager) -> List[datasets.SplitGenerator]:
        split_things = []
        for split_name in self.config.splits:
            split_data_path = _URLS_DICT[self.config.name]
            filepath = dl_manager.download(split_data_path)
            split_thing = datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "filepath": filepath,
                }
            )
            split_things.append(split_thing)
        return split_things

    def _generate_examples(self, filepath):
        reader = csv.DictReader(open(filepath), delimiter='\t', quoting=csv.QUOTE_NONE)
        keys = _FEATURES_DICT[self.config.name].keys()
        idx = -1
        for data in reader:
            idx+=1
            yield idx, {key: data[key] for key in keys}
