"""用户画像 API"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.models.api_models import ProfileCreate, ProfileResponse, SuccessResponse

router = APIRouter()

# 临时内存存储（后续替换为数据库）
profiles_db: Dict[str, dict] = {}


@router.post("", response_model=SuccessResponse[ProfileResponse])
async def create_profile(profile: ProfileCreate):
    """创建或更新用户画像"""
    now = datetime.utcnow().isoformat()
    
    profile_data = {
        "user_id": profile.user_id,
        "grade": profile.grade,
        "interests": profile.interests,
        "created_at": profiles_db.get(profile.user_id, {}).get("created_at", now),
        "updated_at": now,
    }
    
    profiles_db[profile.user_id] = profile_data
    
    return SuccessResponse(
        data=ProfileResponse(**profile_data),
        message="画像创建成功" if profile.user_id not in profiles_db else "画像更新成功",
    )


@router.get("/{user_id}", response_model=SuccessResponse[ProfileResponse])
async def get_profile(user_id: str):
    """获取用户画像"""
    if user_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    return SuccessResponse(data=ProfileResponse(**profiles_db[user_id]))


@router.delete("/{user_id}")
async def delete_profile(user_id: str):
    """删除用户画像"""
    if user_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    del profiles_db[user_id]
    return SuccessResponse(data={"user_id": user_id}, message="画像删除成功")
