from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .personas import router as personas_router
from .topics import router as topics_router
from .ideas import router as ideas_router
from .research import router as research_router
from .blog_posts import router as blog_posts_router
from .assets import router as assets_router
from .social_posts import router as social_posts_router
from .export import router as export_router
from .progress import router as progress_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(personas_router, prefix="/personas", tags=["Personas"])
api_router.include_router(topics_router, prefix="/topics", tags=["Topics"])
api_router.include_router(ideas_router, prefix="/ideas", tags=["Ideas"])
api_router.include_router(research_router, prefix="/research", tags=["Research"])
api_router.include_router(blog_posts_router, prefix="/blog-posts", tags=["Blog Posts"])
api_router.include_router(assets_router, prefix="/assets", tags=["Assets"])
api_router.include_router(social_posts_router, prefix="/social-posts", tags=["Social Posts"])
api_router.include_router(export_router, prefix="/export", tags=["Export"])
api_router.include_router(progress_router, prefix="/progress", tags=["Progress Tracking"])
