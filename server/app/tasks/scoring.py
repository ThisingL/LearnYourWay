"""评测任务"""

import asyncio

from app.tasks.worker import celery_app


@celery_app.task(bind=True, name="evaluate_text")
def evaluate_text_task(
    self,
    original_text: str,
    personalized_text: str,
    grade: int,
    interests: list[str],
):
    """
    评测任务
    
    Args:
        original_text: 原始文本
        personalized_text: 改写后的文本
        grade: 目标年级
        interests: 用户兴趣列表
        
    Returns:
        {
            "scores": Dict[str, float],
            "comments": Dict[str, str],
            "overall_score": float,
            "summary": str,
            "strengths": List[str],
            "weaknesses": List[str]
        }
    """
    try:
        self.update_state(
            state="STARTED",
            meta={"stage": "evaluating", "progress": 30},
        )
        
        # 调用评测服务
        from app.services.evaluation_service import get_evaluation_service
        evaluation_service = get_evaluation_service()
        
        result = asyncio.run(
            evaluation_service.evaluate_personalization(
                original_text=original_text,
                personalized_text=personalized_text,
                grade=grade,
                interests=interests,
            )
        )
        
        self.update_state(
            state="STARTED",
            meta={"stage": "calculating_score", "progress": 80},
        )
        
        # 检查质量阈值
        quality_check = evaluation_service.check_quality_threshold(
            result["scores"], threshold=3.0
        )
        
        result["quality_check"] = quality_check
        
        self.update_state(
            state="STARTED",
            meta={"stage": "completed", "progress": 100},
        )
        
        return result
        
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
