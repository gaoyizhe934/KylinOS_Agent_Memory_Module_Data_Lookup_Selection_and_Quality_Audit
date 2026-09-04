#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Stage8 P1-3 kma_convert idempotency test (canonical). Replaces legacy test_convert
# now that processed is canonicalized. Idempotent via _is_canonical guard.
import glob
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(ROOT, 'data', 'processed')
KMA = os.path.join(ROOT, 'scripts', 'convert', 'kma_convert.py')

def digest():
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(PROCESSED, '*.jsonl'))):
        with open(p, 'rb') as fh:
            raw = fh.read().replace(b'\r\n', b'\n')
            h.update(p.encode('utf-8'))
            h.update(raw)
    return h.hexdigest()

def main():
    before = digest()
    proc = subprocess.run([sys.executable, KMA], capture_output=True, text=True, encoding='utf-8')
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        sys.exit('kma_convert failed')
    after = digest()
    proc2 = subprocess.run([sys.executable, KMA], capture_output=True, text=True, encoding='utf-8')
    if proc2.returncode != 0:
        sys.exit('kma_convert second run failed')
    after2 = digest()
    print('kma_convert idempotency:')
    print('  before=', before[:12])
    print('  after =', after[:12])
    print('  after2=', after2[:12])
    if before != after:
        print('FAIL: processed changed after kma_convert (committed output not canonical-stable)')
        sys.exit(1)
    if after != after2:
        print('FAIL: kma_convert not idempotent')
        sys.exit(1)
    print('PASS: kma_convert idempotent (canonical stable)')

if __name__ == '__main__':
    main()
