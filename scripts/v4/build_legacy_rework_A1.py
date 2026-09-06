# -*- coding: utf-8 -*-
"""v4.1 Data-A Closeout A1 builder — 10 条 Legacy REWORK/RELABEL 重构为 canonical candidate
Deterministic / repo-relative / **exact pinned-input 可验证**（响应 Data-R Review #39 P0 Blocking）：
  - 从 pinned commit 读取冻结输入：`git show <input_commit>:<gold_file>` 逐条取原始行；
    `git show <fix_source_commit>:reports/legacy_semantic_requal_A.jsonl` 取 Rev3 fix_fields；
  - 当前 checkout 与 pinned blob 不一致 => fail-closed；
  - manifest 记录真实可解析 commit + source_files_sha256 + selected_rows_sha256 +
    requal_blob_sha256 + repair_plan_sha256 + 组合 input_hash + 每文件 output_sha256；
  - canonical 序列化（sort_keys / 无尾空格）→ 同 pinned 输入同输出。
CLI：python scripts/v4/build_legacy_rework_A1.py [--repo ROOT] [--check]
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

P = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(P, "..", ".."))
OUTDIR_DEFAULT = os.path.join("data", "interim", "d1_legacy_rework_A_20260906")
REQUAL_DEFAULT = os.path.join("reports", "legacy_semantic_requal_A.jsonl")
CANON = dict(ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canon(o):
    return json.dumps(o, **CANON)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm_ts(orig):
    # B-L2: 'YYYY-MM-DDN' 计数器并入日期日（如 2026-07-202）→ 去多余日位
    m = re.match(r"^(\d{4}-\d{2}-\d{2})\d+T(\d{2}:\d{2}:\d{2})([+-]\d{2}:\d{2})$", orig)
    if m:
        return "%sT%s%s" % (m.group(1), m.group(2), m.group(3))
    raise ValueError("timestamp not in B-L2 broken shape: %s" % orig)


def git(root, args):
    r = subprocess.run(["git", "-C", root] + args, capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
    return r.stdout


def resolve_commit(root, c):
    out = git(root, ["rev-parse", "--verify", "%s^{commit}" % c]).strip().decode("utf-8")
    if len(out) != 40:
        raise SystemExit("commit not resolvable: %s" % c)
    return out


def pinned_bytes(root, commit, relpath):
    return git(root, ["show", "%s:%s" % (commit, relpath)])


def disk_bytes(root, relpath):
    with open(os.path.join(root, relpath), "rb") as f:
        return f.read()


def _nl(b):
    return b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _nl_bytes(b):
    return b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def file_raw_sha(path):
    with open(path, "rb") as f:
        return sha(_nl_bytes(f.read()))


def verify_pinned_identical(root, commit, relpaths):
    bad = []
    for rp in relpaths:
        if _nl(pinned_bytes(root, commit, rp)) != _nl(disk_bytes(root, rp)):
            bad.append(rp)
    if bad:
        raise SystemExit("checkout 与 pinned(%s) 不一致(fail-closed，newline-normalized): %s" % (commit, bad))


def parse_jsonl_text(text):
    rows = []
    for line in text.splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build_records(plan, outdir, gold_rows_by_file, requal_rows, requal_text, fix_commit, root):
    pref_recs, forg_recs = [], []
    selected = []
    for e in plan["entries"]:
        lid = e["legacy_sample_id"]
        rows = gold_rows_by_file[e["gold_file"]]
        gr = next((r for r in rows if r.get("sample_id") == lid), None)
        if gr is None:
            raise SystemExit("gold row not found: %s in %s" % (lid, e["gold_file"]))
        selected.append(canon(gr))  # 10 条原始行 canonical bytes
        ff = requal_rows.get(lid, {}).get("fix_fields", [])
        applied = [dict(f) for f in ff]
        orig_ts = gr.get("timestamp", "")
        fixed_ts = norm_ts(orig_ts)
        applied.append({"field": "timestamp", "issue": "B-L2 YYYY-MM-DDN→ISO", "proposed_action": "%s → %s" % (orig_ts, fixed_ts)})
        gen = {
            "generation_id": e.get("generation_id") or ("gen_" + e["candidate_id"]),
            "prompt_version": e.get("prompt_ref") or plan["generation"]["prompt_ref"],
            "seed": e.get("seed") if e.get("seed") is not None else plan["generation"]["seed"],
            "model": e.get("model") or plan["generation"]["model"],
            "source": "os_controlled_authored",
            "source_layer": "os_controlled_authored",
            "source_file": os.path.relpath(os.path.join(outdir, e["outfile"]), root).replace("\\", "/"),
        }
        dm = {
            "scenario_spec_id": e["scenario_spec_id"],
            "scenario_family": e["scenario_family"],
            "candidate_event_refs": ["evt_" + e["candidate_id"]],
            "applied_fixes": applied,
            "generation": gen,
            "legacy_ref": {
                "legacy_sample_id": lid,
                "file": e["gold_file"],
                "v1_family": gr.get("template_family"),
                "original_user_id": gr.get("user_id"),
                "original_conversation": gr.get("conversation_id"),
                "split": gr.get("split") if gr.get("split") else os.path.basename(os.path.dirname(e["gold_file"])),
            },
            "split_eligibility": e["split_eligibility"],
        }
        if e["task"] == "preference":
            dm["scenario_class"] = e["scenario_class"]
            dm["task_semantic_class"] = e["step1"]
            if e.get("scope"):
                dm["design_scope_target"] = e["scope"]
            blind_user = e.get("blind_user_message") or gr["input"]["user_message"]
            if e.get("rewrite_required"):
                applied.append({"field": "blind_text", "issue": e.get("rewrite_reason"),
                                "proposed_action": "semantic-preserving rewrite per repair_plan (%s)" % e.get("rewrite_strategy")})
            blind = {"user_message": blind_user}
            rec = base_rec(e["candidate_id"], "preference_extraction", fixed_ts, blind, dm)
            tf = gr.get("template_family")
            if not tf:
                raise SystemExit("template_family missing in pinned legacy row %s (fail-closed)" % lid)
            rec["template_family"] = tf
            pref_recs.append(rec)
        else:
            dm["forget_mode"] = e["mode"]
            dm["checkpoints"] = e["checkpoints"]
            dm["expected_residual_count"] = e["expected_residual_count"]
            dm["target_ids"] = e["target_ids"]
            dm["must_keep"] = e["must_keep"]
            if e.get("time_range"):
                dm["target_time_range"] = e["time_range"]
            if e.get("target_topic"):
                dm["target_topic"] = e["target_topic"]
            blind = {"forget_instruction": gr["input"]["forget_instruction"], "inventory_context": e["inventory"]}
            rec = base_rec(e["candidate_id"], "precise_forgetting", fixed_ts, blind, dm)
            tf = gr.get("template_family")
            if not tf:
                raise SystemExit("template_family missing in pinned legacy row %s (fail-closed)" % lid)
            rec["template_family"] = tf
            forg_recs.append(rec)
    selected_rows_sha = sha("\n".join(sorted(selected)).encode("utf-8"))
    requal_blob_sha = sha(requal_text.encode("utf-8") if isinstance(requal_text, str) else requal_text)
    return pref_recs, forg_recs, selected_rows_sha, requal_blob_sha


def base_rec(sid, task, ts, blind, dm):
    return {
        "sample_id": sid, "task_type": task, "language": "zh-CN",
        "dataset_version": "kylin_memory_candidate_v4.1", "dataset_stage": "candidate_only",
        "review_status": "candidate_only", "admission_status": "NOT_ADMISSION_APPROVED",
        "id_binding_status": "NON_PRODUCTION", "scenario_user_ref": "u_" + sid,
        "conversation_id": "conv_" + sid, "timestamp": ts,
        "blind_visible": {"input": blind}, "design_metadata": dm,
    }


def dump_canon(recs, path):
    body = "".join(canon(r) + "\n" for r in recs)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    return sha(body.encode("utf-8"))


def compute_input_hash(input_commit, fix_commit, selected_rows_sha, requal_blob_sha, source_files_sha, plan_sha):
    payload = canon({
        "input_commit": input_commit, "fix_source_commit": fix_commit,
        "selected_rows_sha256": selected_rows_sha, "requal_blob_sha256": requal_blob_sha,
        "source_files_sha256": source_files_sha, "repair_plan_sha256": plan_sha,
    })
    return sha(payload.encode("utf-8"))


def write_manifest(plan, outdir, input_hash, output_hashes, root, extra):
    mf = {
        "schema": "v4.1_d1_legacy_rework_manifest",
        "batch_id": plan["batch_id"], "date": plan["date"], "owner": plan["owner"],
        "branch": plan["branch"], "repo_base": plan["repo_base"],
        "hash_contract": "sha256(lf_normalized_raw_bytes)  // repair_plan/source_files/requal/candidate 均按 LF-normalized raw bytes",
        "template_family_source": "pinned legacy row template_family（lineage；缺失 fail-closed）",
        "input_commit": plan["input_commit"], "fix_source_commit": plan["fix_source_commit"],
        "requal_source": REQUAL_DEFAULT.replace("\\", "/"),
        "input_hash": input_hash,
        "exact_input_proof": extra,
        "output_files": [
            {"file": os.path.relpath(os.path.join(outdir, fn), root).replace("\\", "/"), "count": n, "output_sha256": h}
            for fn, n, h in output_hashes
        ],
        "regeneration_deterministic": {"builder": "scripts/v4/build_legacy_rework_A1.py", "verify": "python scripts/v4/build_legacy_rework_A1.py --check (CI)", "state": "VERIFY_VIA_CHECK"},
        "scope": plan["scope"], "red_line_compliance": plan["red_line_compliance"], "blockers": plan["blockers"],
        "exposed_lineage_blocked": plan.get("exposed_lineage_blocked"),
    }
    with open(os.path.join(outdir, "generation_manifest_A_20260906.json"), "w", encoding="utf-8") as f:
        f.write(canon(mf) + "\n")
    return mf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=ROOT)
    ap.add_argument("--outdir", default=OUTDIR_DEFAULT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.repo)
    outdir = args.outdir if os.path.isabs(args.outdir) else os.path.join(root, args.outdir)
    plan_p = os.path.join(outdir, "repair_plan.json")
    plan = json.load(open(plan_p, encoding="utf-8"))
    plan_sha = file_raw_sha(plan_p)  # pinned repair_plan raw-bytes sha (LF-normalized, 跨平台)
    input_commit = resolve_commit(root, plan["input_commit"])
    fix_commit = resolve_commit(root, plan["fix_source_commit"])
    if input_commit != plan["input_commit"] or fix_commit != plan["fix_source_commit"]:
        raise SystemExit("plan commit not full-resolvable")
    # pinned inputs: gold files + requal
    gold_relpaths = sorted({e["gold_file"] for e in plan["entries"]})
    requal_rel = REQUAL_DEFAULT.replace("\\", "/")
    verify_pinned_identical(root, input_commit, gold_relpaths + [requal_rel])
    requal_text = pinned_bytes(root, fix_commit, requal_rel).decode("utf-8")
    requal_rows = {r.get("sample_id"): r for r in parse_jsonl_text(requal_text)}
    gold_rows_by_file = {}
    source_files_sha = {}
    for rp in gold_relpaths:
        text = pinned_bytes(root, input_commit, rp).decode("utf-8")
        gold_rows_by_file[rp] = parse_jsonl_text(text)
        source_files_sha[rp] = sha(pinned_bytes(root, input_commit, rp))
    requal_blob_sha = sha(requal_text.encode("utf-8"))
    pref_recs, forg_recs, selected_rows_sha, requal_blob_sha2 = build_records(
        plan, outdir, gold_rows_by_file, requal_rows, requal_text, fix_commit, root)
    assert requal_blob_sha == requal_blob_sha2
    extra = {
        "commit_resolvable": {"input_commit": input_commit, "fix_source_commit": fix_commit},
        "source_files_sha256": source_files_sha,
        "selected_rows_sha256": selected_rows_sha,
        "requal_blob_sha256": requal_blob_sha,
        "repair_plan_sha256": plan_sha,
    }
    input_hash = compute_input_hash(input_commit, fix_commit, selected_rows_sha, requal_blob_sha,
                                    source_files_sha, plan_sha)
    pf = os.path.join(outdir, "legacy_rework_preference_candidates.jsonl")
    ff = os.path.join(outdir, "legacy_rework_forgetting_candidates.jsonl")
    mf_path = os.path.join(outdir, "generation_manifest_A_20260906.json")
    if args.check:
        body_p = "".join(canon(r) + "\n" for r in pref_recs)
        body_f = "".join(canon(r) + "\n" for r in forg_recs)
        disk_p = open(pf, encoding="utf-8").read()
        disk_f = open(ff, encoding="utf-8").read()
        mf = json.load(open(mf_path, encoding="utf-8"))
        ok = True
        for name, b, d in [("pref", sha(body_p.encode("utf-8")), sha(disk_p.encode("utf-8"))), ("forg", sha(body_f.encode("utf-8")), sha(disk_f.encode("utf-8")))]:
            om = next(o for o in mf["output_files"] if name in o["file"])
            print("%s regenerated=%s disk=%s manifest=%s eq=%s" % (name, b, d, om["output_sha256"], b == d == om["output_sha256"]))
            if not (b == d == om["output_sha256"]):
                ok = False
        if input_hash != mf.get("input_hash"):
            print("input_hash mismatch recomputed=%s manifest=%s" % (input_hash, mf.get("input_hash")))
            ok = False
        elif extra["selected_rows_sha256"] != mf.get("exact_input_proof", {}).get("selected_rows_sha256"):
            print("selected_rows_sha mismatch"); ok = False
        elif extra["repair_plan_sha256"] != mf.get("exact_input_proof", {}).get("repair_plan_sha256"):
            print("repair_plan_sha mismatch"); ok = False
        print("input_hash=%s" % input_hash)
        print("RESULT:", "MATCH (deterministic, pinned-input verified)" if ok else "MISMATCH")
        sys.exit(0 if ok else 1)
    h1 = dump_canon(pref_recs, pf)
    h2 = dump_canon(forg_recs, ff)
    write_manifest(plan, outdir, input_hash, [(os.path.basename(pf), len(pref_recs), h1), (os.path.basename(ff), len(forg_recs), h2)], root, extra)
    print("WROTE pref=%d forg=%d" % (len(pref_recs), len(forg_recs)))
    print("input_commit", input_commit)
    print("input_hash", input_hash)
    print("selected_rows_sha256", selected_rows_sha)
    print("requal_blob_sha256", requal_blob_sha)
    print("repair_plan_sha256", plan_sha)
    print("output pref", h1)
    print("output forg", h2)


if __name__ == "__main__":
    main()
