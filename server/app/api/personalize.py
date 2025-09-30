"""个性化 API"""

from fastapi import APIRouter

from app.models.api_models import PersonalizeRequest, PersonalizeResponse, SuccessResponse

router = APIRouter()


@router.post("", response_model=SuccessResponse[PersonalizeResponse])
async def personalize_content(request: PersonalizeRequest):
    """个性化改写内容"""
    # TODO: 创建个性化任务
    task_id = f"personalize_{request.chunk_id}_{request.profile_id}"
    
    return SuccessResponse(
        data=PersonalizeResponse(task_id=task_id, status="pending"),
        message="个性化任务已创建",
    )
