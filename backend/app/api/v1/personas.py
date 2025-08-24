from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import selectinload

from ...database import get_db
from ...models.persona import Persona
from ...models.user import User
from ...schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse, PersonaList
from ...schemas.common import PaginationParams
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=PersonaResponse)
async def create_persona(
    persona_data: PersonaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new persona for the current user"""
    persona = Persona(
        **persona_data.dict(),
        user_id=current_user.id
    )
    
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    
    return persona


@router.get("/", response_model=PersonaList)
async def list_personas(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List personas for the current user"""
    # Build query
    query = select(Persona).where(Persona.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((pagination.page - 1) * pagination.size).limit(pagination.size)
    
    # Execute query
    result = await db.execute(query)
    personas = result.scalars().all()
    
    return PersonaList(
        personas=personas,
        total=total
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get persona details"""
    persona = await db.get(Persona, persona_id)
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this persona"
        )
    
    return persona


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: int,
    persona_data: PersonaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update persona"""
    persona = await db.get(Persona, persona_id)
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this persona"
        )
    
    # Update fields
    for field, value in persona_data.dict(exclude_unset=True).items():
        setattr(persona, field, value)
    
    await db.commit()
    await db.refresh(persona)
    
    return persona


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete persona"""
    persona = await db.get(Persona, persona_id)
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    if persona.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this persona"
        )
    
    await db.delete(persona)
    await db.commit()
    
    return {"message": "Persona deleted successfully"}


@router.get("/default/create")
async def create_default_personas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create default personas for the current user if they don't exist"""
    # Check if default personas already exist
    existing_personas = await db.execute(
        select(func.count(Persona.id)).where(Persona.user_id == current_user.id)
    )
    count = existing_personas.scalar()
    
    if count > 0:
        return {"message": "Default personas already exist", "count": count}
    
    # Create default personas
    default_personas = [
        {
            "name": "Analytical",
            "description": "Data-driven, research-focused writing style",
            "writing_style": "professional",
            "tone": "neutral",
            "target_audience": "professionals",
            "include_statistics": True,
            "include_examples": True,
            "always_key_takeaways": True
        },
        {
            "name": "Witty",
            "description": "Engaging, humorous, and conversational tone",
            "writing_style": "casual",
            "tone": "friendly",
            "target_audience": "general",
            "include_statistics": False,
            "include_examples": True,
            "always_key_takeaways": True
        },
        {
            "name": "Educational",
            "description": "Clear, instructional, and informative writing",
            "writing_style": "conversational",
            "tone": "friendly",
            "target_audience": "learners",
            "include_statistics": True,
            "include_examples": True,
            "always_key_takeaways": True
        }
    ]
    
    for persona_data in default_personas:
        persona = Persona(
            user_id=current_user.id,
            **persona_data
        )
        db.add(persona)
    
    await db.commit()
    
    return {"message": "Default personas created successfully", "count": len(default_personas)}
