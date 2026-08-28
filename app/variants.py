"""
A/B 实验变体 - 借鉴 zhouli-translator 的 prompt-variants 设计
"""
from __future__ import annotations

VARIANTS = ("A", "B")


def select_variant(ab_enabled: bool, b_percent: int, bucket: int | None = None) -> str:
    """根据桶位选择变体
    
    Args:
        ab_enabled: 是否启用 A/B
        b_percent: 变体 B 的流量占比 (0-100)
        bucket: 桶位 (0-99)，None 则随机
    """
    if not ab_enabled or b_percent <= 0:
        return "A"
    if b_percent >= 100:
        return "B"
    if bucket is None:
        import random
        bucket = random.randint(0, 99)
    return "B" if bucket < b_percent else "A"


def get_prompt_version(variant: str, version_a: str = "v1.0.0", version_b: str = "v1.1.0") -> str:
    return version_b if variant == "B" else version_a