from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.idea import Idea
from ...models.user import User
from ...models.topic import Topic
from ...schemas.idea import IdeaResponse, IdeaList, IdeaApprovalRequest
from ...schemas.common import PaginationParams, FilterParams
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=IdeaList)
async def list_ideas(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List ideas with filtering and pagination"""
    # Build query
    query = select(Idea).join(Topic).where(Topic.user_id == current_user.id)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            (Idea.title.ilike(search_term)) |
            (Idea.description.ilike(search_term))
        )
    
    if filters.status:
        query = query.where(Idea.status == filters.status)
    
    if filters.topic_id:
        query = query.where(Idea.topic_id == filters.topic_id)
    
    if filters.is_approved is not None:
        query = query.where(Idea.is_approved == filters.is_approved)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    ideas = result.scalars().all()
    
    return IdeaList(
        ideas=ideas,
        total=total
    )


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get idea details"""
    idea = await db.execute(
        select(Idea).join(Topic).where(
            Idea.id == idea_id,
            Topic.user_id == current_user.id
        )
    )
    idea = idea.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    return idea


@router.post("/{idea_id}/approve")
async def approve_idea(
    idea_id: int,
    approval_data: IdeaApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject an idea"""
    idea = await db.execute(
        select(Idea).join(Topic).where(
            Idea.id == idea_id,
            Topic.user_id == current_user.id
        )
    )
    idea = idea.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Update approval status
    idea.is_approved = approval_data.is_approved
    idea.is_rejected = not approval_data.is_approved
    idea.user_notes = approval_data.user_notes
    idea.status = "approved" if approval_data.is_approved else "rejected"
    
    await db.commit()
    
    return {"message": f"Idea {'approved' if approval_data.is_approved else 'rejected'} successfully"}


@router.get("/topic/{topic_id}", response_model=IdeaList)
async def get_ideas_by_topic(
    topic_id: int,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get ideas for a specific topic"""
    # Verify topic belongs to user
    topic = await db.get(Topic, topic_id)
    if not topic or topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Build query
    query = select(Idea).where(Idea.topic_id == topic_id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    ideas = result.scalars().all()
    
    return IdeaList(
        ideas=ideas,
        total=total
    )


@router.get("/status/count")
async def get_idea_status_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of ideas by status for the current user"""
    # Get ideas joined with topics for the current user
    query = select(
        Idea.status,
        func.count(Idea.id).label('count')
    ).join(Topic).where(
        Topic.user_id == current_user.id
    ).group_by(Idea.status)
    
    result = await db.execute(query)
    status_counts = result.all()
    
    return {
        status: count for status, count in status_counts
    }
