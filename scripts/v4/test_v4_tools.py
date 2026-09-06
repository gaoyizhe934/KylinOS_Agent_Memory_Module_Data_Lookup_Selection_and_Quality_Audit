#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P2-A 工具单测 v4（Data-B，2026-09-05）
R7 单测 + R8 真实链路集成：T04->T06 contract、exact/near/template block、#34 OS schema T03、
split invariant（group cross-split / sample conflict / 空输入）。
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


def _make_cands(rows):
    return "".join(json.dumps(r) + "\n" for r in rows)


# ---------------- T02 inventory ----------------
def test_inventory_precedence():
    m = load_mod("inventory_legacy")
    check("inventory_sid_over_raw_drift", m.identity({"sample_id": "s1", "raw_id": "r1"}) == m.identity({"sample_id": "s1", "raw_id": "r2"}))
    check("inventory_raw_different_task_diff_group", m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"}) != m.identity({"raw_id": "r9", "task_type": "conflict", "source": "os"}))
    check("inventory_raw_same_task_same_group", m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"}) == m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"}))
    check("inventory_same_content_diff_sid_diff_group", m.identity({"sample_id": "a", "input": {"t": "x"}}) != m.identity({"sample_id": "b", "input": {"t": "x"}}))


# ---------------- T04 dedup ----------------
def _dedup_cand(sid, text, fam="tf1"):
    return {"sample_id": sid, "template_family": fam, "blind_visible": {"input": {"t": text}}}


def test_dedup_outputs_contract():
    cleanup()
    cands = _make_cands([_dedup_cand("c1", "alpha beta gamma", "fam_a"), _dedup_cand("c2", "delta epsilon zeta", "fam_b")])
    fixture("tmp_p2a_test/cands.jsonl", cands)
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    check("dedup_runs_clean", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("dedup_contract_checked_sample_ids", sorted(rep.get("checked_sample_ids", [])) == ["c1", "c2"])
    check("dedup_contract_input_set_hash", bool(rep.get("input_set_hash")))
    check("dedup_contract_samples", set(rep.get("samples", {}).keys()) == {"c1", "c2"})


def test_dedup_exact_near_template():
    m = load_mod("dedup_scan")
    check("dedup_field_aware", m.normalize_field_aware("v1 2026-01-01 100") != m.normalize_field_aware("v2 2026-02-02 200"))
    check("dedup_near_dup", m.jaccard(m.normalize_field_aware("每周五上午十点提醒交周报"), m.normalize_field_aware("每周五上午十点提醒交周报吧")) > 0.85)


# ---------------- T04 -> T06 集成 ----------------
def _prov_leak_g23(sids, g2v="PASS", g3v="PASS"):
    prov = {"unresolved_count": 0, "checked_sample_ids": sorted(sids), "input_set_hash": "h",
            "samples": {s: {"ok": True, "reason": []} for s in sids}}
    leak = {"leak_count": 0, "checked_sample_ids": sorted(sids), "input_set_hash": "h",
            "samples": {s: {"ok": True, "hit": []} for s in sids}}
    g2 = "sample_id,gate2\n" + "".join("%s,%s\n" % (s, g2v) for s in sids)
    g3 = "sample_id,gate3\n" + "".join("%s,%s\n" % (s, g3v) for s in sids)
    for k, v in {"p.json": json.dumps(prov), "l.json": json.dumps(leak), "g2.csv": g2, "g3.csv": g3}.items():
        fixture("tmp_p2a_test/%s" % k, v)


def test_t04_t06_contract_integration():
    cleanup()
    cands = _make_cands([_dedup_cand("c1", "alpha beta gamma", "fam_a"), _dedup_cand("c2", "delta epsilon zeta", "fam_b")])
    fixture("tmp_p2a_test/cands.jsonl", cands)
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    check("t04_runs_clean", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))
    _prov_leak_g23(["c1", "c2"])
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cands.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("t04_t06_contract_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:200]))


def test_t06_exact_dup_block():
    cleanup()
    # 真实 dedup 会检出 exact dup -> dedup exit 2；T06 需真实 dedup report（含 exact）也应 BLOCKED
    cands = _make_cands([_dedup_cand("c1", "same same"), _dedup_cand("c2", "same same")])
    fixture("tmp_p2a_test/cands.jsonl", cands)
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    check("t04_exact_dup_detected", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:120]))
    _prov_leak_g23(["c1", "c2"])
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cands.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("t06_exact_dup_block", r.returncode == 2, "rc=%d" % r.returncode)


def test_t06_near_unreviewed_block():
    cleanup()
    cands = _make_cands([_dedup_cand("c1", "每周五上午十点提醒交周报"), _dedup_cand("c2", "每周五上午十点提醒交周报吧")])
    fixture("tmp_p2a_test/cands.jsonl", cands)
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    # near-dup UNREVIEWED -> dedup exit 2
    check("t04_near_unreviewed_blocked", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:120]))


# ---------------- T03 OS schema (#34 对齐) ----------------
def test_t03_os_exemplar_schema():
    cleanup()
    fixture("registry/prompt_registry.csv", "prompt_id,version\nP20,v4.1\n")
    fixture("data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            '{"sample_id": "pref_v41_ex01", "source": "os_controlled_authored"}\n')
    # 与 merge 后 #34 schema 一致：scenario_spec_id 在 design_metadata 层
    cand = {"sample_id": "c1", "source": "os_controlled_authored",
            "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            "design_metadata": {"scenario_spec_id": "OSPREF-01", "scenario_family": "os_pref_workflow",
                                "generation": {"source_layer": "os_controlled_authored", "generation_id": "g1",
                                               "prompt_version": "P20", "seed": 1, "model": "m"}}}
    fixture("tmp_p2a_test/os_cand.jsonl", json.dumps(cand) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/os_cand.jsonl")
    check("t03_os_exemplar_schema_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


# ---------------- T11/T12 split invariant ----------------
def test_seal_group_cross_split():
    cleanup()
    g = os.path.join(tempfile.mkdtemp(), "gold.jsonl")
    with open(g, "w", encoding="utf-8") as f:
        f.write('{"sample_id": "s1"}\n')
    fixture("tmp_p2a_test/split_samples.csv", "sample_id,group_key,split\ns1,g1,dev\ns2,g1,sealed_test\n")
    fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h"}))
    fixture("tmp_p2a_test/exposure.json", json.dumps({"dev_reg_only_samples": []}))
    fixture("tmp_p2a_test/seal_record.json", json.dumps({"seal_generation": "seal-v2"}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/split_samples.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exposure.json", "--seal-record", "tmp_p2a_test/seal_record.json")
    check("seal_group_cross_split_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


def test_seal_sample_conflict():
    cleanup()
    g = os.path.join(tempfile.mkdtemp(), "gold.jsonl")
    with open(g, "w", encoding="utf-8") as f:
        f.write('{"sample_id": "s1"}\n')
    fixture("tmp_p2a_test/split_samples.csv", "sample_id,group_key,split\ns1,g1,dev\ns1,g2,sealed_test\n")
    fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h"}))
    fixture("tmp_p2a_test/exposure.json", json.dumps({"dev_reg_only_samples": []}))
    fixture("tmp_p2a_test/seal_record.json", json.dumps({"seal_generation": "seal-v2"}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/split_samples.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exposure.json", "--seal-record", "tmp_p2a_test/seal_record.json")
    check("seal_sample_conflict_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


def test_split_empty_input():
    cleanup()
    fixture("tmp_p2a_test/empty.jsonl", "")
    r = run("split_grouped.py", "--input", "tmp_p2a_test/empty.jsonl")
    check("split_empty_input_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


def main():
    test_inventory_precedence()
    test_dedup_outputs_contract()
    test_dedup_exact_near_template()
    test_t04_t06_contract_integration()
    test_t06_exact_dup_block()
    test_t06_near_unreviewed_block()
    test_t03_os_exemplar_schema()
    test_seal_group_cross_split()
    test_seal_sample_conflict()
    test_split_empty_input()
    cleanup()
    if FAILURES:
        print("\nRESULT: FAIL (%d)" % len(FAILURES))
        sys.exit(1)
    print("\nRESULT: ALL PASS")


if __name__ == "__main__":
    main()