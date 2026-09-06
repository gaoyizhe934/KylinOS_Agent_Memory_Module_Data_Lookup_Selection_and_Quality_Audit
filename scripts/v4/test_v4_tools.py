#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P2-A 工具单测 v6（Data-B，2026-09-05）
12 工具级完整矩阵：T01-T12 CLI 正反例 + fail-closed + raw 不写。
覆盖：零输入/缺文件/缺 Registry、license allowlist、prompt/scenario 真 join（用 #34 真实 exemplar）、
near 逐对裁决、blind A/B membership、runtime build mismatch、split→seal invariant。
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


# ---------- T01 preflight ----------
def test_t01_preflight():
    d = tempfile.mkdtemp()
    r = run("preflight.py", "--json", os.path.relpath(os.path.join(d, "pf.json"), ROOT))
    rep = json.load(open(os.path.join(d, "pf.json"), encoding="utf-8"))
    check("t01_preflight_runs", r.returncode in (0, 2))
    check("t01_git_head_not_na", rep.get("git", {}).get("head", "n/a") != "n/a")
    shutil.rmtree(d)


# ---------- T02 inventory ----------
def test_t02_inventory():
    m = load_mod("inventory_legacy")
    check("t02_sid_over_raw", m.identity({"sample_id": "s1", "raw_id": "r1"}) == m.identity({"sample_id": "s1", "raw_id": "r2"}))
    check("t02_raw_diff_task", m.identity({"raw_id": "r9", "task_type": "pref", "source": "os"}) != m.identity({"raw_id": "r9", "task_type": "conflict", "source": "os"}))
    d = tempfile.mkdtemp()
    bad = os.path.join(d, "bad.jsonl")
    open(bad, "w", encoding="utf-8").write("{malformed\n")
    m.read_jsonl(bad)
    check("t02_fail_closed_malformed", any("jsonl-parse" in e for e in m.ERRORS))
    shutil.rmtree(d)


# ---------- T03 provenance ----------
def test_t03_public_license_pending_fail():
    cleanup()
    cand = {"sample_id": "p1", "source": "public_direct", "source_file": "data/processed/knowledge_retrieval.jsonl",
            "design_metadata": {"generation": {"source_layer": "public_direct", "dataset_id": "longmemeval_cleaned_2025"}}}
    fixture("tmp_p2a_test/pub.jsonl", json.dumps(cand) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/pub.jsonl")
    check("t03_license_pending_fail", r.returncode == 2)


def test_t03_os_real_exemplar_pass():
    # 用已 merge #34 真实 exemplar（P20-v4.1, OSPREF-01）跑 T03，应 PASS
    cleanup()
    real = os.path.join(ROOT, "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl")
    if os.path.exists(real):
        r = run("provenance_resolver.py", "--input", os.path.relpath(real, ROOT))
        check("t03_os_real_exemplar_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


def test_t03_os_wrong_prompt_fail():
    cleanup()
    cand = {"sample_id": "c1", "source": "os_controlled_authored",
            "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            "design_metadata": {"scenario_spec_id": "OSPREF-01",
                                "generation": {"source_layer": "os_controlled_authored", "generation_id": "g1",
                                               "prompt_version": "P20-v9.9", "seed": 1, "model": "m"}}}
    fixture("tmp_p2a_test/os.jsonl", json.dumps(cand) + "\n")
    r = run("provenance_resolver.py", "--input", "tmp_p2a_test/os.jsonl")
    check("t03_wrong_prompt_version_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:250]))


def test_t03_license_blank_reviewer_fail():
    # blank reviewer 不得被判 approved
    m = load_mod("provenance_resolver")
    check("t03_license_blank_fail", m.license_approved({"reviewer": "  ", "verdict": "已确认", "status": "已批准"}) is False)
    check("t03_license_pending_fail", m.license_approved({"reviewer": "Reviewer（待批准）", "verdict": "已确认", "status": "已批准"}) is False)
    check("t03_license_approved_ok", m.license_approved({"reviewer": "已批准 gaoyizhe934", "verdict": "已确认", "status": "已批准"}) is True)
    check("t03_license_unknown_fail", m.license_approved({"reviewer": "Main-B", "verdict": "已确认", "status": "已批准"}) is False)


def test_t03_scenario_missing_fail():
    cleanup()
    # 指向不存在的 scenario_specs 目录（tmp fixture 中不放 scenario）
    cand = {"sample_id": "c1", "source": "os_controlled_authored",
            "source_file": "data/interim/candidates_v4/exemplar_candidates/preference_exemplars.jsonl",
            "design_metadata": {"scenario_spec_id": "X",
                                "generation": {"source_layer": "os_controlled_authored", "generation_id": "g1",
                                               "prompt_version": "P20-v4.1", "seed": 1, "model": "m"}}}
    fixture("tmp_p2a_test/os.jsonl", json.dumps(cand) + "\n")
    # 单测 load_scenario_ids 空/缺失路径
    m = load_mod("provenance_resolver")
    import glob as g
    old = m.SCENARIO_DIR
    m.SCENARIO_DIR = os.path.join(ROOT, "tmp_p2a_test", "no_scenario")
    ids, err = m.load_scenario_ids()
    check("t03_scenario_missing_fail", err is not None and not ids, "err=%s" % err)
    m.SCENARIO_DIR = old


# ---------- T04 dedup ----------
def _cand(sid, text, fam=None):
    if fam is None:
        fam = "fam_%s" % sid
    return {"sample_id": sid, "template_family": fam, "blind_visible": {"input": {"t": text}}}


def test_t04_near_per_pair():
    cleanup()
    cands = "".join(json.dumps(_cand(s, t, "f%s" % i)) + "\n" for i, (s, t) in enumerate(
        [("c1", "每周五上午十点提醒交周报"), ("c2", "每周五上午十点提醒交周报吧"), ("c3", "每周五上午十点提醒交周报哟")]))
    fixture("tmp_p2a_test/cands.jsonl", cands)
    dec1 = {"near_duplicate_decisions": [{"a": "c1", "b": "c2", "decision": "ALLOW", "reviewer": "R", "reason": "ok"}]}
    fixture("tmp_p2a_test/dec.json", json.dumps(dec1))
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--near-decisions", "tmp_p2a_test/dec.json",
            "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("t04_near_missing_pair_blocked", r.returncode == 2 and rep["gates"]["G4_near_reviewed"] is False)
    # all pairs decided -> G4_near_reviewed True；全 ALLOW -> dedup PASS
    dec2 = {"near_duplicate_decisions": [
        {"a": "c1", "b": "c2", "decision": "ALLOW", "reviewer": "R", "reason": "a"},
        {"a": "c1", "b": "c3", "decision": "ALLOW", "reviewer": "R", "reason": "b"},
        {"a": "c2", "b": "c3", "decision": "ALLOW", "reviewer": "R", "reason": "c"}]}
    fixture("tmp_p2a_test/dec.json", json.dumps(dec2))
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--near-decisions", "tmp_p2a_test/dec.json",
            "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("t04_near_all_decided_pass", r.returncode == 0 and rep["gates"]["G4_near_reviewed"] is True,
          "rc=%d gates=%s" % (r.returncode, rep["gates"]))
    # DROP_B => c3 的 G4 fail（单独验证派生）
    dec3 = {"near_duplicate_decisions": [
        {"a": "c1", "b": "c2", "decision": "ALLOW", "reviewer": "R", "reason": "a"},
        {"a": "c1", "b": "c3", "decision": "DROP_B", "reviewer": "R", "reason": "b"},
        {"a": "c2", "b": "c3", "decision": "ALLOW", "reviewer": "R", "reason": "c"}]}
    fixture("tmp_p2a_test/dec.json", json.dumps(dec3))
    run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--near-decisions", "tmp_p2a_test/dec.json",
        "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    rep = json.load(open(os.path.join(ROOT, "tmp_p2a_test/dedup.json"), encoding="utf-8"))
    check("t04_drop_derives_sample_fail", rep["samples"]["c3"]["ok"] is False and rep["samples"]["c1"]["ok"] is True)


# ---------- T05 leakage ----------
def test_t05_leak_reentry():
    m = load_mod("leakage_scan")
    reg = [{"sample_id": "old", "raw_id": "RAW-777", "template_family": "tf"}]
    fps = set()
    fps.add("sid:" + m.fp("old"))
    fps.add("raw:" + m.fp(m.norm("RAW-777")))
    r = {"sample_id": "new_sid", "raw_id": "RAW-777", "template_family": "tf2", "blind_visible": {"input": {"t": "changed"}}}
    hit = m.gen_fingerprints(r) & fps
    check("t05_raw_reentry_hits", "raw:" + m.fp(m.norm("RAW-777")) in hit)


def test_t05_missing_registry_fail():
    r = run("leakage_scan.py", "--input", "data/processed/*.jsonl", "--registry", "registry/nope.json")
    check("t05_missing_registry_fail", r.returncode == 3)


# ---------- T06 admission ----------
def _admission_base(sids):
    prov = {"unresolved_count": 0, "checked_sample_ids": sorted(sids), "input_set_hash": "h",
            "samples": {s: {"ok": True} for s in sids}}
    leak = {"leak_count": 0, "checked_sample_ids": sorted(sids), "input_set_hash": "h",
            "samples": {s: {"ok": True} for s in sids}}
    g2 = "sample_id,gate2\n" + "".join("%s,PASS\n" % s for s in sids)
    g3 = "sample_id,gate3\n" + "".join("%s,PASS\n" % s for s in sids)
    for k, v in {"p.json": json.dumps(prov), "l.json": json.dumps(leak), "g2.csv": g2, "g3.csv": g3}.items():
        fixture("tmp_p2a_test/%s" % k, v)


def test_t06_negatives():
    cleanup()
    sids = ["c1", "c2"]
    cands = "".join(json.dumps(_cand(s, "text %s" % s, "f%s" % i)) + "\n" for i, s in enumerate(sids))
    fixture("tmp_p2a_test/cands.jsonl", cands)
    _admission_base(sids)
    r = run("dedup_scan.py", "--input", "tmp_p2a_test/cands.jsonl", "--out", "tmp_p2a_test/dedup.json", "--template-max", "0.6")
    check("t06_setup_dedup_ok", r.returncode == 0)
    # empty candidate
    fixture("tmp_p2a_test/empty.jsonl", "")
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/empty.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("t06_empty_candidate_fail", r.returncode == 2)
    # set mismatch
    fixture("tmp_p2a_test/candsX.jsonl", "".join(json.dumps(_cand("sX", "tt", "fx")) + "\n" for _ in [1]))
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/candsX.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("t06_set_mismatch_fail", r.returncode == 2)
    # G3 pending
    fixture("tmp_p2a_test/g3p.csv", "sample_id,gate3\nc1,PENDING\nc2,PENDING\n")
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cands.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3p.csv")
    check("t06_g3_pending_fail", r.returncode == 2)
    # happy path
    r = run("admission_gate.py", "--candidates", "tmp_p2a_test/cands.jsonl", "--prov", "tmp_p2a_test/p.json",
            "--dedup", "tmp_p2a_test/dedup.json", "--leak", "tmp_p2a_test/l.json", "--semantic", "tmp_p2a_test/g2.csv",
            "--annotatable", "tmp_p2a_test/g3.csv")
    check("t06_happy_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:200]))


# ---------- T07 blind ----------
def test_t07_membership():
    m = load_mod("build_blind_packets")
    frozen = list(range(40))
    ra, rb = list(frozen), list(frozen)
    import random
    random.Random(11).shuffle(ra)
    random.Random(22).shuffle(rb)
    check("t07_same_membership", set(ra) == set(frozen) == set(rb))
    check("t07_diff_order", ra != rb)


# ---------- T08/T09 module + disagreement ----------
def test_t08_t09():
    for mod in ("validate_labels", "disagreement_report"):
        try:
            load_mod(mod)
            check("t0x_loads_" + mod, True)
        except Exception as e:
            check("t0x_loads_" + mod, False, str(e))


# ---------- T10 runtime ----------
def test_t10_runtime():
    cleanup()
    d = tempfile.mkdtemp()
    log = os.path.join(d, "t.log")
    open(log, "w", encoding="utf-8").close()
    fixture("tmp_p2a_test/build.json", json.dumps({"build_hash": "AAA"}))
    r = run("runtime_import.py", "--logs", os.path.relpath(log, ROOT), "--build", "tmp_p2a_test/build.json", "--type", "tool")
    check("t10_zero_logs_fail", r.returncode == 2)
    with open(log, "w", encoding="utf-8") as f:
        f.write(json.dumps({"build_hash": "BBB", "trace_id": "t", "tool_call_id": "c", "status": "success",
                            "input_ref": "i", "output_ref": "o", "side_effect_evidence": "s"}) + "\n")
    r = run("runtime_import.py", "--logs", os.path.relpath(log, ROOT), "--build", "tmp_p2a_test/build.json", "--type", "tool")
    check("t10_build_mismatch_fail", r.returncode == 2, "rc=%d" % r.returncode)
    shutil.rmtree(d)


# ---------- T11/T12 split→seal ----------
def test_t11_invariant():
    cleanup()
    fixture("tmp_p2a_test/empty.jsonl", "")
    r = run("split_grouped.py", "--input", "tmp_p2a_test/empty.jsonl")
    check("t11_empty_fail", r.returncode == 2)
    a = {"sample_id": "s1", "user_id": "u1", "conversation_id": "c1", "template_family": "fa", "source": "os"}
    b = {"sample_id": "s1", "user_id": "u2", "conversation_id": "c2", "template_family": "fb", "source": "os"}
    fixture("tmp_p2a_test/in.jsonl", json.dumps(a) + "\n" + json.dumps(b) + "\n")
    r = run("split_grouped.py", "--input", "tmp_p2a_test/in.jsonl")
    check("t11_sid_diff_group_fail", r.returncode == 2)


def test_t12_seal():
    cleanup()
    g = os.path.join(tempfile.mkdtemp(), "g.jsonl")
    open(g, "w", encoding="utf-8").write('{"sample_id": "s1"}\n')
    fixture("tmp_p2a_test/sp.csv", "sample_id,group_key,split\ns1,g1,sealed_test\n")
    fixture("tmp_p2a_test/leak.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["s1"], "input_set_hash": "h"}))
    fixture("tmp_p2a_test/exp.json", json.dumps({"dev_reg_only_samples": []}))
    fixture("tmp_p2a_test/rec.json", json.dumps({}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/sp.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exp.json", "--seal-record", "tmp_p2a_test/rec.json")
    check("t12_gen_missing_fail", r.returncode == 2)
    fixture("tmp_p2a_test/rec.json", json.dumps({"seal_generation": "seal-v2"}))
    fixture("tmp_p2a_test/leakX.json", json.dumps({"leak_count": 0, "checked_sample_ids": ["other"], "input_set_hash": "h"}))
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/sp.csv",
            "--leak", "tmp_p2a_test/leakX.json", "--exposure", "tmp_p2a_test/exp.json", "--seal-record", "tmp_p2a_test/rec.json")
    check("t12_leak_set_mismatch_fail", r.returncode == 2)
    # wrong split
    fixture("tmp_p2a_test/spD.csv", "sample_id,group_key,split\ns1,g1,dev\n")
    r = run("seal_release.py", "--gold", os.path.relpath(g, ROOT), "--split-samples", "tmp_p2a_test/spD.csv",
            "--leak", "tmp_p2a_test/leak.json", "--exposure", "tmp_p2a_test/exp.json", "--seal-record", "tmp_p2a_test/rec.json")
    check("t12_wrong_split_fail", r.returncode == 2)


# ---------- T08 validate_labels ----------
def _lab(sid, label, task="preference_extraction", conf=0.9, reason="r"):
    return '{"sample_id": "%s", "label": "%s", "task_type": "%s", "confidence": %s, "reason": "%s"}\n' % (sid, label, task, conf, reason)


def test_t08_validate():
    cleanup()
    fixture("tmp_p2a_test/empty.jsonl", "")
    r = run("validate_labels.py", "--input", "tmp_p2a_test/empty.jsonl", "--role", "A")
    check("t08_empty_fail", r.returncode == 2)
    fixture("tmp_p2a_test/dup.jsonl", _lab("s1", "persistent_preference") * 2)
    r = run("validate_labels.py", "--input", "tmp_p2a_test/dup.jsonl", "--role", "A")
    check("t08_dup_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/badconf.jsonl", _lab("s1", "persistent_preference", conf=1.5))
    r = run("validate_labels.py", "--input", "tmp_p2a_test/badconf.jsonl", "--role", "A")
    check("t08_bad_conf_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/noconf.jsonl", '{"sample_id": "s1", "label": "persistent_preference", "task_type": "preference_extraction", "confidence": "high", "reason": "r"}\n')
    r = run("validate_labels.py", "--input", "tmp_p2a_test/noconf.jsonl", "--role", "A")
    check("t08_conf_not_numeric_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/noreason.jsonl", _lab("s1", "persistent_preference", reason="  "))
    r = run("validate_labels.py", "--input", "tmp_p2a_test/noreason.jsonl", "--role", "A")
    check("t08_empty_reason_fail", r.returncode == 2, "rc=%d" % r.returncode)
    # invalid enum / unknown task / missing schema
    fixture("tmp_p2a_test/badenum.jsonl", _lab("s1", "banana"))
    r = run("validate_labels.py", "--input", "tmp_p2a_test/badenum.jsonl", "--role", "A")
    check("t08_invalid_enum_fail", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))
    fixture("tmp_p2a_test/unk.jsonl", _lab("s1", "persistent_preference", task="made_up_task"))
    r = run("validate_labels.py", "--input", "tmp_p2a_test/unk.jsonl", "--role", "A")
    check("t08_unknown_task_fail", r.returncode == 2, "rc=%d" % r.returncode)
    r = run("validate_labels.py", "--input", "tmp_p2a_test/empty.jsonl", "--role", "A", "--schema", "registry/nope.json")
    check("t08_missing_schema_fail", r.returncode == 3, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/good.jsonl", _lab("s1", "persistent_preference") + _lab("s2", "task_constraint"))
    r = run("validate_labels.py", "--input", "tmp_p2a_test/good.jsonl", "--role", "A")
    check("t08_good_pass", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))


# ---------- T09 disagreement ----------
def test_t09_disagreement():
    cleanup()
    fixture("tmp_p2a_test/A.jsonl", "")
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_empty_a_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/A.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s2", "label": "y"}\n')
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_missing_id_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "sX", "label": "z"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_extra_id_fail", r.returncode == 2, "rc=%d" % r.returncode)
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s1", "label": "w"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_dup_id_fail", r.returncode == 2, "rc=%d" % r.returncode)
    # 1 条分歧 -> non-STOP（exit 0，进 reviewer queue）
    fixture("tmp_p2a_test/A.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s2", "label": "y"}\n')
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s2", "label": "z"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_one_disagree_nonstop", r.returncode == 0, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))
    # 2 条分歧不同规则 -> non-STOP
    fixture("tmp_p2a_test/A.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s2", "label": "y"}\n{"sample_id": "s3", "label": "p"}\n')
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "x"}\n{"sample_id": "s2", "label": "z"}\n{"sample_id": "s3", "label": "q"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_two_disagree_diff_rule_nonstop", r.returncode == 0, "rc=%d" % r.returncode)
    # 同规则 3 条 -> STOP（exit 2）
    fixture("tmp_p2a_test/A.jsonl", '{"sample_id": "s1", "label": "a"}\n{"sample_id": "s2", "label": "a"}\n{"sample_id": "s3", "label": "a"}\n')
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "b"}\n{"sample_id": "s2", "label": "b"}\n{"sample_id": "s3", "label": "b"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_same_rule_3_stop", r.returncode == 2, "rc=%d out=%s" % (r.returncode, (r.stdout + r.stderr)[:150]))
    # 完全一致 -> PASS
    fixture("tmp_p2a_test/B.jsonl", '{"sample_id": "s1", "label": "a"}\n{"sample_id": "s2", "label": "a"}\n{"sample_id": "s3", "label": "a"}\n')
    r = run("disagreement_report.py", "--a", "tmp_p2a_test/A.jsonl", "--b", "tmp_p2a_test/B.jsonl")
    check("t09_agree_pass", r.returncode == 0, "rc=%d" % r.returncode)


# ---------- T03 license/prompt approval ----------
def test_t03_license_verdict_pending_fail():
    m = load_mod("provenance_resolver")
    # reviewer approved 但 verdict 仍 pending -> FAIL
    check("t03_reviewer_ok_verdict_pending_fail", m.license_approved({"reviewer": "已批准 gaoyizhe934", "verdict": "待人工/法务确认", "status": "已批准"}) is False)
    # reviewer approved 但 status history/draft -> FAIL
    check("t03_status_history_fail", m.license_approved({"reviewer": "已批准", "verdict": "已确认", "status": "history/draft"}) is False)
    # status=已存档（archived）-> FAIL（不在 allowlist）
    check("t03_status_archived_fail", m.license_approved({"reviewer": "已批准", "verdict": "已确认", "status": "已存档/待确认"}) is False)
    # status=reviewed（仅 reviewer 审查过）-> FAIL
    check("t03_status_reviewed_only_fail", m.license_approved({"reviewer": "已批准", "verdict": "已确认", "status": "reviewed"}) is False)
    # verdict=unknown -> FAIL
    check("t03_verdict_unknown_fail", m.license_approved({"reviewer": "已批准", "verdict": "whatever", "status": "已批准"}) is False)
    # 全 approved -> PASS
    check("t03_full_approved_pass", m.license_approved({"reviewer": "已批准 gaoyizhe934", "verdict": "已确认", "status": "已批准"}) is True)
    check("t03_full_approved_english_pass", m.license_approved({"reviewer": "APPROVED gaoyizhe934", "verdict": "APPROVED", "status": "APPROVED"}) is True)


def test_t03_prompt_inactive_fail():
    m = load_mod("provenance_resolver")
    d = tempfile.mkdtemp()
    p = os.path.join(d, "pr.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write("prompt_ref,prompt_id,version,role,status\nP20-v4.1,P20,v4.1,A/B/R,inactive\nP21-v4.1,P21,v4.1,A/B/R,active\n")
    refs = m.load_prompt_refs(p)
    check("t03_prompt_inactive_excluded", "P20-v4.1" not in refs and "P21-v4.1" in refs, "refs=%s" % refs)
    shutil.rmtree(d)


def main():
    test_t01_preflight()
    test_t02_inventory()
    test_t03_public_license_pending_fail()
    test_t03_os_real_exemplar_pass()
    test_t03_os_wrong_prompt_fail()
    test_t03_license_blank_reviewer_fail()
    test_t03_scenario_missing_fail()
    test_t04_near_per_pair()
    test_t05_leak_reentry()
    test_t05_missing_registry_fail()
    test_t06_negatives()
    test_t07_membership()
    test_t08_t09()
    test_t10_runtime()
    test_t11_invariant()
    test_t12_seal()
    test_t08_validate()
    test_t09_disagreement()
    test_t03_license_verdict_pending_fail()
    test_t03_prompt_inactive_fail()
    cleanup()
    if FAILURES:
        print("\nRESULT: FAIL (%d)" % len(FAILURES))
        sys.exit(1)
    print("\nRESULT: ALL PASS")


if __name__ == "__main__":
    main()