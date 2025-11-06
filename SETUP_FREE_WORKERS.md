# 🚀 Setup Free Workers with GitHub Actions

## ✅ What This Does

- **FREE** background job processing
- Runs every 15 minutes automatically
- Processes up to 5 jobs per run
- Uses GitHub Actions (2,000 free minutes/month)
- No additional services needed

## 📋 Required Secrets

You need to add these secrets to your GitHub repository:

### 1. DATABASE_URL
**Value:** Your Railway PostgreSQL connection string

**Format:**
```
postgresql+asyncpg://username:password@host:port/database
```

**Where to get it:**
1. Go to: https://railway.app/
2. Click your PostgreSQL service (not backend)
3. Go to "Variables" tab
4. Copy the value of `DATABASE_URL` or `DATABASE_PRIVATE_URL`
5. **IMPORTANT:** Replace `postgresql://` with `postgresql+asyncpg://`

**Example:**
```
postgresql+asyncpg://postgres:password@monorail.proxy.rlwy.net:12345/railway
```

### 2. UPSTASH_REDIS_URL (Optional)
**Value:** Your Upstash Redis connection string

**Where to get it:**
```
https://pure-halibut-27195.upstash.io
```

This is already in your Railway environment variables.

---

## 🔧 Setup Steps

### Step 1: Get DATABASE_URL from Railway

1. Open: https://railway.app/
2. Find your **PostgreSQL database service**
3. Click "Variables" tab
4. Look for `DATABASE_URL` or `DATABASE_PRIVATE_URL`
5. Copy the entire value
6. **Modify it:** Change `postgresql://` to `postgresql+asyncpg://`

**Example transformation:**
```
FROM: postgresql://postgres:pass@host:5432/db
TO:   postgresql+asyncpg://postgres:pass@host:5432/db
```

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository:
   ```
   https://github.com/FraudShield1/web-intelligence-platform
   ```

2. Click **"Settings"** (top menu)

3. In left sidebar, click **"Secrets and variables"** → **"Actions"**

4. Click **"New repository secret"**

5. Add first secret:
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql+asyncpg://...` (your modified Railway URL)
   - Click **"Add secret"**

6. Add second secret (optional):
   - **Name:** `UPSTASH_REDIS_URL`
   - **Value:** `https://pure-halibut-27195.upstash.io`
   - Click **"Add secret"**

### Step 3: Enable GitHub Actions

1. In your GitHub repo, click **"Actions"** tab (top menu)

2. You should see:
   - "Fingerprint Worker" workflow
   
3. If workflows are disabled:
   - Click **"I understand my workflows, go ahead and enable them"**

4. You should see the workflow is now active

### Step 4: Test Manual Run

1. In **Actions** tab, click **"Fingerprint Worker"**

2. Click **"Run workflow"** dropdown (right side)

3. Select branch: **main**

4. Click **"Run workflow"** button

5. Wait ~1-2 minutes

6. Click on the running workflow to see logs

7. Check for:
   ```
   ✅ Found X queued fingerprint jobs
   ✅ Processing job ...
   ✅ Job completed successfully
   ```

### Step 5: Verify It's Working

1. Go to your platform: https://web-intelligence-platform.vercel.app

2. Add a new site (any domain)

3. Go to Jobs page - you should see status: "queued"

4. Wait 15 minutes (or trigger workflow manually)

5. Refresh Jobs page - status should change to "running" then "success"

---

## 📊 GitHub Actions Workflow Details

### Current Setup:

**File:** `.github/workflows/worker_fingerprint.yml`

**Schedule:** Every 15 minutes
```yaml
schedule:
  - cron: '*/15 * * * *'  # Runs at :00, :15, :30, :45 of every hour
```

**What it does:**
1. Spins up Ubuntu VM (free tier)
2. Installs Python 3.11
3. Installs backend dependencies
4. Runs: `python -m app.workers.github_runner fingerprint --max-jobs=5`
5. Processes up to 5 queued jobs
6. Updates job status in database
7. Shuts down VM

**Timeout:** 5 minutes per run
**Cost:** FREE (within GitHub's 2,000 free minutes/month)

### Expected Usage:
- **Per run:** ~2 minutes
- **Runs per day:** 96 (every 15 min)
- **Total monthly:** ~192 minutes
- **Well within free tier!** ✅

---

## 🧪 Testing the Worker

### Test 1: Manual Trigger
```bash
# From Actions tab in GitHub
1. Click "Fingerprint Worker"
2. Click "Run workflow"
3. Check logs for output
```

### Test 2: Add Site and Wait
```bash
1. Add site in your platform
2. Check Jobs page (should be "queued")
3. Wait 15 minutes
4. Refresh Jobs page (should be "success" or "running")
```

### Test 3: Check Workflow Logs
```bash
1. Go to Actions tab
2. Click latest workflow run
3. Click "Process queued fingerprint jobs"
4. See:
   🚀 Starting GitHub Actions worker for: fingerprint
   Found 1 queued fingerprint jobs
   Processing job abc-123...
   ✅ Job abc-123 completed successfully
```

---

## 🔍 Troubleshooting

### Issue: Workflow doesn't run
**Fix:**
1. Check if Actions are enabled (Settings → Actions)
2. Verify workflow file exists in `.github/workflows/`
3. Check branch is `main` (not `master`)

### Issue: DATABASE_URL error
**Fix:**
1. Verify secret is named exactly `DATABASE_URL`
2. Ensure you added `+asyncpg` to the URL
3. Format: `postgresql+asyncpg://user:pass@host:port/db`

### Issue: Jobs stay "queued"
**Fix:**
1. Check if workflow is running (Actions tab)
2. View latest workflow run logs
3. Look for Python errors in logs
4. Verify DATABASE_URL has correct password

### Issue: "No module named 'app'"
**Fix:**
1. Workflow might need updated requirements.txt
2. Check if all dependencies are listed
3. View workflow logs for specific missing module

---

## 📝 What Gets Processed

Currently configured job types:
- ✅ **fingerprint** - Site fingerprinting (every 15 min)

Future job types (can add more workflows):
- **discovery** - Site discovery
- **selector_generation** - CSS selector generation

---

## 🎯 After Setup - What to Expect

### Immediate:
- ✅ Workflow appears in Actions tab
- ✅ Can manually trigger anytime
- ✅ Runs automatically every 15 minutes

### When you add a site:
1. Site created (status: "pending")
2. Job created (status: "queued")
3. Within 15 minutes: Workflow runs
4. Job status → "running" → "success"
5. Site status → "ready"
6. Blueprint generated

### Long-term:
- Fully automated job processing
- No manual intervention needed
- Free forever (within GitHub limits)
- Reliable 15-minute processing cycle

---

## 💰 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| GitHub Actions | ~192 min/month | **FREE** (2,000 min free) |
| Railway Backend | Always-on | **FREE** (free tier) |
| Railway PostgreSQL | Storage | **FREE** (free tier) |
| Vercel Frontend | Bandwidth | **FREE** (hobby tier) |
| **TOTAL** | | **$0/month** 🎉 |

---

## ✅ Quick Start Checklist

- [ ] Get DATABASE_URL from Railway PostgreSQL service
- [ ] Change `postgresql://` to `postgresql+asyncpg://`
- [ ] Go to GitHub repo → Settings → Secrets → Actions
- [ ] Add secret: `DATABASE_URL` with modified URL
- [ ] (Optional) Add secret: `UPSTASH_REDIS_URL`
- [ ] Go to Actions tab
- [ ] Enable workflows if disabled
- [ ] Click "Fingerprint Worker" → "Run workflow"
- [ ] Wait 1-2 minutes and check logs
- [ ] See "✅ Job completed successfully"
- [ ] Add a site in your platform
- [ ] Wait 15 minutes
- [ ] Check if job processed!

---

## 🚀 You're Done!

After this setup:
- ✅ Workers run automatically every 15 minutes
- ✅ Jobs get processed in background
- ✅ Sites get analyzed
- ✅ Completely FREE
- ✅ **Platform is 100% functional!**

---

**Next:** Add a site and watch it get processed automatically! 🎉

