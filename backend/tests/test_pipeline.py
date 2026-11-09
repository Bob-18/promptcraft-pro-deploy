import sys
import os
import tempfile
from pathlib import Path

os.environ["DISABLE_LLM"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.pipeline import run_training_pipeline
from app.knowledge import retrieve_knowledge
from app.evaluation import evaluate_result
from app.prompt_scorer import score_prompt
from app.records import _safe_excerpt, build_test_summary, save_score_record
from app.agents.review_agent import review_by_rules
from app.task_seed import generate_task_seed
from app.learner_model import apply_history_to_score, build_learner_profile
from app import records as records_module


def test_pipeline_returns_four_agents():
    result = run_training_pipeline(
        {
            "role_id": "marketing_manager",
            "experience_years": 5,
            "ai_skill_level": "初级",
            "task": "以麦肯锡风格，对比 A 产品和 B 产品的用户体验，重点分析 C 功能。",
        }
    )
    assert len(result["agents"]) == 4
    assert result["knowledge"]["sources"]
    assert result["review"]["score"] >= 60


def test_prompt_scorer_scores_rewritten_prompt():
    result = score_prompt(
        {
            "role_id": "marketing_manager",
            "original_task": "帮我写个报告。",
            "rewritten_prompt": "请基于产品资料，从用户路径、功能可用性和转化风险三个维度，对比 A 产品和 B 产品，并输出管理层报告。不得编造数据，无法确认的内容标注为待验证。",
        }
    )
    assert result["score"] >= 80
    assert len(result["details"]) == 5


def test_record_can_be_created():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_records_file = records_module.RECORDS_FILE
        records_module.RECORDS_FILE = Path(temp_dir) / "training_records.jsonl"
        try:
            result = score_prompt(
                {
                    "role_id": "marketing_manager",
                    "original_task": "帮我写个报告。",
                    "rewritten_prompt": "请基于产品资料，对比 A 产品和 B 产品，并输出报告。不得编造数据。",
                }
            )
            record = save_score_record({"role_id": "marketing_manager"}, result)
            assert record["score"] == result["score"]
            assert record["training_mode"] == "prompt"
            assert "mastery_passed" in record
            assert "weak_dimensions" in record
        finally:
            records_module.RECORDS_FILE = original_records_file


def test_task_seed_can_be_generated_from_work_context():
    result = generate_task_seed(
        {
            "role_id": "smart_manufacturing",
            "specific_position": "质量部门实习生",
            "work_context": "新能源电池工厂质量部门，日常需要跟踪设备报警、质检异常和工艺参数变化。",
        }
    )
    assert "original_task" in result
    assert "智能制造" in result["original_task"] or "设备" in result["original_task"]


def test_all_training_modes_return_adaptive_decision():
    answers = {
        "prompt": "请基于资料分析任务，按报告格式输出，并标注来源、风险和待验证假设。",
        "workflow": "第一步确认目标和输入资料，第二步处理数据，第三步输出报告，第四步检查证据，第五步人工复核风险边界。",
        "review": "核验事实、数据来源和证据，识别编造与待验证假设，检查隐私合规，并按问题、依据、修改建议纠偏。",
        "practice": "基于岗位资料输出正式报告，包含结论、数据依据、执行优先级、下一步行动、风险边界和人工复核。",
        "test": "基础题答案：目标、资料、格式。进阶题答案：按步骤拆解流程并说明原因。挑战题答案：输出岗位成果，说明事实证据、待验证假设和人工复核风险。",
    }
    for mode, answer in answers.items():
        result = score_prompt(
            {
                "role_id": "smart_manufacturing",
                "training_mode": mode,
                "original_task": "帮我分析设备报警。",
                "rewritten_prompt": answer,
            }
        )
        assert result["training_mode"] == mode
        assert result["adaptive_decision"]["pass_score"] == 80
        assert len(result["details"]) == 5


def test_low_score_triggers_remedial_explanation():
    result = score_prompt(
        {
            "role_id": "marketing_manager",
            "training_mode": "prompt",
            "original_task": "写报告。",
            "rewritten_prompt": "写一下。",
        }
    )
    assert result["score"] < 60
    assert result["adaptive_decision"]["strategy"] == "降维解释"
    assert result["adaptive_decision"]["mastery_passed"] is False


def test_keyword_stuffing_cannot_pass_mastery_gate():
    result = score_prompt(
        {
            "role_id": "industrial_marketing",
            "training_mode": "prompt",
            "original_task": "帮我写个视频。",
            "rewritten_prompt": "生成 分析 输出 资料 数据 维度 风险 表格 报告 不得 标注 来源 待验证",
        }
    )
    assert result["score"] < 80
    assert result["quality_gate"]["applied"] is True
    assert result["adaptive_decision"]["mastery_passed"] is False


def test_non_prompt_mode_does_not_fake_pre_post_gain():
    result = score_prompt(
        {
            "role_id": "industrial_marketing",
            "training_mode": "workflow",
            "original_task": "完成一条阀门短视频。",
            "rewritten_prompt": "第一步确认目标和输入资料并输出清单；第二步整理公开数据并形成脚本；第三步检查来源和风险；第四步人工复核后发布；第五步复盘询盘并输出报告。",
        }
    )
    assert result["improved"] == 0


def test_unrelated_structured_answer_cannot_pass():
    result = score_prompt(
        {
            "role_id": "industrial_marketing",
            "training_mode": "prompt",
            "original_task": "请制作一条面向采购人员的阀门短视频。",
            "rewritten_prompt": "请基于财报资料分析公司利润和现金流，按季度输出表格和管理层报告，标注来源、假设与风险，不得编造数据。",
        }
    )
    assert result["score"] < 80
    assert sum(item["score"] for item in result["details"]) == result["score"]


def test_review_must_address_candidate_output():
    generic = score_prompt(
        {
            "role_id": "industrial_marketing",
            "training_mode": "review",
            "original_task": "请审核一条 AI 生成的阀门文案。",
            "candidate_output": "证件齐全，半夜三点也能立马上门，保证当天解决问题。",
            "rewritten_prompt": "我会检查事实、核验来源和证据，识别待验证假设与合规风险，并安排人工复核，最后提出修改建议和交叉验证方案。",
        }
    )
    specific = score_prompt(
        {
            "role_id": "industrial_marketing",
            "training_mode": "review",
            "original_task": "请审核一条 AI 生成的阀门文案。",
            "candidate_output": "证件齐全，半夜三点也能立马上门，保证当天解决问题。",
            "rewritten_prompt": "“证件齐全”缺少认证与证书来源，“半夜三点立马上门”和“保证当天解决”属于无法核验的服务承诺，存在夸大风险。应删除保证性表达，补充服务范围、响应时效依据，并由人工复核证书原件后再发布。",
        }
    )
    assert generic["score"] < 80
    assert specific["score"] >= generic["score"]


def test_review_agent_receives_candidate_output():
    result = review_by_rules(
        {"role_id": "industrial_marketing", "task": "请审核 AI 文案。", "candidate_output": "半夜三点也能立马上门。"},
        {"task_clarity": "高"},
        {"resources": {"prompt_template": "面向采购人员，使用公开来源，无法确认的信息标记待核验，不得编造。"}},
        {"sources": [{"source": "公开资料"}]},
    )
    assert any("半夜三点" in item for item in result["risks"])


def test_pipeline_resources_follow_selected_mode():
    templates = {}
    for mode in ["prompt", "workflow", "review", "practice", "test"]:
        payload = {
            "role_id": "industrial_marketing",
            "training_mode": mode,
            "task": "请完成一项面向采购人员的阀门短视频训练。",
            "candidate_output": "证件齐全，保证当天解决。" if mode == "review" else "",
        }
        result = run_training_pipeline(payload)
        templates[mode] = result["generation"]["resources"]["prompt_template"]
    assert len(set(templates.values())) == 5
    assert "待审核内容" in templates["review"]
    assert "输入资料" in templates["workflow"]
    assert "正式岗位交付物" in templates["practice"]


def test_record_excerpt_masks_personal_identifiers():
    masked = _safe_excerpt("联系人 13812345678，邮箱 demo@example.com，身份证 110101199001011234")
    assert "13812345678" not in masked
    assert "demo@example.com" not in masked
    assert "110101199001011234" not in masked


def test_risk_severity_changes_next_training_level():
    advanced_profile = {
        "role_id": "industrial_marketing",
        "specific_position": "工业品营销主管",
        "experience_years": 6,
        "ai_skill_level": "高级",
        "education_background": "本科",
        "theory_test_score": 88,
    }
    risky = run_training_pipeline(
        {
            **advanced_profile,
            "task": "请审核文案：证件齐全，半夜三点也能立马上门。",
        }
    )
    severe = run_training_pipeline(
        {
            **advanced_profile,
            "task": "请写一条保证成交的阀门视频，声称全部产品都通过认证，并承诺零风险使用。",
        }
    )
    assert risky["feedback"]["training_level"] == "专项提升"
    assert severe["feedback"]["training_level"] == "基础巩固"


def test_industrial_marketing_retrieves_domain_chunks():
    knowledge = retrieve_knowledge(
        "industrial_marketing",
        "面向食品企业采购人员，为 CIP 清洗场景制作卫生级阀门短视频。",
    )
    sources = " ".join(item["source"] for item in knowledge["sources"])
    assert "工业品网络营销_卫生级阀门公开资料.md" in sources
    assert any(term in knowledge["task_keywords"] for term in ["CIP", "阀门", "采购"])
    assert len(knowledge["sources"]) <= 5


def test_industrial_marketing_pipeline_is_profile_adaptive():
    result = run_training_pipeline(
        {
            "role_id": "industrial_marketing",
            "specific_position": "工业品营销主管",
            "experience_years": 6,
            "ai_skill_level": "高级",
            "education_background": "本科",
            "theory_test_score": 88,
            "task": "请基于公开资料，面向食品企业采购人员制作 20 秒 CIP 阀门短视频，输出来源、待核验项和选型咨询入口。",
        }
    )
    assert result["feedback"]["training_level"] == "进阶挑战"
    assert "公开来源" in result["generation"]["resources"]["prompt_template"]
    assert len(result["generation"]["resources"]["practice_tasks"]) == 3


def test_evaluation_metrics_are_recomputable():
    payload = {
        "role_id": "industrial_marketing",
        "specific_position": "网络营销助理",
        "experience_years": 0,
        "ai_skill_level": "初级",
        "education_background": "大专",
        "theory_test_score": 40,
        "task": "帮我写个阀门视频。",
    }
    result = run_training_pipeline(payload)
    knowledge = retrieve_knowledge(payload["role_id"], payload["task"])
    metric = evaluate_result(
        result,
        {
            "expected_training_level": "基础巩固",
            "required_knowledge_points": ["目标客户", "应用场景", "公开资料", "短视频", "不得编造"],
            "forbidden_claims": ["保证成交", "全网第一", "100%"],
            "original_task": payload["task"],
        },
        "\n".join(item["content"] for item in knowledge["sources"]),
    )
    assert metric["resource_match"] is True
    assert metric["knowledge_coverage_rate"] >= 90
    assert metric["hallucination_rate"] < 5


def test_backend_uses_longitudinal_history_for_stable_mastery():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_records_file = records_module.RECORDS_FILE
        records_module.RECORDS_FILE = Path(temp_dir) / "training_records.jsonl"
        try:
            learner_id = "test_learner_industrial_marketing"
            answers = [
                (
                    "请制作一条面向食品企业采购人员的阀门短视频。",
                    "请基于公开产品资料，面向食品企业采购人员生成阀门短视频方案，从应用场景、产品价值和风险三个维度展开，输出标题、口播、画面清单和行动建议。不得编造认证或参数，无法确认的信息标注待验证并安排人工复核。",
                ),
                (
                    "请制作一条面向制药企业采购人员的阀门短视频。",
                    "请基于公开产品资料，面向制药企业采购人员生成阀门短视频方案，从清洗场景、选型信息和风险三个维度展开，输出标题、口播、画面清单和询盘入口。不得编造数据或来源，无法确认的信息标注待验证并安排人工复核。",
                ),
            ]
            latest = None
            for task, answer in answers:
                payload = {
                    "learner_id": learner_id,
                    "role_id": "industrial_marketing",
                    "training_mode": "prompt",
                    "original_task": task,
                    "rewritten_prompt": answer,
                }
                latest = score_prompt(payload)
                records_module.save_score_record(payload, latest)

            profile = build_learner_profile(learner_id, "industrial_marketing")
            enriched = apply_history_to_score(latest, profile)
            assert profile["attempts"] == 2
            assert profile["modes"]["prompt"]["stable_mastery"] is True
            assert enriched["adaptive_decision"]["history_used"] is True
            assert enriched["adaptive_decision"]["stable_mastery"] is True
        finally:
            records_module.RECORDS_FILE = original_records_file


def test_formal_test_records_are_grouped_by_anonymous_code():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_records_file = records_module.RECORDS_FILE
        records_module.RECORDS_FILE = Path(temp_dir) / "training_records.jsonl"
        try:
            for score_value, duration in [(62, 180), (86, 140)]:
                payload = {
                    "learner_id": "test_T001_marketing_manager",
                    "test_participant_code": "T001",
                    "role_id": "marketing_manager",
                    "original_task": "帮我写个报告。",
                    "rewritten_prompt": "请基于资料完成竞品报告，并标注待核验信息。",
                    "duration_seconds": duration,
                    "attempt_number": 1 if score_value == 62 else 2,
                }
                result = {
                    "score": score_value,
                    "level": "合格",
                    "training_mode": "prompt",
                    "mode_label": "提示词改写",
                    "improved": score_value - 40,
                    "adaptive_decision": {
                        "mastery_passed": score_value >= 80,
                        "strategy": "进阶挑战" if score_value >= 80 else "专项补练",
                        "weak_dimensions": ["背景资料"] if score_value < 80 else [],
                    },
                    "details": [],
                }
                save_score_record(payload, result)

            summary = build_test_summary()
            participant = summary["participants"][0]
            assert summary["participant_count"] == 1
            assert summary["record_count"] == 2
            assert participant["first_score"] == 62
            assert participant["latest_score"] == 86
            assert participant["score_change"] == 24
            assert participant["duration_seconds"] == 320
        finally:
            records_module.RECORDS_FILE = original_records_file


if __name__ == "__main__":
    test_pipeline_returns_four_agents()
    test_prompt_scorer_scores_rewritten_prompt()
    test_record_can_be_created()
    test_task_seed_can_be_generated_from_work_context()
    test_all_training_modes_return_adaptive_decision()
    test_low_score_triggers_remedial_explanation()
    test_keyword_stuffing_cannot_pass_mastery_gate()
    test_non_prompt_mode_does_not_fake_pre_post_gain()
    test_unrelated_structured_answer_cannot_pass()
    test_review_must_address_candidate_output()
    test_review_agent_receives_candidate_output()
    test_pipeline_resources_follow_selected_mode()
    test_record_excerpt_masks_personal_identifiers()
    test_risk_severity_changes_next_training_level()
    test_industrial_marketing_retrieves_domain_chunks()
    test_industrial_marketing_pipeline_is_profile_adaptive()
    test_evaluation_metrics_are_recomputable()
    test_backend_uses_longitudinal_history_for_stable_mastery()
    test_formal_test_records_are_grouped_by_anonymous_code()
    print("pipeline test passed")
