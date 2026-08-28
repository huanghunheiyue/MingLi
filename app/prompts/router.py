"""
Prompt 路由：按文案类型分发
"""
from .couplet import build_couplet_prompt
from .poem import build_poem_prompt
from .elegiac import build_elegiac_prompt
from .meme import build_meme_prompt


def build_prompt(content_type: str, context: str, subject: str, **kwargs) -> str:
    """
    统一入口，根据 content_type 选择对应 prompt 构造器
    
    Args:
        content_type: couplet / poem / elegiac_prose / meme
        context: 知识上下文
        subject: 主体
        **kwargs: 各类型所需参数
            - couplet: relation, occasion
            - poem: poem_type, person
            - elegiac_prose: length, author_role
            - meme: tone, length, meme_text, meme_source, meme_category, hint
    """
    if content_type == "couplet":
        return build_couplet_prompt(
            context=context,
            subject=subject,
            relation=kwargs.get("relation", "后人"),
            occasion=kwargs.get("occasion", "纪念日"),
        )
    if content_type == "poem":
        return build_poem_prompt(
            context=context,
            subject=subject,
            poem_type=kwargs.get("poem_type", "七律"),
            person=kwargs.get("person", ""),
        )
    if content_type == "elegiac_prose":
        return build_elegiac_prompt(
            context=context,
            subject=subject,
            length=kwargs.get("length", 500),
            author_role=kwargs.get("author_role", "后人"),
        )
    if content_type == "meme":
        return build_meme_prompt(
            context=context,
            subject=subject,
            tone=kwargs.get("tone", "致敬"),
            length=kwargs.get("length", "中"),
            meme_text=kwargs.get("meme_text", ""),
            meme_source=kwargs.get("meme_source", ""),
            meme_category=kwargs.get("meme_category", ""),
            hint=kwargs.get("hint", ""),
        )
    raise ValueError(f"不支持的文案类型: {content_type}")