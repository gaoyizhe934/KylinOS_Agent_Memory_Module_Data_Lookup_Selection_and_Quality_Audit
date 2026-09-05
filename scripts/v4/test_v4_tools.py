# -*- coding: utf-8 -*-
"""v4.1 P2-A 最小工具单测（B = DGXD01，2026-09-05）"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run(script, *args):
    return subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "v4", script), *args],
                          capture_output=True, text=True, encoding="utf-8")


def test_inventory():
    # 幂等 + raw 只读 + 输出一致
    with tempfile.TemporaryDirectory() as td:
        o1 = os.path.join(td, "inv1.json")
        o2 = os.path.join(td, "inv2.json")
        r1 = run("inventory_legacy.py", "--out", o1)
        r2 = run("inventory_legacy.py", "--out", o2)
        assert r1.returncode == 0 and r2.returncode == 0, (r1.stdout, r1.stderr)
        d1 = json.load(open(o1, encoding="utf-8"))
        d2 = json.load(open(o2, encoding="utf-8"))
        assert d1["summary"] == d2["summary"], "幂等不一致"
        assert d1["summary"]["gold_total"] >= 0
        print("test_inventory PASS", d1["summary"])


def test_preflight_failclosed():
    r = run("preflight.py")
    # 主仓接口缺失 => exit 2 (fail-closed)；registry 缺失只 PENDING
    assert r.returncode in (0, 2), r.stdout
    assert "BLOCKED_MAIN_CONTRACT" in r.stdout
    print("test_preflight_failclosed PASS rc=", r.returncode)


def test_raw_readonly():
    # 记录 raw 目录某文件 hash，工具运行后应不变（工具本身只读 raw）
    import hashlib
    rawf = os.path.join(ROOT, "data", "raw", "longmemeval_cleaned_2025", "v0_sample", "longmemeval_oracle.json")
    if os.path.exists(rawf):
        h0 = hashlib.sha256(open(rawf, "rb").read()).hexdigest()
        run("inventory_legacy.py")
        run("preflight.py")
        h1 = hashlib.sha256(open(rawf, "rb").read()).hexdigest()
        assert h0 == h1, "raw 被修改"
        print("test_raw_readonly PASS")
    else:
        print("test_raw_readonly SKIP (无 raw 样本)")


if __name__ == "__main__":
    test_inventory()
    test_preflight_failclosed()
    test_raw_readonly()
    print("ALL PASS")
