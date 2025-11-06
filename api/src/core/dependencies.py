"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..db.base import get_db
from ..core.security import decode_token
from ..models.user import User, UserRole
from ..models.tenant import Tenant

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user from database
    user = db.query(User).filter(
        User.id == UUID(user_id_str),
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Get current user's tenant (requires authentication)
    """
    tenant = db.query(Tenant).filter(
        Tenant.id == current_user.tenant_id,
        Tenant.is_active == True
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )

    return tenant


async def get_public_tenant(
    request: Request,
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Get tenant from request state (set by middleware)
    Does not require authentication - for public endpoints like booking widget
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


def require_role(required_role: UserRole):
    """
    Dependency factory to require specific user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role.value}"
            )
        return current_user
    return role_checker


def require_owner(current_user: User = Depends(get_current_user)):
    """
    Require user to be OWNER role
    """
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only business owners can perform this action"
        )
    return current_user


def require_staff_or_admin(current_user: User = Depends(get_current_user)):
    """
    Require user to be STAFF, ADMIN, or OWNER
    """
    allowed_roles = [UserRole.STAFF, UserRole.ADMIN, UserRole.OWNER]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user
