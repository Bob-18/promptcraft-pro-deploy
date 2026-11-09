import re

from .roles import get_role


CRITERIA = [
    {
        "key": "task_goal",
        "label": "任务目标",
        "weight": 20,
        "keywords": ["生成", "分析", "整理", "审查", "输出", "梳理", "对比", "总结"],
        "suggestion": "说明你要完成的具体任务，例如分析、审查、整理、生成报告或输出清单。",
    },
    {
        "key": "context",
        "label": "背景资料",
        "weight": 20,
        "keywords": ["基于", "资料", "数据", "代码", "会议", "反馈", "财报", "截图", "评论", "记录"],
        "suggestion": "补充输入资料来源，例如财报、代码片段、会议记录、用户反馈或产品截图。",
    },
    {
        "key": "dimensions",
        "label": "分析维度",
        "weight": 20,
        "keywords": ["维度", "从", "包括", "用户路径", "风险", "性能", "安全", "收入", "现金流", "优先级"],
        "suggestion": "明确分析维度，让大模型知道从哪些角度处理任务。",
    },
    {
        "key": "output_format",
        "label": "输出格式",
        "weight": 20,
        "keywords": ["输出", "表格", "报告", "清单", "结构", "JSON", "纪要", "摘要", "PRD"],
        "suggestion": "指定输出格式，例如报告结构、表格、清单、JSON、会议纪要或 PRD。",
    },
    {
        "key": "constraints",
        "label": "约束条件",
        "weight": 20,
        "keywords": ["不得", "不要", "标注", "待验证", "来源", "合规", "假设", "人工复核", "不能"],
        "suggestion": "加入约束条件，例如不得编造数据、标注待验证假设、关键判断需要来源。",
    },
]


MODE_CRITERIA = {
    "workflow": [
        {"key": "steps", "label": "步骤完整", "weight": 20, "keywords": ["第一步", "第二步", "步骤", "阶段"], "suggestion": "按先后顺序拆出不少于 4 个可执行步骤。"},
        {"key": "inputs", "label": "输入资料", "weight": 20, "keywords": ["输入", "资料", "数据", "记录", "文档"], "suggestion": "为每一步注明需要的资料、数据或前置条件。"},
        {"key": "outputs", "label": "阶段产出", "weight": 20, "keywords": ["输出", "产出", "清单", "报告", "表格"], "suggestion": "为每一步写清可检查的阶段产出。"},
        {"key": "checks", "label": "复核机制", "weight": 20, "keywords": ["复核", "检查", "验证", "确认", "审核"], "suggestion": "加入复核动作，说明如何判断本步骤已经完成。"},
        {"key": "risks", "label": "风险边界", "weight": 20, "keywords": ["风险", "异常", "失败", "边界", "人工"], "suggestion": "补充失败风险、处理边界和需要人工介入的情况。"},
    ],
    "review": [
        {"key": "claims", "label": "事实核验", "weight": 20, "keywords": ["事实", "核验", "来源", "证据", "数据"], "suggestion": "指出哪些结论需要用来源、数据或原文核验。"},
        {"key": "hallucination", "label": "幻觉识别", "weight": 20, "keywords": ["编造", "幻觉", "待验证", "无法确认", "假设"], "suggestion": "标出可能编造或无法确认的信息，并统一标记为待验证。"},
        {"key": "compliance", "label": "合规风险", "weight": 20, "keywords": ["合规", "隐私", "敏感", "授权", "脱敏"], "suggestion": "检查隐私、敏感信息、授权范围和岗位合规边界。"},
        {"key": "evidence", "label": "证据链", "weight": 20, "keywords": ["依据", "来源", "链接", "原文", "交叉验证"], "suggestion": "把关键结论与依据逐条对应，形成可追溯证据链。"},
        {"key": "revision", "label": "纠偏建议", "weight": 20, "keywords": ["修改", "纠偏", "建议", "替换", "删除"], "suggestion": "按“问题-依据-修改建议”给出可执行纠偏方案。"},
    ],
    "practice": [
        {"key": "deliverable", "label": "岗位成果", "weight": 20, "keywords": ["报告", "方案", "清单", "邮件", "纪要", "PRD", "建议"], "suggestion": "输出岗位中可以直接交付的报告、方案、清单或邮件。"},
        {"key": "professional", "label": "专业贴合", "weight": 20, "keywords": ["岗位", "业务", "用户", "设备", "财报", "产品", "客户"], "suggestion": "补充岗位对象、业务场景和专业判断维度。"},
        {"key": "evidence", "label": "依据来源", "weight": 20, "keywords": ["基于", "资料", "数据", "来源", "记录", "依据"], "suggestion": "说明成果依据了哪些资料、数据或工作记录。"},
        {"key": "action", "label": "行动建议", "weight": 20, "keywords": ["下一步", "行动", "负责人", "时间", "优先级", "执行"], "suggestion": "加入负责人、优先级、时间或下一步行动。"},
        {"key": "risk", "label": "风险边界", "weight": 20, "keywords": ["风险", "待验证", "不得", "人工复核", "边界"], "suggestion": "标明风险、待验证信息和必须人工复核的内容。"},
    ],
    "test": [
        {"key": "basic", "label": "基础题掌握", "weight": 20, "keywords": ["基础题答案", "目标", "资料", "格式", "要素"], "suggestion": "先完整回答基础题，并写出关键任务要素。"},
        {"key": "advanced", "label": "进阶题掌握", "weight": 20, "keywords": ["进阶题答案", "步骤", "流程", "拆解", "原因"], "suggestion": "进阶题需要给出分析过程或任务拆解步骤。"},
        {"key": "challenge", "label": "挑战题掌握", "weight": 20, "keywords": ["挑战题答案", "岗位", "成果", "方案", "报告"], "suggestion": "挑战题应形成与具体岗位相符的完整成果。"},
        {"key": "evidence", "label": "证据意识", "weight": 20, "keywords": ["证据", "来源", "依据", "资料", "事实"], "suggestion": "说明判断依据，并标注可以核验的资料来源。"},
        {"key": "boundary", "label": "风险边界", "weight": 20, "keywords": ["风险", "待验证", "人工复核", "不得", "假设"], "suggestion": "挑战题必须区分事实、假设和待验证信息。"},
    ],
}

MODE_LABELS = {
    "prompt": "提示词改写",
    "workflow": "任务拆解",
    "review": "结果审核",
    "practice": "岗位实战",
    "test": "分阶测试题",
}

ROLE_ANCHORS = {
    "marketing_manager": ["市场", "竞品", "产品", "用户", "营销", "推广"],
    "industrial_marketing": ["阀门", "管件", "短视频", "采购", "食品", "制药", "CIP", "询盘"],
    "finance_analyst": ["财报", "收入", "利润", "现金流", "负债", "公司"],
    "backend_developer": ["代码", "接口", "安全", "性能", "异常", "测试"],
    "admin_specialist": ["会议", "纪要", "通知", "宣传", "待办", "行政"],
    "product_manager": ["需求", "用户", "产品", "优先级", "PRD", "指标"],
    "smart_manufacturing": ["设备", "告警", "传感器", "工艺", "产线", "质检"],
    "industrial_internet": ["平台", "告警", "设备", "日志", "运维", "处置"],
}


def score_prompt(payload):
    role_id = payload.get("role_id", "marketing_manager")
    original = payload.get("original_task", "").strip()
    rewritten = payload.get("rewritten_prompt", "").strip()
    training_mode = payload.get("training_mode", "prompt")
    if training_mode not in MODE_LABELS:
        training_mode = "prompt"
    text = rewritten or original
    role = get_role(role_id)
    criteria = CRITERIA if training_mode == "prompt" else MODE_CRITERIA[training_mode]

    details = []
    total = 0
    suggestions = []
    for criterion in criteria:
        points, evidence = _score_criterion(text, criterion)
        total += points
        if points < criterion["weight"]:
            suggestions.append(criterion["suggestion"])
        details.append(
            {
                "key": criterion["key"],
                "label": criterion["label"],
                "score": points,
                "max_score": criterion["weight"],
                "evidence": evidence,
            }
        )

    details, total, quality_gate = _apply_quality_gate(
        text,
        details,
        total,
        role_id,
        original,
        training_mode,
        payload.get("candidate_output", ""),
    )
    if quality_gate["applied"]:
        suggestions.insert(0, quality_gate["message"])

    level = _level(total)
    improved = max(0, total - _rough_original_score(original)) if training_mode == "prompt" else 0
    exemplar = _build_exemplar(role_id, role["label"], original or role["default_task"])
    if training_mode != "prompt":
        exemplar = _build_mode_exemplar(training_mode, role["label"], original or role["default_task"])
    adaptive_decision = _build_adaptive_decision(total, details, role["label"], training_mode)

    return {
        "role": role["label"],
        "training_mode": training_mode,
        "mode_label": MODE_LABELS[training_mode],
        "score": total,
        "level": level,
        "improved": improved,
        "details": details,
        "suggestions": suggestions or ["提示词结构已经比较完整，下一步可以加入更具体的数据来源和评价标准。"],
        "exemplar_prompt": exemplar,
        "training_feedback": _feedback(total, MODE_LABELS[training_mode]),
        "adaptive_decision": adaptive_decision,
        "quality_gate": quality_gate,
    }


def _apply_quality_gate(text, details, total, role_id="", original="", training_mode="prompt", candidate_output=""):
    cleaned = re.sub(r"\s+", "", text or "")
    length = len(cleaned)
    cap = 100
    reason = ""
    if length < 12:
        cap, reason = 20, "回答过短，无法证明已经掌握本关能力。"
    elif length < 25:
        cap, reason = 40, "回答内容不足，只有关键词，缺少完整判断或步骤。"
    elif length < 45:
        cap, reason = 60, "回答仍偏短，需要补充依据、处理过程和风险边界。"

    keyword_hits = sum(
        1
        for item in details
        if str(item.get("evidence", "")).startswith(("覆盖多个要素", "仅覆盖一个要素"))
    )
    structure_count = len(re.findall(r"[。！？；;\n]|第[一二三四五六七八九十]步|\d+[.、]", text or ""))
    if keyword_hits >= 4 and structure_count < 2 and length < 120:
        cap = min(cap, 60)
        reason = "检测到关键词集中堆叠，但缺少可执行结构，不能据此判定掌握。"

    relevant_anchors = [word for word in ROLE_ANCHORS.get(role_id, []) if word in original]
    if relevant_anchors and not any(word in text for word in relevant_anchors) and not (training_mode == "review" and candidate_output):
        cap = min(cap, 60)
        reason = "回答没有回应原任务中的岗位对象或业务场景，不能用无关的完整答案过关。"

    if training_mode == "review" and candidate_output:
        target_signals = []
        if any(word in candidate_output for word in ["保证", "绝对", "全网第一", "所有", "任何"]):
            target_signals.extend(["保证", "绝对", "夸大", "承诺", "所有", "任何"])
        if any(word in candidate_output for word in ["证件", "认证", "型号", "参数"]):
            target_signals.extend(["证件", "认证", "型号", "参数", "来源"])
        if any(word in candidate_output for word in ["半夜三点", "立马上门", "当天解决"]):
            target_signals.extend(["半夜三点", "立马上门", "当天", "服务", "时效", "承诺"])
        if target_signals and not any(word in text for word in target_signals):
            cap = min(cap, 60)
            reason = "审核意见没有指出待审核内容中的具体风险，泛化检查清单不能判定为已掌握。"

    if total <= cap:
        return details, total, {"applied": False, "score_cap": cap, "message": ""}

    adjusted_scores = [int(item["score"] * cap / max(1, total)) for item in details]
    remaining = cap - sum(adjusted_scores)
    for index in range(len(adjusted_scores)):
        if remaining <= 0:
            break
        room = details[index]["max_score"] - adjusted_scores[index]
        addition = min(room, remaining)
        adjusted_scores[index] += addition
        remaining -= addition
    adjusted = [
        {**item, "score": adjusted_scores[index], "evidence": f"{item['evidence']}；受整体质量门槛限制"}
        for index, item in enumerate(details)
    ]
    return adjusted, cap, {"applied": True, "score_cap": cap, "message": reason}


def _score_criterion(text, criterion):
    if not text:
        return 0, "未输入内容"
    matched = [word for word in criterion["keywords"] if word in text]
    if matched:
        points = criterion["weight"] if len(matched) >= 2 else int(criterion["weight"] * 0.7)
        evidence = "覆盖多个要素：" if len(matched) >= 2 else "仅覆盖一个要素："
        return points, evidence + "、".join(matched[:4])
    if len(text) >= 60 and criterion["key"] in {"task_goal", "output_format"}:
        return 12, "内容较完整，但该项表达不够明确"
    if len(text) >= 30:
        return 8, "有一定描述，但缺少明确标记"
    return 4, "表达过短或过于模糊"


def _rough_original_score(text):
    if not text:
        return 0
    if len(text.strip()) < 12:
        return 20
    if len(text.strip()) < 25:
        return 35
    return 50


def _level(score):
    if score >= 85:
        return "优秀"
    if score >= 70:
        return "合格"
    if score >= 50:
        return "待提升"
    return "基础薄弱"


def _feedback(score, mode_label="提示词改写"):
    if score >= 85:
        return f"{mode_label}已经具备较好的岗位结构，可以进入带证据链的进阶任务。"
    if score >= 70:
        return f"{mode_label}基本可用，建议继续补充资料来源、约束条件和审核标准。"
    if score >= 50:
        return f"{mode_label}已有基本方向，但关键维度覆盖不足，需要继续专项补练。"
    return f"当前{mode_label}仍较模糊，建议先查看示例并完成一个降维练习。"


def _build_adaptive_decision(score, details, role_label, training_mode):
    weak_dimensions = [item["label"] for item in details if item["score"] < item["max_score"]]
    focus = "、".join(weak_dimensions[:3]) or "真实资料与岗位边界"
    if score < 60:
        strategy = "降维解释"
        next_action = f"先查看示例，围绕“{focus}”完成一个更小的补全练习，再重新作答。"
    elif score < 80:
        strategy = "专项补练"
        next_action = f"保留现有答案，只针对“{focus}”补充内容后重新评分。"
    else:
        strategy = "进阶挑战"
        next_action = f"本关已达标，进入{role_label}更复杂的真实任务，并继续加强证据链。"

    return {
        "agent": "反馈迭代 Agent",
        "strategy": strategy,
        "mastery_passed": score >= 80,
        "pass_score": 80,
        "weak_dimensions": weak_dimensions[:3],
        "next_action": next_action,
        "training_mode": training_mode,
    }


def _build_mode_exemplar(training_mode, role_label, task):
    examples = {
        "workflow": (
            f"围绕{role_label}任务“{task}”，按 5 个步骤拆解。每一步都写明：输入资料、处理动作、阶段产出、复核标准和失败风险。"
        ),
        "review": (
            f"审核{role_label}任务“{task}”的 AI 结果。按“问题-依据-风险等级-修改建议”列出审核清单，"
            "区分事实、观点和待验证假设，并标出隐私、合规和人工复核边界。"
        ),
        "practice": (
            f"完成{role_label}任务“{task}”的正式岗位成果。先给结论摘要，再提供依据、执行步骤、负责人或优先级、"
            "风险提示和待核验清单；不得编造数据或来源。"
        ),
        "test": (
            f"基础题回答任务必要要素；进阶题拆解{role_label}工作流程并说明依据；挑战题围绕“{task}”输出带证据链的岗位成果，"
            "同时标注事实、假设、风险和人工复核边界。"
        ),
    }
    return examples[training_mode]


def _build_exemplar(role_id, role_label, task):
    starters = {
        "marketing_manager": "你是一名资深市场战略顾问。请基于我提供的产品资料、用户评论和截图，对 A 产品和 B 产品进行用户体验竞品分析。",
        "industrial_marketing": "你是一名懂工业流体产品和 B2B 内容营销的顾问。请基于公开产品资料，面向食品生产企业老板和采购人员策划一条 20 秒工业阀门短视频。",
        "finance_analyst": "你是一名谨慎的金融分析助理。请基于我提供的财报资料，从收入结构、利润质量、现金流、负债水平和风险因素进行分析。",
        "backend_developer": "你是一名资深后端代码审查专家。请基于我提供的代码片段和业务上下文，从正确性、安全性、性能、异常处理、可读性和测试覆盖进行审查。",
        "admin_specialist": "你是一名专业行政助理。请基于我提供的会议记录，整理会议主题、核心结论、争议问题、待办事项、负责人和截止时间。",
        "product_manager": "你是一名资深产品经理。请基于我提供的用户反馈、业务目标和约束条件，完成需求拆解、优先级判断和 PRD 结构设计。",
    }
    starter = starters.get(role_id, f"你是一名{role_label}岗位的 AI 实训教练。请基于我提供的资料完成以下任务：{task}")
    return (
        f"{starter}\n\n"
        "输出要求：\n"
        "1. 先给出 3-5 条结论摘要。\n"
        "2. 按关键维度展开分析，并说明每个判断的依据。\n"
        "3. 将事实、观点和待验证假设分开标注。\n"
        "4. 输出可执行的下一步建议。\n"
        "5. 不得编造数据或来源；无法确认的内容标注为“待验证”。"
    )
