from celery import Celery
from .config import settings

# Create Celery instance
celery_app = Celery(
    "social_media_forge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.idea_generation",
        "app.tasks.research",
        "app.tasks.blog_writing",
        "app.tasks.image_generation",
        "app.tasks.social_generation"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.tasks.maintenance.cleanup_expired_sessions",
            "schedule": 3600.0,  # Every hour
        },
    }
)

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.idea_generation.*": {"queue": "ideas"},
    "app.tasks.research.*": {"queue": "research"},
    "app.tasks.blog_writing.*": {"queue": "writing"},
    "app.tasks.image_generation.*": {"queue": "images"},
    "app.tasks.social_generation.*": {"queue": "social"},
    "app.tasks.maintenance.*": {"queue": "maintenance"},
}

if __name__ == "__main__":
    celery_app.start()
