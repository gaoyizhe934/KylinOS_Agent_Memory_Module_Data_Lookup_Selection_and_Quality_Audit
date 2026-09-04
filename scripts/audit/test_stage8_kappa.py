#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit smoke tests for stage8_kappa.py math (Cohen's Kappa)."""
import os
import subprocess
import sys
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage8_kappa as k


def close(a, b, eps=1e-9):
    return abs(a - b) < eps


def test_known_case():
    # A: X X X X X X Y Y Y Y ; B: X X X X X Y Y Y Y Y
    pairs = [('X', 'X')] * 5 + [('X', 'Y')] + [('Y', 'Y')] * 4
    kappa, p_o, p_e, n = k.cohen_kappa(pairs)
    assert n == 10
    assert close(p_o, 0.9), p_o
    assert close(p_e, 0.5), p_e
    assert close(kappa, 0.8), kappa
    print('known-case kappa=%.4f OK' % kappa)


def test_perfect():
    pairs = [('cat%d' % (i % 3), 'cat%d' % (i % 3)) for i in range(30)]
    kappa, p_o, p_e, n = k.cohen_kappa(pairs)
    assert n == 30 and close(p_o, 1.0) and close(kappa, 1.0)
    print('perfect kappa=%.4f OK' % kappa)


def test_all_same():
    pairs = [('X', 'X')] * 12
    kappa, p_o, p_e, n = k.cohen_kappa(pairs)
    assert close(kappa, 1.0), kappa
    print('all-same kappa=%.4f OK' % kappa)


def test_disjoint():
    pairs = [('X', 'Y')] * 8
    kappa, p_o, p_e, n = k.cohen_kappa(pairs)
    assert close(p_o, 0.0) and close(kappa, 0.0), (p_o, kappa)
    print('disjoint kappa=%.4f OK (chance-level, p_e=0)' % kappa)


def test_norm_list_order_independent():
    assert k.norm_value(['a', 'b']) == k.norm_value(['b', 'a'])
    assert k.norm_value(True) == k.norm_value(True)
    assert k.norm_value(1) != k.norm_value('1')
    print('norm list-order-independent OK')


def test_kma_preset():
    tasks = ['preference_extraction', 'knowledge_retrieval', 'conflict_resolution', 'precise_forgetting', 'tool_result', 'end_to_end_session']
    assert hasattr(k, 'KMA_FIELD_SETS')
    for task in tasks:
        assert task in k.KMA_FIELD_SETS, task
    reg = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'registry', 'kappa_agreement_fields.json')
    with open(reg, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    single = data.get('kappa_agreement_fields', {})
    for task in tasks:
        assert task in single, 'registry kappa_agreement_fields missing ' + task
        assert single[task] == k.KMA_FIELD_SETS[task], 'registry vs module drift: ' + task
    print('kma preset present OK (registry single source in sync)')


def test_cli_end_to_end():
    tmp = tempfile.mkdtemp(prefix='stage8_kappa_test_')
    a_path = os.path.join(tmp, 'labels_A_trial.jsonl')
    b_path = os.path.join(tmp, 'labels_B_trial.jsonl')
    gold_a = {'preference_type': 'output_style', 'scope': 'global', 'should_store': True, 'operation': 'create'}
    gold_b = {'preference_type': 'output_style', 'scope': 'global', 'should_store': True, 'operation': 'create'}
    # A: operation create x6 then update x4 ; B: create x5 then update x5
    # overlap: 1-5 agree create, 6 disagree (A create / B update), 7-10 agree update -> kappa 0.8
    with open(a_path, 'w', encoding='utf-8') as fh:
        for i in range(1, 11):
            ga = dict(gold_a)
            ga['operation'] = 'create' if i <= 6 else 'update'
            fh.write(json.dumps({'sample_id': 'pref_%06d' % i, 'task_type': 'preference_extraction',
                                 'gold': ga, 'evidence': []}, ensure_ascii=False) + '\n')
    with open(b_path, 'w', encoding='utf-8') as fh:
        for i in range(1, 11):
            gb = dict(gold_b)
            gb['operation'] = 'create' if i <= 5 else 'update'
            fh.write(json.dumps({'sample_id': 'pref_%06d' % i, 'task_type': 'preference_extraction',
                                 'gold': gb, 'evidence': []}, ensure_ascii=False) + '\n')
    out_dir = os.path.join(tmp, 'out')
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stage8_kappa.py')
    proc = subprocess.run([sys.executable, script, '--a', a_path, '--b', b_path,
                           '--out-dir', out_dir, '--tag', 'smoke', '--format', 'legacy'], capture_output=True, text=True, encoding='utf-8')
    assert proc.returncode == 0, proc.stderr
    report = os.path.join(out_dir, 'stage8_kappa_report_smoke.json')
    assert os.path.exists(report)
    with open(report, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    assert data['overall']['n'] == 10
    assert close(data['overall']['kappa'], 0.8), data['overall']['kappa']
    assert data['passed'] is True
    print('cli end-to-end kappa=%.4f OK' % data['overall']['kappa'])


if __name__ == '__main__':
    test_known_case()
    test_perfect()
    test_all_same()
    test_disjoint()
    test_norm_list_order_independent()
    test_kma_preset()
    test_cli_end_to_end()
    print('ALL TESTS PASSED')
