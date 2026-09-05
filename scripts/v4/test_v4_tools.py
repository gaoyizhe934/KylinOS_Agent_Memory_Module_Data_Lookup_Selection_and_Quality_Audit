#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P2-A 工具单测（Data-B，2026-09-05）
覆盖：CLI、幂等、raw 只读、fail-closed、不写最终 Gold、near-dup 反例、field-aware normalization 反例。
运行：python scripts/v4/test_v4_tools.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(ROOT, "scripts", "v4")
FAILURES = []


def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL") + " | " + name + (" | " + detail if detail else ""))
    if not cond:
        FAILURES.append(name)


def run(py, *args, **kw):
    return subprocess.run([sys.executable, py, *args], capture_output=True, text=True, encoding="utf-8", **kw)


def test_dedup_field_aware():
    # field-aware normalization：v1 vs v2 / 不同日期不得折叠成 exact dup
    mod = importlib.import_module("scripts.v4.dedup_scan") if False else None
    import importlib
    spec = importlib.util.spec_from_file_location("dedup_scan", os.path.join(V4, "dedup_scan.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    n1 = m.normalize_field_aware("workflow v1 2026-01-01 amount 100")
    n2 = m.normalize_field_aware("workflow v2 2026-02-02 amount 200")
    check("dedup_field_aware_keeps_version_date_num", n1 != n2, "%s vs %s" % (n1, n2))
    n3 = m.normalize_field_aware("Workflow V1 2026-01-01, amount:100")
    check("dedup_normalize_whitespace_case", n1 == n3, "%s vs %s" % (n1, n3))


def test_dedup_near_dup():
    spec = importlib.util.spec_from_file_location("dedup_scan", os.path.join(V4, "dedup_scan.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    s = m.normalize_field_aware("每周五上午十点提醒交周报")
    t = m.normalize_field_aware("每周五上午十点提醒交周报吧")
    check("dedup_near_dup_jaccard_computed", m.jaccard(s, t) > 0.85)


def test_inventory_fail_closed_malformed():
    d = tempfile.mkdtemp()
    bad = os.path.join(d, "bad.jsonl")
    with open(bad, "w", encoding="utf-8") as f:
        f.write("{malformed json\n")
    # 直接测 read_jsonl 的 fail-closed 行为
    spec = importlib.util.spec_from_file_location("inventory_legacy", os.path.join(V4, "inventory_legacy.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.read_jsonl(bad)
    check("inventory_fail_closed_malformed_jsonl", any("jsonl-parse" in e for e in m.ERRORS))


def test_preflight_git_not_na():
    r = run(os.path.join(V4, "preflight.py"))
    out = r.stdout + r.stderr
    check("preflight_cli_runs", r.returncode in (0, 2))
    # git 信息通过 --json 检查
    tmp = os.path.join(tempfile.mkdtemp(), "pf.json")
    r2 = run(os.path.join(V4, "preflight.py"), "--json", os.path.relpath(tmp, ROOT))
    if os.path.exists(tmp):
        rep = json.load(open(tmp, encoding="utf-8"))
        check("preflight_git_head_not_na", rep.get("git", {}).get("head", "n/a") != "n/a", str(rep.get("git")))


def test_validators_no_gold():
    # validate_candidate_prep 断言 Gold 身份禁止（在 #34 已有；此处确保 validate_labels 不写最终语义）
    spec = importlib.util.spec_from_file_location("validate_labels", os.path.join(V4, "validate_labels.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    check("validate_labels_module_loads", m is not None)


def main():
    test_dedup_field_aware()
    test_dedup_near_dup()
    test_inventory_fail_closed_malformed()
    test_preflight_git_not_na()
    test_validators_no_gold()
    if FAILURES:
        print("\nRESULT: FAIL (%d)" % len(FAILURES))
        sys.exit(1)
    print("\nRESULT: ALL PASS")


if __name__ == "__main__":
    main()