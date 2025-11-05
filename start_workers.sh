#!/bin/bash
cd "$(dirname "$0")/backend"

export PYTHONPATH="$(pwd)"
export DATABASE_URL='postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres'
export REDIS_URL='redis://localhost:6379/0'
export RABBITMQ_URL='amqp://guest:guest@localhost:5672/'

echo "Starting Celery workers..."
echo ""

celery -A app.celery_app worker --loglevel=info --concurrency=2

