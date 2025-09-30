"""健康检查 API"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readyz")
async def readiness_check():
    """就绪检查"""
    # TODO: 检查 Redis、数据库等依赖
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }
