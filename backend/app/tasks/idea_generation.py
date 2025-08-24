from celery import current_task
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import json
import logging

from ..config import settings
from ..models.topic import Topic
from ..models.idea import Idea
from ..database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)


@current_task.task(bind=True)
def generate_ideas_for_topic(self, topic_id: int):
    """Generate blog post ideas for a given topic using OpenAI"""
    try:
        # Update task status
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 10, "status": "Generating ideas..."}
        )
        
        # Create async database session
        engine = create_async_engine(settings.database_url)
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async def generate_ideas():
            async with AsyncSessionLocal() as db:
                # Get topic
                topic = await db.get(Topic, topic_id)
                if not topic:
                    raise ValueError(f"Topic {topic_id} not found")
                
                # Generate ideas using OpenAI
                ideas = []
                for i in range(10):
                    # Update progress
                    current_task.update_state(
                        state="PROGRESS",
                        meta={"current": i + 1, "total": 10, "status": f"Generating idea {i + 1}/10..."}
                    )
                    
                    # Create prompt for idea generation
                    prompt = f"""
                    Generate a unique blog post idea for the topic: "{topic.title}"
                    
                    Topic description: {topic.description or 'No description provided'}
                    Target audience: {topic.target_audience or 'General audience'}
                    Category: {topic.category or 'General'}
                    
                    Requirements:
                    1. Create a compelling, unique angle on this topic
                    2. Tie it to current events or trends if possible
                    3. Make it thought-provoking and engaging
                    4. Include a clear title and description
                    
                    Format your response as JSON:
                    {{
                        "title": "Compelling Blog Post Title",
                        "description": "Detailed description of the blog post idea",
                        "angle": "The unique take or perspective on this topic",
                        "current_event_hook": "How this relates to current events or trends"
                    }}
                    """
                    
                    try:
                        response = await openai_client.chat.completions.create(
                            model=settings.openai_model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.8,
                            max_tokens=500
                        )
                        
                        # Parse response
                        content = response.choices[0].message.content
                        idea_data = json.loads(content)
                        
                        # Create idea record
                        idea = Idea(
                            topic_id=topic_id,
                            user_id=topic.user_id,
                            title=idea_data["title"],
                            description=idea_data["description"],
                            angle=idea_data["angle"],
                            current_event_hook=idea_data["current_event_hook"],
                            prompt_used=prompt,
                            model_used=settings.openai_model,
                            tokens_used=response.usage.total_tokens,
                            status="generated"
                        )
                        
                        db.add(idea)
                        ideas.append(idea)
                        
                    except Exception as e:
                        logger.error(f"Error generating idea {i + 1}: {str(e)}")
                        continue
                
                # Commit all ideas
                await db.commit()
                
                # Update topic status
                topic.status = "completed"
                await db.commit()
                
                return len(ideas)
        
        # Run the async function
        import asyncio
        result = asyncio.run(generate_ideas())
        
        # Update final status
        self.update_state(
            state="SUCCESS",
            meta={"current": 10, "total": 10, "status": f"Successfully generated {result} ideas"}
        )
        
        return {"status": "success", "ideas_generated": result}
        
    except Exception as e:
        logger.error(f"Error in generate_ideas_for_topic: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
