"""个性化改写任务"""

from app.tasks.worker import celery_app


@celery_app.task(bind=True, name="personalize_text")
def personalize_text_task(self, chunk_id: str, profile_id: str):
    """
    个性化改写任务
    
    Args:
        chunk_id: 文本块 ID
        profile_id: 用户画像 ID
        
    Returns:
        {
            "personalized_text": "...",
            "metadata": {...}
        }
    """
    try:
        self.update_state(
            state="STARTED",
            meta={"stage": "loading_profile", "progress": 10},
        )
        
        # TODO: 加载用户画像
        
        self.update_state(
            state="STARTED",
            meta={"stage": "rewriting", "progress": 30},
        )
        
        # TODO: 调用 LLM 进行改写
        # from app.services.llm_provider import get_llm_provider
        # provider = get_llm_provider()
        # result = await provider.chat([...])
        
        self.update_state(
            state="STARTED",
            meta={"stage": "evaluating", "progress": 80},
        )
        
        # TODO: 评测改写质量
        
        return {
            "personalized_text": "改写后的内容...",
            "metadata": {
                "grade": 5,
                "interests": ["足球", "科学"],
            },
        }
    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)},
        )
        raise
