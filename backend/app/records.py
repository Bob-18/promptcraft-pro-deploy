import json
import hashlib
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RECORDS_FILE = DATA_DIR / "training_records.jsonl"


def save_score_record(payload, score_result):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    original = str(payload.get("original_task", ""))
    rewritten = str(payload.get("rewritten_prompt", ""))
    record = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "learner_id": _safe_identifier(payload.get("learner_id", "")),
        "test_participant_code": _safe_identifier(payload.get("test_participant_code", "")),
        "role_id": payload.get("role_id", "marketing_manager"),
        "specific_position": _safe_excerpt(payload.get("specific_position", ""), 60),
        "experience_years": _safe_number(payload.get("experience_years")),
        "ai_skill_level": _safe_excerpt(payload.get("ai_skill_level", ""), 12),
        "education_background": _safe_excerpt(payload.get("education_background", ""), 12),
        "theory_test_score": _safe_number(payload.get("theory_test_score")),
        "duration_seconds": _safe_number(payload.get("duration_seconds")),
        "attempt_number": _safe_number(payload.get("attempt_number")),
        "training_mode": score_result.get("training_mode", payload.get("training_mode", "prompt")),
        "mode_label": score_result.get("mode_label", "提示词改写"),
        "original_task": _safe_excerpt(original),
        "rewritten_prompt": _safe_excerpt(rewritten),
        "content_hash": hashlib.sha256(f"{original}\n{rewritten}".encode("utf-8")).hexdigest()[:16],
        "task_hash": hashlib.sha256(original.encode("utf-8")).hexdigest()[:16],
        "privacy_mode": "脱敏摘要",
        "score": score_result.get("score", 0),
        "level": score_result.get("level", ""),
        "improved": score_result.get("improved", 0),
        "mastery_passed": score_result.get("adaptive_decision", {}).get("mastery_passed", False),
        "adaptive_strategy": score_result.get("adaptive_decision", {}).get("strategy", ""),
        "weak_dimensions": score_result.get("adaptive_decision", {}).get("weak_dimensions", []),
        "dimension_scores": {
            item.get("label", "未命名维度"): item.get("score", 0)
            for item in score_result.get("details", [])
            if isinstance(item, dict)
        },
    }
    with RECORDS_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def _safe_excerpt(value, limit=180):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"1[3-9]\d{9}", "[手机号]", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[邮箱]", text)
    text = re.sub(r"\b\d{17}[0-9Xx]\b", "[身份证号]", text)
    return text[:limit] + ("..." if len(text) > limit else "")


def list_score_records(limit=30, learner_id="", role_id=""):
    return read_score_records(learner_id=learner_id, role_id=role_id, limit=limit)


def build_test_summary():
    grouped = {}
    for record in read_score_records():
        code = _safe_identifier(record.get("test_participant_code", ""))
        if not code:
            continue
        item = grouped.setdefault(
            code,
            {
                "participant_code": code,
                "attempts": 0,
                "scores": [],
                "duration_seconds": 0,
                "roles": set(),
                "training_modes": set(),
                "weak_dimensions": {},
            },
        )
        item["attempts"] += 1
        item["scores"].append(_safe_number(record.get("score")) or 0)
        item["duration_seconds"] += max(0, _safe_number(record.get("duration_seconds")) or 0)
        if record.get("role_id"):
            item["roles"].add(record["role_id"])
        if record.get("mode_label"):
            item["training_modes"].add(record["mode_label"])
        for dimension in record.get("weak_dimensions", []):
            item["weak_dimensions"][dimension] = item["weak_dimensions"].get(dimension, 0) + 1

    participants = []
    for item in grouped.values():
        scores = item.pop("scores")
        weak_counts = item.pop("weak_dimensions")
        item["first_score"] = scores[0] if scores else 0
        item["latest_score"] = scores[-1] if scores else 0
        item["best_score"] = max(scores, default=0)
        item["score_change"] = item["latest_score"] - item["first_score"]
        item["average_score"] = round(sum(scores) / len(scores), 1) if scores else 0
        item["roles"] = sorted(item["roles"])
        item["training_modes"] = sorted(item["training_modes"])
        item["frequent_weak_dimensions"] = [
            name for name, _ in sorted(weak_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
        ]
        participants.append(item)

    participants.sort(key=lambda item: item["participant_code"])
    return {
        "data_scope": "匿名正式测试记录；不包含未填写测试编号的普通体验与历史调试数据",
        "participant_count": len(participants),
        "record_count": sum(item["attempts"] for item in participants),
        "participants": participants,
    }


def read_score_records(learner_id="", role_id="", limit=None):
    if not RECORDS_FILE.exists():
        return []
    records = []
    for line in RECORDS_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            # Legacy records may predate privacy-safe storage. Never return their
            # full raw text through the API.
            record["original_task"] = _safe_excerpt(record.get("original_task", ""))
            record["rewritten_prompt"] = _safe_excerpt(record.get("rewritten_prompt", ""))
            if learner_id and record.get("learner_id") != _safe_identifier(learner_id):
                continue
            if role_id and record.get("role_id") != role_id:
                continue
            records.append(record)
        except json.JSONDecodeError:
            continue
    return records[-limit:] if limit else records


def _safe_identifier(value):
    return re.sub(r"[^A-Za-z0-9_-]", "", str(value or ""))[:120]


def _safe_number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
