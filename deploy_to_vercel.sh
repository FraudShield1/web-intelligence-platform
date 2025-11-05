#!/bin/bash

# Deploy Web Intelligence Platform to Vercel
# This script will guide you through deploying frontend and backend

set -e

export PATH="$HOME/.local/bin:$PATH"
VERCEL="$HOME/.local/bin/vercel"

echo "🚀 Web Intelligence Platform - Vercel Deployment"
echo "================================================="
echo ""

# Check if logged in
echo "📝 Step 1: Login to Vercel"
echo "If you're not logged in, Vercel will open a browser for authentication."
echo ""
$VERCEL whoami 2>/dev/null || $VERCEL login

echo ""
echo "✅ Logged in successfully!"
echo ""

# Deploy Frontend
echo "🎨 Step 2: Deploying Frontend..."
echo "================================"
cd frontend

echo "Installing dependencies..."
npm install

echo ""
echo "Deploying to Vercel..."
echo "When prompted, use these settings:"
echo "  - Set up and deploy: Yes"
echo "  - Link to existing project: No (create new)"
echo "  - Project name: web-intelligence-frontend"
echo "  - Build command: npm run build"
echo "  - Output directory: dist"
echo ""

$VERCEL --prod --yes --name web-intelligence-frontend

FRONTEND_URL=$($VERCEL ls web-intelligence-frontend --scope $(vercel whoami) 2>/dev/null | grep -o 'https://[^ ]*' | head -1 || echo "")

echo ""
echo "✅ Frontend deployed!"
if [ ! -z "$FRONTEND_URL" ]; then
    echo "   URL: $FRONTEND_URL"
fi
echo ""

# Deploy Backend
echo "⚙️  Step 3: Deploying Backend..."
echo "================================"
cd ../backend

echo ""
echo "Deploying to Vercel..."
echo "When prompted, use these settings:"
echo "  - Set up and deploy: Yes"
echo "  - Link to existing project: No (create new)"
echo "  - Project name: web-intelligence-backend"
echo ""

$VERCEL --prod --yes --name web-intelligence-backend

BACKEND_URL=$($VERCEL ls web-intelligence-backend --scope $(vercel whoami) 2>/dev/null | grep -o 'https://[^ ]*' | head -1 || echo "")

echo ""
echo "✅ Backend deployed!"
if [ ! -z "$BACKEND_URL" ]; then
    echo "   URL: $BACKEND_URL"
fi
echo ""

# Summary
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
if [ ! -z "$FRONTEND_URL" ]; then
    echo "Frontend: $FRONTEND_URL"
fi
if [ ! -z "$BACKEND_URL" ]; then
    echo "Backend:  $BACKEND_URL"
fi
echo ""
echo "⚠️  IMPORTANT: Next Steps"
echo "========================="
echo ""
echo "1. Add Environment Variables to Frontend:"
echo "   cd frontend"
echo "   vercel env add VITE_API_URL production"
echo "   → Enter: ${BACKEND_URL}/api (or your backend URL)"
echo ""
echo "   vercel env add VITE_SUPABASE_URL production"
echo "   → Enter: https://aeajgihhgplxcvcsiqeo.supabase.co"
echo ""
echo "   vercel env add VITE_SUPABASE_ANON_KEY production"
echo "   → See ENVIRONMENT_VARS.md for the key"
echo ""
echo "2. Add Environment Variables to Backend:"
echo "   cd backend"
echo "   vercel env add DATABASE_URL production"
echo "   vercel env add UPSTASH_REDIS_REST_URL production"
echo "   vercel env add UPSTASH_REDIS_REST_TOKEN production"
echo "   vercel env add OPENROUTER_API_KEY production"
echo "   vercel env add JWT_SECRET production"
echo "   vercel env add CORS_ORIGINS production"
echo ""
echo "   → See ENVIRONMENT_VARS.md for all values"
echo ""
echo "3. Redeploy after adding env vars:"
echo "   vercel --prod (in each directory)"
echo ""
echo "4. Add GitHub Secrets for workers:"
echo "   → Go to: https://github.com/FraudShield1/web-intelligence-platform/settings/secrets/actions"
echo "   → Add all secrets from ENVIRONMENT_VARS.md"
echo ""
echo "📚 For detailed instructions, see:"
echo "   - DEPLOY_CHECKLIST.md"
echo "   - ENVIRONMENT_VARS.md"
echo ""

