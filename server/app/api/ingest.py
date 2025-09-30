"""PDF 摄取 API

完整实现 PDF 上传、解析、分块、向量化的异步流程
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.models.api_models import IngestResponse, SuccessResponse, TaskResponse
from app.tasks.ingest_pdf import ingest_pdf_task

router = APIRouter()
settings = get_settings()

# 确保上传目录存在
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/pdf", response_model=SuccessResponse[IngestResponse])
async def upload_pdf(file: UploadFile = File(...)):
    """
    上传 PDF 文件并启动解析任务
    
    - **file**: PDF 文件（multipart/form-data）
    - 返回任务ID，用于后续查询进度
    """
    # 验证文件类型
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持 PDF 文件")
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持 {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    saved_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / saved_filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 创建 Celery 任务（如果 Redis 不可用，直接同步处理）
    try:
        # 设置较短的超时时间检测 Redis 是否可用
        from celery.exceptions import OperationalError
        import redis
        
        # 快速检测 Redis 连接
        try:
            r = redis.from_url(settings.redis_url, socket_connect_timeout=1)
            r.ping()
            redis_available = True
        except:
            redis_available = False
        
        if redis_available:
            # Redis 可用，使用 Celery 异步处理
            task = ingest_pdf_task.delay(str(file_path))
            task_id = task.id
            message = f"文件上传成功，异步处理中（任务ID: {task_id}）"
        else:
            # Redis 不可用，同步处理（演示模式）
            print("⚠️  Redis 不可用，使用同步模式处理（演示）")
            from app.services.pdf_parser import PDFParser
            
            parser = PDFParser()
            result = parser.parse_pdf(file_path)
            
            # 生成演示用的任务 ID
            task_id = f"sync_{file_id}"
            message = f"文件上传成功，同步处理完成（演示模式，任务ID: {task_id}）"
            
            # 将结果临时存储（用于后续查询）
            # TODO: 使用更持久的存储
            if not hasattr(upload_pdf, '_sync_results'):
                upload_pdf._sync_results = {}
            upload_pdf._sync_results[task_id] = {
                "status": "success",
                "filename": result["filename"],
                "total_pages": result["total_pages"],
                "message": "同步处理完成（演示模式）"
            }
        
    except Exception as e:
        # 如果任务创建失败，删除已上传的文件
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
    
    return SuccessResponse(
        data=IngestResponse(
            task_id=task_id,
            filename=file.filename,
            status="pending",
        ),
        message=message,
    )


@router.get("/tasks/{task_id}", response_model=SuccessResponse[TaskResponse])
async def get_task_status(task_id: str):
    """
    查询 PDF 解析任务状态
    
    - **task_id**: 任务ID（上传时返回）
    - 返回任务进度、状态和结果
    """
    # 检查是否是同步模式的任务
    if task_id.startswith("sync_"):
        if hasattr(upload_pdf, '_sync_results') and task_id in upload_pdf._sync_results:
            sync_result = upload_pdf._sync_results[task_id]
            return SuccessResponse(
                data=TaskResponse(
                    task_id=task_id,
                    status="success",
                    progress=100,
                    stage="completed",
                    result=sync_result,
                )
            )
        else:
            raise HTTPException(status_code=404, detail="任务不存在")
    
    # Celery 异步任务
    from celery.result import AsyncResult
    
    try:
        result = AsyncResult(task_id)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="任务队列服务不可用"
        )
    
    # 构造响应
    if result.state == "PENDING":
        response_data = TaskResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            stage="queued",
        )
    elif result.state == "STARTED":
        # 从任务 meta 获取进度信息
        meta = result.info or {}
        response_data = TaskResponse(
            task_id=task_id,
            status="started",
            progress=meta.get("progress", 10),
            stage=meta.get("stage", "processing"),
        )
    elif result.state == "SUCCESS":
        response_data = TaskResponse(
            task_id=task_id,
            status="success",
            progress=100,
            stage="completed",
            result=result.result,
        )
    elif result.state == "FAILURE":
        response_data = TaskResponse(
            task_id=task_id,
            status="failure",
            progress=0,
            stage="failed",
            error=str(result.info),
        )
    elif result.state == "RETRY":
        meta = result.info or {}
        response_data = TaskResponse(
            task_id=task_id,
            status="retry",
            progress=meta.get("progress", 50),
            stage="retrying",
        )
    else:
        response_data = TaskResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            stage=result.state.lower(),
        )
    
    return SuccessResponse(data=response_data)