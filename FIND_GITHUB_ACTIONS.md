# 🔍 How to Find GitHub Actions

## Problem: Can't See "Fingerprint Worker"

This usually means GitHub Actions is disabled or workflows aren't showing. Here's how to fix it:

---

## Step-by-Step: Enable and Find Actions

### Step 1: Go to Your GitHub Repository

Open: **https://github.com/FraudShield1/web-intelligence-platform**

### Step 2: Look for Actions Tab

At the top of the page, you should see tabs:
```
Code   Issues   Pull requests   Actions   Projects   Wiki   Settings
```

**Click "Actions"** (4th tab)

---

## What You Might See:

### Scenario A: Actions Disabled

If you see:
```
┌─────────────────────────────────────────┐
│ Workflows aren't being run on this     │
│ repository                              │
│                                         │
│ [Enable GitHub Actions]                 │
└─────────────────────────────────────────┘
```

**Solution:**
1. Click **"Enable GitHub Actions"** button
2. OR click **"I understand my workflows, go ahead and enable them"**

### Scenario B: No Workflows Showing

If Actions is enabled but you see:
```
Get started with GitHub Actions

No workflows found
```

**This means the workflow file isn't in the repo yet.**

**Solution:** Let me push it for you (see below)

### Scenario C: Workflows Showing! ✅

If you see:
```
All workflows
├─ Fingerprint Worker
├─ CI
└─ Deploy
```

**Perfect!** Click "Fingerprint Worker" to use it.

---

## Fix: Push Workflow to GitHub

The workflow file exists locally but might not be on GitHub. Let's push it:

### Option 1: I'll Push It For You

Run these commands:

```bash
cd "/Users/naouri/Downloads/Web Intelligence Platform"

# Check current status
git status

# Add workflows if not tracked
git add .github/workflows/

# Commit if needed
git commit -m "Add GitHub Actions worker workflows"

# Push to GitHub
git push origin main
```

### Option 2: Manual Check

1. Go to: https://github.com/FraudShield1/web-intelligence-platform/tree/main/.github/workflows

2. Look for: `worker_fingerprint.yml`

3. If it's there → Actions should be enabled (go back to Step 2)

4. If it's not there → Run the commands above to push it

---

## Alternative: Create Workflow Manually in GitHub

If pushing doesn't work, create it directly on GitHub:

### Step 1: Go to Actions Tab

https://github.com/FraudShield1/web-intelligence-platform/actions

### Step 2: Click "New workflow"

### Step 3: Click "set up a workflow yourself"

### Step 4: Name it `worker_fingerprint.yml`

### Step 5: Paste This Content:

```yaml
name: Fingerprint Worker

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  process_fingerprint_jobs:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install sqlalchemy asyncpg pydantic pydantic-settings httpx
      
      - name: Process queued fingerprint jobs
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          UPSTASH_REDIS_URL: ${{ secrets.UPSTASH_REDIS_URL }}
        run: |
          cd backend
          python -m app.workers.github_runner fingerprint --max-jobs=5

      - name: Report status
        if: always()
        run: |
          echo "✅ Fingerprint worker completed"
          echo "Processed up to 5 jobs"
```

### Step 6: Click "Commit changes"

---

## Troubleshooting

### Issue: "Actions" tab is grayed out

**Cause:** GitHub Actions might be disabled for your account or organization

**Fix:**
1. Go to Settings → Actions → General
2. Under "Actions permissions", select:
   - ✅ "Allow all actions and reusable workflows"
3. Save

### Issue: Workflow exists but won't run

**Cause:** Workflow might have errors or no secrets

**Fix:**
1. Click the workflow name
2. Look for error messages
3. Add required secrets (DATABASE_URL)

### Issue: Can't find .github/workflows folder

**Cause:** Folder might not exist in repo

**Fix:** Create it manually:
```bash
cd "/Users/naouri/Downloads/Web Intelligence Platform"
mkdir -p .github/workflows
# (then I'll create the file)
```

---

## Quick Verification

### Test if workflow file exists on GitHub:

Open this URL directly:
```
https://github.com/FraudShield1/web-intelligence-platform/blob/main/.github/workflows/worker_fingerprint.yml
```

**If it loads:** ✅ File exists, just enable Actions
**If 404 error:** ❌ Need to push the file

---

## What to Do Next

1. **Try opening:** https://github.com/FraudShield1/web-intelligence-platform/actions

2. **If you see Actions tab but no workflows:**
   - Tell me and I'll push the workflow file

3. **If you can't find Actions tab at all:**
   - Check repository settings
   - You might not have Actions enabled

4. **If you see "Fingerprint Worker":**
   - Perfect! Continue with adding secrets

---

**Let me know what you see and I'll help you fix it!** 🚀

