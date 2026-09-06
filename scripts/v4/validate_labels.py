#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Label Validator（P2-A 工具 T08，Data-B）
只做结构/枚举/required 校验，不推断答案。fail-closed：
- 零记录/空输入 -> FAIL；
- sample_id 非空且唯一；
- required 字段存在；reason 非空；confidence 为数值且 0<=c<=1；
- 可稳定机器化的枚举校验：label 非空（具体 task label enum 由外部 schema 提供，不伪装成已校验）；
不验证 task-specific 语义答案。
退出码：0=PASS；2=校验失败；3=输入缺失。
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
    seen_ids = set()
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
                if field not in r or (field == "sample_id" and not str(r.get(field) or "").strip()):
                    errors.append({"line": i, "sample_id": r.get("sample_id"), "error": "missing/empty %s" % field})
            sid = str(r.get("sample_id") or "").strip()
            if sid:
                if sid in seen_ids:
                    errors.append({"line": i, "sample_id": sid, "error": "duplicate sample_id"})
                seen_ids.add(sid)
            # confidence 类型与范围
            conf = r.get("confidence")
            if "confidence" in r and not isinstance(conf, (int, float)):
                errors.append({"line": i, "sample_id": sid, "error": "confidence not numeric"})
            elif isinstance(conf, (int, float)):
                if isinstance(conf, bool) or not (0.0 <= conf <= 1.0):
                    errors.append({"line": i, "sample_id": sid, "error": "confidence out of range [0,1]"})
            # reason 非空
            if "reason" in r and not str(r.get("reason") or "").strip():
                errors.append({"line": i, "sample_id": sid, "error": "reason empty"})
            # label 非空
            if "label" in r and not str(r.get("label") or "").strip():
                errors.append({"line": i, "sample_id": sid, "error": "label empty"})

    if n == 0:
        print("FAIL_CLOSED: 零记录输入")
        sys.exit(2)

    report = {"schema": "label_validation", "version": "v4.1", "role": args.role, "checked": n,
              "errors": errors, "error_count": len(errors), "pass": len(errors) == 0,
              "note": "结构/required/confidence/reason/enum(非空) 校验；task-specific label enum 需外部 schema，不伪装已验证"}
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