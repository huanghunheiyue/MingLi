"""
Prompts 包
按照 zhouli-translator 架构拆分：
- base: 系统提示词 + 安全准则
- couplet: 挽联
- poem: 怀古诗
- elegiac: 祭文
- meme: 梗文（增强）
"""
from .base import SYSTEM_BASE, SAFETY_GUIDELINES, COMMON_JSON_HINT
from .couplet import build_couplet_prompt
from .poem import build_poem_prompt
from .elegiac import build_elegiac_prompt
from .meme import (
    build_meme_prompt,
    build_crossover_prompt,
    MEME_TONES,
    MEME_LENGTHS,
    CROSSOVER_TONES,
    CROSSOVER_LENGTHS,
)
from .router import build_prompt

__all__ = [
    "SYSTEM_BASE",
    "SAFETY_GUIDELINES",
    "COMMON_JSON_HINT",
    "build_couplet_prompt",
    "build_poem_prompt",
    "build_elegiac_prompt",
    "build_meme_prompt",
    "build_crossover_prompt",
    "MEME_TONES",
    "MEME_LENGTHS",
    "CROSSOVER_TONES",
    "CROSSOVER_LENGTHS",
    "build_prompt",
]