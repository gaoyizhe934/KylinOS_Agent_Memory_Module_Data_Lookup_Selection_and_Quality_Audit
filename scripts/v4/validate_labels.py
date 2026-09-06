#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v4.1 Label Validator（P2-A 工具 T08，Data-B）
结构/required/confidence/reason/枚举校验，不推断答案。fail-closed：
- 零记录/空输入 -> FAIL；
- sample_id 非空且唯一；
- required 字段存在；reason 非空；confidence 数值且 0<=c<=1；
- --schema 指定 task_type->label 枚举注册表；缺 schema/解析失败 -> exit 3；
- 每行必须有 task_type；task_type 未知（不在 schema）-> FAIL；
- label 必须 ∈ schema[task_type] 枚举 -> 非法枚举 FAIL；
不验证 task-specific 子字段语义答案。
退出码：0=PASS；2=校验失败；3=schema 缺失/输入缺失。
用法：python scripts/v4/validate_labels.py --input <label file> --role A|B [--schema registry/label_schema.json] [--out reports/label_validation.json]
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = ["sample_id", "label", "confidence", "reason"]
DEFAULT_SCHEMA = os.path.join(ROOT, "registry", "label_schema.json")


def load_schema(path):
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(p):
        return None, "schema_missing"
    try:
        with open(p, encoding="utf-8") as f:
            sch = json.load(f)
        enums = sch.get("task_label_enums", {})
        if not enums:
            return None, "schema_empty_task_label_enums"
        return enums, None
    except Exception as e:
        return None, "schema_parse_error:%s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--role", required=True, choices=["A", "B"])
    ap.add_argument("--schema", default=DEFAULT_SCHEMA)
    ap.add_argument("--out", default="reports/label_validation.json")
    args = ap.parse_args()

    path = os.path.join(ROOT, args.input)
    if not os.path.exists(path):
        print("FAIL_CLOSED: input not found", path)
        sys.exit(3)
    enums, sch_err = load_schema(args.schema)
    if enums is None:
        print("FAIL_CLOSED: schema unavailable:", sch_err)
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
            conf = r.get("confidence")
            if "confidence" in r and (not isinstance(conf, (int, float)) or isinstance(conf, bool)):
                errors.append({"line": i, "sample_id": sid, "error": "confidence not numeric"})
            elif isinstance(conf, (int, float)) and not isinstance(conf, bool) and not (0.0 <= conf <= 1.0):
                errors.append({"line": i, "sample_id": sid, "error": "confidence out of range [0,1]"})
            if "reason" in r and not str(r.get("reason") or "").strip():
                errors.append({"line": i, "sample_id": sid, "error": "reason empty"})
            # task_type -> label enum 校验
            tt = str(r.get("task_type") or "").strip()
            if not tt:
                errors.append({"line": i, "sample_id": sid, "error": "task_type missing"})
            elif tt not in enums:
                errors.append({"line": i, "sample_id": sid, "error": "unknown_task_type:" + tt})
            else:
                label = r.get("label")
                if not isinstance(label, str) or not label.strip():
                    errors.append({"line": i, "sample_id": sid, "error": "label empty"})
                elif label not in enums[tt]:
                    errors.append({"line": i, "sample_id": sid, "error": "invalid_label_enum:%s (task=%s)" % (label, tt)})

    if n == 0:
        print("FAIL_CLOSED: 零记录输入")
        sys.exit(2)

    report = {"schema": "label_validation", "version": "v4.1", "role": args.role, "checked": n,
              "errors": errors, "error_count": len(errors), "pass": len(errors) == 0,
              "label_schema": os.path.relpath(args.schema, ROOT) if not os.path.isabs(args.schema) else args.schema,
              "note": "结构/required/confidence/reason/task_type->label enum 校验；task-specific 子字段由语义裁决"}
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