#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage8 v2 canonical labels skeleton generator (B, P1-4 readiness).
# Writes canonical empty-skeleton labels to --out (any caller path). Does NOT
# touch data/processed or formal labels; FROZEN 前仅就绪用。
import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SAMPLES = os.path.join(REPO, 'data', 'interim', 'stage8_trial_set.jsonl')

CANONICAL = {
    'preference_extraction': {'expression_type': '', 'preference_scope': '', 'preference_key': '',
                              'preference_value': '', 'confidence_score': None, 'should_persist': None,
                              'is_temporary': None, 'memory_status': '', 'version': 1,
                              'previous_version_id': None, 'evidence_event_ids': []},
    'knowledge_retrieval': {'knowledge_type': '', 'knowledge_id': '', 'memory_status': '',
                            'superseded_by_id': None, 'retrieval_ref': None, 'evaluation_role': '',
                            'rationale': ''},
    'conflict_resolution': {'conflict_type': '', 'resolution_status': '', 'left_knowledge_id': '',
                            'right_knowledge_id': '', 'involved_knowledge_ids': [], 'resolution_strategy': ''},
    'precise_forgetting': {'forget_mode': '', 'target_type': '', 'target_selector': '', 'status': '',
                           'is_cascade': None, 'has_vector_cleanup': None, 'requires_confirmation': None,
                           'resolved_target_ids': [], 'affected_count': None},
    'tool_result': {'source_business_status': '', 'tool_call_id': '', 'content_summary': ''},
    'end_to_end_session': {'expected_memory': {}, 'expected_response': ''},
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', default=DEFAULT_SAMPLES, help='JSONL of sample_id/task_type')
    ap.add_argument('--out', required=True, help='output skeleton JSONL path')
    args = ap.parse_args()
    rows = []
    with open(args.samples, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            tid = o.get('sample_id')
            task = o.get('task_type')
            if not tid or not task:
                continue
            gold = json.loads(json.dumps(CANONICAL.get(task, {})))
            rows.append({'sample_id': tid, 'task_type': task, 'gold': gold, 'evidence': []})
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + chr(10))
    counts = {}
    for r in rows:
        counts[r['task_type']] = counts.get(r['task_type'], 0) + 1
    print('skeleton written: %s' % args.out)
    print('records: %d | per task: %s' % (len(rows), counts))

if __name__ == '__main__':
    main()
