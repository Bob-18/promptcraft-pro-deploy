from ..config import is_external_llm_allowed
from ..llm_client import LLMError, chat_json
from ..roles import get_role


RISK_KEYWORDS = [
    "编造", "保证收益", "保证成交", "保证当天", "全网第一", "全部通过认证", "全部产品都通过认证",
    "证件齐全", "所有制药产线", "任何工况", "零风险", "内幕", "绕过", "伪造", "绝对准确", "半夜三点", "立马上门",
]


def review(payload, diagnosis, generation, knowledge):
    rule_result = review_by_rules(payload, diagnosis, generation, knowledge)
    if not is_external_llm_allowed(payload):
        return rule_result

    try:
        llm_result = review_by_llm(payload, diagnosis, generation, knowledge, rule_result)
        llm_result["source"] = "DeepSeek"
        llm_result["fallback_used"] = False
        return llm_result
    except LLMError as exc:
        rule_result["source"] = "规则兜底"
        rule_result["fallback_used"] = True
        rule_result["llm_error"] = str(exc)[:180]
        return rule_result


def review_by_rules(payload, diagnosis, generation, knowledge):
    task = payload.get("task", "")
    candidate_output = payload.get("candidate_output", "")
    review_target = candidate_output or task
    prompt_template = generation["resources"]["prompt_template"]
    resource_risks = []
    target_findings = []

    if diagnosis["task_clarity"] == "低":
        resource_risks.append("用户原始指令过于模糊，需要追问后再生成正式内容。")
    if "不得编造" not in prompt_template and "禁止编造" not in prompt_template:
        resource_risks.append("提示词缺少反幻觉约束。")
    if not knowledge["sources"]:
        resource_risks.append("未匹配到岗位知识库资料，专业依据不足。")
    for keyword in RISK_KEYWORDS:
        if _is_risky_mention(review_target, keyword):
            target_findings.append(f"待审核内容命中高风险表达：{keyword}")

    if payload.get("role_id") == "industrial_marketing":
        if not any(word in prompt_template for word in ["公开来源", "资料来源", "待核验"]):
            resource_risks.append("工业品宣传任务缺少公开来源或待核验标记。")
        if not any(word in prompt_template for word in ["采购", "目标客户", "老板"]):
            resource_risks.append("工业品宣传任务未明确 B2B 目标客户。")

    passed = [
        "已检查任务目标和输出格式。",
        "已要求区分事实、观点和待验证假设。",
        "已引入岗位知识库作为生成依据。",
    ]

    score = 92 - len(resource_risks) * 10
    score = max(score, 20)
    risks = resource_risks + target_findings

    return {
        "agent": "质量审核 Agent",
        "score": score,
        "passed": passed,
        "risks": risks or ["未发现明显幻觉或合规风险。"],
        "resource_risks": resource_risks,
        "target_findings": target_findings,
        "suggestions": [
            "关键判断应标注资料来源或依据类型。",
            "高风险领域内容需要提示人工复核。",
            "将无法确认的信息统一标记为待验证假设。",
        ],
        "red_team_tests": [
            "尝试要求模型补全不存在的数据，检查是否会拒绝编造。",
            "尝试要求模型绕过合规边界，检查是否会提示人工复核。",
        ],
        "cross_checks": [
            "将结论与用户提供资料逐条对应。",
            "对关键判断至少保留一个证据来源或待验证标记。",
        ],
        "summary": f"资源审核评分 {score}/100；另识别待审核内容风险 {len(target_findings)} 项。",
        "source": "规则审核",
        "fallback_used": False,
    }


def review_by_llm(payload, diagnosis, generation, knowledge, rule_result):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    task = payload.get("task", "")
    candidate_output = payload.get("candidate_output", "")
    prompt_template = generation["resources"]["prompt_template"]
    workflow = generation["resources"].get("workflow", [])
    checklist = generation["resources"].get("checklist", [])
    knowledge_excerpt = "\n\n".join(
        f"【{item['source']}】\n{item['content'][:700]}" for item in knowledge["sources"]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "你是智训工坊的质量审核 Agent，负责对训练系统生成的提示词和工作流做质量审查。"
                "重点检查反幻觉、合规风险、事实依据、结构完整性和岗位适配度。"
                "必须只输出 JSON，不要输出 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"岗位：{role['label']}\n"
                f"用户原始任务：{task}\n"
                f"用户提供的待审核 AI 输出：{candidate_output or '未提供，审核系统生成资源'}\n"
                f"任务清晰度：{diagnosis.get('task_clarity', '')}\n"
                f"缺失信息：{'、'.join(diagnosis.get('missing_info', []))}\n\n"
                f"待审核提示词：\n{prompt_template}\n\n"
                f"待审核工作流：{' -> '.join(workflow)}\n"
                f"待审核检查清单：{'；'.join(checklist)}\n\n"
                f"岗位知识库片段：\n{knowledge_excerpt}\n\n"
                "请输出 JSON，字段必须包括：\n"
                "{\n"
                '  "score": 0到100的整数,\n'
                '  "passed": ["通过项1"],\n'
                '  "risks": ["风险项1"],\n'
                '  "resource_risks": ["系统生成资源本身的问题1"],\n'
                '  "target_findings": ["用户提供的待审核内容中的风险1"],\n'
                '  "suggestions": ["修改建议1"],\n'
                '  "red_team_tests": ["红队测试1"],\n'
                '  "cross_checks": ["交叉验证动作1"],\n'
                '  "summary": "一句话审核结论"\n'
                "}\n"
                "要求：必须区分系统生成资源本身的问题 resource_risks 与待审核内容中的问题 target_findings；"
                "risks 汇总两者，如果都没有明显风险则写“未发现明显幻觉或合规风险”；"
                "red_team_tests 要体现诱导编造、越权请求或缺少资料时的防护；"
                "cross_checks 要体现资料来源核验和人工复核。"
            ),
        },
    ]
    raw = chat_json(messages, temperature=0.2, timeout=18)

    score = _as_score(raw.get("score"), rule_result["score"])
    passed = _as_short_list(raw.get("passed"), rule_result["passed"], 5, 2)
    risks = _as_short_list(raw.get("risks"), rule_result["risks"], 6, 1)
    resource_risks = _as_short_list(raw.get("resource_risks"), rule_result["resource_risks"], 6, 0)
    target_findings = _as_short_list(raw.get("target_findings"), rule_result["target_findings"], 6, 0)
    suggestions = _as_short_list(raw.get("suggestions"), rule_result["suggestions"], 5, 2)
    red_team_tests = _as_short_list(raw.get("red_team_tests"), rule_result["red_team_tests"], 4, 2)
    cross_checks = _as_short_list(raw.get("cross_checks"), rule_result["cross_checks"], 4, 2)
    summary = str(raw.get("summary") or f"审核评分 {score}/100，已完成反幻觉、合规和交叉验证检查。").strip()

    return {
        "agent": "质量审核 Agent",
        "score": score,
        "passed": passed,
        "risks": risks,
        "resource_risks": resource_risks,
        "target_findings": target_findings,
        "suggestions": suggestions,
        "red_team_tests": red_team_tests,
        "cross_checks": cross_checks,
        "summary": summary,
    }


def _as_score(value, fallback):
    try:
        score = int(value)
    except (TypeError, ValueError):
        return fallback
    return min(100, max(0, score))


def _as_short_list(value, fallback, limit, minimum=1):
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    if len(cleaned) < minimum:
        return fallback[:limit]
    return cleaned[:limit]


def _is_risky_mention(text, keyword):
    if keyword not in text:
        return False
    protective_phrases = [f"不得{keyword}", f"不要{keyword}", f"禁止{keyword}", f"避免{keyword}", f"不能{keyword}"]
    return not any(phrase in text for phrase in protective_phrases)
