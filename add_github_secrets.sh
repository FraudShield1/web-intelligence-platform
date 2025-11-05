#!/bin/bash

# Add GitHub Secrets for Workers
# This script will guide you through adding secrets to GitHub

set -e

echo "🔐 GitHub Secrets Setup for Workers"
echo "===================================="
echo ""
echo "To add GitHub Secrets, you need to use the GitHub CLI or web interface."
echo ""
echo "📋 Secrets to Add:"
echo ""
echo "Go to: https://github.com/FraudShield1/web-intelligence-platform/settings/secrets/actions"
echo ""
echo "Click 'New repository secret' for each of these:"
echo ""
echo "1. DATABASE_URL"
echo "   Value: postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres"
echo ""
echo "2. UPSTASH_REDIS_REST_URL"
echo "   Value: https://pure-halibut-27195.upstash.io"
echo ""
echo "3. UPSTASH_REDIS_REST_TOKEN"
echo "   Value: AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU"
echo ""
echo "4. OPENROUTER_API_KEY"
echo "   Value: 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"
echo ""
echo "5. JWT_SECRET"
echo "   Generate with: openssl rand -base64 32"

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)
echo "   Suggested value: $JWT_SECRET"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Or use GitHub CLI (if installed):"
echo ""
echo "gh secret set DATABASE_URL -b 'postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres' --repo FraudShield1/web-intelligence-platform"
echo ""
echo "gh secret set UPSTASH_REDIS_REST_URL -b 'https://pure-halibut-27195.upstash.io' --repo FraudShield1/web-intelligence-platform"
echo ""
echo "gh secret set UPSTASH_REDIS_REST_TOKEN -b 'AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU' --repo FraudShield1/web-intelligence-platform"
echo ""
echo "gh secret set OPENROUTER_API_KEY -b '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' --repo FraudShield1/web-intelligence-platform"
echo ""
echo "gh secret set JWT_SECRET -b '$JWT_SECRET' --repo FraudShield1/web-intelligence-platform"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if gh CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected!"
    echo ""
    read -p "Would you like to add secrets automatically using GitHub CLI? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Adding secrets..."
        
        gh secret set DATABASE_URL -b "postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres" --repo FraudShield1/web-intelligence-platform
        echo "✅ Added DATABASE_URL"
        
        gh secret set UPSTASH_REDIS_REST_URL -b "https://pure-halibut-27195.upstash.io" --repo FraudShield1/web-intelligence-platform
        echo "✅ Added UPSTASH_REDIS_REST_URL"
        
        gh secret set UPSTASH_REDIS_REST_TOKEN -b "AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU" --repo FraudShield1/web-intelligence-platform
        echo "✅ Added UPSTASH_REDIS_REST_TOKEN"
        
        gh secret set OPENROUTER_API_KEY -b "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" --repo FraudShield1/web-intelligence-platform
        echo "✅ Added OPENROUTER_API_KEY"
        
        gh secret set JWT_SECRET -b "$JWT_SECRET" --repo FraudShield1/web-intelligence-platform
        echo "✅ Added JWT_SECRET"
        
        echo ""
        echo "🎉 All GitHub Secrets added successfully!"
        echo ""
        echo "Test by running a workflow:"
        echo "  https://github.com/FraudShield1/web-intelligence-platform/actions"
    fi
else
    echo "ℹ️  GitHub CLI not installed. Please add secrets manually via the web interface."
fi

echo ""
echo "✅ Setup complete!"

