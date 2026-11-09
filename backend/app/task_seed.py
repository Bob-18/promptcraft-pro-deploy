from .config import is_external_llm_allowed
from .llm_client import LLMError, chat_json
from .roles import get_role


def generate_task_seed(payload):
    rule_result = generate_task_seed_by_rules(payload)
    if not is_external_llm_allowed(payload):
        return rule_result

    try:
        llm_result = generate_task_seed_by_llm(payload, rule_result)
        llm_result["source"] = "DeepSeek"
        llm_result["fallback_used"] = False
        return llm_result
    except LLMError as exc:
        rule_result["source"] = "规则兜底"
        rule_result["fallback_used"] = True
        rule_result["llm_error"] = str(exc)[:180]
        return rule_result


def generate_task_seed_by_rules(payload):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    position = payload.get("specific_position") or role["label"]
    context = _clean(payload.get("work_context"))
    ai_level = payload.get("ai_skill_level", "初级")
    role_label = role["label"]
    learner_profile = payload.get("_learning_profile") or {}
    historical_focus = learner_profile.get("next_focus") if learner_profile.get("history_used") else ""

    scene = context.rstrip("。；;，, ") or role["tasks"][0]
    templates = {
        "marketing_manager": f"请围绕“{scene}”，为{position}生成一项市场推广训练任务，要求明确目标客户、产品卖点、宣传渠道、输出格式和事实核验要求。",
        "industrial_marketing": f"请围绕“{scene}”，为{position}生成一项工业品短视频训练任务，要求明确目标客户、应用场景、公开资料、平台时长、行动入口和事实核验边界。",
        "finance_analyst": f"请围绕“{scene}”，为{position}生成一项财务分析训练任务，要求明确公司资料、分析周期、核心指标、风险维度和合规边界。",
        "backend_developer": f"请围绕“{scene}”，为{position}生成一项代码审查训练任务，要求明确代码片段、业务背景、审查维度、安全要求和期望输出格式。",
        "admin_specialist": f"请围绕“{scene}”，为{position}生成一项行政办公训练任务，要求明确宣传/通知/纪要对象、资料来源、输出形式和待确认信息。",
        "product_manager": f"请围绕“{scene}”，为{position}生成一项产品需求训练任务，要求明确业务目标、用户反馈、约束条件、优先级标准和验证指标。",
        "smart_manufacturing": f"请围绕“{scene}”，为{position}生成一项智能制造训练任务，要求明确行业、设备或系统现状、典型场景、数据资料、风险边界和分阶测试要求。",
        "industrial_internet": f"请围绕“{scene}”，为{position}生成一项工业互联网运维训练任务，要求明确告警日志、设备状态、影响范围、历史处置记录和人工复核边界。",
    }

    original_task = templates.get(role_id, templates["marketing_manager"])
    if historical_focus:
        original_task += f" 本题重点训练你过去较薄弱的“{historical_focus}”，请在作答中明确体现。"
    return {
        "agent": "原始题目生成 Agent",
        "role": role_label,
        "specific_position": position,
        "ai_skill_level": ai_level,
        "original_task": original_task,
        "rationale": "已根据岗位画像和工作背景生成一条可用于训练的原始任务。",
        "personalization_basis": f"历史薄弱点：{historical_focus}" if historical_focus else "岗位画像与工作背景",
        "missing_info": ["真实资料链接", "业务数据", "输出格式细节"],
        "source": "规则生成",
        "fallback_used": False,
    }


def generate_task_seed_by_llm(payload, rule_result):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    position = payload.get("specific_position") or role["label"]
    messages = [
        {
            "role": "system",
            "content": (
                "你是智训工坊的原始题目生成 Agent。用户可能没有现成任务，"
                "你需要根据岗位、公司/部门背景和日常工作，生成一条适合训练的大模型原始任务。"
                "任务要像真实职场问题，但不能编造具体公司机密、客户数据或未提供的事实。"
                "必须只输出 JSON，不要输出 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"岗位方向：{role['label']}\n"
                f"具体职位：{position}\n"
                f"工作年限：{payload.get('experience_years', '未填写')}\n"
                f"AI 水平：{payload.get('ai_skill_level', '初级')}\n"
                f"学历背景：{payload.get('education_background', '未填写')}\n"
                f"基础测评分：{payload.get('theory_test_score', '未填写')}\n"
                f"公司/部门/日常任务背景：{_clean(payload.get('work_context')) or '未填写'}\n\n"
                "请输出 JSON，字段必须包括：\n"
                "{\n"
                '  "original_task": "一条用户可以直接放入实训输入框的原始训练任务",\n'
                '  "rationale": "为什么这道题适合该岗位和该用户",\n'
                '  "missing_info": ["后续需要用户补充的信息1"]\n'
                "}\n"
                "要求：original_task 不要太完美，要保留训练空间；但必须贴合岗位真实工作。"
                "必须包含任务对象、任务方向和至少一个质量或风险约束。"
            ),
        },
    ]
    raw = chat_json(messages, temperature=0.45, timeout=16)
    original_task = str(raw.get("original_task") or rule_result["original_task"]).strip()
    rationale = str(raw.get("rationale") or rule_result["rationale"]).strip()
    missing_info = _as_list(raw.get("missing_info"), rule_result["missing_info"], 5)
    return {
        "agent": "原始题目生成 Agent",
        "role": role["label"],
        "specific_position": position,
        "ai_skill_level": payload.get("ai_skill_level", "初级"),
        "original_task": original_task,
        "rationale": rationale,
        "missing_info": missing_info,
    }


def _clean(value):
    return str(value or "").strip()


def _as_list(value, fallback, limit):
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    return cleaned[:limit] or fallback[:limit]
