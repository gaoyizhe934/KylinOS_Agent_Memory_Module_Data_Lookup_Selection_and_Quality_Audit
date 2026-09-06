# -*- coding: utf-8 -*-
"""v4.1 Data-A Closeout A1 builder — 10 条 Legacy REWORK/RELABEL 重构为 canonical candidate
Deterministic / repo-relative：
  - 读取 data/gold 冻结原行（master c21ee694）+ reports/legacy_semantic_requal_A.jsonl（#37 frozen fix_fields）
  - 按 repair_plan.json 的设计决定重构为 os_controlled_authored candidate（双层）
  - canonical 序列化（sort_keys, ', ' 无尾空格）→ 同输入同输出
CLI：python scripts/v4/build_legacy_rework_A1.py [--repo ROOT] [--check]
  --check : 用内存重生成结果比对磁盘文件与 manifest output_hash，不一致则 exit 1（CI 可复现校验）
"""
import argparse
import hashlib
import json
import os
import re
import sys

P = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(P, "..", ".."))
OUTDIR_DEFAULT = os.path.join("data", "interim", "d1_legacy_rework_A_20260906")
REQUAL_DEFAULT = os.path.join("reports", "legacy_semantic_requal_A.jsonl")
CANON = dict(ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canon(o):
    return json.dumps(o, **CANON)


def sha(o_bytes):
    return hashlib.sha256(o_bytes).hexdigest()


def norm_ts(orig):
    # B-L2: 'YYYY-MM-DDN' 计数器并入日期日（如 2026-07-202）→ 去多余日位
    m = re.match(r"^(\d{4}-\d{2}-\d{2})\d+T(\d{2}:\d{2}:\d{2})([+-]\d{2}:\d{2})$", orig)
    if m:
        return "%sT%s%s" % (m.group(1), m.group(2), m.group(3))
    raise ValueError("timestamp not in B-L2 broken shape: %s" % orig)


def load_jsonl(p):
    rows = []
    raw = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
                raw.append(line.rstrip("\n"))
    return rows, raw


def find_gold(rows, sample_id):
    hit = [r for r in rows if r.get("sample_id") == sample_id]
    if len(hit) != 1:
        raise SystemExit("gold row for %s: expected 1 got %d" % (sample_id, len(hit)))
    return hit[0]


def load_requal(p, want):
    rows, _ = load_jsonl(p)
    out = {}
    for r in rows:
        if r.get("sample_id") in want:
            out[r["sample_id"]] = r
    return out


def build_records(plan, outdir, requal_rows, root):
    pref_recs, forg_recs = [], []
    input_parts = []
    for e in plan["entries"]:
        lid = e["legacy_sample_id"]
        gold_rows, gold_raw = load_jsonl(os.path.join(root, e["gold_file"]))
        gr = find_gold(gold_rows, lid)
        # 输入哈希依据 = 原始 gold 行
        input_parts.append("%s::%s" % (e["gold_file"], gr.get("sample_id")))
        ff = requal_rows[lid].get("fix_fields", [])
        applied = [dict(f) for f in ff]
        orig_ts = gr.get("timestamp", "")
        fixed_ts = norm_ts(orig_ts)
        applied.append({"field": "timestamp", "issue": "B-L2 YYYY-MM-DDN→ISO", "proposed_action": "%s → %s" % (orig_ts, fixed_ts)})
        gdef = plan.get("generation", {})
        gen = {
            "generation_id": e.get("generation_id") or ("gen_" + e["candidate_id"]),
            "prompt_version": e.get("prompt_ref") or gdef.get("prompt_ref"),
            "seed": e.get("seed") if e.get("seed") is not None else gdef.get("seed"),
            "model": e.get("model") or gdef.get("model"),
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
        blind = {}
        if e["task"] == "preference":
            dm["scenario_class"] = e["scenario_class"]
            dm["task_semantic_class"] = e["step1"]
            if e.get("scope"):
                dm["design_scope_target"] = e["scope"]
            blind = {"user_message": gr["input"]["user_message"]}
            rec = base_rec(e["candidate_id"], "preference_extraction", fixed_ts, blind, dm)
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
            blind = {"forget_instruction": gr["input"]["forget_instruction"],
                     "inventory_context": e["inventory"]}
            rec = base_rec(e["candidate_id"], "precise_forgetting", fixed_ts, blind, dm)
            forg_recs.append(rec)
    input_hash = sha("\n".join(sorted(input_parts)).encode("utf-8"))
    return pref_recs, forg_recs, input_hash


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


def write_manifest(plan, outdir, input_hash, output_hashes, root):
    mf = {
        "schema": "v4.1_d1_legacy_rework_manifest",
        "batch_id": plan["batch_id"],
        "date": plan["date"],
        "owner": plan["owner"],
        "branch": plan["branch"],
        "repo_base": plan["repo_base"],
        "input_commit": plan["input_commit"],
        "fix_source_commit": plan["fix_source_commit"],
        "requal_source": REQUAL_DEFAULT.replace("\\", "/"),
        "input_hash": input_hash,
        "output_files": [
            {"file": os.path.relpath(os.path.join(outdir, fn), root).replace("\\", "/"), "count": n, "output_sha256": h}
            for fn, n, h in output_hashes
        ],
        "regeneration_deterministic": {"builder": "scripts/v4/build_legacy_rework_A1.py", "verify": "python scripts/v4/build_legacy_rework_A1.py --check (CI)", "state": "VERIFY_VIA_CHECK"},
        "scope": plan["scope"],
        "red_line_compliance": plan["red_line_compliance"],
        "blockers": plan["blockers"],
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
    requal_rows = load_requal(os.path.join(root, REQUAL_DEFAULT), {e["legacy_sample_id"] for e in plan["entries"]})
    if len(requal_rows) != len(plan["entries"]):
        raise SystemExit("requal fix_fields missing for some plan entries")
    pref_recs, forg_recs, input_hash = build_records(plan, outdir, requal_rows, root)
    pf = os.path.join(outdir, "legacy_rework_preference_candidates.jsonl")
    ff = os.path.join(outdir, "legacy_rework_forgetting_candidates.jsonl")
    if args.check:
        checks = []
        for p, recs in [(pf, pref_recs), (ff, forg_recs)]:
            body = "".join(canon(r) + "\n" for r in recs)
            disk = open(p, encoding="utf-8").read()
            checks.append((p, sha(body.encode("utf-8")), sha(disk.encode("utf-8")), body == disk))
        mf_path = os.path.join(outdir, "generation_manifest_A_20260906.json")
        mf = json.load(open(mf_path, encoding="utf-8"))
        ok = True
        for (p, b, d, eq), om in zip(checks, mf["output_files"]):
            print("%s\n  regenerated=%s disk=%s match=%s manifest_sha=%s" % (p, b, d, eq, om["output_sha256"]))
            if not eq or b != om["output_sha256"]:
                ok = False
        print("input_hash recomputed=%s manifest=%s" % (input_hash, mf.get("input_hash")))
        if input_hash != mf.get("input_hash"):
            ok = False
        print("RESULT:", "MATCH (deterministic)" if ok else "MISMATCH")
        sys.exit(0 if ok else 1)
    h1 = dump_canon(pref_recs, pf)
    h2 = dump_canon(forg_recs, ff)
    write_manifest(plan, outdir, input_hash, [(os.path.basename(pf), len(pref_recs), h1), (os.path.basename(ff), len(forg_recs), h2)], root)
    print("WROTE pref=%d forg=%d" % (len(pref_recs), len(forg_recs)))
    print("input_hash", input_hash)
    print("output pref", h1)
    print("output forg", h2)


if __name__ == "__main__":
    main()
