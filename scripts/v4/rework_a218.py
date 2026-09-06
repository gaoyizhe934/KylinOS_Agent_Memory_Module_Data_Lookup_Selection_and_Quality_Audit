#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data-A A218 rework（repo-relative, deterministic, fail-closed）

给 A218（98/64/56）OS-authored factory candidates 补 top-level `template_family`。
取值 = design_metadata.scenario_family（generation-template family；identity mapping 提案，
完整 mapping payload 见同批 mapping 文件 —— 未获 Data-R 批准前不视为 authority）。

用法：
  python scripts/v4/rework_a218.py --repo <repo> --src data/interim/d1_candidates_A_20260906 \
        --dst data/interim/d1_candidates_A_20260906_rw
  python scripts/v4/rework_a218.py --check   # 重生成与磁盘 byte 比对（CI/可复现）
fail-closed：
  - 源 3 文件存在、行数与计划 98/64/56 一致、total=218
  - 每条原始候选不得已含 top-level template_family
  - scenario_spec_id/scenario_family 必须存在且命中 mapping payload（identity）
  - 重跑 canonical byte 一致；hash 与 manifest 一致，否则 exit 1
"""
import argparse
import glob
import hashlib
import json
import os
import sys

CANON = dict(ensure_ascii=False, sort_keys=True, separators=(",", ":"))

PLAN = {"preference_candidates.jsonl": 98, "conflict_candidates.jsonl": 64,
        "forgetting_candidates.jsonl": 56}
SRC_FILES = sorted(PLAN)


def canon(o):
    return json.dumps(o, **CANON)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def nl(b):
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def lf_sha(path):
    with open(path, "rb") as f:
        return sha(nl(f.read()))


def load_manifest(dst):
    with open(os.path.join(dst, "rework_manifest_20260906.json"), encoding="utf-8") as f:
        return json.load(f)


def run(root, src, dst):
    os.makedirs(dst, exist_ok=True)
    src_meta = {}
    input_manifest_parts = []
    for fn in SRC_FILES:
        p = os.path.join(root, src, fn)
        if not os.path.exists(p):
            raise SystemExit("missing source: %s" % p)
        fh = lf_sha(p)
        src_meta[fn] = {"file": os.path.join(src, fn), "count_plan": PLAN[fn], "sha256_lf": fh}
        input_manifest_parts.append({"file": os.path.join(src, fn), "count_plan": PLAN[fn], "sha256_lf": fh})

    outputs = []
    total_in = total_out = 0
    mapping = {}
    for fn in SRC_FILES:
        p = os.path.join(root, src, fn)
        text = nl(open(p, "rb").read()).decode("utf-8")
        rows = [l for l in text.splitlines() if l.strip()]
        if len(rows) != PLAN[fn]:
            raise SystemExit("count mismatch %s: got %d want %d" % (fn, len(rows), PLAN[fn]))
        body = []
        for line in rows:
            r = json.loads(line)
            total_in += 1
            if "template_family" in r:
                raise SystemExit("already has template_family: %s" % r["sample_id"])
            sid_ref = r["design_metadata"].get("scenario_spec_id")
            fam = r["design_metadata"].get("scenario_family")
            if not sid_ref or not fam:
                raise SystemExit("missing scenario spec/family: %s" % r["sample_id"])
            mapping[sid_ref] = {"scenario_spec_id": sid_ref, "scenario_family": fam,
                                "template_family": fam, "mapping_kind": "identity"}
            r["template_family"] = fam
            body.append(canon(r))
        out_text = "\n".join(body) + "\n"
        out_p = os.path.join(dst, fn)
        open(out_p, "w", encoding="utf-8").write(out_text)
        total_out += len(body)
        outputs.append({"file": os.path.join(dst, fn).replace("\\", "/").replace(root + "/", ""),
                        "count": len(body), "sha256_lf": sha(out_text.encode("utf-8"))})
    if total_in != 218 or total_out != 218:
        raise SystemExit("total != 218: in=%d out=%d" % (total_in, total_out))

    # mapping payload（scenario_spec_id -> family identity）
    mapping_payload = {"mapping_kind": "identity_scenario_family_to_template_family",
                       "count": len(mapping), "mapping": mapping}
    mp_path = os.path.join(dst, "template_family_mapping_payload.json")
    open(mp_path, "w", encoding="utf-8").write(canon(mapping_payload) + "\n")
    mapping_payload_sha = sha(canon(mapping_payload).encode("utf-8"))

    input_manifest_payload_sha = sha(canon(sorted(input_manifest_parts, key=lambda x: x["file"])).encode("utf-8"))
    output_set_aggregate_sha = sha(canon(sorted(outputs, key=lambda x: x["file"])).encode("utf-8"))

    manifest = {
        "schema": "v4.1_A_A218_rework_manifest_v2", "date": "2026-09-06", "role": "Data-A (lyf-1213)",
        "repo_relative": True,
        "hash_contract": {
            "per_source_file_sha256_lf": "sha256(lf_normalized raw bytes of file)",
            "input_manifest_payload_sha256": "sha256(canonical JSON of [{file,count_plan,sha256_lf}])",
            "mapping_payload_sha256": "sha256(canonical JSON of identity mapping)",
            "per_output_file_sha256_lf": "sha256(lf_normalized canonical output bytes)",
            "output_set_aggregate_sha256": "sha256(canonical JSON of [{file,count,sha256_lf}])",
        },
        "source_manifest": input_manifest_parts,
        "input_manifest_payload_sha256": input_manifest_payload_sha,
        "mapping_payload_sha256": mapping_payload_sha,
        "output_files": outputs,
        "output_set_aggregate_sha256": output_set_aggregate_sha,
        "status": "DRAFT_FOR_R_REVIEW; A self-check ADVISORY, 非 B2/Data-R authority",
        "g2": "G2_OWNER_PENDING（A 真人 100%；AI 不代）",
        "not_written": "不写 human_decision/final_label/gold/production truth",
    }
    with open(os.path.join(dst, "rework_manifest_20260906.json"), "w", encoding="utf-8") as f:
        f.write(canon(manifest) + "\n")
    return manifest, outputs


def check(root, src, dst):
    m, out = run(root, src, dst)  # 内存重生成到磁盘同路径（确定性）
    disk = load_manifest(dst)
    ok = True
    for o in out:
        d = next(x for x in disk["output_files"] if x["file"] == o["file"])
        cur = lf_sha(os.path.join(root, o["file"]))
        print("%s regenerated=%s disk=%s manifest=%s eq=%s" % (o["file"], o["sha256_lf"], cur, d["sha256_lf"],
                                                               o["sha256_lf"] == cur == d["sha256_lf"]))
        if not (o["sha256_lf"] == cur == d["sha256_lf"]):
            ok = False
    for k in ("input_manifest_payload_sha256", "mapping_payload_sha256", "output_set_aggregate_sha256"):
        if m[k] != disk.get(k):
            print("manifest %s mismatch" % k)
            ok = False
    print("RESULT:", "MATCH (deterministic)" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--src", default="data/interim/d1_candidates_A_20260906")
    ap.add_argument("--dst", default="data/interim/d1_candidates_A_20260906_rw")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.repo)
    if a.check:
        check(root, a.src, a.dst)
    else:
        m, _ = run(root, a.src, a.dst)
        print("WROTE 218")
        print("input_manifest_payload_sha256", m["input_manifest_payload_sha256"])
        print("mapping_payload_sha256", m["mapping_payload_sha256"])
        print("output_set_aggregate_sha256", m["output_set_aggregate_sha256"])
        for o in m["output_files"]:
            print(o["file"], o["count"], o["sha256_lf"][:16])


if __name__ == "__main__":
    main()
