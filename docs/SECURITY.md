# Security Guidelines - Pet Care Scheduler

**Last Updated:** 2025-11-02
**Project:** saas202512 (Pet Care)
**Audience:** Developers, DevOps, Security Reviewers

---

## Table of Contents

- [Security Philosophy](#security-philosophy)
- [Secrets Management](#secrets-management)
- [Multi-Tenant Security](#multi-tenant-security)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [API Security](#api-security)
- [Incident Response](#incident-response)
- [Security Checklist](#security-checklist)

---

## Security Philosophy

**Core Principles:**
1. **Defense in Depth** - Multiple layers of security
2. **Least Privilege** - Minimal access required
3. **Secure by Default** - Security built-in, not bolted-on
4. **Fail Securely** - Errors don't expose sensitive data
5. **Zero Trust** - Verify everything, trust nothing

---

## Secrets Management

### ❌ NEVER Do This

**DO NOT store secrets in:**
- Source code (hardcoded values)
- Configuration files committed to Git
- `parameters.*.json` files
- Environment variable files (`.env`) committed to Git
- Comments or documentation
- Client-side code
- Logs or error messages

**Examples of secrets:**
- API keys (Twilio, Stripe, etc.)
- Database passwords
- JWT signing keys
- Encryption keys
- OAuth client secrets
- Webhook secrets
- Private keys (.pem, .key files)

### ✅ Proper Secrets Management

**Development Environment:**

1. **Use `.env` files (never commit):**
   ```bash
   # .env (DO NOT COMMIT)
   DATABASE_URL=postgresql://user:password@localhost:5412/db
   JWT_SECRET=super-secret-key-change-in-production
   TWILIO_AUTH_TOKEN=your_auth_token
   STRIPE_SECRET_KEY=sk_test_...
   ```

2. **Provide `.env.example` template:**
   ```bash
   # .env.example (COMMIT THIS)
   DATABASE_URL=postgresql://user:password@localhost:5412/db
   JWT_SECRET=change-me-in-production
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
   ```

3. **Document in Developer Guide:**
   - What secrets are needed
   - Where to get them (Twilio.com, Stripe.com)
   - How to configure them locally

**Production Environment:**

1. **Use Azure Key Vault (or equivalent):**
   ```python
   # backend/app/config.py
   from azure.identity import DefaultAzureCredential
   from azure.keyvault.secrets import SecretClient

   # Connect to Key Vault
   credential = DefaultAzureCredential()
   client = SecretClient(
       vault_url="https://petcare-keyvault.vault.azure.net/",
       credential=credential
   )

   # Retrieve secrets
   JWT_SECRET = client.get_secret("jwt-secret").value
   DATABASE_URL = client.get_secret("database-url").value
   TWILIO_AUTH_TOKEN = client.get_secret("twilio-auth-token").value
   ```

2. **Reference secure parameters in config:**
   ```json
   // parameters.prod.json (SAFE to commit)
   {
     "keyVaultName": "petcare-keyvault",
     "secrets": {
       "jwtSecret": {
         "reference": "@Microsoft.KeyVault(SecretUri=https://petcare-keyvault.vault.azure.net/secrets/jwt-secret/)"
       },
       "databaseUrl": {
         "reference": "@Microsoft.KeyVault(SecretUri=https://petcare-keyvault.vault.azure.net/secrets/database-url/)"
       }
     }
   }
   ```

3. **Use Managed Identity for access:**
   - No credentials in code
   - App Service managed identity accesses Key Vault
   - Audit logs for all secret access

### Environment-Specific Secrets

| Environment | Secret Storage | Access Method |
|-------------|----------------|---------------|
| **Development** | `.env` files (local) | Direct read |
| **CI/CD** | GitHub Secrets | Environment variables |
| **Staging** | Azure Key Vault | Managed Identity |
| **Production** | Azure Key Vault | Managed Identity |

### Rotating Secrets

**Schedule:**
- **API keys:** Rotate every 90 days
- **Database passwords:** Rotate every 180 days
- **JWT secrets:** Rotate every 365 days
- **After incident:** Rotate immediately

**Process:**
1. Generate new secret in provider (Twilio, Stripe)
2. Add new secret to Key Vault
3. Update application config reference
4. Deploy and verify
5. Revoke old secret
6. Monitor for errors

---

## Multi-Tenant Security

**Critical:** Multi-tenant isolation is paramount. A breach in one tenant must not affect others.

### Tenant Data Isolation

**Database Level:**
```python
# ALWAYS include tenant_id in queries
@tenant_scoped
def get_appointments(tenant_id: UUID, date: date):
    return db.query(Appointment).filter(
        Appointment.tenant_id == tenant_id,
        Appointment.scheduled_start >= date
    ).all()

# NEVER do this (missing tenant filter)
def get_appointments_UNSAFE(date: date):
    return db.query(Appointment).filter(
        Appointment.scheduled_start >= date
    ).all()  # ❌ Returns appointments from all tenants!
```

**Row-Level Security (PostgreSQL):**
```sql
-- Enable RLS on all tenant tables
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON appointments
FOR ALL
USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Set tenant context per request
SET app.current_tenant = '123e4567-e89b-12d3-a456-426614174000';
```

**Application Level:**
```python
# Middleware extracts tenant from subdomain
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # Extract subdomain (e.g., happypaws.petcare.com)
    host = request.headers.get("host")
    subdomain = host.split(".")[0]

    # Look up tenant
    tenant = get_tenant_by_subdomain(subdomain)
    if not tenant:
        return JSONResponse({"error": "Invalid tenant"}, status_code=404)

    # Inject into request state
    request.state.tenant_id = tenant.id

    return await call_next(request)
```

### Prevent Cross-Tenant Access

**Verify tenant ownership:**
```python
@app.get("/api/v1/appointments/{appointment_id}")
def get_appointment(
    appointment_id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404)

    # CRITICAL: Verify tenant ownership
    if appointment.tenant_id != request.state.tenant_id:
        # Log security incident
        log_security_event("cross_tenant_access_attempt", {
            "user": request.user.id,
            "requested_tenant": appointment.tenant_id,
            "actual_tenant": request.state.tenant_id
        })
        raise HTTPException(status_code=403, detail="Forbidden")

    return appointment
```

### File Storage Isolation

**Use tenant prefix:**
```python
# Store files with tenant prefix
def upload_vaccination_card(tenant_id: UUID, pet_id: UUID, file: UploadFile):
    # ✅ Tenant-scoped path
    file_path = f"{tenant_id}/vax-cards/{pet_id}/{file.filename}"

    # Upload to S3/Azure Blob with tenant prefix
    storage.upload(file_path, file)

    # ❌ NEVER use global path
    # file_path = f"vax-cards/{pet_id}/{file.filename}"  # Missing tenant_id!
```

**Access control:**
```python
def get_vaccination_card(tenant_id: UUID, file_path: str):
    # Verify file belongs to tenant
    if not file_path.startswith(f"{tenant_id}/"):
        raise HTTPException(status_code=403)

    return storage.download(file_path)
```

---

## Authentication & Authorization

### JWT Token Security

**Token Structure:**
```python
{
    "user_id": "uuid",
    "tenant_id": "uuid",
    "email": "user@example.com",
    "role": "owner",
    "exp": 1234567890,  # Expiration
    "iat": 1234567890,  # Issued at
    "jti": "unique-token-id"  # JWT ID for revocation
}
```

**Best Practices:**
- **Short expiration:** 24 hours max
- **Refresh tokens:** Separate long-lived refresh token
- **Revocation:** Use JTI for token blacklist
- **HTTPS only:** Never send over HTTP
- **Secure storage:** HttpOnly cookies (not localStorage)

**Example:**
```python
from datetime import datetime, timedelta
import jwt

def create_access_token(user_id: UUID, tenant_id: UUID, role: str):
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
        "jti": str(uuid4())  # Unique token ID
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Check if revoked
        if is_token_revoked(payload["jti"]):
            raise HTTPException(status_code=401, detail="Token revoked")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Password Security

**Hashing:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Requirements:**
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers
- No common passwords (use dictionary check)
- Rate limiting on login attempts

### Role-Based Access Control (RBAC)

**Roles:**
- `owner` - Tenant owner, full access
- `admin` - Staff with admin privileges
- `staff` - Regular staff member
- `viewer` - Read-only access

**Permission check:**
```python
from functools import wraps

def require_role(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_role = request.state.user.role

            role_hierarchy = {"viewer": 0, "staff": 1, "admin": 2, "owner": 3}

            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 99):
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.delete("/api/v1/appointments/{id}")
@require_role("admin")  # Only admin or owner can delete
async def delete_appointment(id: UUID, request: Request):
    ...
```

---

## Data Protection

### Sensitive Data Handling

**Pet Owner Personal Information:**
- Name, email, phone, address
- Payment card details (never store, use Stripe tokens)
- Pet health records

**Encryption:**
- **At rest:** Database encryption (Azure SQL, RDS encryption)
- **In transit:** TLS 1.2+ for all connections
- **Backups:** Encrypted backups

**Data Minimization:**
- Only collect what's needed
- Delete data when no longer needed
- Anonymize logs

### PCI DSS Compliance (Payments)

**DO:**
- ✅ Use Stripe Elements (PCI-compliant iframe)
- ✅ Never handle raw card numbers
- ✅ Store Stripe customer ID and payment method ID only
- ✅ Use HTTPS for all payment pages

**DON'T:**
- ❌ Store CVV/CVC codes
- ❌ Store full card numbers
- ❌ Log payment details

**Example:**
```typescript
// Frontend: Use Stripe Elements
import { CardElement } from '@stripe/react-stripe-js';

function PaymentForm() {
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Create payment method (Stripe handles card data)
    const {error, paymentMethod} = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,  // Stripe handles securely
    });

    if (error) {
      console.error(error);
    } else {
      // Send only payment method ID to backend
      await fetch('/api/booking', {
        method: 'POST',
        body: JSON.stringify({
          paymentMethodId: paymentMethod.id,  // ✅ Safe to send
          // ❌ NEVER send card number
        })
      });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />  {/* Stripe-hosted, PCI-compliant */}
      <button type="submit">Pay</button>
    </form>
  );
}
```

---

## API Security

### Input Validation

**Validate all inputs:**
```python
from pydantic import BaseModel, EmailStr, constr, validator

class CreateOwnerRequest(BaseModel):
    name: constr(min_length=1, max_length=100)  # Length constraints
    email: EmailStr  # Email validation
    phone: constr(regex=r'^\+?1?\d{10,15}$')  # Phone format

    @validator('name')
    def validate_name(cls, v):
        # No SQL injection attempts
        if any(char in v for char in ['<', '>', ';', '--']):
            raise ValueError('Invalid characters in name')
        return v
```

### SQL Injection Prevention

**Use parameterized queries:**
```python
# ✅ SAFE: SQLAlchemy ORM
appointments = db.query(Appointment).filter(
    Appointment.tenant_id == tenant_id,
    Appointment.pet_id == pet_id
).all()

# ✅ SAFE: Parameterized raw SQL
db.execute(
    "SELECT * FROM appointments WHERE tenant_id = :tenant_id",
    {"tenant_id": tenant_id}
)

# ❌ UNSAFE: String concatenation
query = f"SELECT * FROM appointments WHERE pet_id = '{pet_id}'"  # DON'T!
```

### XSS Prevention

**Frontend:**
```tsx
// ✅ React escapes by default
<div>{ownerName}</div>

// ❌ Dangerous: dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userInput}} />  // DON'T!
```

**Backend:**
```python
# Sanitize HTML if accepting rich text
from bleach import clean

def sanitize_html(html: str) -> str:
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'li']
    return clean(html, tags=allowed_tags, strip=True)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, credentials: LoginRequest):
    ...
```

---

## Incident Response

### Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

**Instead:**
1. Email: chris.stephens@verdaio.com
2. Subject: "[SECURITY] Pet Care - <brief description>"
3. Include: Steps to reproduce, impact, suggested fix

### Incident Response Plan

**If security breach detected:**

1. **Immediate (0-1 hour):**
   - Contain the breach (revoke access, shutdown service if needed)
   - Notify team lead
   - Preserve evidence (logs, database snapshots)

2. **Short-term (1-24 hours):**
   - Assess impact (what data was exposed?)
   - Identify root cause
   - Deploy fix
   - Rotate all secrets

3. **Long-term (1-7 days):**
   - Notify affected users (if PII exposed)
   - Document incident in `incidents/YYYY-MM-DD-incident.md`
   - Conduct post-mortem
   - Update security procedures

---

## Security Checklist

### Before Every PR

- [ ] No secrets in code or config files
- [ ] No secrets in `parameters.*.json`
- [ ] All inputs validated
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CSRF protection enabled (for state-changing operations)
- [ ] Multi-tenant isolation tested
- [ ] Authentication required on protected routes
- [ ] Authorization checked (role-based access)

### Before Production Deployment

- [ ] All secrets in Key Vault
- [ ] HTTPS enforced (no HTTP)
- [ ] Database encryption enabled
- [ ] Backup and disaster recovery tested
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Rate limiting enabled
- [ ] Logging and monitoring configured
- [ ] Incident response plan documented
- [ ] Security audit completed

---

## Additional Resources

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Azure Key Vault Docs:** https://docs.microsoft.com/en-us/azure/key-vault/
- **Stripe Security:** https://stripe.com/docs/security
- **Multi-Tenant Architecture:** `technical/multi-tenant-architecture.md`

---

**Security is everyone's responsibility. When in doubt, ask!** 🔒
