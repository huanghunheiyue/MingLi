"""
配置中心路由
- GET  /api/settings       获取当前所有提供商配置（API Key 脱敏）
- POST /api/settings       保存配置到 .env + 热更新到内存
- POST /api/settings/test  测试连接（不保存）
"""
from __future__ import annotations

import re
import os
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..config import settings, ROOT_DIR


router = APIRouter(prefix="/api/settings", tags=["settings"])


# ============================================================
# 预设提供商列表
# ============================================================
PRESET_PROVIDERS = [
    {
        "id": "minimax",
        "name": "MiniMax (MiniMax)",
        "default_base_url": "https://api.minimaxi.com/v1",
        "default_model": "MiniMax-M3",
        "models": ["MiniMax-M3", "MiniMax-M2", "MiniMax-M2.7-highspeed", "abab6.5s-chat", "MiniMax-Text-01"],
        "note": "国内端点，需使用 Token Plan 订阅 Key",
        "docs": "https://platform.minimaxi.com",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "default_base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner", "deepseek-coder"],
        "note": "性价比之王，reasoner 模式带深度思考",
        "docs": "https://platform.deepseek.com",
    },
    {
        "id": "qwen",
        "name": "阿里云 DashScope (通义千问)",
        "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen-coder-plus", "qwen-long", "qwen3-max-preview"],
        "note": "兼容 OpenAI 协议，需要先在阿里云开通模型",
        "docs": "https://dashscope.console.aliyun.com",
    },
    {
        "id": "doubao",
        "name": "豆包 (火山引擎)",
        "default_base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "doubao-pro-32k",
        "models": ["doubao-pro-32k", "doubao-lite-32k", "doubao-pro-256k"],
        "note": "需先在火山引擎控制台开通推理接入点",
        "docs": "https://www.volcengine.com/product/doubao",
    },
    {
        "id": "openai",
        "name": "OpenAI 官方",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini", "o3-mini"],
        "note": "需海外网络环境",
        "docs": "https://platform.openai.com",
    },
    {
        "id": "moonshot",
        "name": "Moonshot AI (Kimi)",
        "default_base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "note": "长上下文专家，最高支持 128K",
        "docs": "https://platform.moonshot.cn",
    },
    {
        "id": "zhipu",
        "name": "智谱 AI (GLM)",
        "default_base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "models": ["glm-4-plus", "glm-4-air", "glm-4-flash", "glm-4-long"],
        "note": "glm-4-flash 免费，glm-4-plus 能力强",
        "docs": "https://open.bigmodel.cn",
    },
    {
        "id": "siliconflow",
        "name": "硅基流动 (SiliconFlow)",
        "default_base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-72B-Instruct",
        "models": [
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "deepseek-ai/DeepSeek-V2.5",
            "THUDM/glm-4-9b-chat",
        ],
        "note": "聚合多种开源模型，注册送额度",
        "docs": "https://cloud.siliconflow.cn",
    },
    {
        "id": "ollama",
        "name": "Ollama (本地)",
        "default_base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5:7b",
        "models": ["qwen2.5:7b", "llama3.1:8b", "gemma2:9b", "mistral:7b", "deepseek-r1:7b"],
        "note": "本地运行完全免费，API Key 留空即可（任意非空字符串）",
        "docs": "https://ollama.com",
    },
    {
        "id": "custom",
        "name": "自定义 (OpenAI 兼容)",
        "default_base_url": "",
        "default_model": "",
        "models": [],
        "note": "任何 OpenAI 兼容协议的 API（OneAPI/NewAPI/FastGPT/OpenRouter 等）",
        "docs": "",
    },
]


# ============================================================
# 工具函数
# ============================================================
_PLACEHOLDER_RE = re.compile(r"(your-|key-here|placeholder|^sk-cp-your|-key$)", re.I)


def _is_placeholder(key: str) -> bool:
    """检测 API Key 是否仍是模板占位符"""
    if not key:
        return True
    if len(key) < 8:
        return True
    return bool(_PLACEHOLDER_RE.search(key))


def _mask_key(key: str) -> str:
    """脱敏 API Key：保留前 6 后 4，中间用 *** 替换"""
    if not key:
        return ""
    if len(key) <= 10:
        return "*" * len(key)
    return key[:6] + "***" + key[-4:]


def _read_env_value(content: str, key: str, default: str = "") -> str:
    """从 .env 文本中读取指定 key 的值（处理引号包裹）；fallback 到 os.environ"""
    pattern = re.compile(rf'^{re.escape(key)}\s*=\s*"?([^"\n]*)"?', re.M)
    m = pattern.search(content)
    if m:
        val = m.group(1).strip()
        if val:
            return val
    # Fallback: 从环境变量读（PyInstaller onefile 模式下 launcher 已 setdefault 注入）
    env_val = os.environ.get(key, "")
    return env_val if env_val else default


def _update_env_var(content: str, key: str, value: str) -> str:
    """更新 .env 文件中的某个变量（不存在则追加）"""
    needs_quote = any(c in value for c in [" ", "#", "=", '"'])
    value_quoted = f'"{value}"' if needs_quote else value

    pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.M)
    new_line = f"{key}={value_quoted}"

    if pattern.search(content):
        return pattern.sub(new_line, content)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        return content + new_line + "\n"


# ============================================================
# GET /api/settings
# ============================================================
def _resolve_user_env_path() -> Path:
    """返回用户可见的 .env 路径（EXE 旁 / 项目根），而不是 PyInstaller _MEIPASS"""
    import sys
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / ".env"
    return ROOT_DIR / ".env"


@router.get("")
async def get_settings():
    """获取当前所有提供商配置（API Key 脱敏）"""
    # EXE 模式下，ROOT_DIR 指向 _MEIPASS，读取那里的 .env 是无效的。
    # 改读 launcher 已 setdefault 到 os.environ 的真实值，并显示 EXE 旁的 .env 路径。
    user_env_path = _resolve_user_env_path()
    content = user_env_path.read_text(encoding="utf-8") if user_env_path.exists() else ""

    providers = []
    for p in PRESET_PROVIDERS:
        pid = p["id"]
        env_prefix = pid.upper()
        api_key = _read_env_value(content, f"{env_prefix}_API_KEY", "")
        base_url = _read_env_value(content, f"{env_prefix}_BASE_URL", p["default_base_url"])
        model = _read_env_value(content, f"{env_prefix}_MODEL", p["default_model"])

        providers.append({
            **p,
            "api_key_masked": _mask_key(api_key),
            "api_key_set": bool(api_key and not _is_placeholder(api_key)),
            "api_key_full": api_key if (pid == settings.LLM_PROVIDER) else "",
            "base_url": base_url,
            "model": model,
        })

    active_provider_data = next((p for p in providers if p["id"] == settings.LLM_PROVIDER), None)
    active_set = bool(active_provider_data and active_provider_data["api_key_set"])

    return {
        "active_provider": settings.LLM_PROVIDER,
        "active_provider_name": active_provider_data["name"] if active_provider_data else settings.LLM_PROVIDER,
        "active_api_key_set": active_set,
        "providers": providers,
        "env_path": str(user_env_path),
        "current_model": settings.get_provider_config().get("model", ""),
    }


# ============================================================
# POST /api/settings
# ============================================================
class ProviderConfig(BaseModel):
    provider_id: str = Field(..., description="提供商 ID")
    api_key: Optional[str] = Field(None, description="API Key；None 表示不更新")
    base_url: Optional[str] = Field(None, description="Base URL；None 表示不更新")
    model: Optional[str] = Field(None, description="模型名；None 表示不更新")


class SaveRequest(BaseModel):
    llm_provider: Optional[str] = Field(None, description="要激活的提供商 ID")
    providers: list[ProviderConfig] = Field(default_factory=list)


@router.post("")
async def save_settings(req: SaveRequest):
    """保存配置到 .env，并热更新到内存"""
    env_path = _resolve_user_env_path()
    content = env_path.read_text(encoding="utf-8") if env_path.exists() else ""

    saved_fields = []

    if req.llm_provider:
        valid_ids = {p["id"] for p in PRESET_PROVIDERS}
        if req.llm_provider not in valid_ids:
            return {"ok": False, "message": f"未知的 provider_id: {req.llm_provider}"}
        content = _update_env_var(content, "LLM_PROVIDER", req.llm_provider)
        saved_fields.append("LLM_PROVIDER")

    for pc in req.providers:
        env_prefix = pc.provider_id.upper()
        if pc.api_key is not None and pc.api_key != "":
            content = _update_env_var(content, f"{env_prefix}_API_KEY", pc.api_key)
            saved_fields.append(f"{env_prefix}_API_KEY")
        if pc.base_url is not None and pc.base_url != "":
            content = _update_env_var(content, f"{env_prefix}_BASE_URL", pc.base_url)
            saved_fields.append(f"{env_prefix}_BASE_URL")
        if pc.model is not None and pc.model != "":
            content = _update_env_var(content, f"{env_prefix}_MODEL", pc.model)
            saved_fields.append(f"{env_prefix}_MODEL")

    env_path.write_text(content, encoding="utf-8")

    # 热更新 settings + LLMClient
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v
                if hasattr(settings, k):
                    setattr(settings, k, v)

        if req.llm_provider:
            settings.LLM_PROVIDER = req.llm_provider.lower()

        from ..llm_client import client
        client.cfg = settings.get_provider_config()
        client.provider = settings.LLM_PROVIDER
    except Exception as e:
        return {
            "ok": False,
            "message": f"已保存到 .env，但热更新失败（建议重启 EXE）：{e}",
            "saved_fields": saved_fields,
        }

    return {
        "ok": True,
        "message": "✅ 配置已保存，已热更新到运行中的服务",
        "saved_fields": saved_fields,
        "active_provider": settings.LLM_PROVIDER,
        "active_model": settings.get_provider_config().get("model", ""),
    }


# ============================================================
# POST /api/settings/test
# ============================================================
class TestRequest(BaseModel):
    provider_id: str
    api_key: str
    base_url: str
    model: str


@router.post("/test")
async def test_connection(req: TestRequest):
    """测试 LLM 连接（不保存配置）"""
    if req.provider_id == "ollama" and not req.api_key.strip():
        api_key = "ollama"
    else:
        api_key = req.api_key.strip()

    if not api_key:
        return {"ok": False, "message": "❌ API Key 不能为空（Ollama 除外，可填 'ollama'）"}
    if not req.base_url.strip():
        return {"ok": False, "message": "❌ Base URL 不能为空"}
    if not req.model.strip():
        return {"ok": False, "message": "❌ 模型名不能为空"}

    url = f"{req.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": req.model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
        "temperature": 0.0,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as c:
            resp = await c.post(url, headers=headers, json=payload)

        if resp.status_code == 200:
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                return {
                    "ok": True,
                    "message": f"✅ 连接成功！模型回复：{content[:50]!r}",
                    "elapsed_ms": int(resp.elapsed.total_seconds() * 1000),
                    "model_used": data.get("model", req.model),
                }
            return {
                "ok": True,
                "message": f"✅ 200 OK，但返回结构异常：{str(data)[:200]}",
            }

        try:
            err_body = resp.json()
            err_msg = err_body.get("error", {}).get("message", "") or err_body.get("message", "") or str(err_body)[:200]
        except Exception:
            err_msg = resp.text[:200]

        friendly = ""
        if resp.status_code == 401:
            friendly = "（API Key 无效或已过期）"
        elif resp.status_code == 403:
            friendly = "（权限被拒，可能是 Key 错误或该模型未开通）"
        elif resp.status_code == 404:
            friendly = "（接口地址或模型名不存在）"
        elif resp.status_code == 429:
            friendly = "（请求频率超限 / 余额耗尽）"

        return {
            "ok": False,
            "status_code": resp.status_code,
            "message": f"❌ HTTP {resp.status_code} {friendly}\n{err_msg}",
        }
    except httpx.TimeoutException:
        return {"ok": False, "message": "❌ 连接超时（>20 秒）。请检查：①网络 ②Base URL ③代理"}
    except httpx.ConnectError as e:
        return {"ok": False, "message": f"❌ 无法连接服务器：{str(e)[:200]}\n请检查 Base URL 拼写"}
    except Exception as e:
        return {"ok": False, "message": f"❌ 测试失败：{type(e).__name__}: {str(e)[:200]}"}