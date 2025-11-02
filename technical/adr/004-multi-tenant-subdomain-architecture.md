# ADR-004: Multi-Tenant Subdomain Architecture

**Date:** 2025-11-02
**Status:** Accepted
**Deciders:** Chris Stephens
**Technical Story:** Core architectural decision - How tenants are isolated and accessed

---

## Context

Pet Care Scheduler is a multi-tenant SaaS platform where each pet care business (groomer, trainer, salon) is a separate tenant with:

- **Complete data isolation:** Bella's grooming records at Happy Paws should never be visible to Pampered Paws
- **Unique branding:** Each business needs their own subdomain (happypaws.petcare.app)
- **Separate merchant accounts:** Each business receives their own payments (Stripe Connect)
- **Independent SMS numbers:** Each business has their own Twilio phone number
- **Shared infrastructure:** All tenants use the same application code and database (cost efficiency)

Key requirements:
- **Beta launch:** 20 shops need easy signup and onboarding
- **60-minute migration:** Subdomain must be set up instantly during signup
- **Security:** Zero risk of cross-tenant data leaks (critical for trust)
- **Scalability:** Support 100+ tenants within 6 months
- **Simple architecture:** Solo founder needs maintainable codebase

Three common multi-tenant patterns exist:
1. **Subdomain-based:** happypaws.petcare.app (unique subdomain per tenant)
2. **Path-based:** petcare.app/happypaws (tenant in URL path)
3. **Separate databases:** Each tenant has their own database instance

---

## Decision

We will use **subdomain-based multi-tenancy** where:
- Each tenant gets a unique subdomain: `{subdomain}.petcare.app`
- Subdomain is chosen during signup (e.g., "happypaws")
- Tenant ID is resolved from subdomain on every request
- All tenants share a single PostgreSQL database with `tenant_id` column on all tables
- Row-level security (RLS) enforces tenant isolation at database level

**Example:**
- Happy Paws Grooming → `happypaws.petcare.app`
- Pampered Paws Salon → `pamperedpaws.petcare.app`
- Mobile Groomers LLC → `mobilegroomers.petcare.app`

---

## Consequences

### Positive Consequences
- **Clear tenant separation:** Subdomain makes it obvious which business you're accessing
- **Professional branding:** Each business gets their own "branded" URL (better than petcare.app/happypaws)
- **Easier SSL setup:** Wildcard SSL certificate (*.petcare.app) covers all tenant subdomains
- **Simple tenant resolution:** Middleware extracts subdomain from `Host` header to identify tenant
- **Better analytics:** Track usage per subdomain easily (Google Analytics, Mixpanel)
- **Lower infrastructure costs:** Shared database and application server (vs. separate DBs per tenant)
- **Fast onboarding:** New tenant = create subdomain DNS record (instant, automated via API)

### Negative Consequences
- **Subdomain conflicts:** First-come-first-served for popular names (e.g., "best", "premium")
- **DNS dependency:** Requires wildcard DNS (*.petcare.app → app server IP)
- **CORS complexity:** Cross-subdomain requests require explicit CORS configuration
- **Mobile app challenges:** Subdomains complicate mobile app login flow (need tenant picker)
- **Testing complexity:** Need to mock subdomain in tests (e.g., test.localhost)

### Neutral Consequences
- Requires subdomain validation during signup (alphanumeric, 3-30 chars, unique check)
- Need to reserve system subdomains (www, api, admin, docs, etc.)
- Subdomain changes are complex (affects all URLs, would require redirect strategy)

---

## Alternatives Considered

### Alternative 1: Path-Based Multi-Tenancy
**Description:** Tenant identified by URL path: `petcare.app/{tenant-slug}/dashboard`

**Example:**
- `petcare.app/happypaws/appointments`
- `petcare.app/pamperedpaws/appointments`

**Pros:**
- Simpler DNS setup (single domain, no wildcard needed)
- Easier to manage SSL (single certificate)
- Better for mobile apps (single domain login)
- No subdomain conflicts

**Cons:**
- Less professional (looks like multi-tenant platform, not dedicated app)
- More complex routing (need to extract tenant from every URL)
- Harder to separate marketing site (`petcare.app`) from app (`petcare.app/happypaws`)
- Public booking widget URL is longer: `petcare.app/happypaws/book` vs. `happypaws.petcare.app/book`
- Confusing for owners: "Go to petcare.app/happypaws, not petcare.app/pamperedpaws"

**Why rejected:** Subdomain approach feels more professional and avoids owner confusion ("Just go to happypaws.petcare.app"). Path-based would expose our multi-tenant platform nature too obviously.

---

### Alternative 2: Separate Databases Per Tenant
**Description:** Each tenant gets their own PostgreSQL database instance

**Example:**
- `happypaws` tenant → `happypaws_db` database
- `pamperedpaws` tenant → `pamperedpaws_db` database

**Pros:**
- **Strongest isolation:** Database-level separation eliminates risk of tenant data leaks
- **Easier compliance:** HIPAA/SOC2 simpler with physical data separation
- **Tenant-specific performance:** One slow tenant doesn't affect others
- **Custom schemas:** Each tenant could have custom fields/tables
- **Easier to export/migrate:** Single tenant migration = database dump

**Cons:**
- **Much higher infrastructure cost:** 100 tenants = 100 database instances ($5/each = $500/month minimum)
- **Complex migrations:** Alembic migrations must run on ALL tenant databases (100 DBs × 30 seconds = 50 minutes)
- **Backup complexity:** Need to backup 100+ databases individually
- **Resource waste:** Small tenants (10 appointments/week) don't need dedicated database
- **Development complexity:** Local dev requires managing multiple databases
- **Performance overhead:** Connection pooling across 100 databases is harder

**Why rejected:** Cost and complexity far exceed our needs. For beta (20 tenants) and initial scale (100 tenants), shared database with RLS provides sufficient isolation at much lower cost.

---

### Alternative 3: Custom Domain Per Tenant
**Description:** Each tenant uses their own domain: `www.happypawsgrooming.com`

**Pros:**
- Ultimate branding (business owns their domain)
- No "petcare.app" branding visible
- Best for white-label scenarios

**Cons:**
- Massive onboarding friction: Customers must own domain, configure DNS, wait for propagation
- SSL certificate management nightmare (need to provision cert per tenant)
- Breaks 60-minute migration promise (DNS changes take hours to propagate)
- Complicates development and testing
- Not suitable for beta launch (too much setup required)

**Why rejected:** This is a future "enterprise" feature, not suitable for MVP or beta launch. Subdomain approach achieves 90% of the branding benefit with 10% of the complexity.

---

## References

- Multi-tenant architecture guide: `technical/multi-tenant-architecture.md`
- Security guidelines: `docs/SECURITY.md` (row-level security, tenant isolation)
- Sprint 1 plan: `sprints/current/sprint-01-foundation.md` (tenant schema implementation)
- Tenant resolution middleware: (to be implemented in Sprint 1)

---

## Notes

**Implementation details:**

**Subdomain validation rules:**
```python
# During tenant signup
def validate_subdomain(subdomain: str) -> bool:
    # 3-30 characters, alphanumeric + hyphens only
    # Must start with letter, cannot end with hyphen
    # Reserved words: www, api, admin, docs, app, blog, support, help

    if not re.match(r'^[a-z][a-z0-9-]{1,28}[a-z0-9]$', subdomain):
        raise ValueError("Invalid subdomain format")

    if subdomain in RESERVED_SUBDOMAINS:
        raise ValueError("Subdomain is reserved")

    if Tenant.query.filter_by(subdomain=subdomain).exists():
        raise ValueError("Subdomain already taken")

    return True
```

**Tenant resolution middleware (FastAPI):**
```python
@app.middleware("http")
async def tenant_resolver(request: Request, call_next):
    # Extract subdomain from Host header
    host = request.headers.get("host", "")
    subdomain = host.split(".")[0]

    # Lookup tenant by subdomain
    tenant = get_tenant_by_subdomain(subdomain)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Attach tenant to request context
    request.state.tenant_id = tenant.id

    response = await call_next(request)
    return response
```

**Database schema:**
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    subdomain VARCHAR(30) UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- trial, active, suspended
    created_at TIMESTAMP NOT NULL
);

-- All other tables include tenant_id
CREATE TABLE appointments (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    pet_id UUID NOT NULL,
    scheduled_start TIMESTAMP NOT NULL,
    ...
    -- Composite index for common queries
    INDEX idx_tenant_date (tenant_id, scheduled_start)
);
```

**Reserved subdomains:**
```
www, api, app, admin, docs, blog, help, support, status,
staging, dev, test, demo, mail, email, ftp, cdn, static,
assets, files, images, uploads, downloads, webhooks
```

**DNS configuration:**
- Wildcard A record: `*.petcare.app → 12.34.56.78` (app server IP)
- Wildcard SSL: Let's Encrypt wildcard cert for `*.petcare.app`
- TTL: 300 seconds (5 minutes) for fast changes during development

**Public booking widget URL:**
- Format: `https://{subdomain}.petcare.app/book`
- Example: `https://happypaws.petcare.app/book`
- This URL is shared with pet owners for self-service booking

**Development setup:**
- Use `test.localhost:3012` for testing (browsers treat .localhost as subdomain)
- Or configure `/etc/hosts` with local subdomain entries
- Mock subdomain in tests: `client = TestClient(app, base_url="http://happypaws.localhost")`

**Migration from path-based (if needed in future):**
- Set up HTTP 301 redirects: `petcare.app/happypaws → happypaws.petcare.app`
- Support both URLs during transition period (3-6 months)
- Eventually deprecate path-based URLs

---

## Superseded By

[None]
