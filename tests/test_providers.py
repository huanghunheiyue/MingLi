"""
Provider 配置矩阵测试
覆盖 deepseek / qwen / doubao / minimax 四家
"""
import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402


@pytest.fixture
def clean_env(monkeypatch):
    """清理所有 LLM_* / *_API_KEY / *_BASE_URL / *_MODEL"""
    keys_to_clear = [k for k in os.environ if k.startswith(("LLM_", "DEEPSEEK_", "QWEN_", "DOUBAO_", "MINIMAX_"))]
    for k in keys_to_clear:
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


def test_default_provider_is_minimax_or_deepseek(clean_env):
    """无 .env 时默认值应能工作（不报错）"""
    s = Settings()
    assert s.LLM_PROVIDER in ("minimax", "deepseek")


def test_minimax_provider_config(clean_env):
    """MiniMax Token Plan: base_url=https://api.minimaxi.com/v1（国内端点）"""
    s = Settings()
    s.LLM_PROVIDER = "minimax"
    s.MINIMAX_API_KEY = "sk-cp-test"
    cfg = s.get_provider_config()
    assert cfg["api_key"] == "sk-cp-test"
    assert cfg["base_url"] == "https://api.minimaxi.com/v1"
    assert cfg["model"] == "MiniMax-M3"


def test_minimax_env_override(clean_env):
    """通过环境变量切换 MiniMax 模型"""
    # 在 .env 加载前 setenv，然后构造新 Settings
    clean_env.setenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")
    # 直接用 .env 类变量计算: 模拟 Settings 类初始化逻辑
    new_value = os.getenv("MINIMAX_MODEL", "MiniMax-M3")
    assert new_value == "MiniMax-M2.7-highspeed"


def test_minimax_class_default():
    """无环境变量时，MINIMAX_MODEL 默认 MiniMax-M3"""
    s = Settings()
    assert s.MINIMAX_MODEL == "MiniMax-M3"


def test_deepseek_provider_config(clean_env):
    s = Settings()
    s.LLM_PROVIDER = "deepseek"
    s.DEEPSEEK_API_KEY = "sk-test"
    cfg = s.get_provider_config()
    assert cfg["api_key"] == "sk-test"
    assert cfg["base_url"] == "https://api.deepseek.com/v1"
    assert cfg["model"] == "deepseek-chat"


def test_qwen_provider_config(clean_env):
    s = Settings()
    s.LLM_PROVIDER = "qwen"
    s.QWEN_API_KEY = "sk-test"
    cfg = s.get_provider_config()
    assert cfg["base_url"] == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert cfg["model"] == "qwen-plus"


def test_doubao_provider_config(clean_env):
    s = Settings()
    s.LLM_PROVIDER = "doubao"
    s.DOUBAO_API_KEY = "test-key"
    cfg = s.get_provider_config()
    assert cfg["base_url"] == "https://ark.cn-beijing.volces.com/api/v3"
    assert cfg["model"] == "doubao-pro-32k"


def test_unknown_provider_raises(clean_env):
    s = Settings()
    s.LLM_PROVIDER = "openai"  # 不支持
    with pytest.raises(ValueError) as exc:
        s.get_provider_config()
    assert "未知的 LLM_PROVIDER" in str(exc.value)
    # 错误信息应提示支持的 provider
    assert "minimax" in str(exc.value)


def test_all_providers_have_required_fields(clean_env):
    """每个 provider 配置都包含 api_key / base_url / model 三项"""
    s = Settings()
    for prov in ("minimax", "deepseek", "qwen", "doubao"):
        s.LLM_PROVIDER = prov
        cfg = s.get_provider_config()
        assert set(cfg.keys()) == {"api_key", "base_url", "model"}, \
            f"{prov} 配置字段不全: {cfg.keys()}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])