from ..config import is_external_llm_allowed
from ..llm_client import LLMError, chat_json
from ..roles import get_role


def feedback(payload, diagnosis, review):
    rule_result = feedback_by_rules(payload, diagnosis, review)
    if not is_external_llm_allowed(payload):
        return rule_result

    try:
        llm_result = feedback_by_llm(payload, diagnosis, review, rule_result)
        llm_result["source"] = "DeepSeek"
        llm_result["fallback_used"] = False
        return llm_result
    except LLMError as exc:
        rule_result["source"] = "规则兜底"
        rule_result["fallback_used"] = True
        rule_result["llm_error"] = str(exc)[:180]
        return rule_result


def feedback_by_rules(payload, diagnosis, review):
    score = review["score"]
    resource_risks = review.get("resource_risks", review.get("risks", []))
    target_findings = review.get("target_findings", [])
    severe_target_risk = any(
        keyword in finding
        for finding in target_findings
        for keyword in ["保证成交", "全部产品都通过认证", "零风险", "伪造", "绕过"]
    )
    clarity = diagnosis["task_clarity"]
    theory_score = _as_int(payload.get("theory_test_score"), 65)
    experience = _as_int(payload.get("experience_years"), 1)
    ai_score = {"初级": 42, "中级": 68, "高级": 86}.get(payload.get("ai_skill_level"), 50)
    education_score = {"未提供": 65, "大专": 58, "本科": 68, "硕士": 78, "博士": 86}.get(payload.get("education_background"), 65)
    experience_score = min(92, 45 + experience * 8)
    baseline = round(theory_score * 0.4 + ai_score * 0.25 + experience_score * 0.2 + education_score * 0.15)

    if clarity == "低" or score < 75 or baseline < 60 or severe_target_risk:
        level = "基础巩固"
        next_task = "降维解释：先练习如何补全任务目标、背景、分析维度和输出格式。"
        micro_goals = ["补全任务目标、背景资料、分析维度和输出格式。", "把模糊指令改写为可执行的岗位提示词。"]
        coach_feedback = "当前训练重点是把任务说清楚，再进入正式生成。"
        blind_spots = ["任务目标表达不完整", "资料来源意识不足", "输出格式约束缺失"]
        learning_path = ["补全任务信息", "改写岗位提示词", "完成基础分阶题", "再次审核输出"]
    elif score < 88 or baseline < 78 or target_findings:
        level = "专项提升"
        next_task = "补充练习：围绕事实核验、引用来源和待验证假设做专项训练。"
        micro_goals = ["为关键结论补充资料来源。", "把无法确认的信息标注为待验证假设。"]
        coach_feedback = "已经具备基础提示词结构，下一步要加强证据链和复核意识。"
        blind_spots = ["关键结论证据链不足", "待验证假设标注不充分", "人工复核边界不够明确"]
        learning_path = ["补齐证据来源", "练习结果审核", "完成专项测试", "进入岗位实战"]
    else:
        level = "进阶挑战"
        next_task = "进阶任务：基于真实资料生成带证据链的岗位成果，并由审核 Agent 复核。"
        micro_goals = ["使用真实资料完成岗位成果。", "让审核 Agent 对结论、风险和合规边界进行复核。"]
        coach_feedback = "任务表达较完整，可以进入更接近真实工作的综合训练。"
        blind_spots = ["复杂任务拆解深度仍可提高", "跨资料交叉验证能力可继续强化"]
        learning_path = ["引入真实资料", "生成岗位成果", "交叉验证结论", "完成进阶挑战"]

    resource_match_curve = _build_resource_curve(theory_score, score, clarity)
    learner_profile = payload.get("_learning_profile") or {}
    historical_focus = learner_profile.get("next_focus")
    if learner_profile.get("history_used") and historical_focus:
        blind_spots = list(dict.fromkeys([historical_focus, *blind_spots]))[:5]
        micro_goals = list(dict.fromkeys([f"针对历史薄弱点“{historical_focus}”完成一次专项修改。", *micro_goals]))[:4]
        coach_feedback = f"系统已读取 {learner_profile.get('attempts', 0)} 次历史训练；{coach_feedback}"
        next_task = f"历史专项：围绕“{historical_focus}”完成本轮任务后，再进入{level}。"

    return {
        "agent": "反馈迭代 Agent",
        "training_level": level,
        "mastery": {
            "任务表达": 70 if clarity == "低" else 84,
            "提示词结构": 78 if score < 85 else 88,
            "工作流拆解": 76,
            "事实核验": 66 if resource_risks else 82,
            "合规使用": 80,
        },
        "next_task": next_task,
        "micro_goals": micro_goals,
        "coach_feedback": coach_feedback,
        "blind_spots": blind_spots,
        "resource_match_curve": resource_match_curve,
        "learning_path": learning_path,
        "profile_baseline": baseline,
        "history_used": learner_profile.get("history_used", False),
        "historical_focus": historical_focus or "",
        "summary": f"建议进入{level}阶段：{next_task}",
        "source": "规则反馈",
        "fallback_used": False,
    }


def feedback_by_llm(payload, diagnosis, review, rule_result):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    position = payload.get("specific_position", role["label"])
    task = payload.get("task", "")
    messages = [
        {
            "role": "system",
            "content": (
                "你是智训工坊的反馈迭代 Agent，负责根据用户任务表现、职业诊断和质量审核结果，"
                "生成下一轮个性化训练路径。你的输出要像企业培训教练，明确、可执行、可量化。"
                "必须只输出 JSON，不要输出 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"岗位：{role['label']}\n"
                f"具体职位：{position}\n"
                f"岗位能力重点：{'、'.join(role['skill_focus'])}\n"
                f"学历背景：{payload.get('education_background', '未填写')}\n"
                f"理论测试分：{payload.get('theory_test_score', '未填写')}\n"
                f"用户任务：{task}\n"
                f"任务清晰度：{diagnosis.get('task_clarity', '')}\n"
                f"缺失信息：{'、'.join(diagnosis.get('missing_info', []))}\n"
                f"诊断总结：{diagnosis.get('summary', '')}\n\n"
                f"审核评分：{review.get('score')}/100\n"
                f"审核风险：{'；'.join(review.get('risks', []))}\n"
                f"审核建议：{'；'.join(review.get('suggestions', []))}\n\n"
                "请输出 JSON，字段必须包括：\n"
                "{\n"
                '  "training_level": "基础巩固/专项提升/进阶挑战",\n'
                '  "mastery": {"任务表达": 0到100, "提示词结构": 0到100, "工作流拆解": 0到100, "事实核验": 0到100, "合规使用": 0到100},\n'
                '  "next_task": "下一轮训练任务",\n'
                '  "micro_goals": ["小目标1", "小目标2"],\n'
                '  "blind_spots": ["知识盲区1"],\n'
                '  "resource_match_curve": [{"stage": "基础讲义", "difficulty": 40, "match": 80}],\n'
                '  "learning_path": ["路径节点1", "路径节点2"],\n'
                '  "coach_feedback": "给用户的一段简短反馈",\n'
                '  "summary": "一句话总结训练阶段"\n'
                "}\n"
                "要求：training_level 必须三选一；mastery 五项必须都是整数；"
                "next_task 要和岗位强相关，不能泛泛而谈；micro_goals 2 到 4 项。"
            ),
        },
    ]
    raw = chat_json(messages, temperature=0.35, timeout=18)

    training_level = raw.get("training_level", rule_result["training_level"])
    if training_level not in {"基础巩固", "专项提升", "进阶挑战"}:
        training_level = rule_result["training_level"]

    mastery = _normalize_mastery(raw.get("mastery"), rule_result["mastery"])
    next_task = str(raw.get("next_task") or rule_result["next_task"]).strip()
    micro_goals = _as_short_list(
        raw.get("micro_goals"),
        ["补全任务目标、资料来源、分析维度和输出格式。", "对关键结论标注事实依据或待验证。"],
        4,
        2,
    )
    coach_feedback = str(raw.get("coach_feedback") or "建议按下一轮训练任务继续巩固岗位化提示词能力。").strip()
    summary = str(raw.get("summary") or f"建议进入{training_level}阶段：{next_task}").strip()
    blind_spots = _as_short_list(raw.get("blind_spots"), rule_result["blind_spots"], 5, 1)
    resource_match_curve = _normalize_curve(raw.get("resource_match_curve"), rule_result["resource_match_curve"])
    learning_path = _as_short_list(raw.get("learning_path"), rule_result["learning_path"], 5, 3)

    return {
        "agent": "反馈迭代 Agent",
        "training_level": training_level,
        "mastery": mastery,
        "next_task": next_task,
        "micro_goals": micro_goals,
        "blind_spots": blind_spots,
        "resource_match_curve": resource_match_curve,
        "learning_path": learning_path,
        "coach_feedback": coach_feedback,
        "summary": summary,
    }


def _normalize_mastery(value, fallback):
    required = ["任务表达", "提示词结构", "工作流拆解", "事实核验", "合规使用"]
    if not isinstance(value, dict):
        return fallback
    result = {}
    for key in required:
        try:
            result[key] = min(100, max(0, int(value.get(key))))
        except (TypeError, ValueError):
            result[key] = fallback.get(key, 70)
    return result


def _as_short_list(value, fallback, limit, minimum=1):
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    if len(cleaned) < minimum:
        return fallback[:limit]
    return cleaned[:limit]


def _as_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _build_resource_curve(theory_score, review_score, clarity):
    base_match = 88 if clarity == "低" else 78
    practice_match = 72 if clarity == "低" else 86
    test_match = 64 if theory_score < 65 else min(90, review_score)
    return [
        {"stage": "基础讲义", "difficulty": 45 if theory_score < 70 else 55, "match": base_match},
        {"stage": "实操指南", "difficulty": 58 if clarity == "低" else 70, "match": practice_match},
        {"stage": "分阶测试", "difficulty": 68 if review_score < 85 else 82, "match": test_match},
    ]


def _normalize_curve(value, fallback):
    if not isinstance(value, list):
        return fallback
    cleaned = []
    for item in value[:4]:
        if not isinstance(item, dict):
            continue
        stage = str(item.get("stage") or "").strip()
        if not stage:
            continue
        cleaned.append(
            {
                "stage": stage[:12],
                "difficulty": min(100, max(0, _as_int(item.get("difficulty"), 60))),
                "match": min(100, max(0, _as_int(item.get("match"), 75))),
            }
        )
    return cleaned or fallback
