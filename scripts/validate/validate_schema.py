# -*- coding: utf-8 -*-
"""Validate processed JSONL against the unified schema."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = ["sample_id", "dataset_version", "task_type", "language", "user_id",
            "conversation_id", "timestamp", "input", "gold", "evidence",
            "source", "template_family", "review_status"]

def main():
    failed = 0
    for name in os.listdir(os.path.join(ROOT, "data/processed")):
        if not name.endswith(".jsonl"):
            continue
        path = os.path.join(ROOT, "data/processed", name)
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                missing = [f for f in REQUIRED if f not in row]
                if missing:
                    print("FAIL", name, row.get("sample_id"), "missing", missing)
                    failed += 1
    print("validation", "PASS" if failed == 0 else f"FAIL count={failed}")
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
