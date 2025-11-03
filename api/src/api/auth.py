"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..core.security import (
    verify_password,
    get_password_hash,
    create_tenant_token
)
from ..schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    RefreshTokenRequest
)
from ..models.tenant import Tenant, TenantStatus
from ..models.user import User, UserRole
import uuid

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    Register new tenant and owner user
    """
    # Check if subdomain already exists
    existing_tenant = db.query(Tenant).filter(
        Tenant.subdomain == signup_data.subdomain
    ).first()

    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain already taken"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == signup_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        business_name=signup_data.business_name,
        subdomain=signup_data.subdomain,
        email=signup_data.email,
        phone=signup_data.phone,
        status=TenantStatus.TRIAL,
        is_active=True,
        plan_type="trial",
        timezone="America/New_York",
        currency="USD"
    )

    db.add(tenant)
    db.flush()  # Get tenant ID

    # Create owner user
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=signup_data.email,
        password_hash=get_password_hash(signup_data.password),
        role=UserRole.OWNER,
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        is_active=True,
        is_verified=False,
        sms_opted_in=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    tokens = create_tenant_token(
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        email=user.email,
        role=user.role.value
    )

    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return access token
    """
    # Find user by email
    user = db.query(User).filter(
        User.email == login_data.email,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check tenant is active
    tenant = db.query(Tenant).filter(
        Tenant.id == user.tenant_id,
        Tenant.is_active == True
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended or tenant inactive"
        )

    # If subdomain provided, verify user belongs to that tenant
    if login_data.subdomain:
        if tenant.subdomain != login_data.subdomain:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials for this tenant"
            )

    # Generate tokens
    tokens = create_tenant_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        role=user.role.value
    )

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    from ..core.security import decode_token

    # Decode refresh token
    payload = decode_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    user = db.query(User).filter(
        User.id == uuid.UUID(payload["sub"]),
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    tokens = create_tenant_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        role=user.role.value
    )

    return tokens


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete tokens)
    """
    return {"message": "Logged out successfully"}
