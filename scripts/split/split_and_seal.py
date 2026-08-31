# -*- coding: utf-8 -*-
"""Split candidate gold by template family and write hashes."""
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def bucket(family):
    h = int(hashlib.sha256(family.encode("utf-8")).hexdigest(), 16) % 100
    return "dev" if h < 50 else ("regression" if h < 70 else "sealed_test")

def main():
    counts = {}
    for name in os.listdir(os.path.join(ROOT, "data/interim")):
        if not name.startswith("gold_candidates_"):
            continue
        rows = []
        with open(os.path.join(ROOT, "data/interim", name), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        for split in ("dev", "regression", "sealed_test"):
            items = [r for r in rows if bucket(r["template_family"]) == split]
            path = os.path.join(ROOT, "data/gold", split, name.replace("gold_candidates_", ""))
            with open(path, "w", encoding="utf-8") as fh:
                for r in items:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            counts[split] = counts.get(split, 0) + len(items)
    print(json.dumps(counts, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
