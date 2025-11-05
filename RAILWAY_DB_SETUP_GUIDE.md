# 🚀 Railway PostgreSQL Setup Guide

## ✅ Step 1: Update DATABASE_URL in Railway

Your Railway PostgreSQL URL needs to be converted to asyncpg format:

**Original URL:**
```
postgresql://postgres:igXxDjLmfzMAchOxbjCVerkRvCnOuIFv@trolley.proxy.rlwy.net:41967/railway
```

**Update to (add `+asyncpg`):**
```
DATABASE_URL=postgresql+asyncpg://postgres:igXxDjLmfzMAchOxbjCVerkRvCnOuIFv@trolley.proxy.rlwy.net:41967/railway
```

### How to Update:
1. Go to Railway dashboard
2. Select your **backend service**
3. Go to **Variables** tab
4. Find `DATABASE_URL`
5. Change `postgresql://` to `postgresql+asyncpg://`
6. Save (Railway will auto-redeploy)

---

## ✅ Step 2: Initialize Database Schema

You need to run the SQL schema in your Railway PostgreSQL database.

### Option A: Using Railway CLI (Recommended)

```bash
# Install Railway CLI (if not already)
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Connect to PostgreSQL
railway connect postgres

# Once connected, paste the contents of railway_db_setup.sql
# Or run:
railway run psql $DATABASE_URL < railway_db_setup.sql
```

### Option B: Using psql (if you have PostgreSQL client)

```bash
psql postgresql://postgres:igXxDjLmfzMAchOxbjCVerkRvCnOuIFv@trolley.proxy.rlwy.net:41967/railway < railway_db_setup.sql
```

### Option C: Using Railway Web Interface

1. Go to Railway dashboard
2. Click on your PostgreSQL service
3. Click "Data" tab
4. Click "Query" button
5. Copy entire contents of `railway_db_setup.sql`
6. Paste and run

---

## ✅ Step 3: Verify Setup

After Railway redeploys (wait ~2 minutes), test:

```bash
# Test database connection
curl https://web-intelligence-platform-production.up.railway.app/debug/db

# Should return: {"status":"success", "message":"Database connection working"}

# Test list sites
curl https://web-intelligence-platform-production.up.railway.app/api/v1/sites

# Should return: {"total":0,"limit":50,"offset":0,"sites":[]}
```

---

## 📋 Quick Checklist:

- [ ] Update `DATABASE_URL` to use `postgresql+asyncpg://`
- [ ] Wait for Railway backend to redeploy (~2 mins)
- [ ] Run `railway_db_setup.sql` in PostgreSQL
- [ ] Test `/debug/db` endpoint
- [ ] Test `/api/v1/sites` endpoint
- [ ] 🎉 Platform 100% working!

---

## 🔐 Admin Credentials

After setup, you can login with:
- **Email:** admin@example.com
- **Password:** SecurePassword123

---

## 🎯 What This Gives You:

✅ **Same Railway network** = fast & reliable  
✅ **No Supabase routing issues**  
✅ **Automatic backups by Railway**  
✅ **Better performance**  
✅ **All included in Railway pricing**

---

## 💡 Need Help?

If you get stuck on any step, let me know and I'll help you through it!

**Let me know once you've:**
1. Updated the DATABASE_URL
2. Run the schema SQL

Then I'll test everything! 🚀

