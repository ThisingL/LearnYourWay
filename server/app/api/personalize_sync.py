"""个性化 API - 同步版本（不需要 Redis/Celery）

用于开发测试，直接调用服务，无需异步任务队列
"""

from fastapi import APIRouter, HTTPException

from app.models.api_models import PersonalizeRequest, SuccessResponse
from app.api.profiles import profiles_db

router = APIRouter()


@router.post("/sync", response_model=SuccessResponse)
async def personalize_content_sync(request: PersonalizeRequest):
    """
    同步个性化改写（无需 Redis/Celery）
    
    直接调用服务并返回结果，适合开发测试
    
    Args:
        request: 包含 chunk_id, profile_id, original_text
        
    Returns:
        直接返回改写结果
    """
    # 验证用户画像是否存在
    if request.profile_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    profile = profiles_db[request.profile_id]
    grade = profile["grade"]
    interests = profile["interests"]
    
    # 直接调用服务（同步）
    from app.services.readability_service import get_readability_service
    from app.services.personalize_service import get_personalize_service
    from app.services.evaluation_service import get_evaluation_service
    
    # 1. 分析原文可读性
    readability_service = get_readability_service()
    original_readability = readability_service.analyze_readability(
        request.original_text, grade
    )
    
    # 2. 个性化改写
    personalize_service = get_personalize_service()
    result = await personalize_service.personalize_text(
        original_text=request.original_text,
        grade=grade,
        interests=interests,
        must_keep_terms=request.must_keep_terms,
    )
    
    # 3. 评测改写质量
    evaluation_service = get_evaluation_service()
    evaluation = await evaluation_service.evaluate_personalization(
        original_text=request.original_text,
        personalized_text=result["personalized_text"],
        grade=grade,
        interests=interests,
    )
    
    # 返回完整结果
    return SuccessResponse(
        data={
            "chunk_id": request.chunk_id,
            "profile_id": request.profile_id,
            "personalized_text": result["personalized_text"],
            "original_readability": result["original_readability"],
            "personalized_readability": result["personalized_readability"],
            "improvement": result["improvement"],
            "evaluation": evaluation,
        },
        message="个性化改写完成",
    )


@router.post("/analyze", response_model=SuccessResponse)
async def analyze_text_readability(
    text: str,
    target_grade: int = 5,
):
    """
    分析文本可读性（无需 Redis/Celery）
    
    快速测试可读性评估功能
    
    Args:
        text: 待分析文本
        target_grade: 目标年级 (1-12)
        
    Returns:
        可读性分析结果
    """
    from app.services.readability_service import get_readability_service
    
    readability_service = get_readability_service()
    analysis = readability_service.analyze_readability(text, target_grade)
    
    return SuccessResponse(
        data=analysis,
        message="可读性分析完成",
    )

