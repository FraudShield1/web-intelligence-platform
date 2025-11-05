#!/usr/bin/env bash
set -euo pipefail

# Supabase local helper (macOS + Docker required)
# Usage: ./scripts/supabase_local.sh

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Please install Docker Desktop." >&2
  exit 1
fi

if ! command -v supabase >/dev/null 2>&1; then
  echo "Installing Supabase CLI (Homebrew)..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required to auto-install supabase. Install from https://brew.sh/" >&2
    exit 1
  fi
  brew install supabase/tap/supabase
fi

# Initialize supabase project directory if missing
if [[ ! -d "supabase" ]]; then
  supabase init
fi

# Start local supabase stack
supabase start

# Extract connection details
DB_PORT=54322
DB_HOST=127.0.0.1
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres

cat <<EOF

✅ Supabase local is running.

Connection:
  Host:     $DB_HOST
  Port:     $DB_PORT
  User:     $DB_USER
  Password: $DB_PASSWORD
  Database: $DB_NAME

Set backend env:
  export DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

Run migrations:
  (cd backend && DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME \
    bash scripts/db_migrate.sh)

Run backend locally:
  (cd backend && DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME \
    uvicorn app.main:app --host 0.0.0.0 --port 8000)

Stop Supabase:
  supabase stop
EOF
