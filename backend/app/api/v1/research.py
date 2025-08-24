from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.research import Research
from ...models.idea import Idea
from ...models.user import User
from ...schemas.research import ResearchResponse, ResearchList, ResearchStartRequest
from ...schemas.common import PaginationParams
from ..auth import get_current_user
from ...tasks.research import start_research_for_idea

router = APIRouter()


@router.post("/start", response_model=dict)
async def start_research(
    research_request: ResearchStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start research for an approved idea"""
    # Get the idea
    idea = await db.get(Idea, research_request.idea_id)
    
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    if idea.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to research this idea"
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
        research_prompt=research_request.research_prompt or f"Research current events and trends related to: {idea.title}",
        status="pending"
    )
    
    db.add(research)
    await db.commit()
    await db.refresh(research)
    
    # Update idea status
    idea.status = "researching"
    await db.commit()
    
    # Start background research task
    task = start_research_for_idea.delay(research.id)
    
    return {
        "message": "Research started successfully",
        "research_id": research.id,
        "task_id": task.id,
        "status": "processing"
    }


@router.get("/", response_model=ResearchList)
async def list_research(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List research for the current user"""
    # Build query - join with ideas to filter by user
    query = select(Research).join(Idea).where(Idea.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    research_list = result.scalars().all()
    
    return ResearchList(
        research=research_list,
        total=total
    )


@router.get("/{research_id}", response_model=ResearchResponse)
async def get_research(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research details"""
    # Get research with idea to check ownership
    query = select(Research).join(Idea).where(
        Research.id == research_id,
        Idea.user_id == current_user.id
    )
    
    result = await db.execute(query)
    research = result.scalar_one_or_none()
    
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
    # Verify idea ownership
    idea = await db.get(Idea, idea_id)
    if not idea or idea.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Idea not found"
        )
    
    # Get research for idea
    research = await db.execute(
        select(Research).where(Research.idea_id == idea_id)
    )
    research_obj = research.scalar_one_or_none()
    
    if not research_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found for this idea"
        )
    
    return research_obj


@router.get("/status/{research_id}")
async def get_research_status(
    research_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research status and progress"""
    # Get research with idea to check ownership
    query = select(Research).join(Idea).where(
        Research.id == research_id,
        Idea.user_id == current_user.id
    )
    
    result = await db.execute(query)
    research = result.scalar_one_or_none()
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research not found"
        )
    
    return {
        "research_id": research.id,
        "status": research.status,
        "source_count": research.source_count,
        "created_at": research.created_at,
        "updated_at": research.updated_at
    }
