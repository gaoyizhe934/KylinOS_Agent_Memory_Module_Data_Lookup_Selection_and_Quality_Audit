#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 G4 Dedup Scan（P2-A 工具 T04，Data-B）

exact duplicate（归一化后完全一致）+ near duplicate（Jaccard > 0.85 送审）+ template/source 集中度。
field-aware normalization：保留承载业务语义的 version/date/id/数值；不做粗暴删除。
fail-closed：exact dup>0 → FAIL；near>0.85 → REVIEWER；单 template_family>25% → FAIL。
退出码：0=PASS；2=存在 exact dup 或集中度 FAIL；3=环境/解析错误。
用法：python scripts/v4/dedup_scan.py --input data/interim/candidates_v4/exemplar_candidates/*.jsonl [--out reports/dedup_report.json]
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_rows(paths):
    rows = []
    for pat in paths:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rows.append(json.loads(line))
    return rows


def normalize_field_aware(text):
    """保留 version/date/id/数字：不清除这些 token；只做空白/大小写/标点归一。"""
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
            out.extend(list(t))  # 中文按字切分
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
    ap.add_argument("--input", nargs="+", required=True, help="glob 或文件路径")
    ap.add_argument("--out", default="reports/dedup_report.json")
    ap.add_argument("--near-threshold", type=float, default=0.85)
    ap.add_argument("--template-max", type=float, default=0.25)
    args = ap.parse_args()

    rows = load_rows(args.input)
    normed = [(r, normalize_field_aware(json.dumps(r.get("blind_visible", r), ensure_ascii=False))) for r in rows]

    exact = {}
    near = []
    for i, (r, n) in enumerate(normed):
        h = hashlib.sha256(n.encode("utf-8")).hexdigest()
        exact.setdefault(h, []).append(r.get("sample_id"))
    exact_dups = {h: v for h, v in exact.items() if len(v) > 1}

    for i in range(len(normed)):
        for j in range(i + 1, len(normed)):
            sim = jaccard(normed[i][1], normed[j][1])
            if sim > args.near_threshold:
                near.append({"a": normed[i][0].get("sample_id"), "b": normed[j][0].get("sample_id"), "similarity": round(sim, 4)})

    fam = {}
    for r in rows:
        f = r.get("template_family") or "none"
        fam[f] = fam.get(f, 0) + 1
    total = len(rows) or 1
    fam_share = {k: round(v / total, 4) for k, v in fam.items()}
    over_conc = [k for k, v in fam_share.items() if v > args.template_max]

    report = {
        "schema": "dedup_report", "version": "v4.1", "tool": "dedup_scan.py",
        "generated_by": "DGXD01(Data-B)", "input": args.input,
        "exact_duplicate_groups": exact_dups,
        "exact_duplicate_count": sum(len(v) for v in exact_dups.values()) - len(exact_dups),
        "near_duplicate_pairs": near,
        "near_duplicate_count": len(near),
        "template_family_share": fam_share,
        "template_over_concentration": over_conc,
        "gates": {
            "G4_exact_dup_zero": len(exact_dups) == 0,
            "G4_near_reviewed": len(near) == 0,
            "G4_template_concentration_ok": len(over_conc) == 0,
        },
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    for k, v in report["gates"].items():
        print(k, v)
    fail = (len(exact_dups) > 0) or (len(over_conc) > 0)
    sys.exit(2 if fail else 0)


if __name__ == "__main__":
    main()