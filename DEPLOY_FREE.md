# 🚀 Deploy to Production (100% Free)

## Prerequisites

- GitHub account (free)
- Vercel account (free) - sign up at vercel.com
- Upstash account (free) - sign up at upstash.com
- Supabase account (free) - already have ✅

---

## Step 1: Setup Upstash Redis (5 minutes)

### 1.1 Create Account
1. Go to https://upstash.com
2. Sign up with GitHub (free)
3. Click "Create Database"

### 1.2 Create Redis Database
- **Name:** web-intelligence
- **Type:** Regional (free tier)
- **Region:** Choose closest to you
- Click "Create"

### 1.3 Get Connection Details
After creation, copy:
- **UPSTASH_REDIS_REST_URL:** `https://xxxxx.upstash.io`
- **UPSTASH_REDIS_REST_TOKEN:** `AYxxxxxxxxxxxx`

Save these for Step 3!

---

## Step 2: Deploy Frontend to Vercel (5 minutes)

### 2.1 Install Vercel CLI
```bash
npm i -g vercel
```

### 2.2 Login to Vercel
```bash
vercel login
```

### 2.3 Deploy Frontend
```bash
cd /Users/naouri/Downloads/Web\ Intelligence\ Platform/frontend
vercel --prod
```

Follow prompts:
- Link to Git? **Yes** (recommended)
- Which scope? Your account
- Link to existing project? **No**
- Project name? **web-intelligence-frontend**
- Directory? **./`**
- Override settings? **No**

### 2.4 Add Environment Variables
Go to Vercel Dashboard → Project → Settings → Environment Variables

Add:
```
VITE_API_URL=https://your-backend.vercel.app/api
VITE_SUPABASE_URL=https://aeajgihhgplxcvcsiqeo.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Note:** You'll update `VITE_API_URL` after deploying backend (Step 3)

### 2.5 Redeploy
```bash
vercel --prod
```

Your frontend is now live! Note the URL (e.g., `https://web-intelligence-frontend.vercel.app`)

---

## Step 3: Deploy Backend API to Vercel (5 minutes)

### 3.1 Deploy Backend
```bash
cd /Users/naouri/Downloads/Web\ Intelligence\ Platform/backend
vercel --prod
```

Follow prompts (same as frontend)

### 3.2 Add Environment Variables
Go to Vercel Dashboard → Backend Project → Settings → Environment Variables

Add:
```
DATABASE_URL=postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres
UPSTASH_REDIS_REST_URL=https://xxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=AYxxxxxxxxxxxx
JWT_SECRET=your-super-secret-key-change-this-in-production
ANTHROPIC_API_KEY=sk-ant-xxxxx (optional, for LLM features)
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

### 3.3 Redeploy
```bash
vercel --prod
```

Your API is now live! Note the URL (e.g., `https://web-intelligence-backend.vercel.app`)

### 3.4 Update Frontend API URL
1. Go to Frontend project in Vercel
2. Settings → Environment Variables
3. Edit `VITE_API_URL` → `https://your-backend.vercel.app/api`
4. Save and redeploy frontend

---

## Step 4: Setup GitHub Actions Workers (10 minutes)

### 4.1 Add Repository Secrets
Go to GitHub → Your Repo → Settings → Secrets and variables → Actions

Click "New repository secret" and add:

```
DATABASE_URL
Value: postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres

UPSTASH_REDIS_URL  
Value: https://xxxxx.upstash.io

UPSTASH_REDIS_REST_TOKEN
Value: AYxxxxxxxxxxxx

ANTHROPIC_API_KEY (optional)
Value: sk-ant-xxxxx
```

### 4.2 Enable GitHub Actions
1. Go to your repo → Actions tab
2. Click "I understand my workflows, go ahead and enable them"
3. You should see "Fingerprint Worker" workflow

### 4.3 Test Worker Manually
1. Go to Actions tab
2. Click "Fingerprint Worker"
3. Click "Run workflow" → "Run workflow"
4. Wait 1-2 minutes
5. Check logs - should say "Found X queued fingerprint jobs"

### 4.4 Workers Now Run Automatically
- **Fingerprint Worker:** Every 15 minutes
- **Discovery Worker:** Every 30 minutes (if you create that workflow)
- **Selector Generator:** On demand

---

## Step 5: Verify Everything Works (5 minutes)

### 5.1 Test Frontend
1. Open your frontend URL
2. Should see dashboard loading
3. Try logging in (username: admin, password: admin)

### 5.2 Test API
```bash
# Replace with your actual backend URL
API_URL="https://your-backend.vercel.app"

# Health check
curl $API_URL/api/health

# Should return:
# {"status":"healthy","version":"1.0.0","service":"web-intelligence-platform"}
```

### 5.3 Test Full Flow
```bash
# 1. Login
TOKEN=$(curl -s -X POST $API_URL/api/auth/login \
  -d "username=admin&password=admin" | jq -r '.access_token')

# 2. Create a site (this will queue a fingerprint job)
curl -X POST $API_URL/api/sites \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "business_value_score": 0.9}'

# 3. Check jobs (should see queued job)
curl -H "Authorization: Bearer $TOKEN" $API_URL/api/jobs

# 4. Wait 15 minutes for GitHub Action to run
# 5. Check jobs again - should be "running" or "success"
```

---

## ✅ DEPLOYMENT COMPLETE!

### Your Live URLs:
- **Frontend:** https://your-frontend.vercel.app
- **Backend API:** https://your-backend.vercel.app/api
- **API Docs:** https://your-backend.vercel.app/docs

### What's Running:
✅ Frontend on Vercel (instant, auto-scaling)  
✅ Backend API on Vercel Functions (on-demand)  
✅ Workers on GitHub Actions (scheduled every 15-30 min)  
✅ Database on Supabase (always on)  
✅ Redis on Upstash (managed)  

### Total Cost: **$0/month** 🎉

---

## 📊 Monitoring Your Usage

### Vercel
- Dashboard → Your Project → Analytics
- Shows requests, bandwidth, errors
- Free tier: 100GB-hrs/month

### GitHub Actions
- Repo → Actions → See all workflow runs
- Settings → Billing → View usage
- Free tier: 2,000 minutes/month

### Upstash
- Dashboard → Your Database → Metrics
- Shows commands, memory usage
- Free tier: 10,000 commands/day

### Supabase
- Dashboard → Your Project → Database
- Shows storage, queries
- Free tier: 500MB storage

---

## 🎯 Next Steps

### 1. Custom Domain (Optional)
1. Buy domain or use existing
2. Vercel → Project → Settings → Domains
3. Add custom domain
4. Update DNS records

### 2. Add LLM API Key
1. Get Anthropic API key from https://console.anthropic.com
2. Vercel → Backend Project → Settings → Environment Variables
3. Add `ANTHROPIC_API_KEY`
4. Redeploy

### 3. Monitor & Optimize
- Check GitHub Actions logs daily
- Monitor Vercel function times
- Optimize slow endpoints
- Cache frequent queries in Upstash

---

## 🔧 Troubleshooting

### Frontend not loading?
- Check environment variables in Vercel
- Ensure VITE_API_URL is correct
- Check browser console for errors

### API returning 500 errors?
- Check Vercel function logs
- Verify DATABASE_URL is correct
- Test Supabase connection

### Workers not running?
- Check GitHub Actions tab
- Verify repository secrets are set
- Look at workflow logs for errors

### Rate limiting issues?
- Increase Upstash commands (upgrade if needed)
- Optimize caching strategy
- Reduce API call frequency

---

## 💡 Free Tier Optimization Tips

### 1. Cache Aggressively
```python
# Cache GET endpoints for 5 minutes
@app.get("/sites")
async def list_sites():
    cache_key = "sites:list"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Expensive query...
    await redis.setex(cache_key, 300, json.dumps(result))
    return result
```

### 2. Batch Workers
- Process 5-10 jobs per GitHub Action run
- Reduces total minutes used
- Stay under 2,000 min/month limit

### 3. Lazy Load Frontend
- Use code splitting
- Load heavy components only when needed
- Reduces Vercel bandwidth

### 4. Optimize Database
- Add indexes to frequent queries
- Use Supabase's built-in caching
- Paginate large result sets

---

## 🎉 You're Live!

Your Web Intelligence Platform is now:
- ✅ Deployed to production
- ✅ Completely free ($0/month)
- ✅ Auto-scaling
- ✅ Globally distributed (Vercel CDN)
- ✅ Continuously deploying (on git push)
- ✅ Processing jobs automatically

**Estimated capacity on free tier:**
- **300-1000 users per day**
- **15-30 sites analyzed per day**
- **1M+ API requests per month**
- **5,000-10,000 sites stored**

Perfect for MVP, testing, and initial users! 🚀

---

## 📞 Support

- **Vercel:** https://vercel.com/docs
- **Upstash:** https://docs.upstash.com
- **GitHub Actions:** https://docs.github.com/actions
- **Supabase:** https://supabase.com/docs

---

**Need help?** Check logs:
- Vercel: Dashboard → Functions tab
- GitHub: Actions tab → Latest workflow
- Upstash: Dashboard → Logs
- Supabase: Dashboard → Logs

**Happy deploying! 🎊**

