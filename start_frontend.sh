#!/bin/bash
cd "$(dirname "$0")/frontend"

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
  echo "Creating .env.local..."
  cat > .env.local << 'EOF'
REACT_APP_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://aeajgihhgplxcvcsiqeo.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlYWpnaWhoZ3BseGN2Y3NpcWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzMjY1MzMsImV4cCI6MjA3NzkwMjUzM30.KgZrArrNkk_8ujSMhu-QL5TCG9Elv9YHdTp4oxScbKM
EOF
fi

echo "Starting frontend on http://localhost:3000"
echo ""

npm start

