from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.research import Research
from ...models.idea import Idea
from ...models.user import User
from ...models.topic import Topic
from ...schemas.research import ResearchResponse, ResearchList, ResearchStartRequest
from ...schemas.common import PaginationParams
from ...tasks.research import start_research_for_idea
from .auth import get_current_user

router = APIRouter()


@router.post("/start")
async def start_research(
    research_request: ResearchStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start research for an approved idea"""
    # Verify idea exists and belongs to user
    idea = await db.execute(
        select(Idea).join(Topic).where(
            Idea.id == research_request.idea_id,
            Topic.user_id == current_user.id
        )
    )
    idea = idea.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    if not idea.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only research approved ideas"
        )
    
    # Check if research already exists
    existing_research = await db.execute(
        select(Research).where(Research.idea_id == research_request.idea_id)
    )
    if existing_research.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Research already exists for this idea"
        )
    
    # Create research record
    research = Research(
        idea_id=research_request.idea_id,
        research_prompt=research_request.research_prompt,
        status="pending"
    )
    
    db.add(research)
    await db.commit()
    await db.refresh(research)
    
    # Start background research task
    task = start_research_for_idea.delay(research.id)
    
    return {
        "message": "Research started successfully",
        "research_id": research.id,
        "task_id": task.id,
        "status": "pending"
    }


@router.get("/", response_model=ResearchList)
async def list_research(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List research records for the current user"""
    # Build query
    query = select(Research).join(Idea).join(Topic).where(
        Topic.user_id == current_user.id
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    research_records = result.scalars().all()
    
    return ResearchList(
        research_records=research_records,
        total=total
    )


@router.get("/{research_id}", response_model=ResearchResponse)
async def get_research(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research details"""
    research = await db.execute(
        select(Research).join(Idea).join(Topic).where(
            Research.id == research_id,
            Topic.user_id == current_user.id
        )
    )
    research = research.scalar_one_or_none()
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found"
        )
    
    return research


@router.get("/idea/{idea_id}", response_model=ResearchResponse)
async def get_research_by_idea(
    idea_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research for a specific idea"""
    # Verify idea belongs to user
    idea = await db.execute(
        select(Idea).join(Topic).where(
            Idea.id == idea_id,
            Topic.user_id == current_user.id
        )
    )
    if not idea.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Get research
    research = await db.execute(
        select(Research).where(Research.idea_id == idea_id)
    )
    research = research.scalar_one_or_none()
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found for this idea"
        )
    
    return research


@router.get("/status/{research_id}")
async def get_research_status(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research status and progress"""
    research = await db.execute(
        select(Research).join(Idea).join(Topic).where(
            Research.id == research_id,
            Topic.user_id == current_user.id
        )
    )
    research = research.scalar_one_or_none()
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found"
        )
    
    return {
        "research_id": research.id,
        "status": research.status,
        "progress": research.progress if hasattr(research, 'progress') else None,
        "created_at": research.created_at,
        "updated_at": research.updated_at
    }
