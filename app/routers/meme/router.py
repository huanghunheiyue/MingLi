"""
梗文路由 - 专门处理「一键生成悼明梗文」
参照 zhouli-translator app/api/translate 的路由结构设计

端点：
  POST /api/meme/quick     一键生成（随机抽取梗元素）
  POST /api/meme/custom    自定义生成
  POST /api/meme/crossover 悼明之作·跨界梗（用户输入文化作品 → 强行嫁接明朝史）
  GET  /api/meme/elements  查看所有梗元素
  GET  /api/meme/categories 查看梗元素分类
"""
from __future__ import annotations
import random
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.meme_data import MEMES, list_memes, random_meme, list_meme_categories
from app.knowledge_base import get_context_for_subject, FIGURES, EVENTS
from app.llm_client import generate_text
from app.prompts import (
    build_meme_prompt,
    build_crossover_prompt,
    MEME_TONES,
    MEME_LENGTHS,
    CROSSOVER_TONES,
    CROSSOVER_LENGTHS,
)
from app.security import is_prompt_injection, prompt_injection_block_message
from app.rate_limit import MEME_QUICK_LIMITER

router = APIRouter(prefix="/api/meme", tags=["meme"])


class QuickMemeRequest(BaseModel):
    """一键生成请求"""
    subject: str | None = Field(None, description="可选：指定人物/事件；空则随机")
    tone: str | None = Field(None, description="可选：致敬/惋惜/反思/戏谑/咏史")
    length: str | None = Field(None, description="可选：短/中/长")
    category: str | None = Field(None, description="可选：按梗分类筛选")
    hint: str = Field("", description="可选：补充说明")


class CustomMemeRequest(BaseModel):
    """自定义生成请求"""
    subject: str
    tone: str = "致敬"
    length: str = "中"
    meme_text: str
    meme_source: str = ""
    meme_category: str = ""
    hint: str = ""


class CrossoverMemeRequest(BaseModel):
    """悼明之作·跨界梗请求
    把和明朝毫无关系的文化作品强行嫁接到明代历史，一本正经胡扯。
    """
    work_name: str = Field(..., min_length=1, max_length=80,
                           description="文化作品名称（如《进击的巨人》《原神》《让子弹飞》）")
    work_desc: str = Field("", max_length=400,
                           description="作品中的元素/角色/道具/台词描述")
    subject: str = Field("", max_length=40,
                         description="可选：希望强行联系的明代人物/事件；空则随机")
    tone: str = Field("考据", description="考据/奏疏/圣谕/县志")
    length: str = Field("中", description="短/中/长")
    hint: str = Field("", description="可选：补充说明")


def _client_key(request: Request) -> str:
    """获取客户端标识"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.client.host if request.client else "anon")


@router.post("/quick")
async def quick_meme(req: QuickMemeRequest, request: Request):
    """一键生成悼明梗文 - 真正一键"""
    # 限流
    rl = MEME_QUICK_LIMITER.check(_client_key(request))
    if not rl["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "请求过于频繁，请稍后再试。",
                "remaining": rl["remaining"],
                "retryAfterSeconds": rl["retryAfterSeconds"],
            },
        )

    # 注入检测（subject 和 hint 都查）
    for field, val in [("subject", req.subject or ""), ("hint", req.hint)]:
        if is_prompt_injection(val):
            raise HTTPException(
                status_code=400,
                detail=prompt_injection_block_message(field),
            )

    # 1. 随机选梗
    meme = random_meme(category=req.category, mood=req.tone)
    if meme is None:
        # 无匹配则取任意一个
        meme = random_meme()

    # 2. 选风格
    tone = req.tone if req.tone in MEME_TONES else meme["mood"]

    # 3. 选长度（按风格给出合理默认）
    length = req.length if req.length in MEME_LENGTHS else "短" if tone == "戏谑" else "中"

    # 4. 选主体（subject 留空则用梗元素自己的出处）
    subject = (req.subject or meme["source"]).strip()
    if not subject:
        subject = "明代"

    # 5. 取知识上下文
    context = get_context_for_subject(subject, max_chars=600)

    # 6. 构建 Prompt
    user_prompt = build_meme_prompt(
        context=context,
        subject=subject,
        tone=tone,
        length=length,
        meme_text=meme["text"],
        meme_source=meme["source"],
        meme_category=meme["category"],
        hint=req.hint,
    )

    # 7. 生成
    try:
        result = await generate_text(
            user_prompt=user_prompt,
            system_prompt="你是明礼 MingLi，明代历史文化科普智能体，克制、典雅、有温度。",
            temperature=0.9 if tone in ("戏谑", "咏史") else 0.7,
            # reasoning 模型需要足够 token 生成 think + JSON，统一给到 4000
            max_tokens=4000,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败：{e}")

    return {
        "type": "meme",
        "mode": "quick",
        "tone": tone,
        "length": length,
        "subject": subject,
        "meme": {
            "text": meme["text"],
            "source": meme["source"],
            "category": meme["category"],
        },
        "result": result,
        "rateLimit": {
            "remaining": rl["remaining"],
            "dailyRemaining": rl["dailyRemaining"],
        },
    }


@router.post("/custom")
async def custom_meme(req: CustomMemeRequest, request: Request):
    """自定义梗文生成"""
    rl = MEME_QUICK_LIMITER.check(_client_key(request))
    if not rl["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={"error": "请求过于频繁，请稍后再试。", "retryAfterSeconds": rl["retryAfterSeconds"]},
        )

    if is_prompt_injection(req.subject) or is_prompt_injection(req.hint):
        raise HTTPException(status_code=400, detail=prompt_injection_block_message())

    tone = req.tone if req.tone in MEME_TONES else "致敬"
    length = req.length if req.length in MEME_LENGTHS else "中"

    context = get_context_for_subject(req.subject, max_chars=800)

    user_prompt = build_meme_prompt(
        context=context,
        subject=req.subject,
        tone=tone,
        length=length,
        meme_text=req.meme_text,
        meme_source=req.meme_source,
        meme_category=req.meme_category,
        hint=req.hint,
    )

    try:
        result = await generate_text(
            user_prompt=user_prompt,
            system_prompt="你是明礼 MingLi，明代历史文化科普智能体。",
            temperature=0.8 if tone == "戏谑" else 0.65,
            # reasoning 模型需要足够 token 生成 think + JSON，统一给到 4000
            max_tokens=4000,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败：{e}")

    return {
        "type": "meme",
        "mode": "custom",
        "tone": tone,
        "length": length,
        "subject": req.subject,
        "result": result,
    }


@router.get("/elements")
async def list_elements(category: str | None = None, mood: str | None = None):
    """列出所有可用梗元素"""
    return {
        "total": len(MEMES),
        "items": list_memes(category=category, mood=mood),
    }


@router.get("/categories")
async def categories():
    """列出所有分类"""
    return {
        "categories": list_meme_categories(),
        "tones": list(MEME_TONES.keys()),
        "lengths": list(MEME_LENGTHS.keys()),
    }


# ============================================================
# 悼明之作·跨界梗（CROSSOVER）
# ============================================================

@router.post("/crossover")
async def crossover_meme(req: CrossoverMemeRequest, request: Request):
    """悼明之作·跨界梗生成

    把用户填写的文化作品中的元素，强行嫁接到明代历史，
    以"明清史官考据"口吻一本正经地胡扯。
    """
    # 1. 限流
    rl = MEME_QUICK_LIMITER.check(_client_key(request))
    if not rl["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "请求过于频繁，请稍后再试。",
                "remaining": rl["remaining"],
                "retryAfterSeconds": rl["retryAfterSeconds"],
            },
        )

    # 2. 注入检测（所有用户输入字段都查）
    for field, val in [
        ("work_name", req.work_name),
        ("work_desc", req.work_desc),
        ("subject", req.subject),
        ("hint", req.hint),
    ]:
        if is_prompt_injection(val):
            raise HTTPException(
                status_code=400,
                detail=prompt_injection_block_message(field),
            )

    # 3. 文体 + 长度归一化
    tone = req.tone if req.tone in CROSSOVER_TONES else "考据"
    length = req.length if req.length in CROSSOVER_LENGTHS else "中"

    # 4. 选主体：subject 留空 → 从知识库随机抽 1 个人物 + 1 个事件，作为"考据"的两个挂钩点
    subject = req.subject.strip()
    if not subject:
        # 随机抽一个人物 + 一个事件拼成 "人物 + 事件" 形式，作为强行联系对象
        random_figure = random.choice(list(FIGURES.keys()))
        random_event = random.choice(list(EVENTS.keys()))
        subject = f"{random_figure} / {random_event}"

    # 5. 取知识上下文（人物 + 事件各取一份拼起来，论据池更丰富）
    fig_name = subject.split(" / ")[0].strip()
    evt_name = subject.split(" / ")[-1].strip()
    ctx_parts = []
    if fig_name in FIGURES:
        ctx_parts.append(get_context_for_subject(fig_name, max_chars=400))
    if evt_name in EVENTS and evt_name != fig_name:
        ctx_parts.append(get_context_for_subject(evt_name, max_chars=400))
    context = "\n\n".join(ctx_parts) if ctx_parts else ""

    # 6. 构建 Prompt
    user_prompt = build_crossover_prompt(
        work_name=req.work_name.strip(),
        work_desc=req.work_desc.strip(),
        subject=subject,
        tone=tone,
        length=length,
        context=context,
        hint=req.hint.strip(),
    )

    # 7. 调用 LLM（跨界梗允许更高温度，激发荒诞）
    try:
        result = await generate_text(
            user_prompt=user_prompt,
            system_prompt=(
                "你是明礼 MingLi，明代历史文化科普智能体。"
                "你专精'悼明之作·跨界梗'：以明清史官考据之笔，"
                "将现代/外国/架空文化作品元素强行论证为明代真实历史遗产。"
                "表面越严肃越好笑，绝不承认是胡扯。"
            ),
            temperature=1.0 if tone in ("考据", "县志") else 0.95,
            # reasoning 模型需要足够 token 生成 think + JSON；统一给到 4000
            max_tokens=4000,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败：{e}")

    return {
        "type": "meme",
        "mode": "crossover",
        "tone": tone,
        "length": length,
        "work_name": req.work_name.strip(),
        "work_desc": req.work_desc.strip(),
        "subject": subject,
        "result": result,
        "rateLimit": {
            "remaining": rl["remaining"],
            "dailyRemaining": rl["dailyRemaining"],
        },
    }