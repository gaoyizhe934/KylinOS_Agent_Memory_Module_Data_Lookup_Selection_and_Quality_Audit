# -*- coding: utf-8 -*-
"""阶段4 A侧: 为允许试用数据集抽取 50~100 条审计样本到 v0_sample_stage4/

依据: 手册6.3 + 阶段4 脚本 (stage4_sample_audit.py) 要求每集 50~100 条新样本审计。
- 只读 data/raw/<ds_id>/v0_sample/ 全量, 抽取后写入 data/raw/<ds_id>/v0_sample_stage4/
- seed=42 保证可复现
- 不修改/删除全量原始文件 (红线: raw 只读)
- v0_sample_stage4/ 为脚本派生的审计子样本, 属 raw 内"新增", 不改动任何原始文件

修复记录 (Reviewer 复审):
- High-1: 所有写出统一 newline="\\n"(LF), 使 SHA 与 git 提交 blob(LF) 一致
- High-2: manifest 改用仓库相对路径, 注明源数据来自 v1.0 外部工作包(不在仓库内)
- Low-1: 删除未使用的空函数 extract()
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
    """写入 JSONL, 强制 LF(newline='\\n'), 使文件哈希与 git 提交 blob 一致."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return sha256(out_path)


def write_tsv(header, rows, out_path):
    """写入 TSV, 强制 LF."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header + '\n')
        f.write('\n'.join(rows) + '\n')
    return sha256(out_path)


def rel(path):
    """仓库相对路径, 用正斜杠, 保证可移植(不在 manifest 写死他机绝对路径)."""
    return os.path.relpath(path, REPO).replace('\\', '/')


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
report.append(('longmemeval_cleaned_2025', len(chosen), digest, rel(src), rel(out)))

# 2. longmemeval_v2: questions.jsonl (451条)
src = os.path.join(RAW, 'longmemeval_v2_2026', 'v0_sample', 'questions.jsonl')
out = os.path.join(RAW, 'longmemeval_v2_2026', 'v0_sample_stage4', 'questions_sample.jsonl')
recs = [json.loads(l) for l in open(src, encoding='utf-8') if l.strip()]
rnd = random.Random(SEED)
chosen = rnd.sample(recs, SAMPLE_N)
digest = write_jsonl(chosen, out)
report.append(('longmemeval_v2_2026', len(chosen), digest, rel(src), rel(out)))

# 3. t2ranking: queries.dev.tsv (24831条, qid+text)
src = os.path.join(RAW, 't2ranking_2023', 'v0_sample', 'queries.dev.tsv')
out = os.path.join(RAW, 't2ranking_2023', 'v0_sample_stage4', 'queries_sample.tsv')
lines = open(src, encoding='utf-8').read().splitlines()
header = lines[0]
data = lines[1:]
rnd = random.Random(SEED)
chosen_lines = rnd.sample(data, SAMPLE_N)
digest = write_tsv(header, chosen_lines, out)
report.append(('t2ranking_2023', len(chosen_lines), digest, rel(src), rel(out)))

# 4. multiwoz: dialogues_001.json (512段)
src = os.path.join(RAW, 'multiwoz_2_2_2020', 'v0_sample', 'dialogues_001.json')
out = os.path.join(RAW, 'multiwoz_2_2_2020', 'v0_sample_stage4', 'dialogues_sample.jsonl')
recs = json.load(open(src, encoding='utf-8'))
rnd = random.Random(SEED)
chosen = rnd.sample(recs, SAMPLE_N)
digest = write_jsonl(chosen, out)
report.append(('multiwoz_2_2_2020', len(chosen), digest, rel(src), rel(out)))

print('=== 阶段4 A侧样本抽取结果 ===')
for ds, n, dg, s, o in report:
    print(f'[{ds}] 抽取 {n} 条 -> {o}')
    print(f'      来源: {s}')
    print(f'      SHA256: {dg}')
    print()

# 输出清单文件 (仓库相对路径)
manifest = [{
    'dataset_id': d,
    'sample_count': n,
    'sha256': dg,
    'source_file': s,
    'out_file': o,
} for d, n, dg, s, o in report]
mout = os.path.join(REPO, 'evidence', 'audit', 'stage4_a_sample_manifest.json')
os.makedirs(os.path.dirname(mout), exist_ok=True)
with open(mout, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f'清单已写: {rel(mout)}')
print()
print('注: 源数据来自 v1.0 外部工作包 (data/raw/v0_sample 全量, gitignore 大文件, 不在仓库内);')
print('    v0_sample_stage4/ 为脚本派生审计子样本, 不改动任何原始文件.')