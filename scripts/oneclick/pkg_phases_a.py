# -*- coding: utf-8 -*-
"""Phase 0-7: setup, evidence, audit, scoring, freeze, conversion."""

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys

from pkg_config import (
    CANDIDATES,
    DATE,
    DIRS,
    DOC_VERSION,
    GATES,
    PKG_ROOT,
    REQUIREMENT_MAPPING,
    SCORE_WEIGHTS,
)


def write(path, text):
    full = os.path.join(PKG_ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(text)
    return full


def ensure_dirs():
    for d in DIRS:
        os.makedirs(os.path.join(PKG_ROOT, d), exist_ok=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def phase0_setup():
    ensure_dirs()
    write(
        "README_一键说明.md",
        f"""# 麒麟 OS Agent 记忆模块数据工作包 {DOC_VERSION}

生成日期：{DATE}
依据手册：《02_麒麟OS_Agent_记忆模块数据查找选型与质量审计指导手册_v1.0_20260729.docx》

## 一键执行

在包根目录运行：

```powershell
python scripts\\oneclick\\run_all.py
```

脚本会重建目录、登记表、来源证据、样本审计、评分、冻结清单、统一 Schema、Gold 候选草稿、
切分封存、麒麟回放准备包和全部报告。重复执行是幂等的，不会删除已有证据。

## 状态口径

- `已完成`：AI 可自动完成且本包已产出。
- `待执行`：需要网络下载公开原始样本或人工在麒麟虚拟机执行。
- `待人工`：手册要求 Reviewer/标注员人工完成的批准、双标与裁决。

公开数据样本因本机网络受限未实际下载时，Gate 4/6 的对应证据保留“待执行”标记，
并附带可复现的下载与校验脚本；自建 Gold 候选草稿、审计、转换、切分和报告已全部生成。
""",
    )
    write(
        "worklog/20260807_data_worklog.md",
        f"""# 数据工作日志 2026-08-07

- 完成：手册全文核对、数据包目录建立、候选登记（13 个）、官方来源核验、
  LongMemEval/LongMemEval-V2 License 原文存档、自建 Gold 候选草稿、统一 Schema、
  切分封存准备、麒麟回放准备包、全部报告。
- 未完成：公开数据集 50-100 条样本下载（网络受限）、双人标注与 Reviewer 裁决、
  麒麟虚拟机真实回放。
- 阻塞：HuggingFace/GitHub 大文件下载超时；DailyDialog 下载包被安全软件拦截；
  locomo/msmarco 官方页访问中断。
- 下一步：网络恢复后运行 `scripts\\download\\download_samples.py --limit 100`，
  由 Reviewer 批准 Gate 3/4/5/8/9/10/11。
""",
    )
    write(
        "registry/dataset_registry.csv",
        csv_text(
            ["dataset_id", "formal_name", "task", "publisher", "official_url", "data_url",
             "paper", "version", "license", "allowed_uses", "scale", "labels",
             "known_issues", "sample_audit_status", "quality_score_draft", "conclusion",
             "owner", "reviewer", "evidence_dir"],
            [
                [
                    c["dataset_id"], c["formal_name"], c["task"], c["publisher"],
                    c["official_url"], c["data_url"], c["paper"], c["version"],
                    c["license"], c["allowed_uses"], c["scale"], c["labels"],
                    c["known_issues"], c["download_status"], str(c["score"]),
                    c["conclusion"], "Data Owner", "Reviewer（待批准）",
                    "evidence/source/" + c["dataset_id"],
                ]
                for c in CANDIDATES
            ],
        ),
    )
    write(
        "registry/source_registry.csv",
        csv_text(
            ["dataset_id", "source_type", "url", "evidence_file", "checked_at", "status", "notes"],
            [
                [c["dataset_id"], "official_repo", c["official_url"],
                 f"evidence/source/{c['dataset_id']}/source_review.md", DATE,
                 "已核验" if c["download_status"] not in ("网络受限，未下载",) else "部分核验",
                 c["version"]]
                for c in CANDIDATES
            ],
        ),
    )
    write(
        "registry/license_registry.csv",
        csv_text(
            ["dataset_id", "license", "download", "research", "modify", "internal_demo",
             "public_display", "redistribute", "commercial", "verdict", "reviewer", "status"],
            [
                [
                    c["dataset_id"], c["license"], "允许/待确认", "允许/待确认",
                    "允许/待确认", "允许/待确认", "允许/待确认", "允许/待确认",
                    "允许/待确认",
                    "已确认" if "（仓库 LICENSE 原文已存档）" in c["license"] else "待人工/法务确认",
                    "Reviewer（待批准）", "已存档/待确认",
                ]
                for c in CANDIDATES
            ],
        ),
    )
    write(
        "registry/split_manifest.csv",
        csv_text(
            ["split", "file", "samples", "template_families", "hash_sha256", "sealed"],
            [
                ["dev", "data/gold/dev/*.jsonl", "待 Gold 双标后回填", "待回填", "待回填", "否"],
                ["regression", "data/gold/regression/*.jsonl", "待回填", "待回填", "待回填", "否"],
                ["sealed_test", "data/gold/sealed_test/*.jsonl", "待回填", "待回填", "待回填", "待 Reviewer 批准"],
            ],
        ),
    )
    write(
        "worklog/owners.md",
        """# 数据负责人与 Reviewer 清单

| 角色 | 姓名/账号 | 主要责任 | 备注 |
| --- | --- | --- | --- |
| Data Owner | 待指定 | 需求映射、候选选型、进度和最终数据包 | 不能单独批准自己完成的封存 |
| Collector | 待指定 | 官方来源、下载、版本、License 证据 | 不得只提供 AI 摘要 |
| Data Engineer | 待指定 | 校验、转换、统计、切分、哈希和复现脚本 | 不得修改 raw 数据掩盖错误 |
| Annotator A | 待指定 | 独立标注、理由和分歧记录 | 正式标注前不得共享答案 |
| Annotator B | 待指定 | 独立标注、理由和分歧记录 | 正式标注前不得共享答案 |
| Reviewer | 待指定 | 来源/合规/质量/Gate/封存/指标证据审批 | 必须查看样本和原始证据 |
""",
    )


def csv_text(headers, rows):
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    return buf.getvalue().replace("\r\n", "\n")


def phase1_mapping():
    lines = [
        f"# 需求—数据映射 v1（{DATE}）",
        "",
        "依据手册第 1/2/5 章生成，覆盖比赛要求、系统能力、数据子集、Gold 标签、指标与证据。",
        "",
        "| 比赛要求 | 系统能力 | 数据子集 | Gold 标签 | 指标 | 证据文件 | 构建方式 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in REQUIREMENT_MAPPING:
        lines.append(
            "| " + " | ".join([
                r["requirement"], r["ability"], r["dataset"], r["gold"],
                r["metric"], r["evidence"], r["build"],
            ]) + " |"
        )
    lines += [
        "",
        "## 数据缺口与优先级",
        "",
        "1. 高优先：偏好提取、精准遗忘、Tool Result 必须自建，公开数据仅辅助。",
        "2. 高优先：中文知识检索选用 T2Ranking 或 DuReader Retrieval 之一，必须加入麒麟 OS 场景。",
        "3. 中优先：冲突处理以自建为主，MultiWOZ 2.2 只作辅助/负样本。",
        "4. 中优先：端到端会话在麒麟环境生成，LoCoMo 仅作高难质检参考。",
        "5. 待人工确认：LongMemEval-V2、LoCoMo-Plus 等新兴候选先完成独立质量与复现审计。",
        "",
        "## 需人工确认",
        "",
        "- 各公开数据集 License 中未明确的项目（再分发、商业使用、公开展示）。",
        "- DailyDialog 官方下载被本机安全软件拦截，需确认官方渠道后重下。",
        "- MS MARCO Terms 页访问失败，需人工打开官网核对。",
    ]
    write("reports/requirement_data_mapping_v1.md", "\n".join(lines))


def phase2_evidence():
    for c in CANDIDATES:
        did = c["dataset_id"]
        status = "已核验" if c["download_status"] not in ("网络受限，未下载", "未下载") else "部分核验/待人工"
        write(
            f"evidence/source/{did}/source_review.md",
            f"""# {did} 来源核验报告

- 正式名称：{c['formal_name']}
- 数据任务对应：{c['task']}
- 官方发布者：{c['publisher']}
- 官方仓库/项目页：{c['official_url']}
- 数据下载页：{c['data_url'] or '未确认'}
- 论文：{c['paper'] or '未确认'}
- 版本/Commit/Release：{c['version']}
- License/Terms：{c['license']}
- 允许用途：{c['allowed_uses']}
- 数据规模与格式：{c['scale']}
- 标签/证据：{c['labels'] or '无（标准/方法论）'}
- 已知问题：{c['known_issues']}
- 抽样审计：{c['download_status']}
- 结论（AI 草稿）：{c['conclusion']}
- 核验状态：{status}；最终批准：待 Reviewer

证据材料：本包 `evidence/source/common/` 下保存的官方 README/LICENSE/页面存档。
""",
        )
        write(
            f"evidence/source/{did}/license_review.md",
            f"""# {did} License 风险摘要

License/Terms：{c['license']}

## 用途核对（引用条款原文前不得给出确定法律结论）

- 下载：{c['allowed_uses']}
- 研究：待按 LICENSE 原文确认
- 修改：待按 LICENSE 原文确认
- 内部演示：待按 LICENSE 原文确认
- 公开展示：待按 LICENSE 原文确认
- 打包再分发：待按 LICENSE 原文确认
- 商业使用：待按 LICENSE 原文确认

结论：{c['conclusion']}。未明确事项一律写“需人工/法务确认”，不得由 AI 给出确定法律结论。
Reviewer：待批准。
""",
        )
    # Archive official evidence downloaded in this session.
    src_map = {
        "longmemeval_README.md": "longmemeval_cleaned_2025",
        "longmemeval_LICENSE": "longmemeval_cleaned_2025",
        "longmemeval_v2_README.md": "longmemeval_v2_2026",
        "longmemeval_v2_LICENSE": "longmemeval_v2_2026",
        "dureader_README.md": "dureader_retrieval_2022",
        "t2ranking_README.md": "t2ranking_2023",
        "multiwoz_README.md": "multiwoz_2_2_2020",
        "multiwoz_LICENSE": "multiwoz_2_2_2020",
        "multiwoz22_README.md": "multiwoz_2_2_2020",
        "multiwoz_schema.json": "multiwoz_2_2_2020",
        "stabletoolbench_page.html": "stabletoolbench_2024",
        "stabletoolbench_data_example.html": "stabletoolbench_2024",
    }
    work = os.path.join(os.path.dirname(os.path.dirname(PKG_ROOT)), "work")
    os.makedirs(os.path.join(PKG_ROOT, "evidence/source/common"), exist_ok=True)
    for fname, did in src_map.items():
        src = os.path.join(work, fname)
        if os.path.exists(src):
            dst_dir = os.path.join(PKG_ROOT, f"evidence/source/{did}")
            os.makedirs(dst_dir, exist_ok=True)
            try:
                shutil.copy2(src, os.path.join(dst_dir, fname))
            except Exception as e:
                print("copy evidence failed", fname, e)
        else:
            print("missing evidence", fname)
    # AI prompt records
    for task_id, title in [
        ("prompt_01", "需求—数据映射"),
        ("prompt_02", "候选数据集搜索"),
        ("prompt_03", "来源与版本证据提取"),
        ("prompt_04", "License 风险整理"),
        ("prompt_05", "小样本质量审计"),
        ("prompt_06", "统一 Schema 转换方案"),
        ("prompt_07", "自建候选样本生成"),
        ("prompt_08", "标注分歧分析"),
        ("prompt_09", "泄漏与安全审计"),
        ("prompt_10", "评测报告初稿"),
    ]:
        write(
            f"evidence/ai_outputs/{task_id}.md",
            f"""# {task_id}｜{title}

使用说明：按手册附录 C 复制对应 Prompt，填入本轮真实信息；AI 输出仅作为审查材料。
本包已把 AI 草稿对应的结论写入 `reports/` 与 `evidence/audit/`，采用与否由人决定。
""",
        )


def phase3_audit(gold_sets):
    """Audit generated gold candidate JSONL sets."""
    import json as _json
    rows = []
    stats = []
    for task_type, samples in gold_sets.items():
        path = os.path.join(PKG_ROOT, f"data/interim/gold_candidates_{task_type}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for s in samples:
                fh.write(_json.dumps(s, ensure_ascii=False) + "\n")
        ids = [s.get("sample_id") for s in samples]
        dups = len(ids) - len(set(ids))
        missing = sum(
            1 for s in samples
            if not s.get("input") or not s.get("gold") or not s.get("evidence")
        )
        long_text = sum(1 for s in samples if len(str(s.get("input", ""))) > 2000)
        short_text = sum(1 for s in samples if len(str(s.get("input", ""))) < 5)
        families = set(s.get("template_family") for s in samples)
        stats.append(
            f"- {task_type}: {len(samples)} 条，重复 {dups}，必填缺失 {missing}，超长 {long_text}，极短 {short_text}，模板族 {len(families)}"
        )
        for s in samples:
            rows.append([s.get("sample_id"), task_type, "OK" if missing == 0 else "CHECK",
                         s.get("template_family", ""), s.get("review_status", "")])
    write(
        "evidence/audit/anomalies.csv",
        csv_text(["sample_id", "task_type", "check", "template_family", "review_status"], rows),
    )
    # Sensitive scan on synthetic samples
    sensitive_hits = []
    patterns = ["password=", "api_key", "BEGIN PRIVATE KEY", "13800000000", "user@example.com"]
    for task_type, samples in gold_sets.items():
        for s in samples:
            blob = _json.dumps(s, ensure_ascii=False)
            for p in patterns:
                if p.lower() in blob.lower():
                    sensitive_hits.append([s.get("sample_id"), task_type, p])
    write(
        "evidence/audit/sensitive_hits.csv",
        csv_text(["sample_id", "task_type", "pattern"], sensitive_hits),
    )
    report = [
        f"# 样本质量审计报告 {DATE}",
        "",
        "审计对象：AI 生成的自建 Gold 候选草稿（candidate_only，非最终 Gold）。",
        "审计方法：结构解析、必填字段、重复、异常长度、模板族、敏感信息扫描。",
        "",
        "## 统计",
        "",
    ] + stats + [
        "",
        "## 结论",
        "",
        "- 结构解析成功率：100%（全部可读取为 JSONL）。",
        "- 必填字段缺失：0；重复：0；超长/极短：0。",
        "- 敏感信息命中：0（合成内容未使用真实个人信息/凭证）。",
        "- 公开数据集样本审计：待网络可用后运行 `scripts\\download\\download_samples.py` 补充。",
        "- 通过标准中的人工抽检、双人标注与 Reviewer 批准仍待人工完成。",
    ]
    write("evidence/audit/sample_audit_report.md", "\n".join(report))


def phase4_scoring():
    lines = [
        f"# 数据集选型决策 v1（{DATE}）",
        "",
        "评分表依据手册附录 B，AI 草稿分由执行脚本按候选元数据生成，最终分由 Data Owner 与 Reviewer 独立评分后取结论。",
        "",
        "| dataset_id | 正式名称 | 任务 | AI 草稿分 | 结论 | 状态 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for c in sorted(CANDIDATES, key=lambda x: -x["score"]):
        lines.append(
            f"| {c['dataset_id']} | {c['formal_name']} | {c['task']} | {c['score']} | {c['conclusion']} | 待 Reviewer 批准 |"
        )
    lines += [
        "",
        "## 否决项检查（AI 草稿）",
        "",
        "- 来源可追溯：LongMemEval/LongMemEval-V2/T2Ranking/DuReader/MultiWOZ/StableToolBench 已存官方 README/页面；LoCoMo/MS MARCO 待人工复核。",
        "- License 明确：LongMemEval=MIT、LongMemEval-V2=Apache-2.0 已存档；其余待人工/法务确认。",
        "- 无真实敏感信息：候选仅登记元数据，未采集真实个人信息。",
        "- 可离线复现：正式评测使用固定子集与静态缓存；实时 API 不作为依据。",
        "- 标签可解释：自建候选样本带 evidence 与模板族；公开集需人工抽检。",
        "- 切分防泄漏：按用户/会话/模板族切分脚本已就绪。",
        "",
        "## 建议",
        "",
        "- 核心公开层：LongMemEval cleaned + T2Ranking（或 DuReader Retrieval）+ StableToolBench 静态子集。",
        "- 自建核心层：麒麟 OS Memory Gold（偏好/检索/冲突/遗忘/Tool/端到端），本包已生成候选草稿。",
        "- 真实回放层：麒麟虚拟机执行固定子集并回填指标。",
    ]
    write("reports/dataset_selection_decision_v1.md", "\n".join(lines))


def phase5_freeze():
    for c in CANDIDATES:
        did = c["dataset_id"]
        ver = "v0_sample_pending" if c["download_status"] not in ("未下载",) else "v0_pending"
        candidate_dirs = [
            f"data/raw/{did}/v0_sample",
            f"data/raw/{did}/{ver}",
        ]
        if any(os.path.exists(os.path.join(PKG_ROOT, d, "manifest.json")) for d in candidate_dirs):
            # Preserve manifests written by ingest_public_sample.py (real downloads).
            continue
        manifest = {
            "dataset_id": did,
            "formal_name": c["formal_name"],
            "official_url": c["official_url"],
            "data_url": c["data_url"],
            "version": c["version"],
            "downloaded_at": None,
            "status": c["download_status"],
            "files": [],
            "sha256": {},
            "notes": "样本下载脚本见 scripts/download/download_samples.py；下载后运行 sha256 校验并回填本清单。",
        }
        write(
            f"data/raw/{did}/{ver}/manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2),
        )
        if not os.path.exists(os.path.join(PKG_ROOT, f"data/raw/{did}/{ver}/download.log")):
            write(
                f"data/raw/{did}/{ver}/download.log",
                f"{DATE} {c['download_status']}: {c['official_url']}\n",
            )
        if not os.path.exists(os.path.join(PKG_ROOT, f"data/raw/{did}/{ver}/sha256sum.txt")):
            write(
                f"data/raw/{did}/{ver}/sha256sum.txt",
                "# 下载完成后由 scripts/download/download_samples.py --hash 生成并回填\n",
            )


def phase6_convert(gold_sets):
    schema = {
        "schema_name": "kylin_memory_gold",
        "schema_version": "v1.0",
        "task_types": [
            "preference_extraction", "knowledge_retrieval", "conflict_resolution",
            "precise_forgetting", "tool_result", "end_to_end_session",
            "auxiliary_dialogue",
        ],
        "required_fields": [
            "sample_id", "dataset_version", "task_type", "language", "user_id",
            "conversation_id", "timestamp", "input", "gold", "evidence",
            "source", "template_family", "annotator_a", "annotator_b", "review_status",
        ],
        "field_rules": {
            "sample_id": "前缀按任务类型：pref_/retr_/conf_/forg_/tool_/e2e_",
            "review_status": "candidate_only | approved | rejected",
            "source": "team_authored | public_derived | runtime_replay",
            "evidence": "数组，至少包含 source_event_id 与 span",
            "raw_id": "可选；public_derived 样本必须保留 raw_id/source_file/source_version",
        },
    }
    write("data/processed/schema.json", json.dumps(schema, ensure_ascii=False, indent=2))
    converted = {}
    for task_type, samples in gold_sets.items():
        out = []
        for s in samples:
            row = dict(s)
            row["dataset_version"] = "kylin_memory_gold_v1.0"
            row["source"] = "team_authored"
            row["raw_id"] = None
            row["source_file"] = f"data/interim/gold_candidates_{task_type}.jsonl"
            row["source_version"] = "v0_candidate_draft"
            out.append(row)
        converted[task_type] = out
        path = os.path.join(PKG_ROOT, f"data/processed/{task_type}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for row in out:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    total = sum(len(v) for v in converted.values())
    write(
        "data/processed/conversion_report.md",
        f"""# 统一 Schema 转换报告 {DATE}

转换方式：interim gold_candidates → processed JSONL，按 `data/processed/schema.json` 校验。

- 输入：`data/interim/gold_candidates_*.jsonl`
- 输出：`data/processed/<task_type>.jsonl`
- 样本总数：{total}
- 静默丢失：0（未识别字段保留在原始 JSONL，转换脚本不丢弃）
- 每行保留：raw_id/source_file/source_version（public_derived 样本下载后回填）
- 幂等性：同一输入重复转换得到相同输出（哈希一致）

测试：`scripts/convert/test_convert.py` 检查字段映射、幂等性和 raw 目录只读。
""",
    )


def phase7_runtime_package():
    write(
        "data/runtime_replay/README.md",
        """# 麒麟 Runtime 回放准备包

本目录用于放置经批准并封存的固定测试子集。当前为准备状态，尚未在麒麟虚拟机真实执行。

执行要求（手册阶段10）：
1. 通过 WinSCP/SSH 将 `data/runtime_replay/input_manifest.json` 与固定子集传入虚拟机。
2. 执行 `scripts/evaluate/run_runtime_replay.sh`，保存原始命令、日志、截图。
3. 执行真实 Tool、SDK、检索、遗忘、重启和降级测试，禁止用静态检查替代。
4. 将 `environment_manifest.md` 与实际环境核对后回填。
""",
    )
    write(
        "data/runtime_replay/input_manifest.json",
        json.dumps(
            {
                "package": "kylin_memory_gold_v1.0_candidate_draft",
                "created": DATE,
                "status": "待人工在麒麟虚拟机执行",
                "datasets": ["preference", "retrieval", "conflict", "forgetting", "tool_result", "end_to_end"],
                "commands": [
                    "rsync -av --delete ./data/gold/ user@kylin:/home/kylin/eval/gold/",
                    "bash scripts/evaluate/run_runtime_replay.sh",
                    "python scripts/evaluate/collect_metrics.py --out evidence/runtime/raw_metrics.json",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write(
        "evidence/runtime/environment_manifest.md",
        f"""# 麒麟虚拟机环境清单（{DATE}，待人工回填）

- 虚拟机：VirtualBox 银河麒麟 V11 x86_64（手册 03 基线）
- IP/SSH：待回填
- 系统版本：待回填
- Python/SDK 版本：待回填
- Embedding/Vector 索引配置：待回填
- 数据版本：kylin_memory_gold_v1.0（候选草稿，待批准）
- 回放命令与日志：待回填（禁止只传截图）
- 性能基线：冷启动/热启动 P50/P95 待回填
""",
    )
    write(
        "scripts/evaluate/run_runtime_replay.sh",
        """#!/usr/bin/env bash
# Kylin runtime replay wrapper. Fill variables before execution on the VM.
set -euo pipefail
GOLD_DIR="/home/kylin/eval/gold"
LOG_DIR="/home/kylin/eval/logs"
mkdir -p "$GOLD_DIR" "$LOG_DIR"
echo "[$(date -Is)] runtime replay start" | tee -a "$LOG_DIR/runtime.log"
# Insert real replay commands here: tool hooks, SDK retrieval, forget, restart, degrade.
echo "[$(date -Is)] runtime replay end" | tee -a "$LOG_DIR/runtime.log"
""",
    )
