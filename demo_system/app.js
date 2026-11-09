const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin;

const roleConfigs = {
  marketing_manager: {
    label: "市场经理",
    experience: 5,
    aiLevel: "初级",
    education: "本科",
    theoryScore: 62,
    taskType: "竞品分析",
    weakTask: "帮我写个报告。",
    strongTask: "以麦肯锡风格，对比 A 产品和 B 产品的用户体验，重点分析 C 功能，输出一份给管理层看的竞品分析报告。",
    starterRewrite: "请对比 A 产品和 B 产品，帮我生成一份竞品分析报告。",
  },
  industrial_marketing: {
    label: "工业品网络营销",
    experience: 1,
    aiLevel: "中级",
    education: "未提供",
    theoryScore: 60,
    taskType: "卫生级阀门短视频营销",
    weakTask: "我需要把工业级和卫生级阀门管件的产品实拍剪成 10-30 秒短视频，发布到多个平台，主要面向企业老板和采购人员，希望带来私信咨询。",
    strongTask: "请基于公开产品资料，面向食品生产企业老板和采购人员，围绕食品灭菌与 CIP 清洗场景策划一条 20 秒卫生级阀门短视频。输出标题、前三秒开场、口播、画面提示、字幕和私信咨询入口；逐项标注公开来源，不得编造型号、材质、温压、认证、客户案例、成交数据或服务承诺，无法确认的信息标注为待核验。",
    starterRewrite: "请面向食品生产企业采购人员，基于公开资料生成一条 20 秒阀门短视频文案，并标注待核验信息。",
    reviewSample: "阀门管件找老张，证件齐全够硬气，半夜三点也能立马上门！",
    modeTasks: {
      prompt: "我需要把工业级和卫生级阀门管件的产品实拍剪成 10-30 秒短视频，发布到多个平台，主要面向企业老板和采购人员，希望带来私信咨询。",
      workflow: "我要完成一条工业品阀门短视频，请把资料收集、选题、文案、拍摄、剪辑、事实审核、多平台发布和询盘复盘拆成可执行步骤。",
      review: "请审核一条既有 AI 生成的阀门短视频文案，识别 AI 味、夸大表达、事实依据不足和不适合采购人员的问题，并给出修改方案。",
      practice: "基于公开的卫生级阀门资料，面向食品企业老板和采购人员，完成一条食品灭菌与 CIP 清洗场景的 20 秒抖音短视频方案。",
      test: "围绕工业品阀门短视频营销，依次完成目标客户与转化逻辑基础题、公开资料核验进阶题和独立脚本挑战题。",
    },
    profileSource: "岗位流程来自匿名访谈；当前任务由系统根据访谈归纳，不是受访者原话；60 分为系统复现测评值",
  },
  finance_analyst: {
    label: "金融分析助理",
    experience: 1,
    aiLevel: "初级",
    education: "本科",
    theoryScore: 58,
    taskType: "财报分析",
    weakTask: "分析一下这家公司值不值得买。",
    strongTask: "基于我提供的财报资料，从收入结构、利润质量、现金流、负债水平和风险因素五个维度生成研究摘要，并标注事实、观点和待验证假设。",
    starterRewrite: "请基于财报资料，分析这家公司的经营情况和主要风险。",
  },
  backend_developer: {
    label: "后端开发工程师",
    experience: 2,
    aiLevel: "中级",
    education: "本科",
    theoryScore: 74,
    taskType: "代码审查",
    weakTask: "帮我看看这段代码有没有问题。",
    strongTask: "请从正确性、安全性、性能、异常处理、可读性和测试覆盖六个维度审查以下接口代码，并给出风险等级、影响范围和验证方式。",
    starterRewrite: "请审查这段接口代码，指出问题并给出修改建议。",
  },
  admin_specialist: {
    label: "行政专员",
    experience: 3,
    aiLevel: "初级",
    education: "大专",
    theoryScore: 55,
    taskType: "会议纪要",
    weakTask: "把会议内容整理一下。",
    strongTask: "请将以下会议记录整理为会议纪要，包含会议主题、核心结论、争议问题、待办事项、负责人和截止时间；缺失信息请标注待确认。",
    starterRewrite: "请把会议记录整理成会议纪要和待办清单。",
  },
  product_manager: {
    label: "产品经理",
    experience: 4,
    aiLevel: "中级",
    education: "本科",
    theoryScore: 78,
    taskType: "需求分析",
    weakTask: "帮我整理一下需求。",
    strongTask: "请基于用户反馈和业务目标，梳理需求优先级，并输出 PRD 结构、风险点、验证指标和待验证假设。",
    starterRewrite: "请根据用户反馈整理需求优先级，并输出 PRD 框架。",
  },
  smart_manufacturing: {
    label: "智能制造",
    experience: 2,
    aiLevel: "初级",
    education: "本科",
    theoryScore: 66,
    taskType: "设备异常分析",
    weakTask: "帮我分析一下设备为什么报警。",
    strongTask: "基于设备报警记录、传感器数据和近期工艺参数变化，分析产线设备异常原因，输出可能原因、排查步骤、风险等级和人工复核建议。",
    starterRewrite: "请基于设备报警记录和传感器数据，分析设备异常原因并给出处置建议。",
  },
  industrial_internet: {
    label: "工业互联网",
    experience: 3,
    aiLevel: "中级",
    education: "本科",
    theoryScore: 70,
    taskType: "告警运维分析",
    weakTask: "帮我看看平台告警怎么处理。",
    strongTask: "基于工业互联网平台告警日志、设备运行状态和历史处置记录，分析告警原因、影响范围、优先级和运维处置流程，并标注需要人工确认的数据。",
    starterRewrite: "请基于平台告警日志和设备状态，分析告警原因并生成运维处置方案。",
  },
};

const fallbackAgents = [
  { agent: "职业诊断 Agent", tag: "画像诊断", summary: "已识别岗位、任务类型、能力短板和缺失信息。", score: 92, source: "前端演示" },
  { agent: "领域知识生成 Agent", tag: "训练资源", summary: "已生成提示词模板、岗位工作流、三阶训练题和复用检查清单。", score: 88, source: "前端演示" },
  { agent: "质量审核 Agent", tag: "反幻觉", summary: "已检查事实依据、合规风险、输出格式和待验证假设。", score: 86, source: "前端演示" },
  { agent: "反馈迭代 Agent", tag: "路径更新", summary: "已根据任务表现生成下一轮训练建议。", score: 80, source: "前端演示" },
];

const trainingModes = {
  prompt: {
    label: "提示词改写",
    kicker: "第 2 步：改写训练",
    title: "把上面的原始任务升级为高质量提示词",
    hint: "这里不是重新写一个无关任务，而是把上面的原始任务按“目标-资料-维度-格式-约束”五段式改写。改完后点击评分，系统会对比训练前后质量。",
    button: "评分",
    scoreTitle: "提示词评分",
    inputKicker: "第 1 步：输入你原本的提问",
    taskLabel: "训练前：你现在会怎么向 AI 说明工作需求",
    taskTip: "先按你平时的表达填写。系统会诊断缺失信息，再引导你补全目标、资料、格式和约束。",
    starter: (role) => role.starterRewrite,
  },
  workflow: {
    label: "任务拆解",
    kicker: "任务拆解训练",
    title: "把复杂岗位任务拆成可执行步骤",
    hint: "写出 5-7 个步骤，并说明每一步需要什么输入、产出什么结果。",
    button: "检查拆解",
    scoreTitle: "拆解评分",
    inputKicker: "第 1 步：确认要拆解的岗位工作",
    taskLabel: "本关任务：你想把哪项复杂工作拆成步骤",
    taskTip: "系统会检查步骤是否覆盖输入、处理、输出、审核和复盘，而不是继续训练提示词写法。",
    starter: (role) => `请将“${role.taskType}”任务拆解为 6 个步骤，包含目标确认、资料准备、分析维度、初稿生成、事实核验和最终输出。`,
  },
  review: {
    label: "结果审核",
    kicker: "结果审核训练",
    title: "检查 AI 输出是否可靠",
    hint: "从事实来源、待验证假设、风险点、人工复核和修改建议五个角度写审核意见。",
    button: "检查审核",
    scoreTitle: "审核训练评分",
    inputKicker: "第 1 步：确认结果审核任务",
    taskLabel: "本关任务：你要审核什么类型的 AI 结果",
    taskTip: "待审核的 AI 输出会单独显示。你需要写审核意见，而不是再次改写工作任务。",
    starter: (role) =>
      role.reviewSample
        ? `【待审核的既有 AI 输出】\n${role.reviewSample}\n\n请从事实来源、夸大表达、目标客户适配、人工复核和修改建议五个角度完成审核。注意：上面的内容是 AI 输出样例，不是用户的工作任务。`
        : "请检查这份 AI 生成结果：是否存在编造数据、缺少来源、结论过度绝对、格式不符合要求等问题，并给出修改建议。",
  },
  practice: {
    label: "岗位实战",
    kicker: "岗位实战训练",
    title: "完成一轮真实岗位任务成果",
    hint: "按岗位成果格式输出，注意结构、依据、行动建议和风险边界。",
    button: "评估实战",
    scoreTitle: "实战评分",
    inputKicker: "第 1 步：领取岗位实战任务",
    taskLabel: "本关任务：需要完成的岗位交付物",
    taskTip: "请像真实工作一样完成可使用的成果，系统会检查岗位贴合、专业依据、交付结构和风险边界。",
    starter: (role) => `请基于给定资料完成一份${role.label}${role.taskType}成果，包含摘要、关键分析、结论、风险提示和下一步行动。`,
  },
  test: {
    label: "分阶测试题",
    kicker: "分阶测试训练",
    title: "完成岗位专属分阶测试题",
    hint: "系统会根据岗位画像和知识库自动生成三道题。请在下方依次作答，注意写出依据、步骤和风险边界。",
    button: "提交测试",
    scoreTitle: "分阶测试评分",
    inputKicker: "第 1 步：读取本轮分阶测试范围",
    taskLabel: "本关任务：基础题、进阶题和挑战题的测试范围",
    taskTip: "进入后按顺序逐题作答。前一题完成后才能进入下一题，三题完成后统一评分。",
    starter: () => "请按“基础题、进阶题、挑战题”的顺序填写你的答案：\n\n基础题答案：\n\n进阶题答案：\n\n挑战题答案：",
  },
};

let latestResult = null;
let latestScore = null;
let currentTrainingMode = "prompt";
let currentTestStep = 0;
let testAnswers = ["", "", ""];
let trainingStage = "input";
let trainingAttempt = 1;
let currentHintLevel = 0;
let transferChallenge = null;
let activeReviewSample = null;
let theoryScoreSource = "系统示例值";
let trainingStartedAt = Date.now();
let roleChosen = false;

const roleSelect = document.querySelector("#roleSelect");
const roleChips = document.querySelectorAll(".role-chip");
const roleStartCards = document.querySelectorAll(".role-start-card");
const appNav = document.querySelector(".app-nav");
const appNavButtons = document.querySelectorAll(".app-nav button");
const viewSections = document.querySelectorAll(".view-section");
const skillList = document.querySelector("#skillList");
const agentList = document.querySelector("#agentList");
const progressOverview = document.querySelector("#progressOverview");
const taskInput = document.querySelector("#taskInput");
const workContextInput = document.querySelector("#workContextInput");
const generateTaskSeed = document.querySelector("#generateTaskSeed");
const taskSeedResult = document.querySelector("#taskSeedResult");
const rewriteInput = document.querySelector("#rewriteInput");
const reviewSource = document.querySelector("#reviewSource");
const reviewSourceText = document.querySelector("#reviewSourceText");
const trainingModeButtons = document.querySelectorAll(".training-mode");
const modeStartCards = document.querySelectorAll(".mode-start-card");
const trainingModeKicker = document.querySelector("#trainingModeKicker");
const trainingModeTitle = document.querySelector("#trainingModeTitle");
const trainingModeHint = document.querySelector("#trainingModeHint");
const trainingInputKicker = document.querySelector("#trainingInputKicker");
const taskInputLabel = document.querySelector("#taskInputLabel");
const taskInputTip = document.querySelector("#taskInputTip");
const allowExternalLLM = document.querySelector("#allowExternalLLM");
const masteryGoalStrip = document.querySelector("#masteryGoalStrip");
const hintCoach = document.querySelector("#hintCoach");
const hintCoachTitle = document.querySelector("#hintCoachTitle");
const hintContent = document.querySelector("#hintContent");
const activeTestQuestions = document.querySelector("#activeTestQuestions");
const fillStrongTask = document.querySelector("#fillStrongTask");
const runAgents = document.querySelector("#runAgents");
const scorePrompt = document.querySelector("#scorePrompt");
const scorePanel = document.querySelector("#scorePanel");
const clearHistory = document.querySelector("#clearHistory");
const goModeSelect = document.querySelector("#goModeSelect");
const backRoleSelect = document.querySelector("#backRoleSelect");
const goTraining = document.querySelector("#goTraining");
const backModeFromTraining = document.querySelector("#backModeFromTraining");
const backRoleFromTraining = document.querySelector("#backRoleFromTraining");
const historySummary = document.querySelector("#historySummary");
const historyList = document.querySelector("#historyList");
const diagnosisBox = document.querySelector("#diagnosisBox");
const diagnosisLevel = document.querySelector("#diagnosisLevel");
const diagnosisText = document.querySelector("#diagnosisText");
const diagnosisAction = document.querySelector("#diagnosisAction");
const resultContent = document.querySelector("#resultContent");
const tabButtons = document.querySelectorAll(".tabs button");
const profileRole = document.querySelector("#profileRole");
const profileExperience = document.querySelector("#profileExperience");
const profileAiLevel = document.querySelector("#profileAiLevel");
const profileTaskType = document.querySelector("#profileTaskType");
const profileEducation = document.querySelector("#profileEducation");
const profileTheoryScore = document.querySelector("#profileTheoryScore");
const trainingRoleText = document.querySelector("#trainingRoleText");
const trainingPositionText = document.querySelector("#trainingPositionText");
const railRoleText = document.querySelector("#railRoleText");
const railPositionText = document.querySelector("#railPositionText");
const railModeButtons = document.querySelectorAll(".rail-mode");
const trainingModeText = document.querySelector("#trainingModeText");
const trainingGoalText = document.querySelector("#trainingGoalText");
const specificPositionInput = document.querySelector("#specificPositionInput");
const experienceInput = document.querySelector("#experienceInput");
const aiLevelInput = document.querySelector("#aiLevelInput");
const educationInput = document.querySelector("#educationInput");
const theoryScoreInput = document.querySelector("#theoryScoreInput");
const testParticipantInput = document.querySelector("#testParticipantInput");
const profilePreview = document.querySelector("#profilePreview");
const startEntryTest = document.querySelector("#startEntryTest");
const closeEntryTest = document.querySelector("#closeEntryTest");
const submitEntryTest = document.querySelector("#submitEntryTest");
const entryTestArea = document.querySelector("#entryTestArea");
const entryQuestionList = document.querySelector("#entryQuestionList");
const entryTestResult = document.querySelector("#entryTestResult");
const trainingStageCards = document.querySelectorAll("[data-stage-card]");
const blindSpotList = document.querySelector("#blindSpotList");
const difficultyCurve = document.querySelector("#difficultyCurve");
const learningPath = document.querySelector("#learningPath");
const growthEvidence = document.querySelector("#growthEvidence");
const testCollectionStatus = document.querySelector("#testCollectionStatus");
const collectionNote = document.querySelector("#collectionNote");
const exportMyRecords = document.querySelector("#exportMyRecords");
const exportLocalRecords = document.querySelector("#exportLocalRecords");
const exportTestSummary = document.querySelector("#exportTestSummary");
const profileCenterCard = document.querySelector(".profile-center-card");

function currentRole() {
  return roleConfigs[roleSelect.value] || roleConfigs.marketing_manager;
}

function modeTaskFor(role, mode = currentTrainingMode) {
  if (role.modeTasks?.[mode]) return role.modeTasks[mode];
  const genericTasks = {
    prompt: role.weakTask,
    workflow: `我需要完成一项“${role.taskType}”工作，请把从资料准备到成果审核和复盘的全过程拆成可执行步骤。`,
    review: `请审核一份由 AI 生成的“${role.taskType}”结果，找出事实依据、风险边界、格式和岗位适用性方面的问题。`,
    practice: `请基于我提供的真实资料，完成一份可直接使用的“${role.taskType}”岗位成果，并标注依据和待核验信息。`,
    test: `请根据我的岗位画像和“${role.taskType}”知识库，依次生成并完成基础题、进阶题和挑战题。`,
  };
  return genericTasks[mode] || role.weakTask;
}

function defaultReviewSample(role = currentRole()) {
  const samples = {
    marketing_manager: "A 产品已经全面领先所有竞品，市场占有率达到 90%，用户一定会选择它。",
    industrial_marketing: role.reviewSample,
    finance_analyst: "这家公司明年利润必然增长 50%，现在买入没有任何风险。",
    backend_developer: "这段接口代码没有任何安全问题，可以直接上线，不需要补充测试。",
    admin_specialist: "会议中所有部门都已同意该方案，下周一定可以全部完成。",
    product_manager: "全部用户都喜欢这个功能，上线后留存率一定提升 30%。",
    smart_manufacturing: "设备报警一定是传感器故障，可以立即停机更换，无需查看工艺数据。",
    industrial_internet: "平台告警都是网络抖动导致的，直接清除即可，不需要人工复核。",
  };
  return samples[roleSelect.value] || `这份${role.taskType}结果完全正确，可以直接使用，不需要核验资料。`;
}

function reviewCandidateValue() {
  return String(reviewSourceText?.value || "").trim();
}

function currentProfile() {
  const role = currentRole();
  return {
    position: (specificPositionInput?.value || role.label).trim() || role.label,
    experience: Math.max(0, Math.min(30, Number(experienceInput?.value || role.experience))),
    aiLevel: aiLevelInput?.value || role.aiLevel,
    education: educationInput?.value || role.education,
    theoryScore: Math.max(0, Math.min(100, Number(theoryScoreInput?.value || role.theoryScore))),
    theoryScoreSource,
  };
}

function setTrainingStage(stage) {
  const stages = ["input", "rewrite", "scored", "retry"];
  trainingStage = stages.includes(stage) ? stage : "input";
  document.body.dataset.trainingStage = trainingStage;
  const activeIndex = stages.indexOf(trainingStage);
  trainingStageCards.forEach((card) => {
    const cardIndex = stages.indexOf(card.dataset.stageCard);
    card.classList.toggle("active", cardIndex === activeIndex);
    card.classList.toggle("done", cardIndex < activeIndex);
  });
  renderMasteryGoal();
}

function renderMasteryGoal() {
  if (!masteryGoalStrip) return;
  const config = trainingModes[currentTrainingMode];
  masteryGoalStrip.innerHTML = `
    <div><span>本关目标</span><strong>${config.title}</strong></div>
    <div><span>过关标准</span><strong>80 分</strong></div>
    <div><span>当前轮次</span><strong>第 ${trainingAttempt} 轮</strong></div>
  `;
}

function entryQuestions(role = currentRole()) {
  return [
    {
      title: "基础题 1：提示词结构",
      question: `如果你要让 AI 完成一项${role.taskType}任务，一个高质量指令至少应该包含哪些信息？`,
      options: [
        "任务目标、输入资料、分析维度、输出格式和约束条件",
        "只要告诉 AI 帮我做一下就可以",
        "只写岗位名称，不需要写资料",
      ],
      answer: 0,
    },
    {
      title: "基础题 2：资料来源",
      question: "当 AI 需要分析事实性内容，但你没有提供资料时，最合适的做法是什么？",
      options: ["让 AI 自己编完整数据", "要求 AI 标注待核验信息，并提示需要补充资料来源", "删除所有风险提示"],
      answer: 1,
    },
    {
      title: "基础题 3：输出格式",
      question: "为什么要在提示词里写清输出格式？",
      options: ["可以让结果更稳定、更方便复用和检查", "只是为了让文字变长", "输出格式不影响结果质量"],
      answer: 0,
    },
    {
      title: "基础题 4：反幻觉",
      question: "下面哪句话最能降低大模型编造风险？",
      options: ["请自由发挥，越详细越好", "不得编造数据；无法确认的信息请标注为待验证", "请保证所有结论都正确"],
      answer: 1,
    },
    {
      title: "基础题 5：任务拆解",
      question: `面对复杂的${role.taskType}任务，比较好的训练方式是什么？`,
      options: ["直接让 AI 一次性完成全部内容", "先拆目标、资料、步骤、输出和复核点，再逐步生成", "只看最终答案，不检查过程"],
      answer: 1,
    },
  ];
}

function renderEntryTest() {
  const questions = entryQuestions();
  entryQuestionList.innerHTML = questions
    .map(
      (item, index) => `
        <article class="entry-question">
          <strong>${item.title}</strong>
          <p>${item.question}</p>
          ${item.options
            .map(
              (option, optionIndex) => `
                <label>
                  <input type="radio" name="entry_q_${index}" value="${optionIndex}" />
                  <span>${option}</span>
                </label>
              `,
            )
            .join("")}
        </article>
      `,
    )
    .join("");
}

function submitEntryAssessment() {
  const questions = entryQuestions();
  let correct = 0;
  questions.forEach((item, index) => {
    const checked = document.querySelector(`input[name="entry_q_${index}"]:checked`);
    if (checked && Number(checked.value) === item.answer) correct += 1;
  });
  const score = correct * 20;
  theoryScoreInput.value = score;
  theoryScoreSource = "入门测评生成";
  entryTestResult.textContent = `入门测评完成：答对 ${correct}/5，基础测评分已更新为 ${score} 分。`;
  renderProfilePreview();
  renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
}

function profileAdaptation(profile = currentProfile()) {
  const score = profile.theoryScore;
  const isBeginner = profile.aiLevel === "初级" || score < 65 || profile.experience <= 1;
  const isAdvanced = profile.aiLevel === "高级" || (score >= 80 && profile.experience >= 4);
  if (isBeginner) {
    return {
      stage: "基础巩固",
      difficulty: "中低",
      task: "先训练提示词结构化表达和任务信息补全",
    };
  }
  if (isAdvanced) {
    return {
      stage: "进阶挑战",
      difficulty: "较高",
      task: "推荐岗位实战、结果审核和交叉验证任务",
    };
  }
  return {
    stage: "专项提升",
    difficulty: "中等",
    task: "推荐任务拆解、事实核验和分阶测试题",
  };
}

function analyzeInitialProfile(profile = currentProfile(), role = currentRole()) {
  const educationScore = { 大专: 58, 本科: 68, 硕士: 78, 博士: 86 }[profile.education] || 65;
  const aiScore = { 初级: 42, 中级: 68, 高级: 86 }[profile.aiLevel] || 42;
  const experienceScore = Math.min(92, 45 + profile.experience * 8);
  const theoryScore = profile.theoryScore;
  const baseline = Math.round(theoryScore * 0.35 + aiScore * 0.3 + experienceScore * 0.2 + educationScore * 0.15);
  const adaptation = profileAdaptation(profile);
  const blindSpots = [];
  const strengths = [];

  if (profile.aiLevel === "初级") blindSpots.push("AI 提问容易缺少背景、格式和约束");
  if (theoryScore < 65) blindSpots.push("理论基础偏弱，适合先做基础题和示范引导");
  if (profile.experience <= 1) blindSpots.push("岗位经验较少，需要更多样例任务和步骤提示");
  if (profile.experience >= 4) strengths.push("岗位经验较充分，适合使用真实任务进行训练");
  if (theoryScore >= 75) strengths.push("理论基础较好，可以加入事实核验和进阶挑战");
  if (profile.aiLevel !== "初级") strengths.push("已有 AI 使用基础，可以缩短模板提示，增加自主拆解");

  const route =
    baseline < 60
      ? ["示范学习", "提示词补全", "基础题", "二次改写"]
      : baseline < 78
        ? ["任务拆解", "结果审核", "分阶测试", "岗位实战"]
        : ["真实项目", "交叉验证", "红队审核", "进阶挑战"];
  const difficulty =
    baseline < 60
      ? { label: "低到中", level: 48, reason: "先降低题目复杂度，用模板和填空帮助上手" }
      : baseline < 78
        ? { label: "中等", level: 66, reason: "保留一定挑战，重点训练拆解和核验" }
        : { label: "中高", level: 82, reason: "可进入复杂任务和反幻觉挑战" };

  return {
    baseline,
    adaptation,
    educationScore,
    aiScore,
    experienceScore,
    theoryScore,
    blindSpots: blindSpots.length ? blindSpots : ["暂未发现明显基础短板，建议进入专项提升"],
    strengths: strengths.length ? strengths : ["可通过岗位样例快速建立任务表达框架"],
    route,
    difficulty,
    resourcePolicy: `${role.taskType}资源优先匹配“${difficulty.label}”难度，题目会按基础题、进阶题、挑战题递进生成。`,
  };
}

function renderProfilePreview() {
  const profile = currentProfile();
  const role = currentRole();
  const analysis = analyzeInitialProfile(profile, role);
  profilePreview.innerHTML = `
    <div class="profile-diagnosis-score">
      <span>综合起点分</span>
      <strong>${analysis.baseline}</strong>
      <small>${escapeHtml(analysis.adaptation.stage)} / 资源难度：${escapeHtml(analysis.difficulty.label)}</small>
    </div>
    <div class="profile-dimension-grid">
      <div><span>岗位经验</span><strong>${analysis.experienceScore}</strong></div>
      <div><span>AI 使用</span><strong>${analysis.aiScore}</strong></div>
      <div><span>理论基础</span><strong>${analysis.theoryScore}</strong></div>
      <div><span>学历背景</span><strong>${analysis.educationScore}</strong></div>
    </div>
    <div class="profile-diagnosis-block">
      <span>识别出的知识盲区</span>
      <ul>${analysis.blindSpots.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
    <div class="profile-diagnosis-block">
      <span>可利用的学习优势</span>
      <ul>${analysis.strengths.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
    <div class="profile-route-row">
      <div class="profile-route">
        ${analysis.route.map((item, index) => `<b>${index + 1}. ${escapeHtml(item)}</b>`).join("")}
      </div>
      <button class="info-dot" type="button" aria-label="查看画像分析依据">
        !
        <span class="info-tip info-tip-wide" role="tooltip">
          <b>资源难度：</b>${escapeHtml(analysis.resourcePolicy)}<br /><br />
          <b>数据来源：</b>AI 水平为学习者自评；基础测评分为${escapeHtml(profile.theoryScoreSource)}。<br /><br />
          <b>推荐任务：</b>${escapeHtml(analysis.adaptation.task)}${role.profileSource ? `<br /><br /><b>画像说明：</b>${escapeHtml(role.profileSource)}` : ""}
        </span>
      </button>
    </div>
  `;
}

function applyRoleDefaultsToProfile() {
  const role = currentRole();
  specificPositionInput.value = role.label;
  experienceInput.value = role.experience;
  aiLevelInput.value = role.aiLevel;
  educationInput.value = role.education;
  theoryScoreInput.value = role.theoryScore;
}

function switchView(view) {
  const targetView = view || "train";
  appNav.classList.toggle("visible", !["role", "mode"].includes(targetView));
  appNavButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === targetView);
  });
  viewSections.forEach((section) => {
    const isTarget = section.dataset.section === targetView;
    section.classList.toggle("hidden-section", !isTarget);
    if (isTarget) {
      section.classList.remove("view-enter");
      void section.offsetWidth;
      section.classList.add("view-enter");
    }
  });
}

function selectRole(roleId, reset = true) {
  roleSelect.value = roleConfigs[roleId] ? roleId : "marketing_manager";
  roleChosen = true;
  revealProfileCenter();
  syncRoleCards();
  if (reset) {
    resetForRole();
  }
}

function revealProfileCenter() {
  if (!profileCenterCard) return;
  profileCenterCard.classList.add("visible");
  profileCenterCard.classList.remove("profile-reload");
  void profileCenterCard.offsetWidth;
  profileCenterCard.classList.add("profile-reload");
}

function selectMode(mode, preserveAnswer = false) {
  if (mode !== currentTrainingMode) {
    transferChallenge = null;
    activeReviewSample = null;
  }
  setTrainingMode(trainingModes[mode] ? mode : "prompt", preserveAnswer);
  if (!preserveAnswer) {
    taskInput.value = modeTaskFor(currentRole(), currentTrainingMode);
    renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
  }
  syncModeCards();
}

function historyKey() {
  return `promptcraft_training_history_${profileStorageId()}`;
}

function reviewKey() {
  return `promptcraft_review_queue_${profileStorageId()}`;
}

function testParticipantCode() {
  return String(testParticipantInput?.value || "")
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9_-]/g, "")
    .slice(0, 20);
}

function profileStorageId() {
  const participantCode = testParticipantCode();
  if (participantCode) return `test_${participantCode}_${roleSelect.value}`;
  const key = "promptcraft_local_learner_id";
  let learnerId = localStorage.getItem(key);
  if (!learnerId) {
    learnerId = `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 9)}`;
    localStorage.setItem(key, learnerId);
  }
  return `${learnerId}_${roleSelect.value}`;
}

function startTrainingTimer() {
  trainingStartedAt = Date.now();
}

function elapsedTrainingSeconds() {
  return Math.max(1, Math.min(86400, Math.round((Date.now() - trainingStartedAt) / 1000)));
}

function updateCollectionStatus(message = "") {
  const code = testParticipantCode();
  if (testCollectionStatus) testCollectionStatus.textContent = code ? `正式测试：${code}` : "普通体验模式";
  if (collectionNote) {
    collectionNote.textContent =
      message ||
      (code
        ? `编号 ${code} 的评分、用时、薄弱项和成长变化将在提交后保存到后台。`
        : "填写匿名测试编号并提交评分后，后台会自动记录得分、用时、薄弱项和成长变化。");
  }
}

function downloadJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

async function exportCurrentTesterData() {
  const code = testParticipantCode();
  if (!code) {
    updateCollectionStatus("请先在个人中心填写匿名测试编号，例如 T001，再进行训练和导出。");
    return;
  }
  try {
    const query = new URLSearchParams({ learner_id: profileStorageId(), role_id: roleSelect.value });
    const response = await fetch(`${API_BASE}/api/records?${query.toString()}`);
    if (!response.ok) throw new Error("backend unavailable");
    const data = await response.json();
    downloadJson(`${code}_${roleSelect.value}_训练记录.json`, {
      data_scope: "匿名测试者训练记录",
      participant_code: code,
      exported_at: new Date().toISOString(),
      records: data.records || [],
    });
    updateCollectionStatus(`已导出 ${code} 的 ${(data.records || []).length} 条后台记录。`);
  } catch (error) {
    updateCollectionStatus("导出失败：请确认一键启动窗口仍在运行，并至少提交过一次评分。");
  }
}

async function exportFormalTestSummary() {
  try {
    const response = await fetch(`${API_BASE}/api/test-summary`);
    if (!response.ok) throw new Error("backend unavailable");
    const data = await response.json();
    downloadJson(`智训工坊_正式测试汇总_${new Date().toISOString().slice(0, 10)}.json`, data);
    updateCollectionStatus(`已导出 ${data.participant_count || 0} 名匿名测试者、${data.record_count || 0} 条正式记录。`);
  } catch (error) {
    updateCollectionStatus("汇总导出失败：请确认后端正在运行。");
  }
}

function legacyProfileStorageId() {
  const profile = currentProfile();
  const raw = [roleSelect.value, profile.position, profile.experience, profile.aiLevel, profile.education, profile.theoryScore].join("|");
  let hash = 0;
  for (let index = 0; index < raw.length; index += 1) hash = (hash * 31 + raw.charCodeAt(index)) >>> 0;
  return `${roleSelect.value}_${hash.toString(36)}`;
}

function loadHistory() {
  try {
    if (!localStorage.getItem(historyKey())) {
      const legacy = localStorage.getItem(`promptcraft_training_history_${legacyProfileStorageId()}`);
      if (legacy) localStorage.setItem(historyKey(), legacy);
    }
    return JSON.parse(localStorage.getItem(historyKey()) || "[]");
  } catch (error) {
    return [];
  }
}

function exportLocalHistoryData() {
  const records = loadHistory();
  if (!records.length) {
    updateCollectionStatus("本机没有可导出的训练记录，请先至少完成一次评分。");
    return;
  }
  const code = testParticipantCode() || "LOCAL";
  downloadJson(`${code}_${roleSelect.value}_本机训练记录.json`, {
    data_scope: "浏览器本机训练记录，包含尚未同步到后台的历史记录",
    privacy_notice: "分享前请检查并删除姓名、手机号、企业内部资料等敏感信息",
    participant_code: testParticipantCode(),
    learner_id: profileStorageId(),
    role_id: roleSelect.value,
    exported_at: new Date().toISOString(),
    record_count: records.length,
    records,
  });
  updateCollectionStatus(`已导出本机显示的 ${records.length} 条训练记录。`);
}

function saveHistory(records) {
  localStorage.setItem(historyKey(), JSON.stringify(records.slice(-30)));
}

function loadReviewQueue() {
  try {
    if (!localStorage.getItem(reviewKey())) {
      const legacy = localStorage.getItem(`promptcraft_review_queue_${legacyProfileStorageId()}`);
      if (legacy) localStorage.setItem(reviewKey(), legacy);
    }
    return JSON.parse(localStorage.getItem(reviewKey()) || "[]");
  } catch (error) {
    return [];
  }
}

function saveReviewQueue(items) {
  localStorage.setItem(reviewKey(), JSON.stringify(items.slice(-20)));
}

function scheduleReview(record) {
  if (!record.passed) return;
  const queue = loadReviewQueue().filter((item) => !(item.mode === record.mode && item.task === record.task));
  const dueAt = Date.now() + 3 * 24 * 60 * 60 * 1000;
  queue.push({ mode: record.mode, task: record.task, dueAt, score: record.score });
  saveReviewQueue(queue);
}

function differentPassedTasks(records, modeLabel) {
  return new Set(records.filter((record) => record.mode === modeLabel && record.passed).map((record) => record.task)).size;
}

function modeEvidence(records, modeLabel) {
  const modeRecords = records.filter((record) => record.mode === modeLabel);
  const basePassed = modeRecords.some((record) => record.passed && !record.isTransfer);
  const transferPassed = modeRecords.some((record) => record.passed && record.isTransfer);
  return {
    attempted: modeRecords.length > 0,
    best: modeRecords.length ? Math.max(...modeRecords.map((record) => record.score)) : null,
    taskPassed: basePassed,
    transferPassed,
    stableMastery: basePassed && transferPassed,
  };
}

function saveTrainingRecord(score, submittedAnswer = rewriteInput.value.trim()) {
  const records = loadHistory();
  const sameTaskRecords = records.filter(
    (record) => record.mode === trainingModes[currentTrainingMode].label && record.task === taskInput.value.trim(),
  );
  const previous = sameTaskRecords[sameTaskRecords.length - 1];
  const decision = buildAdaptiveDecision(score);
  const isTransfer = Boolean(transferChallenge && taskInput.value.trim() === transferChallenge);
  const firstBaseline = currentTrainingMode === "prompt" ? Math.max(0, score.score - Number(score.improved || 0)) : score.score;
  const record = {
    time: new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" }),
    role: currentRole().label,
    mode: trainingModes[currentTrainingMode].label,
    task: taskInput.value.trim(),
    rewritten: submittedAnswer,
    score: score.score,
    level: score.level,
    improved: previous ? score.score - previous.score : currentTrainingMode === "prompt" ? score.improved : 0,
    baselineGain: currentTrainingMode === "prompt" ? score.improved : 0,
    previousScore: previous ? previous.score : firstBaseline,
    previousAnswer: previous ? previous.rewritten : currentTrainingMode === "prompt" ? taskInput.value.trim() : "首次作答，暂无上一轮答案",
    attempt: sameTaskRecords.length + 1,
    passed: decision.mastery_passed,
    isTransfer,
    decision: decision.strategy,
    focus: decision.weak_dimensions.join("、") || "证据链和岗位落地",
  };
  records.push(record);
  saveHistory(records);
  scheduleReview(record);
  return record;
}

function formatDelta(value) {
  const number = Number(value || 0);
  return `${number >= 0 ? "+" : ""}${number}`;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function shortExcerpt(value, limit = 100) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return escapeHtml(text.length > limit ? `${text.slice(0, limit)}...` : text || "未填写");
}

function transferTaskFor(role = currentRole(), mode = currentTrainingMode) {
  const contexts = {
    marketing_manager: "新品进入陌生区域市场，需要结合另一组访谈、公开竞品资料和销售反馈制定进入策略",
    industrial_marketing: "面向制药企业采购人员，使用另一组公开阀门资料制作 20 秒短视频，并设置提交工况获取选型建议的入口",
    finance_analyst: "使用另一家公司的年报和现金流资料分析经营质量与主要风险",
    backend_developer: "审查一个不同业务接口，覆盖安全、异常、性能和测试证据",
    admin_specialist: "整理一次跨部门项目复盘，提取结论、争议、待办、负责人和待确认信息",
    product_manager: "使用另一类用户反馈完成需求分析、优先级判断和验证指标设计",
    smart_manufacturing: "使用一组不同设备告警、传感器和工艺参数分析异常",
    industrial_internet: "使用一次不同平台告警、设备日志和历史处置记录制定运维方案",
  };
  const context = contexts[roleSelect.value] || `处理另一个${role.taskType}情境`;
  const tasks = {
    prompt: `请围绕以下新情境独立写一条高质量 AI 指令：${context}。必须说明资料、输出和风险边界。`,
    workflow: `请把以下新情境拆成可执行工作流，每步写清输入、动作、产出、复核和失败风险：${context}。`,
    review: `请审核以下新情境中的 AI 结果，逐条写出问题、依据、风险等级、修改建议和人工复核点：${context}。`,
    practice: `请针对以下新情境独立完成一份可交付岗位成果，包含依据、行动和待核验项：${context}。`,
    test: `请围绕以下新情境依次完成基础、进阶和挑战三道迁移题，并写出依据与风险边界：${context}。`,
  };
  return {
    task: tasks[mode] || tasks.prompt,
    reviewSample:
      roleSelect.value === "industrial_marketing" && mode === "review"
        ? "这套阀门适用于所有制药产线，证书齐全，任何工况都能直接使用，保证当天解决问题。"
        : null,
  };
}

function hintText(level) {
  const role = currentRole();
  const config = trainingModes[currentTrainingMode];
  const modeHints = {
    prompt: [
      `先问自己：这项${role.taskType}要解决谁的什么问题？`,
      "至少补齐三项：可用资料、分析维度、交付对象；再写一条不得编造的边界。",
      "目标：……\n资料：……\n分析维度：……\n输出格式：……\n约束与待核验项：……",
    ],
    workflow: [
      "先写起点和终点：输入是什么，最后要交付什么。",
      "每一步都用“输入资料 → 处理动作 → 阶段产出 → 复核点”描述。",
      "1. 确认目标\n2. 收集资料\n3. 建立维度\n4. 分析处理\n5. 事实核验\n6. 输出与复核",
    ],
    review: [
      "先找一句最可能被编造或夸大的结论。",
      "逐条检查：事实来源、待验证假设、风险等级、人工复核、修改建议。",
      "问题：……\n依据/缺失证据：……\n风险等级：……\n修改建议：……\n人工复核：……",
    ],
    practice: [
      "先确定这份成果最终由谁阅读、拿来做什么决定。",
      "用“结论摘要—关键分析—证据—行动—风险边界”组织成果。",
      `【${role.taskType}成果】\n结论摘要：……\n关键分析与依据：……\n下一步行动：……\n风险与待核验：……`,
    ],
    test: [
      "先回答当前这一题，不需要一次完成三题。",
      "基础题看要素，进阶题看拆解，挑战题看岗位成果与证据边界。",
      "答案应包含：判断/结论、理由或依据、具体步骤、风险边界。",
    ],
  };
  const values = modeHints[currentTrainingMode] || modeHints.prompt;
  return { title: `${config.label} · 第 ${level} 级提示`, text: values[Math.max(0, Math.min(2, level - 1))] };
}

function showHint(level) {
  currentHintLevel = Math.max(currentHintLevel, level);
  const hint = hintText(level);
  hintCoachTitle.textContent = hint.title;
  hintContent.textContent = hint.text;
  hintContent.classList.remove("hidden-block");
}

function resetHints() {
  currentHintLevel = 0;
  if (!hintContent) return;
  hintCoachTitle.textContent = "先独立尝试，再按需要逐级查看";
  hintContent.textContent = "";
  hintContent.classList.add("hidden-block");
}

function renderModeStatus() {
  const records = loadHistory();
  document.querySelectorAll("[data-mode-status]").forEach((node, index) => {
    const evidence = modeEvidence(records, node.dataset.modeStatus);
    node.className = `mode-card-status ${evidence.stableMastery ? "mastered" : evidence.taskPassed ? "passed" : evidence.attempted ? "learning" : ""}`;
    node.textContent = evidence.stableMastery
      ? "稳定掌握"
      : evidence.taskPassed
        ? "本题达标·待迁移"
        : evidence.attempted
          ? `补练中·最高 ${evidence.best}`
          : index === 0
            ? "推荐起点"
            : "待训练";
  });
}

function renderHistory() {
  const records = loadHistory();
  updateCollectionStatus();
  renderModeStatus();
  if (!records.length) {
    historySummary.innerHTML = `
      <div class="history-card"><span>训练次数</span><strong>0</strong></div>
      <div class="history-card"><span>最高分</span><strong>-</strong></div>
      <div class="history-card"><span>最近提升</span><strong>-</strong></div>
    `;
    historyList.innerHTML = `
      <div class="empty-score">
        <strong>暂无训练记录</strong>
        <p>完成一次提示词评分后，这里会记录得分变化和训练轨迹。</p>
      </div>
    `;
    renderGrowthEvidence();
    return;
  }

  const best = Math.max(...records.map((record) => record.score));
  const latest = records[records.length - 1];
  historySummary.innerHTML = `
    <div class="history-card"><span>训练次数</span><strong>${records.length}</strong></div>
    <div class="history-card"><span>最高分</span><strong>${best}</strong></div>
    <div class="history-card"><span>最近一轮变化</span><strong>${formatDelta(latest.improved)}</strong></div>
  `;
  historyList.innerHTML = records
    .slice()
    .reverse()
    .map(
      (record, index) => `
        <article class="history-item">
          <time>${record.time}</time>
          <div>
            <span>${escapeHtml(record.role)} / ${escapeHtml(record.mode || "提示词改写")} / 第 ${record.attempt || records.length - index} 轮</span>
            <p>${shortExcerpt(record.rewritten || record.task, 180)}</p>
          </div>
          <div class="history-score">
            <strong>${record.score}</strong>
            <span>${record.passed ? "已达标" : record.decision || record.level} / ${formatDelta(record.improved)}</span>
          </div>
        </article>
      `,
    )
    .join("");
  renderGrowthEvidence();
}

function renderGrowthEvidence() {
  if (!growthEvidence) return;
  const records = loadHistory();
  const modeOrder = ["提示词改写", "任务拆解", "结果审核", "岗位实战", "分阶测试题"];
  if (!records.length) {
    growthEvidence.innerHTML = `
      <div class="growth-empty">
        <strong>还没有训练证据</strong>
        <p>完成第一次评分后，这里会显示训练前后分数、已达标关卡和下一项弱点补练。</p>
      </div>
    `;
    return;
  }

  const first = records[0];
  const latest = records[records.length - 1];
  const estimatedBaseline = Math.max(0, first.score - Number(first.baselineGain || 0));
  const best = Math.max(...records.map((record) => record.score));
  const passedModes = new Set(records.filter((record) => record.passed).map((record) => record.mode));
  const masteredModes = new Set(modeOrder.filter((mode) => modeEvidence(records, mode).stableMastery));
  const dueReviews = loadReviewQueue().filter((item) => item.dueAt <= Date.now());
  growthEvidence.innerHTML = `
    <div class="growth-proof-summary">
      <div><span>训练前估算</span><strong>${estimatedBaseline}</strong></div>
      <div><span>当前最高</span><strong>${best}</strong></div>
      <div><span>累计训练</span><strong>${records.length} 轮</strong></div>
      <div><span>稳定掌握</span><strong>${masteredModes.size}/5</strong></div>
    </div>
    <div class="mastery-route">
      ${modeOrder
        .map((mode, index) => {
          const modeRecords = records.filter((record) => record.mode === mode);
          const modeBest = modeRecords.length ? Math.max(...modeRecords.map((record) => record.score)) : null;
          const evidence = modeEvidence(records, mode);
          const status = evidence.stableMastery ? "passed" : modeRecords.length ? "learning" : "locked";
          const label = evidence.stableMastery ? `稳定掌握 ${modeBest}` : evidence.taskPassed ? `本题达标·待迁移 ${modeBest}` : status === "learning" ? `补练中 ${modeBest}` : "未开始";
          return `<div class="mastery-node ${status}"><b>${index + 1}</b><span>${mode}<small>${label}</small></span></div>`;
        })
        .join("")}
    </div>
    <div class="next-focus"><strong>${dueReviews.length ? `有 ${dueReviews.length} 项到期复练` : "下一步专项补练"}</strong><span>${escapeHtml(dueReviews.length ? "换一个相似情境独立作答，检验是否真正记住。" : latest.focus || "继续补全证据链和岗位边界")}</span></div>
  `;
}

function buildFallbackResult(roleId, task) {
  const role = roleConfigs[roleId];
  const profile = currentProfile();
  const profileAnalysis = analyzeInitialProfile(profile, role);
  const position = profile.position || role.label;
  const isVague = task.trim().length < 20;
  const missingInfo = fallbackMissingInfo(roleId, task);
  const fallbackClarity = isVague ? "低" : missingInfo.length >= 3 ? "中" : "高";
  const reviewTarget = currentTrainingMode === "review" ? activeReviewSample || reviewCandidateValue() || defaultReviewSample(role) : "";
  const hasRiskyClaim =
    roleId === "industrial_marketing" && /半夜三点|立马上门|证件齐全|全网第一|保证成交|所有制药产线|保证当天/.test(reviewTarget);
  const needsDiagnosis = fallbackClarity !== "高";
  const testQuestions = buildTieredTests(role, position);
  const fallbackResources = buildFallbackModeResources(role, position, task, reviewTarget, testQuestions);

  const knowledgeSources =
    roleId === "industrial_marketing"
      ? ["工业品网络营销_卫生级阀门公开资料.md", "职场AI使用规范.md"]
      : ["职场AI使用规范.md", `${role.taskType}知识切片.md`];

  return {
    mode: "offline_frontend_fallback",
    knowledge: { sources: knowledgeSources },
    diagnosis: {
      task_clarity: fallbackClarity,
      missing_info: missingInfo.slice(0, 5),
      next_action: needsDiagnosis ? "启动动态追问" : "生成训练资源",
      summary: isVague
        ? "当前指令过于模糊，需要补充任务目标、资料来源和输出格式。"
        : fallbackClarity === "中"
          ? `当前任务已有方向，但仍缺少${missingInfo.slice(0, 3).join("、")}等关键信息。`
          : "任务目标和岗位场景较清晰，可以进入资源生成。",
    },
    generation: {
      resources: {
        prompt_template: fallbackResources.promptTemplate,
        workflow: fallbackResources.workflow,
        practice_tasks: testQuestions,
        checklist: fallbackResources.checklist,
      },
    },
    review: {
      score: needsDiagnosis ? 76 : 88,
      passed: ["已检查任务目标和输出格式。", "已加入反幻觉约束。"],
      risks: isVague
        ? ["原始指令过于模糊，直接生成容易产生幻觉。"]
        : hasRiskyClaim
          ? ["待审核内容含夸大服务承诺或证件概括，需由人工核验后再发布。"]
          : ["未发现明显幻觉或合规风险。"],
      resource_risks: isVague ? ["原始指令过于模糊，需要追问后再生成资源。"] : [],
      target_findings: hasRiskyClaim ? ["待审核内容含夸大服务承诺或证件概括。"] : [],
      suggestions: ["关键判断应标注资料来源。", "无法确认的信息应标注为待验证假设。"],
      red_team_tests: ["诱导模型编造缺失数据，检查是否拒绝。", "要求绕过合规边界，检查是否提示人工复核。"],
      cross_checks: ["将关键结论与资料来源逐条对应。", "无法确认的信息统一标记为待验证。"],
      summary: `资源审核评分 ${needsDiagnosis ? 76 : 88}/100；另识别待审核内容风险 ${hasRiskyClaim ? 1 : 0} 项。`,
    },
    feedback: {
      training_level: needsDiagnosis ? "专项提升" : "进阶挑战",
      mastery: {
        任务表达: Math.min(92, Math.max(45, profileAnalysis.baseline + (isVague ? -8 : 8))),
        提示词结构: Math.min(92, Math.max(42, profileAnalysis.aiScore + (isVague ? -4 : 10))),
        工作流拆解: Math.min(88, Math.max(45, profileAnalysis.experienceScore + 4)),
        事实核验: Math.min(86, Math.max(38, profileAnalysis.theoryScore + (profile.aiLevel === "初级" ? -8 : 4))),
        合规使用: Math.min(88, Math.max(45, profileAnalysis.educationScore + 8)),
      },
      next_task: `${profileAnalysis.adaptation.stage}：${needsDiagnosis ? "先补全目标客户、公开资料、发布规格、行动入口和事实边界。" : profileAnalysis.adaptation.task}`,
      micro_goals: profileAnalysis.route.map((item) => `完成“${item}”训练节点`),
      coach_feedback: `画像诊断显示综合起点分为 ${profileAnalysis.baseline}，${profileAnalysis.difficulty.reason}。`,
      blind_spots: needsDiagnosis
        ? [...profileAnalysis.blindSpots, hasRiskyClaim ? "当前文案含未经核验的宣传承诺" : "当前原始任务仍偏模糊"]
        : profileAnalysis.blindSpots,
      resource_match_curve: [
        { stage: "基础讲义", difficulty: Math.max(35, profileAnalysis.difficulty.level - 16), match: profileAnalysis.baseline < 60 ? 90 : 74 },
        { stage: "实操指南", difficulty: profileAnalysis.difficulty.level, match: profileAnalysis.baseline < 78 ? 86 : 78 },
        { stage: "分阶测试", difficulty: Math.min(92, profileAnalysis.difficulty.level + 12), match: isVague ? 62 : 84 },
      ],
      learning_path: profileAnalysis.route,
    },
    agents: fallbackAgents,
  };
}

function fallbackMissingInfo(roleId, task) {
  const requirements = {
    industrial_marketing: [
      ["目标客户", /老板|采购|客户|目标受众/],
      ["应用场景", /食品|制药|灭菌|CIP|清洗|应用场景/],
      ["公开资料", /公开|资料|来源|产品页|展会|报道/],
      ["平台与时长", /抖音|快手|视频号|B站|小红书|秒|平台/],
      ["行动入口", /私信|咨询|选型|提交工况|获取/],
      ["事实边界", /不得编造|待核验|来源|人工复核/],
    ],
    marketing_manager: [["竞品对象", /竞品|产品/], ["分析维度", /维度|体验|功能|风险/], ["资料来源", /资料|数据|来源/], ["输出格式", /报告|表格|清单|输出/]],
    finance_analyst: [["财报资料", /财报|收入|利润|现金流/], ["分析周期", /季度|年度|周期/], ["风险维度", /风险|负债|合规/], ["输出格式", /报告|摘要|表格/]],
  };
  const checks = requirements[roleId] || [["输入资料", /资料|数据|记录|代码|反馈/], ["处理维度", /维度|步骤|风险|优先级/], ["输出格式", /报告|清单|表格|纪要|PRD/], ["事实边界", /来源|待核验|不得编造|人工复核/]];
  return checks.filter(([, pattern]) => !pattern.test(task)).map(([label]) => label);
}

function buildFallbackModeResources(role, position, task, reviewTarget, testQuestions) {
  const defaults = {
    promptTemplate: `你是一名${position}岗位的 AI 实训教练，所属方向为${role.label}。请围绕以下任务生成岗位化成果：\n\n${task}\n\n输出要求：\n1. 先给出结论摘要。\n2. 拆解任务步骤。\n3. 标注事实、观点和待验证假设。\n4. 给出下一步行动建议。\n5. 不得编造数据或来源。`,
    workflow: ["明确目标", "补充资料", "拆解维度", "生成初稿", "审核事实", "输出结果"],
    checklist: ["角色明确", "目标明确", "维度清晰", "格式清晰", "包含反幻觉约束"],
  };
  if (currentTrainingMode === "workflow") {
    return {
      promptTemplate: `请把“${task}”拆成 5-7 个可执行步骤，每步写清输入、动作、产出、复核和失败风险。`,
      workflow: ["确认目标与边界", "收集输入资料", "执行核心处理", "形成阶段产出", "事实与质量复核", "交付并复盘"],
      checklist: ["步骤顺序明确", "每步有输入和产出", "包含复核动作", "说明失败风险", "最终成果可检查"],
    };
  }
  if (currentTrainingMode === "review") {
    return {
      promptTemplate: `请审核下面的 AI 输出，而不是重新完成原任务：\n\n${reviewTarget || "尚未提供待审核内容"}\n\n按问题原句、核验依据、风险等级、修改建议和人工复核点输出。`,
      workflow: ["定位事实性主张", "查找公开来源", "识别夸大和幻觉", "判断风险等级", "提出修改建议", "标记人工复核"],
      checklist: ["逐句定位问题", "核验事实来源", "识别夸大表达", "给出可执行修改", "标明人工复核点"],
    };
  }
  if (currentTrainingMode === "practice") {
    return {
      promptTemplate: `请以${position}身份完成“${task}”的正式岗位交付物，包含结论、资料依据、行动建议、风险边界和待核验清单。`,
      workflow: defaults.workflow,
      checklist: ["成果可直接交付", "贴合岗位对象", "结论有资料依据", "行动建议明确", "风险边界清楚"],
    };
  }
  if (currentTrainingMode === "test") {
    return {
      promptTemplate: `请按顺序完成${role.label}的基础、进阶和挑战三道题；每题写出结论、理由、依据和风险边界。`,
      workflow: ["完成基础题", "检查必要要素", "完成进阶题", "说明流程依据", "完成挑战题", "核验风险边界"],
      checklist: ["三题均已完成", "进阶题有推理步骤", "挑战题形成岗位成果", "说明资料依据", "标明风险边界"],
    };
  }
  return defaults;
}

function generateTaskSeedOffline(role, profile, context) {
  const base = (context.trim() || `${profile.position || role.label}的日常岗位任务`).replace(/[。；;，,\s]+$/g, "");
  const templates = {
    市场经理: `请围绕“${base}”，生成一项市场推广训练任务，要求明确目标客户、产品卖点、传播渠道、输出格式和事实核验要求。`,
    工业品网络营销: `请围绕“${base}”，生成一项工业品短视频训练任务，要求明确目标客户、应用场景、公开资料、平台时长、咨询入口和事实核验边界。`,
    金融分析助理: `请围绕“${base}”，生成一项财务分析训练任务，要求明确公司资料、分析周期、核心指标、风险维度和合规边界。`,
    后端开发工程师: `请围绕“${base}”，生成一项代码审查训练任务，要求明确代码片段、业务背景、审查维度、安全要求和期望输出格式。`,
    行政专员: `请围绕“${base}”，生成一项行政办公训练任务，要求明确宣传/通知/纪要对象、资料来源、输出形式和待确认信息。`,
    产品经理: `请围绕“${base}”，生成一项产品需求训练任务，要求明确业务目标、用户反馈、约束条件、优先级标准和验证指标。`,
    智能制造: `请围绕“${base}”，生成一项智能制造训练任务，要求明确行业、设备或系统现状、典型场景、数据资料、风险边界和分阶测试要求。`,
    工业互联网: `请围绕“${base}”，生成一项工业互联网运维训练任务，要求明确告警日志、设备状态、影响范围、历史处置记录和人工复核边界。`,
  };
  return {
    original_task: templates[role.label] || `基于${base}，生成一项贴合${role.label}岗位的原始训练任务，要求包含任务对象、资料来源、输出格式和风险约束。`,
    rationale: "已使用前端规则根据岗位和工作背景生成原始训练题。",
    missing_info: ["真实资料", "输出格式细节", "风险边界"],
    source: "前端规则",
  };
}

function buildTieredTests(role, position) {
  if (role.label === "工业品网络营销") {
    return [
      "基础题：工业品短视频任务必须说明哪五类信息？为什么点赞量不能单独代表 B2B 转化？",
      "进阶题：将食品行业 CIP 阀门资料分为公开可确认、企业公开称和待核验三类，并说明每类资料的审核方法。",
      "挑战题：在没有具体型号和证书原件时，为食品生产企业采购人员写一条 20 秒短视频脚本，加入公开来源、待核验提示和咨询入口。",
    ];
  }
  return [
    `基础题：请以“${position}”身份，把一个模糊的${role.taskType}任务补全为包含目标、资料、维度、格式和约束的提示词。`,
    `进阶题：请围绕“${role.taskType}”设计 5 个事实核验问题，并说明每个问题需要哪些资料支撑。`,
    `挑战题：请基于一组真实或模拟资料，输出一份${position}可使用的${role.taskType}成果，并标注事实、观点和待验证假设。`,
  ];
}

function scorePromptOffline(roleId, originalTask, rewrittenPrompt) {
  const checks = [
    ["任务目标", ["生成", "分析", "整理", "审查", "输出", "梳理", "对比"]],
    ["背景资料", ["基于", "资料", "数据", "代码", "会议", "反馈", "财报", "截图", "记录"]],
    ["分析维度", ["维度", "从", "包括", "风险", "性能", "安全", "收入", "用户路径", "优先级"]],
    ["输出格式", ["输出", "表格", "报告", "清单", "结构", "JSON", "纪要", "摘要", "PRD"]],
    ["约束条件", ["不得", "不要", "标注", "待验证", "来源", "合规", "假设", "不能"]],
  ];
  let total = 0;
  const details = checks.map(([label, keywords]) => {
    const matched = keywords.filter((word) => rewrittenPrompt.includes(word));
    const score = matched.length >= 2 ? 20 : matched.length ? 14 : rewrittenPrompt.length > 35 ? 8 : 4;
    total += score;
    return {
      label,
      score,
      max_score: 20,
      evidence: matched.length >= 2 ? `覆盖多个要素：${matched.slice(0, 4).join("、")}` : matched.length ? `仅覆盖一个要素：${matched[0]}` : "该项表达不够明确",
    };
  });
  return applyOfflineQualityGate({
    role: roleConfigs[roleId].label,
    mode_label: "提示词评分",
    score: total,
    level: total >= 85 ? "优秀" : total >= 70 ? "合格" : total >= 50 ? "待提升" : "基础薄弱",
    improved: Math.max(0, total - (originalTask.length < 20 ? 30 : 50)),
    details,
    suggestions: details.filter((item) => item.score < 20).map((item) => `补充${item.label}相关信息。`),
    exemplar_prompt: roleConfigs[roleId].strongTask + "\n\n约束：不得编造数据；无法确认的信息标注为待验证。",
    training_feedback: total >= 80 ? "提示词已经比较完整，可以进入进阶任务。" : "建议按“目标-资料-维度-格式-约束”五段式继续补全。",
  }, roleId, originalTask, rewrittenPrompt, "");
}

function scoreTrainingOffline(mode, roleId, originalTask, answer) {
  if (mode === "prompt") {
    return scorePromptOffline(roleId, originalTask, answer);
  }

  const checksByMode = {
    workflow: [
      ["目标确认", ["目标", "背景", "对象", "范围"]],
      ["步骤完整", ["步骤", "第一", "第二", "1.", "2.", "3.", "流程"]],
      ["输入资料", ["资料", "数据", "记录", "反馈", "代码", "财报"]],
      ["输出成果", ["输出", "报告", "清单", "纪要", "摘要", "文档"]],
      ["复核机制", ["审核", "核验", "检查", "验证", "待验证", "风险"]],
    ],
    review: [
      ["事实来源", ["来源", "依据", "资料", "证据", "引用"]],
      ["幻觉识别", ["编造", "不确定", "无法确认", "待验证", "假设"]],
      ["风险判断", ["风险", "合规", "安全", "误导", "绝对"]],
      ["人工复核", ["人工", "复核", "确认", "审批", "二次检查"]],
      ["修改建议", ["建议", "修改", "补充", "删除", "调整"]],
    ],
    practice: [
      ["岗位目标", ["目标", "任务", "面向", "管理层", "用户", "业务"]],
      ["结构完整", ["摘要", "分析", "结论", "建议", "风险"]],
      ["资料依据", ["基于", "资料", "数据", "来源", "证据"]],
      ["行动建议", ["下一步", "行动", "建议", "负责人", "优先级"]],
      ["边界约束", ["不得", "待验证", "风险", "假设", "人工复核"]],
    ],
    test: [
      ["基础要素", ["目标", "资料", "维度", "格式", "约束"]],
      ["岗位贴合", ["岗位", "职位", "业务", "场景", "任务"]],
      ["分阶结构", ["基础", "进阶", "挑战", "步骤", "流程"]],
      ["证据意识", ["来源", "证据", "依据", "数据", "待验证"]],
      ["风险边界", ["风险", "合规", "人工复核", "不得", "安全"]],
    ],
  };
  const modeConfig = trainingModes[mode];
  const checks = checksByMode[mode] || checksByMode.workflow;
  let total = 0;
  const details = checks.map(([label, keywords]) => {
    const matched = keywords.filter((word) => answer.includes(word));
    const score = matched.length >= 2 ? 20 : matched.length ? 14 : answer.length > 50 ? 8 : 4;
    total += score;
    return {
      label,
      score,
      max_score: 20,
      evidence: matched.length ? `命中关键词：${matched.slice(0, 4).join("、")}` : "该项表达不够明确",
    };
  });

  return applyOfflineQualityGate({
    role: roleConfigs[roleId].label,
    mode_label: modeConfig.scoreTitle,
    score: total,
    level: total >= 85 ? "优秀" : total >= 70 ? "合格" : total >= 50 ? "待提升" : "基础薄弱",
    improved: 0,
    details,
    suggestions: details.filter((item) => item.score < 20).map((item) => `补充${item.label}相关内容。`),
    exemplar_prompt: modeConfig.starter(roleConfigs[roleId]),
    training_feedback: total >= 80 ? "本轮训练表现较完整，可以进入更复杂岗位任务。" : "建议根据评分维度补全关键要素后再训练一次。",
  }, roleId, originalTask, answer, mode === "review" ? reviewCandidateValue() : "");
}

function applyOfflineQualityGate(result, roleId, originalTask, answer, candidateOutput = "") {
  const compact = String(answer || "").replace(/\s+/g, "");
  let cap = 100;
  let message = "";
  if (compact.length < 12) {
    cap = 20;
    message = "回答过短，无法证明已经掌握本关能力。";
  } else if (compact.length < 25) {
    cap = 40;
    message = "回答内容不足，缺少完整判断或步骤。";
  } else if (compact.length < 45) {
    cap = 60;
    message = "回答仍偏短，需要补充依据、处理过程和风险边界。";
  }

  const strongHits = result.details.filter((item) => item.score >= 14).length;
  const structureCount = (String(answer || "").match(/[。！？；;\n]|第[一二三四五六七八九十]步|\d+[.、]/g) || []).length;
  if (strongHits >= 4 && structureCount < 2 && compact.length < 120) {
    cap = Math.min(cap, 60);
    message = "检测到关键词集中堆叠，但缺少可执行结构。";
  }

  const anchorsByRole = {
    marketing_manager: ["市场", "竞品", "产品", "用户", "营销", "推广"],
    industrial_marketing: ["阀门", "管件", "短视频", "采购", "食品", "制药", "CIP", "询盘"],
    finance_analyst: ["财报", "收入", "利润", "现金流", "负债", "公司"],
    backend_developer: ["代码", "接口", "安全", "性能", "异常", "测试"],
    admin_specialist: ["会议", "纪要", "通知", "宣传", "待办", "行政"],
    product_manager: ["需求", "用户", "产品", "优先级", "PRD", "指标"],
    smart_manufacturing: ["设备", "告警", "传感器", "工艺", "产线", "质检"],
    industrial_internet: ["平台", "告警", "设备", "日志", "运维", "处置"],
  };
  const anchors = (anchorsByRole[roleId] || []).filter((word) => String(originalTask || "").includes(word));
  if (anchors.length && !anchors.some((word) => String(answer || "").includes(word)) && !candidateOutput) {
    cap = Math.min(cap, 60);
    message = "回答没有回应原任务中的岗位对象或业务场景。";
  }
  if (candidateOutput) {
    const targetSignals = [];
    if (/保证|绝对|全网第一|所有|任何/.test(candidateOutput)) targetSignals.push("保证", "绝对", "夸大", "承诺", "所有", "任何");
    if (/证件|认证|型号|参数/.test(candidateOutput)) targetSignals.push("证件", "认证", "型号", "参数", "来源");
    if (/半夜三点|立马上门|当天解决/.test(candidateOutput)) targetSignals.push("半夜三点", "立马上门", "当天", "服务", "时效", "承诺");
    if (targetSignals.length && !targetSignals.some((word) => String(answer || "").includes(word))) {
      cap = Math.min(cap, 60);
      message = "审核意见没有指出待审核内容中的具体风险。";
    }
  }

  if (result.score > cap) {
    const originalTotal = Math.max(1, result.score);
    const scores = result.details.map((item) => Math.floor((item.score * cap) / originalTotal));
    let remaining = cap - scores.reduce((sum, value) => sum + value, 0);
    scores.forEach((value, index) => {
      if (remaining <= 0) return;
      const addition = Math.min(result.details[index].max_score - value, remaining);
      scores[index] += addition;
      remaining -= addition;
    });
    result.details = result.details.map((item, index) => ({ ...item, score: scores[index], evidence: `${item.evidence}；受整体质量门槛限制` }));
    result.score = cap;
    result.level = cap >= 85 ? "优秀" : cap >= 70 ? "合格" : cap >= 50 ? "待提升" : "基础薄弱";
    result.suggestions = [message, ...(result.suggestions || [])];
    result.training_feedback = `${message} 请完成具体改写后再评分。`;
  }
  result.quality_gate = { applied: result.score >= cap && cap < 100, score_cap: cap, message };
  return result;
}

function buildGrowthPlan(score) {
  const weakItems = score.details.filter((item) => item.score < item.max_score);
  const topWeakItems = weakItems.slice(0, 3);
  const modeLabel = trainingModes[currentTrainingMode].label;
  const missingLabels = topWeakItems.map((item) => item.label);
  const focus = missingLabels.join("、") || "跨任务迁移与真实资料质量";
  const role = currentRole();

  const modeActions = {
    prompt: {
      why: "你不是在学会背模板，而是在学会把岗位需求说清楚，让大模型知道目标、资料、边界和交付物。",
      next: `围绕“${focus}”重写一版提示词，至少补充 1 个资料来源、1 个输出格式和 1 条反幻觉约束。`,
      breakthrough: "把同一个任务换成另一个真实业务场景，再独立写一版提示词，检查结构是否还能保持完整。",
    },
    workflow: {
      why: "任务拆解训练的是项目推进能力，让你知道复杂工作该先做什么、每一步要什么资料、最后产出什么。",
      next: `把缺失的“${focus}”补进流程，每一步都写清输入资料、处理动作和输出结果。`,
      breakthrough: "给每一步加一个失败风险和复核动作，让流程从“能做”升级为“可控”。",
    },
    review: {
      why: "结果审核训练的是不盲信 AI 的能力，让你能识别编造、夸大、缺来源和不合规内容。",
      next: `重点补齐“${focus}”，把每条风险都写成“问题-依据-修改建议”的格式。`,
      breakthrough: "尝试故意加入一条可疑结论，再训练自己指出它为什么需要核验。",
    },
    practice: {
      why: "岗位实战训练的是把 AI 用到真实工作的完整能力，既要有成果，也要有依据、行动和风险边界。",
      next: `围绕“${focus}”补强岗位成果，让它能被同事或上级直接阅读和复核。`,
      breakthrough: "把成果改成正式交付格式，例如报告、清单、邮件、PRD、纪要或排查方案。",
    },
    test: {
      why: "分阶测试不是考记忆，而是检查你是否能从基础要素走到进阶拆解，再走到真实岗位应用。",
      next: `回到得分低的题型，补充“${focus}”，再按基础题、进阶题、挑战题顺序答一遍。`,
      breakthrough: "挑战题必须加入证据链、待核验信息和人工复核边界，证明你不是只会泛泛回答。",
    },
  };

  const action = modeActions[currentTrainingMode] || modeActions.prompt;
  if (!weakItems.length) {
    action.next = "当前五个维度已经完整，不再重复补模板；请换一个同岗位新情境，从空白开始独立完成。";
    action.breakthrough = "在新任务中减少模板依赖，并加入真实资料、证据来源和人工复核边界。";
  }
  const growthText =
    score.score >= 85
      ? "本轮已经达到较好水平，下一步应进入更真实、更复杂的岗位任务。"
      : score.score >= 70
        ? "本轮已经具备基本结构，下一步要把证据、约束和岗位交付补扎实。"
        : "本轮还停留在基础表达，下一步先把缺失要素补齐，再重新训练一次。";

  return {
    modeLabel,
    focus,
    why: action.why,
    next: action.next,
    breakthrough: action.breakthrough,
    growthText,
    rewriteStarter: `【二次修改目标】\n${action.next}\n\n【请基于原始任务重新作答】\n岗位：${role.label}\n训练模式：${modeLabel}\n原始任务：${taskInput.value.trim() || role.weakTask}\n\n【我的第二版答案】\n`,
  };
}

function updateProfile() {
  const role = currentRole();
  const profile = currentProfile();
  profileRole.textContent = role.label;
  profileExperience.textContent = `${profile.experience} 年`;
  profileAiLevel.textContent = profile.aiLevel;
  profileTaskType.textContent = role.taskType;
  profileEducation.textContent = profile.education;
  profileTheoryScore.textContent = `${profile.theoryScore} 分`;
  document.querySelector(".input-panel h3").textContent = `${profile.position}${role.taskType}`;
  trainingRoleText.textContent = role.label;
  trainingPositionText.textContent = profile.position;
  if (railRoleText) railRoleText.textContent = role.label;
  if (railPositionText) railPositionText.textContent = profile.position;
  renderProfilePreview();
}

function syncRoleChips() {
  roleChips.forEach((button) => {
    button.classList.toggle("active", button.dataset.role === roleSelect.value);
  });
}

function syncRoleCards() {
  syncRoleChips();
  roleStartCards.forEach((button) => {
    button.classList.toggle("active", roleChosen && button.dataset.role === roleSelect.value);
  });
}

function syncModeCards() {
  modeStartCards.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === currentTrainingMode);
  });
  railModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === currentTrainingMode);
  });
}

function renderSkills(mastery) {
  skillList.innerHTML = Object.entries(mastery)
    .map(
      ([name, value]) => {
        const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
        return `
        <div class="skill-row">
          <div><span>${escapeHtml(name)}</span><strong>${safeValue}</strong></div>
          <div class="meter" aria-label="${escapeHtml(name)} ${safeValue}分"><span style="width:${safeValue}%"></span></div>
        </div>
      `;
      },
    )
    .join("");
}

function masteryWithTrainingHistory(baseMastery = {}) {
  const mastery = { ...baseMastery };
  const modeToSkill = {
    提示词改写: "提示词结构",
    任务拆解: "工作流拆解",
    结果审核: "事实核验",
    岗位实战: "任务表达",
    分阶测试题: "合规使用",
  };
  const records = loadHistory();
  Object.entries(modeToSkill).forEach(([modeLabel, skillName]) => {
    const scores = records.filter((record) => record.mode === modeLabel).map((record) => Number(record.score) || 0);
    if (scores.length) mastery[skillName] = Math.max(...scores);
  });
  return mastery;
}

function setTrainingMode(mode, preserveAnswer = false) {
  const nextMode = trainingModes[mode] ? mode : "prompt";
  if (nextMode !== currentTrainingMode) trainingAttempt = 1;
  currentTrainingMode = nextMode;
  resetHints();
  const config = trainingModes[currentTrainingMode];
  if (currentTrainingMode === "test" && !preserveAnswer) {
    currentTestStep = 0;
    testAnswers = ["", "", ""];
  }
  trainingModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === currentTrainingMode);
  });
  trainingModeKicker.textContent = config.kicker;
  trainingModeTitle.textContent = config.title;
  trainingModeHint.textContent = config.hint;
  trainingInputKicker.textContent = config.inputKicker;
  taskInputLabel.textContent = config.taskLabel;
  taskInputTip.textContent = config.taskTip;
  trainingModeText.textContent = config.label;
  trainingGoalText.textContent = config.title;
  scorePrompt.textContent = config.button;
  const reviewSample = currentTrainingMode === "review" ? activeReviewSample || defaultReviewSample(currentRole()) : "";
  reviewSource.classList.toggle("hidden-block", !reviewSample);
  reviewSourceText.value = reviewSample || "";
  if (!preserveAnswer) {
    rewriteInput.value = "";
    rewriteInput.placeholder = "先按自己的理解作答；卡住时再查看分级提示。";
  }
  if (currentTrainingMode === "test") {
    syncTestAnswerBox();
  }
  scorePanel.innerHTML = `
    <div class="empty-score">
      <strong>等待${escapeHtml(config.scoreTitle)}</strong>
      <p>${escapeHtml(config.hint)}</p>
    </div>
  `;
  renderActiveTestQuestions();
  syncModeCards();
  renderMasteryGoal();
}

function currentTestQuestions() {
  const generatedQuestions = latestResult?.generation?.resources?.practice_tasks;
  if (Array.isArray(generatedQuestions) && generatedQuestions.length) {
    return generatedQuestions;
  }
  const profile = currentProfile();
  return buildTieredTests(currentRole(), profile.position || currentRole().label);
}

function renderActiveTestQuestions() {
  if (currentTrainingMode !== "test") {
    activeTestQuestions.classList.add("hidden-block");
    activeTestQuestions.innerHTML = "";
    scorePrompt.disabled = false;
    scorePrompt.textContent = trainingModes[currentTrainingMode].button;
    return;
  }
  const labels = ["基础题", "进阶题", "挑战题"];
  const questions = currentTestQuestions().slice(0, 3);
  const currentQuestion = questions[currentTestStep] || questions[0] || "请完成本轮分阶测试。";
  const currentComplete = isTestAnswerComplete(testAnswers[currentTestStep]);
  const allComplete = testAnswers.every(isTestAnswerComplete);
  activeTestQuestions.classList.remove("hidden-block");
  activeTestQuestions.innerHTML = `
    <div class="question-source">系统已根据当前岗位画像、原始任务和知识库生成分阶测试。请按顺序完成：基础题 → 进阶题 → 挑战题。</div>
    <div class="test-sequence">
      ${labels
        .map(
          (label, index) => `
            <span class="${index === currentTestStep ? "active" : ""} ${isTestAnswerComplete(testAnswers[index]) ? "done" : ""}">
              ${index + 1}. ${label}
            </span>
          `,
        )
        .join("")}
    </div>
    <article class="active-test-card sequence-card">
      <span>第 ${currentTestStep + 1} 关 / 3：${labels[currentTestStep]}</span>
      <p>${escapeHtml(currentQuestion.replace(/^基础题：|^进阶题：|^挑战题：/, ""))}</p>
    </article>
    <div class="test-step-actions">
      <button class="ghost-button" data-test-nav="prev" ${currentTestStep === 0 ? "disabled" : ""}>上一题</button>
      <button class="primary-button" data-test-nav="next" ${currentTestStep === 2 || !currentComplete ? "disabled" : ""}>保存并进入下一题</button>
    </div>
  `;
  scorePrompt.disabled = currentTestStep < 2 || !allComplete;
  scorePrompt.textContent = allComplete ? trainingModes.test.button : "请依次完成三题";
}

function syncTestAnswerBox() {
  const labels = ["基础题", "进阶题", "挑战题"];
  rewriteInput.value = testAnswers[currentTestStep] || `${labels[currentTestStep]}答案：\n`;
}

function saveCurrentTestAnswer() {
  if (currentTrainingMode === "test") {
    testAnswers[currentTestStep] = rewriteInput.value.trim();
  }
}

function extractLearnerAnswer(value) {
  const text = String(value || "");
  const marker = "【我的第二版答案】";
  const markerIndex = text.lastIndexOf(marker);
  return (markerIndex >= 0 ? text.slice(markerIndex + marker.length) : text).trim();
}

function isTestAnswerComplete(answer) {
  const content = String(answer || "")
    .replace(/^(基础题|进阶题|挑战题)答案：?/, "")
    .replace(/\s+/g, "")
    .trim();
  return content.length >= 20;
}

function agentSource(agent, result) {
  if (agent.source === "DeepSeek") {
    return { label: "DeepSeek", className: "source-llm" };
  }
  if (agent.fallback_used) {
    return { label: "规则兜底", className: "source-fallback" };
  }
  if (agent.source?.includes("规则")) {
    return { label: "规则运行", className: "source-rule" };
  }
  if (result.mode === "offline_frontend_fallback" || agent.source === "前端演示") {
    return { label: "前端演示", className: "source-demo" };
  }
  return { label: "已完成", className: "source-rule" };
}

function renderAgents(result) {
  const reviewScore = result.review?.score || 82;
  const clarity = result.diagnosis?.task_clarity || "中";
  const missingCount = result.diagnosis?.missing_info?.length || 0;
  const completion = Math.max(45, Math.min(96, Math.round((reviewScore + (clarity === "低" ? 58 : 88)) / 2)));

  if (trainingStage === "input") {
    progressOverview.innerHTML = `
      <div class="completion-ring" style="--value:0%">
        <strong>0%</strong>
        <span>等待开始</span>
      </div>
      <div class="progress-summary">
        <span>系统状态</span>
        <strong>等待运行多智能体训练</strong>
        <p>填写原始任务后点击“开始训练”，系统才会生成本轮诊断、资源、审核和反馈结果。</p>
      </div>
    `;
    agentList.innerHTML = '<p class="source-line">尚未运行本轮智能体。</p>';
    return;
  }
  const sourceLabels = (result.agents || []).map((agent) => agentSource(agent, result).label);
  const llmCount = sourceLabels.filter((label) => label === "DeepSeek").length;
  const fallbackCount = sourceLabels.filter((label) => label === "规则兜底").length;
  const sourceSummary =
    result.mode === "offline_frontend_fallback"
      ? "前端演示版"
      : llmCount
        ? `${llmCount} 个后端智能模块已调用 DeepSeek`
        : fallbackCount
          ? "部分模块已启用规则兜底"
          : "后端规则模式运行";

  progressOverview.innerHTML = `
    <div class="completion-ring" style="--value:${completion}%">
      <strong>${completion}%</strong>
      <span>资源就绪</span>
    </div>
    <div class="progress-summary">
      <span>系统状态</span>
      <strong>${escapeHtml(sourceSummary)}</strong>
      <p>${escapeHtml(result.feedback?.summary || "系统已完成本轮训练评估，并生成下一步提升建议。")}</p>
    </div>
  `;

  const cards = [
    {
      title: "任务清晰度",
      value: clarity,
      detail: missingCount ? `仍缺少 ${missingCount} 类关键信息` : "任务目标和约束较完整",
    },
    {
      title: "资源审核分",
      value: `${reviewScore}`,
      detail: result.review?.summary || "已完成质量、风险和结构检查",
    },
    {
      title: "风险控制",
      value: `${result.review?.risks?.length || 0} 项`,
      detail: (result.review?.risks || ["未发现明显幻觉或合规风险。"])[0],
    },
    {
      title: "下一步",
      value: result.feedback?.training_level || "专项提升",
      detail: result.feedback?.next_task || "继续完成下一轮岗位训练。",
    },
  ];

  agentList.innerHTML = cards
    .map(
      (card) => `
        <article class="progress-item">
          <span>${escapeHtml(card.title)}</span>
          <strong>${escapeHtml(card.value)}</strong>
          <p>${escapeHtml(card.detail)}</p>
        </article>
      `,
    )
    .join("");
}

function renderLearningReport(result) {
  const feedback = result.feedback || {};
  const diagnosis = result.diagnosis || {};
  const mastery = feedback.mastery || {};
  const blindSpots =
    feedback.blind_spots ||
    Object.entries(mastery)
      .filter(([, value]) => Number(value) < 75)
      .map(([name]) => `${name}能力需要加强`)
      .concat(diagnosis.missing_info || [])
      .slice(0, 4);
  const curve =
    feedback.resource_match_curve || [
      { stage: "基础讲义", difficulty: 48, match: 84 },
      { stage: "实操指南", difficulty: 64, match: 78 },
      { stage: "分阶测试", difficulty: 76, match: 70 },
    ];
  const path =
    feedback.learning_path || [
      "学情画像诊断",
      "定制资源生成",
      "训练评分与审核",
      "下一轮动态任务",
    ];

  blindSpotList.innerHTML = blindSpots.length
    ? blindSpots.map((item) => `<span>${escapeHtml(item)}</span>`).join("")
    : "<span>暂未发现明显知识盲区</span>";

  difficultyCurve.innerHTML = curve
    .map(
      (item) => `
        <div class="curve-row">
          <div>
            <b>${escapeHtml(item.stage)}</b>
            <small>难度 ${Math.max(0, Math.min(100, Number(item.difficulty) || 0))} / 匹配 ${Math.max(0, Math.min(100, Number(item.match) || 0))}</small>
          </div>
          <div class="curve-bars">
            <i style="width:${Math.max(0, Math.min(100, Number(item.difficulty) || 0))}%"></i>
            <em style="width:${Math.max(0, Math.min(100, Number(item.match) || 0))}%"></em>
          </div>
        </div>
      `,
    )
    .join("");

  learningPath.innerHTML = path
    .map(
      (item, index) => `
        <div class="path-node">
          <strong>${index + 1}</strong>
          <span>${escapeHtml(item)}</span>
        </div>
      `,
    )
    .join("");
}

function refreshDiagnosis(result = latestResult) {
  const diagnosis = result.diagnosis;
  const isVague = diagnosis.task_clarity === "低";
  diagnosisBox.classList.toggle("warning", isVague);
  diagnosisBox.classList.toggle("ready", !isVague);
  diagnosisLevel.textContent = diagnosis.task_clarity;
  diagnosisText.textContent = diagnosis.missing_info?.length
    ? `${diagnosis.summary} 建议补充：${diagnosis.missing_info.join("、")}。`
    : diagnosis.summary;
  diagnosisAction.textContent = diagnosis.next_action;
}

function tabViews(result) {
  const resources = result.generation.resources;
  const sources = escapeHtml(result.knowledge.sources.join("、"));
  const review = result.review;
  const redTeamTests = review.red_team_tests || ["诱导模型编造缺失数据，检查是否拒绝。"];
  const crossChecks = review.cross_checks || ["将关键结论与资料来源逐条对应。"];
  return {
    prompt: `<pre>${escapeHtml(resources.prompt_template)}</pre>`,
    workflow: `
      <ol class="workflow-list">
        ${resources.workflow.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ol>
      <p class="source-line">知识库来源：${sources}</p>
    `,
    review: `
      <div class="review-grid">
        <div><span>审核评分</span><strong>${Math.max(0, Math.min(100, Number(review.score) || 0))}/100</strong><p>${escapeHtml(review.passed.join(" "))}</p></div>
        <div><span>风险项</span><strong>${review.risks.length} 项</strong><p>${escapeHtml(review.risks.join(" "))}</p></div>
        <div><span>修改建议</span><strong>证据链</strong><p>${escapeHtml(review.suggestions.join(" "))}</p></div>
        <div><span>红队测试</span><strong>${redTeamTests.length} 项</strong><p>${escapeHtml(redTeamTests.join(" "))}</p></div>
        <div><span>交叉验证</span><strong>${crossChecks.length} 项</strong><p>${escapeHtml(crossChecks.join(" "))}</p></div>
      </div>
    `,
    next: `
      <div class="challenge-panel">
        <h3>下一轮任务：${escapeHtml(result.feedback.training_level)}</h3>
        <p>${escapeHtml(result.feedback.next_task)}</p>
        ${result.feedback.coach_feedback ? `<p>${escapeHtml(result.feedback.coach_feedback)}</p>` : ""}
        ${
          result.feedback.micro_goals
            ? `<div class="challenge-list">${result.feedback.micro_goals.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>`
            : ""
        }
        <div class="challenge-list">
          ${resources.practice_tasks.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
        </div>
      </div>
    `,
    tests: `
      <div class="test-list">
        ${(resources.practice_tasks || [])
          .map(
            (item, index) => `
              <article class="test-card">
                <span>${["基础题", "进阶题", "挑战题"][index] || `第 ${index + 1} 题`}</span>
                <p>${escapeHtml(item.replace(/^基础题：|^进阶题：|^挑战题：/, ""))}</p>
              </article>
            `,
          )
          .join("")}
      </div>
    `,
  };
}

function switchTab(tab) {
  tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });
  resultContent.innerHTML = tabViews(latestResult)[tab];
}

function renderScore(score, submittedAnswer = rewriteInput.value.trim()) {
  latestScore = score;
  setTrainingStage("scored");
  const growthPlan = buildGrowthPlan(score);
  const decision = buildAdaptiveDecision(score);
  const record = saveTrainingRecord(score, submittedAnswer);
  const records = loadHistory();
  renderSkills(masteryWithTrainingHistory(latestResult?.feedback?.mastery || {}));
  const evidence = modeEvidence(records, trainingModes[currentTrainingMode].label);
  const stableMastery = Boolean(score.adaptive_decision?.stable_mastery || evidence.stableMastery);
  const learnerProfile = score.learning_profile || null;
  const memoryCard = learnerProfile
    ? `
      <div class="backend-memory">
        <div>
          <span>后台长期学习画像</span>
          <strong>${learnerProfile.attempts > 1 ? `已读取 ${learnerProfile.attempts} 次训练记录` : "已建立第一条成长记录"}</strong>
        </div>
        <p>长期薄弱点：${escapeHtml((learnerProfile.weak_dimensions || []).join("、") || "等待更多训练数据")}</p>
        <b>后台推荐：${escapeHtml(learnerProfile.next_mode_label || "继续当前训练")} · ${escapeHtml(learnerProfile.next_focus || "任务目标与证据链")}</b>
      </div>
    `
    : "";
  trainingAttempt = record.attempt;
  renderMasteryGoal();
  const baselineScore = record.previousScore;
  const comparisonLabel = record.attempt > 1 ? "上一轮答案" : currentTrainingMode === "prompt" ? "训练前 · 原始表达" : "首次作答基线";
  const nextMode = nextTrainingMode();
  const nextActionButton = decision.mastery_passed
    ? stableMastery
      ? `<button class="primary-button" data-growth-action="next-mode">${nextMode ? `进入下一关：${escapeHtml(trainingModes[nextMode].label)}` : "完成路线，查看成长报告"}</button>`
      : '<button class="primary-button" data-growth-action="transfer">换一道题验证迁移</button>'
    : "";
  scorePanel.innerHTML = `
    <div class="score-header">
      <div>
        <span>${escapeHtml(score.mode_label || trainingModes[currentTrainingMode].scoreTitle)}</span>
        <strong>${score.score}</strong>
      </div>
      <div class="score-level">${escapeHtml(score.level)}</div>
    </div>
    <p class="score-feedback">${escapeHtml(score.training_feedback)}</p>
    <div class="mastery-decision ${decision.mastery_passed ? "passed" : "practice"}">
      <div>
        <span>反馈迭代 Agent 决策</span>
        <strong>${stableMastery ? "稳定掌握" : decision.mastery_passed ? "本题达标，等待迁移验证" : decision.strategy}</strong>
      </div>
      <p>${escapeHtml(decision.next_action)}</p>
      <b>${stableMastery ? "已在两个不同任务中达标" : decision.mastery_passed ? "本题已达 80 分，换题再通过才算稳定掌握" : `当前 ${score.score} 分，达到 80 分后进入迁移验证`}</b>
    </div>
    ${memoryCard}
    <div class="training-comparison">
      <div>
        <span>${comparisonLabel}</span>
        <strong>${baselineScore}</strong>
        <p>${shortExcerpt(record.previousAnswer)}</p>
      </div>
      <b class="comparison-arrow">→</b>
      <div>
        <span>第 ${record.attempt} 轮 · 当前答案</span>
        <strong>${score.score}</strong>
        <p>${shortExcerpt(record.rewritten)}</p>
      </div>
      <em>${record.attempt > 1 ? "较上一轮" : currentTrainingMode === "prompt" ? "较训练前" : "首次记录"} ${formatDelta(record.improved)} 分</em>
    </div>
    <div class="score-bars">
      ${score.details
        .map(
          (item) => `
            <div class="score-row">
              <div><span>${escapeHtml(item.label)}</span><b>${item.score}/${item.max_score}</b></div>
              <div class="meter"><span style="width:${(item.score / item.max_score) * 100}%"></span></div>
              <small>${escapeHtml(item.evidence)}</small>
            </div>
          `,
        )
        .join("")}
    </div>
    <div class="suggestion-box">
      <strong>修改建议</strong>
      <ul>${score.suggestions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
    <div class="growth-coach">
      <strong>训练教练：下一步怎么提升</strong>
      <p>${escapeHtml(growthPlan.growthText)}</p>
      <div class="growth-grid">
        <div><span>为什么练这个</span><p>${escapeHtml(growthPlan.why)}</p></div>
        <div><span>马上怎么改</span><p>${escapeHtml(growthPlan.next)}</p></div>
        <div><span>突破任务</span><p>${escapeHtml(growthPlan.breakthrough)}</p></div>
      </div>
      <div class="growth-actions">
        <button class="${decision.mastery_passed ? "ghost-button" : "primary-button"}" data-growth-action="retry">${decision.mastery_passed ? "继续挑战更高分" : "按弱项再练一次"}</button>
        ${nextActionButton}
      </div>
    </div>
    <details class="example-box">
      <summary>查看标准示例</summary>
      <pre>${escapeHtml(score.exemplar_prompt)}</pre>
    </details>
  `;
  renderHistory();
}

function buildAdaptiveDecision(score) {
  if (score.adaptive_decision) return score.adaptive_decision;
  const weakDimensions = score.details
    .filter((item) => item.score < item.max_score)
    .map((item) => item.label)
    .slice(0, 3);
  const focus = weakDimensions.join("、") || "真实资料和证据链";
  if (score.score < 60) {
    return {
      strategy: "降维解释",
      mastery_passed: false,
      pass_score: 80,
      weak_dimensions: weakDimensions,
      next_action: `先查看标准示例，只围绕“${focus}”完成一个小补全练习，再重新作答。`,
    };
  }
  if (score.score < 80) {
    return {
      strategy: "专项补练",
      mastery_passed: false,
      pass_score: 80,
      weak_dimensions: weakDimensions,
      next_action: `保留已经写好的内容，只针对“${focus}”补充后再次评分。`,
    };
  }
  return {
    strategy: "进阶挑战",
    mastery_passed: true,
    pass_score: 80,
    weak_dimensions: weakDimensions,
    next_action: "本关已达标，可以围绕同一个岗位任务进入下一项能力训练。",
  };
}

function nextTrainingMode() {
  const modeOrder = ["prompt", "workflow", "review", "practice", "test"];
  const currentIndex = modeOrder.indexOf(currentTrainingMode);
  return currentIndex >= modeOrder.length - 1 ? null : modeOrder[currentIndex + 1];
}

function applyGrowthRetry() {
  if (!latestScore) return;
  trainingAttempt += 1;
  startTrainingTimer();
  setTrainingStage("retry");
  rewriteInput.value = buildGrowthPlan(latestScore).rewriteStarter;
  scorePanel.innerHTML = `
    <div class="empty-score">
      <strong>已进入第二轮改写</strong>
      <p>请根据上方“二次修改目标”补全答案，再点击“${trainingModes[currentTrainingMode].button}”。系统会重新评分并记录成长。</p>
    </div>
  `;
  rewriteInput.focus();
}

function goNextTrainingMode() {
  if (latestScore && !buildAdaptiveDecision(latestScore).mastery_passed) {
    applyGrowthRetry();
    return;
  }
  const evidence = modeEvidence(loadHistory(), trainingModes[currentTrainingMode].label);
  if (!evidence.stableMastery) {
    startTransferChallenge();
    return;
  }
  const nextMode = nextTrainingMode();
  if (!nextMode) {
    switchView("report");
    renderGrowthEvidence();
    return;
  }
  selectMode(nextMode);
  latestScore = null;
  trainingAttempt = 1;
  startTrainingTimer();
  setTrainingStage("rewrite");
  scorePanel.innerHTML = `
    <div class="empty-score">
      <strong>已进入下一关：${trainingModes[nextMode].label}</strong>
      <p>继续完成本关对应的岗位任务。完成后点击“${trainingModes[nextMode].button}”，系统会再次评分并更新成长记录。</p>
    </div>
  `;
  rewriteInput.focus();
}

function startTransferChallenge() {
  const challenge = transferTaskFor();
  transferChallenge = challenge.task;
  activeReviewSample = challenge.reviewSample;
  trainingAttempt = 1;
  startTrainingTimer();
  setTrainingStage("input");
  taskInput.value = transferChallenge;
  if (currentTrainingMode === "review") {
    reviewSource.classList.toggle("hidden-block", !activeReviewSample);
    reviewSourceText.value = activeReviewSample || defaultReviewSample(currentRole());
  }
  rewriteInput.value = "";
  latestScore = null;
  resetHints();
  renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
  scorePanel.innerHTML = `
    <div class="empty-score">
      <strong>迁移验证题已生成</strong>
      <p>这是同岗位的新情境。请先独立完成，不照抄上一题；再次达到 80 分后，本项能力才标记为“稳定掌握”。</p>
    </div>
  `;
  document.querySelector(".input-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAll(result) {
  latestResult = result;
  updateProfile();
  renderSkills(masteryWithTrainingHistory(result.feedback.mastery));
  renderAgents(result);
  renderLearningReport(result);
  refreshDiagnosis(result);
  renderActiveTestQuestions();
  const active = document.querySelector(".tabs button.active")?.dataset.tab || "prompt";
  switchTab(active);
}

async function runPipeline() {
  const role = currentRole();
  const profile = currentProfile();
  if (!taskInput.value.trim()) {
    diagnosisLevel.textContent = "未填写";
    diagnosisText.textContent = "请先写下要训练的岗位任务，系统才能进行诊断和资源生成。";
    diagnosisAction.textContent = "补充任务";
    taskInput.focus();
    return;
  }
  if (currentTrainingMode === "review" && !reviewCandidateValue()) {
    scorePanel.innerHTML = '<div class="empty-score"><strong>缺少待审核内容</strong><p>请先粘贴一段实际 AI 输出，再运行审核训练。</p></div>';
    reviewSourceText.focus();
    return;
  }
  const payload = {
    learner_id: profileStorageId(),
    test_participant_code: testParticipantCode(),
    role_id: roleSelect.value,
    specific_position: profile.position,
    experience_years: profile.experience,
    ai_skill_level: profile.aiLevel,
    education_background: profile.education,
    theory_test_score: profile.theoryScore,
    allow_external_llm: Boolean(allowExternalLLM?.checked),
    training_mode: currentTrainingMode,
    task: taskInput.value.trim(),
    candidate_output: currentTrainingMode === "review" ? reviewCandidateValue() : "",
  };

  startTrainingTimer();

  runAgents.textContent = "运行中...";
  runAgents.disabled = true;
  progressOverview.innerHTML = `
    <div class="coach-loading-mark"><span></span></div>
    <div class="progress-summary">
      <span>AI 训练教练</span>
      <strong>正在诊断你的任务</strong>
      <p>职业诊断、知识检索、质量审核和路径决策正在协同运行。</p>
    </div>
  `;
  agentList.innerHTML = "";
  trainingAttempt = 1;
  try {
    const response = await fetch(`${API_BASE}/api/train`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("backend unavailable");
    setTrainingStage("rewrite");
    renderAll(await response.json());
  } catch (error) {
    setTrainingStage("rewrite");
    renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
  } finally {
    runAgents.textContent = "开始训练";
    runAgents.disabled = false;
  }
}

async function createTaskSeed() {
  const role = currentRole();
  const profile = currentProfile();
  const payload = {
    learner_id: profileStorageId(),
    test_participant_code: testParticipantCode(),
    role_id: roleSelect.value,
    specific_position: profile.position,
    experience_years: profile.experience,
    ai_skill_level: profile.aiLevel,
    education_background: profile.education,
    theory_test_score: profile.theoryScore,
    allow_external_llm: Boolean(allowExternalLLM?.checked),
    work_context: workContextInput.value.trim(),
  };

  generateTaskSeed.textContent = "生成中...";
  generateTaskSeed.disabled = true;
  taskSeedResult.textContent = "正在根据岗位画像和工作背景生成原始训练题。";
  try {
    const response = await fetch(`${API_BASE}/api/task-seed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("backend unavailable");
    const result = await response.json();
    taskInput.value = result.original_task;
    taskSeedResult.textContent = `已生成：${result.rationale || "可作为本轮训练的原始任务。"}`;
  } catch (error) {
    const result = generateTaskSeedOffline(role, profile, payload.work_context);
    taskInput.value = result.original_task;
    taskSeedResult.textContent = "后端未连接，已使用本地规则生成原始训练题。";
  } finally {
    renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
    generateTaskSeed.textContent = "根据实际情况生成原始题目";
    generateTaskSeed.disabled = false;
  }
}

async function scoreRewrite() {
  saveCurrentTestAnswer();
  if (currentTrainingMode === "test" && currentTestStep < 2) {
    return;
  }
  if (currentTrainingMode === "test" && !testAnswers.every(isTestAnswerComplete)) {
    scorePanel.innerHTML = '<div class="empty-score"><strong>还有题目未完成</strong><p>每一题请至少写出一个完整判断和理由，再提交测试。</p></div>';
    return;
  }
  const learnerAnswer = currentTrainingMode === "test" ? "" : extractLearnerAnswer(rewriteInput.value);
  if (currentTrainingMode !== "test" && !learnerAnswer) {
    scorePanel.innerHTML = `<div class="empty-score"><strong>还没有作答</strong><p>请先完成${escapeHtml(trainingModes[currentTrainingMode].label)}，再提交评分。</p></div>`;
    rewriteInput.focus();
    return;
  }
  const submittedAnswer =
    currentTrainingMode === "test"
      ? testAnswers
          .map((answer, index) => `${["基础题", "进阶题", "挑战题"][index]}答案：\n${answer || "未作答"}`)
          .join("\n\n")
      : learnerAnswer;
  const profile = currentProfile();
  const payload = {
    learner_id: profileStorageId(),
    test_participant_code: testParticipantCode(),
    role_id: roleSelect.value,
    specific_position: profile.position,
    experience_years: profile.experience,
    ai_skill_level: profile.aiLevel,
    education_background: profile.education,
    theory_test_score: profile.theoryScore,
    duration_seconds: elapsedTrainingSeconds(),
    attempt_number: trainingAttempt,
    training_mode: currentTrainingMode,
    original_task: taskInput.value.trim(),
    rewritten_prompt: submittedAnswer,
    candidate_output: currentTrainingMode === "review" ? reviewCandidateValue() : "",
  };

  scorePrompt.textContent = "评估中...";
  scorePrompt.disabled = true;
  try {
    const response = await fetch(`${API_BASE}/api/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("backend unavailable");
    renderScore(await response.json(), submittedAnswer);
  } catch (error) {
    renderScore(
      currentTrainingMode === "prompt"
        ? scorePromptOffline(roleSelect.value, payload.original_task, payload.rewritten_prompt)
        : scoreTrainingOffline(currentTrainingMode, roleSelect.value, payload.original_task, payload.rewritten_prompt),
      submittedAnswer,
    );
  } finally {
    scorePrompt.textContent = trainingModes[currentTrainingMode].button;
    scorePrompt.disabled = false;
  }
}

function resetForRole() {
  const role = currentRole();
  transferChallenge = null;
  activeReviewSample = null;
  theoryScoreSource = "系统示例值";
  applyRoleDefaultsToProfile();
  syncRoleCards();
  setTrainingStage("input");
  latestScore = null;
  trainingAttempt = 1;
  setTrainingMode(currentTrainingMode);
  taskInput.value = modeTaskFor(role, currentTrainingMode);
  if (!entryTestArea.classList.contains("hidden-block")) {
    renderEntryTest();
    entryTestResult.textContent = "";
  }
  renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
  renderHistory();
}

roleSelect.addEventListener("change", () => selectRole(roleSelect.value));
appNavButtons.forEach((button) =>
  button.addEventListener("click", () => {
    if (button.dataset.view === "history") renderHistory();
    if (button.dataset.view === "report") renderGrowthEvidence();
    switchView(button.dataset.view);
  }),
);
roleChips.forEach((button) =>
  button.addEventListener("click", () => {
    selectRole(button.dataset.role);
  }),
);
roleStartCards.forEach((button) => button.addEventListener("click", () => selectRole(button.dataset.role)));
trainingModeButtons.forEach((button) =>
  button.addEventListener("click", () => selectMode(button.dataset.mode)),
);
modeStartCards.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.mode)));
railModeButtons.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.mode)));
generateTaskSeed.addEventListener("click", createTaskSeed);
startEntryTest.addEventListener("click", () => {
  entryTestArea.classList.remove("hidden-block");
  renderEntryTest();
  entryTestResult.textContent = "";
});
closeEntryTest.addEventListener("click", () => entryTestArea.classList.add("hidden-block"));
submitEntryTest.addEventListener("click", submitEntryAssessment);
scorePanel.addEventListener("click", (event) => {
  const button = event.target.closest("[data-growth-action='retry']");
  if (button) applyGrowthRetry();
  const nextButton = event.target.closest("[data-growth-action='next-mode']");
  if (nextButton) goNextTrainingMode();
  const transferButton = event.target.closest("[data-growth-action='transfer']");
  if (transferButton) startTransferChallenge();
});
hintCoach.addEventListener("click", (event) => {
  const button = event.target.closest("[data-hint-level]");
  if (button) showHint(Number(button.dataset.hintLevel));
});
activeTestQuestions.addEventListener("click", (event) => {
  const button = event.target.closest("[data-test-nav]");
  if (!button) return;
  saveCurrentTestAnswer();
  if (button.dataset.testNav === "prev") {
    currentTestStep = Math.max(0, currentTestStep - 1);
  }
  if (button.dataset.testNav === "next") {
    if (!isTestAnswerComplete(testAnswers[currentTestStep])) return;
    currentTestStep = Math.min(2, currentTestStep + 1);
  }
  syncTestAnswerBox();
  renderActiveTestQuestions();
});
goModeSelect.addEventListener("click", () => switchView("mode"));
backRoleSelect.addEventListener("click", () => switchView("role"));
goTraining.addEventListener("click", () => {
  setTrainingStage("input");
  trainingAttempt = 1;
  startTrainingTimer();
  switchView("train");
  renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
});
backModeFromTraining.addEventListener("click", () => switchView("mode"));
backRoleFromTraining.addEventListener("click", () => switchView("role"));
taskInput.addEventListener("input", () => renderAll(buildFallbackResult(roleSelect.value, taskInput.value)));
reviewSourceText.addEventListener("input", () => {
  if (currentTrainingMode === "review") renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
});
rewriteInput.addEventListener("input", () => {
  saveCurrentTestAnswer();
  if (currentTrainingMode === "test") renderActiveTestQuestions();
});
[specificPositionInput, experienceInput, aiLevelInput, educationInput, theoryScoreInput].forEach((field) =>
  field.addEventListener("input", () => {
    if (field === theoryScoreInput) theoryScoreSource = "学习者手动填写";
    renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
  }),
);
testParticipantInput.value = localStorage.getItem("promptcraft_test_participant_code") || "";
testParticipantInput.addEventListener("input", () => {
  const code = testParticipantCode();
  if (code) localStorage.setItem("promptcraft_test_participant_code", code);
  else localStorage.removeItem("promptcraft_test_participant_code");
  updateCollectionStatus();
});
testParticipantInput.addEventListener("change", () => {
  const code = testParticipantCode();
  testParticipantInput.value = code;
  if (code) localStorage.setItem("promptcraft_test_participant_code", code);
  else localStorage.removeItem("promptcraft_test_participant_code");
  startTrainingTimer();
  renderHistory();
});
fillStrongTask.addEventListener("click", () => {
  taskInput.value = currentTrainingMode === "prompt" ? currentRole().strongTask : modeTaskFor(currentRole(), currentTrainingMode);
  rewriteInput.value =
    currentTrainingMode === "prompt" ? currentRole().strongTask : trainingModes[currentTrainingMode].starter(currentRole());
  renderAll(buildFallbackResult(roleSelect.value, taskInput.value));
});
runAgents.addEventListener("click", runPipeline);
scorePrompt.addEventListener("click", scoreRewrite);
clearHistory.addEventListener("click", () => {
  saveHistory([]);
  saveReviewQueue([]);
  renderHistory();
});
exportMyRecords.addEventListener("click", exportCurrentTesterData);
exportLocalRecords.addEventListener("click", exportLocalHistoryData);
exportTestSummary.addEventListener("click", exportFormalTestSummary);
tabButtons.forEach((button) => button.addEventListener("click", () => switchTab(button.dataset.tab)));

const goHome = document.querySelector("#goHome");
goHome?.addEventListener("click", () => {
  setTrainingStage("input");
  switchView("role");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

resetForRole();
switchView("role");
// 开场视频只负责展示，加载失败或用户跳过时不阻断实训。
(function initIntro() {
  const overlay = document.querySelector("#introOverlay");
  const video = document.querySelector("#introVideo");
  const start = document.querySelector("#introStart");
  const skip = document.querySelector("#introSkip");
  if (!overlay) return;

  let closed = false;
  function closeIntro() {
    if (closed) return;
    closed = true;
    video?.pause();
    overlay.classList.add("fade-out");
    setTimeout(() => overlay.remove(), 600);
  }

  function beginPlay() {
    if (!video) {
      closeIntro();
      return;
    }
    start?.classList.add("hidden-block");
    skip?.classList.remove("hidden-block");
    video.play().catch(closeIntro);
  }

  video?.addEventListener("ended", closeIntro);
  video?.addEventListener("error", closeIntro);
  start?.addEventListener("click", beginPlay);
  skip?.addEventListener("click", closeIntro);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeIntro();
  });
})();
