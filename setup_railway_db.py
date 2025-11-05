#!/usr/bin/env python3
"""Setup Railway PostgreSQL database"""
import psycopg2
import sys

DATABASE_URL = "postgresql://postgres:igXxDjLmfzMAchOxbjCVerkRvCnOuIFv@trolley.proxy.rlwy.net:41967/railway"

# Read the SQL file
with open('railway_db_setup.sql', 'r') as f:
    sql = f.read()

try:
    print("🔌 Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("📦 Running schema setup...")
    cursor.execute(sql)
    
    print("✅ Database setup complete!")
    print("")
    print("🔐 Admin credentials:")
    print("   Email: admin@example.com")
    print("   Password: SecurePassword123")
    print("")
    print("🎉 Railway PostgreSQL is ready!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("")
    print("💡 Alternative: Use Railway dashboard")
    print("   1. Go to Railway → PostgreSQL → Data → Query")
    print("   2. Copy contents of railway_db_setup.sql")
    print("   3. Paste and run")
    sys.exit(1)

