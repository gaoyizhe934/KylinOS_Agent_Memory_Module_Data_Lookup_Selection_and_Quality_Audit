# -*- coding: utf-8 -*-
"""Data-A D1 P20 Preference 候选工厂（os_controlled_authored, candidate_only）
按 scenario_specs/preference_scenarios.json planned_candidates 量产 98 条。
全部 NON_PRODUCTION；不写 human_decision/final_label；design 字段只在 design_metadata。
source: os_controlled_authored | prompt_version: P20-v4.1 | model: deepseek-v4-flash
生成 & 自检：2026-09-06 lyf-1213(Data-A)
"""
import json, os

OUT = r"C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_candidates_A_20260906\preference_candidates.jsonl"

# (scenario_id, scenario_class, step1_class, scope_or_None, msgs[])
# msgs: 1 条 -> user_message；多条 -> messages
P = []
def add(sid, cls, step1, scope, msgs):
    P.append({"sid": sid, "cls": cls, "step1": step1, "scope": scope, "msgs": msgs})

# ---- OSPREF-01 workflow 12 ----
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["以后每周报告都用要点，每条不超过两行。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["开会前先给我会议议程，当天结束就把纪要要点发我。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "global", ["以后所有安排类提醒都提前十分钟，别卡着时间才提醒。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["每周五下班前把当周已办清单整理好发我。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["每月最后一天给我一份本月支出小结，按类别列。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "global", ["以后默认先讲结论再讲过程，能短就短。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["每周一早上把上周数据汇总成一张表再发我。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "global", ["以后收到消息别只回收到两个字，直接给处理结论。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["我写代码的时候，你先把发现的 TODO 收集到一个清单，别逐条打断我。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "global", ["以后定时任务失败要立刻提醒我，不要静默重试。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "topic", ["每次出差前把行程单和酒店确认号整理到一页给我。"])
add("OSPREF-01", "explicit_persistent", "persistent_preference", "global", ["以后我所有文档的命名都按日期_主题来，别用新建文档一这种名字。"])

# ---- OSPREF-02 app_tool 12 ----
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["项目管理工具里所有标签都用中文。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["邮件客户端默认签名用工作签名，别用系统默认那个。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["日历里我建的日程都显示成忙碌，别显示具体内容。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["文件管理器用列表视图，图标调小一号。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["代码编辑器里缩进统一用两个空格。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["终端窗口背景用深色，字号设成十四。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["浏览器默认主页设成空白页，别放推荐新闻。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["截图工具的保存格式默认改成 PNG。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["通讯录里把我的常用联系人置顶。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["网盘上传失败时，把错误日志追加写到桌面那份报告里。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["记账软件里每笔记账自动沿用上一笔的分类，别每次问我。"])
add("OSPREF-02", "explicit_persistent_tool", "persistent_preference", "tool", ["音乐播放器里音频默认 1.2 倍速播放。"])

# ---- OSPREF-03 topic_style 12 ----
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["做周报时就用三段式：进展、问题、下周计划。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["写代码评审意见时按严重程度分条列，别逐行贴代码。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["整理会议纪要时把决定和待办单独列出来。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["处理发票报销时先按月份分类，再按类贴票据。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["做演示文稿时一页别超过三句话。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["写需求文档时先写背景，再写验收标准。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["回复客户邮件时先肯定对方，再给方案。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["做数据分析时先给结论，图表放最后。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["整理读书笔记时按主题建条目，别记流水账。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["写周例会要项时只列要讨论的，不写已经完成的。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["做故障复盘时按时间线写，别按责任归属写。"])
add("OSPREF-03", "explicit_persistent_topic", "persistent_preference", "topic", ["筛招聘简历时先按硬性条件过滤，再给我短名单。"])

# ---- OSPREF-04 time_window 10 ----
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["这个月每天上午十点提醒我喝水。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["项目上线前这两周，每天下午六点把构建状态发我。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["购物节期间我的购物清单有变化就随时同步给你记录。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["到月底前，每晚十点提醒我记账。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["这周之内我打开工作群都帮我静音，我在赶稿。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["出差这一周，酒店变更要第一时间通知我。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["假期这三天不要给我推任何工作消息。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["每月最后三天的结账周，提醒我先核对预算再付款。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["未来两周每晚七点给我推一次服务器日志摘要。"])
add("OSPREF-04", "temporary_preference", "temporary_preference", "time_window", ["考前这一个月，把学习计划的提醒提前到晚上八点。"])

# ---- OSPREF-05 implicit_repeated_behavior 10 (事件日志式行为证据, 无口头声明) ----
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "topic", ["（事件日志）8月12日、8月14日、8月15日、8月18日，发来的邮件摘要都被手动删除正文、只保留要点。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "topic", ["（事件日志）最近三份周报生成后，都被手动改成只保留三行结论。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "tool", ["（事件日志）过去一周，代码编辑器三次被切回深色主题。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "global", ["（事件日志）新建的每个提醒，提醒方式都被手动改成仅声音。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "topic", ["（事件日志）每次导出的 PDF，存盘前都被手动把字号调大两号。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "global", ["（事件日志）这几周每次提出删除文件前，都会先补一句要求确认的话。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "tool", ["（事件日志）每个周五都会手动触发一次全量备份。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "global", ["（事件日志）每次查询天气后，温度单位都被手动切回摄氏度。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "tool", ["（事件日志）每次保存截图前，都被手动裁掉顶部状态栏区域。"])
add("OSPREF-05", "implicit_repeated_behavior", "implicit_repeated_behavior", "tool", ["（事件日志）每次代码提交前，自动生成的提交信息都被改写为“feat: 一句话”格式。"])

# ---- OSPREF-06 contradictory_preference 8 (双消息) ----
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["以后回复都先用表格总结。", "算了，改成普通段落就好，不要表格了。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["以后提醒都提前半小时。", "提醒改提前五分钟，半小时太久。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["以后所有数字保留两位小数。", "数字别保留两位了，取整就行。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["以后每周报告都用长文详述。", "周报改成只写要点，不写长文。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["默认用英文回复我。", "还是改回中文吧，英文看得费劲。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["邮件签名用简洁版。", "签名换成完整版，带上职位和电话。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["以后新任务先自动建好文件夹。", "不要自动建了，我自己建。"])
add("OSPREF-06", "contradictory_preference", "contradictory_preference", "global", ["我让你核对时直接说没问题就行。", "核对还是要逐条列出来，别只说没问题。"])

# ---- OSPREF-07 withdrawal 8 (双消息) ----
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["以后备份都自动做。", "把自动备份关了，我自己手动备份。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["每天上午提醒我起来站一下。", "站立提醒不要了，把这条取消掉。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["回复格式都用编号列表。", "编号列表这个格式撤掉，用普通段落。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["把公司邮箱和个人邮箱合并成一份通知。", "取消合并，两个邮箱分开通知。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["深夜的消息也照常推给我。", "免打扰还是开着，深夜不要推。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["以后任何删除都先放进回收站。", "回收站那套不要了，彻底删除前问我一次就行。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["日历里我自己的会议都用橙色标记。", "橙色会议标记撤销，恢复默认颜色。"])
add("OSPREF-07", "withdrawal", "withdrawal", "global", ["搜索结果默认按时间排序。", "按时间排序改回去，默认还是按相关度。"])

# ---- OSPREF-08 sensitive/non-storable 8 (负例, 无 scope) ----
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["帮我记一下我网银的登录密码，省得每次自己输。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["记住我体检报告上的诊断结论，以后复诊直接报给医生。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["记着我病历里那条诊断，别删。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["记住我的社保查询密码，每月帮我查一次余额。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["把我孩子的出生证明编号存下来。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["记住我这张卡每月的工资具体数字，方便我比价。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["把这次心理咨询的时间和内容要点记下来。"])
add("OSPREF-08", "sensitive_non_storable", "non_preference", None, ["把家里监控的访问密码记住，方便我随时调看。"])

# ---- OSPREF-09 task_constraint_boundary 10 (负例, 无 scope) ----
add("OSPREF-09", "task_constraint", "task_constraint", None, ["这次就把报告用英文写。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["这封邮件用正式一点的称呼。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["今天这个文件放到 C:\\temp 这个简单路径下。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["这一版演示文稿先别加动画。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["这次回复控制在三行以内。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["这家餐厅帮我挑评分高的，就这一回。"])
add("OSPREF-09", "task_constraint", "task_constraint", None, ["本次会议纪要先别抄送领导。"])
add("OSPREF-09", "ordinary_request", "ordinary_request", None, ["帮我把这份文档转成 PDF。"])
add("OSPREF-09", "ordinary_request", "ordinary_request", None, ["把这段话翻译成日语。"])
add("OSPREF-09", "ordinary_request", "ordinary_request", None, ["现在别放歌单，安静一会儿。"])

# ---- OSPREF-10 session 8 ----
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["这次会话都用暗色主题。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["接下来的对话都用英文。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["这个会话里我叫你小琪，别叫错。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["本次会话里路径都显示完整，别用省略号。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["这次对话先别保存记录。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["这个会话里提到的都是临时讨论，不用记下来。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["本次会话生成的文件先放桌面临时文件夹。"])
add("OSPREF-10", "session_scope", "temporary_preference", "session", ["这个会话里你的回复都加编号。"])

# ---- planned counts ----
PLANNED = {"OSPREF-01": 12, "OSPREF-02": 12, "OSPREF-03": 12, "OSPREF-04": 10, "OSPREF-05": 10,
           "OSPREF-06": 8, "OSPREF-07": 8, "OSPREF-08": 8, "OSPREF-09": 10, "OSPREF-10": 8}
from collections import Counter
cnt = Counter(x["sid"] for x in P)
for k, v in PLANNED.items():
    assert cnt[k] == v, "planned mismatch %s: got %d want %d" % (k, cnt[k], v)
assert len(P) == 98, len(P)

def iso(i):
    hh = 8 + (i % 10)
    mm = (i * 7) % 60
    return "2026-08-2%dT%02d:%02d:00.000Z" % (1 + (i // 24) % 8, hh, mm)

FAMILY = {"OSPREF-01": "os_pref_workflow", "OSPREF-02": "os_pref_app_tool", "OSPREF-03": "os_pref_topic_style",
          "OSPREF-04": "os_pref_time_window", "OSPREF-05": "os_pref_global_rule", "OSPREF-06": "os_pref_contradict",
          "OSPREF-07": "os_pref_withdraw", "OSPREF-08": "os_pref_sensitive", "OSPREF-09": "os_pref_task_constraint",
          "OSPREF-10": "os_pref_session"}

lines = []
for i, s in enumerate(P, start=1):
    sid = "pref_d1_%04d" % i
    if len(s["msgs"]) == 1:
        blind_input = {"user_message": s["msgs"][0]}
    else:
        blind_input = {"messages": s["msgs"]}
    dm = {
        "scenario_spec_id": s["sid"],
        "scenario_family": FAMILY[s["sid"]],
        "scenario_class": s["cls"],
        "task_semantic_class": s["step1"],
        "candidate_event_refs": ["evt_pref_d1_%04d" % i],
    }
    if s["scope"] is not None:
        dm["design_scope_target"] = s["scope"]
    dm["generation"] = {
        "generation_id": "gen_pref_d1_20260906",
        "prompt_version": "P20-v4.1",
        "seed": 20260906,
        "model": "deepseek-v4-flash",
        "source": "os_controlled_authored",
        "source_file": "data/interim/d1_candidates_A_20260906/preference_candidates.jsonl",
    }
    rec = {
        "sample_id": sid, "task_type": "preference_extraction", "language": "zh-CN",
        "dataset_version": "kylin_memory_candidate_v4.1", "dataset_stage": "candidate_only",
        "review_status": "candidate_only", "admission_status": "NOT_ADMISSION_APPROVED",
        "id_binding_status": "NON_PRODUCTION", "scenario_user_ref": "u_os_pref_d1_%04d" % i,
        "conversation_id": "conv_pref_d1_%04d" % i, "timestamp": iso(i),
        "blind_visible": {"input": blind_input}, "design_metadata": dm,
    }
    lines.append(json.dumps(rec, ensure_ascii=False))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("WROTE", len(lines), "->", OUT)
print("per-scenario:", dict(cnt))
