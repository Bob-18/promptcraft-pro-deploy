from ..config import is_external_llm_allowed
from ..llm_client import LLMError, chat_json
from ..roles import get_role


REQUIRED_HINTS = {
    "marketing_manager": ["竞品名称", "分析维度", "报告风格", "输出格式", "资料来源"],
    "industrial_marketing": ["目标客户", "应用场景", "公开资料", "平台与时长", "行动入口", "事实边界"],
    "finance_analyst": ["公司名称", "财报资料", "分析周期", "估值或风险维度", "合规边界"],
    "backend_developer": ["代码片段", "编程语言", "业务上下文", "性能或安全要求", "期望输出格式"],
    "admin_specialist": ["会议原文", "参会人", "会议主题", "负责人", "截止时间"],
    "product_manager": ["业务目标", "用户反馈", "约束条件", "优先级标准", "验证指标"],
    "smart_manufacturing": ["报警记录", "传感器数据", "设备状态", "工艺参数", "安全边界"],
    "industrial_internet": ["告警日志", "设备状态", "影响范围", "历史处置记录", "运维优先级"],
}


def diagnose(payload, knowledge):
    rule_result = diagnose_by_rules(payload, knowledge)
    if not is_external_llm_allowed(payload):
        return rule_result

    try:
        llm_result = diagnose_by_llm(payload, knowledge, rule_result)
        llm_result["source"] = "DeepSeek"
        llm_result["fallback_used"] = False
        return llm_result
    except LLMError as exc:
        rule_result["source"] = "规则兜底"
        rule_result["fallback_used"] = True
        rule_result["llm_error"] = str(exc)[:180]
        return rule_result


def diagnose_by_rules(payload, knowledge):
    role_id = payload.get("role_id", "marketing_manager")
    task = payload.get("task", "").strip()
    experience = payload.get("experience_years", 3)
    ai_level = payload.get("ai_skill_level", "初级")
    education = payload.get("education_background", "未填写")
    theory_score = payload.get("theory_test_score", None)
    position = payload.get("specific_position", "")
    role = get_role(role_id)

    required = REQUIRED_HINTS.get(role_id, REQUIRED_HINTS["marketing_manager"])
    missing = [item for item in required if not _task_mentions(task, item)]
    if len(task) < 18:
        clarity = "低"
        next_action = "动态追问"
    elif len(missing) >= 3:
        clarity = "中"
        next_action = "补充约束后生成"
    else:
        clarity = "高"
        next_action = "生成训练资源"

    return {
        "agent": "职业诊断 Agent",
        "role": role["label"],
        "specific_position": position or role["label"],
        "experience_years": experience,
        "ai_skill_level": ai_level,
        "education_background": education,
        "theory_test_score": theory_score,
        "task_clarity": clarity,
        "missing_info": missing[:5],
        "skill_gap": role["skill_focus"],
        "matched_sources": [item["source"] for item in knowledge["sources"]],
        "next_action": next_action,
        "summary": f"{role['label']}当前任务为岗位实训任务，主要训练{role['skill_focus'][0]}、{role['skill_focus'][1]}和{role['skill_focus'][2]}。",
        "source": "规则诊断",
        "fallback_used": False,
    }


def diagnose_by_llm(payload, knowledge, rule_result):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    task = payload.get("task", "").strip()
    source_names = [item["source"] for item in knowledge["sources"]]
    knowledge_excerpt = "\n\n".join(
        f"【{item['source']}】\n{item['content'][:900]}" for item in knowledge["sources"]
    )
    messages = [
        {
            "role": "system",
            "content": (
                "你是智训工坊的职业诊断 Agent。你的任务是分析职场用户的大模型任务输入，"
                "判断任务清晰度、缺失信息、技能短板和下一步训练动作。"
                "必须只输出 JSON，不要输出 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"岗位：{role['label']}\n"
                f"具体职位：{payload.get('specific_position', role['label'])}\n"
                f"工作年限：{payload.get('experience_years', 3)}\n"
                f"AI 使用水平：{payload.get('ai_skill_level', '初级')}\n"
                f"学历背景：{payload.get('education_background', '未填写')}\n"
                f"理论测试分：{payload.get('theory_test_score', '未填写')}\n"
                f"用户任务：{task}\n\n"
                f"岗位知识库片段：\n{knowledge_excerpt}\n\n"
                "请输出 JSON，字段必须包括：\n"
                "{\n"
                '  "task_clarity": "低/中/高",\n'
                '  "missing_info": ["缺失信息1"],\n'
                '  "skill_gap": ["能力短板1"],\n'
                '  "next_action": "动态追问/补充约束后生成/生成训练资源",\n'
                '  "summary": "一句话诊断总结"\n'
                "}\n"
                "要求：missing_info 不超过 5 项；skill_gap 不超过 4 项；不要编造用户没有提供的事实。"
            ),
        },
    ]
    raw = chat_json(messages)

    task_clarity = raw.get("task_clarity", rule_result["task_clarity"])
    if task_clarity not in {"低", "中", "高"}:
        task_clarity = rule_result["task_clarity"]

    next_action = raw.get("next_action", rule_result["next_action"])
    if next_action not in {"动态追问", "补充约束后生成", "生成训练资源"}:
        next_action = rule_result["next_action"]

    missing_info = _as_short_list(raw.get("missing_info"), rule_result["missing_info"], 5)
    skill_gap = _as_short_list(raw.get("skill_gap"), rule_result["skill_gap"], 4)
    summary = raw.get("summary") or rule_result["summary"]

    return {
        "agent": "职业诊断 Agent",
        "role": role["label"],
        "specific_position": payload.get("specific_position", role["label"]),
        "experience_years": payload.get("experience_years", 3),
        "ai_skill_level": payload.get("ai_skill_level", "初级"),
        "education_background": payload.get("education_background", "未填写"),
        "theory_test_score": payload.get("theory_test_score", None),
        "task_clarity": task_clarity,
        "missing_info": missing_info,
        "skill_gap": skill_gap,
        "matched_sources": source_names,
        "next_action": next_action,
        "summary": summary,
    }


def _as_short_list(value, fallback, limit):
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    return cleaned[:limit] or fallback[:limit]


def _task_mentions(task, hint):
    aliases = {
        "竞品名称": ["A 产品", "B 产品", "竞品", "产品"],
        "目标客户": ["老板", "采购", "客户", "技术决策", "目标受众"],
        "应用场景": ["食品", "制药", "灭菌", "CIP", "清洗", "应用场景"],
        "公开资料": ["公开", "资料", "来源", "产品页", "展会", "报道"],
        "平台与时长": ["抖音", "快手", "视频号", "B站", "小红书", "秒", "平台"],
        "行动入口": ["私信", "咨询", "选型", "获取", "提交工况", "行动"],
        "事实边界": ["不得编造", "待核验", "公开信息不足", "来源", "人工复核"],
        "分析维度": ["维度", "体验", "风险", "结构", "功能"],
        "报告风格": ["风格", "管理层", "麦肯锡", "摘要"],
        "输出格式": ["输出", "表格", "报告", "清单"],
        "资料来源": ["资料", "数据", "来源", "截图", "评论"],
        "公司名称": ["公司", "企业"],
        "财报资料": ["财报", "收入", "利润", "现金流"],
        "代码片段": ["代码", "接口", "函数"],
        "会议原文": ["会议", "记录", "纪要"],
        "业务目标": ["目标", "业务", "增长"],
        "报警记录": ["报警", "告警", "报警代码", "异常"],
        "传感器数据": ["传感器", "温度", "压力", "振动", "电流", "数据"],
        "设备状态": ["设备", "在线", "状态", "运行"],
        "工艺参数": ["工艺", "参数", "节拍", "良品率"],
        "安全边界": ["安全", "风险", "复核"],
        "告警日志": ["告警", "日志", "平台", "触发"],
        "影响范围": ["影响", "范围", "产线", "车间"],
        "历史处置记录": ["历史", "处置", "记录"],
        "运维优先级": ["优先级", "紧急", "处置"],
    }
    return any(alias in task for alias in aliases.get(hint, [hint]))
