"""
FastAPI 主入口
"""
import os
import sys
import io
from contextlib import asynccontextmanager

# Windows GBK 终端输出修复
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .models import HealthResponse
from .routers import generate, history, feedback
from .routers.meme import router as meme_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动钩子
    print(f"[明礼 MingLi] 启动 | LLM Provider: {settings.LLM_PROVIDER} | Model: {settings.get_provider_config()['model']}")
    yield


app = FastAPI(
    title="明礼 MingLi · 明代历史文化科普智能体",
    version="1.0.0",
    description="第十届全国高校易班技术创新大会 · 智能体应用类参赛作品",
    lifespan=lifespan,
)

# CORS（开发期开放）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


@app.get("/")
async def index():
    """首页"""
    index_file = settings.STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"msg": "明礼 MingLi is running. Place index.html under static/."}


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version=app.version,
        provider=f"{settings.LLM_PROVIDER} / {settings.get_provider_config()['model']}",
    )


# 注册路由
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(meme_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
    )