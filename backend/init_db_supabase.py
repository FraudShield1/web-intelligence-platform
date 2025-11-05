"""Initialize Supabase database with tables"""
import asyncio
import asyncpg
import sys

DATABASE_URL = "postgresql://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:5432/postgres"

async def init_schema():
    """Create database schema"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to Supabase")
        
        # Create sites table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                site_id UUID PRIMARY KEY,
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
            )
        ''')
        print("✅ Created sites table")
        
        # Create users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255),
                role VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        print("✅ Created users table")
        
        # Create blueprints table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS blueprints (
                blueprint_id UUID PRIMARY KEY,
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
            )
        ''')
        print("✅ Created blueprints table")
        
        # Create selectors table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS selectors (
                selector_id UUID PRIMARY KEY,
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
            )
        ''')
        print("✅ Created selectors table")
        
        # Create jobs table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id UUID PRIMARY KEY,
                site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
                job_type VARCHAR(50) NOT NULL,
                method VARCHAR(50),
                status VARCHAR(50),
                priority INTEGER,
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
            )
        ''')
        print("✅ Created jobs table")
        
        # Create analytics_metrics table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS analytics_metrics (
                metric_id UUID PRIMARY KEY,
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
            )
        ''')
        print("✅ Created analytics_metrics table")
        
        print("\n✅ All tables created successfully!")
        print(f"Database: {DATABASE_URL.split('@')[1]}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(init_schema())
    sys.exit(0 if success else 1)

