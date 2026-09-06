#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data-A A218 rework — pinned / authority-driven / non-mutating (PR #52)

模板族语义：top-level `template_family` = **checked-in mapping authority** 的
`current_template_family`（reports/v4.1_D1_A_A218_template_family_mapping_authority.json），
不是从 candidate 的 scenario_family 自动等同。
Authority cross-check：source_commit、3×scenario_specs、factory_config（recorded）与
authority 内部 scenario_family 一致性；candidate 的 scenario_spec_id/scenario_family 必须命中。

Mode：
  --write ：生成 dst 3×jsonl + template_family_mapping_payload.json + rework_manifest_20260906.json；
  --check ：内存重生成与磁盘比对，非变异（不写文件）；不匹配 exit 1。
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

CANON = dict(ensure_ascii=False, sort_keys=True, separators=(",", ":"))
PLAN = {"preference_candidates.jsonl": 98, "conflict_candidates.jsonl": 64,
        "forgetting_candidates.jsonl": 56}
SRC_FILES = sorted(PLAN)
SPEC_FILES = ["preference_scenarios.json", "conflict_scenarios.json", "forgetting_scenarios.json"]
DEFAULT_COMMIT = "535ebad3db47e87bbb30f26b86b3193803d81a1b"
AUTHORITY_FILE = "reports/v4.1_D1_A_A218_template_family_mapping_authority.json"


def canon(o):
    return json.dumps(o, **CANON)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def nl(b):
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git_bytes(root, commit, relpath):
    r = subprocess.run(["git", "-C", root, "show", "%s:%s" % (commit, relpath)], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git show failed %s:%s -> %s" % (commit, relpath, r.stderr.decode("utf-8", "replace")[:300]))
    return r.stdout


def relpos(root, p):
    return os.path.relpath(p, root).replace("\\", "/")


def read_jsonl_text(text):
    return [l for l in text.splitlines() if l.strip()]


def load_authority(root, commit):
    p = os.path.join(root, AUTHORITY_FILE)
    if not os.path.exists(p):
        raise SystemExit("mapping authority missing: %s" % AUTHORITY_FILE)
    raw = open(p, "rb").read()
    auth = json.loads(nl(raw).decode("utf-8"))
    if auth.get("source_commit") != commit:
        raise SystemExit("authority source_commit mismatch")
    if auth.get("approved"):
        raise SystemExit("authority must stay DRAFT_FOR_R_REVIEW")
    fams = {}
    spec_files = []
    for fn in SPEC_FILES:
        rel = "data/interim/candidates_v4/scenario_specs/" + fn
        b = git_bytes(root, commit, rel)
        spec_files.append({"file": rel, "sha256_lf": sha(nl(b))})
        spec = json.loads(nl(b).decode("utf-8"))
        for sc in spec.get("scenarios", []):
            if sc.get("scenario_id"):
                fams[sc["scenario_id"]] = sc["scenario_family"]
    entries = {}
    for e in auth["entries"]:
        sid = e["scenario_spec_id"]
        if fams.get(sid) != e["scenario_family"]:
            raise SystemExit("authority %s family mismatch vs pinned spec" % sid)
        if not e.get("current_template_family"):
            raise SystemExit("authority %s missing current_template_family" % sid)
        entries[sid] = e
    if set(fams) != set(entries):
        raise SystemExit("authority must cover all pinned scenario_spec ids")
    auth_sha = sha(nl(raw))
    return entries, auth, auth_sha, spec_files


def compute(root, src_rel, dst_rel, commit):
    if len(commit) != 40:
        raise SystemExit("bad source-commit")
    entries, authobj, auth_sha, spec_files = load_authority(root, commit)
    src_meta = []
    for fn in SRC_FILES:
        rel = src_rel.rstrip("/") + "/" + fn
        raw = git_bytes(root, commit, rel)
        src_meta.append({"file": rel, "count_plan": PLAN[fn], "sha256_lf": sha(nl(raw))})
    inputs = {m["file"]: nl(git_bytes(root, commit, m["file"])).decode("utf-8") for m in src_meta}

    used = {}
    outputs = []
    for fm in src_meta:
        rows = read_jsonl_text(inputs[fm["file"]])
        if len(rows) != PLAN[fm["file"].split("/")[-1]]:
            raise SystemExit("count mismatch %s" % fm["file"])
        body = []
        for line in rows:
            r = json.loads(line)
            if "template_family" in r:
                raise SystemExit("already template_family: %s" % r["sample_id"])
            sid = r["design_metadata"].get("scenario_spec_id")
            fam = r["design_metadata"].get("scenario_family")
            e = entries.get(sid)
            if not e:
                raise SystemExit("scenario_spec_id %s not in mapping authority" % (sid,))
            if fam != e["scenario_family"]:
                raise SystemExit("candidate family mismatch %s: got %s want %s" % (r["sample_id"], fam, e["scenario_family"]))
            if sid in used and used[sid] != e["current_template_family"]:
                raise SystemExit("conflicting current_template_family for %s" % sid)
            used[sid] = e["current_template_family"]
            r["template_family"] = e["current_template_family"]
            body.append(canon(r))
        out_rel = dst_rel.rstrip("/") + "/" + fm["file"].split("/")[-1]
        out_text = "\n".join(body) + "\n"
        outputs.append({"file": out_rel, "count": len(body), "sha256_lf": sha(out_text.encode("utf-8")), "text": out_text})

    mp_entries = sorted([{"scenario_spec_id": sid, "scenario_family": entries[sid]["scenario_family"],
                          "current_template_family": ct} for sid, ct in used.items()],
                        key=lambda x: x["scenario_spec_id"])
    mapping_payload = {"authority": AUTHORITY_FILE, "mapping_kind": "current_template_family per mapping authority",
                       "entries": mp_entries}
    mp_text = canon(mapping_payload) + "\n"
    mp_file = dst_rel.rstrip("/") + "/template_family_mapping_payload.json"

    input_payload = canon(sorted([{"file": m["file"], "count_plan": m["count_plan"], "sha256_lf": m["sha256_lf"]}
                                  for m in src_meta], key=lambda x: x["file"]))
    out_payload = canon(sorted([{"file": o["file"], "count": o["count"], "sha256_lf": o["sha256_lf"]}
                                for o in outputs], key=lambda x: x["file"]))
    manifest = {
        "schema": "v4.1_A_A218_rework_manifest_v4", "date": "2026-09-06", "role": "Data-A (lyf-1213)",
        "source_commit": commit,
        "hash_contract": {
            "paths": "repo-relative POSIX '/'",
            "per_source_file_sha256_lf": "sha256(lf-normalized raw bytes of git show <commit>:file)",
            "input_manifest_payload_sha256": "sha256(canonical JSON of [{file,count_plan,sha256_lf}])",
            "mapping_payload_file_sha256_lf": "sha256(LF-terminated canonical mapping-payload JSON file bytes)",
            "mapping_authority_sha256_lf": "sha256(LF-normalized raw bytes of checked-in mapping authority)",
            "per_output_file_sha256_lf": "sha256(lf-normalized canonical output bytes)",
            "output_set_aggregate_sha256": "sha256(canonical JSON of [{file,count,sha256_lf}])",
        },
        "source_files": src_meta,
        "input_manifest_payload_sha256": sha(input_payload.encode("utf-8")),
        "mapping_authority": {"file": AUTHORITY_FILE, "sha256_lf": auth_sha,
                              "pinned": authobj.get("pinned")},
        "mapping_payload_file_sha256_lf": sha(mp_text.encode("utf-8")),
        "output_files": [{"file": o["file"], "count": o["count"], "sha256_lf": o["sha256_lf"]} for o in outputs],
        "output_set_aggregate_sha256": sha(out_payload.encode("utf-8")),
        "status": "DRAFT_FOR_R_REVIEW; A self-check ADVISORY; formal B2 by Data-B (incl G3)",
        "g2": "G2_OWNER_PENDING",
        "not_written": "不写 human_decision/final_label/gold/production truth",
    }
    mf_text = canon(manifest) + "\n"
    mf_rel = dst_rel.rstrip("/") + "/rework_manifest_20260906.json"
    return {"src_meta": src_meta, "outputs": outputs,
            "mapping_payload": {"file": mp_file, "text": mp_text},
            "manifest": manifest, "manifest_rel": mf_rel, "manifest_text": mf_text}


def write(root, src_rel, dst_rel, commit):
    r = compute(root, src_rel, dst_rel, commit)
    os.makedirs(os.path.join(root, dst_rel), exist_ok=True)
    for o in r["outputs"]:
        with open(os.path.join(root, o["file"]), "wb") as f:
            f.write(o["text"].encode("utf-8"))
    with open(os.path.join(root, r["mapping_payload"]["file"]), "wb") as f:
        f.write(r["mapping_payload"]["text"].encode("utf-8"))
    with open(os.path.join(root, r["manifest_rel"]), "wb") as f:
        f.write(r["manifest_text"].encode("utf-8"))
    return r


def check(root, src_rel, dst_rel, commit):
    r = compute(root, src_rel, dst_rel, commit)
    ok = True
    for o in r["outputs"]:
        p = os.path.join(root, o["file"])
        if not os.path.exists(p):
            print("MISSING", o["file"]); ok = False; continue
        if sha(nl(open(p, "rb").read())) != o["sha256_lf"]:
            print("MISMATCH file", o["file"]); ok = False
    for rel, text in [("template_family_mapping_payload.json", r["mapping_payload"]["text"]),
                      ("rework_manifest_20260906.json", r["manifest_text"])]:
        p = os.path.join(root, dst_rel, rel)
        if not os.path.exists(p) or sha(nl(open(p, "rb").read())) != sha(text.encode("utf-8")):
            print("MISMATCH", rel); ok = False
    print("RESULT:", "MATCH (non-mutating deterministic)" if ok else "MISMATCH")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--src", default="data/interim/d1_candidates_A_20260906")
    ap.add_argument("--dst", default="data/interim/d1_candidates_A_20260906_rw")
    ap.add_argument("--source-commit", default=DEFAULT_COMMIT)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.repo)
    src_rel = relpos(root, os.path.join(root, a.src))
    dst_rel = relpos(root, os.path.join(root, a.dst))
    if a.write:
        r = write(root, src_rel, dst_rel, a.source_commit)
        m = r["manifest"]
        print("WROTE 218")
        print("input_manifest_payload_sha256", m["input_manifest_payload_sha256"])
        print("mapping_payload_file_sha256_lf", m["mapping_payload_file_sha256_lf"])
        print("mapping_authority_sha256_lf", m["mapping_authority"]["sha256_lf"])
        print("output_set_aggregate_sha256", m["output_set_aggregate_sha256"])
    else:
        check(root, src_rel, dst_rel, a.source_commit)


if __name__ == "__main__":
    main()
