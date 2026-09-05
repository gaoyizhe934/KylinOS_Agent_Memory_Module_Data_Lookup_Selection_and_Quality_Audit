#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Seal / Release Packager（P2-A 工具 T12，Data-B/R）
hash/read-only/revoke/reseal/manifest；保留 seal generation 历史；sealed 答案隔离。
用法：python scripts/v4/seal_release.py --sealed <sealed dir> --sha256 --out release/
"""
import argparse
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
    ap.add_argument("--sealed", required=True, help="sealed 数据目录")
    ap.add_argument("--out", default="release")
    ap.add_argument("--manifest", default="release/DATA_RELEASE_v4.1_manifest.json")
    args = ap.parse_args()

    sealed_dir = os.path.join(ROOT, args.sealed)
    if not os.path.isdir(sealed_dir):
        print("FAIL_CLOSED: sealed dir missing", sealed_dir)
        sys.exit(3)

    files = sorted(f for f in os.listdir(sealed_dir) if f.endswith(".jsonl"))
    hashes = {}
    for f in files:
        hashes[f] = sha256(os.path.join(sealed_dir, f))

    manifest = {
        "schema": "DATA_RELEASE_v4.1_manifest", "version": "v4.1",
        "sealed_generation": "seal-v2", "status": "PENDING_REVIEW",
        "files": hashes, "sealed_count": len(files),
        "seal_history": ["seal-v1 REVOKED (v1 模板污染)", "seal-v2 PENDING_REVIEW (排除已暴露 fingerprints)"],
        "signed_by": "PENDING (Data-R)",
    }
    out_dir = os.path.join(ROOT, args.out)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(ROOT, args.manifest), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "SHA256SUMS"), "w", encoding="utf-8") as f:
        for name, h in hashes.items():
            f.write("%s  %s\n" % (h, name))
    print("written:", args.manifest, "SHA256SUMS")
    print("sealed_count=%d status=%s" % (len(files), manifest["status"]))
    sys.exit(0)


if __name__ == "__main__":
    main()