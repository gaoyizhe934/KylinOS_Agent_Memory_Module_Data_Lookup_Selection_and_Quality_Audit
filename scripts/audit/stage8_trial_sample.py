#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 8 trial set sampler (B side).

Stratified deterministic sampling of trial annotation items from data/processed,
covering the gold task types (excludes auxiliary_dialogue by default, since the
manual v1.3 section 7.1 defines those as scenario/negative-source only, not to
be gold-annotated). tool_result has no processed pool yet; supply A-side
controlled scenario candidates via --extra and --per-task tool=N.

Usage:
  python scripts/audit/stage8_trial_sample.py --total 40 --seed 42
"""
import argparse
import glob
import io
import json
import os
import random
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SHORT_TO_TASK = {
    'pref': 'preference_extraction',
    'retr': 'knowledge_retrieval',
    'conf': 'conflict_resolution',
    'forg': 'precise_forgetting',
    'tool': 'tool_result',
    'e2e': 'end_to_end_session',
}
NON_AUX_TASKS = ['preference_extraction', 'knowledge_retrieval', 'conflict_resolution',
                 'precise_forgetting', 'end_to_end_session', 'tool_result']


def load_pool(processed_dir):
    pool = {}
    for path in sorted(glob.glob(os.path.join(processed_dir, '*.jsonl'))):
        fname = os.path.basename(path)
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                sid = obj.get('sample_id')
                task_type = obj.get('task_type')
                if not sid or not task_type:
                    continue
                pool.setdefault(task_type, []).append({
                    'sample_id': sid,
                    'task_type': task_type,
                    'source_file': fname,
                    'source': obj.get('source'),
                    'template_family': obj.get('template_family'),
                })
    return pool


def balanced_allocate(total, limits):
    keys = [k for k in limits if limits[k] > 0]
    if not keys:
        return {}
    # balanced (even) allocation so every gold task gets enough items for
    # per-task layered Kappa; capped by pool size, surplus redistributed.
    order = sorted(keys, key=lambda k: limits[k], reverse=True)
    alloc = {k: total // len(keys) for k in keys}
    rem = total - sum(alloc.values())
    i = 0
    while rem > 0 and i < 10000:
        k = order[i % len(order)]
        if alloc[k] < limits[k]:
            alloc[k] += 1
            rem -= 1
        i += 1
    surplus = 0
    for k in keys:
        if alloc[k] > limits[k]:
            surplus += alloc[k] - limits[k]
            alloc[k] = limits[k]
    i = 0
    while surplus > 0 and i < 10000:
        k = order[i % len(order)]
        if alloc[k] < limits[k]:
            alloc[k] += 1
            surplus -= 1
        i += 1
    return {k: v for k, v in alloc.items() if v > 0}


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap = argparse.ArgumentParser(description='Stage 8 trial set sampler (B side)')
    ap.add_argument('--processed', default=os.path.join(repo_root, 'data', 'processed'))
    ap.add_argument('--extra', action='append', default=[], help='extra candidate JSONL file(s) (e.g. A tool_result candidates)')
    ap.add_argument('--total', type=int, default=40, help='total items when --per-task not given')
    ap.add_argument('--per-task', default='', help='e.g. pref=8,retr=10,conf=7,forg=6,e2e=5,tool=4')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out', default=os.path.join(repo_root, 'data', 'interim', 'stage8_trial_set.jsonl'))
    args = ap.parse_args()

    pool = load_pool(args.processed)
    for extra_path in args.extra:
        with open(extra_path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                sid = obj.get('sample_id')
                task_type = obj.get('task_type')
                if not sid or not task_type:
                    continue
                pool.setdefault(task_type, []).append({
                    'sample_id': sid,
                    'task_type': task_type,
                    'source_file': os.path.basename(extra_path),
                    'source': obj.get('source'),
                    'template_family': obj.get('template_family'),
                })

    avail = {t: len(items) for t, items in pool.items() if t in NON_AUX_TASKS}
    empty_tasks = [t for t in NON_AUX_TASKS if avail.get(t, 0) == 0]

    if args.per_task:
        wanted = {}
        for part in args.per_task.split(','):
            part = part.strip()
            if not part or '=' not in part:
                continue
            key, val = part.split('=')
            task = SHORT_TO_TASK.get(key.strip(), key.strip())
            wanted[task] = int(val)
    else:
        wanted = balanced_allocate(args.total, {k: avail.get(k, 0) for k in avail})
        # give leftovers to the largest pool if wanted sum < total
        diff = args.total - sum(wanted.values())
        if diff > 0 and avail:
            biggest = max(avail, key=lambda k: avail[k])
            wanted[biggest] = wanted.get(biggest, 0) + diff

    if not wanted:
        print('ERROR: no allocatable gold task pool found', file=sys.stderr)
        sys.exit(2)

    rng = random.Random(args.seed)
    chosen = []
    summary = Counter()
    for task_type, count in sorted(wanted.items()):
        items = pool.get(task_type, [])
        cap = min(count, len(items))
        if cap < count:
            print('WARN: %s pool=%d < requested=%d, capped to %d' % (task_type, len(items), count, cap))
        picked = rng.sample(items, cap) if cap else []
        for it in picked:
            chosen.append(it)
            summary[task_type] += 1
    chosen.sort(key=lambda it: (it['task_type'], it['sample_id']))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fh:
        for it in chosen:
            fh.write(json.dumps(it, ensure_ascii=False) + '\n')

    print('========== Stage 8 trial set sampler (seed=%d) ==========' % args.seed)
    print('Total chosen: %d' % len(chosen))
    for task_type in sorted(summary):
        print('  %-28s %d' % (task_type, summary[task_type]))
    print('Empty (no pool, add via --extra/--per-task): %s' % ', '.join(empty_tasks) if empty_tasks else 'None')
    print('written: %s' % args.out)


if __name__ == '__main__':
    main()
