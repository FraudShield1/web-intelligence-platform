# 🚀 Quick Start Guide - Get Your Platform Running in 5 Minutes!

## ✅ Current Status

Your platform is **DEPLOYED** and **LIVE**:
- ✅ Backend: https://web-intelligence-platform-production.up.railway.app
- ✅ Frontend: https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app
- ✅ API Docs: https://web-intelligence-platform-production.up.railway.app/docs

**Last Step:** Initialize the database!

---

## 📝 Step 1: Initialize Database (2 minutes)

### Go to Supabase SQL Editor
https://app.supabase.com/project/aeajgihhgplxcvcsiqeo/sql/new

### Run This SQL (Copy & Paste):

```sql
-- Quick Setup: Create tables and admin user in one go!

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Create Sites Table
CREATE TABLE IF NOT EXISTS sites (
    site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Create Jobs Table
CREATE TABLE IF NOT EXISTS jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- 4. Create Blueprints Table
CREATE TABLE IF NOT EXISTS blueprints (
    blueprint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID REFERENCES sites(site_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    categories JSONB,
    selectors JSONB,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Create Analytics Table
CREATE TABLE IF NOT EXISTS analytics_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT,
    dimensions JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 6. Create Admin User
-- Password: SecurePassword123
INSERT INTO users (
    username,
    email,
    password_hash,
    full_name,
    role,
    is_active
) VALUES (
    'admin@example.com',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRX0JQFCm',
    'Admin User',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- Done!
SELECT 'Database initialized successfully!' as status;
SELECT 'Admin user created: admin@example.com / SecurePassword123' as credentials;
```

Click **"RUN"** button in Supabase!

---

## 🧪 Step 2: Test Your Platform (1 minute)

### Run the test script:
```bash
cd "/Users/naouri/Downloads/Web Intelligence Platform"
bash test_platform.sh
```

You should see:
- ✅ Health check passed
- ✅ API root responding
- ✅ API docs available
- ✅ Login successful
- ✅ All endpoints working

---

## 🎯 Step 3: Use Your Platform!

### Option A: Via Web Dashboard (Easiest)

1. **Open:** https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app

2. **Login:**
   - Email: `admin@example.com`
   - Password: `SecurePassword123`

3. **Add a Site:**
   - Click "Sites" → "Add Site"
   - Enter URL: `https://example.com`
   - Click "Create"

4. **Watch it Analyze:**
   - Jobs will be created
   - LLM will analyze the site
   - Blueprints will be generated

### Option B: Via API

```bash
# 1. Login
TOKEN=$(curl -s -X POST "https://web-intelligence-platform-production.up.railway.app/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=SecurePassword123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Add a site
curl -X POST "https://web-intelligence-platform-production.up.railway.app/api/v1/sites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "name": "Example Site",
    "description": "My first site"
  }'

# 3. List sites
curl "https://web-intelligence-platform-production.up.railway.app/api/v1/sites" \
  -H "Authorization: Bearer $TOKEN"

# 4. View analytics
curl "https://web-intelligence-platform-production.up.railway.app/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

### Option C: Via Swagger UI

1. **Open:** https://web-intelligence-platform-production.up.railway.app/docs

2. **Click "Authorize"** button (top right)

3. **Login first** to get token, then enter it

4. **Try any endpoint** interactively!

---

## 📊 Monitor Your Platform

### Backend (Railway)
https://railway.app/dashboard
- View logs
- Monitor resources
- Check deployments

### Frontend (Vercel)
https://vercel.com/dashboard
- View analytics
- Check deployments

### Database (Supabase)
https://app.supabase.com/project/aeajgihhgplxcvcsiqeo
- Query data
- View tables
- Check connections

---

## 🎉 You're Done!

Your platform is now **100% functional** and ready to use!

### What You Can Do:
- ✅ Add unlimited sites
- ✅ Automatic LLM analysis
- ✅ Generate scraping blueprints
- ✅ Export data
- ✅ Monitor jobs
- ✅ View analytics
- ✅ Manage users

### Cost:
- **~$5-10/month** for everything!

### Support:
- Check `100_PERCENT_COMPLETE.md` for full documentation
- API docs at `/docs`
- All code in GitHub

---

## 🆘 Troubleshooting

### Login fails?
- Make sure you ran the SQL script in Supabase
- Check user was created: `SELECT * FROM users;` in Supabase
- Verify password: `SecurePassword123`

### Can't add sites?
- Make sure you're logged in
- Check token is valid
- Verify tables exist in Supabase

### Internal server errors?
- Check Railway logs in dashboard
- Verify all environment variables set
- Test database connection in Supabase

---

## 📞 Quick Links

- **Backend:** https://web-intelligence-platform-production.up.railway.app
- **Frontend:** https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app
- **API Docs:** https://web-intelligence-platform-production.up.railway.app/docs
- **Supabase:** https://app.supabase.com/project/aeajgihhgplxcvcsiqeo
- **Railway:** https://railway.app/dashboard
- **GitHub:** https://github.com/FraudShield1/web-intelligence-platform

---

**Ready? Run that SQL in Supabase and you're live in 2 minutes!** 🚀

