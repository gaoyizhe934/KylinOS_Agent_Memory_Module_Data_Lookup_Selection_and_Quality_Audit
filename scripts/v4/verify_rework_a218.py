#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data-A A218 rework 专项 verifier（PR #52 CI / 验收）
断言：
  1) counts 98/64/56, total=218
  2) 218 条均有 top-level template_family 且 == 独立 pinned scenario-spec authority family
  3) 输出 sample_id 集合与顺序 == 源（按文件）
  4) 字段不变量：对 output 删除 template_family 后，逐条 canonical == 源 candidate（仅新增该字段）
  5) mapping payload / manifest / output aggregate hash 与磁盘一致（--check 语义，非变异）
  6) 可选 --require-clean：git status --porcelain 为空（CI 专用，证明 check 不写文件）
用法：python scripts/v4/verify_rework_a218.py --repo <root> [--src ...][--dst ...][--source-commit ...][--require-clean]
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rework_a218 as RW  # noqa: E402

CANON = RW.canon
sha = RW.sha
nl = RW.nl


def run_check_assert(root, src_rel, dst_rel, commit):
    fails = []
    r = RW.compute(root, src_rel, dst_rel, commit)
    # 1) counts
    total = sum(o["count"] for o in r["outputs"])
    per = {o["file"].split("/")[-1]: o["count"] for o in r["outputs"]}
    if total != 218 or per.get("preference_candidates.jsonl") != 98 or per.get("conflict_candidates.jsonl") != 64 or per.get("forgetting_candidates.jsonl") != 56:
        fails.append("counts 98/64/56=218 violated: %s" % per)
    # 2) authority-consistent template_family + 3) order/set + 4) invariant
    auth, _ = RW.load_authority(root, commit)
    for fm, out in zip(r["src_meta"], r["outputs"]):
        src_rows = RW.read_jsonl_text(nl(RW.git_bytes(root, commit, fm["file"])).decode("utf-8"))
        out_rows = RW.read_jsonl_text(out["text"])
        if len(src_rows) != len(out_rows):
            fails.append("row count mismatch %s" % fm["file"]); continue
        for sline, oline in zip(src_rows, out_rows):
            s = json.loads(sline); o = json.loads(oline)
            if s["sample_id"] != o["sample_id"]:
                fails.append("order/set changed in %s" % fm["file"]); break
            tf = o.get("template_family")
            sid = o["design_metadata"]["scenario_spec_id"]
            if tf != auth.get(sid):
                fails.append("template_family %s != authority %s (%s)" % (tf, auth.get(sid), o["sample_id"]))
            oo = dict(o); oo.pop("template_family", None)
            if RW.canon(oo) != RW.canon(s):
                fails.append("field invariant violated (beyond template_family) in %s" % o["sample_id"])
    # 5) hash/files disk consistency (non-mutating)
    for o in r["outputs"]:
        p = os.path.join(root, o["file"])
        if not os.path.exists(p) or sha(nl(open(p, "rb").read())) != o["sha256_lf"]:
            fails.append("disk output hash mismatch %s" % o["file"])
    for rel, text in [("template_family_mapping_payload.json", r["mapping_payload"]["text"]),
                      ("rework_manifest_20260906.json", r["manifest_text"])]:
        p = os.path.join(root, dst_rel, rel)
        if not os.path.exists(p) or sha(nl(open(p, "rb").read())) != sha(text.encode("utf-8")):
            fails.append("disk %s mismatch" % rel)
    return fails, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--src", default="data/interim/d1_candidates_A_20260906")
    ap.add_argument("--dst", default="data/interim/d1_candidates_A_20260906_rw")
    ap.add_argument("--source-commit", default=RW.DEFAULT_COMMIT)
    ap.add_argument("--require-clean", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.repo)
    src_rel = RW.relpos(root, os.path.join(root, a.src))
    dst_rel = RW.relpos(root, os.path.join(root, a.dst))
    fails, r = run_check_assert(root, src_rel, dst_rel, a.source_commit)
    print("counts_total=%d input_manifest_payload_sha256=%s mapping_payload_sha256=%s output_aggregate=%s" % (
        sum(o["count"] for o in r["outputs"]), r["manifest"]["input_manifest_payload_sha256"],
        r["manifest"]["mapping_payload"]["sha256"], r["manifest"]["output_set_aggregate_sha256"]))
    if a.require_clean:
        st = subprocess.run(["git", "-C", root, "status", "--porcelain"], capture_output=True).stdout.decode("utf-8", "replace").strip()
        if st:
            fails.append("worktree not clean after --check:\n%s" % st)
    if fails:
        print("RESULT: FAIL (%d)" % len(fails))
        for f in fails[:40]:
            print(" -", f)
        sys.exit(1)
    print("RESULT: ALL PASS (non-mutating, deterministic, authority-consistent)")
    sys.exit(0)


if __name__ == "__main__":
    main()
