"""
统一 LLM 客户端
支持 DeepSeek / 通义千问 / 豆包 / MiniMax 等（OpenAI 兼容协议）
支持普通调用 + 流式输出
针对 reasoning 模型（如 MiniMax-M3）自动剥离 <think>...</think> 块
"""
import json
import re
from typing import AsyncIterator, Optional
import httpx

from .config import settings
from .prompts import SYSTEM_BASE


# 匹配 reasoning 模型的思考块（包含常见变体）
_THINK_BLOCK = re.compile(
    r"<\s*think(?:ing)?\s*>.*?<\s*/\s*think(?:ing)?\s*>",
    re.DOTALL | re.IGNORECASE,
)
# HTML 实体转义的变体（如 &lt;think&gt;）
_THINK_BLOCK_ESCAPED = re.compile(
    r"&lt;\s*think(?:ing)?\s*&gt;.*?&lt;\s*/\s*think(?:ing)?\s*&gt;",
    re.DOTALL | re.IGNORECASE,
)


# 匹配 think 起始标签位置
_THINK_OPEN = re.compile(
    r"<\s*think(?:ing)?\s*>",
    re.IGNORECASE,
)
_THINK_OPEN_ESCAPED = re.compile(
    r"&lt;\s*think(?:ing)?\s*&gt;",
    re.IGNORECASE,
)
# 匹配 think 闭合标签位置
_THINK_CLOSE = re.compile(
    r"<\s*/\s*think(?:ing)?\s*>",
    re.IGNORECASE,
)
_THINK_CLOSE_ESCAPED = re.compile(
    r"&lt;\s*/\s*think(?:ing)?\s*&gt;",
    re.IGNORECASE,
)


def _strip_thinking(text: str) -> str:
    """剥离 reasoning 模型输出里的 <think>...</think> 块。

    策略：
      1. 优先按完整闭合对剥离（循环处理嵌套）。
      2. 如果仍残留 think 起始/闭合标签（max_tokens 截断导致未闭合），
         采用保守策略：保留剩余文本，让上游 JSON 解析补救。
    """
    if not text:
        return text
    # 1. 完整闭合对循环剥（处理嵌套）
    prev = None
    while prev != text:
        prev = text
        text = _THINK_BLOCK.sub("", text)
        text = _THINK_BLOCK_ESCAPED.sub("", text)
    # 2. 检查是否仍有孤立的 think 标签
    has_open = _THINK_OPEN.search(text) or _THINK_OPEN_ESCAPED.search(text)
    has_close = _THINK_CLOSE.search(text) or _THINK_CLOSE_ESCAPED.search(text)
    if has_open and not has_close:
        # 未闭合：保守保留（让上游 parse_json_or_text 用 regex 抽 JSON 子串）
        return text.strip()
    if has_close and not has_open:
        # 孤立闭合：剥掉
        text = _START_TO_CLOSE_FALLBACK.sub("", text)
        text = _START_TO_CLOSE_FALLBACK_ESCAPED.sub("", text)
    return text.strip()


_START_TO_CLOSE_FALLBACK = re.compile(
    r"^.*?<\s*/\s*think(?:ing)?\s*>",
    re.DOTALL | re.IGNORECASE,
)
_START_TO_CLOSE_FALLBACK_ESCAPED = re.compile(
    r"^.*?&lt;\s*/\s*think(?:ing)?\s*&gt;",
    re.DOTALL | re.IGNORECASE,
)


class LLMClient:
    def __init__(self):
        self.cfg = settings.get_provider_config()
        self.provider = settings.LLM_PROVIDER
        self.timeout = settings.LLM_TIMEOUT
        self.max_retries = settings.LLM_MAX_RETRIES

    def _headers(self) -> dict:
        api_key = (self.cfg.get("api_key") or "").strip()
        # 检测常见占位符（空 / 未替换的模板）
        placeholders = ("", "sk-your-", "your-", "sk-cp-your", "placeholder", "xxx", "XXXX")
        is_placeholder = (
            not api_key
            or any(api_key.startswith(p) for p in placeholders if p)
            or "your-" in api_key.lower()
            or "key-here" in api_key.lower()
            or api_key.endswith("-key-here")
        )
        if is_placeholder:
            provider = self.cfg.get("model") or self.provider
            raise RuntimeError(
                f"❌ API Key 未配置：当前使用 LLM_PROVIDER={self.provider}（模型 {provider}），"
                f"但 {self.provider.upper()}_API_KEY 为空或仍是模板占位符。\n"
                f"👉 修复方法：\n"
                f"   1. 在项目根目录创建 .env 文件（可复制 .env.example）\n"
                f"   2. 找到 {self.provider.upper()}_API_KEY= 这一行，把后面替换成你的真实密钥\n"
                f"   3. 保存后重启 MingLi.exe\n"
                f"📌 申请密钥：\n"
                f"   - DeepSeek（推荐·便宜）: https://platform.deepseek.com/\n"
                f"   - 通义千问: https://bailian.console.aliyun.com/\n"
                f"   - 豆包: https://www.volcengine.com/product/doubao\n"
                f"   - MiniMax: https://platform.minimaxi.com/user-center/payment/token-plan"
            )
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat(self, user_prompt: str, *, temperature: float = 0.8,
                   max_tokens: int = 1500, system_prompt: str = "") -> str:
        """普通调用，返回完整文本

        system_prompt 为空时使用全局 SYSTEM_BASE；否则用调用方传入的。
        """
        sys_prompt = system_prompt or SYSTEM_BASE
        url = f"{self.cfg['base_url'].rstrip('/')}/chat/completions"
        payload = {
            "model": self.cfg["model"],
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, headers=self._headers(), json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    msg = data["choices"][0]["message"]
                    content = msg.get("content") or ""
                    # 兼容 reasoning 模型：实际正文可能放在 reasoning_content 字段
                    if not content.strip() and msg.get("reasoning_content"):
                        content = msg["reasoning_content"]
                    return _strip_thinking(content)
            except RuntimeError:
                # 业务异常（如 API Key 未配置）直接抛，不重试
                raise
            except Exception as e:
                last_err = e
        raise RuntimeError(f"LLM 调用失败：{last_err}")

    async def stream_chat(self, user_prompt: str, *, temperature: float = 0.8,
                          max_tokens: int = 1500, system_prompt: str = "") -> AsyncIterator[str]:
        """流式调用，逐 token 产出"""
        sys_prompt = system_prompt or SYSTEM_BASE
        url = f"{self.cfg['base_url'].rstrip('/')}/chat/completions"
        payload = {
            "model": self.cfg["model"],
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, headers=self._headers(), json=payload) as resp:
                resp.raise_for_status()
                # 流式处理：维护一个 buffer，遇到完整 <think>...</think> 块就跳过
                buffer = ""
                in_think = False
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        obj = json.loads(chunk)
                        delta = obj["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if not content:
                            continue
                        buffer += content
                        # 检测是否还在 <think> 块内
                        if not in_think:
                            low = buffer.lower()
                            idx_open = low.find("<think")
                            if idx_open == -1:
                                idx_open = low.find("&lt;think")
                            if idx_open != -1:
                                # 进入 think 块，先把之前的纯内容吐出去
                                pre = buffer[:idx_open]
                                buffer = buffer[idx_open:]
                                in_think = True
                                if pre:
                                    yield _strip_thinking(pre)
                        if in_think:
                            low = buffer.lower()
                            idx_close = low.find("</think>")
                            if idx_close == -1:
                                idx_close = low.find("&lt;/think&gt;")
                            if idx_close != -1:
                                # 找到闭合，丢弃 think 块
                                end = idx_close + (len("</think>") if "</think>" in low[idx_close:idx_close+20] else len("&lt;/think&gt;"))
                                buffer = buffer[end:]
                                in_think = False
                            else:
                                # 还在 think 块内，继续累积
                                continue
                        if buffer:
                            yield buffer
                            buffer = ""
                    except Exception:
                        continue


def parse_json_or_text(text: str) -> dict:
    """尝试从 LLM 输出中解析 JSON；失败则降级为纯文本"""
    # 去除 markdown 代码块
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # 寻找 JSON 子串
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # 降级
    return {
        "title": "（生成结果）",
        "body": text,
        "tags": [],
        "sources": [],
        "note": "未能解析为结构化 JSON，已以纯文本形式返回。",
    }


# 全局单例
client = LLMClient()


async def generate_text(
    user_prompt: str,
    system_prompt: str = "",
    *,
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> str:
    """简洁入口：传入 prompt，返回 LLM 文本
    
    如果 system_prompt 为空，则使用全局 SYSTEM_BASE
    """
    from .prompts import SYSTEM_BASE
    sys_prompt = system_prompt or SYSTEM_BASE
    return await client.chat(user_prompt, temperature=temperature, max_tokens=max_tokens, system_prompt=sys_prompt)


async def generate_text_stream(
    user_prompt: str,
    system_prompt: str = "",
    *,
    temperature: float = 0.7,
    max_tokens: int = 800,
):
    """流式版本"""
    from .prompts import SYSTEM_BASE
    sys_prompt = system_prompt or SYSTEM_BASE
    # 用一个临时 client 走自定义 system prompt
    import httpx, json
    cfg = client.cfg
    url = f"{cfg['base_url'].rstrip('/')}/chat/completions"
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=client.timeout) as c:
        async with c.stream("POST", url, headers=client._headers(), json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj = json.loads(chunk)
                    content = obj["choices"][0].get("delta", {}).get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue