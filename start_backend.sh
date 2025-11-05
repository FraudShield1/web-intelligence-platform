#!/bin/bash
cd "$(dirname "$0")/backend"

export PYTHONPATH="$(pwd)"
export DATABASE_URL='postgresql+asyncpg://postgres.aeajgihhgplxcvcsiqeo:Xonique99@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
export CORS_ORIGINS='["http://localhost:3000"]'
export ENABLE_DOCS=True
export DEBUG=True
export RATE_LIMIT_ENABLED=False

echo "Starting backend on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

