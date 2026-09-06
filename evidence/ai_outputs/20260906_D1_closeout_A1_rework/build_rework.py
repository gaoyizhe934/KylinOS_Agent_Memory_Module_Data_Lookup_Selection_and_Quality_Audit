# -*- coding: utf-8 -*-
"""Data-A Closeout A1 —— 10 条 Legacy REWORK/RELABEL 实际改造
输入：master c21ee694 中 data/gold/{dev,regression,sealed_test} 原始行（10 代表）
     + #37 冻结 fix_fields（requal Rev3 legacy_semantic_requal_A.jsonl）
输出：data/interim/d1_legacy_rework_A_20260906/*.jsonl（candidate_only/NON_PRODUCTION，修复后候选）
规则：不写 human_decision/final_label/gold；blind 无答案；timestamp 归一合法 ISO；DEV_REG_ONLY(sealed) 保留；
      provenance/generation/template_family 保留。
"""
import json, os, re
from collections import Counter

D = r'C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_legacy_rework_A_20260906'
os.makedirs(D, exist_ok=True)
REPO_REF = "c21ee694c1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1d1"  # placeholder replaced below

FIXED_TS = "2026-07-20T10:00:00+08:00"

def norm_ts(orig):
    # B-L2: '2026-07-202T...' 计数器并入日期日 → 去多余日位
    m = re.match(r'^(\d{4}-\d{2}-\d{2})\d+T(\d{2}:\d{2}:\d{2})([+-]\d{2}:\d{2})$', orig)
    if m:
        return "%sT%s%s" % (m.group(1), m.group(2), m.group(3))
    return FIXED_TS

PRE = []
def add_pref(sid, legacy, user_msg, cls, step1, scope, family, fixes, dev_reg=False):
    PRE.append(dict(sample_id=sid, legacy=legacy, user_msg=user_msg, cls=cls, step1=step1,
                    scope=scope, family=family, fixes=fixes, dev_reg=dev_reg))

# ---- Preference 6 ----
add_pref("req_pref_000001",
    dict(legacy_sample_id="pref_000001", file="data/gold/regression/preference_extraction.jsonl",
         v1_family="output_style_length_v1", v1_gold_scope="app", original_user_id="u_synthetic_18917_01", original_conversation="conv_pref_000001", split="regression"),
    "以后项目周报用简洁要点，每条不超过两行，不要长篇段落。",
    "explicit_persistent", "persistent_preference", "topic", "os_pref_topic_style",
    ["timestamp: 2026-07-202T10:00:00+08:00 → 2026-07-20T10:00:00+08:00 (B-L2)", "scope: v1 app → topic (G2: 项目周报文体，禁默认 tool)"], False)
add_pref("req_pref_000002",
    dict(legacy_sample_id="pref_000002", file="data/gold/regression/preference_extraction.jsonl",
         v1_family="tool_choice_confirm_v1", v1_gold_scope="global", original_user_id="u_synthetic_39875_02", original_conversation="conv_pref_000002", split="regression"),
    "需要删除文件前先问我确认，不要直接执行。",
    "explicit_persistent", "persistent_preference", "global", "os_pref_global_rule",
    ["timestamp: 2026-07-203T → 2026-07-20T (B-L2)", "scope 统一 global (Round3 D1: 跨工具删除安全确认)"], False)
add_pref("req_pref_000005",
    dict(legacy_sample_id="pref_000005", file="data/gold/regression/preference_extraction.jsonl",
         v1_family="scope_app_v1", v1_gold_scope="app", original_user_id="u_synthetic_01941_05", original_conversation="conv_pref_000005", split="regression"),
    "在这个项目管理工具里一律用中文标签，其他工具保持英文。",
    "explicit_persistent_tool", "persistent_preference", "tool", "os_pref_app_tool",
    ["timestamp: 2026-07-206T → 2026-07-20T (B-L2)", "scope: tool (项目管理工具唯一确定)"], False)
add_pref("req_pref_000004",
    dict(legacy_sample_id="pref_000004", file="data/gold/sealed_test/preference_extraction.jsonl",
         v1_family="update_revoke_v1", v1_gold_scope="app", original_user_id="u_synthetic_51291_04", original_conversation="conv_pref_000004", split="sealed_test"),
    "之前说报告要详细，以后改成每节只写结论和关键数字。",
    "update_revoke", "preference_update_withdraw", "topic", "os_pref_withdraw",
    ["timestamp: 2026-07-205T → 2026-07-20T (B-L2)", "decision_semantics: update/withdraw 新值优先", "scope: app→topic (G2)", "split_eligibility DEV_REG_ONLY(sealed 暴露)"], True)
add_pref("req_pref_000006",
    dict(legacy_sample_id="pref_000006", file="data/gold/regression/preference_extraction.jsonl",
         v1_family="sensitive_no_store_v1", v1_gold_scope="global", original_user_id="u_synthetic_85014_06", original_conversation="conv_pref_000006", split="regression"),
    "别记我的支付密码，也不要把付款信息写进记忆。",
    "sensitive_non_storable", "non_preference", None, "os_pref_sensitive",
    ["timestamp: 2026-07-207T → 2026-07-20T (B-L2)", "RELABEL→non_storable_negative：不存储不赋 scope，可作 Preference 负例"], False)
add_pref("req_pref_000003",
    dict(legacy_sample_id="pref_000003", file="data/gold/sealed_test/preference_extraction.jsonl",
         v1_family="temp_instruction_v1", v1_gold_scope="session", original_user_id="u_synthetic_96887_03", original_conversation="conv_pref_000003", split="sealed_test"),
    "这次就按英文回复，不用记住。",
    "task_constraint", "task_constraint", None, "os_pref_task_constraint",
    ["timestamp: 2026-07-204T → 2026-07-20T (B-L2)", "RELABEL→task_constraint：仅本次任务约束，不赋 scope", "split_eligibility DEV_REG_ONLY(sealed 暴露)"], True)

# ---- Forgetting 4 ----
FORG = []
def add_forg(sid, legacy, instr, inv, mode, design, family, fixes):
    FORG.append(dict(sample_id=sid, legacy=legacy, instr=instr, inv=inv, mode=mode,
                     design=design, family=family, fixes=fixes))

add_forg("req_forg_000001",
    dict(legacy_sample_id="forg_000001", file="data/gold/dev/precise_forgetting.jsonl",
         v1_family="forget_scoped_v1", original_user_id="u_synthetic_06570_01", original_conversation="conv_forg_000001", split="dev"),
    "忘记我在 VSCode 中偏好深色主题，但保留其他开发偏好。",
    [("pref_ui_theme_001", "VSCode 深色主题偏好"), ("pref_editor_001", "编辑器其他开发偏好"), ("pref_language_001", "开发语言相关偏好")],
    "single_item",
    {"target_ids": ["pref_ui_theme_001"], "must_keep": ["pref_editor_001", "pref_language_001"],
     "checkpoints": ["immediate_query", "after_restart", "after_full_reindex"], "expected_residual_count": 0},
    "os_forg_single_item",
    ["timestamp: 2026-07-202T → 2026-07-20T (B-L2)", "mode: single_item（target 单条，must_keep 其余开发偏好）"])
add_forg("req_forg_000002",
    dict(legacy_sample_id="forg_000002", file="data/gold/dev/precise_forgetting.jsonl",
         v1_family="forget_time_v1", original_user_id="u_synthetic_73376_02", original_conversation="conv_forg_000002", split="dev"),
    "删除上周临时记录的文件路径，保留本周的记录。",
    [("kb_path_009", "上周临时记录的文件路径"), ("kb_path_010", "本周的记录路径"), ("doc_share", "共享文档目录")],
    "time_window",
    {"target_ids": ["kb_path_009"], "must_keep": ["kb_path_010"],
     "target_time_range": {"start": "2026-07-13T00:00:00+08:00", "end": "2026-07-19T23:59:59+08:00"},
     "checkpoints": ["immediate_query", "after_restart", "after_full_reindex"], "expected_residual_count": 0},
    "os_forg_time_window",
    ["timestamp: 2026-07-203T → 2026-07-20T (B-L2)", "mode: time_window；补 target_time_range 显式边界（上周窗口为 NON_PRODUCTION 设计占位，正式绑定前核校）"])
add_forg("req_forg_000003",
    dict(legacy_sample_id="forg_000003", file="data/gold/dev/precise_forgetting.jsonl",
         v1_family="forget_person_v1", original_user_id="u_synthetic_37795_03", original_conversation="conv_forg_000003", split="dev"),
    "忘记某个客户姓名的所有关联记录，但保留流程知识。",
    [("kb_person_012", "某客户姓名关联记录"), ("kb_workflow_003", "业务流程知识"), ("mail_tpl", "邮件模板偏好")],
    "topic",
    {"target_ids": ["kb_person_012"], "must_keep": ["kb_workflow_003", "mail_tpl"],
     "target_topic": "客户姓名关联（个人信息）",
     "checkpoints": ["immediate_query", "after_restart", "after_full_reindex"], "expected_residual_count": 0},
    "os_forg_topic",
    ["timestamp: 2026-07-204T → 2026-07-20T (B-L2)", "mode: topic/relation（客户姓名关联）；must_keep=流程/通用知识", "sensitivity: 人名片 PII —— Data-R 复核，正式集需合成/脱敏（Round3 C3）"])
add_forg("req_forg_000004",
    dict(legacy_sample_id="forg_000004", file="data/gold/dev/precise_forgetting.jsonl",
         v1_family="forget_revoke_v1", original_user_id="u_synthetic_05841_04", original_conversation="conv_forg_000004", split="dev"),
    "撤回刚才设置的桌面布局偏好，恢复系统默认。",
    [("pref_ui_layout_021", "刚才设置的桌面布局偏好"), ("pref_ui_theme_001", "桌面深色主题偏好"), ("pref_ui_font", "界面字号偏好")],
    "single_item",
    {"target_ids": ["pref_ui_layout_021"], "must_keep": ["pref_ui_theme_001", "pref_ui_font"],
     "checkpoints": ["immediate_query", "after_restart", "after_full_reindex"], "expected_residual_count": 0},
    "os_forg_single_item",
    ["timestamp: 2026-07-205T → 2026-07-20T (B-L2)", "mode: single_item（偏好撤销=删除该条偏好记忆，无 full_reset 歧义，Round3 D2）"])

def iso_idx(i):
    return "2026-07-2%dT%02d:%02d:%02d+08:00" % (0, 9, (i*7) % 60, 0)

def build_record(sample_id, task_type, legacy, timestamp, blind, dm):
    dm["legacy_ref"] = legacy
    dm["generation"] = {"generation_id": "gen_legacy_rework_A_20260906", "prompt_version": "P10-Rev3-A1",
                        "seed": 20260906, "model": "deepseek-v4-flash", "source": "legacy_rework_team_authored",
                        "repo_ref": "master c21ee694",
                        "source_file": "data/interim/d1_legacy_rework_A_20260906/"}
    dm["split_eligibility"] = "DEV_REG_ONLY" if dm.get("_dev_reg") else "ANY"
    dm.pop("_dev_reg", None)
    return {"sample_id": sample_id, "task_type": task_type, "language": "zh-CN",
            "dataset_version": "kylin_memory_candidate_v4.1", "dataset_stage": "candidate_only",
            "review_status": "candidate_only", "admission_status": "NOT_ADMISSION_APPROVED",
            "id_binding_status": "NON_PRODUCTION", "scenario_user_ref": "u_" + sample_id,
            "conversation_id": "conv_" + sample_id, "timestamp": timestamp,
            "blind_visible": {"input": blind}, "design_metadata": dm}

pref_lines = []
for i, s in enumerate(PRE, start=1):
    dm = {"scenario_family": s["family"], "scenario_class": s["cls"],
          "task_semantic_class": s["step1"], "candidate_event_refs": ["evt_" + s["sample_id"]],
          "applied_fixes": s["fixes"], "_dev_reg": s["dev_reg"]}
    if s["scope"] is not None:
        dm["design_scope_target"] = s["scope"]
    rec = build_record(s["sample_id"], "preference_extraction", s["legacy"], FIXED_TS, {"user_message": s["user_msg"]}, dm)
    pref_lines.append(rec)

forg_lines = []
for i, s in enumerate(FORG, start=1):
    inv = [{"memory_ref": r, "subject": sub} for r, sub in s["inv"]]
    dm = {"scenario_family": s["family"], "forget_mode": s["mode"],
          "candidate_event_refs": ["evt_" + s["sample_id"]],
          "applied_fixes": s["fixes"], "_dev_reg": False}
    d = s["design"]
    dm["checkpoints"] = d["checkpoints"]; dm["expected_residual_count"] = d["expected_residual_count"]
    dm["target_ids"] = d["target_ids"]; dm["must_keep"] = d["must_keep"]
    if "target_time_range" in d: dm["target_time_range"] = d["target_time_range"]
    if "target_topic" in d: dm["target_topic"] = d["target_topic"]
    blind = {"forget_instruction": s["instr"], "inventory_context": inv}
    rec = build_record(s["sample_id"], "precise_forgetting", s["legacy"], FIXED_TS, blind, dm)
    forg_lines.append(rec)

def dump(recs, fn):
    with open(os.path.join(D, fn), 'w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('WROTE', len(recs), fn)

dump(pref_lines, 'legacy_rework_preference_candidates.jsonl')
dump(forg_lines, 'legacy_rework_forgetting_candidates.jsonl')
print('total', len(pref_lines) + len(forg_lines))
