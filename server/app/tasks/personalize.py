"""个性化改写任务"""

import asyncio

from app.tasks.worker import celery_app


@celery_app.task(bind=True, name="personalize_text")
def personalize_text_task(self, chunk_id: str, profile_id: str, original_text: str):
    """
    个性化改写任务
    
    Args:
        chunk_id: 文本块 ID
        profile_id: 用户画像 ID
        original_text: 原始文本
        
    Returns:
        {
            "personalized_text": str,
            "original_readability": Dict,
            "personalized_readability": Dict,
            "improvement": Dict,
            "evaluation": Dict
        }
    """
    try:
        self.update_state(
            state="STARTED",
            meta={"stage": "loading_profile", "progress": 10},
        )
        
        # 加载用户画像（这里模拟从数据库加载）
        # TODO: 从实际数据库加载
        from app.api.profiles import profiles_db
        
        if profile_id not in profiles_db:
            raise ValueError(f"用户画像不存在: {profile_id}")
        
        profile = profiles_db[profile_id]
        grade = profile["grade"]
        interests = profile["interests"]
        
        self.update_state(
            state="STARTED",
            meta={"stage": "analyzing_readability", "progress": 20},
        )
        
        # 分析原文可读性
        from app.services.readability_service import get_readability_service
        readability_service = get_readability_service()
        original_readability = readability_service.analyze_readability(original_text, grade)
        
        self.update_state(
            state="STARTED",
            meta={"stage": "personalizing", "progress": 40},
        )
        
        # 调用个性化服务进行改写
        from app.services.personalize_service import get_personalize_service
        personalize_service = get_personalize_service()
        
        # 由于 Celery 任务是同步的，需要使用 asyncio.run
        result = asyncio.run(
            personalize_service.personalize_text(
                original_text=original_text,
                grade=grade,
                interests=interests,
                must_keep_terms=None,  # TODO: 从配置或参数中获取
            )
        )
        
        self.update_state(
            state="STARTED",
            meta={"stage": "evaluating", "progress": 70},
        )
        
        # 评测改写质量
        from app.services.evaluation_service import get_evaluation_service
        evaluation_service = get_evaluation_service()
        
        evaluation = asyncio.run(
            evaluation_service.evaluate_personalization(
                original_text=original_text,
                personalized_text=result["personalized_text"],
                grade=grade,
                interests=interests,
            )
        )
        
        self.update_state(
            state="STARTED",
            meta={"stage": "completed", "progress": 100},
        )
        
        return {
            "chunk_id": chunk_id,
            "profile_id": profile_id,
            "personalized_text": result["personalized_text"],
            "original_readability": result["original_readability"],
            "personalized_readability": result["personalized_readability"],
            "improvement": result["improvement"],
            "evaluation": evaluation,
        }
        
    except Exception as e:
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)},
        )
        raise
