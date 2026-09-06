#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P2-A 工具单测 v3（Data-B，2026-09-05）
覆盖 R7：inventory 优先级/canonical、admission zero/mismatch、provenance source-layer、
runtime build mismatch、split→seal wrong-split、seal gen missing/leak-mismatch/read-only、raw leak re-entry。
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


# ---------------- T02 inventory ----------------
def test_inventory_precedence():
    m = load_mod("inventory_legacy")
    # L1：同 sample_id，raw_id 漂移 -> 同组
    k1 = m.identity({"sample_id": "s1", "raw_id": "r1", "input": {"a": 1}})
    k2 = m.identity({"sample_id": "s1", "raw_id": "r2", "input": {"a": 2}})
    check("inventory_sid_over_raw_drift", k1 == k2, "%s vs %s" % (k1, k2))
    # L2：无 sid，同 raw 不同 task -> 不同组
    k3 = m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"})
    k4 = m.identity({"raw_id": "r9", "task_type": "conflict", "source": "os"})
    check("inventory_raw_different_task_diff_group", k3 != k4)
    # L2：无 sid，同 raw+task -> 同组
    k5 = m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"})
    check("inventory_raw_same_task_same_group", k3 == k5)
    # 同内容不同 sid -> 不同组
    k6 = m.identity({"sample_id": "a", "input": {"t": "x"}})
    k7 = m.identity({"sample_id": "b", "input": {"t": "x"}})
    check("inventory_same_content_diff_sid_diff_group", k6 != k7)


def test_inventory_canonical_exact_one():
    m = load_mod("inventory_legacy")
    # 手工分组：每组 2 条（1 IN_SCOPE + 1 DUP），验证组内 IN_SCOPE==1 且 duplicate_of 可解析
    groups = {
        ("L1", "s1"): [
            {"logical_group_id": "g1", "inventory_status": "IN_SCOPE", "sample_id": "s1", "duplicate_of": ""},
            {"logical_group_id": "g1", "inventory_status": "DUPLICATE_FILE", "sample_id": "s1x", "duplicate_of": "s1"},
        ],
        ("L1", "s2"): [
            {"logical_group_id": "g2", "inventory_status": "IN_SCOPE", "sample_id": "s2", "duplicate_of": ""},
        ],
    }
    ok = True
    for g, recs in groups.items():
        in_scope = [r for r in recs if r["inventory_status"] == "IN_SCOPE"]
        if len(in_scope) != 1:
            ok = False
        canonical = in_scope[0]["sample_id"]
        for r in recs:
            if r["inventory_status"] == "DUPLICATE_FILE" and r["duplicate_of"] != canonical:
                ok = False
    check("inventory_canonical_exact_one", ok)


# ---------------- T04 dedup ----------------
def test_dedup_field_aware():
    m = load_mod("dedup_scan")
    check("dedup_field_aware_keeps_version_date", m.normalize_field_aware("v1 2026-01-01 100") != m.normalize_field_aware("v2 2026-02-02 200"))
    check("dedup_near_dup", m.jaccard(m.normalize_field_aware("每周五上午十点提醒交周报"), m.normalize_field_aware("每周五上午十点提醒交周报吧")) > 0.85)


# ---------------- T06 admission ----------------
def _admission_fixture(g3_status):
    d = tempfile.mkdtemp()
    cleanup()
    prov = {"unresolved_count": 0, "checked_sample_ids": ["s1", "s2"],
            "input_set_hash": "h", "samples": {"s1": {"ok": True}, "s2": {"ok": True}}}
    dedup = {"exact_duplicate_groups": {}, "near_duplicate_count": 0, "template_over_concentration": [],
             "checked_sample_ids": ["s1", "s2"], "input_set_hash": "h"}
    leak = {"leak_count": 0, "checked_sample_ids": ["s1", "s2"], "input_set_hash": "h",
            "samples": {"s1": {"ok": True}, "s2": {"ok": True}}}
    g2 = "sample_id,gate2\ns1,PASS\ns2,PASS\n"
    g3 = "sample_id,gate3\ns1,%s\ns2,%s\n" % (g3_status, g3_status)
    cand = '{"sample_id": "s1", "task_type": "t"}\n{"sample_id": "s2", "task_type": "t"}\n'
    files = {"prov.json": json.dumps(prov), "dedup.json": json.dumps(dedup), "leak.json": json.dumps(leak),
             "g2.csv": g2, "g3.csv": g3, "cand.jsonl": cand}
    rels = {k: fixture("tmp_p2a_test/%s" % k, v) for k, v in files.items()}
    return rels


def test_admission_g3_pending_fail():
    rels = _admission_fixture("PENDING")
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cand.jsonl", "--prov", rels["prov.json"],
            "--dedup", rels["dedup.json"], "--leak", rels["leak.json"], "--semantic", rels["g2.csv"],
            "--annotatable", rels["g3.csv"])
    check("admission_g3_pending_fail", r.returncode == 2, "rc=%d" % r.returncode)


def test_admission_zero_candidate_fail():
    cleanup()
    prov = {"unresolved_count": 0, "checked_sample_ids": [], "input_set_hash": "h", "samples": {}}
    dedup = {"exact_duplicate_groups": {}, "near_duplicate_count": 0, "template_over_concentration": [], "checked_sample_ids": [], "input_set_hash": "h"}
    leak = {"leak_count": 0, "checked_sample_ids": [], "input_set_hash": "h", "samples": {}}
    g2 = "sample_id,gate2\n"; g3 = "sample_id,gate3\n"
    cand = fixture("tmp_p2a_test/empty.jsonl", "")
    for k, v in {"p.json": json.dumps(prov), "d.json": json.dumps(dedup), "l.json": json.dumps(leak),
                 "g2.csv": g2, "g3.csv": g3}.items():
        fixture("tmp_p2a_test/%s" % k, v)
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/empty.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/d.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("admission_zero_candidate_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:120]))


def test_admission_set_mismatch_fail():
    cleanup()
    prov = {"unresolved_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h",
            "samples": {"s1": {"ok": True}}}
    dedup = {"exact_duplicate_groups": {}, "near_duplicate_count": 0, "template_over_concentration": [],
             "checked_sample_ids": ["s1"], "input_set_hash": "h"}
    leak = {"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h", "samples": {"s1": {"ok": True}}}
    g2 = "sample_id,gate2\ns1,PASS\n"; g3 = "sample_id,gate3\ns1,PASS\n"
    cand = '{"sample_id": "s1", "task_type": "t"}\n{"sample_id": "sX", "task_type": "t"}\n'
    for k, v in {"p.json": json.dumps(prov), "d.json": json.dumps(dedup), "l.json": json.dumps(leak),
                 "g2.csv": g2, "g3.csv": g3, "cand.jsonl": cand}.items():
        fixture("tmp_p2a_test/%s" % k, v)
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cand.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/d.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("admission_set_mismatch_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


# ---------------- T03 provenance source-layer ----------------
def test_provenance_os_authored():
    d = tempfile.mkdtemp()
    cleanup()
    os.makedirs(os.path.join(ROOT, "registry"), exist_ok=True)
    if not os.path.exists(os.path.join(ROOT, "registry", "prompt_registry.csv")):
        fixture("registry/prompt_registry.csv", "prompt_id,version\nP20,v4.1\n")
    # 让 source_file locator 真实存在
    fixture("data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            '{"sample_id": "pref_v41_ex01", "source": "os_controlled_authored"}\n')
    cand = fixture("tmp_p2a_test/os_cand.jsonl",
                   json.dumps({"sample_id": "c1", "source": "os_controlled_authored",
                               "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
                               "design_metadata": {"generation": {
                                   "source_layer": "os_controlled_authored", "generation_id": "g1",
                                   "prompt_version": "P20", "seed": 1, "model": "m", "scenario_spec_id": "OSPREF-01"}}}) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/os_cand.jsonl")
    check("provenance_os_authored_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:200]))
    shutil.rmtree(d)


def test_provenance_public_requires_dataset_id():
    cleanup()
    cand = fixture("tmp_p2a_test/pub_cand.jsonl",
                   json.dumps({"sample_id": "p1", "source": "public_direct",
                               "source_file": "data/processed/knowledge_retrieval.jsonl",
                               "design_metadata": {"generation": {"source_layer": "public_direct"}}}) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/pub_cand.jsonl")
    check("provenance_public_requires_dataset_id_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


# ---------------- T10 runtime build mismatch ----------------
def test_runtime_build_mismatch():
    cleanup()
    d = tempfile.mkdtemp()
    log = os.path.join(d, "t.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write(json.dumps({"build_hash": "BBB", "trace_id": "t", "tool_call_id": "c",
                            "status": "success", "input_ref": "i", "output_ref": "o",
                            "side_effect_evidence": "s"}) + "\n")
    fixture("tmp_p2a_test/build.json", json.dumps({"build_hash": "AAA"}))
    r = run("runtime_import.py", "--logs", os.path.relpath(log, ROOT), "--build", "tmp_p2a_test/build.json", "--type", "tool")
    check("runtime_build_mismatch_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


# ---------------- T12 seal ----------------
def test_seal_wrong_split():
    cleanup()
    d = tempfile.mkdtemp()
    g = os.path.join(d, "gold.jsonl")
    with open(g, "w", encoding="utf-8") as f:
        f.write(json.dumps({"sample_id": "s1"}) + "\n")
    split = fixture("tmp_p2a_test/split_samples.csv", "sample_id,group_key,split\ns1,g1,dev\n")
    leak = fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h"}))
    exp = fixture("tmp_p2a_test/exposure.json", json.dumps({"dev_reg_only_samples": []}))
    rec = fixture("tmp_p2a_test/seal_record.json", json.dumps({"seal_generation": "seal-v2"}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/split_samples.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exposure.json",
            "--seal-record", "tmp_p2a_test/seal_record.json")
    check("seal_wrong_split_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


def test_seal_generation_missing():
    cleanup()
    d = tempfile.mkdtemp()
    g = os.path.join(d, "gold.jsonl")
    with open(g, "w", encoding="utf-8") as f:
        f.write(json.dumps({"sample_id": "s1"}) + "\n")
    fixture("tmp_p2a_test/split_samples.csv", "sample_id,group_key,split\ns1,g1,sealed_test\n")
    fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h"}))
    fixture("tmp_p2a_test/exposure.json", json.dumps({"dev_reg_only_samples": []}))
    fixture("tmp_p2a_test/seal_record.json", json.dumps({}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/split_samples.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exposure.json",
            "--seal-record", "tmp_p2a_test/seal_record.json")
    check("seal_generation_missing_fail", r.returncode == 2, "rc=%d" % r.returncode)


def test_seal_leak_set_mismatch():
    cleanup()
    d = tempfile.mkdtemp()
    g = os.path.join(d, "gold.jsonl")
    with open(g, "w", encoding="utf-8") as f:
        f.write(json.dumps({"sample_id": "s1"}) + "\n")
    fixture("tmp_p2a_test/split_samples.csv", "sample_id,group_key,split\ns1,g1,sealed_test\n")
    fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["other"], "input_set_hash": "h"}))
    fixture("tmp_p2a_test/exposure.json", json.dumps({"dev_reg_only_samples": []}))
    fixture("tmp_p2a_test/seal_record.json", json.dumps({"seal_generation": "seal-v2"}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/split_samples.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exposure.json",
            "--seal-record", "tmp_p2a_test/seal_record.json")
    check("seal_leak_set_mismatch_fail", r.returncode == 2, "rc=%d" % r.returncode)


# ---------------- T05 raw leak re-entry ----------------
def test_raw_leak_reentry():
    m = load_mod("leakage_scan")
    # 同 raw、新 sample_id、内容轻改 -> raw 指纹仍命中
    reg_entries = [{"sample_id": "old", "raw_id": "RAW-777", "template_family": "tf"}]
    leak_fps = set()
    leak_fps.add("sid:" + m.fp(str("old")))
    leak_fps.add("raw:" + m.fp(m.norm("RAW-777")))
    r = {"sample_id": "new_sid", "raw_id": "RAW-777", "template_family": "tf2",
         "blind_visible": {"input": {"t": "lightly changed"}}}
    hit = m.gen_fingerprints(r) & leak_fps
    check("raw_leak_reentry_hits", "raw:" + m.fp(m.norm("RAW-777")) in hit, str(hit))


def main():
    test_inventory_precedence()
    test_inventory_canonical_exact_one()
    test_dedup_field_aware()
    test_admission_g3_pending_fail()
    test_admission_zero_candidate_fail()
    test_admission_set_mismatch_fail()
    test_provenance_os_authored()
    test_provenance_public_requires_dataset_id()
    test_runtime_build_mismatch()
    test_seal_wrong_split()
    test_seal_generation_missing()
    test_seal_leak_set_mismatch()
    test_raw_leak_reentry()
    cleanup()
    if FAILURES:
        print("\nRESULT: FAIL (%d)" % len(FAILURES))
        sys.exit(1)
    print("\nRESULT: ALL PASS")


if __name__ == "__main__":
    main()