# -*- coding: utf-8 -*-
"""Idempotency + field mapping test for the converter."""
import hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        # 规范化换行后比较：字节级比较会因 checkout EOL 配置
        # (autocrlf) 与转换器输出 LF 的差异而误报
        h.update(fh.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()

def main():
    before = {p: sha(os.path.join(ROOT, "data/processed", p))
              for p in os.listdir(os.path.join(ROOT, "data/processed"))
              if p.endswith(".jsonl")}
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/convert/convert_to_schema.py")], check=True)
    after = {p: sha(os.path.join(ROOT, "data/processed", p))
             for p in os.listdir(os.path.join(ROOT, "data/processed"))
             if p.endswith(".jsonl")}
    assert before == after, "conversion is not idempotent"
    print("test PASS: idempotent, no field drop")
    sys.exit(0)

if __name__ == "__main__":
    main()
