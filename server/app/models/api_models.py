"""API 请求/响应模型"""

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============ 通用响应模型 ============


class SuccessResponse(BaseModel, Generic[T]):
    """成功响应"""

    code: int = 0
    message: str = "success"
    data: T


class ErrorResponse(BaseModel):
    """错误响应"""

    code: int
    message: str
    detail: str | None = None


class TaskResponse(BaseModel):
    """任务响应"""

    task_id: str
    status: Literal["pending", "started", "retry", "success", "failure"]
    progress: int = Field(ge=0, le=100, description="进度 0-100")
    stage: str | None = None
    result: Any | None = None
    error: str | None = None


# ============ 用户画像模型 ============


class ProfileCreate(BaseModel):
    """创建用户画像请求"""

    user_id: str = Field(..., description="用户ID")
    grade: int = Field(..., ge=1, le=12, description="年级 1-12")
    interests: list[str] = Field(..., min_length=1, max_length=10, description="兴趣列表")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "demo_user",
                    "grade": 5,
                    "interests": ["足球", "科学实验", "恐龙"],
                }
            ]
        }
    }


class ProfileResponse(BaseModel):
    """用户画像响应"""

    user_id: str
    grade: int
    interests: list[str]
    created_at: str
    updated_at: str


# ============ PDF 摄取模型 ============


class IngestResponse(BaseModel):
    """PDF 摄取响应"""

    task_id: str
    filename: str
    status: str


# ============ 个性化模型 ============


class PersonalizeRequest(BaseModel):
    """个性化请求"""

    chunk_id: str = Field(..., description="文本块ID")
    profile_id: str = Field(..., description="用户画像ID")
    original_text: str = Field(..., description="原始文本内容")
    must_keep_terms: list[str] | None = Field(None, description="必须保留的术语列表")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chunk_id": "chunk_001",
                    "profile_id": "demo_user",
                    "original_text": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖的过程...",
                    "must_keep_terms": ["光合作用", "二氧化碳", "葡萄糖"],
                }
            ]
        }
    }


class PersonalizeResponse(BaseModel):
    """个性化响应"""

    task_id: str
    status: str


# ============ 学习素材模型 ============


class MaterialRequest(BaseModel):
    """素材生成请求"""

    chunk_id: str = Field(..., description="文本块ID")
    profile_id: str = Field(..., description="用户画像ID")
    content: str = Field(..., description="学习内容")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chunk_id": "chunk_001",
                    "profile_id": "demo_user",
                    "content": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程...",
                }
            ]
        }
    }


class QuizRequest(BaseModel):
    """测验题生成请求"""

    chunk_id: str = Field(..., description="文本块ID")
    profile_id: str = Field(..., description="用户画像ID")
    content: str = Field(..., description="学习内容")
    count: int = Field(10, ge=1, le=50, description="题目数量")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chunk_id": "chunk_001",
                    "profile_id": "demo_user",
                    "content": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程...",
                    "count": 10,
                }
            ]
        }
    }


class QuizQuestion(BaseModel):
    """测验题"""

    id: str
    type: Literal["single", "multi", "tf", "short"]
    stem: str
    options: list[str] | None = None
    answer: Any
    explanation: str
    difficulty: int = Field(ge=1, le=5)


class QuizResponse(BaseModel):
    """测验响应"""

    questions: list[QuizQuestion]


class MindMapNode(BaseModel):
    """思维导图节点"""

    id: str
    label: str
    type: str = "concept"


class MindMapEdge(BaseModel):
    """思维导图边"""

    source: str
    target: str
    label: str = ""


class MindMapResponse(BaseModel):
    """思维导图响应"""

    nodes: list[MindMapNode]
    edges: list[MindMapEdge]


class ImmersiveSection(BaseModel):
    """沉浸式文本章节"""

    title: str
    paragraphs: list[str]


class ImmersiveResponse(BaseModel):
    """沉浸式文本响应"""

    sections: list[ImmersiveSection]
