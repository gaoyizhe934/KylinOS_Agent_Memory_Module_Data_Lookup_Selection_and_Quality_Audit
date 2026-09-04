#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage8 P1-3 reconvert reconciliation (B). Run AFTER A reconverts processed.
# Checks: per-file row counts, timestamp UTC ms (.sssZ), raw_id for public_derived.
# Non-destructive; reads only.
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(REPO, 'data', 'processed')
DEFAULT_EXPECTED = os.path.join(REPO, 'reports', 'reconvert_expected_counts.json')

EXPECTED_DEFAULT = {
    'conflict_resolution.jsonl': 40,
    'end_to_end_session.jsonl': 15,
    'knowledge_retrieval.jsonl': 60,
    'knowledge_retrieval_t2ranking.jsonl': 200,
    'multiwoz_dialogues_sample.jsonl': 200,
    'multiwoz_public_sample.jsonl': 100,
    'precise_forgetting.jsonl': 40,
    'preference_extraction.jsonl': 60,
}

def ts_ok(s):
    if not s or not isinstance(s, str):
        return False
    s = s.strip()
    if not s.endswith('Z'):
        return False
    if len(s) < 24 or s[10] != 'T' or s[19] != '.':
        return False
    return s[20:23].isdigit()

def main():
    use_expected = os.path.exists(DEFAULT_EXPECTED)
    expected = {}
    if use_expected:
        with open(DEFAULT_EXPECTED, 'r', encoding='utf-8') as fh:
            expected = json.load(fh).get('expected', EXPECTED_DEFAULT)
    else:
        expected = EXPECTED_DEFAULT
    rows = {}
    ts_bad = []
    raw_missing = []
    gold_missing = []
    for path in sorted(glob.glob(os.path.join(PROCESSED, '*.jsonl'))):
        fname = os.path.basename(path)
        n = 0
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                n += 1
                o = json.loads(line)
                sid = o.get('sample_id', '')
                if not ts_ok(o.get('timestamp')):
                    ts_bad.append(sid + ':' + str(o.get('timestamp')))
                for f in ('created_at', 'updated_at'):
                    if f in o and not ts_ok(o.get(f)):
                        ts_bad.append(sid + ':' + f)
                if o.get('source') == 'public_derived' and not o.get('raw_id'):
                    raw_missing.append(sid)
                gold = o.get('gold')
                if gold is None or not isinstance(gold, dict) or len(gold) == 0:
                    gold_missing.append(sid)
        rows[fname] = n
    total = sum(rows.values())
    print('========== Stage8 P1-3 reconvert reconciliation ==========')
    print('per file rows: %s' % rows)
    print('total: %d' % total)
    mism = []
    for fname, exp in expected.items():
        if fname not in rows:
            mism.append(fname + ' MISSING')
        elif rows[fname] != exp:
            mism.append('%s=%d expect=%d' % (fname, rows[fname], exp))
    print('count mismatches (vs expected %s): %s' % ('ON' if use_expected else 'OFF(default)', mism if mism else 'none'))
    print('ts not UTC .sssZ: %d' % len(ts_bad))
    for x in ts_bad[:8]:
        print('  TS: ' + x)
    print('public_derived missing raw_id: %d' % len(raw_missing))
    print('records with empty gold: %d' % len(gold_missing))
    ok = (not mism) and (not ts_bad) and (not raw_missing) and (not gold_missing)
    print('RESULT: ' + ('PASS' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
