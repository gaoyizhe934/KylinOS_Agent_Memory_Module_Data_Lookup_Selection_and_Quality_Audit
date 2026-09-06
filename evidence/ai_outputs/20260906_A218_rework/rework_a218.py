# -*- coding: utf-8 -*-
"""Data-A A218 rework（本地 carrier，未开 PR / 未推送）
目标：给 A218(98/64/56) OS-authored factory candidates 补 top-level `template_family`，
取值 = design_metadata.scenario_family（generation-template family，见 mapping contract）。
性质：仍 candidate_only；不写 human_decision/final_label/gold；canonical 序列化，可复现。
Data-R #51 P1 提示：template_family 须为真实 generation/rework template family，非机械复制 ——
映射依据见 reports/v4.1_D1_A_A218_template_family_mapping_contract_draft_20260906.{json,md}（DRAFT，供 R 复核）。
"""
import glob, hashlib, json, os

ROOT = r'C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37'
SRC = os.path.join(ROOT, 'data', 'interim', 'd1_candidates_A_20260906')
DST = os.path.join(ROOT, 'data', 'interim', 'd1_candidates_A_20260906_rw')
os.makedirs(DST, exist_ok=True)
CANON = dict(ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def canon(o):
    return json.dumps(o, **CANON)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def nl(b):
    return b.replace(b'\r\n', b'\n').replace(b'\r', b'\n')

rows_in = 0
rows_out = 0
input_parts = []
outs = []
for p in sorted(glob.glob(os.path.join(SRC, '*.jsonl'))):
    fn = os.path.basename(p)
    src_text = nl(open(p, 'rb').read()).decode('utf-8')
    input_parts.append('%s::%s' % (fn, sha(src_text.encode('utf-8'))))
    body = []
    for line in src_text.splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rows_in += 1
        if 'template_family' in r:
            raise SystemExit('already has template_family: %s' % r['sample_id'])
        fam = r['design_metadata']['scenario_family']
        if not fam:
            raise SystemExit('no scenario_family: %s' % r['sample_id'])
        r['template_family'] = fam
        body.append(canon(r))
    text = '\n'.join(body) + '\n'
    out_p = os.path.join(DST, fn)
    open(out_p, 'w', encoding='utf-8').write(text)
    rows_out += len(body)
    outs.append({'file': 'data/interim/d1_candidates_A_20260906_rw/' + fn, 'count': len(body), 'sha256_lf': sha(text.encode('utf-8'))})

m = {
  'schema': 'v4.1_A_A218_rework_manifest', 'date': '2026-09-06', 'role': 'Data-A',
  'base_commit': '535ebad3db47e87bbb30f26b86b3193803d81a1b',
  'mapping': 'template_family := design_metadata.scenario_family (generation-template family; DRAFT_FOR_R_REVIEW, not pre-approved)',
  'rows_in': rows_in, 'rows_out': rows_out,
  'input_set_sha256': sha('\n'.join(sorted(input_parts)).encode('utf-8')),
  'output_files': outs,
  'note': 'candidate_only；未写 human_decision/final_label/gold；canonical 序列化；待 R 复核 mapping 后由 A 独立 rework PR 正式提交'
}
open(os.path.join(DST, 'A_A218_rework_manifest_20260906.json'), 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=1))
print('rows_in', rows_in, 'rows_out', rows_out)
for o in outs:
    print(o['file'], o['count'], o['sha256_lf'][:16])
