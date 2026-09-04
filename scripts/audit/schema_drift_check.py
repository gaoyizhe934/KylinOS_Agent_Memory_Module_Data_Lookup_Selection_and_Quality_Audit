#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Schema drift check (B side): data pack gold fields vs registry/field_mapping.json.
# Non-destructive; CANDIDATE/FREEZE discipline - does not rewrite Gold values.
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(REPO, 'data', 'processed')
MAPPING = os.path.join(REPO, 'registry', 'field_mapping.json')
ENUM = os.path.join(PROCESSED, 'enum_dictionary.json')
OUT = os.path.join(REPO, 'reports', 'schema_drift_check_output_20260904.txt')

def main():
    with open(MAPPING, 'r', encoding='utf-8') as fh:
        mapping = json.load(fh)
    rows = mapping.get('rows', [])
    allowed = {}
    for r in rows:
        task = r.get('task', '*')
        allowed.setdefault(task, set()).add(r.get('data_field'))

    found = {}
    for path in sorted(glob.glob(os.path.join(PROCESSED, '*.jsonl'))):
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                o = json.loads(line)
                task = o.get('task_type')
                gold = o.get('gold') if isinstance(o.get('gold'), dict) else {}
                found.setdefault(task, set()).update(k for k in gold.keys())

    unregistered = []
    for task, keys in sorted(found.items()):
        a = set(allowed.get(task, set())) | set(allowed.get('*', set()))
        for k in sorted(keys):
            if k not in a:
                unregistered.append(task + '.' + k)

    with open(ENUM, 'r', encoding='utf-8') as fh:
        enum = json.load(fh)
    meta = enum.get('_meta', {})
    meta_issues = []
    if not meta.get('layer_note'):
        meta_issues.append('enum_dictionary._meta.layer_note missing')
    if not meta.get('eval_or_legacy_keys'):
        meta_issues.append('enum_dictionary._meta.eval_or_legacy_keys missing')

    lines = []
    lines.append('Schema drift check output (B side) - 2026-09-04')
    lines.append('mapping rows: %d' % len(rows))
    for task, keys in sorted(found.items()):
        lines.append('task=%s gold fields=%s' % (task, ', '.join(sorted(keys))))
    lines.append('unregistered gold fields: %d' % len(unregistered))
    for u in unregistered:
        lines.append('  UNREGISTERED: ' + u)
    lines.append('enum meta issues: %d' % len(meta_issues))
    for m in meta_issues:
        lines.append('  META: ' + m)
    text = chr(10).join(lines)
    print(text)
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(text + chr(10))
    print('output written: %s' % OUT)
    if unregistered or meta_issues:
        sys.exit(1)

if __name__ == '__main__':
    main()
