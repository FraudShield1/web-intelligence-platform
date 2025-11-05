-- Railway PostgreSQL Database Setup
-- Run this in Railway's PostgreSQL database

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create Sites Table
CREATE TABLE IF NOT EXISTS sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain TEXT NOT NULL,
    platform VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    complexity_score FLOAT,
    business_value_score FLOAT DEFAULT 0.5,
    blueprint_version INTEGER DEFAULT 1,
    fingerprint_data JSONB,
    notes TEXT,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_discovered_at TIMESTAMP
);

-- 3. Create Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(100) NOT NULL,
    method VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Create Blueprints Table
CREATE TABLE IF NOT EXISTS blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    categories JSONB,
    selectors JSONB,
    config JSONB,
    performance_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Create Analytics Table
CREATE TABLE IF NOT EXISTS analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT,
    dimensions JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 6. Create Admin User
-- Password: SecurePassword123
INSERT INTO users (
    username,
    email,
    password_hash,
    role,
    is_active
) VALUES (
    'admin@example.com',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRX0JQFCm',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sites_status ON sites(status);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_jobs_site_id ON jobs(site_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_blueprints_site_id ON blueprints(site_id);
CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_metrics(timestamp);

-- Done!
SELECT 'Database initialized successfully!' as status;
SELECT 'Admin user: admin@example.com / SecurePassword123' as credentials;

