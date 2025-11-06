# 🚨 FORCE VERCEL TO REBUILD (Clear Cache)

## ❌ Problem
Vercel deployed bundle **still has localhost:8000** hardcoded (confirmed by testing actual bundle).

## ✅ Solution: Force Clean Rebuild

### Option 1: Via Vercel Dashboard (EASIEST) ⭐

1. Go to: https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend
2. Click **"Deployments"** tab
3. Find the **latest deployment**
4. Click the **3 dots** menu (⋮)
5. Click **"Redeploy"**
6. ✅ **CHECK "Use existing Build Cache" → UNCHECK IT!**
7. Click **"Redeploy"**

### Option 2: Delete .vercel Cache + Redeploy

1. Go to: https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend/settings
2. Scroll to **"Build & Development Settings"**
3. Click **"Clear Build Cache"**
4. Go back to **Deployments**
5. Click **"Redeploy"** on latest

### Option 3: Create Deploy Hook (Automated)

1. Go to: https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend/settings/git
2. Scroll to **"Deploy Hooks"**
3. Click **"Create Hook"**
   - Name: `force-rebuild`
   - Branch: `main`
4. Copy the webhook URL
5. Run this in terminal:

```bash
curl -X POST "YOUR_WEBHOOK_URL_HERE"
```

---

## 🧪 How to Verify It's Fixed

After redeployment completes (~2 minutes):

```bash
# Test the actual deployed bundle
curl -s "https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app/assets/index-DgGcAAKw.js" | grep -o 'railway\.app[^"]*' | head -3
```

Should show: `railway.app/api/v1`

---

## ⚡ What I Changed

1. **Updated `frontend/vercel.json`:**
   ```json
   "buildCommand": "rm -rf dist node_modules/.vite && npm run build"
   ```
   This forces Vite to rebuild from scratch.

2. **Already hardcoded Railway URL in `frontend/src/App.tsx`:**
   ```typescript
   const API_URL = 'https://web-intelligence-platform-production.up.railway.app/api/v1';
   ```

3. **Pushed to GitHub** (commit: `0996050`)

---

## 🎯 Do This Now

1. **Open Vercel Dashboard**: https://vercel.com/dedes-projects-ee4b20e7/web-intelligence-frontend
2. **Go to Deployments**
3. **Click 3 dots on latest deployment**
4. **Click "Redeploy"**
5. **UNCHECK "Use existing Build Cache"** ← CRITICAL!
6. **Click "Redeploy"**
7. **Wait 2 minutes**
8. **Test in incognito window**

---

## 🔍 Why This Happened

Vercel caches builds aggressively. Even though:
- ✅ Code has Railway URL
- ✅ GitHub has latest code
- ✅ Auto-deploy triggered

Vercel still served the **cached build** with localhost URLs.

The fix: **Force clean rebuild without cache**.

---

## ✅ Success Indicators

After rebuild, you should see:

1. **In browser console:**
   ```
   API Base URL: https://web-intelligence-platform-production.up.railway.app/api/v1
   ```

2. **Dashboard loads** with metrics
3. **No CORS errors**
4. **No "Network Error"**

---

**👉 Go redeploy in Vercel now with cache disabled!**

