# 🚂 Deploy to Railway - Business-Grade Setup

## 🎯 What You'll Get

A **fully functional, production-ready** platform with:
- ✅ Complete FastAPI backend with all features
- ✅ Real database operations (Supabase)
- ✅ Celery workers for async processing
- ✅ LLM integration for site analysis
- ✅ Real-time analytics
- ✅ Authentication & authorization
- ✅ Monitoring & logging
- ✅ **Everything working end-to-end**

**Cost:** $5-10/month (or free tier initially)

---

## 🚀 Quick Deploy (5 minutes)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign in with GitHub

### Step 2: Deploy from GitHub

#### Option A: Via Railway Dashboard (Easiest)
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose: `FraudShield1/web-intelligence-platform`
4. Railway will detect the configuration automatically

#### Option B: Via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
cd "/Users/naouri/Downloads/Web Intelligence Platform"
railway init

# Deploy
railway up
```

### Step 3: Configure Environment Variables

In Railway Dashboard → Variables, add:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres

# Redis
REDIS_URL=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379

# Or use Upstash REST API
UPSTASH_REDIS_REST_URL=https://pure-halibut-27195.upstash.io
UPSTASH_REDIS_REST_TOKEN=AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU

# LLM
OPENROUTER_API_KEY=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

# Security
JWT_SECRET=ohoWjQJpwnREMQgZDBVWnDSsTq++sezllwaH5j07gcw=
SECRET_KEY=your-secret-key-change-in-production

# API Settings
API_HOST=0.0.0.0
API_PORT=$PORT
CORS_ORIGINS=["https://web-intelligence-frontend-9ge6nnqwu-dedes-projects-ee4b20e7.vercel.app","http://localhost:3000"]

# Features
DEBUG=False
ENABLE_DOCS=True
PROMETHEUS_ENABLED=True
LOG_LEVEL=INFO

# Celery
CELERY_BROKER_URL=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379
CELERY_RESULT_BACKEND=redis://default:AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU@pure-halibut-27195.upstash.io:6379

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourplatform.com
```

### Step 4: Deploy Workers (Optional but Recommended)

Create a second service for workers:
1. In Railway Dashboard, click "New Service"
2. Select same GitHub repo
3. Set start command: `cd backend && celery -A app.celery_app worker --loglevel=info`
4. Add same environment variables

### Step 5: Update Frontend

Get your Railway URL (e.g., `https://your-app.railway.app`)

```bash
cd frontend
vercel env rm VITE_API_URL production -y
echo "https://your-app.railway.app" | vercel env add VITE_API_URL production
vercel --prod
```

---

## 🧪 Test Your Deployment

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

### 2. API Documentation
Open: `https://your-app.railway.app/docs`

### 3. Create Admin User
```bash
curl -X POST https://your-app.railway.app/api/v1/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePassword123","full_name":"Admin User"}'
```

### 4. Login
```bash
curl -X POST https://your-app.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"SecurePassword123"}'
```

### 5. Add a Site
```bash
TOKEN="your_token_from_login"

curl -X POST https://your-app.railway.app/api/v1/sites \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","name":"Example Site","description":"Test site"}'
```

### 6. Check Dashboard Metrics
```bash
curl https://your-app.railway.app/api/v1/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Post-Deployment Checklist

### Immediate
- [ ] Health endpoint returns 200
- [ ] Swagger docs accessible
- [ ] Can create admin user
- [ ] Can login and get token
- [ ] Can add a site
- [ ] Dashboard shows real data

### Within 24 Hours
- [ ] Set up custom domain
- [ ] Configure email notifications
- [ ] Enable error tracking (Sentry)
- [ ] Set up monitoring alerts
- [ ] Review logs
- [ ] Test all workflows

### Within 1 Week
- [ ] Load testing
- [ ] Security audit
- [ ] Backup strategy
- [ ] Disaster recovery plan
- [ ] User documentation
- [ ] Team training

---

## 💡 Railway Tips

### Monitoring
- Railway Dashboard shows CPU, Memory, Network usage
- View logs in real-time
- Set up usage alerts

### Scaling
```bash
# Scale up (via dashboard)
Settings → Resources → Increase CPU/Memory

# Or add replicas
Settings → Deployments → Replicas
```

### Custom Domain
```bash
# In Railway Dashboard
Settings → Networking → Custom Domain → Add your domain
```

### Database Backups
```bash
# Add to cron job
0 2 * * * pg_dump $DATABASE_URL > backup.sql
```

---

## 🔄 Continuous Deployment

Railway auto-deploys on every push to `main`:

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main

# Railway automatically deploys!
```

---

## 📊 Cost Management

### Free Tier
- $5 credit/month
- Good for testing
- Limited resources

### Starter Plan ($5/month)
- Better for development
- More resources
- Suitable for low traffic

### Pro Plan ($20/month)
- Production ready
- High availability
- Better performance

### Monitor Usage
- Railway Dashboard → Usage
- Set billing alerts
- Track spend daily

---

## 🆘 Troubleshooting

### Build Fails
**Check:** `requirements-full.txt` exists
**Fix:** Ensure all dependencies are listed

### App Crashes
**Check:** Railway logs
**Fix:** Look for import errors, missing env vars

### Database Connection Failed
**Check:** DATABASE_URL format
**Fix:** Ensure it starts with `postgresql+asyncpg://`

### Workers Not Running
**Check:** Celery broker URL
**Fix:** Verify Redis connection

### High Memory Usage
**Check:** Railway metrics
**Fix:** Reduce worker concurrency or upgrade plan

---

## 🎉 Success!

Once deployed, you have:
- ✅ Full backend at `https://your-app.railway.app`
- ✅ Interactive docs at `/docs`
- ✅ All API endpoints functional
- ✅ Workers processing jobs
- ✅ Real-time analytics
- ✅ Production-ready platform

**Next:** Update frontend, test end-to-end, invite users!

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Celery Docs:** https://docs.celeryq.dev
- **Our Docs:** See `ARCHITECTURE.md`, `API_SPEC.md`

---

## 🚀 Ready to Deploy?

Follow the steps above and your business-grade platform will be live in minutes!

**Need help?** Check the logs, review environment variables, or see troubleshooting section above.

