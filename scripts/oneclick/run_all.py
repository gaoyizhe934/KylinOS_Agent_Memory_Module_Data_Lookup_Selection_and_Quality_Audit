# -*- coding: utf-8 -*-
"""One-click generator for the Kylin OS Agent memory data work package.

Run from any location:
    python scripts/oneclick/run_all.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pkg_config import PKG_ROOT
from pkg_phases_a import (
    phase0_setup,
    phase1_mapping,
    phase2_evidence,
    phase3_audit,
    phase4_scoring,
    phase5_freeze,
    phase6_convert,
    phase7_runtime_package,
    write,
)
from pkg_phases_b import (
    generate_gold,
    phase9_split,
    write_download_script,
)
from pkg_reports import (
    build_docx,
    report_data_card,
    report_gate_status,
    report_handoff,
    report_reproduction,
    write_scripts,
)


def write_annotation_docs():
    write(
        "data/gold/annotation_guideline.md",
        """# 麒麟 OS Memory Gold 标注手册 v1.0（候选草稿）

## 总原则

- 标签必须能从 input/evidence 直接推导，禁止无证据猜测。
- 区分临时指令（should_store=false）与长期偏好（should_store=true）。
- 冲突样本必须写清 conflict_type、winner 与 resolution_reason。
- 遗忘样本必须同时给出 target_ids 与 must_keep，并检查重启/重建索引后的残留。
- Tool Result 必须区分 success/failed/cancelled/timeout/partial_success，禁止把失败写成成功。
- AI 只能生成候选标签；最终标签必须由双人独立标注 + Reviewer 裁决。

## 试标流程

1. 双人独立标注 30-50 条，禁止先讨论答案。
2. 汇总分歧并按类型聚类：任务定义、偏好/临时边界、作用域、证据不足、冲突优先级、应删/应留。
3. 修订本手册后回溯重审受影响样本。
4. 正式阶段双人独立提交，脚本只计算一致性，不自动覆盖。
5. Reviewer 查看原始证据与两份标签，写出 final_label 与 decision_reason。
""",
    )
    write(
        "data/gold/disagreement_log.csv",
        "sample_id,task_type,annotator_a,annotator_b,disagreement_type,evidence_summary,reviewer_decision,status\n",
    )


def main():
    print("== Kylin data work package generator ==")
    print("package root:", PKG_ROOT)

    phase0_setup()
    phase1_mapping()
    phase2_evidence()

    gold_sets = generate_gold()
    phase3_audit(gold_sets)
    phase4_scoring()
    phase5_freeze()
    phase6_convert(gold_sets)
    phase9_split(gold_sets)
    write_download_script()
    write_annotation_docs()
    phase7_runtime_package()
    write_scripts()

    counts = {k: len(v) for k, v in gold_sets.items()}
    report_data_card(counts)
    report_reproduction()
    report_handoff(counts)
    report_gate_status()

    docx_path = build_docx(counts)
    print("gold counts:", counts)
    print("docx:", docx_path)
    print("== done ==")


if __name__ == "__main__":
    main()
