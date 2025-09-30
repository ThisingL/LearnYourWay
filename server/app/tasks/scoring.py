"""评测任务"""

from app.tasks.worker import celery_app


@celery_app.task(bind=True, name="score_eval")
def score_eval_task(self, text: str, criteria: dict):
    """
    评测任务
    
    Args:
        text: 待评测文本
        criteria: 评测标准
        
    Returns:
        {
            "scores": {...},
            "feedback": "..."
        }
    """
    try:
        # TODO: 调用 LLM 进行评测
        # 评测维度：正确性、覆盖度、可读性、兴趣贴合度、长度控制
        
        return {
            "scores": {
                "correctness": 4.5,
                "coverage": 4.0,
                "readability": 4.2,
                "interest_fit": 4.3,
                "length_control": 4.5,
            },
            "feedback": "改写质量良好，建议...",
        }
    except Exception as e:
        self.update_state(state="FAILURE", meta={"error": str(e)})
        raise
