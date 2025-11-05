# 🎯 Final Setup Steps

## ✅ What's Already Done

- ✅ Code pushed to GitHub
- ✅ Frontend deployed to Vercel
- ✅ Backend deployed to Vercel
- ✅ All environment variables configured
- ✅ Database (Supabase) connected
- ✅ Redis (Upstash) connected
- ✅ LLM (OpenRouter) integrated

---

## 🔓 Step 1: Disable Vercel Auth Protection

Your deployments are currently protected by Vercel authentication. To make them publicly accessible:

### Frontend
1. Go to: https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend
2. Click **Settings** (top menu)
3. Scroll down to **Deployment Protection**
4. Select **"Only Preview Deployments"** or **"Disabled"**
5. Click **Save**

### Backend
1. Go to: https://vercel.com/dedes-projects-ee4b20e7/backend
2. Click **Settings** (top menu)
3. Scroll down to **Deployment Protection**
4. Select **"Only Preview Deployments"** or **"Disabled"**
5. Click **Save**

**⚠️ Note:** It may take 1-2 minutes for the changes to propagate.

---

## 🔐 Step 2: Add GitHub Secrets

GitHub Actions workers need these secrets to run background jobs.

### Quick Method (Copy-Paste)

Go to: https://github.com/FraudShield1/web-intelligence-platform/settings/secrets/actions

Click **"New repository secret"** for each:

| Secret Name | Value |
|-------------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres` |
| `UPSTASH_REDIS_REST_URL` | `https://pure-halibut-27195.upstash.io` |
| `UPSTASH_REDIS_REST_TOKEN` | `AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU` |
| `OPENROUTER_API_KEY` | `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` |
| `JWT_SECRET` | `ohoWjQJpwnREMQgZDBVWnDSsTq++sezllwaH5j07gcw=` |

### Using GitHub CLI (Alternative)

If you have GitHub CLI installed:

```bash
gh secret set DATABASE_URL -b 'postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres' --repo FraudShield1/web-intelligence-platform

gh secret set UPSTASH_REDIS_REST_URL -b 'https://pure-halibut-27195.upstash.io' --repo FraudShield1/web-intelligence-platform

gh secret set UPSTASH_REDIS_REST_TOKEN -b 'AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU' --repo FraudShield1/web-intelligence-platform

gh secret set OPENROUTER_API_KEY -b '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' --repo FraudShield1/web-intelligence-platform

gh secret set JWT_SECRET -b 'ohoWjQJpwnREMQgZDBVWnDSsTq++sezllwaH5j07gcw=' --repo FraudShield1/web-intelligence-platform
```

---

## 🧪 Step 3: Test Your Deployment

### Test Backend (after disabling auth)
```bash
curl https://backend-ea0pwqewg-dedes-projects-ee4b20e7.vercel.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T...",
  "database": "connected"
}
```

### Test Frontend
Open: https://web-intelligence-frontend-p6ci327lh-dedes-projects-ee4b20e7.vercel.app

Should show the dashboard!

### Create Admin User
```bash
curl -X POST https://backend-ea0pwqewg-dedes-projects-ee4b20e7.vercel.app/api/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePassword123"}'
```

### Login & Get Token
```bash
curl -X POST https://backend-ea0pwqewg-dedes-projects-ee4b20e7.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"SecurePassword123"}'
```

Copy the `access_token` from the response.

### Add Your First Site
```bash
TOKEN="paste_your_token_here"

curl -X POST https://backend-ea0pwqewg-dedes-projects-ee4b20e7.vercel.app/api/sites \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","name":"Example Site"}'
```

---

## 🚀 Step 4: Test Workers

### Run Fingerprint Worker Manually

1. Go to: https://github.com/FraudShield1/web-intelligence-platform/actions
2. Click on **"Fingerprint Worker"** workflow
3. Click **"Run workflow"** button (top right)
4. Select branch: **main**
5. Click green **"Run workflow"** button
6. Wait for completion (~30 seconds)
7. Click on the workflow run to see logs

**Expected:** Green checkmark ✅

---

## ✅ Success Checklist

Your platform is fully operational when:

- [ ] Frontend loads without authentication prompt
- [ ] Backend `/api/health` returns 200 OK
- [ ] Can create admin user via `/api/auth/bootstrap`
- [ ] Can login and receive JWT token
- [ ] Can add a site via API or UI
- [ ] GitHub Actions worker runs successfully
- [ ] Site appears in database with fingerprint data

---

## 📊 Monitoring Your Platform

### Usage Dashboards
- **Vercel Frontend:** https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend
- **Vercel Backend:** https://vercel.com/dedes-projects-ee4b20e7/backend
- **GitHub Actions:** https://github.com/FraudShield1/web-intelligence-platform/actions
- **Supabase:** https://app.supabase.com/project/aeajgihhgplxcvcsiqeo
- **Upstash:** https://console.upstash.com/

### Free Tier Limits

| Service | Monthly Limit | Alert When |
|---------|---------------|------------|
| Vercel | 100GB bandwidth | > 80GB |
| GitHub Actions | 2000 minutes | > 1600 min |
| Supabase | 500MB database | > 400MB |
| Upstash | 10k requests/day | > 8k/day |

---

## 🆘 Troubleshooting

### "Authentication Required" when accessing Vercel URLs
**Solution:** Disable Deployment Protection in Vercel Settings (see Step 1)

### Backend returns 500 error
**Check:**
1. Vercel logs: `vercel logs <backend-url>`
2. Environment variables are set: Go to Vercel Dashboard → Settings → Environment Variables
3. Supabase database is awake (free tier sleeps)

### Workers fail in GitHub Actions
**Check:**
1. All secrets are added: https://github.com/FraudShield1/web-intelligence-platform/settings/secrets/actions
2. Workflow file exists: `.github/workflows/worker_fingerprint.yml`
3. Actions are enabled: Repository Settings → Actions → General

### Frontend shows blank page
**Check:**
1. Browser console for errors (F12)
2. `VITE_API_URL` environment variable in Vercel
3. Backend is responding

---

## 🎉 You're All Set!

Once you complete these 4 steps, your Web Intelligence Platform will be fully operational and ready to analyze websites at scale!

**Cost:** < $1/month on 100% free infrastructure 🎊

**Questions?** Check:
- `DEPLOYMENT_SUCCESS.md` - Complete deployment guide
- `ENVIRONMENT_VARS.md` - All credentials
- `API_SPEC.md` - API documentation
- `ARCHITECTURE.md` - System architecture

**Happy scraping! 🕷️✨**

