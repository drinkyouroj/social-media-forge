from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.topic import Topic
from ...models.user import User
from ...schemas.topic import TopicCreate, TopicUpdate, TopicResponse, TopicList
from ...schemas.common import PaginationParams
from ...tasks.idea_generation import generate_ideas_for_topic
from .auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TopicResponse)
async def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new topic"""
    topic = Topic(
        **topic_data.dict(),
        user_id=current_user.id
    )
    
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    
    return topic


@router.get("/", response_model=TopicList)
async def list_topics(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List topics for the current user"""
    # Build query
    query = select(Topic).where(Topic.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    topics = result.scalars().all()
    
    return TopicList(
        topics=topics,
        total=total
    )


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get topic details"""
    topic = await db.get(Topic, topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this topic"
        )
    
    return topic


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update topic"""
    topic = await db.get(Topic, topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this topic"
        )
    
    # Update fields
    for field, value in topic_data.dict(exclude_unset=True).items():
        setattr(topic, field, value)
    
    await db.commit()
    await db.refresh(topic)
    
    return topic


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete topic"""
    topic = await db.get(Topic, topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this topic"
        )
    
    await db.delete(topic)
    await db.commit()
    
    return {"message": "Topic deleted successfully"}


@router.post("/{topic_id}/generate-ideas")
async def generate_ideas_for_topic_endpoint(
    topic_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate blog post ideas for a topic"""
    # Verify topic exists and belongs to user
    topic = await db.get(Topic, topic_id)
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    if topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate ideas for this topic"
        )
    
    # Update topic status
    topic.status = "generating_ideas"
    await db.commit()
    
    # Start background task
    task = generate_ideas_for_topic.delay(topic_id)
    
    return {
        "message": "Idea generation started",
        "task_id": task.id,
        "status": "generating_ideas"
    }
