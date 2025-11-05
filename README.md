# 🌐 Web Intelligence Platform

**Intelligent discovery and scoring of website extraction surfaces for LLM-driven scrapers.**

## Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone & Navigate
```bash
cd /Users/naouri/Downloads/Web\ Intelligence\ Platform
```

### 2. Start Services
```bash
docker-compose up --build
```

This will:
- ✅ Start PostgreSQL database
- ✅ Start Redis cache
- ✅ Start RabbitMQ queue
- ✅ Start FastAPI backend (http://localhost:8000)
- ✅ Start React frontend (http://localhost:3000)

### 3. Access the Platform

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ**: http://localhost:15672 (guest/guest)

## Development Setup (Local)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL, Redis, RabbitMQ (or use docker-compose for those only)
# Then:
uvicorn app.main:app --reload
```

API will be at: http://localhost:8000
Docs at: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm start
```

App will open at: http://localhost:3000

## Architecture

```
Frontend (React)
    ↓
API Gateway (FastAPI)
    ↓
├── Sites Service
├── Jobs Service
├── Blueprints Service
├── Analytics Service
    ↓
Database (PostgreSQL)
Cache (Redis)
Queue (RabbitMQ)
```

## API Endpoints

### Sites
- `POST /api/v1/sites` - Create site
- `GET /api/v1/sites` - List sites
- `GET /api/v1/sites/{site_id}` - Get site
- `PUT /api/v1/sites/{site_id}` - Update site
- `DELETE /api/v1/sites/{site_id}` - Delete site

### Jobs
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs` - List jobs
- `GET /api/v1/jobs/{job_id}` - Get job
- `POST /api/v1/jobs/{job_id}/cancel` - Cancel job
- `POST /api/v1/jobs/{job_id}/retry` - Retry job

### Blueprints
- `GET /api/v1/blueprints/sites/{site_id}/latest` - Get latest
- `GET /api/v1/blueprints/{blueprint_id}` - Get blueprint
- `GET /api/v1/blueprints/sites/{site_id}/versions` - List versions
- `POST /api/v1/blueprints/{blueprint_id}/rollback` - Rollback
- `GET /api/v1/blueprints/{blueprint_id}/export` - Export

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/sites/{site_id}/metrics` - Site metrics
- `GET /api/v1/analytics/methods/performance` - Method comparison

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routes_sites.py      # Sites endpoints
│   │   ├── routes_jobs.py       # Jobs endpoints
│   │   ├── routes_blueprints.py # Blueprints endpoints
│   │   └── routes_analytics.py  # Analytics endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── index.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Sites.tsx
│   │   │   ├── Jobs.tsx
│   │   │   └── Analytics.tsx
│   │   └── components/
│   │       ├── Navbar.tsx
│   │       └── Sidebar.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── DATABASE.sql
├── docs/
└── README.md
```

## Features

### Sites Management
- Add new websites for analysis
- View site fingerprints (CMS, framework, JS)
- Track discovery status
- Filter by platform/status

### Jobs System
- Real-time job monitoring
- Queue management
- Auto-retry on failure
- Cancel running jobs

### Blueprints
- Version control
- Category/endpoint extraction
- Selector generation
- Rollback support

### Analytics
- Discovery metrics
- Success rate tracking
- Method performance comparison
- Cost analysis

### Dashboard
- Overview metrics
- Real-time updates
- Status distribution
- Quality insights

## Next Steps

1. **Add Sites** - Click "Add Site" on Sites page
2. **Create Jobs** - Jobs will appear as sites are processed
3. **Monitor Progress** - Watch real-time updates on Jobs page
4. **Review Results** - Check blueprints and analytics

## Configuration

Set environment variables in `.env`:

```
DATABASE_URL=postgresql+asyncpg://wip:password@localhost:5432/web_intelligence
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
DEBUG=False
```

## Documentation

- `BUILD_GUIDE.md` - Setup guide
- `API_SPEC.md` - Full API documentation
- `IMPLEMENTATION.md` - Technical architecture
- `PROMPTS.md` - LLM prompt templates
- `/docs` - Project documentation

## Development Commands

### Backend
```bash
# Format
black app/

# Lint
flake8 app/

# Test
pytest

# Database
python -c "from app.database import init_db; await init_db()"
```

### Frontend
```bash
# Build
npm run build

# Test
npm test

# Eject (WARNING: irreversible)
npm eject
```

## Troubleshooting

### Database connection error
```bash
docker-compose down
docker-compose up --build
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or kill existing process:
lsof -ti:8000 | xargs kill -9
```

### Frontend not updating
```bash
rm -rf frontend/node_modules frontend/build
npm install
npm start
```

## Status

- ✅ Backend API fully implemented
- ✅ Frontend dashboard complete
- ✅ Database schema ready
- ✅ Docker setup ready
- ⏳ LLM integration (ready to add)
- ⏳ Workers (fingerprinter, browser, static)

## License

Proprietary - Web Intelligence Platform

## Support

See documentation in `/docs` directory.

---

**Ready to build intelligent scrapers?** 🚀

Start with the dashboard: http://localhost:3000

