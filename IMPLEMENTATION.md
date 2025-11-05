# Implementation Blueprint
## Complete Technical Architecture & Execution Guide

---

## 1. SYSTEM ARCHITECTURE DETAILED DESIGN

### 1.1 Microservice Architecture

The platform is decomposed into **7 core microservices**:

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│  (Rate limiting, Auth, Request routing, Load balancing)          │
└─────────────────────────────────────────────────────────────────┘
         │          │          │          │          │
    ┌────┴────┐ ┌──┴──┐ ┌─────┴────┐ ┌──┴────┐ ┌──┴───┐
    │          │ │     │ │          │ │       │ │      │
┌───▼──┐   ┌──▼─▼──┐ ┌─▼────┐  ┌──▼─▼──┐ ┌─▼──▼──┐
│ Auth │   │ Sites │ │ Jobs │  │ BluPr │ │ Analyt│
│      │   │ Svc   │ │ Svc  │  │ Svc   │ │ Svc   │
└──────┘   └───────┘ └──────┘  └───────┘ └───────┘
     
     ┌──────────────┐  ┌────────────────┐
     │  Discovery   │  │  Selector/     │
     │  Orchestr.   │  │  Endpoint      │
     │              │  │  Extractor     │
     └──────────────┘  └────────────────┘
              │                 │
     ┌────────┴─────────────────┴────────┐
     │                                    │
┌────▼──────┐  ┌──────────────┐  ┌──────▼────┐
│ Workers   │  │ Template Lib │  │ LLM Svc   │
│ (Fingerpr)│  │ & Cache      │  │ (Proxy)   │
│ (Browser) │  │              │  │           │
│ (Static)  │  │              │  │           │
└───────────┘  └──────────────┘  └───────────┘
```

### 1.2 Module Responsibilities

| Service | Purpose | Key Exports |
|---------|---------|-------------|
| **API Gateway** | Request routing, auth, rate limiting | HTTP endpoints |
| **Auth Service** | JWT generation, RBAC | Access tokens |
| **Sites Service** | CRUD for sites, fingerprints | Site metadata |
| **Jobs Service** | Job lifecycle, queue management | Job status |
| **Blueprint Service** | Blueprint versioning, storage | SIO objects |
| **Analytics Service** | Metrics aggregation, reporting | KPIs, trends |
| **Discovery Orchestrator** | Route discovery method, job dispatch | Job IDs |
| **Selector/Endpoint Extractor** | Parse results, synthesize selectors | Extraction results |
| **Workers** | Fingerprint, browse, crawl, extract | Raw data |
| **Template Library** | Platform patterns, reusable rules | Selector templates |
| **LLM Service** | Proxy for LLM calls, prompt templates | LLM responses |

---

## 2. DATA FLOW & STATE MACHINES

### 2.1 Site Discovery Flow (Complete)

```
User submits domain
         │
         ▼
    Fingerprint Job
    (tech detection,
     sitemap scan,
     JS detection)
         │
         ├─────────┬──────────────┬──────────────┐
         │         │              │              │
    [Static OK]  [JS Req'd]    [API Found]   [Complex]
         │         │              │              │
         ▼         ▼              ▼              ▼
    Static       Browser        API Auth      Visual
    Crawler      Job            Job          Extract
         │         │              │          (future)
         └─────────┼──────────────┴──────────┘
                   │
              ┌────▼────┐
              │ Extract  │
              │ Blueprint│
              │(LLM+Rule)│
              └────┬─────┘
                   │
              ┌────▼─────┐
              │ Score &  │
              │ Validate │
              └────┬─────┘
                   │
         ┌─────────┴──────────┐
         │                    │
      [Pass]              [Review]
         │                    │
         ▼                    ▼
      Ready            Human Review
                       Queue
```

### 2.2 Job State Machine

```
┌─────────┐
│ Pending │ ─────► Job submitted to queue
└────┬────┘       (max_retries=3, backoff=exp)
     │
     ▼
┌─────────┐
│ Queued  │ ─────► Waiting for worker availability
└────┬────┘       (priority by site_score)
     │
     ▼
┌─────────┐
│ Running │ ─────► Worker processing
└────┬────┘       (heartbeat every 30s)
     │
     ├──────────────┬──────────────┬──────────┐
     │              │              │          │
   [OK]          [ERROR]      [TIMEOUT]   [CANCELLED]
     │              │              │          │
     ▼              ▼              ▼          ▼
  Success        Failed      Timeout       Cancelled
     │              │              │          │
     └──────────────┼──────────────┼──────────┘
                    │
              ┌─────▼──────┐
              │ Retry?     │
              │ (attempt<3)│
              └─────┬──────┘
                    │
            ┌───────┴────────┐
            │                │
           [Yes]           [No]
            │                │
            ▼                ▼
          Queued      Dead Letter
                      (escalate)
```

### 2.3 Selector Confidence Scoring

```
CSS Selector Generated
    │
    ├─► Test on 3 sample pages (same domain)
    │   ├─ Returns expected element count? (0.2 pts)
    │   ├─ Text content matches pattern? (0.3 pts)
    │   └─ Attribute values reasonable? (0.2 pts)
    │
    ├─► LLM confidence score (0.3 pts)
    │   ├─ Based on prompt certainty
    │   └─ Semantic validation
    │
    ▼
Final Score = 0.0 - 1.0
├─ 0.0-0.5 = Low (manual review)
├─ 0.5-0.8 = Medium (use with caution)
└─ 0.8-1.0 = High (trusted)
```

---

## 3. DATABASE SCHEMA (DDL)

### 3.1 Core Tables

```sql
-- Sites table
CREATE TABLE sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(100),  -- Shopify, Magento, WooCommerce, Custom
    status VARCHAR(50) DEFAULT 'pending',  -- pending, ready, review, failed
    fingerprint_data JSONB,  -- tech stack, CMS, JS framework
    complexity_score FLOAT,
    business_value_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_discovered_at TIMESTAMP,
    blueprint_version INT DEFAULT 0,
    notes TEXT
);

CREATE INDEX idx_sites_status ON sites(status);
CREATE INDEX idx_sites_platform ON sites(platform);
CREATE INDEX idx_sites_created ON sites(created_at DESC);

-- Jobs table
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(site_id),
    job_type VARCHAR(50),  -- Fingerprint, Discovery, Extraction, Blueprint_Update
    method VARCHAR(50),  -- Static, Browser, API
    status VARCHAR(50) DEFAULT 'queued',  -- queued, running, success, failed
    priority INT DEFAULT 0,  -- Higher number = higher priority
    attempt_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    error_code VARCHAR(50),
    error_message TEXT,
    worker_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    payload JSONB,  -- Method-specific parameters
    result JSONB,  -- Output data
    duration_seconds INT
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_site_id ON jobs(site_id);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
CREATE INDEX idx_jobs_priority ON jobs(priority DESC, created_at ASC);

-- Blueprints table
CREATE TABLE blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(site_id),
    version INT NOT NULL,
    confidence_score FLOAT,
    categories_data JSONB,  -- Embedded instead of file reference
    endpoints_data JSONB,
    render_hints_data JSONB,
    selectors_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    notes TEXT,
    UNIQUE(site_id, version)
);

CREATE INDEX idx_blueprints_site ON blueprints(site_id);
CREATE INDEX idx_blueprints_version ON blueprints(site_id, version DESC);

-- Selectors table
CREATE TABLE selectors (
    selector_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID NOT NULL REFERENCES blueprints(blueprint_id),
    field_name VARCHAR(100),  -- price, title, image_url, etc.
    css_selector VARCHAR(500),
    xpath VARCHAR(500),
    confidence FLOAT,
    generation_method VARCHAR(50),  -- llm, heuristic, manual
    test_pass_rate FLOAT,  -- % of test pages where selector worked
    created_at TIMESTAMP DEFAULT NOW(),
    last_tested_at TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_selectors_blueprint ON selectors(blueprint_id);
CREATE INDEX idx_selectors_field ON selectors(field_name);

-- Analytics metrics table
CREATE TABLE analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id),
    date DATE,
    discovery_time_seconds INT,
    num_categories_found INT,
    num_endpoints_found INT,
    selector_failure_rate FLOAT,
    fetch_cost_usd FLOAT,
    items_extracted INT,
    method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metrics_site_date ON analytics_metrics(site_id, date DESC);
CREATE INDEX idx_metrics_date ON analytics_metrics(date DESC);

-- Templates table
CREATE TABLE platform_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_name VARCHAR(100),  -- Shopify, Magento, etc.
    category_selectors JSONB,
    product_list_selectors JSONB,
    api_patterns JSONB,
    render_hints JSONB,
    confidence FLOAT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_templates_platform ON platform_templates(platform_name);
```

### 3.2 Relationships & Cardinality

```
sites (1) ──────────────── (N) jobs
            orchestrates
            
sites (1) ──────────────── (N) blueprints
            generates versions
            
blueprints (1) ──────────────── (N) selectors
               contains
               
sites (1) ──────────────── (N) analytics_metrics
            monitors
```

---

## 4. API ENDPOINTS (REST)

### 4.1 Sites API

```
POST /api/v1/sites
  Body: { "domain": "example.com" }
  Response: { "site_id": "uuid", "status": "pending", "job_id": "uuid" }
  
GET /api/v1/sites
  Query: ?status=ready&platform=shopify&limit=50&offset=0
  Response: { "sites": [...], "total": 1234 }
  
GET /api/v1/sites/{site_id}
  Response: { "site_id", "domain", "status", "fingerprint_data", 
              "current_blueprint_version", "last_discovered_at", ... }
  
PUT /api/v1/sites/{site_id}
  Body: { "business_value_score": 0.95, "notes": "..." }
  Response: { "updated_at": "..." }
  
DELETE /api/v1/sites/{site_id}
  Response: { "deleted": true }
```

### 4.2 Jobs API

```
POST /api/v1/jobs
  Body: { "site_id": "uuid", "job_type": "Discovery", "method": "Auto" }
  Response: { "job_id": "uuid", "status": "queued", "position": 42 }
  
GET /api/v1/jobs/{job_id}
  Response: { "job_id", "status", "progress", "error", "result", 
              "started_at", "ended_at", ... }
  
GET /api/v1/jobs?site_id=uuid&status=running&limit=50
  Response: { "jobs": [...], "total": 123 }
  
POST /api/v1/jobs/{job_id}/cancel
  Response: { "status": "cancelled" }
  
POST /api/v1/jobs/{job_id}/retry
  Response: { "new_job_id": "uuid" }
```

### 4.3 Blueprints API

```
GET /api/v1/blueprints/sites/{site_id}/latest
  Response: { "blueprint_id", "version", "confidence_score", 
              "categories_data", "endpoints_data", ... }
  
GET /api/v1/blueprints/{blueprint_id}
  Response: full blueprint object
  
GET /api/v1/blueprints/{blueprint_id}/versions
  Query: ?limit=10
  Response: { "versions": [...] }
  
POST /api/v1/blueprints/{blueprint_id}/rollback
  Body: { "to_version": 1 }
  Response: { "new_version": 2, "from": 1, "to": 2 }
  
GET /api/v1/blueprints/{blueprint_id}/export
  Query: ?format=json&include=selectors,endpoints
  Response: downloadable JSON or YAML
```

### 4.4 Analytics API

```
GET /api/v1/analytics/dashboard
  Query: ?date_range=7d&metric_types=discovery_time,selector_failure
  Response: { "overview": {...}, "trends": {...}, "alerts": [...] }
  
GET /api/v1/analytics/sites/{site_id}/metrics
  Query: ?start_date=2024-01-01&end_date=2024-12-31
  Response: { "metrics": [...], "trend": "improving|stable|declining" }
  
GET /api/v1/analytics/methods/performance
  Query: ?groupby=platform,method
  Response: { "methods": [...], "cost_yield_matrix": {...} }
  
POST /api/v1/analytics/export
  Body: { "report_type": "monthly", "format": "csv" }
  Response: downloadable file
```

---

## 5. WORKER IMPLEMENTATION PATTERNS

### 5.1 Generic Worker Interface

```python
# workers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import httpx

class BaseWorker(ABC):
    def __init__(self, worker_id: str, config: Dict):
        self.worker_id = worker_id
        self.config = config
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 60)
    
    @abstractmethod
    async def execute(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Execute job and return results."""
        pass
    
    async def heartbeat(self):
        """Send heartbeat to job service."""
        await self._update_job_status("running")
    
    async def _handle_error(self, job_id: str, error: Exception):
        """Log error and update job status."""
        await self._update_job_status("failed", error=str(error))
    
    async def _update_job_status(self, status: str, **kwargs):
        """Update job status in database."""
        # Implementation details
        pass
```

### 5.2 Fingerprint Worker Example

```python
# workers/fingerprinter.py
import asyncio
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class FingerprintWorker(BaseWorker):
    async def execute(self, job: Dict) -> Dict:
        site_id = job["site_id"]
        domain = job["payload"]["domain"]
        
        result = {
            "site_id": site_id,
            "tech_stack": [],
            "cms_detected": None,
            "js_frameworks": [],
            "sitemap_urls": [],
            "api_hints": [],
            "has_js_rendering": False,
        }
        
        try:
            # Fetch homepage
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"https://{domain}", 
                                           follow_redirects=True)
                html = response.text
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Detect CMS
            result["cms_detected"] = self._detect_cms(soup, html)
            
            # Detect JS frameworks
            result["js_frameworks"] = self._detect_js_frameworks(html)
            
            # Extract meta information
            result["has_js_rendering"] = self._needs_js_rendering(html)
            
            # Find sitemap
            result["sitemap_urls"] = await self._find_sitemaps(domain)
            
            # Detect APIs
            result["api_hints"] = self._extract_api_hints(html)
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def _detect_cms(self, soup, html) -> str:
        """Detect platform: Shopify, Magento, WooCommerce, etc."""
        if "Shopify.AppBridge" in html:
            return "shopify"
        if "magento" in html.lower():
            return "magento"
        if "woocommerce" in html.lower():
            return "woocommerce"
        # Add more detection patterns
        return "custom"
    
    def _detect_js_frameworks(self, html) -> list:
        """Detect React, Vue, Angular, etc."""
        frameworks = []
        if "react" in html.lower() or "__REACT" in html:
            frameworks.append("react")
        if "vue" in html.lower() or "__VUE" in html:
            frameworks.append("vue")
        if "angular" in html.lower():
            frameworks.append("angular")
        return frameworks
    
    async def _find_sitemaps(self, domain) -> list:
        """Find sitemap URLs."""
        sitemaps = []
        candidates = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/sitemap-index.xml",
        ]
        async with httpx.AsyncClient() as client:
            for url in candidates:
                try:
                    response = await client.head(url, timeout=5)
                    if response.status_code == 200:
                        sitemaps.append(url)
                except:
                    pass
        return sitemaps
```

---

## 6. LLM SERVICE INTEGRATION

### 6.1 LLM Service Layer

```python
# services/llm_service.py
from typing import Dict, List, Any
import anthropic
import openai

class LLMService:
    def __init__(self, config):
        self.provider = config.get("provider", "anthropic")
        self.model = config.get("model", "claude-3-opus")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
    
    async def extract_categories(self, html: str, base_url: str) -> Dict:
        """LLM: Extract category links from HTML."""
        prompt = self._build_category_prompt(html, base_url)
        response = await self._call_llm(prompt)
        return self._parse_json_response(response)
    
    async def synthesize_selectors(self, html: str, fields: List[str]) -> Dict:
        """LLM: Generate CSS/XPath selectors."""
        prompt = self._build_selector_prompt(html, fields)
        response = await self._call_llm(prompt)
        return self._parse_json_response(response)
    
    async def interpret_network_logs(self, network_requests: List[Dict]) -> Dict:
        """LLM: Propose API endpoints from network trace."""
        prompt = self._build_api_prompt(network_requests)
        response = await self._call_llm(prompt)
        return self._parse_json_response(response)
    
    def _build_category_prompt(self, html: str, base_url: str) -> str:
        """Build prompt for category extraction."""
        return f"""
You are an expert web scraper analyzing HTML to find product categories.

BASE URL: {base_url}

HTML (truncated to first 50KB):
{html[:50000]}

Task: Identify all category links in the navigation or category menu.

For each category, provide:
1. name (category name as displayed)
2. url (full URL of category page)
3. selector (CSS selector that uniquely identifies this link)
4. confidence (0.0-1.0, your confidence in this being a real category)

Return JSON array of categories. Be thorough but conservative.
"""
    
    def _build_selector_prompt(self, html: str, fields: List[str]) -> str:
        """Build prompt for selector synthesis."""
        fields_str = ", ".join(fields)
        return f"""
You are an expert in CSS selectors and XPath expressions.

HTML of a product listing page (first 30KB):
{html[:30000]}

Task: Generate CSS selectors (and alternative XPath) for these fields:
{fields_str}

For each field, provide:
1. field_name
2. css_selector (preferred)
3. xpath (alternative)
4. confidence (0.0-1.0)
5. notes (why this selector works)

Return as JSON object with field names as keys.
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API with retry and error handling."""
        if self.provider == "anthropic":
            client = anthropic.Anthropic()
            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            # OpenAI or other provider
            pass
    
    def _parse_json_response(self, response: str) -> Dict:
        """Extract JSON from LLM response."""
        import json
        import re
        
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
```

---

## 7. CONFIGURATION MANAGEMENT

### 7.1 Config Structure

```yaml
# config/settings.yml
app:
  name: "Web Intelligence Platform"
  version: "1.0.0"
  debug: false

services:
  api_gateway:
    host: "0.0.0.0"
    port: 8000
    workers: 4
  
  database:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "web_intelligence"
    pool_size: 20
    connection_timeout: 10
  
  redis:
    host: "localhost"
    port: 6379
    db: 0
  
  queue:
    type: "rabbitmq"
    host: "localhost"
    port: 5672
    prefetch_count: 10

workers:
  fingerprinter:
    timeout: 60
    max_retries: 3
    concurrency: 5
  
  browser:
    timeout: 120
    max_retries: 2
    concurrency: 2
    headless: true
  
  static_crawler:
    timeout: 60
    max_retries: 3
    concurrency: 10

llm:
  provider: "anthropic"
  model: "claude-3-opus"
  temperature: 0.7
  max_tokens: 4096
  timeout: 60
  cost_limit_per_day: 100.0

proxy:
  enabled: true
  pool_size: 50
  rotation_delay: 5
  fallback_direct: true

monitoring:
  prometheus:
    enabled: true
    port: 9090
  
  logging:
    level: "INFO"
    format: "json"
    output: "stdout"

auth:
  jwt_secret: "${JWT_SECRET}"
  token_expiry: 3600
```

---

## 8. ERROR HANDLING & RECOVERY

### 8.1 Error Classification

| Error Code | Type | Severity | Recovery |
|-----------|------|----------|----------|
| 4001 | Network timeout | High | Retry with backoff |
| 4002 | IP blocked (403) | Critical | Switch proxy, escalate |
| 4003 | CAPTCHA detected | Critical | Manual review queue |
| 4004 | JS parsing error | Medium | Fallback to static |
| 4005 | Selector not found | Medium | Re-generate, manual review |
| 4006 | LLM quota exceeded | High | Queue, retry next hour |
| 5001 | Database error | Critical | Circuit breaker, fallback |
| 5002 | Queue full | High | Backpressure, scale workers |

### 8.2 Retry Strategy

```python
# utils/retry.py
import random
from datetime import datetime, timedelta

class RetryStrategy:
    def __init__(self, max_retries=3, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def should_retry(self, attempt: int, error_code: str) -> bool:
        """Determine if we should retry based on error."""
        if attempt >= self.max_retries:
            return False
        
        # Don't retry certain errors
        no_retry_codes = ["4003", "5001"]  # CAPTCHA, DB error
        if error_code in no_retry_codes:
            return False
        
        return True
    
    def get_backoff_delay(self, attempt: int) -> int:
        """Exponential backoff with jitter."""
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, 0.1 * delay)
        return int(delay + jitter)
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with automatic retry."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if not self.should_retry(attempt, e.code):
                    raise
                delay = self.get_backoff_delay(attempt)
                await asyncio.sleep(delay)
        raise Exception("Max retries exceeded")
```

---

## 9. DEPLOYMENT & SCALING

### 9.1 Docker Compose (Development)

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/web_intelligence
      - REDIS_URL=redis://cache:6379
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - db
      - cache
      - rabbitmq
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --reload

  fingerprinter:
    build:
      context: ./workers
      dockerfile: Dockerfile
    environment:
      - WORKER_TYPE=fingerprinter
      - DATABASE_URL=postgresql://user:pass@db:5432/web_intelligence
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - db
      - rabbitmq
    deploy:
      replicas: 2

  browser_worker:
    build:
      context: ./workers
      dockerfile: Dockerfile.browser
    environment:
      - WORKER_TYPE=browser
      - DATABASE_URL=postgresql://user:pass@db:5432/web_intelligence
      - RABBITMQ_URL=amqp://rabbitmq:5672
    depends_on:
      - db
      - rabbitmq
    deploy:
      replicas: 1

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=web_intelligence
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=user
      - RABBITMQ_DEFAULT_PASS=pass

  dashboard:
    build:
      context: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 10. MONITORING & OBSERVABILITY

### 10.1 Key Metrics to Track

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Job metrics
jobs_submitted = Counter('jobs_submitted_total', 'Total jobs submitted')
jobs_completed = Counter('jobs_completed_total', 'Total jobs completed', ['status'])
job_duration = Histogram('job_duration_seconds', 'Job execution time', ['job_type'])
jobs_in_queue = Gauge('jobs_in_queue', 'Jobs waiting in queue')

# Worker metrics
worker_heartbeat = Gauge('worker_heartbeat', 'Worker last heartbeat', ['worker_id'])
worker_errors = Counter('worker_errors_total', 'Worker errors', ['worker_id', 'error_code'])

# Site metrics
sites_discovered = Counter('sites_discovered_total', 'Sites discovered')
selector_failures = Counter('selector_failures_total', 'Selector test failures', ['site_id'])

# LLM metrics
llm_calls = Counter('llm_calls_total', 'LLM API calls', ['prompt_type'])
llm_cost = Counter('llm_cost_usd', 'LLM costs', ['model'])
llm_latency = Histogram('llm_latency_seconds', 'LLM response time')

# Database metrics
db_query_time = Histogram('db_query_duration_seconds', 'Database query duration', ['query_type'])
db_errors = Counter('db_errors_total', 'Database errors')
```

---

## NEXT STEPS

1. **Database**: Run `DATABASE.sql` to create schema
2. **Backend**: Start with FastAPI app skeleton
3. **Frontend**: React dashboard with Recharts
4. **Workers**: Deploy fingerprinter first, test end-to-end
5. **LLM**: Integrate Claude API with prompt templates
6. **Testing**: Unit tests, integration tests, E2E tests

See `API_SPEC.md` and implementation repos for full code.

