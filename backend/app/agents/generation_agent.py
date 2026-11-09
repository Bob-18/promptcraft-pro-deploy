from ..config import is_external_llm_allowed
from ..llm_client import LLMError, chat_json
from ..roles import get_role


PROMPT_FRAMES = {
    "marketing_manager": "你是一名资深市场战略顾问。请基于我提供的资料，对目标竞品进行用户体验竞品分析，并输出管理层可阅读的结构化报告。",
    "industrial_marketing": "你是一名懂工业流体产品和 B2B 内容营销的实训教练。请基于公开产品资料，为目标客户生成可核验、不夸大的短视频任务。",
    "finance_analyst": "你是一名谨慎的金融分析助理。请基于用户提供的财报资料进行研究摘要，区分事实、估计和观点。",
    "backend_developer": "你是一名资深后端代码审查专家。请从正确性、安全性、性能、异常处理、可读性和测试覆盖六个维度审查代码。",
    "admin_specialist": "你是一名专业行政助理。请将会议材料整理为结构化纪要，明确结论、待办、负责人和截止时间。",
    "product_manager": "你是一名资深产品经理。请基于业务目标、用户反馈和约束条件，完成需求拆解、优先级判断和验证指标设计。",
    "smart_manufacturing": "你是一名智能制造实训教练。请基于设备报警、传感器数据和工艺参数，分析设备异常原因并生成安全可执行的排查方案。",
    "industrial_internet": "你是一名工业互联网运维实训教练。请基于平台告警日志、设备状态和历史处置记录，分析告警原因、影响范围和运维处置流程。",
}

WORKFLOWS = {
    "marketing_manager": ["明确报告目标", "确定竞品对象", "建立分析维度", "收集资料", "生成初稿", "审核事实和假设"],
    "industrial_marketing": ["明确目标客户与平台", "检索公开产品资料", "区分事实与待核验项", "设计短视频结构", "审核夸大和服务承诺", "按询盘漏斗复盘"],
    "finance_analyst": ["确认公司和周期", "读取财报资料", "拆分核心指标", "识别风险因素", "标注假设边界", "输出合规摘要"],
    "backend_developer": ["理解业务意图", "检查输入输出", "审查异常处理", "识别安全风险", "评估测试覆盖", "给出可验证修改建议"],
    "admin_specialist": ["识别会议主题", "归纳核心结论", "提取争议问题", "整理行动项", "补全责任人和时间", "标注待确认内容"],
    "product_manager": ["明确业务目标", "聚类用户反馈", "拆解需求场景", "评估价值和成本", "排序优先级", "设计验证指标"],
    "smart_manufacturing": ["确认报警信息", "读取传感器数据", "对比工艺参数", "排查设备状态", "评估安全风险", "输出复核建议"],
    "industrial_internet": ["确认告警类型", "检查设备在线状态", "分析数据链路", "判断影响范围", "制定处置优先级", "记录闭环结果"],
}


def generate(payload, diagnosis, knowledge):
    rule_result = generate_by_rules(payload, diagnosis, knowledge)
    if not is_external_llm_allowed(payload):
        return rule_result

    try:
        llm_result = generate_by_llm(payload, diagnosis, knowledge, rule_result)
        llm_result["source"] = "DeepSeek"
        llm_result["fallback_used"] = False
        return llm_result
    except LLMError as exc:
        rule_result["source"] = "规则兜底"
        rule_result["fallback_used"] = True
        rule_result["llm_error"] = str(exc)[:180]
        return rule_result


def generate_by_rules(payload, diagnosis, knowledge):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    position = payload.get("specific_position") or role["label"]
    task = payload.get("task", role["default_task"]).strip()
    scenario = _scenario_override(role_id, task, position)
    frame = scenario.get("frame") or PROMPT_FRAMES.get(role_id, PROMPT_FRAMES["marketing_manager"])
    workflow = scenario.get("workflow") or WORKFLOWS.get(role_id, WORKFLOWS["marketing_manager"])
    source_names = "、".join(item["source"] for item in knowledge["sources"])
    training_mode = payload.get("training_mode", "prompt")

    prompt_template = scenario.get("prompt_template") or _default_prompt_template(frame, position, task)
    practice_tasks = scenario.get("practice_tasks") or [
        f"基础题：以{position}身份，把模糊指令改写为包含目标、背景、维度和格式的提示词。",
        f"进阶题：围绕{role['tasks'][0]}任务设计 5 个事实核验问题，并说明资料来源。",
        f"挑战题：基于真实或模拟资料生成一份{position}可使用的岗位任务成果，并标注事实、观点和待验证假设。",
    ]
    checklist = scenario.get("checklist") or [
        "是否说明角色和任务目标",
        "是否给出输入资料和约束条件",
        "是否要求结构化输出",
        "是否标注事实来源和待验证假设",
        "是否设置合规和质量标准",
    ]
    prompt_template, workflow, practice_tasks, checklist = _adapt_resources_for_mode(
        training_mode,
        role,
        position,
        task,
        payload.get("candidate_output", ""),
        prompt_template,
        workflow,
        practice_tasks,
        checklist,
    )

    return {
        "agent": "领域知识生成 Agent",
        "resources": {
            "prompt_template": prompt_template,
            "workflow": workflow,
            "practice_tasks": practice_tasks,
            "checklist": checklist,
        },
        "knowledge_used": source_names,
        "summary": f"已为{role['label']}生成与{_mode_label(training_mode)}对应的定制资源、实操指南和分阶测试题。",
        "source": "规则生成",
        "fallback_used": False,
    }


def generate_by_llm(payload, diagnosis, knowledge, rule_result):
    role_id = payload.get("role_id", "marketing_manager")
    role = get_role(role_id)
    position = payload.get("specific_position") or role["label"]
    task = payload.get("task", role["default_task"]).strip()
    training_mode = payload.get("training_mode", "prompt")
    candidate_output = payload.get("candidate_output", "")
    source_names = [item["source"] for item in knowledge["sources"]]
    knowledge_excerpt = "\n\n".join(
        f"【{item['source']}】\n{item['content'][:900]}" for item in knowledge["sources"]
    )
    messages = [
        {
            "role": "system",
            "content": (
                "你是智训工坊的领域知识生成 Agent。你的任务是把职场用户的模糊任务，"
                "转化为可执行的大模型提示词模板、岗位工作流、实训任务和质量检查清单。"
                "必须只输出 JSON，不要输出 Markdown。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"岗位：{role['label']}\n"
                f"具体职位：{position}\n"
                f"岗位能力重点：{'、'.join(role['skill_focus'])}\n"
                f"用户任务：{task}\n"
                f"当前训练模式：{_mode_label(training_mode)}\n"
                f"待审核 AI 输出：{candidate_output or '未提供'}\n"
                f"诊断总结：{diagnosis.get('summary', '')}\n"
                f"任务清晰度：{diagnosis.get('task_clarity', '')}\n"
                f"缺失信息：{'、'.join(diagnosis.get('missing_info', []))}\n\n"
                f"岗位知识库片段：\n{knowledge_excerpt}\n\n"
                "请输出 JSON，字段必须包括：\n"
                "{\n"
                '  "prompt_template": "一段可直接复制给大模型的高质量提示词",\n'
                '  "workflow": ["步骤1", "步骤2", "步骤3"],\n'
                '  "practice_tasks": ["基础题", "进阶题", "挑战题"],\n'
                '  "checklist": ["检查项1", "检查项2"],\n'
                '  "summary": "一句话说明本次训练资源"\n'
                "}\n"
                "要求：所有资源必须服务于当前训练模式，不能把五种训练都退化成提示词改写；"
                "prompt_template 必须包含角色、任务目标、输入资料、分析维度、输出格式、事实核验和禁止编造；"
                "workflow 4 到 7 步；practice_tasks 3 项；checklist 4 到 6 项；不要编造用户没有提供的具体业务数据。"
            ),
        },
    ]
    raw = chat_json(messages, temperature=0.35, timeout=18)
    fallback_resources = rule_result["resources"]

    prompt_template = str(raw.get("prompt_template") or fallback_resources["prompt_template"]).strip()
    workflow = _as_short_list(raw.get("workflow"), fallback_resources["workflow"], 7, 4)
    practice_tasks = _as_short_list(raw.get("practice_tasks"), fallback_resources["practice_tasks"], 3, 3)
    checklist = _as_short_list(raw.get("checklist"), fallback_resources["checklist"], 6, 4)
    summary = str(raw.get("summary") or rule_result["summary"]).strip()

    return {
        "agent": "领域知识生成 Agent",
        "resources": {
            "prompt_template": prompt_template,
            "workflow": workflow,
            "practice_tasks": practice_tasks,
            "checklist": checklist,
        },
        "knowledge_used": "、".join(source_names),
        "summary": summary,
    }


def _adapt_resources_for_mode(mode, role, position, task, candidate_output, prompt_template, workflow, practice_tasks, checklist):
    if mode == "workflow":
        prompt_template = (
            f"请以{position}身份，将任务“{task}”拆成 5-7 个可执行步骤。"
            "每一步必须写清输入资料、处理动作、阶段产出、复核标准和失败风险；最后说明步骤之间的依赖关系。"
        )
        checklist = ["步骤是否有明确顺序", "每步是否注明输入和产出", "是否包含事实复核", "是否覆盖失败风险", "是否说明最终交付物"]
    elif mode == "review":
        target = candidate_output or "用户尚未提供待审核内容，开始前需先补充 AI 输出。"
        prompt_template = (
            f"请以{position}身份审核下面的 AI 输出，而不是重新完成原任务。\n\n待审核内容：\n{target}\n\n"
            "按“问题原句-问题类型-核验依据-风险等级-修改建议-人工复核点”输出审核表，"
            "结合目标客户（如企业老板或采购人员）检查表达适配度，区分事实、观点和待验证假设；"
            "关键事实必须核验公开来源或标记待核验，不得编造。"
        )
        checklist = ["是否逐句定位问题", "是否核验事实来源", "是否识别夸大和幻觉", "是否给出可执行修改", "是否标明人工复核点"]
    elif mode == "practice":
        prompt_template = (
            f"请以{position}身份完成任务“{task}”的正式岗位交付物。"
            "成果必须包含结论摘要、关键分析、资料依据、下一步行动、风险边界和待核验清单，并适合真实工作场景使用。"
        )
        checklist = ["成果是否可直接交付", "是否贴合岗位和对象", "结论是否有资料依据", "是否包含行动建议", "是否标明风险和待核验项"]
    elif mode == "test":
        prompt_template = (
            f"围绕{role['label']}任务“{task}”，按顺序完成基础题、进阶题和挑战题。"
            "基础题检验必要要素，进阶题检验流程与依据，挑战题检验独立岗位成果和风险边界。"
        )
        checklist = ["是否完整回答基础题", "是否说明进阶题推理步骤", "挑战题是否形成岗位成果", "是否写明证据来源", "是否标明风险边界"]
    return prompt_template, workflow, practice_tasks, checklist


def _mode_label(mode):
    return {
        "prompt": "提示词改写",
        "workflow": "任务拆解",
        "review": "结果审核",
        "practice": "岗位实战",
        "test": "分阶测试",
    }.get(mode, "提示词改写")


def _as_short_list(value, fallback, limit, minimum=1):
    if not isinstance(value, list):
        return fallback[:limit]
    cleaned = [str(item).strip() for item in value if str(item).strip()]
    if len(cleaned) < minimum:
        return fallback[:limit]
    return cleaned[:limit]


def _default_prompt_template(frame, position, task):
    return (
        f"{frame}\n\n"
        f"具体职位：{position}\n"
        f"用户任务：{task}\n\n"
        "请按以下要求输出：\n"
        "1. 先给出结论摘要。\n"
        "2. 按岗位任务拆解关键步骤。\n"
        "3. 对事实、观点和待验证假设分别标注。\n"
        "4. 给出可执行的下一步建议。\n"
        "5. 不得编造数据；没有依据的内容必须标注为“待验证”。"
    )


def _scenario_override(role_id, task, position):
    if role_id == "industrial_marketing":
        return {
            "frame": "你是一名懂工业流体产品和 B2B 内容营销的实训教练。请帮助网络营销人员把产品宣传需求转化为有场景、有依据、有行动入口的短视频任务。",
            "prompt_template": (
                "请你扮演一名懂工业流体产品和 B2B 短视频营销的内容顾问，"
                "基于我提供的公开资料，为食品生产企业老板和采购人员策划一条工业阀门短视频。\n\n"
                f"具体职位：{position}\n"
                f"用户任务：{task}\n\n"
                "请输出：\n"
                "1. 目标客户及其采购关注点；\n"
                "2. 20 秒短视频结构，包括标题、前三秒开场、口播、画面提示和字幕；\n"
                "3. 可确认的产品类别和应用场景，并逐项标注公开来源；\n"
                "4. 需要补充或核验的型号、材质、温压、认证和服务信息；\n"
                "5. 不同平台的表达调整建议，但产品事实必须保持一致；\n"
                "6. 私信咨询或提交工况获取选型建议的行动入口；\n"
                "7. 目标客户曝光、主页访问、私信、有效询盘和报价请求的复盘指标。\n\n"
                "要求：不得编造型号、参数、认证、客户案例、成交数据或服务承诺；"
                "不得把行业媒体报道扩大为全部产品事实；无法确认的信息标注为‘待核验’。"
            ),
            "workflow": ["明确客户与平台", "检索公开资料", "标注事实等级", "设计短视频结构", "审核夸大表达", "设置询盘入口", "复盘转化漏斗"],
            "practice_tasks": [
                "基础题：工业品短视频任务必须说明哪五类信息？为什么点赞量不能单独代表 B2B 转化？",
                "进阶题：将食品行业 CIP 阀门资料分为公开可确认、企业公开称和待核验三类，并说明审核方法。",
                "挑战题：在没有具体型号和证书原件时，完成一条面向采购人员的 20 秒短视频脚本，加入来源、待核验提示和咨询入口。",
            ],
            "checklist": [
                "是否明确老板、采购或技术决策者",
                "是否说明食品灭菌或 CIP 清洗等应用场景",
                "是否为产品事实标注公开来源或待核验",
                "是否避免绝对化宣传和无法核验的服务承诺",
                "是否给出提交工况或私信咨询的行动入口",
                "是否使用询盘漏斗而非只看点赞量",
            ],
        }

    if role_id == "marketing_manager" and _contains_any(task, ["具身", "机器人", "实训室", "高职", "院校"]):
        return {
            "frame": "你是一名懂职业教育和 AI 教育产品推广的市场顾问。请帮助市场经理把模糊推广需求转化为面向高职院校决策者的结构化推广任务。",
            "prompt_template": (
                "请你扮演一名懂职业教育和 AI 教育产品推广的市场顾问，"
                "面向高职院校实训中心主任，撰写一份具身机器人实训室升级建议书。\n\n"
                f"具体职位：{position}\n"
                f"用户任务：{task}\n\n"
                "请输出：\n"
                "1. 开场痛点分析，区分实训中心主任、院系负责人和专业教师的关注点；\n"
                "2. 产品能力到教学价值的转化说明，不堆砌技术参数；\n"
                "3. 可支撑预算申请或成果展示的方向清单；\n"
                "4. 适合手机端阅读的邮件或微信长文；\n"
                "5. 需要补充或核验的政策、赛事、资金和案例资料清单；\n"
                "6. 预约演示、获取预算表或安排试用课的行动入口。\n\n"
                "要求：不得编造政策、资金、赛事、学校案例和数据；资料不足时标注“待补充”或“待核验”。"
            ),
            "workflow": ["明确客户角色", "提炼院校痛点", "翻译产品价值", "补齐事实依据", "设计行动入口", "审核夸大宣传"],
            "practice_tasks": [
                "基础题：面向高职院校推广具身机器人实训室时，至少需要明确哪 4 类关键信息？",
                "进阶题：为什么“帮我写个给高职院校老师的推广方案”不是一个高质量提示词？请指出至少 3 个问题。",
                "挑战题：将原始推广任务改写成包含目标客户、产品背景、输出格式、价值翻译和事实核验约束的高质量指令。",
            ],
            "checklist": [
                "是否区分目标客户角色",
                "是否把产品参数翻译成教学价值",
                "是否标注政策、赛事、资金和案例的来源状态",
                "是否避免保证获奖、必然申报成功等夸大承诺",
                "是否提供明确的下一步行动入口",
            ],
        }

    if role_id == "admin_specialist" and _contains_any(task, ["产品成果", "宣传", "推广", "公众号", "海报"]):
        return {
            "frame": "你是一名资深企业行政宣传专员。请帮助行政办公岗位用户把模糊宣传需求转化为可执行的产品成果宣传方案。",
            "prompt_template": (
                "请你扮演一名资深企业行政宣传专员，根据产品成果资料，帮助我制定一份产品成果宣传方案。\n\n"
                f"具体职位：{position}\n"
                f"用户任务：{task}\n\n"
                "请输出：\n"
                "1. 宣传目标与目标受众分析；\n"
                "2. 产品成果核心亮点提炼；\n"
                "3. 宣传主题和传播策略；\n"
                "4. 宣传渠道规划，例如企业公众号、官网、内部邮件、宣传海报、企业微信群；\n"
                "5. 不同场景宣传文案，例如长篇宣传稿、公众号标题、海报短文案；\n"
                "6. 宣传执行计划和后续优化建议；\n"
                "7. 需要进一步确认的数据、案例和事实来源清单。\n\n"
                "要求：语言专业、简洁、有传播力；不得编造产品数据、客户案例、传播效果或企业荣誉。"
            ),
            "workflow": ["确定宣传对象", "收集成果资料", "提炼核心亮点", "匹配宣传渠道", "生成宣传内容", "核验事实来源"],
            "practice_tasks": [
                "基础题：产品成果宣传方案至少应包含哪 4 类核心信息？",
                "进阶题：为什么“如何对产品成果进行一些宣传”不是一个高质量 AI 提示词？请说明至少 3 个原因。",
                "挑战题：将原始宣传需求改写成包含任务背景、宣传目标、目标对象、输出格式和内容要求的高质量指令。",
            ],
            "checklist": [
                "是否明确宣传目标和目标受众",
                "是否补充产品成果资料和使用场景",
                "是否给出渠道规划和多场景文案",
                "是否标注待核验数据、案例和事实来源",
                "是否避免绝对化、夸大化宣传表达",
            ],
        }

    if role_id == "smart_manufacturing" and _contains_any(task, ["智能工厂", "5G", "机器视觉", "AI全检", "场景", "申报", "标准体系"]):
        return {
            "frame": "你是一名智能制造实训教练。请基于公开政策、典型场景指引和智能工厂案例，帮助学习者完成智能制造场景判断、建设流程拆解和分阶测试。",
            "prompt_template": (
                "请你扮演智能制造实训教练，基于我提供的企业资料和公开政策/案例资料，"
                "帮助我完成智能工厂建设或智能制造场景分析。\n\n"
                f"具体职位：{position}\n"
                f"用户任务：{task}\n\n"
                "请输出：\n"
                "1. 该任务可能对应的智能制造典型场景或重点环节，并说明判断依据；\n"
                "2. 建设或改造工作流程，例如场景选择、数据采集、网络建设、系统集成、智能决策、效果评估；\n"
                "3. 关键技术与系统组成，例如 5G、工业互联网平台、机器视觉、AI、数字孪生等；\n"
                "4. 需要补充的数据、设备、网络、软件和企业现状资料；\n"
                "5. 常见错误、风险点和人工复核要求；\n"
                "6. 基础题、进阶题和挑战题各 1 道，并给出参考答案。\n\n"
                "要求：不得编造政策文件、企业案例、成本数据和技术指标；无法确认的信息必须标注为“待核验”。"
            ),
            "workflow": ["识别行业与建设目标", "匹配典型场景", "梳理技术系统", "拆解实施流程", "标注待核验资料", "生成分阶测试题"],
            "practice_tasks": [
                "基础题：根据智能制造典型场景参考指引，智能制造典型场景从多少个重点环节进行凝练？",
                "进阶题：为什么“帮我建个智能工厂”不是一个高质量任务指令？请指出缺失信息并给出改进方向。",
                "挑战题：分析新能源电池工厂部署 5G+机器视觉 AI 全检系统更接近哪个智能制造环节，并说明判断依据和待核验资料。",
            ],
            "checklist": [
                "是否明确行业、建设类型和目标场景",
                "是否基于公开指引或案例说明判断依据",
                "是否区分事实、推测和待核验信息",
                "是否覆盖技术系统、实施流程和效果评估",
                "是否生成基础、进阶、挑战三类测试题",
            ],
        }

    return {}


def _contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)
