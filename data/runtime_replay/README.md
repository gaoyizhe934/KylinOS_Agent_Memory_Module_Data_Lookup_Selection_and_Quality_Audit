# 麒麟 Runtime 回放准备包

本目录用于放置经批准并封存的固定测试子集。当前为准备状态，尚未在麒麟虚拟机真实执行。

执行要求（手册阶段10）：
1. 通过 WinSCP/SSH 将 `data/runtime_replay/input_manifest.json` 与固定子集传入虚拟机。
2. 执行 `scripts/evaluate/run_runtime_replay.sh`，保存原始命令、日志、截图。
3. 执行真实 Tool、SDK、检索、遗忘、重启和降级测试，禁止用静态检查替代。
4. 将 `environment_manifest.md` 与实际环境核对后回填。
