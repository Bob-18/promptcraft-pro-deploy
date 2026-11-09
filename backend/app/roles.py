ROLES = {
    "marketing_manager": {
        "label": "市场经理",
        "tasks": ["竞品分析", "营销文案", "投放复盘"],
        "default_task": "以麦肯锡风格，对比 A 产品和 B 产品的用户体验，重点分析 C 功能，输出一份给管理层看的竞品分析报告。",
        "skill_focus": ["提示词结构化", "竞品维度拆解", "事实核验"],
        "knowledge_files": ["市场竞品分析模板.md", "市场经理具身机器人实训室推广案例.md", "职场AI使用规范.md"],
    },
    "industrial_marketing": {
        "label": "工业品网络营销",
        "tasks": ["工业品短视频", "公开资料核验", "多平台内容适配"],
        "default_task": "面向食品生产企业老板和采购人员，基于公开产品资料制作一条 20 秒卫生级阀门短视频文案，标注资料来源，不得编造型号、参数、认证、客户案例和服务承诺。",
        "skill_focus": ["客户场景表达", "公开资料核验", "反夸大与转化设计"],
        "knowledge_files": ["工业品网络营销_卫生级阀门公开资料.md", "职场AI使用规范.md"],
    },
    "finance_analyst": {
        "label": "金融分析助理",
        "tasks": ["财报摘要", "风险分析", "研究报告"],
        "default_task": "基于我提供的财报资料，从收入结构、利润质量、现金流、负债水平和风险因素五个维度生成研究摘要。",
        "skill_focus": ["事实观点区分", "合规表达", "假设标注"],
        "knowledge_files": ["金融财报分析规范.md", "职场AI使用规范.md"],
    },
    "backend_developer": {
        "label": "后端开发工程师",
        "tasks": ["代码审查", "接口文档", "测试用例"],
        "default_task": "请从正确性、安全性、性能、异常处理、可读性和测试覆盖六个维度审查以下接口代码。",
        "skill_focus": ["审查维度设计", "风险定位", "测试意识"],
        "knowledge_files": ["代码审查标准.md", "职场AI使用规范.md"],
    },
    "admin_specialist": {
        "label": "行政专员",
        "tasks": ["会议纪要", "通知公告", "产品宣传"],
        "default_task": "请将以下会议记录整理为会议纪要，包含核心结论、争议问题、待办事项、负责人和截止时间。",
        "skill_focus": ["信息提取", "结构化表达", "事实核验"],
        "knowledge_files": ["会议纪要整理规范.md", "行政办公产品成果宣传案例.md", "职场AI使用规范.md"],
    },
    "product_manager": {
        "label": "产品经理",
        "tasks": ["PRD 梳理", "需求优先级", "用户反馈分析"],
        "default_task": "请基于用户反馈和业务目标，梳理需求优先级，并输出 PRD 结构、风险点和验证指标。",
        "skill_focus": ["需求拆解", "优先级判断", "验证指标设计"],
        "knowledge_files": ["产品需求分析规范.md", "职场AI使用规范.md"],
    },
    "smart_manufacturing": {
        "label": "智能制造",
        "tasks": ["设备异常分析", "工艺参数优化", "质检报告生成"],
        "default_task": "基于设备报警记录、传感器数据和近期工艺参数变化，分析产线设备异常原因，输出可能原因、排查步骤、风险等级和人工复核建议。",
        "skill_focus": ["设备异常定位", "工艺参数分析", "安全复核意识"],
        "knowledge_files": ["智能制造设备异常分析规范.md", "智能制造公开资料与分阶题库.md", "职场AI使用规范.md"],
    },
    "industrial_internet": {
        "label": "工业互联网",
        "tasks": ["告警分析", "设备监测", "运维处置方案"],
        "default_task": "基于工业互联网平台告警日志、设备运行状态和历史处置记录，分析告警原因、影响范围、优先级和运维处置流程，并标注需要人工确认的数据。",
        "skill_focus": ["告警归因", "运维流程拆解", "数据可信度校验"],
        "knowledge_files": ["工业互联网告警运维规范.md", "职场AI使用规范.md"],
    },
}


def get_role(role_id):
    return ROLES.get(role_id, ROLES["marketing_manager"])


def list_roles():
    return [
        {
            "id": role_id,
            "label": config["label"],
            "tasks": config["tasks"],
            "default_task": config["default_task"],
        }
        for role_id, config in ROLES.items()
    ]
