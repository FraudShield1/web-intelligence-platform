# Web Intelligence Platform - Complete Build Guide
## From Zero to Production-Ready System

---

## WHAT YOU HAVE

You now have a **complete, enterprise-grade documentation and technical specification** for building the Web Intelligence Platform. Here's what exists:

### Documentation Files
1. **prd.md** — Product requirements and objectives
2. **System Architecture & Design Doc.md** — High-level architecture
3. **Data Model & Schema Doc.md** — Database schema overview
4. **LLM & Prompt Strategy Doc.md** — Initial LLM approach
5. **Dashboard & Analytics Specifications .md** — UI/UX requirements
6. **Operations & Monitoring Doc .md** — Operational procedures
7. **Roadmap & Milestones Doc .md** — Project timeline

### NEW Implementation Files (Created Today)
1. **IMPLEMENTATION.md** — Complete technical blueprint with code examples
2. **API_SPEC.md** — Full REST API specification (OpenAPI 3.0)
3. **DATABASE.sql** — Complete PostgreSQL schema (ready to run)
4. **PROMPTS.md** — Comprehensive LLM prompt library
5. **backend_setup.py** — Backend starter code and patterns
6. **FRONTEND_SETUP.md** — React frontend architecture guide
7. **IMPLEMENTATION_ROADMAP.md** — Week-by-week execution plan
8. **BUILD_GUIDE.md** — This file

---

## QUICK START: NEXT 72 HOURS

### Day 1: Project Setup

**Hour 1-2: Repository & Infrastructure**
```bash
# 1. Create project directories
mkdir -p web-intelligence-platform/{backend,frontend,workers,docs,k8s,scripts}
cd web-intelligence-platform

# 2. Initialize git
git init
echo "# Web Intelligence Platform" > README.md

# 3. Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
node_modules/
.env
.env.local
.DS_Store
venv/
build/
dist/
*.db
.vscode/
EOF

# 4. Copy documentation
cp /path/to/docs/* docs/

# 5. Create .env template
cp backend_setup.py backend/.env.example
```

**Hour 3-4: Database Setup**
```bash
# 1. Run PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_USER=wip \
  -e POSTGRES_PASSWORD=dev123 \
  -e POSTGRES_DB=web_intelligence \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# 2. Wait 10 seconds for startup
sleep 10

# 3. Create schema
psql -U wip -d web_intelligence -h localhost < DATABASE.sql

# 4. Verify
psql -U wip -d web_intelligence -h localhost -c "SELECT COUNT(*) FROM sites;"
```

**Hour 5-6: Backend Skeleton**
```bash
# 1. Navigate to backend
cd backend

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install FastAPI
pip install fastapi uvicorn sqlalchemy asyncpg pydantic python-dotenv

# 4. Create app structure
mkdir -p app/{api/v1,models,schemas,services,workers,middleware,utils}
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/database.py

# 5. Copy code from backend_setup.py into respective files
# (Follow patterns from IMPLEMENTATION.md)

# 6. Test API start
uvicorn app.main:app --reload
# Should see: Uvicorn running on http://127.0.0.1:8000
```

**Hour 7-8: Frontend Setup**
```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Create React app
npx create-react-app . --template typescript

# 3. Install dependencies
npm install react-router-dom axios @reduxjs/toolkit react-redux recharts

# 4. Create structure
mkdir -p src/{components/{pages,common},services,store/slices,hooks,types,utils}

# 5. Configure tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 6. Test frontend start
npm start
# Should open http://localhost:3000
```

**End of Day 1 Checkpoint:**
- [ ] Git repository created
- [ ] PostgreSQL running with schema
- [ ] Backend API starts without errors
- [ ] Frontend React app loads
- [ ] Can access API docs at localhost:8000/docs

---

### Day 2: Core Functionality

**Morning (4 hours): Implement Basic Sites API**

```python
# backend/app/models/site.py
from sqlalchemy import Column, String, Float, DateTime, UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"
    site_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default='pending')
    complexity_score = Column(Float)
    business_value_score = Column(Float)
    created_at = Column(DateTime, default=__import__('datetime').datetime.utcnow)
```

```python
# backend/app/api/v1/sites.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteResponse

router = APIRouter(prefix="/sites")

@router.post("", response_model=SiteResponse, status_code=201)
async def create_site(site_data: SiteCreate, db: AsyncSession = Depends(get_db)):
    db_site = Site(**site_data.dict())
    db.add(db_site)
    await db.commit()
    await db.refresh(db_site)
    return db_site

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(site_id: str, db: AsyncSession = Depends(get_db)):
    site = await db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site
```

**Afternoon (4 hours): Frontend Sites Component**

```typescript
// frontend/src/pages/Sites.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export const Sites = () => {
  const [sites, setSites] = useState([]);
  const [domain, setDomain] = useState('');

  const fetchSites = async () => {
    const response = await axios.get('/api/v1/sites');
    setSites(response.data.sites);
  };

  const addSite = async () => {
    await axios.post('/api/v1/sites', { domain });
    setDomain('');
    fetchSites();
  };

  useEffect(() => {
    fetchSites();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Sites</h1>
      
      <div className="mb-6">
        <input 
          type="text"
          placeholder="Enter domain"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          className="border px-4 py-2 rounded"
        />
        <button 
          onClick={addSite}
          className="bg-blue-600 text-white px-4 py-2 rounded ml-2"
        >
          Add Site
        </button>
      </div>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">Domain</th>
            <th className="border p-2">Status</th>
            <th className="border p-2">Score</th>
          </tr>
        </thead>
        <tbody>
          {sites.map(site => (
            <tr key={site.site_id}>
              <td className="border p-2">{site.domain}</td>
              <td className="border p-2">{site.status}</td>
              <td className="border p-2">{site.complexity_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**End of Day 2 Checkpoint:**
- [ ] Can create sites via API
- [ ] Can list sites via API
- [ ] Can create sites from frontend
- [ ] Sites show in frontend table
- [ ] Data persists in database

---

### Day 3: Worker & Job System

**Morning (4 hours): Job Queue System**

```python
# backend/app/services/queue_service.py
import json
import aio_pika
from app.config import settings

class QueueService:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
    
    async def enqueue_job(self, queue_name: str, job_data: dict):
        exchange = await self.channel.declare_exchange('discovery', aio_pika.ExchangeType.TOPIC)
        await exchange.publish(
            aio_pika.Message(body=json.dumps(job_data).encode()),
            routing_key=f'jobs.{queue_name}'
        )
    
    async def consume_jobs(self, queue_name: str):
        exchange = await self.channel.declare_exchange('discovery', aio_pika.ExchangeType.TOPIC)
        queue = await self.channel.declare_queue(f'{queue_name}_queue')
        await queue.bind(exchange, f'jobs.{queue_name}')
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                yield json.loads(message.body)
                await message.ack()
```

```python
# backend/workers/fingerprinter_worker.py
import asyncio
import httpx
from bs4 import BeautifulSoup

class FingerprinterWorker:
    async def process_job(self, job_data):
        domain = job_data['domain']
        
        try:
            # Fetch homepage
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://{domain}", timeout=30)
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Detect technology
            result = {
                'cms': self._detect_cms(html),
                'js_frameworks': self._detect_js(html),
                'has_api': self._check_api(html),
                'status': 'success'
            }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}
    
    def _detect_cms(self, html):
        if 'Shopify' in html:
            return 'shopify'
        if 'magento' in html.lower():
            return 'magento'
        return 'custom'
    
    def _detect_js(self, html):
        frameworks = []
        if 'react' in html.lower():
            frameworks.append('react')
        if 'vue' in html.lower():
            frameworks.append('vue')
        return frameworks
    
    def _check_api(self, html):
        return '/api' in html or 'graphql' in html.lower()
```

**Afternoon (4 hours): Job Endpoints & Frontend**

```python
# backend/app/api/v1/jobs.py
from fastapi import APIRouter
from app.models.job import Job

router = APIRouter(prefix="/jobs")

@router.post("", status_code=201)
async def create_job(job_data: JobCreate, db: AsyncSession = Depends(get_db)):
    # Create job record
    db_job = Job(**job_data.dict())
    db.add(db_job)
    await db.commit()
    
    # Enqueue to RabbitMQ
    await queue_service.enqueue_job('fingerprint', {
        'job_id': str(db_job.job_id),
        'site_id': str(job_data.site_id),
        'domain': job_data.domain
    })
    
    return JobResponse.from_orm(db_job)

@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404)
    return JobResponse.from_orm(job)
```

```typescript
// frontend/src/pages/Jobs.tsx
import { useEffect, useState } from 'react';
import axios from 'axios';

export const Jobs = () => {
  const [jobs, setJobs] = useState([]);

  const fetchJobs = async () => {
    const response = await axios.get('/api/v1/jobs');
    setJobs(response.data.jobs);
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Active Jobs</h1>
      
      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.job_id} className="border rounded p-4 bg-white">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold">{job.job_type}</h3>
                <p className="text-sm text-gray-600">{job.site_id}</p>
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded text-white ${
                  job.status === 'running' ? 'bg-blue-500' :
                  job.status === 'success' ? 'bg-green-500' :
                  'bg-red-500'
                }`}>
                  {job.status}
                </span>
                <p className="text-sm">{job.created_at}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

**End of Day 3 Checkpoint:**
- [ ] RabbitMQ connected and working
- [ ] Can create jobs from API
- [ ] Jobs stored in database
- [ ] Can consume jobs from queue
- [ ] Job status visible in frontend
- [ ] Jobs update in real-time

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│              http://localhost:3000                           │
│  Dashboard | Sites | Jobs | Analytics | Settings            │
└────────────────────────┬────────────────────────────────────┘
                         │ (HTTP/REST)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Gateway                               │
│              FastAPI - Port 8000                             │
│  GET/POST/PUT/DELETE /api/v1/{resource}                     │
└────────┬────────────────┬──────────────┬─────────────────────┘
         │                │              │
    [Auth]           [Services]      [Queue]
         │                │              │
    ┌────▼────────┬──────▼───────┬─────▼─────────┐
    │             │              │               │
 PostgreSQL   Redis Cache    RabbitMQ        External
 Database     Session Store   Job Queue      APIs (LLM)
    │             │              │               │
    └─────────────┴──────────────┴───────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    Workers (async)                            │
│                                                              │
│  Fingerprinter   →  Browser Worker  →  Static Crawler      │
│  (Tech detect)      (JS rendering)      (HTML parsing)      │
│  Updates DB         Captures Network    Generates           │
│                     Traces              Selectors            │
│                                                              │
│  All invoke LLM Service for intelligence generation          │
└──────────────────────────────────────────────────────────────┘
```

---

## DATA FLOW EXAMPLE

```
User visits frontend http://localhost:3000
       │
       ├─> Clicks "Add New Site"
       │   └─> Frontend sends POST /api/v1/sites {domain: "example.com"}
       │       └─> Backend creates Site record in DB
       │           └─> Backend enqueues fingerprint job to RabbitMQ
       │
       └─> Watches Jobs page (polls every 5 sec)
           └─> Frontend polls GET /api/v1/jobs
               └─> Shows "Queued" then "Running"
                   
Fingerprinter worker picks up job from RabbitMQ
       │
       ├─> Fetches homepage: https://example.com
       │   └─> Detects CMS (Shopify, Magento, etc.)
       │   └─> Detects JS frameworks
       │   └─> Checks for API endpoints
       │
       ├─> Updates Job status to "success" in DB
       │   └─> Frontend shows green checkmark
       │
       └─> Next phase: Browser Worker or Static Crawler
           └─> Calls LLM to extract categories & selectors
               └─> Stores blueprint in DB
                   └─> Frontend shows blueprint details
```

---

## CONFIGURATION FILES

### .env Template
```bash
# Backend
DEBUG=False
DATABASE_URL=postgresql://wip:dev123@localhost:5432/web_intelligence
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# LLM
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Auth
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://wip:dev123@postgres:5432/web_intelligence
    depends_on: [postgres, redis, rabbitmq]
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: wip
      POSTGRES_PASSWORD: dev123
      POSTGRES_DB: web_intelligence
    volumes: [postgres_data:/var/lib/postgresql/data]
    ports: ["5432:5432"]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports: ["5672:5672", "15672:15672"]
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      REACT_APP_API_URL: http://localhost:8000/api/v1

volumes:
  postgres_data:
```

---

## TESTING YOUR SETUP

### Health Checks
```bash
# API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Database
psql -U wip -d web_intelligence -h localhost -c "SELECT COUNT(*) FROM sites;"

# Redis
redis-cli ping

# RabbitMQ
curl http://localhost:15672 (use guest/guest)
```

### Full End-to-End Test
```bash
# 1. Add a site
curl -X POST http://localhost:8000/api/v1/sites \
  -H "Content-Type: application/json" \
  -d '{"domain": "shopify-example.myshopify.com"}'

# Response:
# {
#   "site_id": "abc123...",
#   "domain": "shopify-example.myshopify.com",
#   "status": "pending",
#   "created_at": "2024-01-15T10:00:00Z"
# }

# 2. List sites
curl http://localhost:8000/api/v1/sites

# 3. Check jobs
curl http://localhost:8000/api/v1/jobs

# 4. In frontend, watch the Jobs page refresh
```

---

## NEXT STEPS AFTER SETUP

### Week 1 Tasks
1. ✅ Get everything running locally
2. ✅ Add more sites for testing
3. ✅ Implement fingerprinter worker fully
4. ✅ Add database indexes for performance
5. ✅ Set up logging and error handling

### Week 2 Tasks
1. Implement browser worker with Playwright
2. Add LLM integration (Claude API)
3. Create selector generation
4. Build analytics dashboard
5. Add authentication

### Week 3-4 Tasks
1. Implement all blueprint operations
2. Create advanced analytics
3. Add template system
4. Deploy to staging
5. Begin load testing

---

## DEPLOYMENT READINESS CHECKLIST

- [ ] All unit tests passing
- [ ] Integration tests working
- [ ] Environment variables documented
- [ ] Database migrations automated
- [ ] Logging configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Error handling complete
- [ ] Security review done
- [ ] Performance tested
- [ ] Disaster recovery plan

---

## COMMON ISSUES & FIXES

### "Cannot connect to PostgreSQL"
```bash
docker ps | grep postgres
docker logs <container_id>
# Ensure container is running and port 5432 open
```

### "RabbitMQ connection refused"
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### "ModuleNotFoundError"
```bash
# Activate venv
source backend/venv/bin/activate
pip install -r requirements.txt
```

### "CORS errors in frontend"
```python
# Add to FastAPI app
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## WHERE TO GO FROM HERE

1. **Read IMPLEMENTATION_ROADMAP.md** for week-by-week plan
2. **Check IMPLEMENTATION.md** for code patterns and examples
3. **Review PROMPTS.md** for LLM prompt templates
4. **Follow API_SPEC.md** for endpoint definitions
5. **Consult DATABASE.sql** for schema details

---

## SUPPORT RESOURCES

- FastAPI docs: https://fastapi.tiangolo.com/
- React docs: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Anthropic Claude: https://console.anthropic.com/

---

## SUCCESS CRITERIA

By end of Day 3, you should have:
- ✅ Database schema initialized
- ✅ API endpoints responding
- ✅ Frontend showing data
- ✅ Jobs being queued and processed
- ✅ Real-time updates working

This is the **minimum viable setup** to begin the development cycle. From here, you expand feature by feature following the IMPLEMENTATION_ROADMAP.

**You are now ready to build.** 🚀


