"""
文案生成路由
- POST /api/generate        非流式
- POST /api/generate/stream 流式 (SSE)
- GET  /api/subjects?type=eulogy
"""
import json
import time
import asyncio
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
        # reasoning 模型需要足够 token 生成 think + JSON，max_tokens 给到 8000
        raw = await client.chat(prompt, temperature=0.85, max_tokens=8000)
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
        "body": parsed.get("body", raw),
        "horizontal": parsed.get("horizontal", ""),
        "tags": parsed.get("tags", []),
        "sources": parsed.get("sources", [f"知识库:{req.subject}"]),
        "note": parsed.get("note", ""),
    }
    elapsed = int((time.time() - t0) * 1000)
    record["elapsed_ms"] = elapsed
    saved = storage.save_history(record)

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
        buffer = []
        used_fallback = False
        try:
            # reasoning 模型需要足够 token 生成 think + JSON，max_tokens 给到 16000
            async for chunk in client.stream_chat(prompt, temperature=0.85, max_tokens=16000):
                buffer.append(chunk)
                yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
            full_text = "".join(buffer)
            # Fallback: 如果流式返回内容过少（thinking 占满 tokens），自动降级到非流式 chat()
            if len(full_text) < 50:
                full_text = await client.chat(prompt, temperature=0.85, max_tokens=8000)
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
                "body": parsed.get("body", full_text),
                "horizontal": parsed.get("horizontal", ""),
                "tags": parsed.get("tags", []),
                "sources": parsed.get("sources", [f"知识库:{req.subject}"]),
                "note": parsed.get("note", ""),
            }
            saved = storage.save_history(record)
            yield f"data: {json.dumps({'done': True, 'id': saved['id'], 'title': saved['title'], 'tags': saved.get('tags', []), 'sources': saved.get('sources', [])}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")