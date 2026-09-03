#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 8 B-side Cohen's Kappa calculator.

Implements annotation manual v1.3 section 8:
- overall + per-task layered Cohen's Kappa
- per-task compared field sets (gold main fields)
- A/B label file convention: JSONL with sample_id / task_type / gold / evidence
  (A: labels_A_trial.jsonl, B: labels_B_trial.jsonl)

Usage:
  python scripts/audit/stage8_kappa.py --a labels_A_trial.jsonl --b labels_B_trial.jsonl
"""
import argparse
import csv
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Manual v1.3 section 8: gold main field set used to decide "agreement" per task.
TASK_FIELD_SETS = {
    'preference_extraction': ['preference_type', 'scope', 'should_store', 'operation'],
    'knowledge_retrieval': ['relevant_ids', 'hard_negative_ids'],
    'conflict_resolution': ['conflict_type', 'winner'],
    'precise_forgetting': ['expected_deleted', 'must_keep'],
    'tool_result': ['status', 'persist_policy'],
    'end_to_end_session': ['expected_response'],
}

# KMA canonical gold 主字段集（草案，依据 reports/stage8_kma_gold_annotation_draft_A.md；
# KMA=FREEZE_PROPOSAL，待 FROZEN/labels 定稿；可用 --fields-json 覆盖）
KMA_FIELD_SETS = {
    'preference_extraction': ['expression_type', 'preference_scope', 'should_persist', 'is_temporary', 'memory_status'],
    'knowledge_retrieval': ['evaluation_role', 'knowledge_type', 'memory_status'],
    'conflict_resolution': ['conflict_type', 'resolution_status'],
    'precise_forgetting': ['forget_mode', 'target_type', 'status'],
    'tool_result': ['source_business_status'],
    'end_to_end_session': ['expected_response'],
}


def load_labels(path):
    records = {}
    with open(path, 'r', encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                print('ERROR: invalid JSON in %s line %d: %s' % (path, lineno, exc), file=sys.stderr)
                sys.exit(2)
            sid = obj.get('sample_id')
            if not sid:
                print('ERROR: missing sample_id at %s line %d' % (path, lineno), file=sys.stderr)
                sys.exit(2)
            if 'gold' not in obj:
                print('ERROR: missing gold at %s line %d' % (path, lineno), file=sys.stderr)
                sys.exit(2)
            records[sid] = obj
    return records


def norm_value(v):
    if isinstance(v, bool):
        return ('bool', str(v).lower())
    if isinstance(v, (int, float)):
        return ('num', v)
    if isinstance(v, str):
        return ('str', v.strip())
    if isinstance(v, list):
        return tuple(sorted((norm_value(x) for x in v), key=repr))
    if isinstance(v, dict):
        return tuple(sorted(((str(k), norm_value(x)) for k, x in v.items()), key=repr))
    if v is None:
        return ('none',)
    return ('other', repr(v))


def signature(gold, fields):
    return tuple(norm_value(gold.get(f)) for f in fields)


def disagreed_fields(gold_a, gold_b, fields):
    return [f for f in fields if norm_value(gold_a.get(f)) != norm_value(gold_b.get(f))]


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None, None, None, 0
    agreed = sum(1 for a, b in pairs if a == b)
    p_o = agreed / float(n)
    cnt_a = Counter(a for a, _ in pairs)
    cnt_b = Counter(b for _, b in pairs)
    cats = set(cnt_a) | set(cnt_b)
    p_e = sum((cnt_a[c] / float(n)) * (cnt_b[c] / float(n)) for c in cats)
    if p_e == 1.0:
        kappa = 1.0 if p_o == 1.0 else 0.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)
    return kappa, p_o, p_e, n


def summarize(pairs):
    kappa, p_o, p_e, n = cohen_kappa(pairs)
    return {'n': n, 'p_observed': p_o, 'p_expected': p_e, 'kappa': kappa}


def main():
    ap = argparse.ArgumentParser(description='Stage 8 Cohen Kappa (B side)')
    ap.add_argument('--a', required=True, help='A label file (JSONL)')
    ap.add_argument('--b', required=True, help='B label file (JSONL)')
    ap.add_argument('--threshold', type=float, default=0.70, help='overall kappa pass line (default 0.70)')
    ap.add_argument('--out-dir', default='reports', help='output directory for report json + disagreement csv')
    ap.add_argument('--tag', default='trial', help='tag used in output filenames')
    ap.add_argument('--strict', action='store_true', help='exit 1 when overall kappa < threshold')
    ap.add_argument('--format', choices=['legacy', 'kma'], default='legacy', help='field-set preset: legacy (v1.3) or kma (canonical draft)')
    ap.add_argument('--fields-json', default='', help='override task->field-set mapping JSON file')
    args = ap.parse_args()
    if args.fields_json:
        with open(args.fields_json, 'r', encoding='utf-8') as fh:
            field_sets = json.load(fh)
    elif args.format == 'kma':
        field_sets = KMA_FIELD_SETS
    else:
        field_sets = TASK_FIELD_SETS

    recs_a = load_labels(args.a)
    recs_b = load_labels(args.b)
    matched_ids = sorted(set(recs_a) & set(recs_b))

    if not matched_ids:
        print('ERROR: no matched sample_id between %s and %s' % (args.a, args.b), file=sys.stderr)
        sys.exit(2)

    by_task = {}
    overall_pairs = []
    disagreements = []
    for sid in matched_ids:
        ra, rb = recs_a[sid], recs_b[sid]
        task_type = ra.get('task_type') or rb.get('task_type') or 'unknown'
        ga, gb = ra.get('gold', {}), rb.get('gold', {})
        fields = field_sets.get(task_type)
        if fields is None:
            fields = sorted(set(ga) | set(gb))
            task_type = task_type + ' (full-gold fallback)'
        sig_a = signature(ga, fields)
        sig_b = signature(gb, fields)
        overall_pairs.append((sig_a, sig_b))
        by_task.setdefault(task_type, []).append((sig_a, sig_b))
        if sig_a != sig_b:
            disagreements.append({
                'sample_id': sid,
                'task_type': task_type,
                'disagreed_fields': ','.join(disagreed_fields(ga, gb, fields)),
                'gold_a': json.dumps(ga, ensure_ascii=False, sort_keys=True),
                'gold_b': json.dumps(gb, ensure_ascii=False, sort_keys=True),
            })

    overall = summarize(overall_pairs)
    per_task = {}
    for task_type, pairs in sorted(by_task.items()):
        per_task[task_type] = summarize(pairs)

    print('========== Stage 8 Cohen Kappa (tag=%s, format=%s) ==========' % (args.tag, args.format))
    print('A records: %d | B records: %d | matched: %d | only A: %d | only B: %d' % (
        len(recs_a), len(recs_b), len(matched_ids),
        len(set(recs_a) - set(recs_b)), len(set(recs_b) - set(recs_a))))
    print()
    print('%-28s %6s %10s %10s %8s' % ('task', 'n', 'p_obs', 'p_exp', 'kappa'))
    print('%-28s %6d %10.4f %10.4f %8.4f' % ('OVERALL', overall['n'], overall['p_observed'], overall['p_expected'], overall['kappa']))
    for task_type, s in per_task.items():
        print('%-28s %6d %10.4f %10.4f %8.4f' % (task_type[:28], s['n'], s['p_observed'], s['p_expected'], s['kappa']))

    low_tasks = [t for t, s in per_task.items() if s['n'] > 0 and s['kappa'] is not None and s['kappa'] < args.threshold]
    passed = overall['kappa'] is not None and overall['kappa'] >= args.threshold
    print()
    print('Overall Kappa = %.4f (threshold %.2f) -> %s' % (overall['kappa'], args.threshold, 'PASS' if passed else 'FAIL'))
    if low_tasks:
        print('Per-task below threshold (退回该任务批次修订并回溯): %s' % ', '.join(low_tasks))
    print('Disagreements: %d / %d' % (len(disagreements), len(matched_ids)))

    os.makedirs(args.out_dir, exist_ok=True)
    report_path = os.path.join(args.out_dir, 'stage8_kappa_report_%s.json' % args.tag)
    with open(report_path, 'w', encoding='utf-8') as fh:
        json.dump({
            'tag': args.tag,
            'threshold': args.threshold,
            'passed': passed,
            'counts': {'a': len(recs_a), 'b': len(recs_b), 'matched': len(matched_ids),
                       'only_a': len(set(recs_a) - set(recs_b)), 'only_b': len(set(recs_b) - set(recs_a))},
            'overall': overall,
            'per_task': per_task,
            'below_threshold_tasks': low_tasks,
        }, fh, ensure_ascii=False, indent=2)
    print('report written: %s' % report_path)

    csv_path = os.path.join(args.out_dir, 'stage8_disagreement_%s.csv' % args.tag)
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['sample_id', 'task_type', 'disagreed_fields', 'gold_a', 'gold_b'])
        writer.writeheader()
        for row in disagreements:
            writer.writerow(row)
    print('disagreement csv written: %s' % csv_path)

    if args.strict and not passed:
        sys.exit(1)


if __name__ == '__main__':
    main()
