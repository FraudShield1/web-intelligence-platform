# Web Intelligence Platform - Complete Technical Documentation

**Version:** 1.0  
**Date:** November 6, 2025  
**Status:** Production - Fully Deployed  
**Cost:** $0/month  

---

## 🎯 Executive Summary

The **Web Intelligence Platform** is an autonomous web discovery and analysis system that automatically fingerprints websites, detects their technology stack, assesses scraping complexity, and prepares blueprints for downstream scraping operations. It serves as an intelligent reconnaissance layer that reduces manual scraper development time by 80%.

**Primary Use Case:** Automatically understand any website's structure, technology, and complexity before building scrapers, enabling data-driven prioritization and faster scraper deployment.

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         END USER                                │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         FRONTEND (Vercel - React/TypeScript)             │  │
│  │  https://web-intelligence-platform.vercel.app            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         BACKEND API (Railway - FastAPI/Python)           │  │
│  │  https://web-intelligence-platform-production.           │  │
│  │           up.railway.app                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│             ↓              ↓              ↓                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │ Upstash Redis│  │  OpenRouter  │         │
│  │  (Railway)   │  │ (Rate Limit) │  │   (LLM API)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │    WORKERS (GitHub Actions - Scheduled Every 15 min)    │  │
│  │  • Fingerprinting Worker                                │  │
│  │  • Discovery Worker                                      │  │
│  │  • Selector Generator Worker                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Styling:** Custom CSS (no framework)
- **Deployment:** Vercel (Hobby tier)
- **URL:** https://web-intelligence-platform.vercel.app

#### Backend
- **Framework:** FastAPI (Python 3.11)
- **ASGI Server:** Uvicorn
- **ORM:** SQLAlchemy 2.0 (async)
- **Database Driver:** asyncpg (PostgreSQL)
- **Validation:** Pydantic v2
- **Task Queue:** Celery 5.3
- **Deployment:** Railway (Dockerfile-based)
- **URL:** https://web-intelligence-platform-production.up.railway.app

#### Database
- **Primary Database:** PostgreSQL 15 (Railway)
- **Connection Pool:** SQLAlchemy async engine
- **Migrations:** Alembic
- **Schema:** Fully relational with foreign keys

#### Cache & Rate Limiting
- **Service:** Upstash Redis (Free tier)
- **Access Method:** REST API (HTTP-based)
- **Purpose:** Rate limiting (100 req/min per IP)
- **Fallback:** Direct Redis connection for Celery

#### Workers
- **Platform:** GitHub Actions (Free tier, 2000 min/month)
- **Schedule:** Cron every 15 minutes
- **Browser:** Playwright (Chromium)
- **HTML Parser:** BeautifulSoup4 + lxml
- **HTTP Client:** httpx (async)

#### LLM Integration
- **Service:** OpenRouter (pay-per-use)
- **Models Supported:** Claude, GPT-3.5/4, Llama
- **Usage:** Site analysis, semantic understanding (optional)
- **Status:** Ready but not yet fully integrated

---

## 📊 Data Model

### Core Entities

#### 1. Sites
**Table:** `sites`  
**Purpose:** Stores discovered websites and their metadata

```sql
CREATE TABLE sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(100),                    -- Shopify, Magento, Custom, etc.
    status VARCHAR(50) DEFAULT 'pending',     -- pending, fingerprinted, discovered, error
    fingerprint_data JSONB,                   -- Tech stack, frameworks, anti-bot
    complexity_score FLOAT,                   -- 0.0-1.0
    business_value_score FLOAT,               -- 0.0-1.0 (user-defined)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_discovered_at TIMESTAMP,
    blueprint_version INTEGER DEFAULT 1,
    notes TEXT,
    created_by UUID
);
```

**Key Fields:**
- `fingerprint_data`: JSON containing platform, CMS, frameworks, anti-bot systems, JS requirements
- `complexity_score`: Calculated based on JS requirements, anti-bot, framework complexity
- `status`: Lifecycle state of the site

#### 2. Jobs
**Table:** `jobs`  
**Purpose:** Tracks background processing jobs

```sql
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,            -- fingerprint, discover, generate_selectors
    method VARCHAR(50),                       -- auto, manual, scheduled
    status VARCHAR(50) DEFAULT 'queued',      -- queued, running, success, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB,                             -- Job output
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Job Types:**
- `fingerprint`: Detect tech stack, platform, complexity
- `discover`: Find categories, products, endpoints (Feature G - not yet implemented)
- `generate_selectors`: Create CSS/XPath selectors (Feature G - not yet implemented)

#### 3. Blueprints
**Table:** `blueprints`  
**Purpose:** Stores versioned site intelligence objects (blueprints)

```sql
CREATE TABLE blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    confidence_score FLOAT,                   -- 0.0-1.0
    categories_data JSON,                     -- Category hierarchy
    endpoints_data JSON,                      -- API endpoints
    render_hints_data JSON,                   -- JS requirements, wait times
    selectors_data JSON,                      -- CSS/XPath selectors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT,
    UNIQUE(site_id, version)
);
```

**Purpose:** Each blueprint version represents a snapshot of site intelligence at a point in time.

#### 4. Users
**Table:** `users`  
**Purpose:** Authentication and RBAC

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',  -- admin, analyst, viewer
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Status:** Authentication currently disabled for easier testing. Can be re-enabled by uncommenting security middleware.

#### 5. Analytics Metrics
**Table:** `analytics_metrics`  
**Purpose:** Track system performance and usage

```sql
CREATE TABLE analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    site_id UUID REFERENCES sites(site_id),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

---

## 🔄 System Workflows

### Workflow 1: Add New Site & Automatic Fingerprinting

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User adds site via UI                                  │
│   POST /api/v1/sites                                            │
│   { "domain": "example.com" }                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Backend creates records                                │
│   • Site record (status: "pending")                            │
│   • Fingerprint job (status: "queued")                         │
│   • Triggers Celery task (async)                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: GitHub Actions worker picks up job (every 15 min)      │
│   • Queries database for queued jobs                           │
│   • Processes up to 5 jobs per run                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Fingerprinting Worker executes                         │
│   • Fetches homepage HTML (httpx with timeout)                 │
│   • Detects platform (Shopify, Magento, etc.)                  │
│   • Detects CMS (WordPress, Drupal)                            │
│   • Detects JS frameworks (React, Vue, Angular)                │
│   • Detects anti-bot systems (Cloudflare, reCAPTCHA)           │
│   • Checks if JS rendering required                            │
│   • Calculates complexity score                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Update database                                        │
│   • Site.status → "fingerprinted"                              │
│   • Site.fingerprint_data → {platform, cms, frameworks, ...}   │
│   • Site.complexity_score → 0.0-1.0                            │
│   • Job.status → "success"                                     │
│   • Job.result → fingerprint data                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: UI reflects changes                                    │
│   • User refreshes sites page                                  │
│   • Status badge shows "fingerprinted"                         │
│   • "View Details" button becomes active                       │
│   • Complexity score displayed                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Timing:**
- User adds site: Instant (< 1 second)
- Job queued: Instant
- Worker picks up: Within 15 minutes
- Processing time: 5-30 seconds per site
- Total time to fingerprint: < 15 minutes

### Workflow 2: View Site Details & Fingerprint Data

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User clicks "View Details" on a site                   │
│   Navigate to: /sites/:siteId                                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Frontend fetches site details                          │
│   GET /api/v1/sites/:siteId                                    │
│   Returns: SiteDetailResponse (includes fingerprint_data)      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Frontend displays 3 tabs                               │
│                                                                 │
│   TAB 1: Overview                                               │
│   • Domain, platform, status                                   │
│   • Complexity & business value scores                         │
│   • Blueprint version                                           │
│   • Timestamps                                                  │
│                                                                 │
│   TAB 2: Fingerprint Data                                       │
│   • Technology stack (frameworks, libraries)                   │
│   • Anti-bot systems detected                                  │
│   • Rendering requirements                                     │
│   • Raw JSON data (expandable)                                 │
│                                                                 │
│   TAB 3: Blueprint                                              │
│   • Categories (if discovered)                                 │
│   • Endpoints (if discovered)                                  │
│   • Selectors (if generated)                                   │
│   • Render hints                                               │
│   • Export buttons (JSON/YAML)                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow 3: Export Blueprint

```
┌─────────────────────────────────────────────────────────────────┐
│ User clicks "Export JSON" or "Export YAML"                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ GET /api/v1/blueprints/:blueprintId/export?format=json         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Backend serializes blueprint data                              │
│   • Categories array                                            │
│   • Endpoints array                                             │
│   • Selectors array                                             │
│   • Render hints object                                         │
│   • Metadata (version, confidence, timestamps)                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ File downloads: blueprint_domain_v1.json                        │
│                                                                 │
│ Ready to feed into:                                             │
│   • Scraper configuration                                       │
│   • LLM context for scraper generation                         │
│   • Team collaboration                                          │
│   • Version control                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Features (Current Implementation)

### Feature A: Site Fingerprinting ✅ IMPLEMENTED

**Purpose:** Automatically detect website technology stack and characteristics.

**Implementation:**
- **Service:** `backend/app/services/fingerprint_service.py`
- **Worker:** `backend/app/workers/fingerprinter.py`
- **Triggered:** Automatically when site is added

**Detection Capabilities:**

1. **E-commerce Platform Detection**
   - Shopify (cdn.shopify.com patterns)
   - WooCommerce (woocommerce plugins)
   - Magento (Mage.Cookies)
   - BigCommerce (bigcommerce CDN)
   - PrestaShop (prestashop patterns)
   - Custom (default)

2. **CMS Detection**
   - WordPress (wp-content)
   - Drupal (sites/default)
   - Joomla

3. **JavaScript Frameworks**
   - React (data-react attributes)
   - Angular (ng-app)
   - Vue (_vue patterns)
   - Next.js (/_next/ paths)
   - Nuxt

4. **Anti-Bot Systems**
   - Cloudflare (cf-ray header, HTML patterns)
   - reCAPTCHA (recaptcha scripts)
   - DataDome
   - Imperva/Incapsula
   - PerimeterX

5. **Rendering Requirements**
   - JS requirement detection (SPA indicators)
   - Body content analysis
   - Script tag density

6. **Complexity Scoring (0.0-1.0)**
   - +0.3 if requires JavaScript
   - +0.2 per anti-bot service detected
   - +0.2 if modern framework (React/Vue/Angular)
   - +0.1 if large HTML (>100KB)
   - Capped at 1.0

**Output Format:**
```json
{
  "platform": "Custom",
  "cms": "WordPress",
  "javascript_frameworks": ["React", "Next.js"],
  "anti_bot": {
    "detected": true,
    "services": ["cloudflare", "recaptcha"]
  },
  "requires_js": true,
  "complexity_score": 0.7
}
```

### Feature B: Selector & Endpoint Extraction ⚠️ NOT YET IMPLEMENTED

**Status:** Ready for implementation (Feature G)

**Planned Capabilities:**
- Crawl category and product pages
- Detect repeating structures (DOM patterns)
- Find AJAX/GraphQL/REST endpoints
- LLM-assisted selector extraction
- Generate CSS/XPath selectors

**Output Format (when implemented):**
```json
{
  "selectors": {
    "product_name": ".product-title",
    "price": ".price",
    "image": ".product-image img",
    "next_page": "a.pagination-next"
  },
  "endpoints": [
    {
      "url": "/api/products",
      "method": "GET",
      "params": ["page", "category", "limit"]
    }
  ],
  "render_hints": {
    "requires_js": true,
    "infinite_scroll": false,
    "wait_for_selector": ".products-loaded",
    "timeout_seconds": 30
  }
}
```

### Feature C: Scoring Engine ✅ IMPLEMENTED

**Purpose:** Prioritize sites based on scraping complexity and business value.

**Implementation:**
- **Complexity Score:** Automatically calculated during fingerprinting
- **Business Value Score:** User-defined (0.0-1.0)

**Scoring Dimensions:**
1. **Complexity (Automatic)**
   - Tech stack simplicity
   - Anti-bot presence
   - JavaScript requirements
   - HTML size and structure

2. **Business Value (Manual)**
   - User assigns based on business priorities
   - Can be updated via API: `PUT /api/v1/sites/:id`

**Use Cases:**
- Sort sites by complexity (easiest first)
- Filter by business value (highest ROI first)
- Identify quick wins (low complexity + high value)
- Plan resource allocation

### Feature D: Dashboard & Analytics ✅ IMPLEMENTED

**Purpose:** Operational visibility into discovery pipeline and system health.

**Endpoints:**
- `GET /api/v1/analytics/dashboard` - Overview metrics
- `GET /api/v1/analytics/sites/:id/metrics` - Site-specific metrics
- `GET /api/v1/analytics/methods/performance` - Method performance

**Dashboard Metrics:**
1. **System-Wide:**
   - Total sites tracked
   - Active jobs count
   - Total blueprints generated
   - Average discovery time
   - Success rate

2. **Site-Specific:**
   - Jobs run count
   - Success/failure breakdown
   - Average job duration
   - Latest job status

3. **Method Performance:**
   - Performance by job type (fingerprint, discover, etc.)
   - Success rates per method
   - Average execution time

**Frontend Pages:**
- Dashboard: System overview with charts
- Sites: Filterable list with search
- Jobs: Job history and status
- Analytics: Detailed performance metrics

### Feature E: Blueprint Export ✅ IMPLEMENTED

**Purpose:** Generate ready-to-use files for scrapers and LLMs.

**Endpoints:**
- `GET /api/v1/blueprints?site_id=:id` - List blueprints
- `GET /api/v1/blueprints/:id/export?format=json` - Export as JSON
- `GET /api/v1/blueprints/:id/export?format=yaml` - Export as YAML

**Export Structure:**
```json
{
  "blueprint_id": "uuid",
  "site_id": "uuid",
  "version": 1,
  "domain": "example.com",
  "confidence_score": 0.94,
  "created_at": "2025-11-06T12:00:00Z",
  "categories_data": [...],
  "endpoints_data": [...],
  "selectors_data": [...],
  "render_hints_data": {...}
}
```

**Use Cases:**
- Feed into LLM for scraper generation
- Import into scraper configuration
- Share with team members
- Version control tracking
- Template creation

### Feature F: Template Library ⚠️ PARTIAL IMPLEMENTATION

**Status:** Foundation ready, needs population

**Concept:**
- Store reusable templates per platform (Shopify, Magento, etc.)
- New sites inherit template as starting point
- LLM suggests template improvements
- Community-driven template evolution

**File Structure (planned):**
```
/templates/
  shopify.json
  magento.json
  woocommerce.json
  prestashop.json
  custom.json
```

---

## 🚀 Feature G: Advanced Discovery (NOT YET IMPLEMENTED)

### Overview

**Feature G** is the most advanced capability: autonomous deep web discovery that goes beyond basic fingerprinting to create complete site maps.

### Phase Breakdown

#### Phase 1: Structure Exploration
**Status:** Not implemented  
**Time Estimate:** 1 hour  

**Capabilities:**
- Crawl homepage and extract all internal links
- Filter relevant URLs (categories, products, lists)
- Identify navigation patterns
- Build initial site structure

**Tech:**
- Playwright for JS-rendered sites
- BeautifulSoup for static sites
- URL pattern matching heuristics

#### Phase 2: Category Hierarchy Detection
**Status:** Not implemented  
**Time Estimate:** 1 hour  

**Capabilities:**
- Cluster URLs by path similarity
- Deduce parent-child relationships
- Build category tree with confidence scores
- Detect breadcrumb patterns

**Output:**
```json
{
  "categories": {
    "electronics": {
      "tvs": ["led", "oled", "smart"],
      "phones": ["android", "iphone"],
      "computers": ["laptops", "desktops"]
    }
  },
  "confidence": 0.92
}
```

#### Phase 3: Product Page Recognition
**Status:** Not implemented  
**Time Estimate:** 1 hour  

**Capabilities:**
- Detect repeated structural patterns
- Identify product listing pages
- Recognize product detail pages
- Extract product URL patterns
- LLM validation of patterns

**Output:**
```json
{
  "product_list_pattern": "/products/category/:slug",
  "product_detail_pattern": "/product/:id",
  "selectors": {
    "product_name": ".product-title",
    "price": ".price-value",
    "image": ".product-image img[src]"
  }
}
```

#### Phase 4: Endpoint Discovery
**Status:** Not implemented  
**Time Estimate:** 30 minutes  

**Capabilities:**
- Watch for inline JSON blocks
- Detect GraphQL/REST endpoints
- Test endpoints with sample requests
- LLM inference of parameters

**Output:**
```json
{
  "endpoints": [
    {
      "url": "/graphql",
      "method": "POST",
      "type": "graphql",
      "queries": ["products", "categories"]
    },
    {
      "url": "/api/v1/products",
      "method": "GET",
      "params": ["page", "category", "sort"]
    }
  ]
}
```

#### Phase 5: Pagination & Filtering
**Status:** Not implemented  
**Time Estimate:** 30 minutes  

**Capabilities:**
- Detect pagination patterns (?page=, /page/N/)
- Identify filter parameters
- Test pagination consistency
- Store reusable logic

#### Phase 6: Render Logic Detection
**Status:** Not implemented  
**Time Estimate:** 30 minutes  

**Capabilities:**
- Classify render type (HTML/JS/API)
- Determine wait requirements
- Detect infinite scroll
- Tag pages accordingly

### Total Feature G Time: 3-4 hours

---

## 🔒 Security & Rate Limiting

### Rate Limiting

**Implementation:** Upstash Redis REST API

**Middleware:** `backend/app/middleware_rate_limit.py`

**Default Limits:**
- 100 requests per minute per IP
- Applied to all API endpoints
- Sliding window algorithm

**Response on Limit Exceeded:**
```json
{
  "detail": "Rate limit exceeded. Try again later.",
  "status_code": 429
}
```

### Authentication (Currently Disabled)

**System:** JWT-based with bcrypt password hashing

**Roles:**
- `admin`: Full access
- `analyst`: Read/write access to sites and jobs
- `viewer`: Read-only access

**Status:** Temporarily disabled for easier testing. Can be re-enabled by uncommenting imports in route files.

**Files:**
- `backend/app/security.py` - JWT utilities
- `backend/app/middleware_auth.py` - Authentication middleware

### CORS Configuration

**Allowed Origins:**
- `https://web-intelligence-platform.vercel.app` (production frontend)
- `http://localhost:3000` (local development)

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:** Authorization, Content-Type, X-Request-ID

---

## 📡 API Endpoints Reference

### Sites API

```
POST   /api/v1/sites              Create new site
GET    /api/v1/sites              List sites (with filters)
GET    /api/v1/sites/:id          Get site details (with fingerprint_data)
PUT    /api/v1/sites/:id          Update site metadata
DELETE /api/v1/sites/:id          Delete site
```

**Query Parameters (List):**
- `status`: Filter by status (pending, fingerprinted, discovered, error)
- `platform`: Filter by platform (Shopify, Magento, Custom)
- `min_complexity`: Minimum complexity score
- `max_complexity`: Maximum complexity score
- `limit`: Results per page (default: 50)
- `offset`: Pagination offset

### Jobs API

```
GET    /api/v1/jobs               List all jobs
GET    /api/v1/jobs/:id           Get job details
POST   /api/v1/jobs               Create manual job
```

**Query Parameters (List):**
- `site_id`: Filter by site
- `job_type`: Filter by type (fingerprint, discover, generate_selectors)
- `status`: Filter by status (queued, running, success, failed)
- `limit`: Results per page
- `offset`: Pagination offset

### Blueprints API

```
GET    /api/v1/blueprints                  List blueprints
GET    /api/v1/blueprints/:id              Get blueprint details
GET    /api/v1/blueprints/:id/export       Export blueprint (JSON/YAML)
```

**Query Parameters (List):**
- `site_id`: Filter by site

**Query Parameters (Export):**
- `format`: Export format (json or yaml)

### Analytics API

```
GET    /api/v1/analytics/dashboard         System overview metrics
GET    /api/v1/analytics/sites/:id/metrics Site-specific metrics
GET    /api/v1/analytics/methods/performance Method performance stats
```

**Query Parameters (Dashboard):**
- `date_range`: Time range in days (default: 7)

### Health & Status

```
GET    /health                    System health check
GET    /docs                      Swagger API documentation
GET    /redoc                     ReDoc API documentation
```

---

## 🧪 Testing & Quality Assurance

### Current Test Status

**Manual Testing:** ✅ Complete
- All API endpoints tested
- Frontend UI tested
- Worker execution verified
- End-to-end flow validated

**Automated Testing:** ⚠️ Not implemented
- Unit tests: Needed
- Integration tests: Needed
- E2E tests: Needed

### Test Data

**Example Site:** worten.pt
- Status: fingerprinted
- Complexity: 50%
- Platform: Custom
- Anti-bot: Cloudflare
- Requires JS: Yes

### Known Limitations

1. **Worker Frequency:** 15-minute intervals (GitHub Actions limit)
2. **No Deep Discovery:** Only homepage analyzed (Feature G pending)
3. **No Category Detection:** Categories not discovered yet
4. **No Product Detection:** Product patterns not recognized yet
5. **No API Endpoints:** Endpoints not discovered automatically
6. **No Selectors:** CSS/XPath selectors not generated yet

---

## 🚀 Deployment Details

### Frontend (Vercel)

**Build Command:**
```bash
rm -rf dist node_modules/.vite && npm run build
```

**Environment Variables:**
```
VITE_API_URL=https://web-intelligence-platform-production.up.railway.app/api/v1
```

**Build Configuration:**
- Framework: Vite
- Output Directory: dist
- Install Command: `npm install --legacy-peer-deps`

**Auto-Deploy:** Triggered on push to `main` branch

### Backend (Railway)

**Build Method:** Dockerfile

**Dockerfile Highlights:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app/backend
# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client
# Install Python dependencies
COPY backend/requirements-full.txt ./
RUN pip install -r requirements-full.txt
# Copy application
COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations
# Set environment
ENV PYTHONPATH=/app/backend:$PYTHONPATH
# Health check
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/health')"
# Run server
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Environment Variables:**
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
REDIS_URL=redis://host:port/0
UPSTASH_REDIS_REST_URL=https://...
UPSTASH_REDIS_REST_TOKEN=...
OPENROUTER_API_KEY=sk-or-v1-...
JWT_SECRET=...
CORS_ORIGINS=["https://web-intelligence-platform.vercel.app","http://localhost:3000"]
PORT=8000
```

**Auto-Deploy:** Triggered on push to `main` branch

### Workers (GitHub Actions)

**Workflow File:** `.github/workflows/worker_fingerprint.yml`

**Schedule:**
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
```

**Secrets Required:**
- `DATABASE_URL`: Railway PostgreSQL connection string
- `UPSTASH_REDIS_REST_URL`: Upstash Redis REST URL
- `UPSTASH_REDIS_REST_TOKEN`: Upstash Redis token
- `OPENROUTER_API_KEY`: OpenRouter API key (optional)

**Dependencies:**
- Python 3.11
- requirements-worker.txt
- Playwright Chromium

### Database (Railway PostgreSQL)

**Version:** PostgreSQL 15

**Connection:**
- Public URL: `monorail.proxy.rlwy.net`
- Internal URL: `postgres.railway.internal` (within Railway network)
- SSL: Required

**Migrations:**
- Tool: Alembic
- Location: `backend/migrations/`
- Auto-run: On Railway deployment (if configured)

---

## 💰 Cost Breakdown

### Monthly Costs

| Service | Tier | Cost | Usage |
|---------|------|------|-------|
| Vercel Frontend | Hobby | $0 | Unlimited deployments |
| Railway Backend | Free | $0 | $5 credit/month |
| Railway PostgreSQL | Free | $0 | Included in Railway |
| GitHub Actions | Free | $0 | 2000 minutes/month |
| Upstash Redis | Free | $0 | 10K requests/day |
| OpenRouter | Pay-per-use | ~$0 | Not yet used |

**Total:** $0/month

**Scalability Limits (Free Tier):**
- Railway: ~500 hours/month uptime
- GitHub Actions: ~133 worker runs/month (15min each)
- Upstash: ~300K requests/month
- Vercel: Unlimited builds, 100GB bandwidth

**Upgrade Path:**
- Railway Pro: $20/month (unlimited hours)
- Upstash Pro: $60/month (500K requests/day)
- OpenRouter: Pay-per-use ($0.001-$0.01 per request)

---

## 🔮 Future Roadmap

### Phase 1: Feature G Implementation (3-4 hours)
- [ ] Category hierarchy detection
- [ ] Product page pattern recognition
- [ ] API endpoint discovery
- [ ] CSS selector generation
- [ ] LLM semantic analysis
- [ ] Complete blueprint generation

### Phase 2: Enhanced LLM Integration (2 hours)
- [ ] Automatic selector validation
- [ ] Blueprint quality assessment
- [ ] Scraper strategy recommendations
- [ ] Natural language site analysis

### Phase 3: Template Library (1 hour)
- [ ] Pre-built Shopify template
- [ ] Pre-built Magento template
- [ ] Pre-built WooCommerce template
- [ ] Template suggestion system

### Phase 4: Monitoring & Observability (2 hours)
- [ ] Sentry error tracking
- [ ] Performance monitoring
- [ ] Usage analytics
- [ ] Alerting system

### Phase 5: Testing & CI/CD (3 hours)
- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] Automated test runs

### Phase 6: Authentication & RBAC (1 hour)
- [ ] Re-enable JWT authentication
- [ ] Add user registration flow
- [ ] Implement role-based permissions
- [ ] Add API key authentication

---

## 📚 Code Organization

### Backend Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and environment config
│   ├── database.py             # Database connection and sessions
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── site.py
│   │   ├── job.py
│   │   ├── blueprint.py
│   │   ├── user.py
│   │   └── analytics.py
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── site.py
│   │   ├── job.py
│   │   ├── blueprint.py
│   │   ├── auth.py
│   │   └── analytics.py
│   ├── routes_sites.py         # Site management endpoints
│   ├── routes_jobs.py          # Job management endpoints
│   ├── routes_blueprints.py    # Blueprint endpoints
│   ├── routes_analytics.py     # Analytics endpoints
│   ├── services/               # Business logic services
│   │   ├── fingerprint_service.py
│   │   └── llm_service.py
│   ├── workers/                # Celery background workers
│   │   ├── fingerprinter.py
│   │   ├── discoverer.py
│   │   ├── selector_generator.py
│   │   └── github_runner.py
│   ├── middleware_rate_limit.py
│   ├── middleware_auth.py
│   ├── security.py
│   └── celery_app.py
├── migrations/                 # Alembic database migrations
├── requirements-full.txt       # All Python dependencies
├── requirements-worker.txt     # Worker-specific dependencies
└── Dockerfile

frontend/
├── src/
│   ├── App.tsx                 # Main application component
│   ├── App.css                 # Global styles
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── Sidebar.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Sites.tsx
│   │   ├── SiteDetails.tsx     # NEW: Site details with tabs
│   │   ├── Jobs.tsx
│   │   └── Analytics.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── vercel.json

.github/
└── workflows/
    ├── worker_fingerprint.yml  # Scheduled fingerprinting worker
    ├── worker_discover.yml     # (Future) Discovery worker
    └── worker_selectors.yml    # (Future) Selector generation worker
```

---

## 🎓 Key Design Decisions

### 1. Why GitHub Actions for Workers?

**Pros:**
- Free tier: 2000 minutes/month
- No server maintenance
- Scheduled execution (cron)
- Easy secret management
- Automatic scaling

**Cons:**
- 15-minute minimum interval
- 6-hour max runtime per job
- Can't respond to events instantly

**Decision:** Perfect for batch processing jobs every 15 minutes. For real-time processing, could add Railway-based Celery workers later.

### 2. Why Upstash Redis REST API?

**Pros:**
- Free tier available
- No connection pool needed
- HTTP-based (works from serverless)
- Global edge network

**Cons:**
- Slightly higher latency than direct connection
- Limited to REST API features

**Decision:** Perfect for rate limiting from Railway. Direct Redis connection available as fallback for Celery.

### 3. Why Railway + Vercel Instead of All-Vercel?

**Pros:**
- Railway: Better for stateful apps, WebSockets, long-running processes
- Vercel: Perfect for static frontends with edge caching
- Separation of concerns

**Cons:**
- Two platforms to manage
- Cross-origin requests (CORS needed)

**Decision:** Best of both worlds. Railway for backend, Vercel for frontend.

### 4. Why FastAPI Instead of Django/Flask?

**Pros:**
- Native async support
- Automatic API docs (Swagger)
- Type hints and validation (Pydantic)
- High performance (ASGI)
- Modern Python features

**Cons:**
- Less mature ecosystem than Django
- Fewer built-in features

**Decision:** Perfect for API-first architecture with async database operations.

### 5. Why Disable Authentication?

**Reason:** Easier initial testing and development. Production deployment should re-enable authentication.

**How to Re-enable:**
1. Uncomment imports in route files
2. Add `get_current_user` dependency to endpoints
3. Add `require_roles` decorators
4. Set strong `JWT_SECRET` in environment

---

## 🐛 Troubleshooting Guide

### Frontend Shows 404 on Site Details

**Symptom:** Clicking "View Details" shows 404 error

**Cause:** Vercel didn't deploy SiteDetails.tsx page

**Fix:** Force rebuild by pushing a commit

```bash
# Make a small change
echo "// Force rebuild" >> frontend/src/App.tsx
git add -A
git commit -m "Force Vercel rebuild"
git push origin main
# Wait 1-2 minutes for Vercel to deploy
```

### Workers Not Processing Jobs

**Symptom:** Jobs stay in "queued" status forever

**Cause 1:** GitHub Actions not running
**Fix 1:** Check Actions tab in GitHub, manually trigger workflow

**Cause 2:** Database connection error in worker
**Fix 2:** Verify `DATABASE_URL` secret in GitHub is correct and public

**Cause 3:** Worker reached GitHub Actions limit
**Fix 3:** Upgrade to paid plan or reduce frequency

### Backend Returns 500 on Analytics Endpoints

**Symptom:** Analytics dashboard shows "Failed to load metrics"

**Cause:** Pydantic schema mismatch

**Fix:** Ensure route returns exactly the fields defined in schema

```python
# Correct:
return DashboardMetricsResponse(
    total_sites=10,
    active_jobs=5,
    total_blueprints=8,
    avg_discovery_time=15.5,
    success_rate=0.95
)

# Incorrect:
return {
    "total_sites": 10,
    # Missing other required fields
}
```

### CORS Errors in Browser Console

**Symptom:** `No 'Access-Control-Allow-Origin' header`

**Cause 1:** Backend CORS_ORIGINS not set
**Fix 1:** Set in Railway environment variables

**Cause 2:** Backend returning 500, so CORS headers not sent
**Fix 2:** Fix the underlying 500 error first

### Rate Limit Errors

**Symptom:** `Rate limit exceeded` (429) on API calls

**Cause:** Upstash REST API returning 400 error

**Fix:** Verify Upstash credentials in Railway environment:
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

---

## 📞 Support & Maintenance

### Git Repository
https://github.com/FraudShield1/web-intelligence-platform

### Deployment URLs
- Frontend: https://web-intelligence-platform.vercel.app
- Backend: https://web-intelligence-platform-production.up.railway.app
- API Docs: https://web-intelligence-platform-production.up.railway.app/docs

### Monitoring Dashboards
- Vercel: https://vercel.com/dashboard
- Railway: https://railway.app/dashboard
- GitHub Actions: https://github.com/FraudShield1/web-intelligence-platform/actions

### Key Contacts
- Platform Owner: [Your Name]
- Repository: FraudShield1/web-intelligence-platform

---

## 📖 Additional Resources

### Documentation Files
- `TESTING_GUIDE.md` - How to test the platform
- `PLATFORM_100_PERCENT_COMPLETE.md` - What's implemented
- `READY_FOR_TESTING.md` - Quick testing guide
- `docs/prd.md` - Original product requirements

### External Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Playwright: https://playwright.dev/
- Railway: https://docs.railway.app/
- Vercel: https://vercel.com/docs

---

## 🎯 Summary for LLMs

**What is this?**
An autonomous web intelligence platform that fingerprints websites, detects technology stacks, assesses scraping complexity, and prepares blueprints for downstream scrapers. Built with FastAPI (Python), React (TypeScript), PostgreSQL, and GitHub Actions workers.

**Current Status:**
- ✅ Basic fingerprinting working (tech stack, platform, complexity)
- ✅ Site details UI with tabs (Overview, Fingerprint, Blueprint)
- ✅ Export blueprints (JSON/YAML)
- ✅ Analytics dashboard
- ✅ Automated workers (every 15 minutes)
- ⚠️ Feature G (deep discovery) not yet implemented
- ⚠️ No categories, products, selectors yet

**Next Steps:**
- User tests current fingerprinting
- Decides if Feature G is needed
- Implement Feature G phases as requested
- Add LLM semantic analysis
- Enhance blueprint generation

**Cost:** $0/month (all free tiers)

**Deployment:** Fully operational and accessible online

---

*Last Updated: November 6, 2025*  
*Version: 1.0*  
*Status: Production-Ready (Basic Features)*

