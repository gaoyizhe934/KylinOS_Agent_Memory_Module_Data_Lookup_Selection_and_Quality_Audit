#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Provenance Resolver（P2-A 工具 T03，Data-B）

source-layer 区分：
  public_direct / public_controlled_derived：必须带 dataset_id，join source_registry + license_registry；
  os_controlled_authored：校验 generation manifest（generation_id/prompt_version/seed/model/scenario_spec_id）+ prompt registry + source_file 可解析；不伪造公共 license。
禁止从文件 basename 猜 dataset_id；无法确定 source layer/dataset_id => fail-closed。
零 glob / Registry 缺失 / 报告字段缺失 => nonzero。
输出含 checked_sample_ids + samples(sid->ok) + input_set_hash（供 T06 join）。
退出码：0=PASS；2=unresolved/空输入/Registry 缺失；3=环境错误。
用法：python scripts/v4/provenance_resolver.py --input <glob> [--out reports/prov_report.json]
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_CSV = os.path.join(ROOT, "registry", "source_registry.csv")
LIC_CSV = os.path.join(ROOT, "registry", "license_registry.csv")
PUBLIC_LAYERS = {"public_direct", "public_controlled_derived"}
OS_LAYER = "os_controlled_authored"
GEN_REQUIRED = ["generation_id", "prompt_version", "seed", "model"]


def read_csv(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return {r["dataset_id"]: r for r in csv.DictReader(f)}


def input_set_hash(ids):
    return hashlib.sha256(json.dumps(sorted(ids)).encode("utf-8")).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True)
    ap.add_argument("--out", default="reports/prov_report.json")
    args = ap.parse_args()

    src_reg = read_csv(SRC_CSV)
    lic_reg = read_csv(LIC_CSV)
    if src_reg is None or lic_reg is None:
        print("FAIL_CLOSED: source/license registry missing")
        sys.exit(3)

    checked = []
    unresolved = []
    samples = {}
    for pat in args.input:
        matched = glob.glob(os.path.join(ROOT, pat))
        if not matched:
            unresolved.append({"pattern": pat, "reason": "glob 零匹配（fail-closed）"})
            continue
        for p in matched:
            try:
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        r = json.loads(line)
                        sid = r.get("sample_id")
                        checked.append(sid)
                        dm = r.get("design_metadata", {})
                        gen = dm.get("generation", {})
                        src = r.get("source") or gen.get("source")
                        sfile = r.get("source_file") or gen.get("source_file")
                        missing = []
                        if not src:
                            missing.append("source")
                        if not sfile:
                            missing.append("source_file")
                        elif not os.path.exists(os.path.join(ROOT, sfile)):
                            missing.append("locator_not_resolvable:" + sfile)
                        layer = gen.get("source_layer") or r.get("source_layer")
                        if src in PUBLIC_LAYERS or layer in PUBLIC_LAYERS:
                            ds = gen.get("dataset_id")
                            if not ds:
                                missing.append("dataset_id_missing_for_public")
                            else:
                                if ds not in src_reg:
                                    missing.append("dataset_not_in_source_registry")
                                if ds not in lic_reg:
                                    missing.append("dataset_not_in_license_registry")
                        elif src == OS_LAYER or layer == OS_LAYER:
                            for fld in GEN_REQUIRED:
                                if not gen.get(fld):
                                    missing.append("generation_missing:" + fld)
                            # scenario_spec_id 以已合并 #34 schema 为准：design_metadata.scenario_spec_id
                            if not dm.get("scenario_spec_id"):
                                missing.append("design_metadata_missing:scenario_spec_id")
                            if not os.path.exists(os.path.join(ROOT, "registry", "prompt_registry.csv")):
                                missing.append("prompt_registry_missing")
                        else:
                            missing.append("source_layer_undetermined")
                        samples[sid] = {"ok": not missing, "reason": missing}
                        if missing:
                            unresolved.append({"sample_id": sid, "missing": missing, "file": os.path.relpath(p, ROOT)})
            except Exception as e:
                unresolved.append({"file": os.path.relpath(p, ROOT), "error": str(e)})

    if not checked:
        unresolved.append({"reason": "零样本输入（fail-closed）"})

    report = {
        "schema": "prov_report", "version": "v4.1", "tool": "provenance_resolver.py",
        "input": args.input, "checked": len(checked),
        "checked_sample_ids": sorted(set(checked)), "input_set_hash": input_set_hash(set(checked)),
        "samples": samples, "unresolved": unresolved, "unresolved_count": len(unresolved),
        "gates": {"G1_provenance_unresolved_zero": len(unresolved) == 0},
    }
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("checked=%d unresolved=%d" % (len(checked), len(unresolved)))
    sys.exit(2 if unresolved else 0)


if __name__ == "__main__":
    main()