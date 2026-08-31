# -*- coding: utf-8 -*-
"""Cross-set leakage check for user/conversation/template."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    sets = {}
    for split in ("dev", "regression", "sealed_test"):
        rows = []
        for name in os.listdir(os.path.join(ROOT, "data/gold", split)):
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(ROOT, "data/gold", split, name), encoding="utf-8") as fh:
                rows += [json.loads(l) for l in fh if l.strip()]
        sets[split] = rows
    ok = True
    for a, rows_a in sets.items():
        for b, rows_b in sets.items():
            if a >= b:
                continue
            for key in ("sample_id", "user_id", "conversation_id", "template_family"):
                va = {r.get(key) for r in rows_a}
                vb = {r.get(key) for r in rows_b}
                inter = va & vb
                if inter:
                    print("LEAK", a, b, key, len(inter))
                    ok = False
    print("leakage_check", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
