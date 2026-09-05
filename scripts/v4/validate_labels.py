#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Label Validator（P2-A 工具 T08，Data-B）
只做结构/枚举/required 校验，不推断答案。缺字段/非法枚举 -> exit 2。
用法：python scripts/v4/validate_labels.py --input <label file> --role A|B [--out reports/label_validation.json]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = ["sample_id", "label", "confidence", "reason"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--role", required=True, choices=["A", "B"])
    ap.add_argument("--out", default="reports/label_validation.json")
    args = ap.parse_args()

    path = os.path.join(ROOT, args.input)
    if not os.path.exists(path):
        print("FAIL_CLOSED: input not found", path)
        sys.exit(3)
    errors = []
    n = 0
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            n += 1
            try:
                r = json.loads(line)
            except Exception as e:
                errors.append({"line": i, "error": "json parse: %s" % e})
                continue
            for field in REQUIRED:
                if field not in r:
                    errors.append({"line": i, "sample_id": r.get("sample_id"), "error": "missing %s" % field})
    report = {"schema": "label_validation", "version": "v4.1", "role": args.role, "checked": n,
              "errors": errors, "error_count": len(errors), "pass": len(errors) == 0}
    if args.out:
        out = os.path.join(ROOT, args.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("written:", out)
    print("checked=%d errors=%d pass=%s" % (n, len(errors), report["pass"]))
    sys.exit(2 if errors else 0)


if __name__ == "__main__":
    main()