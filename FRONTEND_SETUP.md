# 🎨 Frontend Setup & Deployment

## 📍 Current Status

**Frontend URL:** https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app

✅ **Deployed** on Vercel  
⚠️ **Needs Update** to connect to Railway backend

---

## 🔧 What Was Fixed

1. ✅ Updated `App.tsx` to use `VITE_API_URL` (Vite format, not React CRA)
2. ✅ Set default backend URL to Railway production
3. ✅ Created `.env.production` for Vercel
4. ✅ Committed changes to GitHub

---

## 🚀 Deploy Updated Frontend to Vercel

### Option 1: Automatic (Recommended)

Vercel is connected to your GitHub repo, so it should auto-deploy when you push. Check:

1. Go to: https://vercel.com/
2. Find your project
3. Check if it's rebuilding (should happen automatically)
4. Wait ~2 minutes for deployment

### Option 2: Manual Trigger

If auto-deploy didn't trigger:

1. Go to Vercel dashboard
2. Select your frontend project
3. Click "Deployments" tab
4. Click "Redeploy" on the latest deployment

### Option 3: Set Environment Variable in Vercel

For extra safety, set the env var in Vercel dashboard:

1. Go to Vercel → Your Project → Settings → Environment Variables
2. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://web-intelligence-platform-production.up.railway.app/api/v1`
   - **Environments:** Production, Preview, Development
3. Click "Save"
4. Redeploy from Deployments tab

---

## ✅ Test After Deployment

Once redeployed, test the frontend:

```bash
# Open in browser
open https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app
```

**You should see:**
- ✅ Dashboard loads without errors
- ✅ Sites page shows the example.com site we created
- ✅ Jobs page shows the fingerprint job
- ✅ No "failed to load metrics" errors

---

## 🎯 Features in the Frontend

### Pages
1. **Dashboard** (`/`) - Overview metrics and stats
2. **Sites** (`/sites`) - Manage websites for analysis
3. **Jobs** (`/jobs`) - Monitor processing jobs
4. **Analytics** (`/analytics`) - View intelligence reports

### Components
- **Navbar** - Top navigation
- **Sidebar** - Side menu for quick access

---

## 🛠️ Local Development

If you want to run the frontend locally:

```bash
cd frontend

# Install dependencies
npm install

# Create .env for local development
echo "VITE_API_URL=https://web-intelligence-platform-production.up.railway.app/api/v1" > .env

# Run development server
npm run dev

# Open http://localhost:5173
```

---

## 📊 Frontend Stack

- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite (fast, modern)
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Styling:** Custom CSS
- **Hosting:** Vercel

---

## 🔗 API Connection

The frontend connects to:
```
Backend: https://web-intelligence-platform-production.up.railway.app
API Base: /api/v1
```

**Endpoints Used:**
- `GET /analytics/dashboard` - Dashboard metrics
- `GET /sites` - List sites
- `POST /sites` - Create site
- `GET /jobs` - List jobs
- `GET /blueprints` - List blueprints

---

## 🎨 Next Steps (Optional Enhancements)

### Immediate Improvements
1. Add authentication UI (login/logout buttons)
2. Add loading spinners
3. Improve error messages
4. Add site creation form
5. Add job detail view

### Future Features
1. Real-time job updates (WebSocket)
2. Blueprint visualization
3. Site comparison
4. Export functionality
5. Dark mode
6. Mobile responsive design

---

## 💡 Troubleshooting

### Frontend shows "Failed to load metrics"
- **Cause:** Frontend can't reach backend
- **Fix:** Check VITE_API_URL is set correctly in Vercel
- **Verify:** Backend is running at Railway URL

### CORS errors in browser console
- **Cause:** Backend CORS not configured for frontend URL
- **Fix:** Add frontend URL to CORS_ORIGINS in Railway env vars

### "Network Error" in console
- **Cause:** Backend URL is wrong or backend is down
- **Fix:** Check Railway backend is healthy: `/health` endpoint

---

## ✅ After Deployment Checklist

- [ ] Frontend redeployed on Vercel
- [ ] Open frontend URL in browser
- [ ] Check browser console for errors
- [ ] Test Dashboard page loads
- [ ] Test Sites page shows data
- [ ] Test Jobs page shows data
- [ ] No CORS errors
- [ ] No network errors

---

**🎉 Once the frontend is redeployed with the updated config, it will work perfectly with your Railway backend!**

**Frontend will be at:** https://web-intelligence-frontend-re7pv7y48-dedes-projects-ee4b20e7.vercel.app
