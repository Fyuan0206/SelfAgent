"""
配置管理
支持从config.yaml和环境变量加载配置
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class ServerConfig(BaseSettings):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    log_level: str = "INFO"


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = "sqlite+aiosqlite:///./data/dbt_skills.db"
    echo: bool = False


class LLMConfig(BaseSettings):
    """LLM配置"""
    base_url: str = "https://api.openai.com/v1"
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30


class RecommendationConfig(BaseSettings):
    """推荐引擎配置"""
    max_skills_per_recommendation: int = 2
    min_match_score: float = 0.3
    enable_llm_fallback: bool = True
    enable_llm_reason: bool = True


class CacheConfig(BaseSettings):
    """缓存配置"""
    enabled: bool = False
    ttl: int = 3600


class Settings(BaseSettings):
    """主配置类"""
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    recommendation: RecommendationConfig = RecommendationConfig()
    cache: CacheConfig = CacheConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def load_yaml_config(config_path: Optional[str] = None) -> dict:
    """从YAML文件加载配置"""
    if config_path is None:
        # 默认查找config.yaml
        base_dir = Path(__file__).parent.parent.parent
        config_path = base_dir / "config.yaml"

    config_path = Path(config_path)
    if not config_path.exists():
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # 处理环境变量替换
    def replace_env_vars(obj):
        if isinstance(obj, str):
            if obj.startswith("${") and obj.endswith("}"):
                env_var = obj[2:-1]
                return os.getenv(env_var, "")
            return obj
        elif isinstance(obj, dict):
            return {k: replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env_vars(item) for item in obj]
        return obj

    return replace_env_vars(config)


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    yaml_config = load_yaml_config()

    # 从YAML配置创建Settings对象
    settings = Settings()

    if "server" in yaml_config:
        settings.server = ServerConfig(**yaml_config["server"])
    if "database" in yaml_config:
        settings.database = DatabaseConfig(**yaml_config["database"])
    if "llm" in yaml_config:
        # 优先使用环境变量中的API key
        llm_config = yaml_config["llm"].copy()
        env_api_key = os.getenv("OPENAI_API_KEY", "")
        if env_api_key:
            llm_config["api_key"] = env_api_key
        settings.llm = LLMConfig(**llm_config)
    if "recommendation" in yaml_config:
        settings.recommendation = RecommendationConfig(**yaml_config["recommendation"])
    if "cache" in yaml_config:
        settings.cache = CacheConfig(**yaml_config["cache"])

    return settings


# ============== 测试用例 ==============
if __name__ == "__main__":
    def test_config():
        """测试配置加载"""
        # 测试1: 加载默认配置
        settings = get_settings()
        print(f"服务器配置: {settings.server.host}:{settings.server.port}")
        print(f"数据库URL: {settings.database.url}")
        print(f"LLM模型: {settings.llm.model}")
        print("✓ 测试1通过: 配置加载成功")

        # 测试2: 检查默认值
        assert settings.recommendation.max_skills_per_recommendation == 2
        assert settings.recommendation.min_match_score == 0.3
        print("✓ 测试2通过: 默认值正确")

        # 测试3: YAML配置加载
        yaml_config = load_yaml_config()
        if yaml_config:
            print(f"✓ 测试3通过: YAML配置加载成功，包含 {list(yaml_config.keys())} 配置项")
        else:
            print("✓ 测试3通过: 未找到YAML配置文件，使用默认值")

        print("\n所有配置测试通过！")

    # 清除缓存以便测试
    get_settings.cache_clear()
    test_config()
