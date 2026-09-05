#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 P00 Preflight（P2-A 工具 T01，Data-B）

按 P00/P2-A 硬要求：git branch/HEAD/working-tree、v4.1 SOP/Prompt 存在性、
registry、main-to-data 4 接口、数据目录、Closure Q1-Q8 引用；fail-closed。
退出码：0=PASS(无 BLOCKED)；2=存在 BLOCKED_*；3=环境错误。
用法：python scripts/v4/preflight.py [--json reports/preflight_report.json]
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED_DIRS = ["data/raw", "data/interim", "data/processed", "data/gold", "registry", "evidence", "reports", "scripts"]
V41_DOCS = ["麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环执行SOP.docx",
            "麒麟OS_Agent_Memory_Data_v4.1_新人AI闭环施工台账.xlsx",
            "麒麟OS_Agent_Memory_Data_v4.1_AI_Prompt_Pack.md"]
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
    "prompt_registry": "registry/prompt_registry.csv",
    "provenance_registry": "registry/provenance_registry_v4.json",
}
Q8_REFS = {
    "Q1_legacy_inventory": "reports/legacy_inventory_v4_full.jsonl",
    "Q2_seal_audit": "reports/seal_audit_v4.1.json",
    "Q3_tooling": "reports/tooling_bootstrap_report.json",
    "Q4_kb": "interfaces/main_to_data/kb_import_contract.json",
    "Q5_runtime": "interfaces/main_to_data/frozen_build_manifest.json",
    "Q6_trial40": "reports/trial40_reuse_audit.json",
    "Q7_quota": "reports/quota_plan_v4.1.csv",
    "Q8_independence": "reports/independence_manifest.json",
}


def git_state():
    def _run(cmd):
        try:
            return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.strip()
        except Exception:
            return "n/a"
    return {
        "branch": _run(["git", "branch", "--show-current"]),
        "head": _run(["git", "rev-parse", "HEAD"]),
        "dirty": _run(["git", "status", "--porcelain"]) != "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="output report path")
    args = ap.parse_args()
    checks = []
    blockers = []

    gs = git_state()
    checks.append({"id": "GIT:branch", "value": gs["branch"], "status": "PASS" if gs["branch"] not in ("n/a", "") else "FAIL"})
    checks.append({"id": "GIT:head", "value": gs["head"], "status": "PASS" if gs["head"] not in ("n/a", "") else "FAIL"})
    checks.append({"id": "GIT:working_tree", "value": "dirty" if gs["dirty"] else "clean", "status": "PASS"})

    for d in REQUIRED_DIRS:
        ex = os.path.isdir(os.path.join(ROOT, d))
        checks.append({"id": "DIR:" + d, "exists": ex, "status": "PASS" if ex else "FAIL"})
        if not ex:
            blockers.append({"id": "DIR:" + d, "reason": "目录缺失"})

    for name in V41_DOCS:
        ex = os.path.isfile(os.path.join(ROOT, name))
        checks.append({"id": "DOC:" + name, "exists": ex, "status": "PASS" if ex else "PENDING"})

    for name, rel in INTERFACE_PATHS.items():
        ex = os.path.isfile(os.path.join(ROOT, rel))
        st = "PASS" if ex else "BLOCKED_MAIN_CONTRACT"
        checks.append({"id": "IF:" + name, "path": rel, "exists": ex, "status": st})
        if not ex:
            blockers.append({"id": "IF:" + name, "reason": rel + " 缺失（需主仓提供/FROZEN）"})

    for name, rel in REGISTRY_PATHS.items():
        ex = os.path.isfile(os.path.join(ROOT, rel))
        checks.append({"id": "REG:" + name, "path": rel, "exists": ex, "status": "PASS" if ex else "PENDING"})

    for q, rel in Q8_REFS.items():
        ex = os.path.isfile(os.path.join(ROOT, rel))
        checks.append({"id": "Q8:" + q, "path": rel, "exists": ex, "status": "PASS" if ex else "PENDING"})

    report = {
        "schema": "preflight_report", "version": "v4.1", "tool": "preflight.py",
        "generated_by": "DGXD01(Data-B)", "git": gs,
        "checks": checks, "blockers": blockers,
        "next_action": "safe_parallel: inventory_legacy / tooling bootstrap; 不产生 production Gold",
    }
    if args.json:
        out = os.path.join(ROOT, args.json)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    else:
        for c in checks:
            print(c["id"], c["status"])
    sys.exit(2 if any(b["id"].startswith("IF:") or b["id"].startswith("DIR:") for b in blockers) else 0)


if __name__ == "__main__":
    main()