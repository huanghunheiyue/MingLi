"""
安全模块 - 借鉴 zhouli-translator 的 prompt-security 设计
- 注入检测
- 输出质量检测
"""
from __future__ import annotations
import re

# ---- 注入检测 ----
def normalized(value: str) -> str:
    """NFKC 标准化 + 去零宽字符 + 小写"""
    return (
        value.replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", "")
        .lower()
    )


_INJECTION_PROTECTED = (
    r"(系统|开发者|内部|隐藏|初始|原始|此前|之前|上面|前面)"
    r".{0,12}(提示词|指令|规则|消息|设定)"
    r"|system\s*(prompt|message)|developer\s*(prompt|message)"
    r"|previous\s*instructions?|hidden\s*prompt"
)
_INJECTION_OVERRIDE = (
    r"(忽略|无视|忘记|遗忘|覆盖|绕过|放弃|不要接受|不再遵守|解除|取消)"
    r".{0,18}(提示词|指令|规则|设定|要求|限制)"
    r"|ignore\s+(all\s+)?(previous|prior|above|system)"
    r"|forget\s+(all\s+)?(previous|prior|system)"
    r"|disregard\s+(all\s+)?(previous|prior|above|system)"
)
_INJECTION_EXTRACT = (
    r"(告诉|显示|输出|打印|复述|重复|泄露|透露|展示|发给|给出)"
    r".{0,18}(系统|开发者|内部|隐藏|初始|原始).{0,8}(提示词|指令|规则|消息)"
    r"|你的.{0,10}(系统提示词|system\s*prompt)"
    r"|reveal.{0,16}(system|developer|hidden)\s*(prompt|message|instructions?)"
)
_INJECTION_ROLE = (
    r"(你现在是|从现在起你是|扮演|假装|改成|切换成|以.{0,12}身份|请以.{0,16}身份)"
    r".{0,24}(ai|gpt|助手|模型|chatgpt|claude|deepseek|专家|身份)"
    r"|act\s+as|pretend\s+to\s+be|you\s+are\s+now\s+a"
)


def is_prompt_injection(value: str) -> bool:
    """检测输入是否包含注入尝试

    任一强信号（extract/override）+ 任一辅助信号（mentions/role）即视为注入；
    extract/override 单独出现也视为注入；
    role 必须配合 mentions 或指向具体 AI 名（chatgpt/claude/ai/gpt）才算注入。
    """
    text = normalized(value)
    mentions = bool(re.search(_INJECTION_PROTECTED, text))
    override = bool(re.search(_INJECTION_OVERRIDE, text))
    extract = bool(re.search(_INJECTION_EXTRACT, text))
    role = bool(re.search(_INJECTION_ROLE, text))
    # role + 具体 AI 名命中即算
    role_to_ai = bool(re.search(
        r"(你现在是|从现在起你是|假装|扮演|改成|切换成|以.{0,12}身份)"
        r".{0,24}(chatgpt|claude|gpt|deepseek|grok)",
        text,
    ))
    role_to_ai_zh = bool(re.search(
        r"(你现在是|从现在起你是|假装|扮演|改成|切换成|以.{0,12}身份)"
        r".{0,18}(ai\b|人工智能|语言模型|智能助手)",
        text,
    ))
    return (
        extract
        or override
        or (role and mentions)
        or role_to_ai
        or role_to_ai_zh
    )


def prompt_injection_block_message(subject: str = "") -> str:
    """被注入检测拦截时的礼貌回复"""
    if subject:
        return (
            f"抱歉，「{subject}」相关请求中包含疑似提示词注入的指令。"
            "明礼只做明代历史文化科普，不会执行越权指令。"
        )
    return (
        "抱歉，请求中包含疑似提示词注入的指令。"
        "明礼只做明代历史文化科普，不会执行越权指令。"
    )


# ---- 输出质量检测 ----
def looks_like_hijacked_output(source: str, result: str) -> bool:
    """检测输出是否被劫持（如暴露内部信息、宣称忽略指令等）"""
    out = normalized(result)
    reveals = bool(re.search(
        r"(系统|开发者|内部|隐藏).{0,10}(提示词|指令|规则)(如下|是|为|包括)"
        r"|system\s*prompt\s*(is|:)|developer\s*message\s*(is|:)", out
    ))
    claims_override = bool(re.search(
        r"(已|已经|现在).{0,8}(忽略|忘记|绕过|解除).{0,16}(提示词|指令|规则|限制)"
        r"|i\s+(have\s+)?ignored\s+(the\s+)?(previous|system)", out
    ))
    claims_identity = bool(re.search(
        r"(?:^|[。！？!?\n])\s*(?:我|本助手|本模型)(?:是|由).{0,24}"
        r"(deepseek|chatgpt|claude|人工智能|ai|语言模型)", out
    ))
    source_already = bool(re.search(
        r"(?:^|[。！？!?\n])\s*我(?:是|由).{0,24}(deepseek|chatgpt|claude|人工智能|ai|语言模型)",
        normalized(source),
    ))
    return reveals or claims_override or (claims_identity and not source_already)


def assess_generated_text(text: str, min_length: int) -> str | None:
    """评估生成文本质量，返回失败原因或 None
    
    Args:
        text: 生成文本
        min_length: 最小可接受长度
    """
    if not text or not text.strip():
        return "empty"
    stripped = text.strip()
    if len(stripped) < min_length:
        return "too_short"
    # 截断 / 工具调用失败标识
    truncated_markers = [
        "[truncated",
        "<truncated",
        "……（未完）",
        "未完待续",
    ]
    for marker in truncated_markers:
        if marker in stripped.lower() or marker in stripped:
            return "truncated"
    return None


def incomplete_error_message(reason: str | None) -> str:
    if reason == "empty":
        return "生成结果为空，请稍后再试。"
    if reason == "too_short":
        return "生成结果过短，请稍后再试。"
    if reason == "truncated":
        return "生成结果不完整，请稍后再试。"
    if reason == "hijack":
        return "输出含有疑似提示词回显，已拦截。"
    return "生成失败，请稍后再试。"