# -*- coding: utf-8 -*-
"""Data-A D1 P23 Forgetting 候选工厂（os_controlled_authored, candidate_only）
按 scenario_specs/forgetting_scenarios.json planned_candidates 量产 56 条。
每条正式候选含 memory_inventory(inventory_context) + target + must_keep + checkpoints + expected_residual。
负例(ambiguous_selector)用 scenario_class，不含 forget_mode/selector 字段。
"""
import json, os
from collections import Counter

OUT = r"C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_candidates_A_20260906\forgetting_candidates.jsonl"

PLANNED = {"OSFORG-01": 10, "OSFORG-02": 8, "OSFORG-03": 8, "OSFORG-04": 8,
           "OSFORG-05": 6, "OSFORG-06": 6, "OSFORG-07": 6, "OSFORG-08": 4}
FAMILY = {"OSFORG-01": "os_forg_single_item", "OSFORG-02": "os_forg_session", "OSFORG-03": "os_forg_topic",
          "OSFORG-04": "os_forg_time_window", "OSFORG-05": "os_forg_restart", "OSFORG-06": "os_forg_reindex",
          "OSFORG-07": "os_forg_ambiguous_negative", "OSFORG-08": "os_forg_full_reset"}

# 记录字段: sid, forget_instruction, inventory(list of (ref,subject)), design(dict), cls, mode
S = []
def add(sid, instr, inv, mode, design, cls=None):
    S.append({"sid": sid, "instr": instr, "inv": inv, "mode": mode, "design": design, "cls": cls})

def t(i):  # timestamp
    return "2026-08-2%dT%02d:%02d:00.000Z" % (1 + (i // 28) % 8, 8 + (i % 9), (i * 11) % 60)

# ---- OSFORG-01 single_item 10 ----
add("OSFORG-01", "忘记我设置的每周五早上十点提醒交周报这条。",
    [("m_remind_wfr", "每周五上午十点提醒交周报"), ("m_meet_tpl", "会议纪要模板"), ("m_addr_home", "家庭地址")],
    "single_item", {"target_ids": ["m_remind_wfr"], "must_keep": ["m_meet_tpl", "m_addr_home"], "expected_residual_count": 0})
add("OSFORG-01", "把下载目录每周日自动清理这条设置忘掉。",
    [("m_clean_dl", "下载目录每周日自动清理"), ("m_theme_dark", "编辑器深色主题"), ("m_browser_home", "浏览器空白主页")],
    "single_item", {"target_ids": ["m_clean_dl"], "must_keep": ["m_theme_dark", "m_browser_home"], "expected_residual_count": 0})
add("OSFORG-01", "忘记新邮件自动转发到工作邮箱这条规则。",
    [("m_auto_fwd", "新邮件自动转发到工作邮箱"), ("m_wallpaper", "桌面壁纸图片"), ("m_weekly_meet", "每周例会提醒")],
    "single_item", {"target_ids": ["m_auto_fwd"], "must_keep": ["m_wallpaper", "m_weekly_meet"], "expected_residual_count": 0})
add("OSFORG-01", "忘掉我存的小区物业电话。",
    [("m_prop_tel", "小区物业电话"), ("m_fam_doc", "家庭医生电话"), ("m_office_ext", "办公室分机号")],
    "single_item", {"target_ids": ["m_prop_tel"], "must_keep": ["m_fam_doc", "m_office_ext"], "expected_residual_count": 0})
add("OSFORG-01", "忘记每月一号自动续费会员这条订阅记忆。",
    [("m_sub_renew", "每月一号自动续费会员"), ("m_annual_check", "年度体检预约"), ("m_pay_date", "下期还款日")],
    "single_item", {"target_ids": ["m_sub_renew"], "must_keep": ["m_annual_check", "m_pay_date"], "expected_residual_count": 0})
add("OSFORG-01", "忘掉我常点的咖啡是燕麦拿铁这条口味记录。",
    [("m_coffee_taste", "常点燕麦拿铁"), ("m_bookstore", "常去书店的位置"), ("m_commute", "通勤大概时长")],
    "single_item", {"target_ids": ["m_coffee_taste"], "must_keep": ["m_bookstore", "m_commute"], "expected_residual_count": 0})
add("OSFORG-01", "忘记文档默认保存到 D 盘这条设置。",
    [("m_save_d", "文档默认保存到 D 盘"), ("m_printer_dup", "打印机默认双面打印"), ("m_recycle_days", "回收站保留天数")],
    "single_item", {"target_ids": ["m_save_d"], "must_keep": ["m_printer_dup", "m_recycle_days"], "expected_residual_count": 0})
add("OSFORG-01", "把晚上九点睡觉提醒这条忘掉。",
    [("m_sleep_alarm", "晚上九点睡觉提醒"), ("m_morning_run", "晨跑路线"), ("m_report_fmt", "周报格式偏好")],
    "single_item", {"target_ids": ["m_sleep_alarm"], "must_keep": ["m_morning_run", "m_report_fmt"], "expected_residual_count": 0})
add("OSFORG-01", "忘掉会议纪要要抄送行政这条规则。",
    [("m_minutes_cc", "纪要抄送行政"), ("m_room_device", "会议室默认设备"), ("m_travel_seat", "差旅偏好靠窗")],
    "single_item", {"target_ids": ["m_minutes_cc"], "must_keep": ["m_room_device", "m_travel_seat"], "expected_residual_count": 0})
add("OSFORG-01", "忘掉自动备份到移动硬盘这条记录。",
    [("m_backup_hdd", "自动备份到移动硬盘"), ("m_cloud_acct", "云盘账号"), ("m_sync_freq", "同步频率设置")],
    "single_item", {"target_ids": ["m_backup_hdd"], "must_keep": ["m_cloud_acct", "m_sync_freq"], "expected_residual_count": 0})

# ---- OSFORG-02 session 8 ----
add("OSFORG-02", "删除上周二那次调试会话产生的全部记录。",
    [("m_dbg_dir", "调试临时目录路径"), ("m_dbg_log", "报错日志摘录"), ("m_dbg_brk", "断点位置"), ("m_addr_home", "家庭地址")],
    "session", {"target_session_id": "sess_debug_last_tue", "target_ids": ["m_dbg_dir", "m_dbg_log", "m_dbg_brk"],
                "must_keep": ["m_addr_home"], "expected_residual_count": 0})
add("OSFORG-02", "把上个月那次出行规划会话的聊天记录都删掉。",
    [("m_trip_plan", "出行计划备忘"), ("m_trip_fav", "收藏的景点"), ("m_trip_hotel", "备选酒店"), ("m_meet_tpl", "会议纪要模板")],
    "session", {"target_session_id": "sess_trip_plan_last_m", "target_ids": ["m_trip_plan", "m_trip_fav", "m_trip_hotel"],
                "must_keep": ["m_meet_tpl"], "expected_residual_count": 0})
add("OSFORG-02", "删除昨天装修咨询会话里记下的联系人报价。",
    [("m_dec_quote_a", "装修公司甲报价"), ("m_dec_quote_b", "工长乙报价"), ("m_dec_brand", "瓷砖品牌笔记"), ("m_work_proj", "工作项目信息")],
    "session", {"target_session_id": "sess_decoration_yday", "target_ids": ["m_dec_quote_a", "m_dec_quote_b", "m_dec_brand"],
                "must_keep": ["m_work_proj"], "expected_residual_count": 0})
add("OSFORG-02", "清理上次搬家规划会话产生的清单和预约记录。",
    [("m_move_list", "搬家物品清单"), ("m_move_appt", "搬家公司预约"), ("m_move_note", "新居尺寸笔记"), ("m_fam_doc", "家庭医生电话")],
    "session", {"target_session_id": "sess_move_plan", "target_ids": ["m_move_list", "m_move_appt", "m_move_note"],
                "must_keep": ["m_fam_doc"], "expected_residual_count": 0})
add("OSFORG-02", "忘掉那次需求评审会话记录的所有待办。",
    [("m_req_todo", "需求评审待办"), ("m_req_open", "遗留问题清单"), ("m_req_verdict", "评审结论"), ("m_sprint", "迭代排期")],
    "session", {"target_session_id": "sess_req_review", "target_ids": ["m_req_todo", "m_req_open", "m_req_verdict"],
                "must_keep": ["m_sprint"], "expected_residual_count": 0})
add("OSFORG-02", "删除那次健康咨询会话里留下的全部记录。",
    [("m_health_symptom", "症状描述"), ("m_health_advice", "医生建议"), ("m_health_followup", "复查提醒"), ("m_coffee_taste", "咖啡口味偏好")],
    "session", {"target_session_id": "sess_health_query", "target_ids": ["m_health_symptom", "m_health_advice", "m_health_followup"],
                "must_keep": ["m_coffee_taste"], "expected_residual_count": 0})
add("OSFORG-02", "忘掉活动策划那个会话产生的草稿和预算。",
    [("m_evt_draft", "活动方案草稿"), ("m_evt_budget", "活动预算表"), ("m_evt_vendor", "候选供应商"), ("m_browser_home", "浏览器主页设置")],
    "session", {"target_session_id": "sess_evt_plan", "target_ids": ["m_evt_draft", "m_evt_budget", "m_evt_vendor"],
                "must_keep": ["m_browser_home"], "expected_residual_count": 0})
add("OSFORG-02", "把那次密码重置会话产生的临时验证码记录删掉。",
    [("m_pw_otp", "临时验证码"), ("m_pw_hint", "重置提示问题"), ("m_pw_time", "重置时间"), ("m_wallpaper", "桌面壁纸")],
    "session", {"target_session_id": "sess_pw_reset", "target_ids": ["m_pw_otp", "m_pw_hint", "m_pw_time"],
                "must_keep": ["m_wallpaper"], "expected_residual_count": 0})

# ---- OSFORG-03 topic 8 ----
add("OSFORG-03", "忘掉所有关于装修的记忆。",
    [("m_dec_budget", "装修预算"), ("m_dec_team", "施工队联系人"), ("m_dec_material", "材料清单"), ("m_addr_home", "家庭地址")],
    "topic", {"target_topic": "装修", "target_ids": ["m_dec_budget", "m_dec_team", "m_dec_material"],
              "must_keep": ["m_addr_home"], "expected_residual_count": 0})
add("OSFORG-03", "把我记的所有关于看牙的信息清掉。",
    [("m_dent_clinic", "口腔诊所"), ("m_dent_doc", "主治医生"), ("m_dent_appt", "复诊预约"), ("m_work_proj", "工作项目")],
    "topic", {"target_topic": "看牙", "target_ids": ["m_dent_clinic", "m_dent_doc", "m_dent_appt"],
              "must_keep": ["m_work_proj"], "expected_residual_count": 0})
add("OSFORG-03", "忘记所有关于上次购车的记忆。",
    [("m_car_model", "看的车型"), ("m_car_price", "报价单"), ("m_car_dealer", "销售联系方式"), ("m_commute", "通勤时长")],
    "topic", {"target_topic": "购车", "target_ids": ["m_car_model", "m_car_price", "m_car_dealer"],
              "must_keep": ["m_commute"], "expected_residual_count": 0})
add("OSFORG-03", "清理所有关于社保办理的记录。",
    [("m_ss_material", "社保材料清单"), ("m_ss_window", "办理窗口"), ("m_ss_status", "办理进度"), ("m_meet_tpl", "会议纪要模板")],
    "topic", {"target_topic": "社保办理", "target_ids": ["m_ss_material", "m_ss_window", "m_ss_status"],
              "must_keep": ["m_meet_tpl"], "expected_residual_count": 0})
add("OSFORG-03", "忘掉所有关于毕业论文的记忆。",
    [("m_thesis_title", "论文选题"), ("m_thesis_draft", "草稿版本"), ("m_thesis_refs", "参考文献"), ("m_sprint", "工作排期")],
    "topic", {"target_topic": "毕业论文", "target_ids": ["m_thesis_title", "m_thesis_draft", "m_thesis_refs"],
              "must_keep": ["m_sprint"], "expected_residual_count": 0})
add("OSFORG-03", "把所有关于减肥食谱的记录都忘掉。",
    [("m_diet_menu", "一周食谱"), ("m_diet_cal", "热量表"), ("m_diet_notes", "试做笔记"), ("m_theme_dark", "编辑器主题")],
    "topic", {"target_topic": "减肥食谱", "target_ids": ["m_diet_menu", "m_diet_cal", "m_diet_notes"],
              "must_keep": ["m_theme_dark"], "expected_residual_count": 0})
add("OSFORG-03", "忘记所有和旅游签证相关的记忆。",
    [("m_visa_docs", "签证材料"), ("m_visa_appt", "递签预约"), ("m_visa_sched", "出签时间"), ("m_cloud_acct", "云盘账号")],
    "topic", {"target_topic": "旅游签证", "target_ids": ["m_visa_docs", "m_visa_appt", "m_visa_sched"],
              "must_keep": ["m_cloud_acct"], "expected_residual_count": 0})
add("OSFORG-03", "忘掉所有关于旧公司项目的记录。",
    [("m_oldp_arch", "旧项目架构"), ("m_oldp_cred", "旧项目账号"), ("m_oldp_people", "旧同事分工"), ("m_browser_home", "浏览器主页")],
    "topic", {"target_topic": "旧公司项目", "target_ids": ["m_oldp_arch", "m_oldp_cred", "m_oldp_people"],
              "must_keep": ["m_browser_home"], "expected_residual_count": 0})

# ---- OSFORG-04 time_window 8 ----
add("OSFORG-04", "删除上周产生的所有记忆。",
    [("m_w_last_note", "上周随手记"), ("m_w_last_meet", "上周会议要点"), ("m_w_last_todo", "上周待办"), ("m_addr_home", "家庭地址")],
    "time_window", {"target_time_range": {"start": "2026-08-17", "end": "2026-08-23"},
                    "target_ids": ["m_w_last_note", "m_w_last_meet", "m_w_last_todo"],
                    "must_keep": ["m_addr_home"], "expected_residual_count": 0})
add("OSFORG-04", "忘掉六月之前记录的所有偏好设置。",
    [("m_old_pref_a", "旧版字体偏好"), ("m_old_pref_b", "旧版通知偏好"), ("m_old_pref_c", "旧版排序偏好"), ("m_new_pref", "当前主题偏好")],
    "time_window", {"target_time_range": {"start": "2025-01-01", "end": "2026-05-31"},
                    "target_ids": ["m_old_pref_a", "m_old_pref_b", "m_old_pref_c"],
                    "must_keep": ["m_new_pref"], "expected_residual_count": 0})
add("OSFORG-04", "删除今年一月到三月之间的提醒记录。",
    [("m_q1_alarm_a", "一月账单提醒"), ("m_q1_alarm_b", "二月体检提醒"), ("m_q1_alarm_c", "三月续费提醒"), ("m_q3_alarm", "九月考试提醒")],
    "time_window", {"target_time_range": {"start": "2026-01-01", "end": "2026-03-31"},
                    "target_ids": ["m_q1_alarm_a", "m_q1_alarm_b", "m_q1_alarm_c"],
                    "must_keep": ["m_q3_alarm"], "expected_residual_count": 0})
add("OSFORG-04", "忘掉这个月五号那天产生的所有临时记录。",
    [("m_d5_note", "五号随手备忘"), ("m_d5_photo", "五号截图存档"), ("m_d5_clip", "五号剪贴板"), ("m_week_meet", "本周例会提醒")],
    "time_window", {"target_time_range": {"start": "2026-08-05", "end": "2026-08-05"},
                    "target_ids": ["m_d5_note", "m_d5_photo", "m_d5_clip"],
                    "must_keep": ["m_week_meet"], "expected_residual_count": 0})
add("OSFORG-04", "删除上次出差那周的整个行程记忆。",
    [("m_biz_flight", "出差航班"), ("m_biz_hotel", "出差酒店"), ("m_biz_meet", "出差会见安排"), ("m_report_fmt", "周报格式偏好")],
    "time_window", {"target_time_range": {"start": "2026-08-10", "end": "2026-08-14"},
                    "target_ids": ["m_biz_flight", "m_biz_hotel", "m_biz_meet"],
                    "must_keep": ["m_report_fmt"], "expected_residual_count": 0})
add("OSFORG-04", "忘掉旧地址相关的记忆。",
    [("m_old_addr_work", "旧工作地址"), ("m_old_addr_home", "旧家庭地址"), ("m_old_addr_mail", "旧收件地址"), ("m_addr_new", "现住址")],
    "time_window", {"target_time_range": {"start": "2020-01-01", "end": "2025-12-31"},
                    "target_ids": ["m_old_addr_work", "m_old_addr_home", "m_old_addr_mail"],
                    "must_keep": ["m_addr_new"], "expected_residual_count": 0})
add("OSFORG-04", "删除试用期三个月期间保存的工作相关记忆。",
    [("m_try_task", "试用期任务记录"), ("m_try_fb", "试用期反馈"), ("m_try_login", "试用期内部账号"), ("m_now_skill", "当前技能偏好")],
    "time_window", {"target_time_range": {"start": "2026-03-01", "end": "2026-05-31"},
                    "target_ids": ["m_try_task", "m_try_fb", "m_try_login"],
                    "must_keep": ["m_now_skill"], "expected_residual_count": 0})
add("OSFORG-04", "忘掉上周五下午那两小时的调试记录。",
    [("m_dbg_pm", "上周五调试日志"), ("m_dbg_env", "临时环境变量"), ("m_dbg_pkg", "临时安装包"), ("m_theme_dark", "编辑器主题")],
    "time_window", {"target_time_range": {"start": "2026-08-21T14:00:00Z", "end": "2026-08-21T16:00:00Z"},
                    "target_ids": ["m_dbg_pm", "m_dbg_env", "m_dbg_pkg"],
                    "must_keep": ["m_theme_dark"], "expected_residual_count": 0})

# ---- OSFORG-05 restart 6 (checkpoints 含 after_restart) ----
add("OSFORG-05", "忘记开机自动启动音乐软件这条设置，重启后验证它不再自动启动。",
    [("m_autostart_music", "开机自动启动音乐软件"), ("m_autostart_notes", "开机自动打开笔记"), ("m_theme_dark", "编辑器深色主题")],
    "single_item", {"target_ids": ["m_autostart_music"], "must_keep": ["m_autostart_notes", "m_theme_dark"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")
add("OSFORG-05", "忘记新文件默认只读这条设置，重启后确认新文件可正常编辑。",
    [("m_ro_new", "新文件默认只读"), ("m_ro_ext", "只读扩展名单"), ("m_save_d", "默认保存目录")],
    "single_item", {"target_ids": ["m_ro_new"], "must_keep": ["m_ro_ext", "m_save_d"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")
add("OSFORG-05", "忘记窗口默认最大化这条偏好，重启后验证恢复默认大小。",
    [("m_win_max", "窗口默认最大化"), ("m_win_pos", "记住窗口位置"), ("m_win_scale", "界面缩放比例")],
    "single_item", {"target_ids": ["m_win_max"], "must_keep": ["m_win_pos", "m_win_scale"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")
add("OSFORG-05", "忘记命令行默认工作目录那条记忆，重启后确认回到默认目录。",
    [("m_shell_cwd", "命令行默认目录"), ("m_shell_alias", "自定义别名"), ("m_shell_theme", "命令行配色")],
    "single_item", {"target_ids": ["m_shell_cwd"], "must_keep": ["m_shell_alias", "m_shell_theme"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")
add("OSFORG-05", "忘记自动连接办公室网络这条记录，重启后验证它不自动连。",
    [("m_wifi_office", "自动连接办公室网络"), ("m_wifi_home", "自动连接家庭网络"), ("m_wifi_forget", "忽略的网络列表")],
    "single_item", {"target_ids": ["m_wifi_office"], "must_keep": ["m_wifi_home", "m_wifi_forget"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")
add("OSFORG-05", "忘记回收站上限 5G 这条设置，重启后验证回到默认上限。",
    [("m_rec_5g", "回收站上限五 G"), ("m_rec_days", "回收站保留天数"), ("m_rec_src", "回收站来源设备")],
    "single_item", {"target_ids": ["m_rec_5g"], "must_keep": ["m_rec_days", "m_rec_src"],
                    "checkpoints": ["immediate_query", "after_restart"], "expected_residual_count": 0}, cls="single_restart")

# ---- OSFORG-06 reindex 6 (checkpoints 含 after_full_reindex) ----
add("OSFORG-06", "忘记收藏夹里那个旧书签，全量重建索引后确认搜索不到它。",
    [("m_bm_old", "旧书签条目"), ("m_bm_new", "常用书签")],
    "single_item", {"target_ids": ["m_bm_old"], "must_keep": ["m_bm_new"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")
add("OSFORG-06", "忘掉自动纠错词表里的那个错词，重建索引后它不再被补全。",
    [("m_corr_wrong", "自定义纠错词"), ("m_corr_dict", "内置词典设置")],
    "single_item", {"target_ids": ["m_corr_wrong"], "must_keep": ["m_corr_dict"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")
add("OSFORG-06", "忘掉最近打开文件里那份合同记录，重建索引后不再出现。",
    [("m_recent_contract", "最近打开的合同文件"), ("m_recent_report", "最近打开的报告文件")],
    "single_item", {"target_ids": ["m_recent_contract"], "must_keep": ["m_recent_report"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")
add("OSFORG-06", "忘记剪贴板历史里那段文本，重建索引后检索不到。",
    [("m_clip_txt", "剪贴板历史某段文本"), ("m_clip_img", "剪贴板历史图片")],
    "single_item", {"target_ids": ["m_clip_txt"], "must_keep": ["m_clip_img"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")
add("OSFORG-06", "忘记全局搜索缓存里的那条路径，重建索引后不再命中。",
    [("m_cache_path", "全局搜索缓存路径"), ("m_cache_scope", "搜索范围设置")],
    "single_item", {"target_ids": ["m_cache_path"], "must_keep": ["m_cache_scope"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")
add("OSFORG-06", "忘记语音助手记住的那个称呼，重建后不再使用它。",
    [("m_va_nick", "语音助手自定义称呼"), ("m_va_wake", "唤醒词设置")],
    "single_item", {"target_ids": ["m_va_nick"], "must_keep": ["m_va_wake"],
                    "checkpoints": ["immediate_query", "after_full_reindex"], "expected_residual_count": 0}, cls="single_reindex")

# ---- OSFORG-07 ambiguous_selector negative 6 ----
add("OSFORG-07", "把那些都删了吧。",
    [("m_fam_doc", "家庭医生电话"), ("m_sprint", "迭代排期"), ("m_theme_dark", "编辑器主题")], None, {})
add("OSFORG-07", "之前那些乱七八糟的记录帮我清一清。",
    [("m_addr_home", "家庭地址"), ("m_work_proj", "工作项目"), ("m_report_fmt", "周报格式")], None, {})
add("OSFORG-07", "你记住的东西太多了，删掉点没用的。",
    [("m_cloud_acct", "云盘账号"), ("m_commute", "通勤时长"), ("m_sync_freq", "同步频率")], None, {})
add("OSFORG-07", "把昨天那些都忘了吧。",
    [("m_d5_note", "某天随手记"), ("m_d5_clip", "某天剪贴板"), ("m_week_meet", "本周例会提醒")], None, {})
add("OSFORG-07", "有些东西我不想让你记着，你看着删。",
    [("m_browser_home", "浏览器主页"), ("m_coffee_taste", "咖啡口味"), ("m_office_ext", "办公室分机")], None, {})
add("OSFORG-07", "记着的东西清一半就行。",
    [("m_meet_tpl", "会议纪要模板"), ("m_wallpaper", "桌面壁纸"), ("m_annual_check", "年度体检预约")], None, {})

# ---- OSFORG-08 full_reset 4 ----
add("OSFORG-08", "把我所有的记忆都清空，重置成刚安装时的状态。",
    [("m_pref_a", "已存偏好甲"), ("m_note_b", "历史笔记"), ("m_sess_c", "旧会话记录")],
    "full_reset", {"target_ids": ["m_pref_a", "m_note_b", "m_sess_c"], "must_keep": [],
                   "checkpoints": ["immediate_query"], "expected_residual_count": 0}, cls="full_reset")
add("OSFORG-08", "恢复出厂，所有偏好和记录全部删除。",
    [("m_pref_d", "界面偏好"), ("m_rule_e", "自动化规则"), ("m_mem_f", "个人记忆条目")],
    "full_reset", {"target_ids": ["m_pref_d", "m_rule_e", "m_mem_f"], "must_keep": [],
                   "checkpoints": ["immediate_query"], "expected_residual_count": 0}, cls="full_reset")
add("OSFORG-08", "把我记得的一切都忘掉，重新开始。",
    [("m_g", "收藏内容"), ("m_h", "设置记录"), ("m_i", "对话上下文")],
    "full_reset", {"target_ids": ["m_g", "m_h", "m_i"], "must_keep": [],
                   "checkpoints": ["immediate_query"], "expected_residual_count": 0}, cls="full_reset")
add("OSFORG-08", "全部记忆清掉，包括偏好、设置和会话。",
    [("m_j", "全部偏好"), ("m_k", "全部设置"), ("m_l", "全部会话")],
    "full_reset", {"target_ids": ["m_j", "m_k", "m_l"], "must_keep": [],
                   "checkpoints": ["immediate_query"], "expected_residual_count": 0}, cls="full_reset")

cnt = Counter(x["sid"] for x in S)
for k, v in PLANNED.items():
    assert cnt[k] == v, "planned mismatch %s: got %d want %d" % (k, cnt[k], v)
assert len(S) == 56, len(S)

lines = []
for i, s in enumerate(S, start=1):
    sid = "forg_d1_%04d" % i
    inv = [{"memory_ref": r, "subject": sub} for (r, sub) in s["inv"]]
    blind = {"forget_instruction": s["instr"]}
    if inv:
        blind["inventory_context"] = inv
    dm = {"scenario_spec_id": s["sid"], "scenario_family": FAMILY[s["sid"]],
          "candidate_event_refs": ["evt_forg_d1_%04d" % i]}
    if s["mode"] is None:
        dm["scenario_class"] = "ambiguous_selector_negative"
    else:
        dm["scenario_class"] = s["cls"] or s["mode"]
        dm["forget_mode"] = s["mode"]
        dm["checkpoints"] = s["design"].get("checkpoints", ["immediate_query"])
        dm["expected_residual_count"] = s["design"].get("expected_residual_count", 0)
        if "target_time_range" in s["design"]:
            dm["target_time_range"] = s["design"]["target_time_range"]
        if "target_topic" in s["design"]:
            dm["target_topic"] = s["design"]["target_topic"]
        if "target_session_id" in s["design"]:
            dm["target_session_id"] = s["design"]["target_session_id"]
        if "target_ids" in s["design"]:
            dm["target_ids"] = s["design"]["target_ids"]
        dm["must_keep"] = s["design"].get("must_keep", [])
    dm["generation"] = {"generation_id": "gen_forg_d1_20260906", "prompt_version": "P23-v4.1",
                        "seed": 20260906, "model": "deepseek-v4-flash", "source": "os_controlled_authored",
                        "source_file": "data/interim/d1_candidates_A_20260906/forgetting_candidates.jsonl"}
    rec = {"sample_id": sid, "task_type": "precise_forgetting", "language": "zh-CN",
           "dataset_version": "kylin_memory_candidate_v4.1", "dataset_stage": "candidate_only",
           "review_status": "candidate_only", "admission_status": "NOT_ADMISSION_APPROVED",
           "id_binding_status": "NON_PRODUCTION", "scenario_user_ref": "u_os_forg_d1_%04d" % i,
           "conversation_id": "conv_forg_d1_%04d" % i, "timestamp": t(i),
           "blind_visible": {"input": blind}, "design_metadata": dm}
    lines.append(json.dumps(rec, ensure_ascii=False))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("WROTE", len(lines), "->", OUT)
print("per-scenario:", dict(cnt))
