#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P2-A 工具单测 v5（Data-B，2026-09-05）
R8 单测 + R9：T03 Registry 状态真判定、T04 near 逐对裁决、T11 sample invariant、真实链路。
运行：python scripts/v4/test_v4_tools.py
"""
import importlib.util
import json
import os
import shutil
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


def run(*args, **kw):
    return subprocess.run([sys.executable, os.path.join(V4, args[0]), *args[1:]], capture_output=True,
                          text=True, encoding="utf-8", **kw)


def load_mod(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(V4, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fixture(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return rel


def cleanup():
    shutil.rmtree(os.path.join(ROOT, "tmp_p2a_test"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT, "release"), ignore_errors=True)


# ---------------- T02 ----------------
def test_inventory_precedence():
    m = load_mod("inventory_legacy")
    check("inv_sid_over_raw_drift", m.identity({"sample_id": "s1", "raw_id": "r1"}) == m.identity({"sample_id": "s1", "raw_id": "r2"}))
    check("inv_raw_diff_task", m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"}) != m.identity({"raw_id": "r9", "task_type": "conflict", "source": "os"}))


# ---------------- T03 public Registry state ----------------
def _pub_cand(ds):
    return {"sample_id": "p1", "source": "public_direct",
            "source_file": "data/processed/knowledge_retrieval.jsonl",
            "design_metadata": {"generation": {"source_layer": "public_direct", "dataset_id": ds}}}


def test_t03_public_license_pending_fail():
    cleanup()
    # longmemeval_cleaned_2025：source 已核验，但 license reviewer=Reviewer（待批准）-> 应 FAIL
    fixture("tmp_p2a_test/pub.jsonl", json.dumps(_pub_cand("longmemeval_cleaned_2025")) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/pub.jsonl")
    check("t03_public_license_pending_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


def test_t03_public_source_partial_fail():
    cleanup()
    # personachat_2018：source 部分核验 -> FAIL
    fixture("tmp_p2a_test/pub.jsonl", json.dumps(_pub_cand("personachat_2018")) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/pub.jsonl")
    check("t03_public_source_partial_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


def test_t03_os_prompt_not_in_registry_fail():
    cleanup()
    fixture("registry/prompt_registry.csv", "prompt_id,version\nP20,v4.1\n")
    fixture("data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl", '{"sample_id":"x"}\n')
    cand = {"sample_id": "c1", "source": "os_controlled_authored",
            "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            "design_metadata": {"scenario_spec_id": "OSPREF-01",
                                "generation": {"source_layer": "os_controlled_authored", "generation_id": "g1",
                                               "prompt_version": "P999_NOPE", "seed": 1, "model": "m"}}}
    fixture("tmp_p2a_test/os.jsonl", json.dumps(cand) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/os.jsonl")
    check("t03_os_prompt_not_in_registry_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


def test_t03_os_scenario_not_found_fail():
    cleanup()
    fixture("registry/prompt_registry.csv", "prompt_id,version\nP20,v4.1\n")
    fixture("data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl", '{"sample_id":"x"}\n')
    cand = {"sample_id": "c1", "source": "os_controlled_authored",
            "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            "design_metadata": {"scenario_spec_id": "NO_SUCH_SCENARIO",
                                "generation": {"source_layer": "os_controlled_authored", "generation_id": "g1",
                                               "prompt_version": "P20", "seed": 1, "model": "m"}}}
    fixture("tmp_p2a_test/os.jsonl", json.dumps(cand) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/os.jsonl")
    check("t03_os_scenario_not_found_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


# ---------------- T04 near per-pair ----------------
def _dedup_cand(sid, text, fam="tf_a"):
    return {"sample_id": sid, "template_family": fam, "blind_visible": {"input": {"t": text}}}


def test_t04_near_only_one_decision_blocked():
    cleanup()
    # c1 与 c2、c3 均 near；只裁 (c1,c2) -> (c1,c3) 缺裁决 -> G4_near_reviewed False
    cands = "".join(json.dumps(_dedup_cand(s, t, "fam_%s" % i)) + "\n" for i, (s, t) in enumerate(
        [("c1", "每周五上午十点提醒交周报"), ("c2", "每周五上午十点提醒交周报吧"), ("c3", "每周五上午十点提醒交周报哟")]))
    fixture("tmp_p2a_test/cands.jsonl", cands)
    dec = {"near_duplicate_decisions": [{"a": "c1", "b": "c2", "decision": "ALLOW", "reviewer": "R", "reason": "ok"}]}
    fixture("tmp_p2a_test/dec.json", json.dumps(dec))
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--near-decisions", "tmp_p2a_test/dec.json",
            "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("t04_near_only_one_decision_blocked", r.returncode == 2 and rep.get("gates", {}).get("G4_near_reviewed") is False,
          "rc=%d gates=%s out=%s" % (r.returncode, rep.get("gates"), (r.stdout + r.stderr)[:150]))


def test_t04_near_unknown_pair_blocked():
    cleanup()
    cands = "".join(json.dumps(_dedup_cand(s, t, "fam_%s" % i)) + "\n" for i, (s, t) in enumerate(
        [("c1", "每周五上午十点提醒交周报"), ("c2", "每周五上午十点提醒交周报吧")]))
    fixture("tmp_p2a_test/cands.jsonl", cands)
    dec = {"near_duplicate_decisions": [{"a": "c1", "b": "ZZZ", "decision": "ALLOW", "reviewer": "R", "reason": "unknown"}]}
    fixture("tmp_p2a_test/dec.json", json.dumps(dec))
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--near-decisions", "tmp_p2a_test/dec.json",
            "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("t04_near_unknown_pair_blocked", r.returncode == 2 and rep.get("gates", {}).get("G4_near_reviewed") is False,
          "rc=%d gates=%s out=%s" % (r.returncode, rep.get("gates"), (r.stdout + r.stderr)[:150]))


# ---------------- T11 sample invariant ----------------
def test_t11_same_sid_diff_group_fail():
    cleanup()
    a = {"sample_id": "s1", "user_id": "u1", "conversation_id": "conv1", "template_family": "fa", "source": "os"}
    b = {"sample_id": "s1", "user_id": "u2", "conversation_id": "conv2", "template_family": "fb", "source": "os"}
    fixture("tmp_p2a_test/in.jsonl", json.dumps(a) + "\n" + json.dumps(b) + "\n")
    r = run("split_grouped.py", "--input", "tmp_p2a_test/in.jsonl")
    check("t11_same_sid_diff_group_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:200]))


def test_t11_empty_fail():
    cleanup()
    fixture("tmp_p2a_test/empty.jsonl", "")
    r = run("split_grouped.py", "--input", "tmp_p2a_test/empty.jsonl")
    check("t11_empty_fail", r.returncode == 2)


def main():
    test_inventory_precedence()
    test_t03_public_license_pending_fail()
    test_t03_public_source_partial_fail()
    test_t03_os_prompt_not_in_registry_fail()
    test_t03_os_scenario_not_found_fail()
    test_t04_near_only_one_decision_blocked()
    test_t04_near_unknown_pair_blocked()
    test_t11_same_sid_diff_group_fail()
    test_t11_empty_fail()
    cleanup()
    if FAILURES:
        print("\nRESULT: FAIL (%d)" % len(FAILURES))
        sys.exit(1)
    print("\nRESULT: ALL PASS")


if __name__ == "__main__":
    main()