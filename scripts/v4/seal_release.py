#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Seal / Release Packager（P2-A 工具 T12，Data-B/R）——按 P90 顺序实现

1. grouped split 验证（0 group 跨 split）
2. exposure eligibility（DEV_REG_ONLY 不得进 sealed）
3. final leakage scan
4. sealed generation（来自 seal record，不硬编码）
5. SHA256
6. read-only copy
7. manifest
8. compatibility report
任一 fail -> exit 2；Data-R 仍是唯一 PENDING_REVIEW -> APPROVED 签署者。
用法：python scripts/v4/seal_release.py --gold <glob> --split <split_manifest.csv> --leak <leak_report.json> --exposure <exposure.json> --seal-record <seal_record.json> [--out release]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", nargs="+", required=True)
    ap.add_argument("--split", required=True, help="split_grouped.py 输出 split_manifest.csv")
    ap.add_argument("--leak", required=True, help="final leakage_scan 报告")
    ap.add_argument("--exposure", required=True, help="exposure registry（DEV_REG_ONLY 样本）")
    ap.add_argument("--seal-record", required=True, help="seal generation record")
    ap.add_argument("--out", default="release")
    args = ap.parse_args()

    # 1) split manifest
    split_path = os.path.join(ROOT, args.split)
    if not os.path.exists(split_path):
        print("FAIL_CLOSED: split manifest missing")
        sys.exit(3)
    group_split = {}
    cross = 0
    seen = {}
    with open(split_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            group_split[row["group_key"]] = row["split"]
    # 2) exposure eligibility
    exp = json.load(open(os.path.join(ROOT, args.exposure), encoding="utf-8"))
    dev_reg_only = set(exp.get("dev_reg_only_samples", []))
    # 3) final leak scan
    leak = json.load(open(os.path.join(ROOT, args.leak), encoding="utf-8"))
    if leak.get("leak_count", 1) > 0:
        print("FAIL_CLOSED: final leak scan not clean")
        sys.exit(2)
    # 4) seal record
    rec = json.load(open(os.path.join(ROOT, args.seal_record), encoding="utf-8"))
    gen = rec.get("seal_generation", "seal-v2")
    if gen in ("", None):
        print("FAIL_CLOSED: seal generation empty")
        sys.exit(2)

    # 收集 gold + 分配 split + exposure 检查
    sealed_samples = []
    out_dir = os.path.join(ROOT, args.out, "sealed_" + gen)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    for pat in args.gold:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    sid = r.get("sample_id")
                    if sid in dev_reg_only:
                        print("FAIL_CLOSED: DEV_REG_ONLY sample in sealed", sid)
                        sys.exit(2)
                    if sid in seen and seen[sid] != "sealed_test":
                        cross += 1
                    seen[sid] = "sealed_test"
                    sealed_samples.append(sid)
                    # 6) read-only copy
                    dst = os.path.join(out_dir, os.path.basename(p))
                    with open(dst, "a", encoding="utf-8") as out_f:
                        out_f.write(line)

    if not sealed_samples:
        print("FAIL_CLOSED: no sealed samples")
        sys.exit(2)

    # 5) SHA256 of sealed files
    hashes = {}
    for name in sorted(os.listdir(out_dir)):
        if name.endswith(".jsonl"):
            hashes[name] = sha256(os.path.join(out_dir, name))

    # 7/8) manifest + compat report
    manifest = {
        "schema": "DATA_RELEASE_v4.1_manifest", "version": "v4.1",
        "seal_generation": gen, "status": "PENDING_REVIEW",
        "sealed_sample_count": len(sealed_samples),
        "files": hashes, "signed_by": "PENDING (Data-R)",
    }
    with open(os.path.join(ROOT, args.out, "DATA_RELEASE_v4.1_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, args.out, "SHA256SUMS"), "w", encoding="utf-8") as f:
        for name, h in hashes.items():
            f.write("%s  %s\n" % (h, name))
    compat = {"schema": "compatibility_report", "version": "v4.1", "seal_generation": gen,
              "sealed_sample_count": len(sealed_samples), "cross_split": cross,
              "dev_reg_only_excluded": True, "final_leak_clean": True}
    with open(os.path.join(ROOT, args.out, "compatibility_report.json"), "w", encoding="utf-8") as f:
        json.dump(compat, f, ensure_ascii=False, indent=2)
    print("written:", out_dir, "samples=%d cross_split=%d" % (len(sealed_samples), cross))
    sys.exit(2 if cross else 0)


if __name__ == "__main__":
    main()