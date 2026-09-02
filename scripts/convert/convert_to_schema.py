# -*- coding: utf-8 -*-
"""Convert interim gold candidates + public raw subsets to processed unified schema.

Stage 7（A 侧）：
- 修复 v1.0 非法 timestamp（如 2026-07-202T10:00:00 → 2026-07-20T10:00:00）
- public_derived 样本保留 raw_id / source_file / source_version 溯源
- 公开数据集按手册"只取固定小规模子集"，全量保留在 data/raw
- 无静默丢失：输入输出行数显式对账
- 幂等：同一输入重复转换输出字节一致（LF）
"""
import glob
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTERIM = os.path.join(ROOT, "data/interim")
PROCESSED = os.path.join(ROOT, "data/processed")
RAW = os.path.join(ROOT, "data/raw")

SCHEMA_REQUIRED = [
    "sample_id", "dataset_version", "task_type", "language",
    "user_id", "conversation_id", "timestamp", "input", "gold",
    "evidence", "source", "template_family", "annotator_a",
    "annotator_b", "review_status",
]

# 公开子集固定规模（手册：全量过大，只取固定小规模子集）
PUBLIC_LIMITS = {"t2ranking": 200, "multiwoz_dialogues": 200}

# 非法 timestamp 修复：3 位日期（2026-07-202T）截断为 2 位（2026-07-20T）
TS_3DIGIT_DAY = re.compile(r"^(\d{4}-\d{2})-(\d{3})(T.*)$")


def normalize_timestamp(ts, row_id="?"):
    if not isinstance(ts, str) or not ts:
        return ts, False
    fixed = False
    m = TS_3DIGIT_DAY.match(ts)
    if m:
        ts = f"{m.group(1)}-{m.group(2)[:2]}{m.group(3)}"
        fixed = True
    try:
        datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return ts, fixed
    except ValueError:
        return ts, fixed


def _valid_ts(ts):
    if not ts:
        return False
    try:
        datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def convert_team_authored():
    """interim gold_candidates_*.jsonl → processed/<task>.jsonl（修复 timestamp + 溯源字段）。"""
    stats = {"files": [], "input_rows": 0, "output_rows": 0, "fixed_ts": 0, "unfixed_ts": 0, "silent_drop": 0}
    for path in sorted(glob.glob(os.path.join(INTERIM, "gold_candidates_*.jsonl"))):
        name = os.path.basename(path)
        rows, in_n = [], 0
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                in_n += 1
                row = json.loads(line)
                row["dataset_version"] = "kylin_memory_gold_v1.0"
                row["source"] = row.get("source", "team_authored")
                row["raw_id"] = row.get("raw_id")
                row["source_file"] = row.get("source_file", "data/interim/" + name)
                row["source_version"] = row.get("source_version", "v0_candidate_draft")
                ts, fixed = normalize_timestamp(row.get("timestamp"), row.get("sample_id"))
                row["timestamp"] = ts
                if fixed:
                    stats["fixed_ts"] += 1
                elif not _valid_ts(ts):
                    stats["unfixed_ts"] += 1
                rows.append(row)
        out_name = name.replace("gold_candidates_", "").replace(".jsonl", ".jsonl")
        write_jsonl(os.path.join(PROCESSED, out_name), rows)
        stats["files"].append((name, out_name, in_n, len(rows)))
        stats["input_rows"] += in_n
        stats["output_rows"] += len(rows)
    return stats


def convert_multiwoz_public_sample():
    """interim multiwoz_public_sample.jsonl（public_derived）→ processed（保留 raw_id）。"""
    src = os.path.join(INTERIM, "multiwoz_public_sample.jsonl")
    if not os.path.exists(src):
        return {"input_rows": 0, "output_rows": 0, "fixed_ts": 0, "silent_drop": 0}
    rows, in_n = [], 0
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            in_n += 1
            row = json.loads(line)
            ts, fixed = normalize_timestamp(row.get("timestamp"), row.get("sample_id"))
            row["timestamp"] = ts
            rows.append(row)
    write_jsonl(os.path.join(PROCESSED, "multiwoz_public_sample.jsonl"), rows)
    return {"input_rows": in_n, "output_rows": len(rows), "fixed_ts": 0, "silent_drop": 0}


def convert_t2ranking_dev():
    """t2ranking dev queries+qrels → processed knowledge_retrieval 固定子集（public_derived，raw_id=qid）。"""
    q_path = os.path.join(RAW, "t2ranking_2023/v0_subset/queries.dev.tsv")
    r_path = os.path.join(RAW, "t2ranking_2023/v0_subset/qrels.retrieval.dev.tsv")
    if not (os.path.exists(q_path) and os.path.exists(r_path)):
        return {"input_rows": 0, "output_rows": 0, "silent_drop": 0, "note": "raw 缺失"}

    queries = {}
    with open(q_path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or parts[0] == "qid":
                continue
            queries[parts[0]] = parts[1]

    rel = {}
    with open(r_path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or parts[0] == "qid":
                continue
            rel.setdefault(parts[0], []).append(parts[1])

    limit = PUBLIC_LIMITS["t2ranking"]
    qids = sorted(queries.keys())[:limit]
    rows, in_n = [], len(queries)
    for qid in qids:
        relevant = sorted(rel.get(qid, []))
        rows.append({
            "sample_id": f"retr_t2r_{qid}",
            "dataset_version": "kylin_memory_gold_v1.0",
            "task_type": "knowledge_retrieval",
            "language": "zh-CN",
            "user_id": "u_public_t2ranking",
            "conversation_id": f"q_{qid}",
            "timestamp": "2026-09-01T00:00:00+08:00",
            "input": {"query": queries[qid], "query_id": qid},
            "gold": {
                "relevant_ids": relevant,
                "relevance": {pid: 1 for pid in relevant},
                "hard_negative_ids": [],
                "expected_answer_points": [],
            },
            "evidence": [{"source_event_id": qid, "span": queries[qid]}],
            "source": "public_derived",
            "template_family": "t2ranking_retrieval_v1",
            "annotator_a": "", "annotator_b": "", "review_status": "candidate_only",
            "raw_id": qid,
            "source_file": "data/raw/t2ranking_2023/v0_subset/queries.dev.tsv",
            "source_version": "hf_rev_2a369a43",
        })
    write_jsonl(os.path.join(PROCESSED, "knowledge_retrieval_t2ranking.jsonl"), rows)
    return {"input_rows": in_n, "output_rows": len(rows), "silent_drop": in_n - len(rows),
            "note": f"固定子集前 {limit} 个查询（全量 {in_n} 保留在 raw）"}


def convert_multiwoz_dialogues():
    """multiwoz dialogues_001.json → processed auxiliary_dialogue 固定子集（public_derived，raw_id=dialogue_id）。"""
    src = os.path.join(RAW, "multiwoz_2_2_2020/v0_subset/dialogues_001.json")
    if not os.path.exists(src):
        return {"input_rows": 0, "output_rows": 0, "silent_drop": 0, "note": "raw 缺失"}
    with open(src, encoding="utf-8") as fh:
        dialogues = json.load(fh)
    limit = PUBLIC_LIMITS["multiwoz_dialogues"]
    rows, in_n = [], len(dialogues)
    for dlg in dialogues[:limit]:
        dlg_id = dlg.get("dialogue_id", "unknown")
        turns = dlg.get("turns", [])
        rows.append({
            "sample_id": f"aux_mwz_{dlg_id.replace('.json','')}",
            "dataset_version": "kylin_memory_gold_v1.0",
            "task_type": "auxiliary_dialogue",
            "language": "en",
            "user_id": "u_public_multiwoz",
            "conversation_id": dlg_id,
            "timestamp": "2026-09-01T00:00:00+08:00",
            "input": {"dialogue_id": dlg_id, "services": dlg.get("services", []), "n_turns": len(turns)},
            "gold": {"goals": [], "services": dlg.get("services", [])},
            "evidence": [{"source_event_id": dlg_id, "span": dlg_id}],
            "source": "public_derived",
            "template_family": "multiwoz_dialogue_v1",
            "annotator_a": "", "annotator_b": "", "review_status": "candidate_only",
            "raw_id": dlg_id,
            "source_file": "data/raw/multiwoz_2_2_2020/v0_subset/dialogues_001.json",
            "source_version": "commit_fe0c8e65",
        })
    write_jsonl(os.path.join(PROCESSED, "multiwoz_dialogues_sample.jsonl"), rows)
    return {"input_rows": in_n, "output_rows": len(rows), "silent_drop": in_n - len(rows),
            "note": f"固定子集前 {limit} 个对话（全量 {in_n} 保留在 raw）"}


def handle_stale_tool_result():
    """processed/tool_result.jsonl 为 v1.0 残留，interim 源缺失（违反红线5：processed 全部可溯源 raw_id）。

    v2.0 阶段 8.2 候选草稿生成才产出 tool_result gold_candidates；
    本阶段不做 mock，删除无法溯源的残留文件并如实记录。
    """
    path = os.path.join(PROCESSED, "tool_result.jsonl")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            n = sum(1 for l in fh if l.strip())
        os.remove(path)
        return {"removed": True, "rows": n, "reason": "interim 源 gold_candidates_tool_result.jsonl 缺失，无法溯源"}
    return {"removed": False, "rows": 0, "reason": "不存在"}


def build_enum_dictionary():
    """从 processed 全量生成枚举字典（控制词表 + 模板族分布）。"""
    enums = {
        "task_type": set(), "source": set(), "template_family": set(),
        "preference_type": set(), "conflict_type": set(), "status": set(),
        "scope": set(), "operation": set(), "review_status": set(),
    }
    template_counts = {}
    for path in glob.glob(os.path.join(PROCESSED, "*.jsonl")):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                enums["task_type"].add(r.get("task_type"))
                enums["source"].add(r.get("source"))
                enums["review_status"].add(r.get("review_status"))
                tf = r.get("template_family")
                enums["template_family"].add(tf)
                template_counts[tf] = template_counts.get(tf, 0) + 1
                g = r.get("gold") or {}
                for k in ("preference_type", "conflict_type", "status", "scope", "operation"):
                    v = g.get(k)
                    if v:
                        enums[k].add(v)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "enum": {k: sorted(v) for k, v in enums.items() if v},
        "template_family_distribution": dict(sorted(template_counts.items(), key=lambda x: -x[1])),
    }
    with open(os.path.join(PROCESSED, "enum_dictionary.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return payload


def audit_processed():
    """对账：processed 全量必填字段 + timestamp 合法性 + raw_id 溯源（public_derived）。"""
    issues = {"missing_field": [], "invalid_ts": [], "missing_raw_id_public": []}
    total = 0
    for path in glob.glob(os.path.join(PROCESSED, "*.jsonl")):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                total += 1
                r = json.loads(line)
                sid = r.get("sample_id", path)
                for f in SCHEMA_REQUIRED:
                    if f not in r:
                        issues["missing_field"].append(f"{sid}:{f}")
                if not _valid_ts(r.get("timestamp")):
                    issues["invalid_ts"].append(f"{sid}:{r.get('timestamp')}")
                if r.get("source") == "public_derived" and not r.get("raw_id"):
                    issues["missing_raw_id_public"].append(sid)
    return total, issues


def main():
    s1 = convert_team_authored()
    s2 = convert_multiwoz_public_sample()
    s3 = convert_t2ranking_dev()
    s4 = convert_multiwoz_dialogues()
    s5 = handle_stale_tool_result()
    build_enum_dictionary()
    total, issues = audit_processed()

    print("== 转换对账 ==")
    print("[team_authored] files:", s1["files"])
    print("  input=", s1["input_rows"], "output=", s1["output_rows"],
          "fixed_ts=", s1["fixed_ts"], "unfixed_ts=", s1["unfixed_ts"], "silent_drop=", s1["silent_drop"])
    print("[multiwoz_public_sample] input=", s2["input_rows"], "output=", s2["output_rows"])
    print("[t2ranking_dev] input=", s3["input_rows"], "output=", s3["output_rows"], "drop=", s3["silent_drop"], s3.get("note", ""))
    print("[multiwoz_dialogues] input=", s4["input_rows"], "output=", s4["output_rows"], "drop=", s4["silent_drop"], s4.get("note", ""))
    print("[stale_tool_result]", s5)
    print("[audit] total=", total, "issues=", issues)
    print("== done ==")
    sys.exit(0 if not any(issues.values()) else 1)


if __name__ == "__main__":
    main()