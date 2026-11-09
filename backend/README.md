# 智训工坊后端原型

这是“多岗位 + 本地知识库 + DeepSeek + 多 Agent 调度”的第一版后端原型。

当前不依赖 FastAPI，也不需要安装第三方包，使用 Python 标准库即可运行。这样做的目的是先把系统结构跑通，后续再替换为 FastAPI、数据库和更完整的真实大模型接口。

## 启动方式

在项目根目录执行：

```powershell
python backend/main.py
```

启动后访问：

```text
http://127.0.0.1:8000/health
```

## 大模型配置

后端会读取：

```text
backend/.env
```

DeepSeek 配置示例：

```text
API_BASE_URL=https://api.deepseek.com/v1
API_KEY=你的 DeepSeek API Key
MODEL_NAME=deepseek-chat
```

当前已接入真实大模型的模块：

- 职业诊断 Agent
- 领域知识生成 Agent
- 质量审核 Agent
- 反馈迭代 Agent

当前重点深度实例：

- 岗位：工业品网络营销
- 任务：卫生级阀门短视频营销与公开资料核验
- 知识库：`backend/knowledge_base/工业品网络营销_卫生级阀门公开资料.md`
- 数据范围：匿名访谈、公开短视频画面、企业公开网页、展会资料和行业媒体；不使用客户、订单、报价或询盘聊天记录

运行逻辑：

- 即使 `.env` 中配置了 API Key，默认也只运行本地规则；只有学习者在页面中明确勾选“使用 DeepSeek 增强本轮训练”后，才会向外部模型发送本轮画像、任务和检索片段。
- 如果没有配置 API Key、网络失败或模型返回异常，会自动回退到规则诊断/规则生成/规则审核/规则反馈。
- 本地测试默认关闭真实模型调用，避免消耗 API。
- `training_mode` 会传入生成 Agent，使提示词改写、任务拆解、结果审核、岗位实战和分阶测试生成不同的训练资源。
- 结果审核模式使用独立的 `candidate_output` 字段传递待审核 AI 输出，避免把失败文案误当作用户工作任务。

## 接口

### 获取岗位列表

```text
GET /api/roles
```

### 运行多 Agent 实训

```text
POST /api/train
```

请求示例：

```json
{
  "learner_id": "anonymous_user_001_marketing_manager",
  "role_id": "marketing_manager",
  "experience_years": 5,
  "ai_skill_level": "初级",
  "training_mode": "prompt",
  "allow_external_llm": false,
  "task": "以麦肯锡风格，对比 A 产品和 B 产品的用户体验，重点分析 C 功能。"
}
```

返回内容包含：

- 职业诊断 Agent 输出
- 领域知识生成 Agent 输出
- 质量审核 Agent 输出
- 反馈迭代 Agent 输出
- 匹配到的知识库来源
- 已调用 DeepSeek 的 Agent 列表

### 五种训练模式统一评分

```text
POST /api/score
```

请求示例：

```json
{
  "learner_id": "anonymous_user_001_marketing_manager",
  "role_id": "marketing_manager",
  "training_mode": "prompt",
  "original_task": "帮我写个报告。",
  "rewritten_prompt": "请基于产品资料，从用户路径、功能可用性和转化风险三个维度，对比 A 产品和 B 产品，并输出管理层报告。不得编造数据，无法确认的内容标注为待验证。"
}
```

返回内容包含：

- 总分
- 训练等级
- 当前训练模式对应的五维评分
- 修改建议
- 标准示例提示词
- 反馈迭代 Agent 的降维解释/专项补练/进阶挑战决策
- 80 分掌握线和是否解锁下一关

### 查看训练记录

```text
GET /api/records?learner_id=anonymous_user_001_marketing_manager&role_id=marketing_manager
```

每次调用 `/api/score` 后，后端会把训练模式、得分、是否达标、动态决策和薄弱维度追加保存到。任务和答案只保留最长 180 字的脱敏摘要，并掩码手机号、邮箱和身份证号：

```text
backend/data/training_records.jsonl
```

### 查看长期学习画像

```text
GET /api/learner-profile?learner_id=anonymous_user_001_marketing_manager&role_id=marketing_manager
```

后台会按匿名学习者聚合历史训练次数、平均分、长期薄弱维度、各训练模式的迁移通过次数和下一关建议。单题达到 80 分只代表本题达标；同一能力在两个不同任务中达到 80 分后，才标记为“稳定掌握”。下一次生成训练题和反馈路径时，会优先使用历史薄弱点。

该机制属于可解释的历史学习策略，不会使用少量用户记录直接微调 DeepSeek，也不会把未经人工审核的用户答案自动写入领域知识库。

## 竞赛指标复算

在项目根目录运行：

```powershell
python scripts/run_competition_evaluation.py
```

脚本会在关闭外部大模型的本地规则模式下运行 50 条工业品网络营销测试，并更新：

- `backend/test_results/industrial_marketing_complete_cases.json`：3 组完整画像及四 Agent 中间数据
- `backend/test_results/industrial_marketing_evaluation_50.json`：50 条逐项指标数据
- `项目材料/18_系统测试报告_20260817.md`：自动规则代理指标与风险识别报告

这些指标只是自动规则代理结果，用于验证规则、知识检索和多 Agent 调度的一致性，不等同于经专家验证的真实幻觉率、适配准确率或真实用户学习效果。提交前应再完成人工抽检与真实用户前后测。

## 当前状态

当前系统是“四个 DeepSeek 驱动 Agent + 规则兜底 + 后台长期学习画像”的完整多智能体原型。系统能够跨轮次读取同一匿名学习者的历史表现，围绕长期薄弱点生成补练任务，并用不同情境的迁移题验证稳定掌握。
