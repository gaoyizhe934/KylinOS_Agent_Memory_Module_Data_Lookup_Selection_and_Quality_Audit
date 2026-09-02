# -*- coding: utf-8 -*-
"""阶段4 A侧: 为允许试用数据集抽取 50~100 条审计样本到 v0_sample_stage4/

依据: 手册6.3 + 阶段4 脚本 (stage4_sample_audit.py) 要求每集 50~100 条新样本审计。
- 只读 data/raw/<ds_id>/v0_sample/ 全量, 抽取后写入 data/raw/<ds_id>/v0_sample_stage4/
- seed=42 保证可复现
- 不修改/删除全量原始文件 (红线: raw 只读)
"""
import json, os, sys, io, hashlib, random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(REPO, 'data', 'raw')
SAMPLE_N = 100
SEED = 42

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def write_jsonl(records, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return sha256(out_path)

def extract(source_path, out_name, pick):
    """从 source 读取记录, 用 pick(records)->list 返回要抽取的条目. 返回 (out_records, n)"""
    return None

# --- 各数据集抽取 ---
report = []

# 1. longmemeval_cleaned: oracle.json (500条 JSON 数组)
src = os.path.join(RAW, 'longmemeval_cleaned_2025', 'v0_sample', 'longmemeval_oracle.json')
out = os.path.join(RAW, 'longmemeval_cleaned_2025', 'v0_sample_stage4', 'longmemeval_oracle_sample.jsonl')
with open(src, encoding='utf-8') as f:
    recs = json.load(f)
rnd = random.Random(SEED)
chosen = rnd.sample(recs, SAMPLE_N)
digest = write_jsonl(chosen, out)
report.append(('longmemeval_cleaned_2025', len(chosen), digest, src, out))

# 2. longmemeval_v2: questions.jsonl (451条)
src = os.path.join(RAW, 'longmemeval_v2_2026', 'v0_sample', 'questions.jsonl')
out = os.path.join(RAW, 'longmemeval_v2_2026', 'v0_sample_stage4', 'questions_sample.jsonl')
recs = [json.loads(l) for l in open(src, encoding='utf-8') if l.strip()]
rnd = random.Random(SEED)
chosen = rnd.sample(recs, SAMPLE_N)
digest = write_jsonl(chosen, out)
report.append(('longmemeval_v2_2026', len(chosen), digest, src, out))

# 3. t2ranking: queries.dev.tsv (24831条, qid+text)
src = os.path.join(RAW, 't2ranking_2023', 'v0_sample', 'queries.dev.tsv')
out = os.path.join(RAW, 't2ranking_2023', 'v0_sample_stage4', 'queries_sample.tsv')
lines = open(src, encoding='utf-8').read().splitlines()
header = lines[0]
data = lines[1:]
rnd = random.Random(SEED)
chosen_lines = rnd.sample(data, SAMPLE_N)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    f.write(header + '\n')
    f.write('\n'.join(chosen_lines) + '\n')
digest = sha256(out)
report.append(('t2ranking_2023', len(chosen_lines), digest, src, out))

# 4. multiwoz: dialogues_001.json (512段)
src = os.path.join(RAW, 'multiwoz_2_2_2020', 'v0_sample', 'dialogues_001.json')
out = os.path.join(RAW, 'multiwoz_2_2_2020', 'v0_sample_stage4', 'dialogues_sample.jsonl')
recs = json.load(open(src, encoding='utf-8'))
rnd = random.Random(SEED)
chosen = rnd.sample(recs, SAMPLE_N)
digest = write_jsonl(chosen, out)
report.append(('multiwoz_2_2_2020', len(chosen), digest, src, out))

print('=== 阶段4 A侧样本抽取结果 ===')
for ds, n, dg, s, o in report:
    print(f'[{ds}] 抽取 {n} 条 -> {os.path.relpath(o, REPO)}')
    print(f'      来源: {os.path.relpath(s, REPO)}')
    print(f'      SHA256: {dg}')
    print()

# 输出一个清单文件
manifest = [{'dataset_id': d, 'sample_count': n, 'sha256': dg, 'source_file': s, 'out_file': o} for d, n, dg, s, o in report]
mout = os.path.join(REPO, 'evidence', 'audit', 'stage4_a_sample_manifest.json')
os.makedirs(os.path.dirname(mout), exist_ok=True)
with open(mout, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f'清单已写: {os.path.relpath(mout, REPO)}')