"""Celery Worker 实例配置"""

from celery import Celery

from app.config import get_settings

settings = get_settings()

# 创建 Celery 应用
celery_app = Celery(
    "learnyourway",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分钟
    task_soft_time_limit=25 * 60,  # 25 分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 自动发现任务
celery_app.autodiscover_tasks(
    [
        "app.tasks.ingest_pdf",
        "app.tasks.personalize",
        "app.tasks.materials",
        "app.tasks.scoring",
    ]
)
