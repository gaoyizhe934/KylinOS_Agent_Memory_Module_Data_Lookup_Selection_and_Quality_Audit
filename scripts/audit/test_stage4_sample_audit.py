# -*- coding: utf-8 -*-
"""阶段4: 审计脚本单元测试（PR #3 审查意见修复验证）

夹具说明: 全部测试记录为代码内构造的合成数据, 仅用于验证脚本逻辑,
不属于数据包任何层级, 不进入候选/interim/processed/gold（R3 红线针对数据包,
单元测试夹具不是数据样本）。

覆盖的审查意见:
- P1-2 字段类型校验: 已配置字段类型错误记 type_mismatch; 合法记录零误报;
  bool 不因 Python 的 bool<int 继承而漏报; 缺失/空值不算类型错误
- P1-3 人工复核清单: 总量 >= min(6.3 最低抽样量, 唯一ID数); 每个类别
  至少 2 条（类别记录不足 2 条则全取）; 覆盖全部类别; 全部异常 ID 入选;
  seed 固定可复现
- Gate 3 门禁: 未获 Reviewer 批准返回 False; registry gate3_status 列读取;
  50~100 条样本量范围校验

运行: python scripts/audit/test_stage4_sample_audit.py
退出码: 全部通过 0, 任一失败 1; 本测试不读 data/raw, 不写任何产物文件
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage4_sample_audit as audit  # noqa: E402

FAILED = []


def check(name, cond, detail=''):
    status = 'PASS' if cond else 'FAIL'
    suffix = ('  -- ' + detail) if (detail and not cond) else ''
    print('[%s] %s%s' % (status, name, suffix))
    if not cond:
        FAILED.append(name)


def run_audit(ds_id, rows):
    tmp = tempfile.mkdtemp(prefix='stage4_test_')
    try:
        ds_dir = os.path.join(tmp, ds_id)
        os.makedirs(ds_dir)
        with open(os.path.join(ds_dir, 'sample.jsonl'), 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        return audit.audit_dataset(ds_id, '', ds_dir=ds_dir)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def type_anoms(anomalies):
    return [a for a in anomalies if a['anomaly_type'] == 'type_mismatch']


def test_configured_type_rules():
    """longmemeval_v2_2026 显式配置: id/answer/question/question_type/eval_function 均 str."""
    rows = [
        {'id': 'q1', 'answer': 'a', 'question': 'q', 'question_type': 't', 'eval_function': 'f'},
        {'id': 123, 'answer': 'a', 'question': 'q', 'question_type': 't', 'eval_function': 'f'},
        {'id': 'q3', 'answer': ['a', 'b'], 'question': 'q', 'question_type': 't', 'eval_function': 'f'},
        {'id': 'q4', 'answer': 'a', 'question': 'q', 'question_type': 7, 'eval_function': 'f'},
        {'id': 'q5', 'answer': 'a', 'question': 'q', 'question_type': 't', 'eval_function': ['x']},
        {'id': True, 'answer': 'a', 'question': 'q', 'question_type': 't', 'eval_function': 'f'},
    ]
    result, anomalies = run_audit('longmemeval_v2_2026', rows)
    ta = type_anoms(anomalies)
    check('P1-2 显式规则: 5 条类型错误全部命中', len(ta) == 5,
          '期望 5, 实际 %d: %s' % (len(ta), [(a['record_id'], a['detail'][:40]) for a in ta]))
    fields = {a['detail'].split()[1] for a in ta}
    check('P1-2 显式规则: 覆盖 id/answer/question_type/eval_function 四个字段',
          fields == {'id', 'answer', 'question_type', 'eval_function'}, str(fields))

    ok = [{'id': 'r%d' % i, 'answer': 'a', 'question': 'q', 'question_type': 't',
           'eval_function': 'f'} for i in range(5)]
    _, anomalies_ok = run_audit('longmemeval_v2_2026', ok)
    check('P1-2 合法记录零 type_mismatch 误报', len(type_anoms(anomalies_ok)) == 0)


def test_generic_type_rules():
    """自动探测配置: sample_id 允许 str|int, 其余字段按泛化规则."""
    rows = [
        {'sample_id': 'g1', 'answer': 'a', 'task_type': 't', 'body': 'text'},
        {'sample_id': 7, 'answer': 'a', 'task_type': 't', 'body': 'text'},
        {'sample_id': True, 'answer': 'a', 'task_type': 't', 'body': 'text'},
        {'sample_id': 'g4', 'answer': {'k': 'v'}, 'task_type': 't', 'body': 'text'},
        {'sample_id': 'g5', 'answer': 'a', 'task_type': 't', 'body': 123},
    ]
    _, anomalies = run_audit('unit_test_generic', rows)
    ta = type_anoms(anomalies)
    check('P1-2 泛化规则: int ID 合法不报, bool ID / dict 标签 / int 文本报错',
          len(ta) == 3, '期望 3, 实际 %d: %s' % (len(ta), [a['detail'][:50] for a in ta]))
    check('P1-2 泛化规则: 缺失字段不触发 type_mismatch（如无 category 数据集）',
          all('sample_id' in a['detail'] or 'answer' in a['detail'] or 'body' in a['detail'] for a in ta))


def test_manual_sampling_quantity():
    """60 条 / 3 类: 最低抽样量 50, 清单总量应 >= 50 且每类 >= 2."""
    rows = []
    for i in range(60):
        rows.append({'sample_id': 's%03d' % i, 'answer': 'a',
                     'task_type': 'cat%d' % (i % 3), 'body': 'text %d' % i})
    result, anomalies = run_audit('unit_test_sampling', rows)
    check('P1-3 无异常数据: 清单总量 >= 最低抽样量 50',
          result['manual_review_total'] >= 50,
          '总量 %d' % result['manual_review_total'])
    cats = result.get('manual_review_categories', {})
    check('P1-3 三个类别全部覆盖且每类 >= 2 条',
          len(cats) == 3 and all(v >= 2 for v in cats.values()), str(cats))
    check('P1-3 清单 ID 唯一', len(set(result['manual_review_ids'])) == result['manual_review_total'])


def test_manual_sampling_topup_large():
    """600 条 / 3 类: 最低抽样量 100, 总量应 >= 100."""
    rows = []
    for i in range(600):
        rows.append({'sample_id': 'b%04d' % i, 'answer': 'a',
                     'task_type': 'cat%d' % (i % 3), 'body': 'text %d' % i})
    result, _ = run_audit('unit_test_topup', rows)
    check('P1-3 大数据集: 清单总量 >= 最低抽样量 100',
          result['manual_review_total'] >= 100,
          '总量 %d' % result['manual_review_total'])
    cats = result.get('manual_review_categories', {})
    check('P1-3 大数据集: 三类全覆盖', len(cats) == 3, str(cats))


def test_manual_sampling_small_dataset():
    """10 条: 抽样量取 min(50, 唯一ID)=10, 清单应含全部 10 个 ID."""
    rows = [{'sample_id': 'm%d' % i, 'answer': 'a', 'task_type': 't', 'body': 'x'}
            for i in range(10)]
    result, _ = run_audit('unit_test_small', rows)
    check('P1-3 小数据集: 唯一ID不足最低抽样量时全量入选',
          result['manual_review_total'] == 10, '总量 %d' % result['manual_review_total'])


def test_flagged_all_included_and_deterministic():
    """异常记录全部入选; 两次运行清单一致（seed 可复现）."""
    rows = [{'sample_id': 'd%d' % i, 'answer': 'a', 'task_type': 'cat%d' % (i % 2),
             'body': 'x'} for i in range(80)]
    rows[5]['sample_id'] = rows[6]['sample_id']  # 制造重复 ID
    rows[10]['body'] = 123                       # 制造类型错误
    result, anomalies = run_audit('unit_test_flagged', rows)
    flagged_ids = {a['record_id'] for a in anomalies if a['record_id']}
    check('P1-3 全部异常记录 ID 入选清单',
          flagged_ids <= set(result['manual_review_ids']),
          '缺失: %s' % (flagged_ids - set(result['manual_review_ids'])))
    result2, _ = run_audit('unit_test_flagged', rows)
    check('P1-3 seed=42 两次运行清单完全一致',
          result['manual_review_ids'] == result2['manual_review_ids'])
    check('P1-3 含异常数据集总量仍 >= 最低抽样量 50',
          result['manual_review_total'] >= 50, '总量 %d' % result['manual_review_total'])


def test_gate3_enforcement():
    """P1-2 Gate 3 门禁: 批准状态判定 / 候选状态读取 / 50~100 样本量范围."""
    tmp = tempfile.mkdtemp(prefix='stage4_gate3_')
    try:
        not_approved = os.path.join(tmp, 'gate_not.md')
        with open(not_approved, 'w', encoding='utf-8') as f:
            f.write('| Gate 3 | 阶段 3 | Reviewer 明确标记允许试用/需确认/淘汰 | ⏳ 下一阶段 |\n')
        ok, _ = audit.gate3_approved(not_approved)
        check('P1-2 Gate3 未批准 -> 返回 False', ok is False)

        approved = os.path.join(tmp, 'gate_ok.md')
        with open(approved, 'w', encoding='utf-8') as f:
            f.write('| Gate 3 | 阶段 3 | Reviewer 明确标记允许试用/需确认/淘汰 | ✅ 通过 |\n')
        ok, _ = audit.gate3_approved(approved)
        check('P1-2 Gate3 已批准 -> 返回 True', ok is True)

        reg = os.path.join(tmp, 'registry.csv')
        with open(reg, 'w', encoding='utf-8-sig', newline='') as f:
            f.write('dataset_id,gate3_status\n')
            f.write('a,允许试用\n')
            f.write('b,需确认\n')
            f.write('c,淘汰\n')
        m = audit.load_registry_gate3_status(reg)
        check('P1-2 registry gate3_status 映射正确',
              m == {'a': '允许试用', 'b': '需确认', 'c': '淘汰'}, str(m))

        reg2 = os.path.join(tmp, 'registry_nocol.csv')
        with open(reg2, 'w', encoding='utf-8-sig', newline='') as f:
            f.write('dataset_id,conclusion\n')
            f.write('a,核心候选\n')
        check('P1-2 registry 无 gate3_status 列 -> 空 dict',
              audit.load_registry_gate3_status(reg2) == {})

        check('P1-2 范围: 49 拒绝', audit.in_formal_sample_range(49) is False)
        check('P1-2 范围: 50 允许', audit.in_formal_sample_range(50) is True)
        check('P1-2 范围: 100 允许', audit.in_formal_sample_range(100) is True)
        check('P1-2 范围: 101 拒绝', audit.in_formal_sample_range(101) is False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    print('=' * 60)
    print('阶段4 审计脚本单元测试（PR #3 P1-2 / P1-3 修复验证）')
    print('=' * 60)
    test_configured_type_rules()
    test_generic_type_rules()
    test_manual_sampling_quantity()
    test_manual_sampling_topup_large()
    test_manual_sampling_small_dataset()
    test_flagged_all_included_and_deterministic()
    test_gate3_enforcement()
    print('-' * 60)
    if FAILED:
        print('失败 %d 项: %s' % (len(FAILED), ', '.join(FAILED)))
        return 1
    print('全部通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
