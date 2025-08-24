from celery import current_task
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import json
import logging
import time
from typing import List, Dict, Any

from ..config import settings
from ..models.research import Research
from ..models.idea import Idea
from ..database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


def is_reputable_source(url: str) -> bool:
    """Check if a source is in the whitelist of reputable sources"""
    if settings.allowed_source_mode == "allow_all":
        return True
    
    domain = url.lower().split('/')[2] if len(url.split('/')) > 2 else url.lower()
    
    if settings.allowed_source_mode == "whitelist":
        return any(source in domain for source in settings.allowed_sources)
    else:  # blacklist mode
        return not any(source in domain for source in settings.allowed_sources)


async def search_current_events(topic: str) -> List[Dict[str, Any]]:
    """Search for current events related to the topic using OpenAI"""
    prompt = f"""
    Research current events and trends related to: "{topic}"
    
    Find recent news, developments, and insights that would be relevant for a blog post.
    Focus on mainstream, reputable sources and current events from the past few months.
    
    Return your findings as a JSON array with this structure:
    [
        {{
            "title": "News headline or topic",
            "summary": "Brief summary of the development",
            "relevance": "How this relates to the main topic",
            "date": "When this happened (approximate)",
            "source_type": "news, research, trend, etc."
        }}
    ]
    
    Limit to 5-8 most relevant current events.
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        events = json.loads(content)
        return events
        
    except Exception as e:
        logger.error(f"Error searching current events: {str(e)}")
        return []


async def find_relevant_sources(topic: str, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find relevant sources and citations for the research"""
    sources = []
    
    # Create a comprehensive research prompt
    research_prompt = f"""
    Topic: {topic}
    
    Current Events Found:
    {json.dumps(events, indent=2)}
    
    Find 5-10 relevant, reputable sources that support or provide context for these developments.
    Focus on:
    1. Recent news articles (last 6 months)
    2. Academic or industry research
    3. Expert opinions and analysis
    4. Statistical data and reports
    
    For each source, provide:
    - URL (must be accessible)
    - Title
    - Publication name
    - Author (if available)
    - Date published
    - Brief excerpt explaining relevance
    
    Return as JSON array:
    [
        {{
            "url": "https://example.com/article",
            "title": "Article Title",
            "publication": "Publication Name",
            "author": "Author Name",
            "date_published": "2024-01-15",
            "excerpt": "Brief explanation of why this source is relevant"
        }}
    ]
    
    Only include sources from reputable publications and ensure URLs are valid.
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": research_prompt}],
            temperature=0.6,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        raw_sources = json.loads(content)
        
        # Filter and validate sources
        for source in raw_sources:
            if is_reputable_source(source.get("url", "")):
                sources.append(source)
        
        return sources[:10]  # Limit to 10 sources
        
    except Exception as e:
        logger.error(f"Error finding sources: {str(e)}")
        return []


async def generate_research_outline(topic: str, events: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a research outline based on findings"""
    outline_prompt = f"""
    Topic: {topic}
    
    Current Events:
    {json.dumps(events, indent=2)}
    
    Sources:
    {json.dumps(sources, indent=2)}
    
    Create a comprehensive research outline for a blog post that incorporates these findings.
    
    Structure the outline as JSON:
    {{
        "title": "Working title for the blog post",
        "introduction": "Key points for the introduction",
        "main_sections": [
            {{
                "heading": "Section heading",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "sources": ["source_index_1", "source_index_2"],
                "current_events": ["event_index_1", "event_index_2"]
            }}
        ],
        "conclusion": "Key points for the conclusion",
        "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
        "recommended_word_count": 1500
    }}
    
    Ensure the outline flows logically and incorporates current events naturally.
    """
    
    try:
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": outline_prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        outline = json.loads(content)
        return outline
        
    except Exception as e:
        logger.error(f"Error generating outline: {str(e)}")
        return {}


@current_task.task(bind=True)
def start_research_for_idea(self, research_id: int):
    """Start research process for an approved idea"""
    start_time = time.time()
    
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 4, "status": "Starting research..."}
        )
        
        # Create async database session
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async def conduct_research():
            async with AsyncSessionLocal() as db:
                # Get research record
                research = await db.get(Research, research_id)
                if not research:
                    raise ValueError(f"Research {research_id} not found")
                
                # Get the idea
                idea = await db.get(Idea, research.idea_id)
                if not idea:
                    raise ValueError(f"Idea {research.idea_id} not found")
                
                # Step 1: Search current events
                self.update_state(
                    state="PROGRESS",
                    meta={"current": 1, "total": 4, "status": "Searching current events..."}
                )
                
                events = await search_current_events(idea.title)
                
                # Step 2: Find relevant sources
                self.update_state(
                    state="PROGRESS",
                    meta={"current": 2, "total": 4, "status": "Finding relevant sources..."}
                )
                
                sources = await find_relevant_sources(idea.title, events)
                
                # Step 3: Generate research outline
                self.update_state(
                    state="PROGRESS",
                    meta={"current": 3, "total": 4, "status": "Generating research outline..."}
                )
                
                outline = await generate_research_outline(idea.title, events, sources)
                
                # Step 4: Update research record
                self.update_state(
                    state="PROGRESS",
                    meta={"current": 4, "total": 4, "status": "Finalizing research..."}
                )
                
                # Extract key findings from events
                key_findings = [event["summary"] for event in events[:5]]
                
                # Update research record
                research.key_findings = key_findings
                research.outline = outline
                research.sources = sources
                research.source_count = len(sources)
                research.status = "completed"
                research.model_used = settings.openai_model
                research.tokens_used = 0  # TODO: Track actual token usage
                research.research_duration = int(time.time() - start_time)
                
                await db.commit()
                
                # Update idea status
                idea.status = "researched"
                await db.commit()
                
                return {
                    "events_found": len(events),
                    "sources_found": len(sources),
                    "outline_generated": bool(outline)
                }
        
        # Run the async function
        import asyncio
        result = asyncio.run(conduct_research())
        
        # Update final status
        self.update_state(
            state="SUCCESS",
            meta={"current": 4, "total": 4, "status": "Research completed successfully"}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in start_research_for_idea: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
