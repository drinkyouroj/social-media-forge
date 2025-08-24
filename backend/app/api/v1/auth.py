from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from typing import Optional

from ...database import get_db
from ...sessions import session_manager
from ...models.user import User
from ...schemas.auth import LoginRequest, LoginResponse, UserResponse
from ...schemas.common import MessageResponse

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def get_current_user(
    session_id: str = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from session"""
    session = await session_manager.get_session(session_id.credentials)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    user_id = session.get("user_id")
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint"""
    # Find user by email
    user = await db.get(User, login_data.email)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # Create session
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin
    }
    
    session_id = await session_manager.create_session(user.id, user_data)
    
    return LoginResponse(
        session_id=session_id,
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=user.is_admin
        )
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    session_id: str = Depends(security)
):
    """User logout endpoint"""
    await session_manager.delete_session(session_id.credentials)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_admin=current_user.is_admin
    )


@router.post("/refresh", response_model=MessageResponse)
async def refresh_session(
    session_id: str = Depends(security)
):
    """Refresh session expiration"""
    success = await session_manager.refresh_session(session_id.credentials)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return MessageResponse(message="Session refreshed successfully")
