"""FastAPI 应用入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api import health, ingest, materials, personalize, profiles
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 LLM Provider: {settings.llm_provider}")
    print(f"🔧 Debug Mode: {settings.debug}")
    
    yield
    
    # 关闭时
    print(f"👋 Shutting down {settings.app_name}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="个性化学习内容生成平台 API",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, tags=["健康检查"])
app.include_router(profiles.router, prefix="/profiles", tags=["用户画像"])
app.include_router(ingest.router, prefix="/ingest", tags=["PDF摄取"])
app.include_router(personalize.router, prefix="/personalize", tags=["个性化"])
app.include_router(materials.router, prefix="/materials", tags=["学习素材"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs",
    }
