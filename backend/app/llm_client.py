import json
import urllib.error
import urllib.request

from .config import get_model_config, is_llm_available


class LLMError(RuntimeError):
    pass


def chat_json(messages, temperature=0.2, timeout=12):
    if not is_llm_available():
        raise LLMError("LLM is not configured")

    config = get_model_config()
    url = config["api_base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": config["model_name"],
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise LLMError(f"LLM HTTP error {exc.code}: {body[:300]}") from exc
    except Exception as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    try:
        result = json.loads(raw)
        content = result["choices"][0]["message"]["content"]
        return _parse_json_content(content)
    except Exception as exc:
        raise LLMError(f"LLM response parse failed: {exc}") from exc


def _parse_json_content(content):
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        text = text[start : end + 1]
    return json.loads(text)
