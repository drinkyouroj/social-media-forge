from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from ...database import get_db
from ...models.topic import Topic
from ...models.idea import Idea
from ...models.research import Research
from ...models.blog_post import BlogPost
from ...models.user import User
from ..auth import get_current_user
from ...celery_app import celery_app

router = APIRouter()


@router.get("/overview")
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overview of all content generation progress for the user"""
    
    # Count topics by status
    topic_counts = await db.execute(
        select(Topic.status, func.count(Topic.id))
        .where(Topic.user_id == current_user.id)
        .group_by(Topic.status)
    )
    topic_status = dict(topic_counts.all())
    
    # Count ideas by status
    idea_counts = await db.execute(
        select(Idea.status, func.count(Idea.id))
        .where(Idea.user_id == current_user.id)
        .group_by(Idea.status)
    )
    idea_status = dict(idea_counts.all())
    
    # Count research by status
    research_counts = await db.execute(
        select(Research.status, func.count(Research.id))
        .join(Idea)
        .where(Idea.user_id == current_user.id)
        .group_by(Research.status)
    )
    research_status = dict(research_counts.all())
    
    # Count blog posts by status
    blog_counts = await db.execute(
        select(BlogPost.status, func.count(BlogPost.id))
        .where(BlogPost.user_id == current_user.id)
        .group_by(BlogPost.status)
    )
    blog_status = dict(blog_counts.all())
    
    return {
        "topics": {
            "total": sum(topic_status.values()),
            "by_status": topic_status
        },
        "ideas": {
            "total": sum(idea_status.values()),
            "by_status": idea_status
        },
        "research": {
            "total": sum(research_status.values()),
            "by_status": research_status
        },
        "blog_posts": {
            "total": sum(blog_status.values()),
            "by_status": blog_status
        }
    }


@router.get("/topic/{topic_id}")
async def get_topic_progress(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed progress for a specific topic"""
    
    # Verify topic ownership
    topic = await db.get(Topic, topic_id)
    if not topic or topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get ideas for this topic
    ideas = await db.execute(
        select(Idea).where(Idea.topic_id == topic_id)
    )
    ideas_list = ideas.scalars().all()
    
    # Get research for approved ideas
    research_list = []
    for idea in ideas_list:
        if idea.is_approved:
            research = await db.execute(
                select(Research).where(Research.idea_id == idea.id)
            )
            research_obj = research.scalar_one_or_none()
            if research_obj:
                research_list.append(research_obj)
    
    # Get blog posts for approved ideas
    blog_posts = []
    for idea in ideas_list:
        if idea.is_approved:
            blog_post = await db.execute(
                select(BlogPost).where(BlogPost.idea_id == idea.id)
            )
            blog_obj = blog_post.scalar_one_or_none()
            if blog_obj:
                blog_posts.append(blog_obj)
    
    return {
        "topic": {
            "id": topic.id,
            "title": topic.title,
            "status": topic.status,
            "created_at": topic.created_at
        },
        "progress": {
            "ideas_generated": len(ideas_list),
            "ideas_approved": len([i for i in ideas_list if i.is_approved]),
            "ideas_rejected": len([i for i in ideas_list if i.is_rejected]),
            "research_completed": len([r for r in research_list if r.status == "completed"]),
            "blog_posts_drafted": len([b for b in blog_posts if b.status == "draft"]),
            "blog_posts_approved": len([b for b in blog_posts if b.status == "approved"])
        },
        "ideas": [
            {
                "id": idea.id,
                "title": idea.title,
                "status": idea.status,
                "is_approved": idea.is_approved,
                "is_rejected": idea.is_rejected
            }
            for idea in ideas_list
        ]
    }


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific Celery task"""
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": 0,
                "total": 1,
                "status": "Task is pending..."
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "status": task_result.info.get("status", "")
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 1),
                "total": task_result.info.get("total", 1),
                "status": "Task completed successfully",
                "result": task_result.result
            }
        else:
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": 0,
                "total": 1,
                "status": "Task failed",
                "error": str(task_result.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting task status: {str(e)}"
        )
