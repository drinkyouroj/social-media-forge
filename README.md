# Social Media Forge 🚀

An AI-powered social media content generation platform that transforms simple ideas into complete blog posts, images, and social media content.

## 🌟 Features

- **AI-Powered Idea Generation**: Generate 10 unique blog post ideas from a single topic using OpenAI
- **Intelligent Research**: Automated research with current events and reputable sources
- **Content Creation**: AI-generated blog posts using Anthropic's Claude
- **Image Generation**: Create visuals using Freepik's Flux-dev API
- **Social Media Posts**: Generate platform-specific content with hashtags
- **Multi-User Support**: User authentication with configurable personas
- **Progress Tracking**: Real-time updates on content generation pipeline
- **Export & Filtering**: JSON, Markdown, and text exports with advanced filtering

## 🏗️ Architecture

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ Database (PostgreSQL)
                              ↓
                    Job Queue (Celery + Redis)
                              ↓
                    AI Services (OpenAI + Anthropic + Freepik)
```

### Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy, Alembic
- **Database**: PostgreSQL 15+ with JSONB support
- **Cache & Sessions**: Redis
- **Background Jobs**: Celery with Redis broker
- **AI Services**: OpenAI GPT-4o, Anthropic Claude, Freepik Flux-dev
- **Authentication**: Session-based with Redis storage
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- API keys for OpenAI, Anthropic, and Freepik

### 1. Clone and Setup

```bash
git clone <repository-url>
cd social-media-forge
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```bash
# AI API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
FREEPIK_API_KEY=your_freepik_key_here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/forge
REDIS_URL=redis://redis:6379/0

# Security
SESSION_SECRET=your-secret-key-here
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=JustinIsNotReallySocial%789

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Initialize Database

```bash
# Create admin user and initial data
docker-compose exec backend python -m app.scripts.init_db
```

### 5. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
social-media-forge/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── tasks/          # Celery background tasks
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   ├── sessions.py     # Session management
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # Next.js frontend (coming soon)
├── docker/                 # Docker configuration
│   └── postgres/          # Database init scripts
├── app_data/              # Generated content storage
├── docker-compose.yml     # Service orchestration
└── README.md              # This file
```

## 🔧 Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Celery Worker

```bash
# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.celery_app beat --loglevel=info
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh session

### Topics
- `POST /api/v1/topics/` - Create new topic
- `GET /api/v1/topics/` - List topics
- `GET /api/v1/topics/{id}` - Get topic details
- `PUT /api/v1/topics/{id}` - Update topic
- `DELETE /api/v1/topics/{id}` - Delete topic

### Ideas
- `POST /api/v1/topics/{topic_id}/generate-ideas` - Generate ideas for topic
- `GET /api/v1/ideas/` - List ideas with filtering
- `PUT /api/v1/ideas/{id}/approve` - Approve idea
- `PUT /api/v1/ideas/{id}/reject` - Reject idea

### Research
- `POST /api/v1/ideas/{idea_id}/research` - Start research for idea
- `GET /api/v1/research/{id}` - Get research results

### Blog Posts
- `POST /api/v1/ideas/{idea_id}/write-blog` - Generate blog post
- `GET /api/v1/blog-posts/` - List blog posts
- `PUT /api/v1/blog-posts/{id}/approve` - Approve blog post

### Assets & Social
- `POST /api/v1/blog-posts/{id}/generate-images` - Generate images
- `POST /api/v1/blog-posts/{id}/generate-social` - Generate social posts
- `GET /api/v1/assets/` - List generated assets
- `GET /api/v1/social-posts/` - List social posts

### Export
- `GET /api/v1/export/blog-posts` - Export blog posts
- `GET /api/v1/export/ideas` - Export ideas
- `GET /api/v1/export/social-posts` - Export social posts

## 🔄 Content Generation Pipeline

1. **Topic Input** → User provides topic and preferences
2. **Idea Generation** → AI generates 10 unique blog post ideas
3. **User Approval** → User selects ideas to proceed with
4. **Research Phase** → AI researches current events and sources
5. **Outline Creation** → AI creates structured outline
6. **Blog Writing** → AI writes full blog post using research + persona
7. **User Approval** → User reviews and approves blog post
8. **Image Generation** → AI generates visuals using Freepik
9. **Social Creation** → AI creates platform-specific social posts
10. **Content Pool** → All content available for export and use

## 🎭 Personas & Customization

Users can create multiple writing personas with:

- **Writing Style**: Professional, casual, technical, conversational
- **Tone**: Neutral, authoritative, friendly, challenging
- **Content Preferences**: Statistics, examples, case studies, quotes
- **Structure**: Key takeaways, call-to-action, section preferences
- **Target Audience**: General, technical, business, etc.

## 🔍 Source Filtering

The platform includes intelligent source filtering:

- **Whitelist Mode**: Only allow reputable sources (default)
- **Blacklist Mode**: Block unreliable sources
- **Allow All**: Accept any source (use with caution)

Default whitelist includes: BBC, CNN, Reuters, AP News, NY Times, WSJ, FT, TechCrunch, The Verge, Wired

## 📈 Progress Tracking

Real-time progress updates via polling:

- **Task Status**: Pending, processing, completed, failed
- **Progress Bars**: Visual progress indicators
- **Status Messages**: Detailed status updates
- **Error Handling**: Clear error messages and recovery options

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Secure all API keys and secrets
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **SSL/TLS**: Enable HTTPS with proper certificates
5. **Rate Limiting**: Implement API rate limiting
6. **Monitoring**: Add logging and monitoring
7. **Backup**: Regular database backups

### Scaling

- **Horizontal Scaling**: Multiple Celery workers
- **Load Balancing**: Multiple backend instances
- **Caching**: Redis for session and data caching
- **CDN**: For static assets and generated images

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health check endpoint at `/health`

## 🔮 Roadmap

- [ ] Frontend Next.js application
- [ ] Advanced filtering and search
- [ ] Content scheduling
- [ ] Analytics and insights
- [ ] Team collaboration features
- [ ] API rate limiting
- [ ] Webhook support
- [ ] Multi-language support

---

**Built with ❤️ using FastAPI, Next.js, and AI services**
