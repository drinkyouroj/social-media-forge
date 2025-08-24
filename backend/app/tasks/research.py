from celery import shared_task
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import json
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any

from ..config import settings
from ..models.research import Research
from ..models.idea import Idea
from ..database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize OpenAI client only if API key is available
openai_client = None
if settings.openai_api_key:
    openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


def is_reputable_source(url: str) -> bool:
    """Check if a source is reputable based on domain"""
    reputable_domains = [
        'bbc.com', 'cnn.com', 'reuters.com', 'apnews.com',
        'nytimes.com', 'wsj.com', 'ft.com', 'techcrunch.com',
        'theverge.com', 'wired.com', 'arstechnica.com',
        'github.com', 'stackoverflow.com', 'medium.com'
    ]
    
    for domain in reputable_domains:
        if domain in url.lower():
            return True
    return False


@shared_task(bind=True)
def start_research_for_idea(self, research_id: int):
    """Start research for an approved idea using OpenAI"""
    
    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        error_msg = "OpenAI API key not configured. Please add OPENAI_API_KEY to your environment variables."
        logger.error(error_msg)
        self.update_state(
            state="FAILURE",
            meta={"error": error_msg}
        )
        raise ValueError(error_msg)
    
    if not openai_client:
        error_msg = "OpenAI client not initialized. Please check your API key configuration."
        logger.error(error_msg)
        self.update_state(
            state="FAILURE",
            meta={"error": error_msg}
        )
        raise ValueError(error_msg)
    
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 5, "status": "Starting research..."}
        )
        
        # Create async database session
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async def perform_research():
            async with AsyncSessionLocal() as db:
                # Get research record
                research = await db.get(Research, research_id)
                if not research:
                    raise ValueError(f"Research {research_id} not found")
                
                # Get idea details
                idea = await db.get(Idea, research.idea_id)
                if not idea:
                    raise ValueError(f"Idea {research.idea_id} not found")
                
                # Update progress
                self.update_state(
                    state="PROGRESS",
                    meta={"current": 1, "total": 5, "status": "Searching current events..."}
                )
                
                # Search for current events related to the topic
                current_events_prompt = f"""
                Find 3-5 current events, trends, or recent developments related to: "{idea.title}"
                
                Focus on:
                1. Recent news articles (last 3 months)
                2. Industry trends and developments
                3. Technological advances
                4. Market changes or business developments
                
                For each event, provide:
                - Brief description
                - Source (reputable news outlet)
                - Relevance to the topic
                
                Format as JSON:
                {{
                    "current_events": [
                        {{
                            "title": "Event Title",
                            "description": "Brief description",
                            "source": "Source name",
                            "url": "Source URL",
                            "relevance": "Why this matters"
                        }}
                    ]
                }}
                """
                
                try:
                    response = await openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[{"role": "user", "content": current_events_prompt}],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    current_events_data = json.loads(response.choices[0].message.content)
                    
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={"current": 2, "total": 5, "status": "Analyzing sources..."}
                    )
                    
                    # Filter and validate sources
                    valid_sources = []
                    for event in current_events_data.get("current_events", []):
                        if is_reputable_source(event.get("url", "")):
                            valid_sources.append(event)
                    
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={"current": 3, "total": 5, "status": "Generating research outline..."}
                    )
                    
                    # Generate research outline
                    outline_prompt = f"""
                    Based on the topic "{idea.title}" and current events, create a comprehensive research outline.
                    
                    Current events context: {json.dumps(valid_sources[:3])}
                    
                    Create a structured outline that covers:
                    1. Introduction and context
                    2. Key areas of research
                    3. Supporting evidence and examples
                    4. Implications and conclusions
                    
                    Format as JSON:
                    {{
                        "outline": {{
                            "title": "Research Outline Title",
                            "sections": [
                                {{
                                    "heading": "Section Heading",
                                    "key_points": ["Point 1", "Point 2"],
                                    "sources_needed": ["Type of source", "Specific focus"]
                                }}
                            ]
                        }}
                    }}
                    """
                    
                    outline_response = await openai_client.chat.completions.create(
                        model=settings.openai_model,
                        messages=[{"role": "user", "content": outline_prompt}],
                        temperature=0.7,
                        max_tokens=800
                    )
                    
                    outline_data = json.loads(outline_response.choices[0].message.content)
                    
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={"current": 4, "total": 5, "status": "Finalizing research..."}
                    )
                    
                    # Update research record
                    research.key_findings = current_events_data
                    research.outline = outline_data
                    research.sources = valid_sources
                    research.source_count = len(valid_sources)
                    research.model_used = settings.openai_model
                    research.tokens_used = response.usage.total_tokens + outline_response.usage.total_tokens
                    research.status = "completed"
                    
                    await db.commit()
                    
                    # Update progress
                    self.update_state(
                        state="PROGRESS",
                        meta={"current": 5, "total": 5, "status": "Research completed!"}
                    )
                    
                    return {
                        "status": "success",
                        "sources_found": len(valid_sources),
                        "outline_generated": True
                    }
                    
                except Exception as e:
                    logger.error(f"Error in OpenAI API call: {str(e)}")
                    research.status = "failed"
                    research.error_message = str(e)
                    await db.commit()
                    raise
        
        # Run the async function
        result = asyncio.run(perform_research())
        
        # Update final status
        self.update_state(
            state="SUCCESS",
            meta={"current": 5, "total": 5, "status": "Research completed successfully"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in start_research_for_idea: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
