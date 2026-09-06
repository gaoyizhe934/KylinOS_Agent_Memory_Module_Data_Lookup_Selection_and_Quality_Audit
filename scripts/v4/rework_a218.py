#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data-A A218 rework — pinned/deterministic/non-mutating (PR #52)

语义：给 A218（98/64/56）补 top-level `template_family`。
template_family 取自 **独立、pinned 的 scenario-spec authority**（git show <source_commit>:scenario_specs/*.json
的 scenario_spec_id->scenario_family），逐候选核验：
  - candidate.design_metadata.scenario_spec_id 必须在 authority 内；
  - candidate.design_metadata.scenario_family 必须等于 authority 该 id 的 family；
  - candidate 不得已有 top-level template_family；
  - 同一 scenario_spec_id 出现不同 family -> FAIL（无 last-write-wins）。

Mode：
  默认（write）：在 dst 生成 3 个 rw JSONL + template_family_mapping_payload.json + rework_manifest_20260906.json；
  --check（**非变异**）：在内存重生成，与已提交文件 bytes/hash 比对，不一致 exit 1，且不写任何文件。

CLI：
  python scripts/v4/rework_a218.py --repo <root> [--src .../d1_candidates_A_20260906] [--dst ..._rw]
        [--source-commit 535ebad3db47e87bbb30f26b86b3193803d81a1b] [--write|--check]
"""
import argparse
import glob
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
    auth = {}
    files = []
    for fn in SPEC_FILES:
        rel = "data/interim/candidates_v4/scenario_specs/" + fn
        raw = git_bytes(root, commit, rel)
        files.append({"file": rel, "sha256_lf": sha(nl(raw))})
        spec = json.loads(nl(raw).decode("utf-8"))
        for sc in spec.get("scenarios", []):
            sid = sc.get("scenario_id")
            fam = sc.get("scenario_family")
            if sid:
                if sid in auth and auth[sid] != fam:
                    raise SystemExit("authority conflict scenario_spec_id=%s family %s vs %s" % (sid, auth[sid], fam))
                auth[sid] = fam
    return auth, files


def compute(root, src_rel, dst_rel, commit):
    if len(commit) != 40:
        raise SystemExit("bad source-commit")
    src_meta = []
    for fn in SRC_FILES:
        rel = src_rel + "/" + fn if not src_rel.endswith("/") else src_rel + fn
        raw = git_bytes(root, commit, rel)
        src_meta.append({"file": rel, "count_plan": PLAN[fn], "sha256_lf": sha(nl(raw))})

    auth, spec_files = load_authority(root, commit)
    used = {}
    inputs_lines = {}
    for fm in src_meta:
        text = nl(git_bytes(root, commit, fm["file"])).decode("utf-8")
        inputs_lines[fm["file"]] = text

    outputs = []
    used_ordered = []
    for fm in src_meta:
        base = fm["file"].split("/")[-1]
        rows = read_jsonl_text(inputs_lines[fm["file"]])
        if len(rows) != PLAN[base]:
            raise SystemExit("count mismatch %s" % fm["file"])
        body = []
        for line in rows:
            r = json.loads(line)
            if "template_family" in r:
                raise SystemExit("already template_family: %s" % r["sample_id"])
            sid = r["design_metadata"].get("scenario_spec_id")
            fam = r["design_metadata"].get("scenario_family")
            afam = auth.get(sid)
            if not sid or not afam:
                raise SystemExit("scenario_spec_id %s not in pinned authority" % (sid,))
            if fam != afam:
                raise SystemExit("candidate family mismatch %s: got %s want %s" % (r["sample_id"], fam, afam))
            if sid in used and used[sid] != fam:
                raise SystemExit("conflicting scenario_spec_id family in candidates: %s" % sid)
            used[sid] = fam
            r["template_family"] = afam
            body.append(canon(r))
        out_rel = dst_rel.rstrip("/") + "/" + fm["file"].split("/")[-1]
        out_text = "\n".join(body) + "\n"
        outputs.append({"file": out_rel, "count": len(body), "sha256_lf": sha(out_text.encode("utf-8")),
                        "text": out_text})
        used_ordered.append(sid)

    mapping_payload = {"authority": "pinned scenario_specs (%s)" % commit,
                       "mapping_kind": "identity_to_scenario_spec_family",
                       "entries": sorted([{"scenario_spec_id": k, "scenario_family": v} for k, v in used.items()],
                                         key=lambda x: x["scenario_spec_id"])}
    mp_text = canon(mapping_payload) + "\n"
    mapping_payload_rel = dst_rel.rstrip("/") + "/template_family_mapping_payload.json"

    input_payload = canon(sorted([{"file": m["file"], "count_plan": m["count_plan"], "sha256_lf": m["sha256_lf"]}
                                  for m in src_meta], key=lambda x: x["file"]))
    out_payload = canon(sorted([{"file": o["file"], "count": o["count"], "sha256_lf": o["sha256_lf"]}
                                for o in outputs], key=lambda x: x["file"]))
    manifest = {
        "schema": "v4.1_A_A218_rework_manifest_v3", "date": "2026-09-06", "role": "Data-A (lyf-1213)",
        "source_commit": commit,
        "hash_contract": {
            "paths": "repo-relative POSIX '/'",
            "per_source_file_sha256_lf": "sha256(lf-normalized raw bytes of git show <commit>:file)",
            "input_manifest_payload_sha256": "sha256(canonical JSON of [{file,count_plan,sha256_lf}])",
            "authority_files": [{"file": f["file"], "sha256_lf": f["sha256_lf"]} for f in spec_files],
            "mapping_payload_sha256": "sha256(canonical JSON of identity mapping, derived from pinned authority)",
            "per_output_file_sha256_lf": "sha256(lf-normalized canonical output bytes)",
            "output_set_aggregate_sha256": "sha256(canonical JSON of [{file,count,sha256_lf}])",
        },
        "source_files": src_meta,
        "input_manifest_payload_sha256": sha(input_payload.encode("utf-8")),
        "authority": {"scenario_spec_files": spec_files, "scenario_ids": len(auth)},
        "mapping_payload": {"file": mapping_payload_rel, "sha256": sha(mp_text.encode("utf-8"))},
        "output_files": [{"file": o["file"], "count": o["count"], "sha256_lf": o["sha256_lf"]} for o in outputs],
        "output_set_aggregate_sha256": sha(out_payload.encode("utf-8")),
        "status": "DRAFT_FOR_R_REVIEW; A self-check ADVISORY; formal B2 by Data-B (incl G3)",
        "g2": "G2_OWNER_PENDING",
        "not_written": "不写 human_decision/final_label/gold/production truth",
    }
    mf_text = canon(manifest) + "\n"
    manifest_rel = dst_rel.rstrip("/") + "/rework_manifest_20260906.json"
    return {"src_meta": src_meta, "outputs": outputs, "output_text": {o["file"]: o["text"] for o in outputs},
            "mapping_payload": {"file": mapping_payload_rel, "text": mp_text},
            "manifest": manifest, "manifest_rel": manifest_rel, "manifest_text": mf_text}


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
        cur = sha(nl(open(p, "rb").read()))
        if cur != o["sha256_lf"]:
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
        print("WROTE 218")
        print("input_manifest_payload_sha256", r["manifest"]["input_manifest_payload_sha256"])
        print("mapping_payload_sha256", r["manifest"]["mapping_payload"]["sha256"])
        print("output_set_aggregate_sha256", r["manifest"]["output_set_aggregate_sha256"])
    else:
        check(root, src_rel, dst_rel, a.source_commit)


if __name__ == "__main__":
    main()
