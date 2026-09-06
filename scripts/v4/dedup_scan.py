#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 G4 Dedup Scan（P2-A 工具 T04，Data-B）

exact duplicate + near duplicate（Jaccard>0.85）+ template/source 集中度。
field-aware normalization：保留 version/date/id/数值。
输出 contract（供 T06）：checked_sample_ids + input_set_hash + samples(sid->G4 ok/reason) + gates。
near-dup>0.85：规则为 Reviewer review；报告必须给 near_duplicate_review.status（UNREVIEWED/REVIEWED）；
未裁决一律视为 G4 BLOCKED。
退出码：0=PASS；2=exact dup>0 或 template 集中度 FAIL 或 near-dup 未裁决。
用法：python scripts/v4/dedup_scan.py --input <glob> [--out reports/dedup_report.json] [--near-threshold 0.85] [--template-max 0.25]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def input_set_hash(ids):
    return hashlib.sha256(json.dumps(sorted(ids)).encode("utf-8")).hexdigest()


def load_rows(paths):
    rows = []
    for pat in paths:
        matched = glob.glob(os.path.join(ROOT, pat))
        for p in matched:
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
    return rows, sum(1 for pat in paths for _ in glob.glob(os.path.join(ROOT, pat)))


def normalize_field_aware(text):
    s = text.strip().lower()
    s = re.sub(r"[，。！？、；：,.!?;:（）()【】\[\]「」]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def tokenize(s):
    out = []
    for t in re.split(r"[\s_\-/]+", s):
        if not t:
            continue
        if re.search(r"[\u4e00-\u9fff]", t):
            out.extend(list(t))
        else:
            out.append(t)
    return out


def jaccard(a, b):
    sa, sb = set(tokenize(a)), set(tokenize(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--out", default="reports/dedup_report.json")
    ap.add_argument("--near-threshold", type=float, default=0.85)
    ap.add_argument("--template-max", type=float, default=0.25)
    ap.add_argument("--near-review-status", default="UNREVIEWED", choices=["UNREVIEWED", "REVIEWED"],
                    help="near-dup 裁决状态：REVIEWED 表示 Reviewer 已逐对裁决")
    ap.add_argument("--near-review-decision", default="", help="REVIEWED 时每对裁决，如 DROP:PASS 列表")
    args = ap.parse_args()

    rows, matched_count = load_rows(args.input)
    if not rows:
        print("FAIL_CLOSED: 零样本/零 glob 匹配")
        sys.exit(2)
    normed = [(r, normalize_field_aware(json.dumps(r.get("blind_visible", r), ensure_ascii=False))) for r in rows]

    # exact
    exact_map = {}
    for r, n in normed:
        h = hashlib.sha256(n.encode("utf-8")).hexdigest()
        exact_map.setdefault(h, []).append(r.get("sample_id"))
    exact_dups = {h: v for h, v in exact_map.items() if len(v) > 1}

    # near
    near = []
    for i in range(len(normed)):
        for j in range(i + 1, len(normed)):
            sim = jaccard(normed[i][1], normed[j][1])
            if sim > args.near_threshold:
                near.append({"a": normed[i][0].get("sample_id"), "b": normed[j][0].get("sample_id"),
                             "similarity": round(sim, 4), "review_status": args.near_review_status})

    # template concentration
    fam = {}
    for r in rows:
        f = r.get("template_family") or "none"
        fam[f] = fam.get(f, 0) + 1
    total = len(rows)
    fam_share = {k: round(v / total, 4) for k, v in fam.items()}
    over_conc = [k for k, v in fam_share.items() if v > args.template_max]

    # near review：REVIEWED 需要每对裁决；未裁决 -> near_unreviewed 存在
    near_review_ok = (len(near) == 0) or (args.near_review_status == "REVIEWED" and bool(args.near_review_decision))
    near_unreviewed_pairs = [p for p in near if p["review_status"] != "REVIEWED"]

    # 逐样本 G4
    samples = {}
    for r in rows:
        sid = r.get("sample_id")
        reasons = []
        if any(sid in grp for grp in exact_dups.values()):
            reasons.append("in_exact_duplicate_group")
        if any(sid in (p["a"], p["b"]) for p in near_unreviewed_pairs):
            reasons.append("in_unreviewed_near_dup")
        if (r.get("template_family") or "none") in over_conc:
            reasons.append("template_over_concentration")
        samples[sid] = {"ok": not reasons, "reasons": reasons}

    gates = {
        "G4_exact_dup_zero": len(exact_dups) == 0,
        "G4_near_reviewed": near_review_ok,
        "G4_template_concentration_ok": len(over_conc) == 0,
    }
    all_ok = all(gates.values()) and all(s["ok"] for s in samples.values())
    report = {
        "schema": "dedup_report", "version": "v4.1", "tool": "dedup_scan.py",
        "input": args.input, "checked": len(rows),
        "checked_sample_ids": sorted(r.get("sample_id") for r in rows),
        "input_set_hash": input_set_hash(r.get("sample_id") for r in rows),
        "samples": samples,
        "exact_duplicate_groups": exact_dups,
        "near_duplicate_pairs": near,
        "near_duplicate_review": {"status": args.near_review_status, "decision": args.near_review_decision},
        "template_family_share": fam_share,
        "template_over_concentration": over_conc,
        "gates": gates,
        "dedup_status": "PASS" if all_ok else "BLOCKED",
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    for k, v in gates.items():
        print(k, v)
    print("dedup_status", report["dedup_status"])
    sys.exit(2 if not all_ok else 0)


if __name__ == "__main__":
    main()