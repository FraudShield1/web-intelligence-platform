#!/bin/bash

# Add Environment Variables to Vercel Projects
# Run this script to configure all necessary environment variables

set -e

export PATH="$HOME/.local/bin:$PATH"
VERCEL="$HOME/.local/bin/vercel"

echo "🔐 Adding Environment Variables to Vercel"
echo "=========================================="
echo ""

# Frontend Environment Variables
echo "📱 Frontend Variables..."
cd "/Users/naouri/Downloads/Web Intelligence Platform/frontend"

echo "Adding VITE_API_URL..."
echo "https://backend-ehtwmhrfr-dedes-projects-ee4b20e7.vercel.app/api" | $VERCEL env add VITE_API_URL production

echo "Adding VITE_SUPABASE_URL..."
echo "https://aeajgihhgplxcvcsiqeo.supabase.co" | $VERCEL env add VITE_SUPABASE_URL production

echo "Adding VITE_SUPABASE_ANON_KEY..."
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlYWpnaWhoZ3BseGN2Y3NpcWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzMjY1MzMsImV4cCI6MjA3NzkwMjUzM30.KgZrArrNkk_8ujSMhu-QL5TCG9Elv9YHdTp4oxScbKM" | $VERCEL env add VITE_SUPABASE_ANON_KEY production

echo "✅ Frontend variables added!"
echo ""

# Backend Environment Variables
echo "⚙️  Backend Variables..."
cd "/Users/naouri/Downloads/Web Intelligence Platform/backend"

echo "Adding DATABASE_URL..."
echo "postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres" | $VERCEL env add DATABASE_URL production

echo "Adding UPSTASH_REDIS_REST_URL..."
echo "https://pure-halibut-27195.upstash.io" | $VERCEL env add UPSTASH_REDIS_REST_URL production

echo "Adding UPSTASH_REDIS_REST_TOKEN..."
echo "AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU" | $VERCEL env add UPSTASH_REDIS_REST_TOKEN production

echo "Adding OPENROUTER_API_KEY..."
echo "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" | $VERCEL env add OPENROUTER_API_KEY production

echo "Generating JWT_SECRET..."
JWT_SECRET=$(openssl rand -base64 32)
echo "$JWT_SECRET" | $VERCEL env add JWT_SECRET production

echo "Adding CORS_ORIGINS..."
echo "[\"https://web-intelligence-frontend-8hyx7bmif-dedes-projects-ee4b20e7.vercel.app\"]" | $VERCEL env add CORS_ORIGINS production

echo "✅ Backend variables added!"
echo ""

echo "🎉 All Environment Variables Added!"
echo "===================================="
echo ""
echo "⚡ Redeploying to apply changes..."
echo ""

# Redeploy frontend
echo "📱 Redeploying frontend..."
cd "/Users/naouri/Downloads/Web Intelligence Platform/frontend"
$VERCEL --prod --yes

echo ""

# Redeploy backend  
echo "⚙️  Redeploying backend..."
cd "/Users/naouri/Downloads/Web Intelligence Platform/backend"
$VERCEL --prod --yes

echo ""
echo "✅ Deployment Complete!"
echo "======================="
echo ""
echo "Frontend: https://web-intelligence-frontend-8hyx7bmif-dedes-projects-ee4b20e7.vercel.app"
echo "Backend:  https://backend-ehtwmhrfr-dedes-projects-ee4b20e7.vercel.app"
echo ""
echo "🧪 Test your deployment:"
echo "  curl https://backend-ehtwmhrfr-dedes-projects-ee4b20e7.vercel.app/api/health"
echo ""

