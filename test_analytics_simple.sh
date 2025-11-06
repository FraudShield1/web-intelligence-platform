#!/bin/bash

echo "🧪 Testing Analytics Endpoint - Simple Test"
echo ""

BACKEND="https://web-intelligence-platform-production.up.railway.app"

echo "1️⃣ Health Check:"
HEALTH=$(curl -s "$BACKEND/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend not responding"
    exit 1
fi
echo ""

echo "2️⃣ Testing Analytics Dashboard:"
echo "   URL: $BACKEND/api/v1/analytics/dashboard?date_range=7d"
echo ""

RESPONSE=$(curl -s "$BACKEND/api/v1/analytics/dashboard?date_range=7d")

if [ "$RESPONSE" == "Internal Server Error" ]; then
    echo "   ❌ Still getting 500 error"
    echo "   This means Railway hasn't deployed the code fix yet"
    echo ""
    echo "   ⏳ Wait another 2-3 minutes and try again"
    echo "   Or check Railway deployment logs for errors"
    exit 1
fi

if echo "$RESPONSE" | grep -q "total_sites"; then
    echo "   ✅ Analytics working!"
    echo ""
    echo "   Response:"
    echo "$RESPONSE" | python3 -m json.tool | head -20
    exit 0
else
    echo "   ❌ Unexpected response:"
    echo "$RESPONSE"
    exit 1
fi

