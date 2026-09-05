#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P00 Preflight（B 侧工具，2026-09-05）

按 v4.1 C3 硬要求：CLI 固定 IO、退出码、幂等、raw 只读、fail-closed、不写 Gold。
检查：目录/版本/registry/接口包存在性 + 角色边界占位。
退出码：0=PASS(或仅有非阻塞 PENDING)；2=存在 BLOCKED_* 或文件缺失(主仓接口)；3=环境错误。
用法：python scripts/v4/preflight.py [--json out.json]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED_DIRS = ["data/raw", "data/interim", "data/processed", "data/gold", "registry", "evidence", "reports", "scripts"]
INTERFACE_PATHS = {
    "schema_snapshot": "interfaces/main_to_data/schema_snapshot.json",
    "kb_import_contract": "interfaces/main_to_data/kb_import_contract.json",
    "runtime_runner_contract": "interfaces/main_to_data/runtime_runner_contract.md",
    "frozen_build_manifest": "interfaces/main_to_data/frozen_build_manifest.json",
}
REGISTRY_PATHS = {
    "source_registry": "registry/source_registry.csv",
    "license_registry": "registry/license_registry.csv",
    "leaked_registry": "registry/leaked_content_registry.json",
    "provenance_registry": "registry/provenance_registry_v4.json",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="output report path")
    args = ap.parse_args()
    checks = []
    blockers = []

    for d in REQUIRED_DIRS:
        checks.append({"id": "DIR:" + d, "exists": os.path.isdir(os.path.join(ROOT, d)),
                       "status": "PASS" if os.path.isdir(os.path.join(ROOT, d)) else "FAIL"})

    for name, rel in INTERFACE_PATHS.items():
        ex = os.path.isfile(os.path.join(ROOT, rel))
        status = "PASS" if ex else "BLOCKED_MAIN_CONTRACT"
        checks.append({"id": "IF:" + name, "path": rel, "exists": ex, "status": status})
        if not ex:
            blockers.append({"id": "IF:" + name, "reason": rel + " 缺失（需主仓提供/FROZEN）"})

    for name, rel in REGISTRY_PATHS.items():
        ex = os.path.isfile(os.path.join(ROOT, rel))
        checks.append({"id": "REG:" + name, "path": rel, "exists": ex, "status": "PASS" if ex else "PENDING"})

    report = {
        "schema": "preflight_report", "version": "v4.1", "tool": "preflight.py",
        "generated_by": "DGXD01(Data-B)", "git": "n/a",
        "checks": checks, "blockers": blockers,
        "next_action": "safe_parallel: inventory_legacy / tooling bootstrap; 不产出 production Gold",
    }
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", args.json)
    else:
        for c in checks:
            print(c["id"], c["status"])
    # exit code: 2 if main-contract blockers (fail-closed), else 0
    sys.exit(2 if any(b["id"].startswith("IF:") for b in blockers) else 0)


if __name__ == "__main__":
    main()
