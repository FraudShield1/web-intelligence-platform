# 🔧 Fix Database Connection - Railway Setup

## ✅ Problem Identified:

Your backend is healthy, but the database connection is failing with:
```
Connection refused (Errno 111)
```

This means the `DATABASE_URL` environment variable in Railway is pointing to the wrong host (probably `localhost`).

---

## 🎯 Solution: Update Railway Environment Variables

### Step 1: Go to Railway Dashboard

1. Open: https://railway.app/
2. Select your project: **web-intelligence-platform-production**
3. Click on your **backend service**
4. Go to **Variables** tab

### Step 2: Set the Correct DATABASE_URL

**Delete the old `DATABASE_URL` if it exists, and add this:**

```
DATABASE_URL=postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:5432/postgres?sslmode=require
```

**Important Notes:**
- Use port `5432` (direct connection - more reliable from Railway)
- Use `postgresql+asyncpg://` for async SQLAlchemy
- Include `?sslmode=require` at the end (our code handles SSL properly now)

### Step 3: Verify Other Environment Variables

Make sure these are also set in Railway:

```bash
# Redis (Upstash)
REDIS_URL=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379

UPSTASH_REDIS_REST_URL=https://pure-halibut-27195.upstash.io
UPSTASH_REDIS_REST_TOKEN=AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU

# Celery (using Redis)
CELERY_BROKER_URL=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379

# LLM
OPENROUTER_API_KEY=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

# CORS (allow your frontend)
CORS_ORIGINS=["https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app","https://web-intelligence-platform-production.up.railway.app"]

# Security
SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)
JWT_SECRET=your-jwt-secret-change-in-production-$(openssl rand -hex 32)

# App Config
DEBUG=false
ENABLE_DOCS=true
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
```

### Step 4: Restart the Service

After adding/updating the variables:
1. Railway will automatically redeploy
2. Wait ~2 minutes
3. Test again!

---

## 🧪 Test After Fix:

Once Railway redeploys, run these in your terminal:

```bash
# Test database connection
curl https://web-intelligence-platform-production.up.railway.app/debug/db

# Should return: {"status":"success", "message":"Database connection working"}
```

```bash
# Test list sites
curl https://web-intelligence-platform-production.up.railway.app/api/v1/sites

# Should return: {"total":0,"limit":50,"offset":0,"sites":[]}
```

---

## ✅ Once Fixed:

Your platform will be 100% operational! You'll be able to:
1. Create sites via API
2. Run fingerprinting jobs
3. View analytics
4. Export blueprints
5. Full end-to-end functionality!

---

## 📝 Quick Checklist:

- [ ] Go to Railway dashboard
- [ ] Select backend service
- [ ] Click Variables tab
- [ ] Update `DATABASE_URL` to the correct Supabase URL (port 6543)
- [ ] Add other environment variables (Redis, OpenRouter, etc.)
- [ ] Wait for automatic redeploy (~2 mins)
- [ ] Test `/debug/db` endpoint
- [ ] Test `/api/v1/sites` endpoint
- [ ] 🎉 Platform 100% working!

---

**Let me know once you've updated the Railway variables, and I'll test everything!** 🚀

