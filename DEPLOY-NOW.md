# 🚀 Deployment Commands - Run on Your Local Machine

**Environment**: Docker isn't available in the Claude Code environment. Run these commands on your **Windows machine** where Docker Desktop is installed.

---

## Step-by-Step Deployment

### 1. Open PowerShell or Command Prompt

Navigate to your project:
```bash
cd C:\devop\saas202512
```

### 2. Verify Docker Desktop is Running

```bash
docker ps
```

**Expected**: Should show running containers or empty list (not an error)

**If error**: Start Docker Desktop from Start Menu

---

### 3. Deploy the Complete Stack

```bash
# Deploy all services (PostgreSQL, Redis, API, Frontend)
docker-compose -f docker-compose.full.yml up --build -d
```

**What this does**:
- Builds the API container (Python FastAPI)
- Builds the Web container (Next.js)
- Starts PostgreSQL container
- Starts Redis container
- Runs all services in detached mode (-d)

**Expected output**:
```
[+] Building ...
[+] Running 4/4
 ✔ Container saas202512-postgres  Started
 ✔ Container saas202512-redis     Started
 ✔ Container saas202512-api       Started
 ✔ Container saas202512-web       Started
```

---

### 4. Check Service Status

```bash
# View all running containers
docker-compose -f docker-compose.full.yml ps
```

**Expected**: All services should show "Up" status

```
NAME                   STATUS         PORTS
saas202512-postgres    Up (healthy)   0.0.0.0:5412->5432/tcp
saas202512-redis       Up (healthy)   0.0.0.0:6412->6379/tcp
saas202512-api         Up (healthy)   0.0.0.0:5410->5410/tcp
saas202512-web         Up             0.0.0.0:3010->3010/tcp
```

---

### 5. Watch Logs (Optional)

```bash
# View logs from all services
docker-compose -f docker-compose.full.yml logs -f

# View logs from specific service
docker-compose -f docker-compose.full.yml logs -f api
docker-compose -f docker-compose.full.yml logs -f web
```

**Press Ctrl+C to stop watching logs**

---

### 6. Test the Application

Open these URLs in your browser:

#### Frontend (Booking Widget)
```
http://localhost:3010
```
**Expected**: Pet Care booking widget loads

#### API Documentation
```
http://localhost:5410/api/v1/docs
```
**Expected**: Interactive Swagger API documentation

#### Health Check
```
http://localhost:5410/health
```
**Expected**: `{"status": "healthy"}`

---

### 7. Verify Database

```bash
# Connect to PostgreSQL container
docker exec -it saas202512-postgres psql -U postgres -d saas202512

# Inside PostgreSQL shell, run:
\dt                    # List all tables (should show 11 tables)
SELECT * FROM tenants; # Check tenant data
\q                     # Exit
```

---

## Troubleshooting

### Issue: "Cannot connect to the Docker daemon"
**Solution**: Start Docker Desktop from Windows Start Menu, wait 30 seconds, try again

### Issue: "Port already in use"
**Solution**: Stop conflicting services or containers
```bash
# Stop all project containers
docker-compose -f docker-compose.full.yml down

# Check what's using the port
netstat -ano | findstr :3010
netstat -ano | findstr :5410
```

### Issue: "Build failed" or "Container exits immediately"
**Solution**: View detailed logs
```bash
docker-compose -f docker-compose.full.yml logs api
docker-compose -f docker-compose.full.yml logs web
```

### Issue: Database migrations not applied
**Solution**: Run migrations manually
```bash
docker exec -it saas202512-api alembic upgrade head
```

---

## Management Commands

### Stop All Services
```bash
docker-compose -f docker-compose.full.yml down
```

### Restart All Services
```bash
docker-compose -f docker-compose.full.yml restart
```

### Rebuild After Code Changes
```bash
docker-compose -f docker-compose.full.yml up --build -d
```

### View Resource Usage
```bash
docker stats
```

---

## What's Running After Deployment

| Service | Container Name | Port | URL |
|---------|---------------|------|-----|
| Frontend | saas202512-web | 3010 | http://localhost:3010 |
| API | saas202512-api | 5410 | http://localhost:5410 |
| PostgreSQL | saas202512-postgres | 5412 | localhost:5412 |
| Redis | saas202512-redis | 6412 | localhost:6412 |

---

## Next Steps After Successful Deployment

1. **Test the booking flow** - Create a test booking through the widget
2. **Explore the API** - Try endpoints in http://localhost:5410/api/v1/docs
3. **Check the database** - View created data in PostgreSQL
4. **Enable monitoring** (optional) - Set up Sentry or Application Insights
5. **Plan Sprint 4** - Admin dashboard and reporting features

---

## 📊 Success Checklist

- [ ] All containers show "Up (healthy)" status
- [ ] Frontend loads at http://localhost:3010
- [ ] API docs accessible at http://localhost:5410/api/v1/docs
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Database has 11 tables
- [ ] Can create a test booking through the widget

---

**Time to deploy**: ~5-10 minutes (first build takes longer)

**Questions?** Paste any error messages and I'll help troubleshoot!
