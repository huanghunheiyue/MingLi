"""
反馈凭证签名 - 借鉴 zhouli-translator 的 signFeedbackToken 设计
用于防止反馈接口滥用
"""
from __future__ import annotations
import hmac
import hashlib
import secrets
import time

DEFAULT_SECRET = "mingli-feedback-secret"


def make_response_id() -> str:
    return secrets.token_urlsafe(16)


def sign_token(secret: str, response_id: str, surface: str, ttl_ms: int = 24 * 60 * 60 * 1000) -> dict:
    """签发反馈凭证"""
    ts = int(time.time() * 1000)
    expires = ts + ttl_ms
    payload = f"{response_id}|{surface}|{expires}"
    sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "feedbackToken": f"{payload}|{sig}",
        "responseId": response_id,
        "surface": surface,
        "expiresAt": expires,
    }


def verify_token(secret: str, token: str, response_id: str, surface: str) -> bool:
    """校验反馈凭证"""
    if not token or "|" not in token:
        return False
    parts = token.split("|")
    if len(parts) != 4:
        return False
    rid, surf, exp, sig = parts
    if rid != response_id or surf != surface:
        return False
    try:
        if int(exp) < int(time.time() * 1000):
            return False
    except ValueError:
        return False
    payload = f"{rid}|{surf}|{exp}"
    expected = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)