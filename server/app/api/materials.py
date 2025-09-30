"""学习素材生成 API"""

from fastapi import APIRouter

from app.models.api_models import (
    ImmersiveResponse,
    MaterialRequest,
    MindMapResponse,
    QuizResponse,
    SuccessResponse,
)

router = APIRouter()


@router.post("/quiz", response_model=SuccessResponse[QuizResponse])
async def generate_quiz(request: MaterialRequest):
    """生成测验题"""
    # TODO: 调用生成服务
    return SuccessResponse(
        data=QuizResponse(questions=[]),
        message="测验生成成功",
    )


@router.post("/mindmap", response_model=SuccessResponse[MindMapResponse])
async def generate_mindmap(request: MaterialRequest):
    """生成思维导图"""
    # TODO: 调用生成服务
    return SuccessResponse(
        data=MindMapResponse(nodes=[], edges=[]),
        message="思维导图生成成功",
    )


@router.post("/immersive", response_model=SuccessResponse[ImmersiveResponse])
async def generate_immersive(request: MaterialRequest):
    """生成沉浸式文本"""
    # TODO: 调用生成服务
    return SuccessResponse(
        data=ImmersiveResponse(sections=[]),
        message="沉浸式文本生成成功",
    )
