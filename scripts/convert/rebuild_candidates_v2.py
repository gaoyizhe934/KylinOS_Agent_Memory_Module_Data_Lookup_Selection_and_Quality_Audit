#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阶段8 候选池重建 v2（A = lyf-1213，2026-09-04）

目的：废弃 v1.0 模板×计数器批量生成的候选母体，重建"真实数据接地 + 自建多样化"候选池。

来源策略：
- knowledge_retrieval: t2ranking 真实 query（public_derived）+ A 手写 OS 场景 query
- preference_extraction: longmemeval 真实用户偏好句 + multiwoz 真实用户句 + A 手写 OS 偏好场景
- conflict_resolution: longmemeval knowledge-update/temporal 真实事件链 + A 手写 OS 冲突场景
- precise_forgetting: longmemeval 真实记忆条目 + A 手写 OS 记忆场景
- end_to_end_session: longmemeval_v2 真实 question（任务链）+ A 手写 OS 会话链
- tool_result: 本轮不产（依赖阶段 10 麒麟 VM 回放，登记依赖）

输出：data/interim/gold_candidates_*_v2.jsonl（新文件，不覆盖 v1 母体）

用法：
  python scripts/convert/rebuild_candidates_v2.py [--dry-run]
"""
import json
import os
import random
import re
import sys

random.seed(20260904)

INTERIM = "data/interim"
LME_ORACLE = "data/raw/longmemeval_cleaned_2025/v0_subset/longmemeval_oracle.json"
LME_V2_Q = "data/raw/longmemeval_v2_2026/v0_subset/questions.jsonl"
T2R_Q = "data/raw/t2ranking_2023/v0_subset/queries.dev.tsv"
MWZ_RAW = "data/raw/multiwoz_2_2_2020/v0_subset/dialogues_001.json"

OUT_PATTERN = os.path.join(INTERIM, "gold_candidates_{task}_v2.jsonl")


def load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def load_lme_oracle():
    if not os.path.exists(LME_ORACLE):
        return []
    return json.load(open(LME_ORACLE, encoding="utf-8"))


def load_lme_v2_questions():
    rows = []
    if os.path.exists(LME_V2_Q):
        rows = load_jsonl(LME_V2_Q)
    return rows


def load_t2r_queries():
    if not os.path.exists(T2R_Q):
        return []
    out = []
    with open(T2R_Q, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                qid, query = parts[0], parts[1]
                if qid.lower() == "qid" or query.lower() in ("text", ""):
                    continue  # 跳过表头/无效行
                out.append({"query_id": qid, "query": query})
    return out


def load_multiwoz_user_utterances():
    if not os.path.exists(MWZ_RAW):
        return []
    d = json.load(open(MWZ_RAW, encoding="utf-8"))
    out = []
    for item in d:
        if not isinstance(item, dict):
            continue
        for turn in item.get("turns", []):
            if not isinstance(turn, dict):
                continue
            speaker = turn.get("speaker", "") or turn.get("role", "")
            text = turn.get("utterance", "") or turn.get("text", "")
            if speaker == "USER" and len(str(text).strip()) >= 10:
                out.append(str(text).strip())
    return out


# ---------------------------------------------------------------- 偏好句抽取
_PREF_HINT = re.compile(r"(prefer|like|want|always|usually|never|habit|tend|rather|please|don't|do not)", re.I)


def extract_lme_preferences(lme, limit=6):
    out = []
    for x in lme:
        if x.get("question_type") != "single-session-preference":
            continue
        uid = x["question_id"]
        for sess in x.get("haystack_sessions", []):
            for turn in sess:
                if not isinstance(turn, dict) or turn.get("role") != "user":
                    continue
                c = str(turn.get("content", "")).strip()
                if len(c) >= 25 and _PREF_HINT.search(c):
                    out.append({"raw_id": uid, "utterance": c})
                    break
            if len(out) >= limit:
                break
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------- 冲突事件链
def extract_lme_conflicts(lme, limit=5):
    """从 knowledge-update/temporal-reasoning 抽取真实事件冲突对。"""
    out = []
    for x in lme:
        qt = x.get("question_type")
        if qt not in ("knowledge-update", "temporal-reasoning"):
            continue
        uid = x["question_id"]
        users = []
        for sess in x.get("haystack_sessions", []):
            for turn in sess:
                if isinstance(turn, dict) and turn.get("role") == "user":
                    c = str(turn.get("content", "")).strip()
                    if len(c) >= 20:
                        users.append(c)
        if len(users) >= 2:
            out.append({
                "raw_id": uid,
                "question": x.get("question", ""),
                "answer": x.get("answer", ""),
                "old_turn": users[0],
                "new_turn": users[1],
            })
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------- 记忆条目
def extract_lme_memory_items(lme, limit=6):
    """从会话提取可遗忘的真实记忆条目（user 陈述的事实/偏好/事件）。"""
    out = []
    for x in lme:
        uid = x["question_id"]
        for sess in x.get("haystack_sessions", []):
            for turn in sess:
                if isinstance(turn, dict) and turn.get("role") == "user":
                    c = str(turn.get("content", "")).strip()
                    if len(c) >= 25:
                        out.append({"raw_id": uid, "item": c})
                    if len(out) >= limit:
                        break
            if len(out) >= limit:
                break
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------- 基础记录构造
def base_record(task_type, sample_id, user_id, conv_id, language, ts, template_family, input_, source, evidence, raw_id=None, source_file=None, source_version=None):
    rec = {
        "sample_id": sample_id,
        "dataset_version": "kylin_memory_gold_v1.0",
        "task_type": task_type,
        "language": language,
        "user_id": user_id,
        "conversation_id": conv_id,
        "timestamp": ts,
        "input": input_,
        "gold": {},
        "evidence": evidence,
        "source": source,
        "template_family": template_family,
        "annotator_a": "",
        "annotator_b": "",
        "review_status": "candidate_only",
    }
    if raw_id:
        rec["raw_id"] = raw_id
        rec["source_file"] = source_file or ""
        rec["source_version"] = source_version or ""
    return rec


TS = "2026-09-04T08:00:00.000Z"


# ================================================================ 任务构建
def build_preference(lme_prefs, mwz_utterances):
    records = []
    n = 1
    # A. longmemeval 真实偏好句（原文英文保留，candidate_only）
    for p in lme_prefs:
        records.append(base_record(
            "preference_extraction", f"pref_v2_{n:04d}", "u_lme_pref", f"conv_pref_v2_{n:04d}",
            "en", TS, "lme_preference_v1",
            {"user_message": p["utterance"], "scene": "longmemeval real session"},
            "public_derived",
            [{"source_event_id": p["raw_id"], "span": p["utterance"][:60]}],
            raw_id=p["raw_id"], source_file="longmemeval_oracle.json",
            source_version="longmemeval_cleaned_2025_v0_subset",
        ))
        n += 1
    # B. multiwoz 真实用户句
    for u in mwz_utterances[:4]:
        records.append(base_record(
            "preference_extraction", f"pref_v2_{n:04d}", "u_mwz_pref", f"conv_pref_v2_{n:04d}",
            "en", TS, "multiwoz_user_v1",
            {"user_message": u, "scene": "multiwoz dialogue"},
            "public_derived",
            [{"source_event_id": "mwz", "span": u[:60]}],
            raw_id="mwz", source_file="dialogues_001.json",
            source_version="multiwoz_2_2_2020_v0_subset",
        ))
        n += 1
    # C. A 手写 OS 偏好场景（多样化，覆盖 KMA preference_key 前缀族）
    os_scenes = [
        # (user_message, scene, template_family, language)
        ("以后截图默认保存成 PNG，不要 JPG。", "麒麟 OS 截图工具", "os_screenshot_style_v1", "zh-CN"),
        ("每次删除文件前先问我确认，别直接删。", "麒麟 OS 文件管理器", "os_delete_confirm_v1", "zh-CN"),
        ("写邮件时默认用中文，只有对方是外籍才用英文。", "麒麟 OS 邮件客户端", "os_mail_language_v1", "zh-CN"),
        ("终端里我习惯用 zsh，别给我换回 bash。", "麒麟 OS 终端", "os_terminal_shell_v1", "zh-CN"),
        ("开会期间把通知都静音，只留日历提醒。", "麒麟 OS 通知中心", "os_notify_silent_v1", "zh-CN"),
        ("外接显示器的时候桌面壁纸用浅色系。", "麒麟 OS 桌面", "os_desktop_theme_v1", "zh-CN"),
        ("备份任务放周末凌晨跑，别占用工作日。", "麒麟 OS 备份", "os_backup_schedule_v1", "zh-CN"),
        ("浏览器下载文件统一放 ~/Downloads，别问。", "麒麟 OS 浏览器", "os_download_dir_v1", "zh-CN"),
        ("这次系统更新先别装，等稳定版。", "麒麟 OS 更新管理器", "os_update_defer_v1", "zh-CN"),
        ("给客户演示时窗口用无边框模式。", "麒麟 OS 演示工具", "os_demo_borderless_v1", "zh-CN"),
    ]
    for msg, scene, fam, lang in os_scenes:
        records.append(base_record(
            "preference_extraction", f"pref_v2_{n:04d}", f"u_os_pref_{n:04d}", f"conv_pref_v2_{n:04d}",
            lang, TS, fam,
            {"user_message": msg, "scene": scene},
            "team_authored",
            [{"source_event_id": f"evt_pref_v2_{n:04d}", "span": msg[:60]}],
        ))
        n += 1
    return records


def build_retrieval(t2r_queries):
    records = []
    n = 1
    # A. t2ranking 真实 query（public_derived，语义多样）
    for q in t2r_queries[:12]:
        records.append(base_record(
            "knowledge_retrieval", f"retr_v2_{n:04d}", "u_t2r", f"conv_retr_v2_{n:04d}",
            "zh-CN", TS, "t2ranking_query_v1",
            {"query": q["query"], "query_id": q["query_id"]},
            "public_derived",
            [{"source_event_id": q["query_id"], "span": q["query"]}],
            raw_id=q["query_id"], source_file="queries.dev.tsv",
            source_version="t2ranking_2023_v0_subset",
        ))
        n += 1
    # B. A 手写 OS 检索 query（workflow/template/failure_experience 类型）
    os_queries = [
        ("麒麟系统里怎么查看开机自启项？", "workflow_reuse"),
        ("上次打印机卡纸是怎么解决的？", "history_case"),
        ("月度备份的流程模板是什么？", "template_reuse"),
        ("外接显示器不识别有哪些排查步骤？", "failure_experience"),
        ("软件安装失败先检查什么？", "workflow_reuse"),
        ("麒麟默认包管理器是什么？", "fact_knowledge"),
        ("截图快捷键怎么自定义？", "constraint"),
        ("系统更新后开机变慢怎么排查？", "failure_experience"),
    ]
    for q, qt in os_queries:
        records.append(base_record(
            "knowledge_retrieval", f"retr_v2_{n:04d}", f"u_os_retr_{n:04d}", f"conv_retr_v2_{n:04d}",
            "zh-CN", TS, "os_knowledge_retrieval_v1",
            {"query": q, "query_type": qt},
            "team_authored",
            [{"source_event_id": f"evt_retr_v2_{n:04d}", "span": q[:60]}],
        ))
        n += 1
    return records


def build_conflict(lme_conflicts):
    records = []
    n = 1
    # A. longmemeval 真实事件链（old/new 真实用户陈述）
    for c in lme_conflicts:
        records.append(base_record(
            "conflict_resolution", f"conf_v2_{n:04d}", "u_lme_conf", f"conv_conf_v2_{n:04d}",
            "en", TS, "lme_conflict_chain_v1",
            {
                "candidates": {"old": c["old_turn"], "new": c["new_turn"]},
                "scenario": f"真实会话事件链（question: {c['question'][:60]}）",
            },
            "public_derived",
            [{"source_event_id": c["raw_id"], "span": c["old_turn"][:60]},
             {"source_event_id": c["raw_id"], "span": c["new_turn"][:60]}],
            raw_id=c["raw_id"], source_file="longmemeval_oracle.json",
            source_version="longmemeval_cleaned_2025_v0_subset",
        ))
        n += 1
    # B. A 手写 OS 冲突场景
    os_conflicts = [
        ("桌面快捷键 F5 设为刷新，但某个应用里 F5 是另存为。", "作用域冲突：全局 vs 应用内", "os_scope_conflict_v1"),
        ("你以前说周报要详细，现在要求每节只写结论。", "时间先后更新冲突", "os_time_update_v1"),
        ("用户手动设置窗口大小，与行为推断的默认大小不同。", "来源冲突：手动 vs 推断", "os_source_conflict_v1"),
        ("旧安装流程要求先卸载，新版系统要求直接覆盖。", "知识版本冲突", "os_knowledge_version_v1"),
        ("为了效率想跳过删除确认，但安全策略要求必须确认。", "安全 vs 效率偏好冲突", "os_safety_conflict_v1"),
        ("全局用中文，但财务软件要求英文界面。", "作用域冲突：全局 vs 工具", "os_app_lang_conflict_v1"),
    ]
    for scenario, label, fam in os_conflicts:
        records.append(base_record(
            "conflict_resolution", f"conf_v2_{n:04d}", f"u_os_conf_{n:04d}", f"conv_conf_v2_{n:04d}",
            "zh-CN", TS, fam,
            {"candidates": {"old": "旧记忆", "new": "新指令"}, "scenario": scenario, "conflict_note": label},
            "team_authored",
            [{"source_event_id": f"evt_conf_v2_{n:04d}", "span": scenario[:60]}],
        ))
        n += 1
    return records


def build_forgetting(lme_items):
    records = []
    n = 1
    # A. longmemeval 真实记忆条目（forget_instruction 指向真实条目）
    for it in lme_items:
        records.append(base_record(
            "precise_forgetting", f"forg_v2_{n:04d}", "u_lme_forg", f"conv_forg_v2_{n:04d}",
            "en", TS, "lme_memory_item_v1",
            {"forget_instruction": f"请忘记这条记录：{it['item'][:80]}（仅此一条，保留其余会话记忆）"},
            "public_derived",
            [{"source_event_id": it["raw_id"], "span": it["item"][:60]}],
            raw_id=it["raw_id"], source_file="longmemeval_oracle.json",
            source_version="longmemeval_cleaned_2025_v0_subset",
        ))
        n += 1
    # B. A 手写 OS 遗忘场景
    os_forget = [
        ("忘记我上次设置的临时壁纸，恢复默认主题。", "single_item", "zh-CN"),
        ("删掉上周做的实验数据缓存，保留本周的。", "time_window", "zh-CN"),
        ("忘记关于客户 A 的联系记录，但保留销售流程知识。", "topic", "zh-CN"),
        ("撤回刚才对终端配色的修改。", "single_item", "zh-CN"),
        ("清空本次会话里我提到的所有临时偏好。", "session", "zh-CN"),
        ("把演示工具的默认字体改回系统默认。", "single_item", "zh-CN"),
        ("删除上个月的所有下载记录索引。", "time_window", "zh-CN"),
        ("忘了我的浏览器书签里那个临时收藏夹。", "topic", "zh-CN"),
    ]
    for instr, mode, lang in os_forget:
        records.append(base_record(
            "precise_forgetting", f"forg_v2_{n:04d}", f"u_os_forg_{n:04d}", f"conv_forg_v2_{n:04d}",
            lang, TS, f"os_forget_{mode}_v1",
            {"forget_instruction": instr, "forget_mode_hint": mode},
            "team_authored",
            [{"source_event_id": f"evt_forg_v2_{n:04d}", "span": instr[:60]}],
        ))
        n += 1
    return records


def build_e2e(lme_v2_questions):
    records = []
    n = 1
    # A. longmemeval_v2 真实 question（真实任务链，procedure/dynamic-environment 类型）
    picked = 0
    for q in lme_v2_questions:
        qt = q.get("question_type", "")
        if qt not in ("procedure", "dynamic-environment", "errors-gotchas"):
            continue
        records.append(base_record(
            "end_to_end_session", f"e2e_v2_{n:04d}", "u_lme_e2e", f"conv_e2e_v2_{n:04d}",
            "en", TS, "lme_v2_task_chain_v1",
            {"turns": [{"role": "user", "content": q.get("question", "")[:200]}],
             "events": [qt]},
            "public_derived",
            [{"source_event_id": q.get("id", "?"), "span": q.get("question", "")[:60]}],
            raw_id=q.get("id", "?"), source_file="questions.jsonl",
            source_version="longmemeval_v2_2026_v0_subset",
        ))
        n += 1
        picked += 1
        if picked >= 6:
            break
    # B. A 手写 OS 会话链
    os_e2e = [
        ("帮我准备今天的产品发布检查：先看版本号，再备份数据库，然后跑回归测试。",
         ["version_check", "db_backup", "regression_test"], "zh-CN"),
        ("新同事入职：创建账号、分配权限、配置邮箱签名、加入项目群。",
         ["account_create", "permission", "mail_signature", "join_group"], "zh-CN"),
        ("远程办公：连 VPN、同步办公文档、设置勿扰、定时备份。",
         ["vpn", "sync_docs", "dnd", "scheduled_backup"], "zh-CN"),
        ("给客户演示：关闭通知、固定演示窗口、切换演示壁纸、录屏。",
         ["dnd", "window_pin", "wallpaper", "screen_record"], "zh-CN"),
        ("磁盘快满了：查看占用、清理缓存、转移旧文件、重启磁盘索引。",
         ["df_check", "cache_clean", "file_move", "reindex"], "zh-CN"),
        ("系统更新后：验证关键服务、清理残留包、确认开机项、更新文档。",
         ["service_check", "residue_clean", "boot_check", "doc_update"], "zh-CN"),
    ]
    for turns_txt, events, lang in os_e2e:
        turns = [{"role": "user", "content": turns_txt}]
        records.append(base_record(
            "end_to_end_session", f"e2e_v2_{n:04d}", f"u_os_e2e_{n:04d}", f"conv_e2e_v2_{n:04d}",
            lang, TS, "os_e2e_workflow_v1",
            {"turns": turns, "events": events},
            "team_authored",
            [{"source_event_id": f"evt_e2e_v2_{n:04d}", "span": turns_txt[:60]}],
        ))
        n += 1
    return records


def main():
    dry = "--dry-run" in sys.argv
    lme = load_lme_oracle()
    lme_v2 = load_lme_v2_questions()
    t2r = load_t2r_queries()
    mwz = load_multiwoz_user_utterances()

    print(f"数据源: lme_oracle={len(lme)} lme_v2={len(lme_v2)} t2r={len(t2r)} mwz_user={len(mwz)}")

    tasks = {
        "preference_extraction": build_preference(extract_lme_preferences(lme, 6), mwz),
        "knowledge_retrieval": build_retrieval(t2r),
        "conflict_resolution": build_conflict(extract_lme_conflicts(lme, 5)),
        "precise_forgetting": build_forgetting(extract_lme_memory_items(lme, 6)),
        "end_to_end_session": build_e2e(lme_v2),
    }

    os.makedirs(INTERIM, exist_ok=True)
    for task, records in tasks.items():
        out = OUT_PATTERN.format(task=task)
        if dry:
            print(f"[dry-run] {task}: {len(records)} -> {out}")
            continue
        with open(out, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"[written] {task}: {len(records)} -> {out}")

    if dry:
        return
    # 去重自检
    sys.path.insert(0, os.path.join("scripts", "audit"))
    from stage8_semantic_dedup import scan_files
    files = [OUT_PATTERN.format(task=t) for t in tasks]
    res = scan_files(files)
    ok = True
    for path, v in res.items():
        print(f"dedup[{path}]: total={v['total']} unique={v['unique_input']} dup_groups={v['dup_groups']}")
        if v["dup_groups"]:
            ok = False
    print("DEDUP:", "CLEAN" if ok else "DUP_FOUND")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()