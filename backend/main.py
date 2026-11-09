import json
import mimetypes
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from app.learner_model import apply_history_to_score, build_learner_profile
from app.pipeline import run_training_pipeline
from app.prompt_scorer import score_prompt
from app.records import build_test_summary, list_score_records, save_score_record
from app.roles import ROLES, list_roles
from app.task_seed import generate_task_seed


HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
STATIC_DIR = Path(__file__).resolve().parent.parent / "demo_system"


class AgentRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        origin = self.headers.get("Origin", "")
        if origin in {"http://127.0.0.1:8010", "http://localhost:8010", "null"}:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if path == "/health":
            self._send_json(200, {"status": "ok", "service": "promptcraft-pro-backend"})
            return
        if path == "/api/roles":
            self._send_json(200, {"roles": list_roles()})
            return
        if path == "/api/records":
            learner_id = query.get("learner_id", [""])[0]
            role_id = query.get("role_id", [""])[0]
            self._send_json(200, {"records": list_score_records(learner_id=learner_id, role_id=role_id)})
            return
        if path == "/api/learner-profile":
            learner_id = query.get("learner_id", [""])[0]
            role_id = query.get("role_id", [""])[0]
            self._send_json(200, build_learner_profile(learner_id, role_id))
            return
        if path == "/api/test-summary":
            self._send_json(200, build_test_summary())
            return
        if self._send_static(path):
            return
        self._send_json(404, {"error": "not_found", "message": "接口不存在"})

    def _send_static(self, request_path):
        relative_path = "index.html" if request_path in {"/", "/index.html"} else unquote(request_path).lstrip("/")
        try:
            target = (STATIC_DIR / relative_path).resolve()
            target.relative_to(STATIC_DIR.resolve())
        except (ValueError, OSError):
            return False
        if not target.is_file():
            return False

        content = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache" if target.name == "index.html" else "public, max-age=3600")
        self.end_headers()
        self.wfile.write(content)
        return True

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in {"/api/train", "/api/score", "/api/task-seed"}:
            self._send_json(404, {"error": "not_found", "message": "接口不存在"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 1_000_000:
                self._send_json(413, {"error": "payload_too_large", "message": "请求内容过大"})
                return
            raw_body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(raw_body or "{}")
            _validate_payload(path, payload)
            learner_profile = build_learner_profile(payload.get("learner_id", ""), payload.get("role_id", ""))
            payload["_learning_profile"] = learner_profile
            if path == "/api/train":
                result = run_training_pipeline(payload)
            elif path == "/api/score":
                result = score_prompt(payload)
                result["record"] = save_score_record(payload, result)
                learner_profile = build_learner_profile(payload.get("learner_id", ""), payload.get("role_id", ""))
                result = apply_history_to_score(result, learner_profile)
            else:
                result = generate_task_seed(payload)
            self._send_json(200, result)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "bad_request", "message": "请求体不是合法 JSON"})
        except ValueError as exc:
            self._send_json(400, {"error": "bad_request", "message": str(exc)})
        except Exception:
            self._send_json(500, {"error": "server_error", "message": "服务器处理失败，请检查后端日志"})

    def log_message(self, fmt, *args):
        return


def _validate_payload(path, payload):
    if not isinstance(payload, dict):
        raise ValueError("请求体必须是 JSON 对象")
    role_id = payload.get("role_id", "marketing_manager")
    if role_id not in ROLES:
        raise ValueError("岗位编号不存在")
    if "allow_external_llm" in payload and not isinstance(payload["allow_external_llm"], bool):
        raise ValueError("allow_external_llm 必须是布尔值")
    if payload.get("training_mode", "prompt") not in {"prompt", "workflow", "review", "practice", "test"}:
        raise ValueError("训练模式不存在")
    if payload.get("ai_skill_level") not in {None, "", "初级", "中级", "高级"}:
        raise ValueError("AI 水平选项不存在")

    limits = {
        "task": 10_000,
        "original_task": 10_000,
        "rewritten_prompt": 30_000,
        "work_context": 10_000,
        "candidate_output": 20_000,
        "specific_position": 100,
        "learner_id": 120,
        "test_participant_code": 40,
    }
    for field, limit in limits.items():
        value = payload.get(field, "")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{field} 必须是文本")
        if len(value or "") > limit:
            raise ValueError(f"{field} 超出长度限制")

    for field, lower, upper in [("duration_seconds", 0, 86400), ("attempt_number", 1, 100)]:
        if field not in payload or payload[field] in (None, ""):
            continue
        try:
            number = int(payload[field])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} 必须是整数") from exc
        if not lower <= number <= upper:
            raise ValueError(f"{field} 必须在 {lower} 到 {upper} 之间")

    if path == "/api/train" and not payload.get("task", "").strip():
        raise ValueError("训练任务不能为空")
    if path == "/api/score" and not payload.get("rewritten_prompt", "").strip():
        raise ValueError("训练答案不能为空")

    for field, lower, upper in [("experience_years", 0, 50), ("theory_test_score", 0, 100)]:
        if field not in payload or payload[field] in (None, ""):
            continue
        try:
            number = int(payload[field])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} 必须是整数") from exc
        if not lower <= number <= upper:
            raise ValueError(f"{field} 必须在 {lower} 到 {upper} 之间")


def run():
    try:
        server = ExclusiveThreadingHTTPServer((HOST, PORT), AgentRequestHandler)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048:
            print("端口 8000 已被占用：请保留一个后端窗口，关闭其余旧窗口后重试。")
            return
        raise
    print(f"智训工坊后端已启动：http://{HOST}:{PORT}")
    print(f"健康检查：http://{HOST}:{PORT}/health")
    server.serve_forever()


class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False
    allow_reuse_port = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


if __name__ == "__main__":
    run()
