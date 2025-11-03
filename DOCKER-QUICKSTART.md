# 🐳 Docker Quick Start Guide

The easiest way to run the entire Pet Care SaaS platform is with Docker.

## Prerequisites

- Docker Desktop installed and running
- 5 minutes of your time

## Quick Start (3 Commands)

### 1. Set Environment Variables

Copy the example file:
```bash
cp api/.env.example api/.env
```

Edit `api/.env` and add your Stripe and Twilio credentials (optional for testing).

### 2. Start Everything

```bash
# Build and start all services
docker-compose -f docker-compose.full.yml up --build
```

This will start:
- **PostgreSQL** (port 5412)
- **Redis** (port 6412)
- **Backend API** (port 5410)
- **Frontend** (port 3010)

### 3. Access Application

Open your browser:
- **Booking Widget**: http://localhost:3010
- **API Documentation**: http://localhost:5410/api/v1/docs
- **Health Check**: http://localhost:5410/health

## What's Happening?

1. **PostgreSQL**: Database is created and migrations run automatically
2. **Backend API**: FastAPI server starts with all 90+ endpoints
3. **Frontend**: Next.js dev server starts with booking widget
4. **Networking**: All services are connected on the same Docker network

## Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.full.yml down

# Stop and remove volumes (clean slate)
docker-compose -f docker-compose.full.yml down -v
```

## Viewing Logs

```bash
# All services
docker-compose -f docker-compose.full.yml logs -f

# Specific service
docker-compose -f docker-compose.full.yml logs -f api
docker-compose -f docker-compose.full.yml logs -f web
docker-compose -f docker-compose.full.yml logs -f postgres
```

## Database Access

```bash
# Connect to PostgreSQL
docker exec -it saas202512-postgres psql -U postgres -d saas202512

# Check tables
\dt

# View data
SELECT * FROM tenants;
SELECT * FROM services;
```

## Troubleshooting

### Port Already in Use

If you get "port already allocated" errors:

```bash
# Check what's using the ports
netstat -ano | findstr :5410
netstat -ano | findstr :3010
netstat -ano | findstr :5412

# Stop the process or change ports in docker-compose.full.yml
```

### Build Issues

```bash
# Clean rebuild
docker-compose -f docker-compose.full.yml down -v
docker-compose -f docker-compose.full.yml build --no-cache
docker-compose -f docker-compose.full.yml up
```

### Database Not Initializing

```bash
# Check migrations
docker-compose -f docker-compose.full.yml exec api alembic current
docker-compose -f docker-compose.full.yml exec api alembic upgrade head
```

## Production Deployment

For production, update environment variables:

```env
# api/.env
DEBUG=False
DATABASE_URL=postgresql://user:password@your-db-host:5432/prod_db
JWT_SECRET=your-secure-random-secret
STRIPE_SECRET_KEY=sk_live_your_key
TWILIO_ACCOUNT_SID=your_production_sid
```

Then deploy to:
- **AWS**: ECS/Fargate
- **Azure**: Container Apps
- **GCP**: Cloud Run
- **Kubernetes**: Use provided Dockerfiles with K8s manifests

## Alternative: Just Backend/Frontend Only

Already have PostgreSQL and Redis running? Use the existing docker-compose:

```bash
# Just start database services (already running for you)
docker-compose up -d

# Run API locally
cd api
pip install -r requirements.txt
uvicorn src.main:app --reload --port 5410

# Run frontend locally
cd web
npm install
npm run dev
```

## Testing the Application

1. **Open Frontend**: http://localhost:3010
2. **Select a Service**: Click on a grooming service
3. **Choose Date/Time**: Pick an available slot
4. **Enter Information**: Fill in pet owner details
5. **Confirm**: See confirmation screen

## Features Ready to Use

✅ Service catalog
✅ Real-time availability
✅ Multi-pet booking
✅ SMS notifications (when Twilio configured)
✅ Payment processing (when Stripe configured)
✅ Vaccination tracking
✅ Multi-tenant support

## Next Steps

1. Add your first service via API:
```bash
curl -X POST http://localhost:5410/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Happy Paws Grooming",
    "subdomain": "happypaws",
    "email": "owner@happypaws.com",
    "password": "SecurePassword123!"
  }'
```

2. Login and add services via API docs: http://localhost:5410/api/v1/docs

3. Test booking widget: http://localhost:3010

---

**You're ready to go! 🚀**

All 3 sprints are complete and everything is running in Docker.
