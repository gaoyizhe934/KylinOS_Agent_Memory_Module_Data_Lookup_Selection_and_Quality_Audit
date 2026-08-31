# 复现说明 2026-08-07

## 环境

- Windows PowerShell + 本包内置 Python 脚本；麒麟虚拟机阶段按手册 03 配置。
- 依赖：python-docx（报告生成）、标准库（其余脚本）。

## 一键重建

```powershell
python scripts\oneclick\run_all.py
```

## 公开样本下载与冻结

```powershell
python scripts\download\download_samples.py --limit 100
python scripts\validate\validate_schema.py
```

下载后把原始文件放入 `data/raw/<dataset_id>/<version>/`，生成 `manifest.json`、
`sha256sum.txt` 与 `download.log`，并由 Reviewer 复核 Gate 6。

## 转换与测试

```powershell
python scripts\convert\convert_to_schema.py
python scripts\convert\test_convert.py
```

## 切分与泄漏检查

```powershell
python scripts\split\split_and_seal.py
python scripts\split\leakage_check.py
```

## 麒麟虚拟机回放

将 `data/runtime_replay/` 与固定子集传入虚拟机，执行：

```bash
bash scripts/evaluate/run_runtime_replay.sh
python scripts/evaluate/collect_metrics.py --out evidence/runtime/raw_metrics.json
```

回放结果回填 `evaluation_report_v1.docx` 与 `handoff_v1.md` 后重新出报告。
