import json
import re


UNCERTAINTY_MARKERS = ["待核验", "待验证", "无法确认", "不得编造", "禁止编造", "需要补充", "公开信息不足"]
FACT_MARKERS = ["认证", "型号", "材质", "316L", "压力", "温度", "客户案例", "成交", "%", "专利"]


def flatten_generated_result(result):
    payload = {
        "generation": result.get("generation", {}).get("resources", {}),
        "review": {
            "passed": result.get("review", {}).get("passed", []),
            "risks": result.get("review", {}).get("risks", []),
            "suggestions": result.get("review", {}).get("suggestions", []),
            "cross_checks": result.get("review", {}).get("cross_checks", []),
        },
        "feedback": {
            "next_task": result.get("feedback", {}).get("next_task", ""),
            "micro_goals": result.get("feedback", {}).get("micro_goals", []),
            "learning_path": result.get("feedback", {}).get("learning_path", []),
        },
    }
    return json.dumps(payload, ensure_ascii=False)


def flatten_generation_resources(result):
    return json.dumps(result.get("generation", {}).get("resources", {}), ensure_ascii=False)


def evaluate_result(result, expected, knowledge_text=""):
    generated_text = flatten_generated_result(result)
    hallucination_text = flatten_generation_resources(result)
    original_task = expected.get("original_task", "")
    if original_task:
        hallucination_text = hallucination_text.replace(original_task, "")
    required_points = expected.get("required_knowledge_points", [])
    covered_points = [point for point in required_points if point.lower() in generated_text.lower()]
    coverage_rate = round(100 * len(covered_points) / max(1, len(required_points)), 2)

    expected_level = expected.get("expected_training_level", "")
    actual_level = result.get("feedback", {}).get("training_level", "")
    resource_match = expected_level == actual_level

    unsupported_claims, factual_claims = _find_unsupported_claims(hallucination_text, knowledge_text)
    forbidden_hits = [claim for claim in expected.get("forbidden_claims", []) if claim in hallucination_text]
    unsupported_total = len(unsupported_claims) + len(forbidden_hits)
    hallucination_rate = round(100 * unsupported_total / max(1, factual_claims), 2)

    expected_risks = expected.get("expected_risk_terms", [])
    review_text = " ".join(result.get("review", {}).get("risks", []))
    detected_risks = [risk for risk in expected_risks if risk in review_text]
    risk_detection_rate = round(100 * len(detected_risks) / max(1, len(expected_risks)), 2) if expected_risks else 100.0

    return {
        "metric_scope": "自动规则代理评估（非专家人工终测）",
        "human_validation_required": True,
        "hallucination_rate": hallucination_rate,
        "unsupported_claims": unsupported_claims + forbidden_hits,
        "factual_claim_count": factual_claims,
        "resource_match": resource_match,
        "expected_training_level": expected_level,
        "actual_training_level": actual_level,
        "knowledge_coverage_rate": coverage_rate,
        "covered_knowledge_points": covered_points,
        "missing_knowledge_points": [point for point in required_points if point not in covered_points],
        "risk_detection_rate": risk_detection_rate,
        "detected_risks": detected_risks,
    }


def summarize_evaluations(evaluations):
    count = len(evaluations)
    factual_claims = sum(item["factual_claim_count"] for item in evaluations)
    unsupported = sum(len(item["unsupported_claims"]) for item in evaluations)
    return {
        "metric_scope": "自动规则代理评估（非专家人工终测）",
        "human_validation_required": True,
        "case_count": count,
        "hallucination_rate": round(100 * unsupported / max(1, factual_claims), 2),
        "resource_match_rate": round(100 * sum(item["resource_match"] for item in evaluations) / max(1, count), 2),
        "knowledge_coverage_rate": round(sum(item["knowledge_coverage_rate"] for item in evaluations) / max(1, count), 2),
        "risk_detection_rate": round(sum(item["risk_detection_rate"] for item in evaluations) / max(1, count), 2),
        "unsupported_claim_count": unsupported,
        "factual_claim_count": factual_claims,
    }


def _find_unsupported_claims(generated_text, knowledge_text):
    sentences = [item.strip() for item in re.split(r"[。！？；\n]+", generated_text) if item.strip()]
    factual = [sentence for sentence in sentences if any(marker in sentence for marker in FACT_MARKERS)]
    unsupported = []
    for sentence in factual:
        if any(marker in sentence for marker in UNCERTAINTY_MARKERS):
            continue
        precise_tokens = re.findall(r"\d+(?:\.\d+)?%?|[A-Za-z]+-?\d+", sentence)
        if precise_tokens and not all(token in knowledge_text for token in precise_tokens):
            unsupported.append(sentence[:160])
    return unsupported, len(factual)
