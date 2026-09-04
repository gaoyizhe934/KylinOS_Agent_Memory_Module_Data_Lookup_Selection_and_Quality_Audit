#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage8 v2 canonical label pre-submission QA (B, P1-5 readiness).
# Validates filled labels_A/B v2 files: coverage, required canonical gold main
# fields non-empty, evidence non-empty. Non-destructive; no data written.
import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED = {
    'preference_extraction': ['expression_type', 'preference_scope', 'preference_key', 'preference_value', 'confidence_score', 'should_persist', 'is_temporary', 'memory_status', 'version', 'evidence_event_ids'],
    'knowledge_retrieval': ['knowledge_type', 'knowledge_id', 'memory_status', 'evaluation_role'],
    'conflict_resolution': ['conflict_type', 'resolution_status', 'left_knowledge_id', 'right_knowledge_id'],
    'precise_forgetting': ['forget_mode', 'target_type', 'target_selector', 'status'],
    'tool_result': ['source_business_status', 'tool_call_id'],
    'end_to_end_session': ['expected_response'],
}

def is_empty(v):
    if v is None:
        return True
    if isinstance(v, bool):
        return False
    if isinstance(v, str):
        return v.strip() == ''
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--labels', required=True, help='filled v2 labels JSONL')
    ap.add_argument('--samples', default='', help='optional expected sample_id/task_type JSONL')
    args = ap.parse_args()
    labels = []
    with open(args.labels, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                labels.append(json.loads(line))
    errors = []
    warnings = []
    for r in labels:
        sid = r.get('sample_id', '?')
        task = r.get('task_type', '')
        gold = r.get('gold') if isinstance(r.get('gold'), dict) else {}
        if not task or not gold:
            errors.append(sid + ': 缺 task_type/gold')
            continue
        for f in REQUIRED.get(task, []):
            if is_empty(gold.get(f)):
                errors.append(sid + ': gold.' + f + ' 为空')
        if task == 'preference_extraction' and not isinstance(gold.get('version'), int):
            errors.append(sid + ': gold.version 需 integer>=1')
        if task == 'conflict_resolution' and gold.get('left_knowledge_id') == gold.get('right_knowledge_id') and not is_empty(gold.get('left_knowledge_id')):
            errors.append(sid + ': left/right_knowledge_id 不得相同')
        ev = r.get('evidence')
        if not isinstance(ev, list) or len(ev) == 0:
            errors.append(sid + ': evidence 至少 1 条')
        else:
            for i, e in enumerate(ev):
                if not isinstance(e, dict) or is_empty(e.get('source_event_id')) or is_empty(e.get('span')):
                    errors.append(sid + ': evidence[' + str(i) + '] 缺 source_event_id/span')
    if args.samples and os.path.exists(args.samples):
        expect = {}
        with open(args.samples, 'r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if line:
                    o = json.loads(line)
                    expect[o.get('sample_id')] = o.get('task_type')
        have = {r.get('sample_id') for r in labels}
        for sid in sorted(set(expect) - have):
            errors.append('缺失样本: ' + sid)
        for sid in sorted(have - set(expect)):
            warnings.append('多余样本: ' + sid)
    counts = {}
    for r in labels:
        counts[r.get('task_type', '?')] = counts.get(r.get('task_type', '?'), 0) + 1
    print('========== Stage8 v2 label QA ==========')
    print('labels: %d | per task: %s' % (len(labels), counts))
    print('errors: %d | warnings: %d' % (len(errors), len(warnings)))
    for w in warnings:
        print('WARN: ' + w)
    for e in errors[:60]:
        print('ERROR: ' + e)
    if len(errors) > 60:
        print('... (%d more)' % (len(errors) - 60))
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
