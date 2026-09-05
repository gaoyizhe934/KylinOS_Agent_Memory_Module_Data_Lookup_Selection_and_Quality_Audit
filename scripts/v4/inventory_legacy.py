#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 C1/P01 Legacy Inventory CLI（B 侧工具，2026-09-05）

按 v4.1 C3 硬要求：CLI 固定 IO、退出码、幂等、raw 只读、fail-closed、不写 Gold。
真实盘点 data/gold + data/processed(非aux) + data/interim(v1 候选)，不假设 N=265。
输出 legacy_inventory_v4.json；status=NOT_FROZEN（待 Data-R 签 LEGACY_SET_FROZEN）。
退出码：0=盘点完成；2=扫描异常（fail-closed）。
用法：python scripts/v4/inventory_legacy.py [--out reports/legacy_inventory_v4.json]
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def count_lines(p):
    try:
        return sum(1 for _ in open(p, encoding="utf-8") if _.strip())
    except Exception as e:
        print("ERR", p, e)
        return -1


def scan_gold():
    per_split = {"dev": 0, "regression": 0, "sealed_test": 0}
    total = 0
    for split in per_split:
        for p in glob.glob(os.path.join(ROOT, "data", "gold", split, "*.jsonl")):
            n = count_lines(p)
            if n > 0:
                per_split[split] += n
                total += n
    return total, per_split


def scan_processed():
    total = 0
    for p in glob.glob(os.path.join(ROOT, "data", "processed", "*.jsonl")):
        if "multiwoz" in os.path.basename(p):
            continue
        n = count_lines(p)
        total += n if n > 0 else 0
    return total


def scan_interim_v1():
    total = 0
    for p in glob.glob(os.path.join(ROOT, "data", "interim", "gold_candidates_*.jsonl")):
        b = os.path.basename(p)
        if "_v2" in b or "_v3" in b:
            continue
        n = count_lines(p)
        total += n if n > 0 else 0
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("reports", "legacy_inventory_v4.json"))
    args = ap.parse_args()

    g_total, g_split = scan_gold()
    p_total = scan_processed()
    i_total = scan_interim_v1()
    if g_total < 0 or p_total < 0 or i_total < 0:
        print("scan error -> FAIL_CLOSED")
        sys.exit(2)

    report = {
        "schema": "legacy_inventory_v4", "version": "v4.1", "tool": "inventory_legacy.py",
        "generated_by": "DGXD01(Data-B)", "date": "2026-09-05",
        "status": "NOT_FROZEN",
        "summary": {
            "gold_total": g_total,
            "gold_dev": g_split["dev"],
            "gold_regression": g_split["regression"],
            "gold_sealed": g_split["sealed_test"],
            "processed_nonaux_total": p_total,
            "interim_v1_candidates_total": i_total,
            "note": "N 为盘点结果非假设；IN_SCOPE 边界由 Data-R 判定",
        },
    }
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("written:", out)
    print(json.dumps(report["summary"], ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
