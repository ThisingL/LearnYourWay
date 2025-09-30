"""PDF 摄取 API"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.api_models import IngestResponse, SuccessResponse, TaskResponse

router = APIRouter()


@router.post("/pdf", response_model=SuccessResponse[IngestResponse])
async def upload_pdf(file: UploadFile = File(...)):
    """上传 PDF 文件"""
    # 验证文件类型
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    # TODO: 保存文件并创建 Celery 任务
    task_id = f"task_{file.filename}_{hash(file.filename)}"
    
    return SuccessResponse(
        data=IngestResponse(
            task_id=task_id,
            filename=file.filename,
            status="pending",
        ),
        message="文件上传成功，开始解析",
    )


@router.get("/tasks/{task_id}", response_model=SuccessResponse[TaskResponse])
async def get_task_status(task_id: str):
    """查询任务状态"""
    # TODO: 从 Celery 获取真实状态
    return SuccessResponse(
        data=TaskResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            stage="queued",
        )
    )
