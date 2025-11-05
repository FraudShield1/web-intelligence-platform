-- Web Intelligence Platform - Database Schema
-- PostgreSQL 14+

-- ============================================================================
-- 1. CORE TABLES
-- ============================================================================

-- Sites Table: Master record for each discovered website
CREATE TABLE sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(255) NOT NULL UNIQUE,
    platform VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'review', 'failed', 'archived')),
    fingerprint_data JSONB,
    complexity_score FLOAT,
    business_value_score FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_discovered_at TIMESTAMP,
    blueprint_version INT DEFAULT 0,
    notes TEXT,
    organization_id UUID,
    created_by VARCHAR(100)
);

CREATE INDEX idx_sites_status ON sites(status);
CREATE INDEX idx_sites_platform ON sites(platform);
CREATE INDEX idx_sites_created ON sites(created_at DESC);
CREATE INDEX idx_sites_score ON sites(business_value_score DESC);
CREATE INDEX idx_sites_domain ON sites(domain);

-- Jobs Table: Track all discovery and processing jobs
CREATE TABLE jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('fingerprint', 'discovery', 'extraction', 'blueprint_update', 'validation')),
    method VARCHAR(50) CHECK (method IN ('static', 'browser', 'api', 'auto')),
    status VARCHAR(50) NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'success', 'failed', 'timeout', 'cancelled')),
    priority INT DEFAULT 0,
    attempt_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    error_code VARCHAR(50),
    error_message TEXT,
    worker_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    payload JSONB,
    result JSONB,
    duration_seconds INT,
    heartbeat_at TIMESTAMP
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_site_id ON jobs(site_id);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);
CREATE INDEX idx_jobs_priority ON jobs(priority DESC, created_at ASC);
CREATE INDEX idx_jobs_type ON jobs(job_type);
CREATE INDEX idx_jobs_worker ON jobs(worker_id);

-- Blueprints Table: Versioned site intelligence objects
CREATE TABLE blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    version INT NOT NULL,
    confidence_score FLOAT,
    categories_data JSONB NOT NULL DEFAULT '[]'::jsonb,
    endpoints_data JSONB NOT NULL DEFAULT '[]'::jsonb,
    render_hints_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    selectors_data JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    notes TEXT,
    UNIQUE(site_id, version)
);

CREATE INDEX idx_blueprints_site ON blueprints(site_id);
CREATE INDEX idx_blueprints_version ON blueprints(site_id, version DESC);
CREATE INDEX idx_blueprints_confidence ON blueprints(confidence_score DESC);

-- Selectors Table: Individual selectors and their performance
CREATE TABLE selectors (
    selector_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id UUID NOT NULL REFERENCES blueprints(blueprint_id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    css_selector VARCHAR(500),
    xpath VARCHAR(500),
    confidence FLOAT,
    generation_method VARCHAR(50) CHECK (generation_method IN ('llm', 'heuristic', 'manual', 'template')),
    test_pass_rate FLOAT,
    test_count INT DEFAULT 0,
    test_failures INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_tested_at TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_selectors_blueprint ON selectors(blueprint_id);
CREATE INDEX idx_selectors_field ON selectors(field_name);
CREATE INDEX idx_selectors_method ON selectors(generation_method);

-- Analytics Metrics Table: Time-series metrics for reporting
CREATE TABLE analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    discovery_time_seconds INT,
    num_categories_found INT,
    num_endpoints_found INT,
    selector_failure_rate FLOAT,
    fetch_cost_usd FLOAT,
    items_extracted INT,
    method VARCHAR(50),
    job_id UUID REFERENCES jobs(job_id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_metrics_site_date ON analytics_metrics(site_id, date DESC);
CREATE INDEX idx_metrics_date ON analytics_metrics(date DESC);

-- Templates Table: Reusable platform patterns
CREATE TABLE platform_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_name VARCHAR(100) NOT NULL,
    platform_variant VARCHAR(100),
    category_selectors JSONB,
    product_list_selectors JSONB,
    api_patterns JSONB,
    render_hints JSONB,
    confidence FLOAT,
    active BOOLEAN DEFAULT TRUE,
    match_patterns JSONB,  -- Patterns to detect this template
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_templates_platform ON platform_templates(platform_name);
CREATE INDEX idx_templates_active ON platform_templates(active);

-- LLM Calls Log: Track usage and cost
CREATE TABLE llm_calls_log (
    call_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(job_id),
    prompt_type VARCHAR(100),
    model VARCHAR(100),
    tokens_input INT,
    tokens_output INT,
    cost_usd FLOAT,
    latency_ms INT,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_llm_job ON llm_calls_log(job_id);
CREATE INDEX idx_llm_created ON llm_calls_log(created_at DESC);

-- ============================================================================
-- 2. AUDIT & CHANGE TRACKING
-- ============================================================================

-- Blueprint Changes: Track what changed between versions
CREATE TABLE blueprint_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    from_version INT,
    to_version INT NOT NULL,
    categories_added INT DEFAULT 0,
    categories_removed INT DEFAULT 0,
    selectors_updated INT DEFAULT 0,
    endpoints_changed INT DEFAULT 0,
    change_details JSONB,
    reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX idx_changes_site ON blueprint_changes(site_id);

-- Selector Failures: Track when selectors break
CREATE TABLE selector_failures (
    failure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    selector_id UUID NOT NULL REFERENCES selectors(selector_id) ON DELETE CASCADE,
    site_id UUID NOT NULL REFERENCES sites(site_id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(job_id),
    failure_reason VARCHAR(255),
    error_message TEXT,
    html_snapshot TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_failures_selector ON selector_failures(selector_id);
CREATE INDEX idx_failures_site ON selector_failures(site_id);
CREATE INDEX idx_failures_created ON selector_failures(created_at DESC);

-- Audit Log: All user actions
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    user_id VARCHAR(100),
    details JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- ============================================================================
-- 3. QUEUE & PROCESSING
-- ============================================================================

-- Job Queue State (for distributed processing)
CREATE TABLE job_queue_state (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    queue_name VARCHAR(100),
    position INT,
    enqueued_at TIMESTAMP NOT NULL DEFAULT NOW(),
    dequeued_at TIMESTAMP,
    UNIQUE(job_id)
);

CREATE INDEX idx_queue_name ON job_queue_state(queue_name);

-- Dead Letter Queue: Failed jobs for escalation
CREATE TABLE dead_letter_queue (
    dlq_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    reason VARCHAR(255),
    error_message TEXT,
    escalated BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP
);

CREATE INDEX idx_dlq_escalated ON dead_letter_queue(escalated);

-- ============================================================================
-- 4. USER & PERMISSIONS
-- ============================================================================

-- Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'product_lead', 'scraper_engineer', 'viewer')),
    organization_id UUID,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- API Keys Table
CREATE TABLE api_keys (
    key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_name VARCHAR(100),
    scopes VARCHAR(500),
    last_used TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_keys_user ON api_keys(user_id);

-- ============================================================================
-- 5. CACHING & SESSION
-- ============================================================================

-- Cache Table (for expensive computations)
CREATE TABLE cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    cache_value TEXT,
    ttl_seconds INT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_cache_expires ON cache(expires_at);

-- ============================================================================
-- 6. MATERIALIZED VIEWS (for analytics)
-- ============================================================================

-- Site Summary View
CREATE MATERIALIZED VIEW site_summary_view AS
SELECT
    s.site_id,
    s.domain,
    s.platform,
    s.status,
    s.complexity_score,
    s.business_value_score,
    COUNT(DISTINCT j.job_id) as total_jobs,
    SUM(CASE WHEN j.status = 'success' THEN 1 ELSE 0 END) as successful_jobs,
    AVG(CASE WHEN j.status = 'success' THEN j.duration_seconds END) as avg_job_duration,
    SUM(CASE WHEN j.status = 'failed' THEN 1 ELSE 0 END) as failed_jobs,
    MAX(j.created_at) as last_job_date,
    COUNT(DISTINCT b.version) as blueprint_versions
FROM sites s
LEFT JOIN jobs j ON s.site_id = j.site_id
LEFT JOIN blueprints b ON s.site_id = b.site_id
GROUP BY s.site_id, s.domain, s.platform, s.status, s.complexity_score, s.business_value_score;

CREATE INDEX idx_site_summary_status ON site_summary_view(status);

-- Method Performance View
CREATE MATERIALIZED VIEW method_performance_view AS
SELECT
    j.method,
    s.platform,
    COUNT(j.job_id) as total_jobs,
    SUM(CASE WHEN j.status = 'success' THEN 1 ELSE 0 END)::float / COUNT(j.job_id) as success_rate,
    AVG(j.duration_seconds) as avg_duration,
    AVG(am.fetch_cost_usd) as avg_cost
FROM jobs j
LEFT JOIN sites s ON j.site_id = s.site_id
LEFT JOIN analytics_metrics am ON j.job_id = am.job_id
WHERE j.status IN ('success', 'failed')
GROUP BY j.method, s.platform;

-- Selector Reliability View
CREATE MATERIALIZED VIEW selector_reliability_view AS
SELECT
    sel.selector_id,
    sel.field_name,
    bp.site_id,
    s.domain,
    sel.generation_method,
    sel.test_pass_rate,
    COUNT(sf.failure_id) as total_failures,
    CURRENT_DATE - sel.created_at::date as days_alive,
    CASE
        WHEN sel.test_pass_rate >= 0.9 THEN 'healthy'
        WHEN sel.test_pass_rate >= 0.7 THEN 'at_risk'
        ELSE 'failed'
    END as status
FROM selectors sel
JOIN blueprints bp ON sel.blueprint_id = bp.blueprint_id
JOIN sites s ON bp.site_id = s.site_id
LEFT JOIN selector_failures sf ON sel.selector_id = sf.selector_id
GROUP BY sel.selector_id, sel.field_name, bp.site_id, s.domain, 
         sel.generation_method, sel.test_pass_rate, sel.created_at;

-- ============================================================================
-- 7. TRIGGERS & FUNCTIONS
-- ============================================================================

-- Function: Update site.updated_at on any modification
CREATE OR REPLACE FUNCTION update_site_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_site_timestamp
BEFORE UPDATE ON sites
FOR EACH ROW
EXECUTE FUNCTION update_site_timestamp();

-- Function: Auto-update blueprint version
CREATE OR REPLACE FUNCTION auto_increment_blueprint_version()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.version IS NULL THEN
        NEW.version = (SELECT COALESCE(MAX(version), 0) + 1 FROM blueprints WHERE site_id = NEW.site_id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_version
BEFORE INSERT ON blueprints
FOR EACH ROW
EXECUTE FUNCTION auto_increment_blueprint_version();

-- Function: Log blueprint changes
CREATE OR REPLACE FUNCTION log_blueprint_change()
RETURNS TRIGGER AS $$
DECLARE
    prev_version INT;
    added_cats INT;
    removed_cats INT;
BEGIN
    IF TG_OP = 'INSERT' THEN
        prev_version = NEW.version - 1;
        
        -- Calculate changes (simplified)
        added_cats = jsonb_array_length(NEW.categories_data);
        
        INSERT INTO blueprint_changes (site_id, to_version, from_version, categories_added, created_by)
        VALUES (NEW.site_id, NEW.version, prev_version, added_cats, NEW.created_by);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_blueprint_change
AFTER INSERT ON blueprints
FOR EACH ROW
EXECUTE FUNCTION log_blueprint_change();

-- Function: Clean up expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM cache WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. STORED PROCEDURES
-- ============================================================================

-- Procedure: Get site with all related data
CREATE OR REPLACE FUNCTION get_site_with_blueprint(p_site_id UUID)
RETURNS TABLE (
    site_id UUID,
    domain VARCHAR,
    platform VARCHAR,
    status VARCHAR,
    blueprint_id UUID,
    blueprint_version INT,
    confidence_score FLOAT,
    categories_data JSONB,
    endpoints_data JSONB,
    selectors_data JSONB
) AS $$
SELECT
    s.site_id,
    s.domain,
    s.platform,
    s.status,
    b.blueprint_id,
    b.version,
    b.confidence_score,
    b.categories_data,
    b.endpoints_data,
    b.selectors_data
FROM sites s
LEFT JOIN blueprints b ON s.site_id = b.site_id AND b.version = (
    SELECT MAX(version) FROM blueprints WHERE site_id = s.site_id
)
WHERE s.site_id = p_site_id;
$$ LANGUAGE SQL STABLE;

-- Procedure: Get jobs for site with pagination
CREATE OR REPLACE FUNCTION get_site_jobs(
    p_site_id UUID,
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    job_id UUID,
    job_type VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP,
    duration_seconds INT
) AS $$
SELECT
    j.job_id,
    j.job_type,
    j.status,
    j.created_at,
    j.duration_seconds
FROM jobs j
WHERE j.site_id = p_site_id
ORDER BY j.created_at DESC
LIMIT p_limit OFFSET p_offset;
$$ LANGUAGE SQL STABLE;

-- ============================================================================
-- 9. CONSTRAINTS & CHECKS
-- ============================================================================

-- Add check constraints for data integrity
ALTER TABLE sites ADD CONSTRAINT check_complexity_score CHECK (complexity_score >= 0 AND complexity_score <= 1);
ALTER TABLE sites ADD CONSTRAINT check_business_value CHECK (business_value_score >= 0 AND business_value_score <= 1);
ALTER TABLE blueprints ADD CONSTRAINT check_blueprint_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1);
ALTER TABLE selectors ADD CONSTRAINT check_selector_confidence CHECK (confidence >= 0 AND confidence <= 1);

-- ============================================================================
-- 10. PERMISSIONS (for role-based access)
-- ============================================================================

-- Note: These would typically be managed through application-level access control,
-- but can be enforced at the database level using row-level security (RLS).

-- Example RLS policy (PostgreSQL 10+):
-- ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY sites_access ON sites
--   USING (organization_id = current_setting('app.organization_id')::uuid);

-- ============================================================================
-- 11. INDEXES FOR COMMON QUERIES
-- ============================================================================

-- Query: Recent sites by platform
CREATE INDEX idx_sites_platform_created ON sites(platform, created_at DESC);

-- Query: Jobs by status and type
CREATE INDEX idx_jobs_status_type ON jobs(status, job_type);

-- Query: Blueprints by confidence
CREATE INDEX idx_blueprints_site_confidence ON blueprints(site_id, confidence_score DESC);

-- Query: Analytics by site and date range
CREATE INDEX idx_metrics_site_date_method ON analytics_metrics(site_id, date DESC, method);

-- Query: LLM cost tracking
CREATE INDEX idx_llm_cost ON llm_calls_log(created_at DESC, cost_usd);

-- ============================================================================
-- 12. INITIAL DATA (Optional)
-- ============================================================================

-- Insert common platform templates
INSERT INTO platform_templates (platform_name, platform_variant, confidence, active, match_patterns)
VALUES
    ('shopify', NULL, 0.95, TRUE, '{"indicators": ["Shopify.AppBridge", "myshopify.com"]}'),
    ('magento', '1.x', 0.90, TRUE, '{"indicators": ["Magento_Js", "mage"]}'),
    ('magento', '2.x', 0.92, TRUE, '{"indicators": ["Magento_Js", "mage", "require.js"]}'),
    ('woocommerce', NULL, 0.88, TRUE, '{"indicators": ["wp-content", "woocommerce"]}'),
    ('bigcommerce', NULL, 0.89, TRUE, '{"indicators": ["bigcommerce", "storefront"]}')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 13. REFRESH MATERIALIZED VIEWS
-- ============================================================================

-- Refresh views periodically (via cron job or application)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY site_summary_view;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY method_performance_view;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY selector_reliability_view;

-- ============================================================================
-- SEED DATA FOR TESTING (Optional)
-- ============================================================================

-- Uncomment to populate test data:
/*

-- Insert test organizations
INSERT INTO users (username, email, role) VALUES
    ('admin', 'admin@example.com', 'admin'),
    ('product', 'product@example.com', 'product_lead')
ON CONFLICT DO NOTHING;

-- Insert test sites
INSERT INTO sites (domain, platform, status, complexity_score, business_value_score)
VALUES
    ('example-store-1.com', 'shopify', 'ready', 0.45, 0.85),
    ('example-store-2.com', 'magento', 'ready', 0.72, 0.92),
    ('example-store-3.com', 'custom', 'pending', 0.88, 0.65)
ON CONFLICT DO NOTHING;

*/

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

