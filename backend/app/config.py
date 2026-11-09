import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def load_env_file(path=ENV_PATH):
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_model_config():
    file_values = load_env_file()
    return {
        "api_base_url": os.getenv("API_BASE_URL") or file_values.get("API_BASE_URL", ""),
        "api_key": os.getenv("API_KEY") or file_values.get("API_KEY", ""),
        "model_name": os.getenv("MODEL_NAME") or file_values.get("MODEL_NAME", "deepseek-chat"),
        "disabled": os.getenv("DISABLE_LLM", "0") == "1",
    }


def is_llm_available():
    config = get_model_config()
    return bool(config["api_base_url"] and config["api_key"] and config["model_name"] and not config["disabled"])


def is_external_llm_allowed(payload):
    return bool(payload.get("allow_external_llm", False)) and is_llm_available()
