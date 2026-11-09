from .agents.diagnosis_agent import diagnose
from .agents.feedback_agent import feedback
from .agents.generation_agent import generate
from .agents.review_agent import review
from .knowledge import retrieve_knowledge


def run_training_pipeline(payload):
    role_id = payload.get("role_id", "marketing_manager")
    task = payload.get("task", "")
    knowledge = retrieve_knowledge(role_id, task)
    diagnosis = diagnose(payload, knowledge)
    generation = generate(payload, diagnosis, knowledge)
    quality_review = review(payload, diagnosis, generation, knowledge)
    iteration = feedback(payload, diagnosis, quality_review)
    agents = [diagnosis, generation, quality_review, iteration]
    llm_agents = [agent["agent"] for agent in agents if agent.get("source") == "DeepSeek"]

    return {
        "project": "智训工坊 / PromptCraft Pro",
        "mode": "llm_enhanced_multi_agent_v1" if llm_agents else "local_rule_multi_agent_v1",
        "llm_agents": llm_agents,
        "input_summary": {
            "role_id": role_id,
            "specific_position": payload.get("specific_position", ""),
            "training_mode": payload.get("training_mode", "prompt"),
            "external_llm_enabled": bool(payload.get("allow_external_llm")),
        },
        "knowledge": {
            "role_label": knowledge["role_label"],
            "task_keywords": knowledge["task_keywords"],
            "retrieval_method": knowledge.get("retrieval_method", "岗位知识库检索"),
            "sources": [item["source"] for item in knowledge["sources"]],
            "source_details": [
                {
                    "source": item["source"],
                    "file": item.get("file", item["source"]),
                    "section": item.get("section", ""),
                    "retrieval_score": item.get("retrieval_score", 0),
                }
                for item in knowledge["sources"]
            ],
        },
        "agents": agents,
        "diagnosis": diagnosis,
        "generation": generation,
        "review": quality_review,
        "feedback": iteration,
        "learning_profile": payload.get("_learning_profile", {}),
    }
