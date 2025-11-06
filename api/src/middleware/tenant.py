"""
Tenant resolution and scoping middleware
"""
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import re

from ..core.config import settings
from ..models.tenant import Tenant


class TenantMiddleware:
    """
    Middleware to resolve tenant from request and add to request state
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        tenant_id = await self.resolve_tenant(request)

        # Add tenant_id to request state
        scope["state"] = {"tenant_id": tenant_id}

        await self.app(scope, receive, send)

    async def resolve_tenant(self, request: Request) -> Optional[str]:
        """
        Resolve tenant ID from request based on configuration
        """
        if settings.TENANT_RESOLUTION == "subdomain":
            return await self._resolve_from_subdomain(request)
        elif settings.TENANT_RESOLUTION == "header":
            return await self._resolve_from_header(request)
        elif settings.TENANT_RESOLUTION == "path":
            return await self._resolve_from_path(request)
        else:
            return None

    async def _resolve_from_subdomain(self, request: Request) -> Optional[str]:
        """
        Extract tenant subdomain from host header
        Example: happypaws.petcare.local -> happypaws
        """
        host = request.headers.get("host", "")

        # Extract subdomain
        # Pattern: subdomain.domain.tld or subdomain.localhost:port
        match = re.match(r"^([a-z0-9-]+)\.(.*)", host)

        if match:
            subdomain = match.group(1)

            # Skip common non-tenant subdomains
            if subdomain in ["www", "api", "admin"]:
                return None

            return subdomain

        # Default to "demo" tenant for localhost (development/testing)
        if "localhost" in host or "127.0.0.1" in host:
            return "demo"

        return None

    async def _resolve_from_header(self, request: Request) -> Optional[str]:
        """
        Extract tenant ID from custom header
        """
        return request.headers.get(settings.TENANT_HEADER_NAME)

    async def _resolve_from_path(self, request: Request) -> Optional[str]:
        """
        Extract tenant ID from URL path
        Example: /tenants/{tenant_id}/...
        """
        path = request.url.path
        match = re.match(r"^/tenants/([^/]+)", path)

        if match:
            return match.group(1)

        return None


def get_current_tenant(request: Request, db: Session) -> Tenant:
    """
    Get current tenant from request state
    """
    tenant_subdomain = getattr(request.state, "tenant_id", None)

    if not tenant_subdomain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context not found"
        )

    # Look up tenant by subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == tenant_subdomain,
        Tenant.is_active == True
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found: {tenant_subdomain}"
        )

    return tenant


def require_tenant_access(user_tenant_id: str, resource_tenant_id: str):
    """
    Verify user has access to resource's tenant
    Raises HTTPException if access denied
    """
    if user_tenant_id != resource_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: resource belongs to different tenant"
        )
