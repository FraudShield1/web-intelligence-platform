# Supabase Setup Instructions

## Your Supabase Credentials

```
Project URL: https://aeajgihhgplxcvcsiqeo.supabase.co
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Get Database Connection String

1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Project Settings** → **Database**
4. Find **Connection string** section
5. Copy the **URI** format (should look like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.aeajgihhgplxcvcsiqeo.supabase.co:5432/postgres
   ```

## Alternative: Use Supabase REST API (recommended for now)

Since direct database connection isn't working, we can:

1. Create tables via Supabase SQL Editor (Dashboard → SQL Editor)
2. Use Supabase JS client for data operations
3. Backend can use Supabase REST API

## Create Tables in Supabase

Go to https://supabase.com/dashboard → SQL Editor → New Query

Run this SQL:

```sql
-- Sites table
CREATE TABLE IF NOT EXISTS sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(100),
    status VARCHAR(50),
    fingerprint_data JSONB,
    complexity_score FLOAT,
    business_value_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    last_discovered_at TIMESTAMP,
    blueprint_version INTEGER,
    notes TEXT
);

-- Users table  
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Blueprints table
CREATE TABLE IF NOT EXISTS blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    confidence_score FLOAT,
    categories_data JSONB,
    endpoints_data JSONB,
    render_hints_data JSONB,
    selectors_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- Selectors table
CREATE TABLE IF NOT EXISTS selectors (
    selector_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID REFERENCES blueprints(blueprint_id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    css_selector VARCHAR(500),
    xpath VARCHAR(500),
    confidence FLOAT,
    generation_method VARCHAR(50),
    test_pass_rate FLOAT,
    test_count INTEGER,
    test_failures INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested_at TIMESTAMP,
    notes TEXT
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    attempt_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    error_code VARCHAR(50),
    error_message TEXT,
    worker_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload JSONB,
    result JSONB,
    duration_seconds INTEGER,
    heartbeat_at TIMESTAMP
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE SET NULL,
    date TIMESTAMP,
    discovery_time_seconds INTEGER,
    num_categories_found INTEGER,
    num_endpoints_found INTEGER,
    selector_failure_rate FLOAT,
    fetch_cost_usd FLOAT,
    items_extracted INTEGER,
    method VARCHAR(50),
    job_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_site_id ON jobs(site_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_site_id ON blueprints(site_id);
```

## After Creating Tables

Run the backend locally (no database migrations needed):

```bash
cd backend

# Set environment
export DATABASE_URL='postgresql+asyncpg://postgres:YOUR_PASSWORD@db.aeajgihhgplxcvcsiqeo.supabase.co:5432/postgres'
export CORS_ORIGINS='["http://localhost:3000"]'
export ENABLE_DOCS=true
export DEBUG=true

# Run backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend Setup

```bash
cd frontend

# Create .env.local
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://aeajgihhgplxcvcsiqeo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlYWpnaWhoZ3BseGN2Y3NpcWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzMjY1MzMsImV4cCI6MjA3NzkwMjUzM30.KgZrArrNkk_8ujSMhu-QL5TCG9Elv9YHdTp4oxScbKM
EOF

# Install and run
npm install
npm start
```

## Verify

- Backend: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Next: Get Database Password

To get the correct connection string with password:
1. Supabase Dashboard → Project Settings → Database
2. Look for "Connection string" → "URI"
3. Reset password if needed (Database → Settings → Reset)

The hostname should be: `db.aeajgihhgplxcvcsiqeo.supabase.co`

