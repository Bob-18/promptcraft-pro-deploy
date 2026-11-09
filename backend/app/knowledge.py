import re
from pathlib import Path

from .roles import get_role


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge_base"
MAX_CHUNKS = 5

DOMAIN_TERMS = [
    "竞品", "用户体验", "报告", "市场", "营销", "短视频", "文案", "平台", "采购", "客户", "老板",
    "阀门", "角座阀", "隔膜阀", "比例调节", "卫生级", "食品", "制药", "灭菌", "CIP", "清洗",
    "公开资料", "来源", "认证", "参数", "询盘", "转化", "财报", "现金流", "代码", "安全", "会议",
    "纪要", "产品需求", "PRD", "设备", "报警", "传感器", "工艺", "智能制造", "工业互联网", "运维",
]


def read_knowledge_file(filename):
    path = KNOWLEDGE_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def retrieve_knowledge(role_id, task):
    role = get_role(role_id)
    query_terms = _query_terms(task, role)
    candidates = []

    for filename in role["knowledge_files"]:
        content = read_knowledge_file(filename)
        if not content:
            continue
        for index, chunk in enumerate(_split_markdown(content)):
            score = _score_chunk(filename, chunk, query_terms)
            candidates.append(
                {
                    "source": f"{filename}｜{chunk['heading']}",
                    "file": filename,
                    "section": chunk["heading"],
                    "content": chunk["content"],
                    "retrieval_score": score,
                    "chunk_index": index,
                }
            )

    selected = _select_chunks(candidates)
    return {
        "role_label": role["label"],
        "task_keywords": query_terms,
        "retrieval_method": "岗位过滤 + 标题/正文关键词切片排序",
        "sources": selected,
    }


def _split_markdown(content, max_chars=1400):
    chunks = []
    heading = "文档概述"
    buffer = []

    def flush():
        nonlocal buffer
        text = "\n".join(buffer).strip()
        if not text:
            buffer = []
            return
        while len(text) > max_chars:
            cut = text.rfind("\n", 0, max_chars)
            if cut < max_chars // 2:
                cut = max_chars
            chunks.append({"heading": heading, "content": text[:cut].strip()})
            text = text[cut:].strip()
        if text:
            chunks.append({"heading": heading, "content": text})
        buffer = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("## ") or line.startswith("### "):
            flush()
            heading = line.lstrip("# ").strip()
            continue
        if line.startswith("# "):
            if buffer:
                flush()
            heading = line.lstrip("# ").strip()
            continue
        buffer.append(raw_line)
    flush()
    return chunks


def _query_terms(task, role):
    text = f"{task} {' '.join(role.get('tasks', []))} {role.get('label', '')}"
    terms = [term for term in DOMAIN_TERMS if term.lower() in text.lower()]
    seen = {item.lower() for item in terms}
    for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9+._-]{1,20}", text):
        if token.lower() not in seen:
            terms.append(token)
            seen.add(token.lower())
    return terms[:18]


def _score_chunk(filename, chunk, query_terms):
    heading = chunk["heading"].lower()
    content = chunk["content"].lower()
    filename_lower = filename.lower()
    score = 0
    for term in query_terms:
        needle = term.lower()
        if needle in filename_lower:
            score += 5
        if needle in heading:
            score += 4
        score += min(content.count(needle), 3)
    if filename == "职场AI使用规范.md":
        score += 1
    return score


def _select_chunks(candidates):
    if not candidates:
        return []

    ranked = sorted(candidates, key=lambda item: (-item["retrieval_score"], item["file"], item["chunk_index"]))
    selected = [item for item in ranked if item["retrieval_score"] > 0][:MAX_CHUNKS]
    if not selected:
        selected = ranked[:MAX_CHUNKS]

    norm_chunk = next((item for item in ranked if item["file"] == "职场AI使用规范.md"), None)
    if norm_chunk and all(item["file"] != "职场AI使用规范.md" for item in selected):
        selected = (selected[: MAX_CHUNKS - 1] + [norm_chunk])[:MAX_CHUNKS]

    return [
        {
            "source": item["source"],
            "file": item["file"],
            "section": item["section"],
            "content": item["content"],
            "retrieval_score": item["retrieval_score"],
        }
        for item in selected
    ]
