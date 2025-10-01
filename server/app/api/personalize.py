"""个性化 API"""

from fastapi import APIRouter, HTTPException

from app.models.api_models import (
    PersonalizeRequest,
    PersonalizeResponse,
    SuccessResponse,
    TaskResponse,
)

router = APIRouter()


@router.post("", response_model=SuccessResponse[PersonalizeResponse])
async def personalize_content(request: PersonalizeRequest):
    """
    创建个性化改写任务
    
    Args:
        request: 包含 chunk_id, profile_id, original_text
        
    Returns:
        任务 ID 和状态
    """
    from app.api.profiles import profiles_db
    from app.tasks.personalize import personalize_text_task
    
    # 验证用户画像是否存在
    if request.profile_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # 创建 Celery 任务
    task = personalize_text_task.apply_async(
        args=[request.chunk_id, request.profile_id, request.original_text],
        task_id=f"personalize_{request.chunk_id}_{request.profile_id}",
    )
    
    return SuccessResponse(
        data=PersonalizeResponse(task_id=task.id, status="pending"),
        message="个性化任务已创建",
    )


@router.get("/tasks/{task_id}", response_model=SuccessResponse[TaskResponse])
async def get_personalize_task(task_id: str):
    """
    查询个性化任务状态
    
    Args:
        task_id: 任务 ID
        
    Returns:
        任务状态和结果
    """
    from celery.result import AsyncResult
    from app.tasks.worker import celery_app
    
    task = AsyncResult(task_id, app=celery_app)
    
    # 映射 Celery 状态到我们的状态
    status_mapping = {
        "PENDING": "pending",
        "STARTED": "started",
        "RETRY": "retry",
        "SUCCESS": "success",
        "FAILURE": "failure",
    }
    
    status = status_mapping.get(task.state, "pending")
    
    # 获取进度信息
    meta = task.info if isinstance(task.info, dict) else {}
    progress = meta.get("progress", 0)
    stage = meta.get("stage")
    error = meta.get("error") if status == "failure" else None
    
    # 获取结果
    result = None
    if status == "success":
        result = task.result
    
    return SuccessResponse(
        data=TaskResponse(
            task_id=task_id,
            status=status,
            progress=progress,
            stage=stage,
            result=result,
            error=error,
        )
    )
