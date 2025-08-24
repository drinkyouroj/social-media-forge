#!/usr/bin/env python3
"""
Database initialization script for Social Media Forge
Creates admin user and default personas
"""

import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.persona import Persona
from app.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def create_admin_user():
    """Create the admin user"""
    async with AsyncSessionLocal() as db:
        # Check if admin user already exists
        existing_admin = await db.get(User, 1)
        if existing_admin:
            print("Admin user already exists")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            email=settings.admin_email,
            password_hash=get_password_hash(settings.admin_password),
            first_name="Admin",
            last_name="User",
            is_admin=True,
            is_active=True
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"Admin user created: {admin_user.email}")
        return admin_user


async def create_default_personas(admin_user: User):
    """Create default personas for the admin user"""
    async with AsyncSessionLocal() as db:
        # Check if personas already exist
        existing_personas = await db.execute(
            "SELECT COUNT(*) FROM personas WHERE user_id = :user_id",
            {"user_id": admin_user.id}
        )
        count = existing_personas.scalar()
        
        if count > 0:
            print("Default personas already exist")
            return
        
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
                user_id=admin_user.id,
                **persona_data
            )
            db.add(persona)
        
        await db.commit()
        print("Default personas created successfully")


async def main():
    """Main initialization function"""
    print("Initializing Social Media Forge database...")
    
    try:
        # Initialize database tables
        await init_db()
        print("Database tables created successfully")
        
        # Create admin user
        admin_user = await create_admin_user()
        
        # Create default personas
        await create_default_personas(admin_user)
        
        print("Database initialization completed successfully!")
        print(f"Admin user: {settings.admin_email}")
        print(f"Admin password: {settings.admin_password}")
        print("\nYou can now start the application and log in with these credentials.")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
