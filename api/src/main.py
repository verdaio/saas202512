"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .middleware.tenant import TenantMiddleware
from .db.base import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant middleware
app.add_middleware(TenantMiddleware)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Pet Care API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


# Import and include routers
from .api import auth, staff, owners, pets, services, resources, appointments, packages, payments, vaccination_records

# Authentication
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

# Staff management
app.include_router(staff.router, prefix=f"{settings.API_V1_STR}/staff", tags=["staff"])

# Pet owners
app.include_router(owners.router, prefix=f"{settings.API_V1_STR}/owners", tags=["owners"])

# Pets
app.include_router(pets.router, prefix=f"{settings.API_V1_STR}/pets", tags=["pets"])

# Services
app.include_router(services.router, prefix=f"{settings.API_V1_STR}/services", tags=["services"])

# Resources
app.include_router(resources.router, prefix=f"{settings.API_V1_STR}/resources", tags=["resources"])

# Appointments
app.include_router(appointments.router, prefix=f"{settings.API_V1_STR}/appointments", tags=["appointments"])

# Packages (punch cards, memberships)
app.include_router(packages.router, prefix=f"{settings.API_V1_STR}/packages", tags=["packages"])

# Payments
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])

# Vaccination records
app.include_router(vaccination_records.router, prefix=f"{settings.API_V1_STR}/vaccinations", tags=["vaccinations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
