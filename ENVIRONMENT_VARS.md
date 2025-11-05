# 🔐 Environment Variables for Production

## ⚠️ IMPORTANT: Never commit these values to git!

Add these to:
1. **Vercel Dashboard** → Project → Settings → Environment Variables
2. **GitHub** → Repository → Settings → Secrets and variables → Actions

---

## 📋 Complete List

### Supabase (Database) ✅
```
DATABASE_URL
postgresql+asyncpg://postgres:Xonique99@db.aeajgihhgplxcvcsiqeo.supabase.co:6543/postgres

VITE_SUPABASE_URL
https://aeajgihhgplxcvcsiqeo.supabase.co

VITE_SUPABASE_ANON_KEY
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlYWpnaWhoZ3BseGN2Y3NpcWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzMjY1MzMsImV4cCI6MjA3NzkwMjUzM30.KgZrArrNkk_8ujSMhu-QL5TCG9Elv9YHdTp4oxScbKM
```

### Upstash Redis ✅
```
UPSTASH_REDIS_REST_URL
https://pure-halibut-27195.upstash.io

UPSTASH_REDIS_REST_TOKEN
AWo7AAIncDIyNmQ5NzkxZDQxMzc0ZGQ5YWY4NGIzNDljYzM0NjM3ZHAyMjcxOTU
```

### OpenRouter (LLM) ✅
```
OPENROUTER_API_KEY
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
```

### Security (Generate New!)
```
JWT_SECRET
[Generate a strong random string - use: openssl rand -base64 32]
```

---

## 🚀 Quick Setup Commands

### For Vercel (Frontend)
```bash
vercel env add VITE_API_URL production
# Enter: https://your-backend.vercel.app/api

vercel env add VITE_SUPABASE_URL production
# Enter: https://aeajgihhgplxcvcsiqeo.supabase.co

vercel env add VITE_SUPABASE_ANON_KEY production
# Paste the long key above
```

### For Vercel (Backend)
```bash
vercel env add DATABASE_URL production
# Paste the PostgreSQL URL above

vercel env add UPSTASH_REDIS_REST_URL production
# Enter: https://pure-halibut-27195.upstash.io

vercel env add UPSTASH_REDIS_REST_TOKEN production
# Paste the Upstash token above

vercel env add OPENROUTER_API_KEY production
# Paste: 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

vercel env add JWT_SECRET production
# Generate: openssl rand -base64 32

vercel env add CORS_ORIGINS production
# Enter: ["https://your-frontend.vercel.app"]
```

### For GitHub Actions
Go to: Repository → Settings → Secrets and variables → Actions → New repository secret

Add each:
1. `DATABASE_URL` → (PostgreSQL URL)
2. `UPSTASH_REDIS_REST_URL` → https://pure-halibut-27195.upstash.io
3. `UPSTASH_REDIS_REST_TOKEN` → (Your token)
4. `OPENROUTER_API_KEY` → (Your key)
5. `JWT_SECRET` → (Generate with openssl)

---

## 🔒 Security Notes

1. **JWT_SECRET**: Generate a strong random string:
   ```bash
   openssl rand -base64 32
   ```
   Output example: `xK7vN2pQ8mR9sT4uV5wX6yZ7aB8cD9eF0gH1iJ2kL3m=`

2. **Never commit** `.env` files with real credentials

3. **Rotate keys** regularly (every 90 days recommended)

4. **Use different values** for development and production

---

## ✅ Verification

After adding all variables:

### Test Backend
```bash
curl https://your-backend.vercel.app/api/health
# Should return: {"status":"healthy"...}
```

### Test Frontend
Open: https://your-frontend.vercel.app
- Should load without errors
- Check browser console for API connection

### Test Workers
GitHub → Actions → Run "Fingerprint Worker" manually
- Should connect to database
- Should process jobs successfully

---

## 🎯 All Set!

Once you add these environment variables:
- ✅ Vercel will use them automatically
- ✅ GitHub Actions will access them securely
- ✅ Your app will be fully functional

**Next:** Follow `DEPLOY_FREE.md` to deploy! 🚀

