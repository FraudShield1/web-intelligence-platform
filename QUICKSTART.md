# ⚡ QUICKSTART - Get Running in 5 Minutes

## Prerequisites
- Docker & Docker Compose installed
- Git
- ~30 seconds to download images

## Step 1: Navigate to Project
```bash
cd /Users/naouri/Downloads/Web\ Intelligence\ Platform
```

## Step 2: Start Everything
```bash
docker-compose up --build
```

**Wait for all services to be healthy** (look for "web_intelligence_api" ready messages)

Takes ~2-3 minutes first time (downloads ~1GB of Docker images)

## Step 3: Open Dashboard
```
http://localhost:3000
```

You should see the **Web Intelligence Platform Dashboard** 🎉

## Step 4: Test It Works

### Add a Site
1. Click **"Sites"** in sidebar
2. Enter domain: `shopify-example.myshopify.com`
3. Click **"Add Site"**
4. Refresh - you should see it in the table

### Check API Health
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "web-intelligence-platform"
}
```

### View API Docs
```
http://localhost:8000/docs
```

Interactive Swagger UI with all endpoints

## Step 5: Create First Job
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "site_id": "<copy site_id from response above>",
    "job_type": "fingerprint",
    "method": "static"
  }'
```

Then check Jobs page - you should see your job!

## Services Running

| Service | URL | Details |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React Dashboard |
| Backend API | http://localhost:8000 | FastAPI with Swagger |
| API Docs | http://localhost:8000/docs | Interactive docs |
| Database | localhost:5432 | PostgreSQL (wip/password) |
| Redis | localhost:6379 | Cache |
| RabbitMQ | http://localhost:15672 | Queue (guest/guest) |

## Logs

### View all logs
```bash
docker-compose logs -f
```

### View specific service
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Stop Services
```bash
docker-compose down
```

## Troubleshooting

### Port already in use
```bash
# Find what's using the port
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Database connection error
```bash
# Reset everything
docker-compose down -v
docker-compose up --build
```

### Frontend not loading
```bash
# Clear browser cache
# Or force refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

## Next Steps

1. ✅ **Dashboard is working** - You're here!
2. 📝 Add more test sites
3. 🔗 Create jobs for each site
4. 📊 Check analytics
5. 🛠️ Add workers (see IMPLEMENTATION_ROADMAP.md)
6. 🧠 Integrate LLM (see PROMPTS.md)

## Documentation

- **README.md** - Full setup guide
- **API_SPEC.md** - All endpoints documented
- **IMPLEMENTATION.md** - Technical architecture
- **BUILD_GUIDE.md** - Development setup
- **IMPLEMENTATION_ROADMAP.md** - 24-week plan

---

**That's it! You now have a running intelligent web scraping platform.** 🚀

Next: Read `BUILD_GUIDE.md` for development setup or `IMPLEMENTATION_ROADMAP.md` for adding features.

