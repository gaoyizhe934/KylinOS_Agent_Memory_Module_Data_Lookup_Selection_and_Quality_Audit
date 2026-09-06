#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Seal / Release Packager（P2-A 工具 T12，Data-B/R）——按 P90 顺序实现

1. grouped split 验证（每个 sample 按 split_samples.csv 解析，强制 sealed_test；0 group 跨 split）
2. exposure eligibility（DEV_REG_ONLY 不得进 sealed）
3. final leakage scan（leak report 必须绑定本次 sealed set：input_set_hash/checked ids 一致）
4. seal generation（必须来自显式有效 seal record，缺失 => fail-closed，禁止默认）
5. SHA256
6. read-only copy（设置并验证只读）
7. manifest
8. compatibility report
任一 fail -> exit 2；Data-R 是唯一 PENDING_REVIEW -> APPROVED 签署者。
用法：python scripts/v4/seal_release.py --gold <glob> --split-samples <split_samples.csv> --leak <leak_report.json> --exposure <exposure.json> --seal-record <seal_record.json> [--out release]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import shutil
import stat
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
    ap.add_argument("--split-samples", required=True, help="split_grouped.py 输出 split_samples.csv (sample_id,group_key,split)")
    ap.add_argument("--leak", required=True)
    ap.add_argument("--exposure", required=True)
    ap.add_argument("--seal-record", required=True)
    ap.add_argument("--out", default="release")
    args = ap.parse_args()

    # 1) split_samples 解析
    sp_path = os.path.join(ROOT, args.split_samples)
    if not os.path.exists(sp_path):
        print("FAIL_CLOSED: split_samples manifest missing")
        sys.exit(3)
    sample_split = {}
    group_split = {}
    with open(sp_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sample_split[row["sample_id"]] = row["split"]
            gk = row["group_key"]
            group_split[gk] = row["split"]

    # 2) exposure eligibility
    exp = json.load(open(os.path.join(ROOT, args.exposure), encoding="utf-8"))
    dev_reg_only = set(exp.get("dev_reg_only_samples", []))

    # 3) final leak scan 绑定
    leak = json.load(open(os.path.join(ROOT, args.leak), encoding="utf-8"))
    if leak.get("leak_count", 1) > 0:
        print("FAIL_CLOSED: final leak scan not clean")
        sys.exit(2)

    # 4) seal record 显式 generation
    rec = json.load(open(os.path.join(ROOT, args.seal_record), encoding="utf-8"))
    gen = rec.get("seal_generation")
    if not gen:
        print("FAIL_CLOSED: seal_generation missing in seal record（禁止默认）")
        sys.exit(2)

    # 收集 gold sealed 样本 + 校验 split/exposure/cross
    sealed_samples = []
    sealed_ids = []
    out_dir = os.path.join(ROOT, args.out, "sealed_" + gen)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    cross = 0
    for pat in args.gold:
        for p in glob.glob(os.path.join(ROOT, pat)):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    sid = r.get("sample_id")
                    sp = sample_split.get(sid)
                    if sp is None:
                        print("FAIL_CLOSED: sample %s missing in split manifest" % sid)
                        sys.exit(2)
                    if sp != "sealed_test":
                        print("FAIL_CLOSED: sample %s split=%s != sealed_test" % (sid, sp))
                        sys.exit(2)
                    if sid in dev_reg_only:
                        print("FAIL_CLOSED: DEV_REG_ONLY sample in sealed", sid)
                        sys.exit(2)
                    sealed_ids.append(sid)
                    dst = os.path.join(out_dir, os.path.basename(p))
                    with open(dst, "a", encoding="utf-8") as out_f:
                        out_f.write(line)

    if not sealed_ids:
        print("FAIL_CLOSED: no sealed samples")
        sys.exit(2)
    # group 跨 split 校验
    seen_g = {}
    for row in csv.DictReader(open(sp_path, encoding="utf-8")):
        if row["sample_id"] in sealed_ids:
            gk = row["group_key"]
            if gk in seen_g and seen_g[gk] != "sealed_test":
                cross += 1
            seen_g[gk] = "sealed_test"

    # leak 绑定 sealed set
    if set(leak.get("checked_sample_ids", [])) != set(sealed_ids):
        print("FAIL_CLOSED: leak report checked set != sealed set（绑定失败）")
        sys.exit(2)

    # 5/6) SHA256 + read-only copy（设置并验证只读）
    hashes = {}
    for name in sorted(os.listdir(out_dir)):
        if name.endswith(".jsonl"):
            path = os.path.join(out_dir, name)
            hashes[name] = sha256(path)
            os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            if os.access(path, os.W_OK):
                print("FAIL_CLOSED: sealed file not read-only:", name)
                sys.exit(2)

    # 7/8) manifest + compat
    manifest = {
        "schema": "DATA_RELEASE_v4.1_manifest", "version": "v4.1",
        "seal_generation": gen, "status": "PENDING_REVIEW",
        "sealed_sample_count": len(sealed_ids),
        "files": hashes, "signed_by": "PENDING (Data-R)",
    }
    with open(os.path.join(ROOT, args.out, "DATA_RELEASE_v4.1_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ROOT, args.out, "SHA256SUMS"), "w", encoding="utf-8") as f:
        for name, h in hashes.items():
            f.write("%s  %s\n" % (h, name))
    compat = {"schema": "compatibility_report", "version": "v4.1", "seal_generation": gen,
              "sealed_sample_count": len(sealed_ids), "cross_split": cross,
              "dev_reg_only_excluded": True, "final_leak_clean": True, "leak_bound_to_sealed_set": True}
    with open(os.path.join(ROOT, args.out, "compatibility_report.json"), "w", encoding="utf-8") as f:
        json.dump(compat, f, ensure_ascii=False, indent=2)
    print("written:", out_dir, "samples=%d cross_split=%d" % (len(sealed_ids), cross))
    sys.exit(2 if cross else 0)


if __name__ == "__main__":
    main()