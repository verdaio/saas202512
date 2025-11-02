# Sprint 1 - Foundation

**Sprint Duration:** Week 1-2 (January 6-17, 2025)
**Sprint Goal:** Establish multi-tenant architecture, core data models, and authentication system
**Status:** Planning

---

## Sprint Goal

Build the foundational infrastructure for Pet Care Scheduler including:
1. Multi-tenant PostgreSQL database schema with secure tenant isolation
2. Core data models (pets, owners, staff, services, resources, appointments, payments)
3. Authentication system with tenant context
4. Basic API structure with tenant-scoped endpoints
5. Development environment setup (frontend, backend, database)

This sprint sets the architectural foundation for all future features. Success means we have a secure, scalable multi-tenant system ready for the scheduling engine in Sprint 2.

---

## Sprint Capacity

**Available Days:** 10 working days (2 weeks)
**Capacity:** ~60-70 hours (solo founder, 6-7 hours/day)
**Commitments/Time Off:** None

**Prerequisites:** Before starting this sprint, review:
- `docs/Developer-Guide.md` - Environment setup and tooling requirements
- `docs/CONTRIBUTING.md` - File naming and code style guidelines
- `docs/SECURITY.md` - Secrets management and multi-tenant security

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-001 | Set up project infrastructure (frontend/backend/db) | M | Chris | 📋 Todo | Next.js + FastAPI + PostgreSQL |
| US-002 | Design multi-tenant database schema | L | Chris | 📋 Todo | All tables with tenant_id; subdomain model |
| US-003 | Implement core models: Tenant, User, Staff | M | Chris | 📋 Todo | SQLAlchemy models with relationships |
| US-004 | Implement core models: Pet, Owner | M | Chris | 📋 Todo | Pet profiles, owner contact info |
| US-005 | Implement core models: Service, Resource | M | Chris | 📋 Todo | Services (grooming/training), Resources (tables/vans) |
| US-006 | Implement core models: Appointment, Payment | M | Chris | 📋 Todo | Appointment entity, payment records |
| US-007 | Build authentication system with tenant context | L | Chris | 📋 Todo | JWT tokens with tenant_id claim |
| US-008 | Create tenant onboarding flow | M | Chris | 📋 Todo | Business signup, subdomain assignment |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-009 | Build tenant-scoped API middleware | M | Chris | 📋 Todo | Auto-inject tenant filter on all queries |
| US-010 | Create database migration system | S | Chris | 📋 Todo | Alembic for schema versioning |
| US-011 | Set up Docker dev environment | M | Chris | 📋 Todo | docker-compose for local dev |
| US-012 | Implement basic CRUD APIs for core models | M | Chris | 📋 Todo | RESTful endpoints with tenant scoping |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-013 | Create admin dashboard shell | S | Chris | 📋 Todo | Basic layout, routing setup |
| US-014 | Set up logging and monitoring | S | Chris | 📋 Todo | Structured logging, error tracking |
| US-015 | Write API documentation (OpenAPI/Swagger) | XS | Chris | 📋 Todo | Auto-generated from code |

**Story Size Legend:**
- **XS:** <2 hours
- **S:** 2-4 hours
- **M:** 4-8 hours
- **L:** 8-16 hours

**Story Status Legend:**
- 📋 Todo
- 🏗️ In Progress
- 👀 In Review
- ✅ Done
- ❌ Blocked

---

## Technical Debt / Maintenance

Items to address during sprint:

- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure pre-commit hooks (linting, formatting)
- [ ] Set up test framework (pytest for backend, Jest for frontend)
- [ ] Create initial test coverage for models
- [ ] Document database schema design decisions

---

## Detailed Story Breakdown

### US-001: Set up project infrastructure

**Acceptance Criteria:**
- ✅ Frontend: Next.js 14+ with TypeScript, Tailwind CSS
- ✅ Backend: FastAPI with Python 3.11+
- ✅ Database: PostgreSQL 15+
- ✅ Local dev environment running on configured ports (3012, 8012, 5412)
- ✅ Hot reload working for both frontend and backend
- ✅ Environment variables configured (.env files)

**Technical Notes:**
- Frontend port: 3012
- Backend port: 8012
- PostgreSQL port: 5412
- Redis port: 6412 (for future sessions)
- MongoDB port: 27012 (reserved, not used initially)

---

### US-002: Design multi-tenant database schema

**Acceptance Criteria:**
- ✅ All tables include `tenant_id` column (except system tables)
- ✅ Indexes on `tenant_id` for query performance
- ✅ Foreign key constraints properly defined
- ✅ Schema documented in `technical/architecture/database-schema.md`
- ✅ Migration scripts created and tested

**Key Tables:**
1. **tenants** - Business accounts (subdomain, name, plan, status, settings)
2. **users** - User accounts (email, password_hash, role, tenant_id)
3. **staff** - Staff members (name, role, skills, availability, tenant_id)
4. **pets** - Pet profiles (name, breed, age, medical_notes, owner_id, tenant_id)
5. **owners** - Pet owners (name, email, phone, address, tenant_id)
6. **services** - Service types (name, duration, buffer_before, buffer_after, price, tenant_id)
7. **resources** - Bookable resources (name, type [table/van/room], tenant_id)
8. **appointments** - Booking records (pet_id, service_id, staff_id, resource_id, start_time, status, tenant_id)
9. **payments** - Payment records (appointment_id, amount, type, status, stripe_payment_id, tenant_id)
10. **packages** - Punch cards/credits (name, credits, price, expiry_days, tenant_id)
11. **vaccination_records** - Vax tracking (pet_id, vax_type, date, expiry_date, file_url, tenant_id)

**Multi-Tenant Isolation:**
- Row-level security policies (RLS) in PostgreSQL
- Application-level tenant filtering on all queries
- Subdomain-to-tenant_id mapping table

---

### US-003: Implement core models - Tenant, User, Staff

**Acceptance Criteria:**
- ✅ SQLAlchemy models with proper relationships
- ✅ Pydantic schemas for validation
- ✅ Unit tests for model creation and validation
- ✅ Database migrations created

**Tenant Model Fields:**
- id (UUID, primary key)
- subdomain (unique, indexed)
- business_name
- plan (starter/standard/pro)
- status (trial/active/suspended/cancelled)
- settings (JSONB - for tenant-specific config)
- created_at, updated_at

**User Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- email (unique per tenant)
- password_hash
- role (owner/staff/admin)
- is_active
- created_at, updated_at

**Staff Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- user_id (foreign key, nullable - staff may not have login)
- name
- email, phone
- role (groomer/trainer/both)
- skills (JSONB - array of service types)
- is_active
- created_at, updated_at

---

### US-004: Implement core models - Pet, Owner

**Acceptance Criteria:**
- ✅ SQLAlchemy models with relationships to tenants
- ✅ Pydantic schemas for validation
- ✅ Unit tests
- ✅ Database migrations

**Pet Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- owner_id (foreign key)
- name
- breed
- age (or date_of_birth)
- weight
- medical_notes (text)
- behavioral_notes (text)
- is_active
- created_at, updated_at

**Owner Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- name
- email
- phone (primary contact)
- phone_alt (alternative)
- address (JSONB - street, city, state, zip)
- notes (text)
- stripe_customer_id (for payments)
- is_active
- created_at, updated_at

**Relationships:**
- Owner has many Pets (one-to-many)
- Pet belongs to one Owner

---

### US-005: Implement core models - Service, Resource

**Acceptance Criteria:**
- ✅ SQLAlchemy models
- ✅ Pydantic schemas
- ✅ Unit tests
- ✅ Migrations

**Service Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- name (e.g., "Full Groom", "Basic Obedience")
- description
- duration_minutes
- buffer_before_minutes (setup time)
- buffer_after_minutes (cleanup time)
- price
- requires_vaccination (boolean)
- is_active
- created_at, updated_at

**Resource Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- name (e.g., "Table 1", "Van 2", "Training Room A")
- type (table/van/room)
- is_mobile (boolean - for vans)
- is_active
- created_at, updated_at

---

### US-006: Implement core models - Appointment, Payment

**Acceptance Criteria:**
- ✅ Complex models with multiple relationships
- ✅ Status enums defined
- ✅ Validation logic for booking rules
- ✅ Unit tests
- ✅ Migrations

**Appointment Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- pet_id (foreign key)
- owner_id (foreign key - denormalized for queries)
- service_id (foreign key)
- staff_id (foreign key)
- resource_id (foreign key, nullable)
- scheduled_start (timestamp with timezone)
- scheduled_end (computed from start + service.duration)
- actual_start (nullable timestamp)
- actual_end (nullable timestamp)
- status (scheduled/confirmed/in_progress/completed/cancelled/no_show)
- cancellation_reason (text, nullable)
- notes (text)
- created_at, updated_at

**Payment Model Fields:**
- id (UUID, primary key)
- tenant_id (foreign key, indexed)
- appointment_id (foreign key, nullable - for package purchases)
- owner_id (foreign key)
- amount_cents (integer - store in cents)
- type (deposit/full_payment/tip/package/gift_card)
- status (pending/completed/failed/refunded)
- stripe_payment_intent_id
- stripe_charge_id
- metadata (JSONB - for additional context)
- created_at, updated_at

---

### US-007: Build authentication system with tenant context

**Acceptance Criteria:**
- ✅ User registration with tenant assignment
- ✅ Login endpoint returns JWT with tenant_id claim
- ✅ Token validation middleware
- ✅ Password hashing (bcrypt)
- ✅ Tenant extracted from subdomain on each request
- ✅ Authentication tests

**Endpoints:**
- POST /auth/register - Create new user account
- POST /auth/login - Authenticate and get JWT
- POST /auth/logout - Invalidate token (if using refresh tokens)
- GET /auth/me - Get current user info

**JWT Claims:**
- user_id
- tenant_id
- email
- role
- exp (expiration)

**Security:**
- Passwords hashed with bcrypt (12 rounds)
- JWT secret from environment variable
- Token expiration: 24 hours (access token)
- HTTPS-only cookies in production

---

### US-008: Create tenant onboarding flow

**Acceptance Criteria:**
- ✅ Tenant registration form (business name, subdomain, owner info)
- ✅ Subdomain availability check
- ✅ Create tenant + owner user in single transaction
- ✅ Send welcome email (placeholder for now)
- ✅ Redirect to tenant dashboard
- ✅ Validation and error handling

**Onboarding Steps:**
1. Choose subdomain (e.g., "happypaws" → happypaws.petcare.localhost)
2. Enter business details (name, phone, address)
3. Create owner account (email, password)
4. Set initial preferences (timezone, service types)
5. Assign default ports (or use shared ports based on tenant_id)

**Validation:**
- Subdomain: 3-30 chars, alphanumeric + hyphens, lowercase
- Subdomain uniqueness check
- Email format and uniqueness
- Password strength (8+ chars, mixed case, number)

---

### US-009: Build tenant-scoped API middleware

**Acceptance Criteria:**
- ✅ Middleware extracts subdomain from request
- ✅ Looks up tenant_id from subdomain
- ✅ Injects tenant_id into request context
- ✅ All database queries automatically filtered by tenant_id
- ✅ Returns 404 if invalid subdomain
- ✅ Returns 403 if user tenant doesn't match request tenant

**Implementation:**
- FastAPI dependency injection for tenant resolution
- SQLAlchemy session with tenant filter
- Request scoped tenant context
- Security: verify JWT tenant_id matches subdomain tenant_id

---

### US-012: Implement basic CRUD APIs for core models

**Acceptance Criteria:**
- ✅ RESTful endpoints for Pets, Owners, Staff, Services, Resources
- ✅ All endpoints tenant-scoped
- ✅ Validation using Pydantic
- ✅ Error handling (400, 404, 403, 500)
- ✅ OpenAPI documentation auto-generated

**Endpoints per model (example for Pets):**
- GET /pets - List all pets (paginated, filtered by tenant)
- POST /pets - Create new pet
- GET /pets/{id} - Get pet details
- PUT /pets/{id} - Update pet
- DELETE /pets/{id} - Soft delete pet

**Common patterns:**
- Pagination: ?page=1&limit=20
- Filtering: ?owner_id=xxx&is_active=true
- Sorting: ?sort_by=name&order=asc
- Tenant scoping enforced on all queries

---

## Daily Progress

*(To be filled in during sprint execution)*

### Day 1 - Monday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 2 - Tuesday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 3 - Wednesday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 4 - Thursday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 5 - Friday
**What I worked on:**
-

**Blockers:**
-

**Plan for next week:**
-

---

### Day 6 - Monday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 7 - Tuesday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 8 - Wednesday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 9 - Thursday
**What I worked on:**
-

**Blockers:**
-

**Plan for tomorrow:**
-

---

### Day 10 - Friday
**What I worked on:**
-

**Blockers:**
-

**Plan for next sprint:**
-

---

## Scope Changes

Document any stories added or removed during the sprint:

| Date | Change | Reason |
|------|--------|--------|
| - | - | - |

---

## Sprint Metrics

### Planned vs Actual
- **Planned:** 8 high-priority stories + 4 medium-priority stories
- **Completed:** (TBD at sprint end)
- **Completion Rate:** (TBD)%

### Velocity
- **Previous Sprint:** N/A (first sprint)
- **This Sprint:** (TBD) points
- **Trend:** Baseline

---

## Wins & Learnings

*(To be completed at end of sprint)*

### What Went Well
-

### What Could Be Improved
-

### Action Items for Next Sprint
- [ ]

---

## Sprint Review Notes

*(To be completed at end of sprint)*

**What We Shipped:**
-

**Demo Notes:**
-

**Feedback Received:**
-

---

## Links & References

**Sprint Planning:**
- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Related PRD: (To be created during sprint)
- GitHub milestone: (To be created)

**Technical Documentation:**
- Database Schema Doc: `technical/architecture/database-schema.md` (to be created)
- Multi-Tenant Architecture Guide: `technical/multi-tenant-architecture.md`
- ADR Template: `technical/adr-template.md` (create ADRs for major architectural decisions)

**Developer Resources:**
- Developer Guide: `docs/Developer-Guide.md` - Setup, Docker, tooling
- Contributing Guide: `docs/CONTRIBUTING.md` - Style, commits, PRs
- Security Guidelines: `docs/SECURITY.md` - Secrets management, multi-tenant security
- Testing Guide: `docs/TESTING-GUIDE.md` - Unit tests, smoke tests, coverage

---

## Sprint Success Criteria

Sprint 1 is successful if:
- ✅ All core models implemented and tested
- ✅ Multi-tenant architecture working (verified with 2+ test tenants)
- ✅ Authentication system functional
- ✅ Basic CRUD APIs operational
- ✅ Database migrations clean and reversible
- ✅ Local dev environment stable
- ✅ No cross-tenant data leaks (security validated)
- ✅ Documentation complete for database schema
- ✅ Ready to start Sprint 2 (Scheduling Engine)
