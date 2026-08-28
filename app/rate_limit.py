"""
限流模块 - 借鉴 zhouli-translator 的 RATE_WINDOW 设计
基于全局 dict 实现简单 IP 滑动窗口限流
"""
from __future__ import annotations
import time

# 默认配置
DEFAULT_WINDOW_MS = 10 * 60 * 1000       # 10 分钟窗口
DEFAULT_WINDOW_LIMIT = 30                # 窗口内最多 30 次
DEFAULT_DAY_LIMIT = 200                  # 每天最多 200 次


class RateLimiter:
    """简单内存限流器（生产环境建议替换为 Redis）"""

    def __init__(self, window_ms: int = DEFAULT_WINDOW_MS,
                 window_limit: int = DEFAULT_WINDOW_LIMIT,
                 day_limit: int = DEFAULT_DAY_LIMIT) -> None:
        self.window_ms = window_ms
        self.window_limit = window_limit
        self.day_limit = day_limit
        self._store: dict[str, dict] = {}

    def _now(self) -> int:
        return int(time.time() * 1000)

    def _today(self) -> str:
        return time.strftime("%Y-%m-%d")

    def check(self, key: str) -> dict:
        """检查是否允许请求，返回详情"""
        now = self._now()
        today = self._today()
        rec = self._store.get(key)
        if not rec:
            rec = {"windowStartedAt": now, "count": 0, "day": today, "dayCount": 0}
            self._store[key] = rec

        # 窗口过期
        if now - rec["windowStartedAt"] >= self.window_ms:
            rec["windowStartedAt"] = now
            rec["count"] = 0

        # 日期变更
        if rec["day"] != today:
            rec["day"] = today
            rec["dayCount"] = 0

        rec["count"] += 1
        rec["dayCount"] += 1

        window_remaining = max(0, self.window_limit - rec["count"])
        daily_remaining = max(0, self.day_limit - rec["dayCount"])

        if rec["count"] > self.window_limit:
            return {
                "allowed": False,
                "reason": "window",
                "remaining": 0,
                "windowRemaining": 0,
                "dailyRemaining": daily_remaining,
                "retryAfterSeconds": max(1, int((self.window_ms - (now - rec["windowStartedAt"])) / 1000)),
            }
        if rec["dayCount"] > self.day_limit:
            return {
                "allowed": False,
                "reason": "day",
                "remaining": window_remaining,
                "windowRemaining": window_remaining,
                "dailyRemaining": 0,
                "retryAfterSeconds": 60,
            }
        return {
            "allowed": True,
            "reason": None,
            "remaining": window_remaining,
            "windowRemaining": window_remaining,
            "dailyRemaining": daily_remaining,
            "retryAfterSeconds": 0,
        }


# 全局单例
GENERATE_LIMITER = RateLimiter()
MEME_QUICK_LIMITER = RateLimiter(window_ms=60 * 1000, window_limit=10, day_limit=100)
INTERACTION_LIMITER = RateLimiter(window_ms=60 * 1000, window_limit=20, day_limit=200)