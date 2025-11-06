# 🔐 GitHub Secrets Quick Reference

## Where to Add Secrets

1. Go to: **https://github.com/FraudShield1/web-intelligence-platform**
2. Click: **Settings** (top menu)
3. Left sidebar: **Secrets and variables** → **Actions**
4. Click: **"New repository secret"**

---

## Required Secrets

### ✅ Secret #1: DATABASE_URL (REQUIRED)

**Name:** `DATABASE_URL`

**Value:** Get from Railway PostgreSQL service

**How to get it:**
1. Go to: https://railway.app/
2. Click your **PostgreSQL** service (NOT backend)
3. Click "Variables" tab
4. Find `DATABASE_URL` or `DATABASE_PRIVATE_URL`
5. Copy the value
6. **⚠️ IMPORTANT:** Change `postgresql://` to `postgresql+asyncpg://`

**Example:**
```
BEFORE: postgresql://postgres:mypass123@monorail.proxy.rlwy.net:12345/railway
AFTER:  postgresql+asyncpg://postgres:mypass123@monorail.proxy.rlwy.net:12345/railway
```

**Full format:**
```
postgresql+asyncpg://[username]:[password]@[host]:[port]/[database]
```

---

### ⚙️ Secret #2: UPSTASH_REDIS_URL (Optional)

**Name:** `UPSTASH_REDIS_URL`

**Value:**
```
https://pure-halibut-27195.upstash.io
```

*(This is your Upstash Redis REST endpoint)*

---

## 🎯 Quick Setup Steps

1. **Get DATABASE_URL from Railway:**
   - Railway → PostgreSQL service → Variables tab
   - Copy `DATABASE_URL`
   - Change `postgresql://` to `postgresql+asyncpg://`

2. **Add to GitHub:**
   - GitHub repo → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `DATABASE_URL`
   - Value: (paste modified URL)
   - Click "Add secret"

3. **Enable GitHub Actions:**
   - GitHub repo → Actions tab
   - Enable workflows if needed
   - Test: Click "Fingerprint Worker" → "Run workflow"

---

## ✅ Verification

After adding secrets, test:

```bash
# In GitHub Actions tab
1. Click "Fingerprint Worker"
2. Click "Run workflow" (right side)
3. Click "Run workflow" button
4. Wait 1-2 minutes
5. Click the running workflow
6. Check logs for: "✅ Job completed successfully"
```

If you see errors about DATABASE_URL:
- Check you added `+asyncpg` to the URL
- Verify no extra spaces in the secret value
- Ensure password is correct

---

## 📊 What These Secrets Do

**DATABASE_URL:**
- Connects GitHub Actions to your Railway database
- Allows workers to fetch queued jobs
- Updates job status after processing

**UPSTASH_REDIS_URL (optional):**
- Used for caching (if needed)
- Not critical for basic functionality

---

## 🔒 Security Notes

- ✅ Secrets are encrypted by GitHub
- ✅ Not visible in logs
- ✅ Only accessible during workflow runs
- ✅ Can be updated anytime

---

**That's it! Just these 2 secrets (really just 1 required) and your workers will run!** 🚀

