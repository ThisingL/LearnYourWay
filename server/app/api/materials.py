"""学习素材生成 API"""

from fastapi import APIRouter, HTTPException

from app.api.profiles import profiles_db
from app.models.api_models import (
    ImmersiveResponse,
    MaterialRequest,
    MindMapResponse,
    QuizRequest,
    QuizResponse,
    SuccessResponse,
)
from app.services.material_generator import (
    get_immersive_generator,
    get_mindmap_generator,
    get_quiz_generator,
)

router = APIRouter()


@router.post("/quiz", response_model=SuccessResponse[QuizResponse])
async def generate_quiz(request: QuizRequest):
    """
    生成测验题
    
    根据用户画像和学习内容生成个性化测验题，包括：
    - 单选题 (single)
    - 多选题 (multi)
    - 判断题 (tf)
    - 简答题 (short)
    
    Args:
        request: 包含 chunk_id, profile_id, content, count
        
    Returns:
        测验题列表
    """
    # 验证用户画像是否存在
    if request.profile_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    profile = profiles_db[request.profile_id]
    
    # 调用生成服务
    generator = get_quiz_generator()
    result = await generator.generate(
        content=request.content,
        profile=profile,
        count=request.count,
    )
    
    # 验证结果
    if not generator.validate(result):
        raise HTTPException(status_code=500, detail="生成的测验题格式不正确")
    
    return SuccessResponse(
        data=QuizResponse(questions=result["questions"]),
        message=f"成功生成 {len(result['questions'])} 道测验题",
    )


@router.post("/mindmap", response_model=SuccessResponse[MindMapResponse])
async def generate_mindmap(request: MaterialRequest):
    """
    生成思维导图
    
    将学习内容转化为结构化的思维导图，包含：
    - 节点：核心概念、子概念、示例
    - 边：概念之间的关系
    
    Args:
        request: 包含 chunk_id, profile_id, content
        
    Returns:
        思维导图的节点和边数据
    """
    # 验证用户画像是否存在
    if request.profile_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    profile = profiles_db[request.profile_id]
    
    # 调用生成服务
    generator = get_mindmap_generator()
    result = await generator.generate(
        content=request.content,
        profile=profile,
    )
    
    # 验证结果
    if not generator.validate(result):
        raise HTTPException(status_code=500, detail="生成的思维导图格式不正确")
    
    return SuccessResponse(
        data=MindMapResponse(
            nodes=result["nodes"],
            edges=result["edges"],
        ),
        message=f"成功生成思维导图（{len(result['nodes'])} 个节点，{len(result['edges'])} 条连接）",
    )


@router.post("/immersive", response_model=SuccessResponse[ImmersiveResponse])
async def generate_immersive(request: MaterialRequest):
    """
    生成沉浸式文本
    
    将学习内容改写为引人入胜的故事化表达，特点：
    - 生动有趣的叙述方式
    - 融入学生兴趣的场景和例子
    - 包含插图占位符
    - 分章节组织
    
    Args:
        request: 包含 chunk_id, profile_id, content
        
    Returns:
        沉浸式文本的章节数据
    """
    # 验证用户画像是否存在
    if request.profile_id not in profiles_db:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    profile = profiles_db[request.profile_id]
    
    # 调用生成服务
    generator = get_immersive_generator()
    result = await generator.generate(
        content=request.content,
        profile=profile,
    )
    
    # 验证结果
    if not generator.validate(result):
        raise HTTPException(status_code=500, detail="生成的沉浸式文本格式不正确")
    
    return SuccessResponse(
        data=ImmersiveResponse(sections=result["sections"]),
        message=f"成功生成沉浸式文本（{len(result['sections'])} 个章节）",
    )
