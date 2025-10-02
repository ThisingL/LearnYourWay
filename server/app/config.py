"""应用配置管理"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        protected_namespaces=('settings_',),  # 修复 model_ 命名空间冲突
    )

    # 应用基础配置
    app_name: str = "LearnYourWay"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # LLM 配置
    llm_provider: Literal["openai", "anthropic", "google", "qwen", "siliconflow"] = "siliconflow"
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"
    llm_base_url: str = "https://api.siliconflow.cn/v1"  # LLM API 基础地址
    embedding_model: str = "text-embedding-3-large"
    max_tokens: int = 8000  # LLM 最大输出 token 数

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    qwen_api_key: str = ""

    # 队列与存储
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # 数据库（支持两种命名方式）
    database_url: str = "postgresql://dev:dev@localhost:5432/learnyourway_dev"
    db_url: str | None = None  # 兼容别名

    # 向量数据库
    vector_db: Literal["pgvector", "qdrant"] = "pgvector"
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    
    def model_post_init(self, __context):
        """初始化后处理"""
        # 如果提供了 db_url，使用它覆盖 database_url
        if self.db_url:
            self.database_url = self.db_url

    # 其他
    model_serve_mode: Literal["api", "local"] = "api"
    rate_limit_rps: int = 1
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # 文件存储
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB

    @property
    def cors_origins(self) -> list[str]:
        """解析 CORS 允许的源"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
