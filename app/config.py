"""
应用配置模块
从 .env 读取所有配置项，支持 阿里云百炼 / MiniMax / DeepSeek / 通义千问 / 豆包 五家切换
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env (位于项目根目录)
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    """统一配置"""

    # LLM 提供商选择
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "aliyun_bailian").lower()

    # DeepSeek
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # 通义千问
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen-plus")

    # 豆包
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")
    DOUBAO_BASE_URL: str = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    DOUBAO_MODEL: str = os.getenv("DOUBAO_MODEL", "doubao-pro-32k")

    # 阿里云百炼 token-plan (OpenAI 兼容端点)
    # 订阅 Key 用量查询: https://bailian.console.aliyun.com/
    # 注意：此端点只能用 token-plan 订阅 Key，不能用普通 API Key
    ALIYUN_BAILIAN_API_KEY: str = os.getenv("ALIYUN_BAILIAN_API_KEY", "")
    ALIYUN_BAILIAN_BASE_URL: str = os.getenv(
        "ALIYUN_BAILIAN_BASE_URL",
        "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    )
    ALIYUN_BAILIAN_MODEL: str = os.getenv("ALIYUN_BAILIAN_MODEL", "qwen3.8-flash")

    # MiniMax (Token Plan 订阅 Key 必须用国内端点 api.minimaxi.com)
    # ⚠️ 国际端点 api.minimax.io 不能用 Token Plan Key（会返回 401）
    # OpenAI 兼容路径: POST {base_url}/chat/completions
    # 订阅 Key 用量查询: https://www.minimaxi.com/v1/token_plan/remains
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_BASE_URL: str = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
    MINIMAX_MODEL: str = os.getenv("MINIMAX_MODEL", "MiniMax-M3")

    # 通用
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # 数据目录
    DATA_DIR: Path = ROOT_DIR / "data"
    HISTORY_FILE: Path = DATA_DIR / "history.json"
    FEEDBACK_FILE: Path = DATA_DIR / "feedback.json"

    # 静态目录（默认走 ROOT_DIR/static；EXE 模式下支持磁盘覆盖）
    STATIC_DIR: Path = ROOT_DIR / "static"
    # PyInstaller onefile 模式：若 EXE 同级有 static/ 且包含 index.html，
    # 自动改用磁盘版（覆盖打包进 EXE 的版本），便于静态资源热更新无需重新打包
    if getattr(sys, "frozen", False):
        _disk_static = Path(sys.executable).resolve().parent / "static"
        if _disk_static.is_dir() and (_disk_static / "index.html").exists():
            STATIC_DIR = _disk_static

    def get_provider_config(self) -> dict:
        """根据当前选择返回对应 provider 的连接参数"""
        if self.LLM_PROVIDER == "deepseek":
            return {
                "api_key": self.DEEPSEEK_API_KEY,
                "base_url": self.DEEPSEEK_BASE_URL,
                "model": self.DEEPSEEK_MODEL,
            }
        elif self.LLM_PROVIDER == "qwen":
            return {
                "api_key": self.QWEN_API_KEY,
                "base_url": self.QWEN_BASE_URL,
                "model": self.QWEN_MODEL,
            }
        elif self.LLM_PROVIDER == "doubao":
            return {
                "api_key": self.DOUBAO_API_KEY,
                "base_url": self.DOUBAO_BASE_URL,
                "model": self.DOUBAO_MODEL,
            }
        elif self.LLM_PROVIDER == "minimax":
            return {
                "api_key": self.MINIMAX_API_KEY,
                "base_url": self.MINIMAX_BASE_URL,
                "model": self.MINIMAX_MODEL,
            }
        elif self.LLM_PROVIDER == "aliyun_bailian":
            return {
                "api_key": self.ALIYUN_BAILIAN_API_KEY,
                "base_url": self.ALIYUN_BAILIAN_BASE_URL,
                "model": self.ALIYUN_BAILIAN_MODEL,
            }
        else:
            raise ValueError(
                f"未知的 LLM_PROVIDER: {self.LLM_PROVIDER}"
                "（可选: aliyun_bailian / minimax / deepseek / qwen / doubao）"
            )


settings = Settings()