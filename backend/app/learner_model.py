from collections import Counter

from .records import read_score_records


MODE_ORDER = [
    ("prompt", "提示词改写"),
    ("workflow", "任务拆解"),
    ("review", "结果审核"),
    ("practice", "岗位实战"),
    ("test", "分阶测试题"),
]


def build_learner_profile(learner_id="", role_id=""):
    records = read_score_records(learner_id=learner_id, role_id=role_id) if learner_id else []
    scores = [_number(record.get("score")) for record in records]
    weak_counter = Counter(
        str(dimension)
        for record in records
        for dimension in record.get("weak_dimensions", [])
        if str(dimension).strip()
    )
    modes = {}
    for mode, label in MODE_ORDER:
        mode_records = [record for record in records if record.get("training_mode") == mode]
        passed_tasks = {
            record.get("task_hash") or record.get("content_hash")
            for record in mode_records
            if record.get("mastery_passed")
        }
        passed_tasks.discard(None)
        stable = len(passed_tasks) >= 2
        passed_once = len(passed_tasks) == 1
        modes[mode] = {
            "label": label,
            "attempts": len(mode_records),
            "best_score": max((_number(item.get("score")) for item in mode_records), default=None),
            "passed_tasks": len(passed_tasks),
            "stable_mastery": stable,
            "status": "稳定掌握" if stable else "等待迁移验证" if passed_once else "训练中" if mode_records else "未开始",
        }

    next_mode = next((mode for mode, _ in MODE_ORDER if not modes[mode]["stable_mastery"]), None)
    next_focus = weak_counter.most_common(1)[0][0] if weak_counter else "任务目标与证据链"
    growth = 0
    if len(scores) >= 2:
        early = scores[: min(3, len(scores))]
        recent = scores[-min(3, len(scores)) :]
        growth = round(sum(recent) / len(recent) - sum(early) / len(early))

    return {
        "learner_id": learner_id,
        "role_id": role_id,
        "history_used": bool(records),
        "attempts": len(records),
        "average_score": round(sum(scores) / len(scores)) if scores else None,
        "best_score": max(scores) if scores else None,
        "recent_score": scores[-1] if scores else None,
        "growth": growth,
        "weak_dimensions": [item for item, _ in weak_counter.most_common(3)],
        "next_focus": next_focus,
        "next_mode": next_mode,
        "next_mode_label": dict(MODE_ORDER).get(next_mode, "成长报告"),
        "modes": modes,
        "summary": (
            f"已读取 {len(records)} 次历史训练，下一步重点补练“{next_focus}”。"
            if records
            else "尚无历史训练，完成本轮后将建立第一条成长记录。"
        ),
    }


def apply_history_to_score(score_result, profile):
    result = dict(score_result)
    result["learning_profile"] = profile
    decision = dict(result.get("adaptive_decision", {}))
    mode = result.get("training_mode", "prompt")
    mode_state = profile.get("modes", {}).get(mode, {})
    current_score = _number(result.get("score"))
    focus = profile.get("next_focus", "任务目标与证据链")

    decision["history_used"] = profile.get("history_used", False)
    decision["stable_mastery"] = mode_state.get("stable_mastery", False)
    decision["historical_focus"] = focus
    decision["history_attempts"] = profile.get("attempts", 0)
    if current_score < 80:
        decision["next_action"] = f"结合历史记录，先只补练“{focus}”，修改后再次评分。"
    elif mode_state.get("stable_mastery"):
        decision["next_action"] = f"已在两个不同任务中达标，可以进入“{profile.get('next_mode_label', '下一关')}”。"
    else:
        decision["next_action"] = "本题已达标，请换一个同岗位新情境独立完成；再次达到 80 分才算稳定掌握。"
    result["adaptive_decision"] = decision
    return result


def _number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
