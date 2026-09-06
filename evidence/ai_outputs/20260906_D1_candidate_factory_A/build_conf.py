# -*- coding: utf-8 -*-
"""Data-A D1 P22 Conflict 候选工厂（os_controlled_authored, candidate_only）
按 scenario_specs/conflict_scenarios.json planned_candidates 量产 64 条。
负例(scenario_class=non_conflict_hard_negative)不含 design_conflict_type。
"""
import json, os
from collections import Counter

OUT = r"C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_candidates_A_20260906\conflict_candidates.jsonl"

PLANNED = {"OSCONF-01": 10, "OSCONF-02": 12, "OSCONF-03": 8, "OSCONF-04": 8,
           "OSCONF-05": 8, "OSCONF-06": 10, "OSCONF-07": 8}
FAMILY = {"OSCONF-01": "os_conf_contradiction", "OSCONF-02": "os_conf_temporal_update",
          "OSCONF-03": "os_conf_pref_change", "OSCONF-04": "os_conf_scope_ambiguity",
          "OSCONF-05": "os_conf_source_conflict", "OSCONF-06": "os_conf_non_conflict_negative",
          "OSCONF-07": "os_conf_version"}

# (sid, old, new, design_conflict_type_or_None, design_reason_or_None)
S = []
def add(sid, old, new, ctype, reason=None):
    S.append({"sid": sid, "old": old, "new": new, "ctype": ctype, "reason": reason})

# ---- OSCONF-01 contradiction 10 ----
add("OSCONF-01", "项目评审会改到周三下午三点。", "项目评审会改到周五下午三点。", "contradiction")
add("OSCONF-01", "新项目代号定成北斗。", "新项目代号改叫启明。", "contradiction")
add("OSCONF-01", "报销流程：先贴票再走审批。", "报销流程：先审批通过再贴票。", "contradiction")
add("OSCONF-01", "版本发布窗口定在周四。", "版本发布窗口改到周一。", "contradiction")
add("OSCONF-01", "账号找回统一用邮箱验证。", "账号找回改成了短信验证。", "contradiction")
add("OSCONF-01", "这份会议纪要由张工负责。", "会议纪要改由李工负责。", "contradiction")
add("OSCONF-01", "服务器维护窗口是凌晨两点到四点。", "服务器维护窗口挪到凌晨四点以后。", "contradiction")
add("OSCONF-01", "这个需求排进下个迭代。", "这个需求推迟到再下一个迭代。", "contradiction")
add("OSCONF-01", "春节值班名单里有我。", "春节值班我不用去。", "contradiction")
add("OSCONF-01", "日志备份保留三十天。", "日志保留期改为九十天。", "contradiction")

# ---- OSCONF-02 temporal_update 12 (旧被新替代, 带日期) ----
add("OSCONF-02", "（3月记录）家庭地址是朝阳区一号院三栋。", "（5月记录）搬家后地址是海淀区三街九号。", "temporal_inconsistency")
add("OSCONF-02", "（年初）每周例会定在周一。", "（本周）从这周起例会改到周三。", "temporal_inconsistency")
add("OSCONF-02", "（上月）联系电话是 138 开头那个尾号 6221。", "（今天）手机换号了，新号尾号 8730。", "temporal_inconsistency")
add("OSCONF-02", "（旧）项目运行环境是 Python 3.8。", "（上周）环境已升级到 Python 3.12。", "temporal_inconsistency")
add("OSCONF-02", "（旧规）单笔报销上限五百元。", "（新规）上限已提到八百元。", "temporal_inconsistency")
add("OSCONF-02", "（旧）服务域名指向原服务器地址。", "（已切换）域名现在指向新服务器。", "temporal_inconsistency")
add("OSCONF-02", "（原定）评审在三楼 A 会议室。", "（临时改）会议室换到五楼 C 室。", "temporal_inconsistency")
add("OSCONF-02", "（之前）默认浏览器是 Edge。", "（现在）默认浏览器改成 Chrome。", "temporal_inconsistency")
add("OSCONF-02", "（冬季）午休十二点到一点。", "（夏令时起）午休改十二点半到一点半。", "temporal_inconsistency")
add("OSCONF-02", "（旧政策）登录密码每三个月一换。", "（新政策）改成每半年一换。", "temporal_inconsistency")
add("OSCONF-02", "（以前）通勤走三环主路。", "（现在）通勤改走四环高架。", "temporal_inconsistency")
add("OSCONF-02", "（旧）代码托管在 Group 一。", "（迁移后）仓库迁到了 Group 二。", "temporal_inconsistency")

# ---- OSCONF-03 preference_change 8 ----
add("OSCONF-03", "以后提醒都提前十分钟。", "现在改成提前半小时提醒我。", "preference_conflict")
add("OSCONF-03", "以后回复都先列要点。", "以后别列要点，给完整段落就行。", "preference_conflict")
add("OSCONF-03", "发出去的邮件默认抄送主管。", "邮件以后不要再抄送主管了。", "preference_conflict")
add("OSCONF-03", "交付文档都用 PDF 格式。", "以后改成优先用 Word 交付。", "preference_conflict")
add("OSCONF-03", "会议纪要当天晚上发。", "纪要改到会后一小时内发。", "preference_conflict")
add("OSCONF-03", "重要数据每周备份一次。", "备份改成每天一次。", "preference_conflict")
add("OSCONF-03", "和我交流默认用中文。", "默认切换成英文回复。", "preference_conflict")
add("OSCONF-03", "待办按截止时间排序。", "待办以后按优先级排序。", "preference_conflict")

# ---- OSCONF-04 scope_ambiguity 8 (scope 不同可共存 -> hard negative) ----
add("OSCONF-04", "工作邮箱的邮件一律自动归档。", "个人邮箱的邮件不要自动归档。", None, "scope 不同(工作 vs 个人)可共存")
add("OSCONF-04", "电脑上文件都用列表视图。", "手机上文件管理器用图标视图。", None, "scope 不同(设备)可共存")
add("OSCONF-04", "会议室系统自动清理一个月前的预订。", "律师会客室的历史预订保留两年。", None, "scope 不同(会议室类型)可共存")
add("OSCONF-04", "客厅空调设二十六度。", "卧室空调设二十四度。", None, "scope 不同(房间)可共存")
add("OSCONF-04", "主卧智能音箱每天早上报天气。", "书房的音箱不用报天气。", None, "scope 不同(设备)可共存")
add("OSCONF-04", "在线文档界面用深色。", "打印用的表格模板用浅色。", None, "scope 不同(文档类型/介质)可共存")
add("OSCONF-04", "开车出门提前半小时提醒。", "步行出门不用提醒。", None, "scope 不同(出行方式)可共存")
add("OSCONF-04", "重要联系人的电话设快捷拨号。", "快递外卖这些号码不要快捷拨号。", None, "scope 不同(联系人类别)可共存")

# ---- OSCONF-05 source_conflict 8 ----
add("OSCONF-05", "口述：这个月预算还剩两千。", "预算表：本月剩余五千。", "source_conflict")
add("OSCONF-05", "手机通讯录：李姐电话尾号 3301。", "电脑联系人：李姐电话尾号 3309。", "source_conflict")
add("OSCONF-05", "用户：这台服务器应该是八核。", "云控制台：实例配置显示四核。", "source_conflict")
add("OSCONF-05", "群公告：周五全公司团建放假。", "人事排班：周五正常上班。", "source_conflict")
add("OSCONF-05", "聊天里约好会议十点开始。", "日历邀请写的是九点开始。", "source_conflict")
add("OSCONF-05", "纸质收据金额一百二十元。", "信用卡账单这笔消费是两百一十元。", "source_conflict")
add("OSCONF-05", "安装记录显示装的是 2.0 版。", "更新日志显示已升级到 3.0 版。", "source_conflict")
add("OSCONF-05", "我记得定时发布设的是周三。", "后台显示定时发布排在周四。", "source_conflict")

# ---- OSCONF-06 non_conflict negative 10 ----
add("OSCONF-06", "周一我买了两本书。", "周一我还删了两个旧安装包。", None, "同一天不同对象,可共存")
add("OSCONF-06", "我设了每天早上八点的起床闹钟。", "我把七点的会议闹钟关了。", None, "两个不同闹钟,可共存")
add("OSCONF-06", "我最近在读《三体》。", "我同时也在追一部历史剧。", None, "不同休闲对象,可共存")
add("OSCONF-06", "下午三点有项目评审。", "上午十点我约了牙医复诊。", None, "不同时段,可共存")
add("OSCONF-06", "我偏好用命令行操作。", "这个图形化小工具也挺好用。", None, "一般习惯 vs 具体工具,可共存")
add("OSCONF-06", "平时喝咖啡都点美式。", "今天想换杯拿铁尝尝。", None, "习惯 vs 单次选择,可共存")
add("OSCONF-06", "出差住酒店偏好安静的高层。", "这次订的是民宿。", None, "习惯 vs 单次安排,可共存")
add("OSCONF-06", "项目甲用的是 Java。", "项目乙用的 Go。", None, "不同项目,可共存")
add("OSCONF-06", "屏幕上我喜欢把字调大。", "打印文档用的小字号省纸。", None, "显示 vs 打印,可共存")
add("OSCONF-06", "群里说周五有培训。", "我周五要出趟差。", None, "不同事项,可共存")

# ---- OSCONF-07 version 8 ----
add("OSCONF-07", "审批流程 v1：先经主管。", "流程 v2：改为先经项目经理。", "temporal_inconsistency")
add("OSCONF-07", "日报模板 v3：只含进度。", "日报模板 v4：新增风险一列。", "temporal_inconsistency")
add("OSCONF-07", "接口 v1 返回 JSON。", "接口 v2 起返回 XML。", "temporal_inconsistency")
add("OSCONF-07", "品牌手册 v1：主色为蓝色。", "品牌手册 v2：主色改为绿色。", "temporal_inconsistency")
add("OSCONF-07", "报销 SOP 1.0：需要纸质单据。", "报销 SOP 2.0：改为线上提交。", "temporal_inconsistency")
add("OSCONF-07", "权限模型 v1：所有人可建群。", "权限模型 v2：仅管理员可建群。", "temporal_inconsistency")
add("OSCONF-07", "排期旧版：功能 F1 在六月。", "排期新版：F1 推迟到八月。", "temporal_inconsistency")
add("OSCONF-07", "数据字典 v1：字段类型取 1 或 2。", "数据字典 v2：取值为 A、B、C。", "temporal_inconsistency")

# ---- checks ----
cnt = Counter(x["sid"] for x in S)
for k, v in PLANNED.items():
    assert cnt[k] == v, "planned mismatch %s: got %d want %d" % (k, cnt[k], v)
assert len(S) == 64, len(S)

def iso(i):
    hh = 8 + (i % 9)
    mm = (i * 11) % 60
    return "2026-08-2%dT%02d:%02d:00.000Z" % (1 + (i // 30) % 8, hh, mm)

lines = []
for i, s in enumerate(S, start=1):
    sid = "conf_d1_%04d" % i
    dm = {"scenario_spec_id": s["sid"], "scenario_family": FAMILY[s["sid"]],
          "candidate_event_refs": ["evt_conf_d1_%04d_a" % i, "evt_conf_d1_%04d_b" % i]}
    if s["ctype"] is None:
        dm["scenario_class"] = "non_conflict_hard_negative"
        dm["design_reason"] = s["reason"]
    else:
        dm["scenario_class"] = "actual_conflict"
        dm["design_conflict_type"] = s["ctype"]
    dm["generation"] = {"generation_id": "gen_conf_d1_20260906", "prompt_version": "P22-v4.1",
                        "seed": 20260906, "model": "deepseek-v4-flash", "source": "os_controlled_authored",
                        "source_file": "data/interim/d1_candidates_A_20260906/conflict_candidates.jsonl"}
    rec = {"sample_id": sid, "task_type": "conflict_resolution", "language": "zh-CN",
           "dataset_version": "kylin_memory_candidate_v4.1", "dataset_stage": "candidate_only",
           "review_status": "candidate_only", "admission_status": "NOT_ADMISSION_APPROVED",
           "id_binding_status": "NON_PRODUCTION", "scenario_user_ref": "u_os_conf_d1_%04d" % i,
           "conversation_id": "conv_conf_d1_%04d" % i, "timestamp": iso(i),
           "blind_visible": {"input": {"candidates": {"old": s["old"], "new": s["new"]}}},
           "design_metadata": dm}
    lines.append(json.dumps(rec, ensure_ascii=False))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("WROTE", len(lines), "->", OUT)
print("per-scenario:", dict(cnt))
