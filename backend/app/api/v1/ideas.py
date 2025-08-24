from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.idea import Idea
from ...models.topic import Topic
from ...models.user import User
from ...schemas.idea import IdeaResponse, IdeaList, IdeaApprovalRequest
from ...schemas.common import PaginationParams, FilterParams
from ..auth import get_current_user

router = APIRouter()


@router.get("/", response_model=IdeaList)
async def list_ideas(
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List ideas with filtering and pagination"""
    # Build query
    query = select(Idea).where(Idea.user_id == current_user.id)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            (Idea.title.ilike(search_term)) |
            (Idea.description.ilike(search_term)) |
            (Idea.angle.ilike(search_term))
        )
    
    if filters.status:
        query = query.where(Idea.status == filters.status)
    
    if topic_id:
        query = query.where(Idea.topic_id == topic_id)
    
    if filters.date_from:
        query = query.where(Idea.created_at >= filters.date_from)
    
    if filters.date_to:
        query = query.where(Idea.created_at <= filters.date_to)
    
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
    idea = await db.get(Idea, idea_id)
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    if idea.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this idea"
        )
    
    return idea


@router.put("/{idea_id}/approve")
async def approve_idea(
    idea_id: int,
    approval_data: IdeaApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject an idea"""
    idea = await db.get(Idea, idea_id)
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    if idea.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this idea"
        )
    
    # Update approval status
    if approval_data.is_approved:
        idea.is_approved = True
        idea.is_rejected = False
        idea.status = "approved"
    else:
        idea.is_approved = False
        idea.is_rejected = True
        idea.status = "rejected"
    
    # Update user notes
    if approval_data.user_notes:
        idea.user_notes = approval_data.user_notes
    
    await db.commit()
    await db.refresh(idea)
    
    action = "approved" if approval_data.is_approved else "rejected"
    return {"message": f"Idea {action} successfully"}


@router.get("/topic/{topic_id}", response_model=IdeaList)
async def get_ideas_by_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all ideas for a specific topic"""
    # Verify topic ownership
    topic = await db.get(Topic, topic_id)
    if not topic or topic.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Get ideas for topic
    query = select(Idea).where(
        Idea.topic_id == topic_id,
        Idea.user_id == current_user.id
    ).order_by(Idea.created_at.desc())
    
    result = await db.execute(query)
    ideas = result.scalars().all()
    
    return IdeaList(
        ideas=ideas,
        total=len(ideas)
    )


@router.get("/pending/count")
async def get_pending_ideas_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of pending ideas for the current user"""
    query = select(func.count(Idea.id)).where(
        Idea.user_id == current_user.id,
        Idea.is_approved == False,
        Idea.is_rejected == False
    )
    
    count = await db.scalar(query)
    return {"pending_count": count}


@router.get("/approved/count")
async def get_approved_ideas_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of approved ideas for the current user"""
    query = select(func.count(Idea.id)).where(
        Idea.user_id == current_user.id,
        Idea.is_approved == True
    )
    
    count = await db.scalar(query)
    return {"approved_count": count}
