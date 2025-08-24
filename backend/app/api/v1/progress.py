from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from ...database import get_db
from ...models.user import User
from ...models.topic import Topic
from ...models.idea import Idea
from ...models.research import Research
from ...models.blog_post import BlogPost
from ...celery_app import celery_app
from .auth import get_current_user

router = APIRouter()


@router.get("/overview")
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an overview of content generation progress"""
    try:
        # Get counts for different stages
        topic_count = await db.scalar(
            select(func.count(Topic.id)).where(Topic.user_id == current_user.id)
        )
        
        idea_count = await db.scalar(
            select(func.count(Idea.id)).join(Topic).where(Topic.user_id == current_user.id)
        )
        
        approved_idea_count = await db.scalar(
            select(func.count(Idea.id)).join(Topic).where(
                Topic.user_id == current_user.id,
                Idea.is_approved == True
            )
        )
        
        research_count = await db.scalar(
            select(func.count(Research.id)).join(Idea).join(Topic).where(
                Topic.user_id == current_user.id
            )
        )
        
        completed_research_count = await db.scalar(
            select(func.count(Research.id)).join(Idea).join(Topic).where(
                Topic.user_id == current_user.id,
                Research.status == "completed"
            )
        )
        
        blog_post_count = await db.scalar(
            select(func.count(BlogPost.id)).join(Idea).join(Topic).where(
                Topic.user_id == current_user.id
            )
        )
        
        approved_blog_post_count = await db.scalar(
            select(func.count(BlogPost.id)).join(Idea).join(Topic).where(
                Topic.user_id == current_user.id,
                BlogPost.is_approved == True
            )
        )
        
        return {
            "topics": {
                "total": topic_count or 0,
                "completed": topic_count or 0  # All topics are considered completed
            },
            "ideas": {
                "total": idea_count or 0,
                "approved": approved_idea_count or 0,
                "pending_review": (idea_count or 0) - (approved_idea_count or 0)
            },
            "research": {
                "total": research_count or 0,
                "completed": completed_research_count or 0,
                "pending": (research_count or 0) - (completed_research_count or 0)
            },
            "blog_posts": {
                "total": blog_post_count or 0,
                "approved": approved_blog_post_count or 0,
                "pending_review": (blog_post_count or 0) - (approved_blog_post_count or 0)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting progress overview: {str(e)}"
        )


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a specific Celery task"""
    try:
        # Get task result from Celery
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "status": "Task is waiting for execution or unknown"
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result
            }
        elif task_result.state == "FAILURE":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info)
            }
        else:
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "info": task_result.info
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        )
