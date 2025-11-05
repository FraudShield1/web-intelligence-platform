-- Web Intelligence Platform - Supabase Schema
-- Run this in Supabase Dashboard → SQL Editor → New Query

-- Sites table
CREATE TABLE IF NOT EXISTS sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    fingerprint_data JSONB,
    complexity_score FLOAT,
    business_value_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_discovered_at TIMESTAMP,
    blueprint_version INTEGER DEFAULT 0,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blueprints table
CREATE TABLE IF NOT EXISTS blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    confidence_score FLOAT DEFAULT 0.0,
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
    confidence FLOAT DEFAULT 0.0,
    generation_method VARCHAR(50),
    test_pass_rate FLOAT DEFAULT 0.0,
    test_count INTEGER DEFAULT 0,
    test_failures INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_tested_at TIMESTAMP,
    notes TEXT
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL,
    method VARCHAR(50) DEFAULT 'auto',
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

-- Analytics metrics table
CREATE TABLE IF NOT EXISTS analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE SET NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_sites_created_at ON sites(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_site_id ON jobs(site_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_blueprints_site_id ON blueprints(site_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_version ON blueprints(site_id, version DESC);

CREATE INDEX IF NOT EXISTS idx_selectors_blueprint_id ON selectors(blueprint_id);

CREATE INDEX IF NOT EXISTS idx_analytics_site_id ON analytics_metrics(site_id);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_metrics(date DESC);

-- Insert a sample admin user (password: admin - you should change this!)
-- Password hash for "admin" using bcrypt
INSERT INTO users (username, email, password_hash, role, is_active)
VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYqYqYqYq',
    'admin',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- Verify tables were created
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Show row counts
SELECT 
    'sites' as table_name, COUNT(*) as count FROM sites
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'blueprints', COUNT(*) FROM blueprints
UNION ALL
SELECT 'selectors', COUNT(*) FROM selectors
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs
UNION ALL
SELECT 'analytics_metrics', COUNT(*) FROM analytics_metrics;

