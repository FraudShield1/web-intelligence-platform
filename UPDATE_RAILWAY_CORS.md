# 🔧 FIX: Network Error - Update Railway CORS Settings

## ❌ Problem:
Frontend shows: **"Failed to load metrics: Network Error"**

**Cause:** Railway backend is blocking requests from your Vercel frontend due to CORS (Cross-Origin Resource Sharing) restrictions.

---

## ✅ Solution: Add Frontend URL to CORS_ORIGINS

### Quick Fix (1 minute):

1. **Go to Railway Dashboard:**
   - https://railway.app/
   - Select your **backend service** (NOT PostgreSQL)
   - Click **"Variables"** tab

2. **Add/Update CORS_ORIGINS:**
   
   **If CORS_ORIGINS exists:** Click to edit it
   
   **If it doesn't exist:** Click "+ New Variable"
   
   **Set:**
   - **Name:** `CORS_ORIGINS`
   - **Value:** 
   ```json
   ["https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app","http://localhost:3000","http://localhost:5173"]
   ```

3. **Save**
   - Railway will automatically redeploy (~2 minutes)

---

## 🧪 Test After Deployment

Wait 2 minutes for Railway to redeploy, then:

1. **Open frontend:** https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app
2. **Check browser console** (F12 → Console tab)
3. **Should see:** Dashboard loads, no CORS errors!

---

## 🔍 Verify CORS is Working

**Open browser console (F12) and check:**

**Before fix:**
```
Access to XMLHttpRequest at 'https://web-intelligence-platform-production.up.railway.app/api/v1/analytics/dashboard'
from origin 'https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app' 
has been blocked by CORS policy
```

**After fix:**
```
✅ No CORS errors
✅ Network requests succeed
✅ Dashboard data loads
```

---

## 💡 What is CORS?

CORS (Cross-Origin Resource Sharing) is a security feature that prevents websites from making requests to different domains unless explicitly allowed.

**Your setup:**
- Frontend: `https://web-intelligence-frontend-...vercel.app` (Domain A)
- Backend: `https://web-intelligence-platform-...railway.app` (Domain B)

Backend must explicitly allow requests from Frontend's domain.

---

## 📋 Complete Railway Environment Variables

For reference, here are ALL the env vars you should have in Railway:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:igXxDjLmfzMAchOxbjCVerkRvCnOuIFv@trolley.proxy.rlwy.net:41967/railway

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://pure-halibut-27195.upstash.io
UPSTASH_REDIS_REST_TOKEN=AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU

# Celery
CELERY_BROKER_URL=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379

# LLM
OPENROUTER_API_KEY=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

# CORS (THIS IS THE IMPORTANT ONE!)
CORS_ORIGINS=["https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app","http://localhost:3000","http://localhost:5173"]

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production

# App Config
DEBUG=false
ENABLE_DOCS=true
LOG_LEVEL=INFO
```

---

## ⚡ After CORS is Fixed:

Your frontend will be **fully functional**:
- ✅ Dashboard loads with metrics
- ✅ Sites page shows data
- ✅ Jobs page shows data  
- ✅ Analytics work
- ✅ No network errors!

---

**👉 Go to Railway now and add the CORS_ORIGINS variable, then wait 2 mins for redeploy!** 🚀

