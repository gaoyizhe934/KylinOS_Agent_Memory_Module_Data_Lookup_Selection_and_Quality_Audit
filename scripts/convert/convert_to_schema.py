# -*- coding: utf-8 -*-
"""Convert interim gold candidates to processed unified schema (idempotent)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    interim = os.path.join(ROOT, "data/interim")
    processed = os.path.join(ROOT, "data/processed")
    total = 0
    for name in sorted(os.listdir(interim)):
        if not name.startswith("gold_candidates_") or not name.endswith(".jsonl"):
            continue
        rows = []
        with open(os.path.join(interim, name), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                row["dataset_version"] = "kylin_memory_gold_v1.0"
                row["source"] = "team_authored"
                row["raw_id"] = None
                row["source_file"] = "data/interim/" + name
                row["source_version"] = "v0_candidate_draft"
                rows.append(row)
        out_name = name.replace("gold_candidates_", "").replace(".jsonl", ".jsonl")
        with open(os.path.join(processed, out_name), "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        total += len(rows)
        print("converted", out_name, len(rows))
    print("total", total, "silent_drop", 0)
    sys.exit(0)

if __name__ == "__main__":
    main()
