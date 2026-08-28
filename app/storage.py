"""
数据持久化层
- history.json: 生成历史
- feedback.json: 用户反馈
"""
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

from .config import settings


_lock = threading.Lock()


def _ensure_file(p: Path, default):
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(default, ensure_ascii=False), encoding="utf-8")


def _read(p: Path):
    _ensure_file(p, [])
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write(p: Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# -------- 生成历史 --------
def save_history(record: dict) -> dict:
    record.setdefault("id", str(uuid.uuid4()))
    record.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    with _lock:
        items = _read(settings.HISTORY_FILE)
        items.insert(0, record)
        # 最多保留 500 条
        items = items[:500]
        _write(settings.HISTORY_FILE, items)
    return record


def list_history(limit: int = 20):
    with _lock:
        items = _read(settings.HISTORY_FILE)
    return items[:limit]


def get_history(hid: str):
    with _lock:
        items = _read(settings.HISTORY_FILE)
    for it in items:
        if it.get("id") == hid:
            return it
    return None


# -------- 反馈 --------
def save_feedback(record: dict) -> dict:
    record.setdefault("id", str(uuid.uuid4()))
    record.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    with _lock:
        items = _read(settings.FEEDBACK_FILE)
        items.insert(0, record)
        items = items[:1000]
        _write(settings.FEEDBACK_FILE, items)
    return record