# 🚀 Free Tier Deployment Checklist

Follow these steps in order to deploy your Web Intelligence Platform on completely free infrastructure.

---

## ✅ Prerequisites Done

- [x] Supabase account + database created
- [x] Upstash Redis account + database created  
- [x] OpenRouter API key obtained
- [x] GitHub repository initialized

---

## 📋 Step-by-Step Deployment

### 1️⃣ Push to GitHub ✅ (Next)
```bash
cd /Users/naouri/Downloads/Web\ Intelligence\ Platform
git add .
git commit -m "feat: complete free tier deployment setup with all configs"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/web-intelligence-platform.git
git push -u origin main
```

### 2️⃣ Deploy Frontend to Vercel

#### Install Vercel CLI
```bash
npm install -g vercel
```

#### Deploy Frontend
```bash
cd frontend
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name: web-intelligence-frontend
# - Directory: ./ 
# - Build command: npm run build
# - Output directory: dist
```

#### Add Environment Variables
```bash
vercel env add VITE_API_URL production
# Enter: https://YOUR_BACKEND_URL.vercel.app/api

vercel env add VITE_SUPABASE_URL production
# Enter: https://aeajgihhgplxcvcsiqeo.supabase.co

vercel env add VITE_SUPABASE_ANON_KEY production
# Paste: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlYWpnaWloZ3BseGN2Y3NpcWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzMjY1MzMsImV4cCI6MjA3NzkwMjUzM30.KgZrArrNkk_8ujSMhu-QL5TCG9Elv9YHdTp4oxScbKM

# Redeploy to pick up env vars
vercel --prod
```

### 3️⃣ Deploy Backend to Vercel

#### Deploy Backend
```bash
cd ../backend
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name: web-intelligence-backend
# - Directory: ./
```

#### Add Environment Variables
```bash
# Database
vercel env add DATABASE_URL production
# Enter: postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres

# Redis
vercel env add UPSTASH_REDIS_REST_URL production
# Enter: https://pure-halibut-27195.upstash.io

vercel env add UPSTASH_REDIS_REST_TOKEN production
# Enter: AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU

# LLM
vercel env add OPENROUTER_API_KEY production
# Enter: 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

# Security (generate new!)
vercel env add JWT_SECRET production
# Generate: openssl rand -base64 32
# Paste the output

# CORS (use your frontend URL)
vercel env add CORS_ORIGINS production
# Enter: ["https://YOUR_FRONTEND_URL.vercel.app"]

# Redeploy to pick up env vars
vercel --prod
```

### 4️⃣ Configure GitHub Actions

Go to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets (copy from `ENVIRONMENT_VARS.md`):
- `DATABASE_URL`
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `OPENROUTER_API_KEY`
- `JWT_SECRET` (generate with: `openssl rand -base64 32`)

### 5️⃣ Update Frontend API URL

After backend is deployed, update frontend:
```bash
# Note your backend URL from Vercel
# Then update frontend env var:
vercel env add VITE_API_URL production
# Enter: https://YOUR_BACKEND_URL.vercel.app/api

vercel --prod
```

---

## 🧪 Testing

### Test Backend
```bash
curl https://YOUR_BACKEND_URL.vercel.app/api/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### Test Frontend
Open: `https://YOUR_FRONTEND_URL.vercel.app`
- Should load dashboard
- Check browser console for errors
- Try logging in (use bootstrap endpoint first)

### Test Workers
1. Go to GitHub → Actions
2. Click "Fingerprint Worker"
3. Click "Run workflow"
4. Select branch: main
5. Click "Run workflow"
6. Wait for completion (should be green ✓)

---

## 🎯 Post-Deployment

### Create Admin User
```bash
curl -X POST https://YOUR_BACKEND_URL.vercel.app/api/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"SecurePassword123"}'
```

### Test Login
```bash
curl -X POST https://YOUR_BACKEND_URL.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"SecurePassword123"}'
```

### Add Your First Site
Via the UI or API:
```bash
curl -X POST https://YOUR_BACKEND_URL.vercel.app/api/sites \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","name":"Example Site"}'
```

---

## 📊 Monitoring

### Vercel Dashboards
- Frontend: https://vercel.com/YOUR_USERNAME/web-intelligence-frontend
- Backend: https://vercel.com/YOUR_USERNAME/web-intelligence-backend

### GitHub Actions
- Workflows: https://github.com/YOUR_USERNAME/web-intelligence-platform/actions

### Supabase
- Database: https://app.supabase.com/project/aeajgihhgplxcvcsiqeo

### Upstash
- Redis: https://console.upstash.com/

---

## 🆘 Troubleshooting

### Backend 500 errors
Check Vercel logs: Dashboard → Runtime Logs

Common issues:
- Missing environment variables
- Database connection (check Supabase is awake)
- CORS (verify CORS_ORIGINS matches frontend URL)

### Frontend blank page
Check browser console (F12)

Common issues:
- `VITE_API_URL` not set
- Backend not responding
- CORS errors (check backend CORS_ORIGINS)

### Workers not running
Check GitHub Actions logs

Common issues:
- Missing secrets in GitHub
- Database connection timeout
- OpenRouter API quota

---

## 💰 Free Tier Limits

Monitor your usage:

| Service | Free Limit | Reset |
|---------|-----------|-------|
| Vercel | 100GB bandwidth/month | Monthly |
| GitHub Actions | 2,000 minutes/month | Monthly |
| Supabase | 500MB database | - |
| Upstash | 10k requests/day | Daily |
| OpenRouter | Varies by model | - |

**Tip:** Set up alerts in each dashboard!

---

## ✅ Success Criteria

Your deployment is successful when:
- [ ] Backend `/health` returns 200 OK
- [ ] Frontend loads without console errors
- [ ] Can log in with admin account
- [ ] Can create a site via UI
- [ ] GitHub Actions worker completes successfully
- [ ] Site fingerprinting job creates blueprint

---

## 🎉 You're Live!

Congratulations! Your Web Intelligence Platform is now running on 100% free infrastructure.

**Next steps:**
- Invite team members
- Start analyzing sites
- Monitor usage dashboards
- Scale up when ready to pay

**Questions?** Check `DEPLOY_FREE.md` for detailed explanations.

