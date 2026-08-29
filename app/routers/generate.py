"""
文案生成路由
- POST /api/generate        非流式
- POST /api/generate/stream 流式 (SSE)
- GET  /api/subjects?type=eulogy
"""
import json
import time
import asyncio
import hashlib
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from ..models import GenerateRequest, GenerateResponse
from .. import storage
from ..prompts import build_prompt
from ..knowledge_base import list_subjects, get_context_for_subject, _kg
from ..llm_client import client, parse_json_or_text
from ..security import is_prompt_injection, prompt_injection_block_message, looks_like_hijacked_output, assess_generated_text, incomplete_error_message
from ..rate_limit import GENERATE_LIMITER

router = APIRouter()

# ---- 简单 LRU 缓存：5 分钟内同请求直接返回，缓解 aliyun token-plan 端点的 TTFT 排队 ----
# key: sha256(content_type|subject|sorted_params)  value: (saved_record, expire_ts)
_RESULT_CACHE: dict = {}
_CACHE_TTL_SEC = 300


def _cache_key(req) -> str:
    params = {
        "relation": getattr(req, "relation", None),
        "occasion": getattr(req, "occasion", None),
        "poem_type": getattr(req, "poem_type", None),
        "person": getattr(req, "person", None),
        "length": getattr(req, "length", None),
        "author_role": getattr(req, "author_role", None),
        "tone": getattr(req, "tone", None),
        "length_meme": getattr(req, "meme_length", None),
    }
    raw = f"{req.content_type}|{req.subject}|{json.dumps(params, sort_keys=True, ensure_ascii=False)}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _cache_get(key: str):
    item = _RESULT_CACHE.get(key)
    if not item:
        return None
    record, expire_ts = item
    if time.time() > expire_ts:
        _RESULT_CACHE.pop(key, None)
        return None
    return record


def _cache_set(key: str, record: dict):
    _RESULT_CACHE[key] = (record, time.time() + _CACHE_TTL_SEC)
    # 简易 LRU：超过 200 条清理过期
    if len(_RESULT_CACHE) > 200:
        now = time.time()
        expired_keys = [k for k, (_, exp) in _RESULT_CACHE.items() if now > exp]
        for k in expired_keys:
            _RESULT_CACHE.pop(k, None)


# ---- max_tokens: qwen3.8-flash 实测 JSON 仅 ~200 tokens，给 768 既能容纳又减少排队 TTFT ----
_STREAM_MAX_TOKENS = 768
_CHAT_MAX_TOKENS = 1024



def _format_body(parsed: dict, content_type: str, fallback: str) -> str:
    """把 LLM 解析结果格式化为人类可读的文本 body

    - couplet: 上下联 + 横批 + 创作思路（因为 prompt JSON 没有 body 字段）
    - 其他: 直接用 parsed["body"] 字段
    - fallback: 解析失败时用原始 markdown 文本
    """
    if content_type == "couplet":
        parts = []
        if parsed.get("upper"):
            parts.append(f"上联：{parsed['upper']}")
        if parsed.get("lower"):
            parts.append(f"下联：{parsed['lower']}")
        if parsed.get("horizontal"):
            parts.append(f"横批：{parsed['horizontal']}")
        if parsed.get("note"):
            parts.append(f"\n创作思路：{parsed['note']}")
        return "\n".join(parts) if parts else fallback
    # 其他 content_type (poem/elegiac/meme) 已经有 body 字段
    body = parsed.get("body")
    if body:
        return body
    return fallback


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.client.host if request.client else "anon")


@router.get("/api/subjects")
async def subjects(
    content_type: str = Query("couplet", alias="type"),
    type_filter: str = Query("", alias="entity_type",
                             description="可选：历史人物/历史事件/战争/作品/地点/法律/历史时期"),
):
    """返回该类型下可选的 subject 列表

    - 默认按 content_type（挽联/祭文/怀古诗/梗文）返回精选库主题
    - 设置 entity_type 后追加知识图谱相关类型主题（精选库优先，其余按 KG 实体名排序）
    """
    items = list_subjects(content_type, type_filter=type_filter)
    return {
        "content_type": content_type,
        "entity_type": type_filter,
        "subjects": items,
        "kg_loaded": _kg().is_loaded,
        "kg_stats": _kg().stats if _kg().is_loaded else None,
    }


@router.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, request: Request):
    t0 = time.time()

    # 限流
    rl = GENERATE_LIMITER.check(_client_key(request))
    if not rl["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "请求过于频繁，请稍后再试。",
                "remaining": rl["remaining"],
                "retryAfterSeconds": rl["retryAfterSeconds"],
            },
        )

    # 注入检测
    if is_prompt_injection(req.subject):
        raise HTTPException(status_code=400, detail=prompt_injection_block_message("subject"))

    # 缓存命中直接返回（5 分钟内同请求）
    cache_k = _cache_key(req)
    cached = _cache_get(cache_k)
    if cached:
        elapsed = int((time.time() - t0) * 1000)
        return GenerateResponse(
            id=cached["id"],
            content_type=cached["content_type"],
            subject=cached["subject"],
            title=cached["title"],
            body=cached["body"],
            horizontal=cached.get("horizontal", ""),
            tags=cached.get("tags", []),
            sources=cached.get("sources", []),
            note=cached.get("note", ""),
            elapsed_ms=elapsed,
            created_at=cached["created_at"],
        )

    ctx = get_context_for_subject(req.subject)
    prompt_params = {
        "relation": req.relation,
        "occasion": req.occasion,
        "poem_type": req.poem_type,
        "person": req.person,
        "length": req.length,
        "author_role": req.author_role,
        "tone": req.tone,
        "length_meme": req.meme_length,
    }
    prompt = build_prompt(req.content_type, ctx, req.subject, **prompt_params)

    try:
        # JSON 实际 ~200 tokens，给 1024 足够
        raw = await client.chat(prompt, temperature=0.85, max_tokens=_CHAT_MAX_TOKENS)
    except Exception as e:
        # e 可能是 RuntimeError（如 API Key 未配置），信息已经完整；其他异常加前缀
        msg = str(e)
        if "API Key 未配置" in msg or "API key" in msg.lower():
            # 业务异常，前端可识别并触发引导
            raise HTTPException(status_code=503, detail={"error": "api_key_missing", "message": msg})
        raise HTTPException(status_code=502, detail=f"LLM 调用失败：{msg}")

    # 输出质量校验
    if looks_like_hijacked_output(req.subject, raw):
        raise HTTPException(status_code=400, detail=incomplete_error_message("hijack"))
    reason = assess_generated_text(raw, min_length=20)
    if reason:
        raise HTTPException(status_code=502, detail=incomplete_error_message(reason))

    parsed = parse_json_or_text(raw)
    record = {
        "content_type": req.content_type,
        "subject": req.subject,
        "title": parsed.get("title", f"{req.subject}·生成结果"),
        "body": _format_body(parsed, req.content_type, raw),
        "horizontal": parsed.get("horizontal", ""),
        "tags": parsed.get("tags", []),
        "sources": parsed.get("sources", [f"知识库:{req.subject}"]),
        "note": parsed.get("note", ""),
    }
    elapsed = int((time.time() - t0) * 1000)
    record["elapsed_ms"] = elapsed
    saved = storage.save_history(record)
    # 写入缓存（key 已存在则覆盖 TTL）
    _cache_set(cache_k, saved)

    return GenerateResponse(
        id=saved["id"],
        content_type=saved["content_type"],
        subject=saved["subject"],
        title=saved["title"],
        body=saved["body"],
        horizontal=saved.get("horizontal", ""),
        tags=saved.get("tags", []),
        sources=saved.get("sources", []),
        note=saved.get("note", ""),
        elapsed_ms=elapsed,
        created_at=saved["created_at"],
    )


@router.post("/api/generate/stream")
async def generate_stream(req: GenerateRequest, request: Request):
    """SSE 流式输出"""
    # 限流
    rl = GENERATE_LIMITER.check(_client_key(request))
    if not rl["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={"error": "请求过于频繁，请稍后再试。", "retryAfterSeconds": rl["retryAfterSeconds"]},
        )

    if is_prompt_injection(req.subject):
        raise HTTPException(status_code=400, detail=prompt_injection_block_message("subject"))

    # 缓存命中：流式也直接发 done 事件（前端体验是瞬间返回）
    cache_k = _cache_key(req)
    cached = _cache_get(cache_k)

    ctx = get_context_for_subject(req.subject)
    prompt_params = {
        "relation": req.relation,
        "occasion": req.occasion,
        "poem_type": req.poem_type,
        "person": req.person,
        "length": req.length,
        "author_role": req.author_role,
        "tone": req.tone,
        "length_meme": req.meme_length,
    }
    prompt = build_prompt(req.content_type, ctx, req.subject, **prompt_params)

    async def event_gen():
        try:
            if cached:
                # 直接 yield done（不调用 LLM）
                yield f"data: {json.dumps({'done': True, 'id': cached['id'], 'title': cached['title'], 'body': cached['body'], 'tags': cached.get('tags', []), 'sources': cached.get('sources', []), 'cached': True}, ensure_ascii=False)}\n\n"
                return
            buffer = []
            used_fallback = False
            try:
                # JSON 实际 ~200 tokens，给 768 既能容纳又减少排队 TTFT
                async for chunk in client.stream_chat(prompt, temperature=0.85, max_tokens=_STREAM_MAX_TOKENS):
                    buffer.append(chunk)
                    yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
                full_text = "".join(buffer)
                # Fallback: 如果流式返回内容过少（被截断或排队超时），自动降级到非流式 chat()
                if len(full_text) < 50:
                    full_text = await client.chat(prompt, temperature=0.85, max_tokens=_CHAT_MAX_TOKENS)
                    used_fallback = True
                    yield f"data: {json.dumps({'delta': full_text}, ensure_ascii=False)}\n\n"
                if looks_like_hijacked_output(req.subject, full_text):
                    yield f"data: {json.dumps({'error': incomplete_error_message('hijack')}, ensure_ascii=False)}\n\n"
                    return
                reason = assess_generated_text(full_text, min_length=20)
                if reason:
                    yield f"data: {json.dumps({'error': incomplete_error_message(reason)}, ensure_ascii=False)}\n\n"
                    return
                parsed = parse_json_or_text(full_text)
                record = {
                    "content_type": req.content_type,
                    "subject": req.subject,
                    "title": parsed.get("title", f"{req.subject}·生成结果"),
                    "body": _format_body(parsed, req.content_type, full_text),
                    "horizontal": parsed.get("horizontal", ""),
                    "tags": parsed.get("tags", []),
                    "sources": parsed.get("sources", [f"知识库:{req.subject}"]),
                    "note": parsed.get("note", ""),
                }
                saved = storage.save_history(record)
                _cache_set(cache_k, saved)
                yield f"data: {json.dumps({'done': True, 'id': saved['id'], 'title': saved['title'], 'body': saved['body'], 'tags': saved.get('tags', []), 'sources': saved.get('sources', [])}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            pass  # 占位：前端已通过 SSE error/done 自行清理进度条

    return StreamingResponse(event_gen(), media_type="text/event-stream")