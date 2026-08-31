# -*- coding: utf-8 -*-
"""Phase 8-10: gold candidate generation, split/seal, runtime package, download script."""

import csv
import hashlib
import json
import os
from pkg_config import DATE, PKG_ROOT
from pkg_phases_a import write


def _uid(prefix, n):
    return f"{prefix}_{n:06d}"


def _base(task_type, prefix, n, family, input_obj, gold_obj, evidence, conv_seed=1):
    return {
        "sample_id": _uid(prefix, n),
        "dataset_version": "kylin_memory_gold_v1.0",
        "task_type": task_type,
        "language": "zh-CN",
        "user_id": f"u_synthetic_{abs(hash(family)) % 100000:05d}_{conv_seed:02d}",
        "conversation_id": f"conv_{prefix}_{n:06d}",
        "timestamp": f"2026-07-2{n % 9 + 1:02d}T10:00:00+08:00",
        "input": input_obj,
        "gold": gold_obj,
        "evidence": evidence,
        "source": "team_authored",
        "template_family": family,
        "annotator_a": "",
        "annotator_b": "",
        "review_status": "candidate_only",
    }


def generate_gold():
    sets = {}

    pref_templates = [
        ("output_style_length_v1", "显式偏好", "以后项目周报用简洁要点，每条不超过两行，不要长篇段落。",
         {"preference_type": "output_style", "value": "周报用简洁要点，每条<=2行", "scope": "app", "confidence": "high", "should_store": True, "operation": "create"}),
        ("tool_choice_confirm_v1", "显式偏好", "需要删除文件前先问我确认，不要直接执行。",
         {"preference_type": "tool_choice", "value": "删除类工具执行前必须确认", "scope": "global", "confidence": "high", "should_store": True, "operation": "create"}),
        ("temp_instruction_v1", "单次临时要求", "这次就按英文回复，不用记住。",
         {"preference_type": "output_style", "value": "本次会话英文回复", "scope": "session", "confidence": "high", "should_store": False, "operation": "no_op"}),
        ("update_revoke_v1", "更新偏好", "之前说报告要详细，以后改成每节只写结论和关键数字。",
         {"preference_type": "output_style", "value": "报告每节只写结论和关键数字", "scope": "app", "confidence": "high", "should_store": True, "operation": "update", "old_value": "报告要详细"}),
        ("scope_app_v1", "作用域", "在这个项目管理工具里一律用中文标签，其他工具保持英文。",
         {"preference_type": "app", "value": "项目管理工具用中文标签", "scope": "app", "confidence": "high", "should_store": True, "operation": "create"}),
        ("sensitive_no_store_v1", "敏感偏好不可存储", "别记我的支付密码，也不要把付款信息写进记忆。",
         {"preference_type": "safety", "value": "不存储支付凭据", "scope": "global", "confidence": "high", "should_store": False, "operation": "no_op"}),
    ]
    pref = []
    for i in range(60):
        t = pref_templates[i % len(pref_templates)]
        n = i + 1
        pref.append(_base(
            "preference_extraction", "pref", n, t[0],
            {"user_message": t[2], "context": f"第 {n} 次会话上下文", "scene": "麒麟 OS 桌面助手"},
            t[3],
            [{"source_event_id": f"evt_pref_{n}", "span": t[2][:24]}],
            conv_seed=(i % 12) + 1,
        ))
    sets["preference_extraction"] = pref

    qtypes = [
        ("workflow_reuse", "以后软件安装失败先检查什么？", ["kb_case_001", "kb_workflow_003"], [3, 2],
         ["kb_case_014", "kb_template_006"], ["网络/DNS", "依赖与目标平台 Wheel"]),
        ("fact_knowledge", "麒麟 V11 默认包管理器是什么？", ["kb_fact_011"], [3],
         ["kb_fact_099"], ["yum/dnf", "官方软件源"]),
        ("history_case", "上次打印机卡纸是怎么解决的？", ["kb_case_018", "kb_case_020"], [3, 2],
         ["kb_case_031"], ["清纸路径", "重启打印服务"]),
        ("template_reuse", "月度备份的流程模板是什么？", ["kb_template_024"], [3],
         ["kb_template_091"], ["备份范围", "校验和步骤"]),
        ("failure_experience", "外接显示器不识别有哪些排查步骤？", ["kb_case_007", "kb_fact_013"], [3, 1],
         ["kb_case_042"], ["驱动状态", "线材与接口", "显示设置"]),
    ]
    retr = []
    for i in range(60):
        q = qtypes[i % len(qtypes)]
        n = i + 1
        rel = {r: s for r, s in zip(q[2], q[3])}
        retr.append(_base(
            "knowledge_retrieval", "retr", n, "os_knowledge_retrieval_v1",
            {"query": q[1], "query_type": q[0]},
            {"relevant_ids": q[2], "relevance": rel, "hard_negative_ids": q[4],
             "expected_answer_points": q[5]},
            [{"source_event_id": rid, "span": "知识文档内证据片段"} for rid in q[2]],
            conv_seed=(i % 8) + 1,
        ))
    sets["knowledge_retrieval"] = retr

    conflict_types = [
        ("time_update", "旧偏好“回答详细” → 新偏好“以后简短”", "新显式、同作用域、时间更晚，旧版本保留可回溯", "keep_new"),
        ("scope", "全局中文 vs 某应用要求英文", "应用级在该应用内优先，全局不被删除", "app_priority"),
        ("source", "用户手动配置 vs 行为推断", "显式配置优先，规则在标注手册固定", "explicit_config"),
        ("knowledge_version", "旧安装流程 vs 新版系统流程", "按系统版本、有效期和可信来源选择", "new_version"),
        ("safety", "效率偏好跳过确认 vs 安全策略要求确认", "安全策略优先，记录拒绝/降级", "safety_priority"),
    ]
    conf = []
    for i in range(40):
        t = conflict_types[i % len(conflict_types)]
        n = i + 1
        conf.append(_base(
            "conflict_resolution", "conf", n, f"conflict_{t[0]}_v1",
            {"conflict_type": t[0], "candidates": {"old": "旧记忆", "new": "新指令"}, "scenario": t[1]},
            {"conflict_type": t[0], "winner": t[3], "resolution_reason": t[2],
             "keep_ids": ["keep_001"], "remove_ids": ["remove_001"]},
            [{"source_event_id": f"evt_conf_{n}_a", "span": t[1][:20]},
             {"source_event_id": f"evt_conf_{n}_b", "span": t[2][:20]}],
            conv_seed=(i % 9) + 1,
        ))
    sets["conflict_resolution"] = conf

    forg = []
    for i in range(40):
        n = i + 1
        kind = i % 4
        if kind == 0:
            instr = "忘记我在 VSCode 中偏好深色主题，但保留其他开发偏好"
            target = ["pref_ui_theme_001"]
            keep = ["pref_editor_001", "pref_language_001"]
            family = "forget_scoped_v1"
        elif kind == 1:
            instr = "删除上周临时记录的文件路径，保留本周的记录"
            target = ["kb_path_009"]
            keep = ["kb_path_010"]
            family = "forget_time_v1"
        elif kind == 2:
            instr = "忘记某个客户姓名的所有关联记录，但保留流程知识"
            target = ["kb_person_012"]
            keep = ["kb_workflow_003"]
            family = "forget_person_v1"
        else:
            instr = "撤回刚才设置的桌面布局偏好，恢复系统默认"
            target = ["pref_ui_layout_021"]
            keep = ["pref_ui_theme_001"]
            family = "forget_revoke_v1"
        forg.append(_base(
            "precise_forgetting", "forg", n, family,
            {"forget_instruction": instr},
            {"target_ids": target, "expected_deleted": target, "must_keep": keep,
             "checkpoints": ["immediate_query", "after_restart", "after_full_reindex"],
             "expected_residual_count": 0},
            [{"source_event_id": f"evt_forg_{n}", "span": instr[:20]}],
            conv_seed=(i % 10) + 1,
        ))
    sets["precise_forgetting"] = forg

    tool_status = [
        ("success", "安装 python3-pip 成功，可沉淀步骤"),
        ("failed", "安装失败，原因是网络不可达，沉淀失败原因"),
        ("cancelled", "用户取消下载，不推断副作用"),
        ("timeout", "查询超时，标记未知状态"),
        ("partial_success", "备份完成但校验未通过，拆分成功与失败"),
    ]
    tool = []
    for i in range(50):
        t = tool_status[i % len(tool_status)]
        n = i + 1
        tool.append(_base(
            "tool_result", "tool", n, f"tool_status_{t[0]}_v1",
            {"tool": "shell", "args": f"command_{n}", "result_summary": t[1]},
            {"status": t[0], "persist_policy": "no" if t[0] == "cancelled" else "yes",
             "side_effect": "none" if t[0] in ("failed", "cancelled") else "recorded",
             "failure_reason": t[1]},
            [{"source_event_id": f"evt_tool_{n}", "span": t[1][:24]}],
            conv_seed=(i % 11) + 1,
        ))
    sets["tool_result"] = tool

    e2e = []
    for i in range(15):
        n = i + 1
        e2e.append(_base(
            "end_to_end_session", "e2e", n, "kylin_e2e_workflow_v1",
            {"turns": [
                {"role": "user", "content": f"帮我准备第 {n} 次项目发布检查"},
                {"role": "assistant", "content": "先检查版本号、备份和发布清单。"},
            ], "events": ["release_check", "backup", "deploy"]},
            {"expected_memory": {"version": f"v1.{n}", "status": "pending_review"},
             "expected_response": "发布前需完成备份与回归测试"},
            [{"source_event_id": f"evt_e2e_{n}_1", "span": "发布检查"},
             {"source_event_id": f"evt_e2e_{n}_2", "span": "备份"}],
            conv_seed=i + 1,
        ))
    sets["end_to_end_session"] = e2e
    return sets


def _family_bucket(family):
    h = int(hashlib.sha256(family.encode("utf-8")).hexdigest(), 16)
    r = h % 100
    if r < 50:
        return "dev"
    if r < 70:
        return "regression"
    return "sealed_test"


def phase9_split(gold_sets):
    import json as _json
    manifest_rows = []
    seal_rows = []
    leakage_rows = []
    for task_type, samples in gold_sets.items():
        buckets = {"dev": [], "regression": [], "sealed_test": []}
        for s in samples:
            buckets[_family_bucket(s["template_family"])].append(s)
        for split, items in buckets.items():
            path = os.path.join(PKG_ROOT, f"data/gold/{split}/{task_type}.jsonl")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                for s in items:
                    fh.write(_json.dumps(s, ensure_ascii=False) + "\n")
            h = sha256_text(path)
            manifest_rows.append([
                split, f"data/gold/{split}/{task_type}.jsonl", len(items),
                len(set(s["template_family"] for s in items)), h,
                "待 Reviewer 批准" if split == "sealed_test" else "否",
            ])
        # leakage check across buckets
        for split, items in buckets.items():
            ids = {s["sample_id"] for s in items}
            users = {s["user_id"] for s in items}
            convs = {s["conversation_id"] for s in items}
            fams = {s["template_family"] for s in items}
            for other_split, other_items in buckets.items():
                if other_split == split:
                    continue
                oids = {s["sample_id"] for s in other_items}
                ousers = {s["user_id"] for s in other_items}
                oconvs = {s["conversation_id"] for s in other_items}
                ofams = {s["template_family"] for s in other_items}
                leakage_rows.append([
                    task_type, split, other_split,
                    len(ids & oids), len(users & ousers), len(convs & oconvs), len(fams & ofams),
                    "PASS" if not (ids & oids or users & ousers or convs & oconvs or fams & ofams) else "FAIL",
                ])
    write(
        "registry/split_manifest.csv",
        csv_text(["split", "file", "samples", "template_families", "hash_sha256", "sealed"], manifest_rows),
    )
    write(
        "evidence/audit/leakage_report.md",
        f"""# 泄漏审计报告 {DATE}

切分规则：按 template_family 整体分配，dev 50% / regression 20% / sealed_test 30%。
检查项：sample_id、user_id、conversation_id、template_family 跨集合重复。

| 任务 | 集合 A | 集合 B | 样本重复 | 用户重复 | 会话重复 | 模板族重复 | 结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |
""" + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in leakage_rows) + """

结论：自建候选草稿按构造无跨集合泄漏；公开数据子集下载后需运行
`scripts/split/leakage_check.py` 对 user/conversation/workflow/template 重新审计。
""",
    )
    seal_lines = [
        f"# 封存记录 {DATE}",
        "",
        "- 封存对象：自建 Gold 候选草稿（candidate_only），非最终 Gold。",
        "- 封存状态：已生成哈希；Reviewer 批准前不得作为正式评测答案。",
        "- 权限：sealed_test 答案仅 Reviewer/评测负责人可见。",
        "- 变更纪律：任何改动至少 PATCH 版本并重新哈希、更新报告和审批。",
        "",
        "| 文件 | SHA256 |",
        "| --- | --- |",
    ]
    for row in manifest_rows:
        seal_lines.append(f"| {row[1]} | {row[4]} |")
    write("evidence/hashes/seal_record.md", "\n".join(seal_lines))


def sha256_text(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_text(headers, rows):
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)
    return buf.getvalue().replace("\r\n", "\n")


def write_download_script():
    targets = [
        {
            "dataset_id": "longmemeval_cleaned_2025",
            "urls": [
                "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_oracle.json",
                "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json",
            ],
            "note": "只下载 oracle（首选）或 S cleaned；不要下载 M 全量。",
        },
        {
            "dataset_id": "t2ranking_2023",
            "urls": [
                "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/queries.dev.tsv",
                "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/qrels.retrieval.dev.tsv",
                "https://huggingface.co/datasets/THUIR/T2Ranking/resolve/main/data/collection.tsv",
            ],
            "note": "collection 较大，可先用 dev 查询+qrels 作为小样本。",
        },
        {
            "dataset_id": "multiwoz_2_2_2020",
            "urls": [
                "https://raw.githubusercontent.com/budzianowski/multiwoz/master/data/MultiWOZ_2.2/dev/dialogues_001.json",
            ],
            "note": "dev 子集已下载并抽样 100 条；如需更多样本可下载 dialogues_002.json 或 train/test。",
        },
        {
            "dataset_id": "dureader_retrieval_2022",
            "urls": [],
            "note": "按百度官方 README/千言渠道下载，抽样 50-100 条。",
        },
        {
            "dataset_id": "stabletoolbench_2024",
            "urls": [
                "https://raw.githubusercontent.com/THUNLP-MT/StableToolBench/master/data_example/answer/answer.json",
            ],
            "note": "data_example 为官方样例；完整静态子集按官方发布渠道下载。",
        },
    ]
    lines = [
        "# -*- coding: utf-8 -*-",
        "\"\"\"Public dataset sample downloader. Usage: python download_samples.py --limit 100\"\"\"",
        "import argparse",
        "import json",
        "import os",
        "import ssl",
        "import sys",
        "import time",
        "import urllib.request",
        "",
        "TARGETS = " + json.dumps(targets, ensure_ascii=False, indent=4),
        "",
        "def fetch(url, out, timeout=120):",
        "    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE",
        "    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})",
        "    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:",
        "        data = resp.read()",
        "        with open(out, 'wb') as fh: fh.write(data)",
        "    return len(data)",
        "",
        "def main():",
        "    ap = argparse.ArgumentParser()",
        "    ap.add_argument('--dataset', default=None)",
        "    ap.add_argument('--limit', type=int, default=100)",
        "    ap.add_argument('--out', default='data/raw')",
        "    args = ap.parse_args()",
        "    for t in TARGETS:",
        "        if args.dataset and t['dataset_id'] != args.dataset: continue",
        "        print('[download]', t['dataset_id'], t['note'])",
        "        if not t['urls']:",
        "            print('  官方渠道需人工确认 URL，跳过。')",
        "            continue",
        "        for url in t['urls'][:2]:",
        "            fname = os.path.basename(url.split('?')[0]) or 'sample'",
        "            out = os.path.join(args.out, t['dataset_id'], 'v0_sample', fname)",
        "            os.makedirs(os.path.dirname(out), exist_ok=True)",
        "            try:",
        "                n = fetch(url, out)",
        "                print('  OK', fname, n, 'bytes')",
        "            except Exception as e:",
        "                print('  FAIL', url, str(e)[:120])",
        "    print('[done] Run sha256 and update manifests after downloads.')",
        "",
        "if __name__ == '__main__':",
        "    main()",
    ]
    write("scripts/download/download_samples.py", "\n".join(lines))
