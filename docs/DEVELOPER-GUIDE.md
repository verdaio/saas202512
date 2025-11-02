# Developer Guide - Pet Care Scheduler

**Last Updated:** 2025-11-02
**Project:** saas202512 (Pet Care)
**Architecture:** Multi-tenant SaaS (subdomain model)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Environment Setup](#development-environment-setup)
- [Docker Quick Reference](#docker-quick-reference)
- [Running the Application](#running-the-application)
- [Database Management](#database-management)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tooling

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| **Node.js** | LTS (20.x+) | Frontend (Next.js) | https://nodejs.org |
| **Python** | 3.11+ | Backend (FastAPI) | https://python.org |
| **Docker** | 24.x+ | Containerization | https://docker.com |
| **Docker Compose** | v2 (required) | Multi-container orchestration | Bundled with Docker Desktop |
| **Git** | 2.x+ | Version control | https://git-scm.com |
| **PostgreSQL Client** | 15+ (optional) | Database access | https://postgresql.org |

### Optional Tools

- **pgAdmin** or **DBeaver** - GUI for PostgreSQL
- **Postman** or **Insomnia** - API testing
- **Redis CLI** - Redis debugging (if using sessions)

---

## Development Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/ChrisStephens1971/saas202512.git
cd saas202512
```

### 2. Verify Docker Compose Version

**IMPORTANT:** Docker Compose v2 is required (uses `docker compose` not `docker-compose`)

```bash
# Check version (must be v2.x+)
docker compose version
# Output: Docker Compose version v2.24.0 (or higher)
```

If you have v1 (`docker-compose`), upgrade to Docker Desktop or install Compose v2 standalone.

### 3. Environment Variables

Copy environment template:

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

Edit `.env` files with your local configuration:

**Backend `.env`:**
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5412/petcare_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=petcare_dev

# Redis
REDIS_URL=redis://localhost:6412

# Auth
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Twilio (get from twilio.com)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Stripe (get from stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Frontend `.env`:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8012
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### 4. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## Docker Quick Reference

### Start All Services

```bash
docker compose up -d
```

### Quick Diagnostics

```bash
# Check running containers
docker compose ps

# Expected output:
# NAME                 SERVICE    STATUS     PORTS
# saas202512-postgres  postgres   running    0.0.0.0:5412->5432/tcp
# saas202512-redis     redis      running    0.0.0.0:6412->6379/tcp
# saas202512-backend   backend    running    0.0.0.0:8012->8000/tcp
# saas202512-frontend  frontend   running    0.0.0.0:3012->3000/tcp
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service (PostgreSQL)
docker compose logs -f postgres

# Last 100 lines
docker compose logs --tail=100 postgres

# Backend only
docker compose logs -f backend
```

### Stop Services

```bash
# Stop all
docker compose down

# Stop and remove volumes (CAUTION: deletes data)
docker compose down -v
```

### Restart Single Service

```bash
docker compose restart postgres
docker compose restart backend
```

### Validate Configuration

```bash
# Check docker-compose.yml syntax
docker compose config

# Should output parsed YAML without errors
```

---

## Running the Application

### Option 1: Full Docker Stack

```bash
# Start everything
docker compose up -d

# Access:
# - Frontend: http://localhost:3012
# - Backend API: http://localhost:8012
# - API Docs: http://localhost:8012/docs
```

### Option 2: Local Development (Recommended)

Run database in Docker, apps locally for hot-reload:

```bash
# Start only database services
docker compose up -d postgres redis

# Run backend (separate terminal)
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
uvicorn app.main:app --reload --port 8012

# Run frontend (separate terminal)
cd frontend
npm run dev
```

**Benefits:**
- Faster hot-reload
- Better debugging
- IDE integration

---

## Database Management

### Connect to PostgreSQL

**Using Docker:**
```bash
docker compose exec postgres psql -U postgres -d petcare_dev
```

**Using local client:**
```bash
psql -h localhost -p 5412 -U postgres -d petcare_dev
```

### Migrations (Alembic)

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "add vaccination table"

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history
```

### Database Reset (Development Only)

```bash
# Stop containers
docker compose down

# Remove database volume
docker volume rm saas202512_postgres_data

# Restart and run migrations
docker compose up -d postgres
cd backend
alembic upgrade head
```

### Seed Test Data

```bash
cd backend
python scripts/seed_dev_data.py
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_scheduling.py

# Verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Integration Tests

```bash
# Requires running database
docker compose up -d postgres redis

cd backend
pytest tests/integration/
```

### Smoke Tests (Quick Validation)

```bash
# Backend health check
curl http://localhost:8012/health
# Expected: {"status":"healthy"}

# Frontend
curl http://localhost:3012
# Expected: HTML response

# Database connection
docker compose exec postgres pg_isready
# Expected: /var/run/postgresql:5432 - accepting connections
```

---

## Troubleshooting

### Docker Issues

**Problem:** `docker compose: command not found`
```bash
# Solution: Upgrade to Docker Compose v2
# Install Docker Desktop (includes v2) or:
docker --version  # Check Docker is installed
docker compose version  # Should work, not docker-compose
```

**Problem:** Port already in use (5412, 8012, 3012)
```bash
# Find process using port (Windows PowerShell)
netstat -ano | findstr :5412

# Kill process
taskkill /F /PID <PID>

# Or change port in docker-compose.yml
```

**Problem:** Containers won't start
```bash
# Check logs
docker compose logs

# Remove and rebuild
docker compose down -v
docker compose up -d --build
```

### Database Connection Issues

**Problem:** `psycopg2.OperationalError: could not connect to server`
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs -f postgres

# Verify connection string in .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5412/petcare_dev
```

**Problem:** Migration errors
```bash
# Check migration history
alembic history

# Manually set version (CAREFUL)
alembic stamp head

# Or reset database (development only)
docker compose down -v
docker compose up -d postgres
alembic upgrade head
```

### Backend Issues

**Problem:** Module not found
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** Twilio/Stripe errors
```bash
# Check API keys in .env
# Use test mode keys (sk_test_..., not sk_live_...)
# Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set
```

### Frontend Issues

**Problem:** Module not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

**Problem:** Environment variables not loading
```bash
# NEXT_PUBLIC_ prefix required for client-side vars
NEXT_PUBLIC_API_URL=http://localhost:8012  # ✅ Works
API_URL=http://localhost:8012              # ❌ Won't work in browser
```

---

## OS-Specific Notes

### Windows (PowerShell)

**Scripts use `.ps1` extension:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run PowerShell scripts
.\scripts\seed_data.ps1
```

**Line endings:** Set Git to use LF (not CRLF)
```bash
git config --global core.autocrlf input
```

### macOS/Linux (Bash/Zsh)

**Scripts use `.sh` extension:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run shell scripts
./scripts/seed_data.sh

# May need execute permission
chmod +x scripts/seed_data.sh
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend (Next.js) | 3012 | http://localhost:3012 |
| Backend (FastAPI) | 8012 | http://localhost:8012 |
| API Docs (Swagger) | 8012 | http://localhost:8012/docs |
| PostgreSQL | 5412 | localhost:5412 |
| Redis | 6412 | localhost:6412 |
| MongoDB (reserved) | 27012 | localhost:27012 |

---

## Additional Resources

- **Multi-Tenant Architecture:** `technical/multi-tenant-architecture.md`
- **Contributing Guidelines:** `docs/CONTRIBUTING.md`
- **Testing Guide:** `docs/TESTING-GUIDE.md`
- **Security Guidelines:** `docs/SECURITY.md`
- **Sprint Plans:** `sprints/current/sprint-01-foundation.md` (etc.)
- **Product Roadmap:** `product/roadmap/2025-Q1-roadmap.md`

---

## Getting Help

1. Check this guide first
2. Review sprint plan for current work
3. Check GitHub issues
4. Ask in team chat (if applicable)
5. Create GitHub issue with:
   - What you tried
   - Error messages
   - Environment details (OS, Docker version, etc.)

---

**Happy coding!** 🚀
