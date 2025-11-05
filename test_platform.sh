#!/bin/bash

# Test Platform - Complete End-to-End Testing
# Run this after creating admin user

BACKEND_URL="https://web-intelligence-platform-production.up.railway.app"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="SecurePassword123"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Testing Web Intelligence Platform                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Health Check
echo "1️⃣ Testing Health Check..."
HEALTH=$(curl -s "$BACKEND_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
    echo "   $HEALTH"
else
    echo "   ❌ Health check failed"
    echo "   $HEALTH"
fi
echo ""

# Test 2: API Root
echo "2️⃣ Testing API Root..."
API_ROOT=$(curl -s "$BACKEND_URL/")
if echo "$API_ROOT" | grep -q "Web Intelligence Platform"; then
    echo "   ✅ API root responding"
else
    echo "   ❌ API root failed"
fi
echo ""

# Test 3: API Docs
echo "3️⃣ Testing API Documentation..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
if [ "$DOCS_STATUS" = "200" ]; then
    echo "   ✅ API docs available at $BACKEND_URL/docs"
else
    echo "   ⚠️  API docs status: $DOCS_STATUS"
fi
echo ""

# Test 4: Login
echo "4️⃣ Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Login successful!"
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        echo "   ✅ Token received"
        echo ""
        
        # Test 5: List Sites
        echo "5️⃣ Testing Sites Endpoint..."
        SITES=$(curl -s "$BACKEND_URL/api/v1/sites" \
            -H "Authorization: Bearer $TOKEN")
        if echo "$SITES" | grep -q "sites"; then
            echo "   ✅ Sites endpoint working"
            echo "   $SITES"
        else
            echo "   ⚠️  Sites response: $SITES"
        fi
        echo ""
        
        # Test 6: Dashboard Analytics
        echo "6️⃣ Testing Dashboard Analytics..."
        ANALYTICS=$(curl -s "$BACKEND_URL/api/v1/analytics/dashboard" \
            -H "Authorization: Bearer $TOKEN")
        if echo "$ANALYTICS" | grep -q "total_sites"; then
            echo "   ✅ Analytics endpoint working"
            echo "   $ANALYTICS"
        else
            echo "   ⚠️  Analytics response: $ANALYTICS"
        fi
        echo ""
        
        # Test 7: Create Test Site
        echo "7️⃣ Testing Create Site..."
        NEW_SITE=$(curl -s -X POST "$BACKEND_URL/api/v1/sites" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"url":"https://example.com","name":"Test Site","description":"Testing site creation"}')
        
        if echo "$NEW_SITE" | grep -q "site_id"; then
            echo "   ✅ Site created successfully!"
            echo "   $NEW_SITE"
            
            # Extract site ID
            SITE_ID=$(echo "$NEW_SITE" | python3 -c "import sys, json; print(json.load(sys.stdin)['site_id'])" 2>/dev/null)
            if [ -n "$SITE_ID" ]; then
                echo "   Site ID: $SITE_ID"
            fi
        else
            echo "   ⚠️  Site creation response: $NEW_SITE"
        fi
        echo ""
        
    else
        echo "   ⚠️  Could not extract token"
    fi
else
    echo "   ❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
    echo ""
    echo "   Make sure you:"
    echo "   1. Ran supabase_schema.sql in Supabase"
    echo "   2. Ran create_admin_user.sql in Supabase"
    echo "   3. User exists with email: $ADMIN_EMAIL"
fi
echo ""

# Test 8: Frontend
echo "8️⃣ Testing Frontend..."
FRONTEND_URL="https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend is live at $FRONTEND_URL"
else
    echo "   ⚠️  Frontend status: $FRONTEND_STATUS"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  Testing Complete!                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📖 Next Steps:"
echo "   1. If login failed, run create_admin_user.sql in Supabase"
echo "   2. Open frontend: $FRONTEND_URL"
echo "   3. Login with: $ADMIN_EMAIL / $ADMIN_PASSWORD"
echo "   4. Start adding sites!"
echo ""

