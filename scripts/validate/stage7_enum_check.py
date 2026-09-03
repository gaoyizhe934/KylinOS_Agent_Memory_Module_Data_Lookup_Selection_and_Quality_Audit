#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enum dictionary consistency check for stage 8 gold candidates (B side).

Matches the command referenced by annotation manual v1.3 section 11:
  python scripts/validate/stage7_enum_check.py --gold <gold_draft> --enum data/processed/enum_dictionary.json

Checks: sample_id prefix vs task_type, top-level enums (task_type / source /
template_family / review_status), and gold-level enum fields for which the
enum dictionary provides a vocabulary. Missing dictionary keys are reported as
warnings (dictionary gap), not errors.
"""
import argparse
import glob
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PREFIX_BY_TASK = {
    'preference_extraction': 'pref_',
    'knowledge_retrieval': 'retr_',
    'conflict_resolution': 'conf_',
    'precise_forgetting': 'forg_',
    'tool_result': 'tool_',
    'end_to_end_session': 'e2e_',
    'auxiliary_dialogue': 'aux_',
}
# gold-level enum fields that the manual defines (checked only when dict provides them)
GOLD_ENUM_FIELDS = ['preference_type', 'conflict_type', 'scope', 'operation',
                    'review_status']
REQUIRED_GOLD_BY_TASK = {
    'preference_extraction': ['preference_type', 'scope', 'should_store', 'operation'],
    'knowledge_retrieval': ['relevant_ids', 'hard_negative_ids', 'expected_answer_points'],
    'conflict_resolution': ['conflict_type', 'winner', 'resolution_reason'],
    'precise_forgetting': ['target_ids', 'must_keep', 'checkpoints', 'expected_residual_count'],
    'tool_result': ['status', 'persist_policy'],
    'end_to_end_session': ['expected_memory', 'expected_response'],
}
ALLOW_EXTRA_TASK_TYPES = {'tool_result'}


def iter_records(gold_patterns):
    for pat in gold_patterns:
        for path in sorted(glob.glob(pat)):
            with open(path, 'r', encoding='utf-8') as fh:
                for lineno, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError as exc:
                        print('ERROR: %s:%d invalid JSON: %s' % (path, lineno, exc))
                        sys.exit(2)
                    yield path, lineno, obj


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap = argparse.ArgumentParser(description='Stage 8 enum dictionary check (B side)')
    ap.add_argument('--gold', nargs='+', required=True, help='gold JSONL path(s)/glob(s)')
    ap.add_argument('--enum', default=os.path.join(repo_root, 'data', 'processed', 'enum_dictionary.json'))
    args = ap.parse_args()

    with open(args.enum, 'r', encoding='utf-8') as fh:
        enum_data = json.load(fh)
    enum = enum_data.get('enum', {})

    errors = []
    warnings = []
    rec_count = 0
    for path, lineno, obj in iter_records(args.gold):
        rec_count += 1
        sid = obj.get('sample_id', '')
        task_type = obj.get('task_type', '')
        gold = obj.get('gold') if isinstance(obj.get('gold'), dict) else {}
        source = obj.get('source', '')
        template_family = obj.get('template_family', '')
        review_status = obj.get('review_status', '')

        if not task_type:
            errors.append('%s:%d 缺 task_type' % (path, lineno))
            continue
        known = set(enum.get('task_type', [])) | ALLOW_EXTRA_TASK_TYPES
        if task_type not in known:
            errors.append('%s:%d task_type 越出词表: %s' % (path, lineno, task_type))

        if sid:
            expect_prefix = PREFIX_BY_TASK.get(task_type)
            if expect_prefix and not sid.startswith(expect_prefix):
                errors.append('%s:%d sample_id 前缀与 task_type 不符: %s vs %s' % (path, lineno, sid, task_type))

        if source and 'source' in enum and source not in set(enum['source']) | {'runtime_replay'}:
            errors.append('%s:%d source 越出词表: %s' % (path, lineno, source))

        if template_family and 'template_family' in enum and template_family not in set(enum['template_family']):
            errors.append('%s:%d template_family 越出词表: %s' % (path, lineno, template_family))

        if review_status and 'review_status' in enum and review_status not in set(enum['review_status']):
            errors.append('%s:%d review_status 越出词表: %s' % (path, lineno, review_status))

        req = REQUIRED_GOLD_BY_TASK.get(task_type, [])
        for field in req:
            if field not in gold:
                errors.append('%s:%d %s 缺 gold 字段 %s' % (path, lineno, sid, field))

        if task_type == 'knowledge_retrieval':
            hn = gold.get('hard_negative_ids')
            empty = hn is None or hn == [] or (isinstance(hn, list) and len(hn) == 0)
            if empty and source != 'public_derived':
                errors.append('%s:%d %s hard_negative_ids 为空（P1-1 硬性，每查询>=1）' % (path, lineno, sid))

        for field in GOLD_ENUM_FIELDS:
            if field in gold:
                vocab = enum.get(field)
                if vocab is not None and gold[field] not in set(vocab):
                    errors.append('%s:%d %s gold.%s 越出词表: %s' % (path, lineno, sid, field, gold[field]))

    for key in ['status', 'persist_policy', 'checkpoints', 'should_store', 'confidence', 'winner', 'expected_residual_count']:
        if key not in enum:
            warnings.append('enum 字典缺键 %s（建议随 8.2 候选草稿补充词表）' % key)

    print('========== Stage 8 enum dictionary check ==========')
    print('records checked: %d' % rec_count)
    print('errors: %d | warnings: %d' % (len(errors), len(warnings)))
    for w in warnings:
        print('WARN: ' + w)
    for e in errors:
        print('ERROR: ' + e)
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
