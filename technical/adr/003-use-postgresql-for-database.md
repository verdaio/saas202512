# ADR-003: Use PostgreSQL for Primary Database

**Date:** 2025-11-02
**Status:** Accepted
**Deciders:** Chris Stephens
**Technical Story:** Core MVP requirement - Multi-tenant data isolation with relational data model

---

## Context

Pet Care Scheduler requires a database that supports:

- **Multi-tenant isolation:** Strict data separation between pet care businesses (subdomain-based tenants)
- **Relational data:** Complex relationships between pets, owners, appointments, services, staff, vaccinations
- **Row-level security:** Prevent cross-tenant data access at database level (critical for compliance and trust)
- **ACID compliance:** Financial transactions (deposits, payments, refunds) require transactional integrity
- **Rich query capabilities:** Complex scheduling queries with date/time filtering, resource availability, conflict detection
- **JSON support:** Store flexible metadata (service details, payment metadata, SMS conversation context)
- **Full-text search:** Search pets, owners, appointments across tenant data
- **Scalability:** Support 100+ tenants with 50-200 appointments/week each

Key constraints:
- Solo founder building in 60-90 days (need familiar, well-documented database)
- Multi-tenant architecture with tenant_id on all tables
- Financial data requires audit trails and rollback capability
- Docker Compose for local development
- Cloud deployment readiness (AWS RDS, Azure PostgreSQL, or Heroku Postgres)

---

## Decision

We will use **PostgreSQL 15+** as our primary database with:
- **SQLAlchemy 2.0** ORM for Python/FastAPI backend
- **Alembic** for database migrations
- **Row-level security (RLS)** policies to enforce tenant isolation
- **Tenant ID column** on all non-system tables
- **JSONB columns** for flexible metadata storage
- **Full-text search** using PostgreSQL's built-in tsvector/tsquery
- **Indexes** on tenant_id, scheduled_start (appointments), and common query paths

---

## Consequences

### Positive Consequences
- **Battle-tested reliability:** PostgreSQL has 30+ years of proven stability in production
- **Strong ACID guarantees:** Perfect for financial transactions (deposits, payments, refunds)
- **Row-level security (RLS):** Native support for multi-tenant data isolation at database level (reduces risk of tenant data leaks)
- **Rich data types:** JSONB, arrays, date/time types, UUID native support
- **Excellent ecosystem:** SQLAlchemy ORM, Alembic migrations, pgAdmin for debugging
- **Full-text search:** Built-in search without additional dependencies (Elasticsearch not needed for MVP)
- **Developer familiarity:** PostgreSQL is widely known, extensive documentation and community support
- **Free and open-source:** No licensing costs (unlike Oracle, SQL Server)
- **Cloud-ready:** Managed offerings from AWS (RDS), Azure (PostgreSQL), Heroku, DigitalOcean
- **Performance:** Handles 10,000+ queries/second for our use case (far exceeds beta needs)

### Negative Consequences
- **Vertical scaling limits:** Single-server architecture limits to ~100-500 tenants before needing read replicas or sharding
- **Backup complexity:** Need to configure automated backups and point-in-time recovery (PITR)
- **Connection pooling required:** PostgreSQL doesn't handle thousands of concurrent connections (need PgBouncer or similar)
- **Schema changes require downtime:** Alembic migrations can lock tables during schema updates (need blue-green deployment for zero-downtime)

### Neutral Consequences
- Requires PostgreSQL-specific knowledge (but most developers already have this)
- Docker container for local dev, managed service for production
- Need to monitor slow queries and optimize indexes as data grows

---

## Alternatives Considered

### Alternative 1: MongoDB
**Description:** NoSQL document database with flexible schema

**Pros:**
- Schemaless design (easier to iterate on data model during early development)
- Built-in sharding for horizontal scaling
- JSONB-style document storage is native (no ORM mapping needed)
- Fast writes for high-volume data

**Cons:**
- No native multi-tenant row-level security (would need application-level enforcement only)
- Weaker ACID guarantees (especially across collections)
- Less suitable for relational data (appointments ↔ pets ↔ owners ↔ services requires manual joins)
- No built-in full-text search (need Atlas Search or Elasticsearch)
- Less familiar to most backend developers (steeper learning curve)
- Financial data best practices favor relational databases

**Why rejected:** Multi-tenant security is critical. PostgreSQL's RLS provides database-level enforcement, while MongoDB requires application-level checks (higher risk of bugs exposing cross-tenant data).

---

### Alternative 2: MySQL
**Description:** Popular open-source relational database

**Pros:**
- Very similar to PostgreSQL (relational model, ACID, SQL)
- Widely deployed (proven at scale)
- Good developer familiarity
- Cloud-managed options (AWS RDS, Azure MySQL)

**Cons:**
- Weaker JSON support compared to PostgreSQL's JSONB
- No native row-level security (RLS) - must implement in application code
- Less advanced full-text search capabilities
- Historically weaker at complex queries and transactions
- Licensing concerns (Oracle ownership, though MySQL is still open-source)

**Why rejected:** PostgreSQL's JSONB performance and native RLS support are significant advantages for our multi-tenant use case. The feature gap outweighs MySQL's marginal adoption advantage.

---

### Alternative 3: SQLite
**Description:** Embedded file-based database

**Pros:**
- Zero configuration (no server setup)
- Perfect for local development
- Extremely lightweight
- ACID compliant

**Cons:**
- Not designed for concurrent writes (single-writer locks entire database)
- No built-in row-level security or multi-tenant features
- Limited scalability (single-file architecture)
- Not suitable for production multi-tenant SaaS

**Why rejected:** While excellent for prototypes, SQLite cannot support production multi-tenant workloads with concurrent users. We'd need to migrate to PostgreSQL/MySQL eventually, creating migration work.

---

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/15/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Alembic Migrations: https://alembic.sqlalchemy.org/
- Row-Level Security (RLS): https://www.postgresql.org/docs/15/ddl-rowsecurity.html
- Multi-tenant architecture: `technical/multi-tenant-architecture.md`
- Security guidelines: `docs/SECURITY.md`
- Sprint 1 plan: `sprints/current/sprint-01-foundation.md`

---

## Notes

**Implementation details:**

**Row-Level Security (RLS) example:**
```sql
-- Enable RLS on appointments table
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Create policy: Users can only see their tenant's data
CREATE POLICY tenant_isolation ON appointments
  FOR ALL
  TO app_user
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**SQLAlchemy ORM pattern:**
```python
# Always include tenant_id in queries
@tenant_scoped
def get_appointments(tenant_id: UUID, date: date):
    return db.query(Appointment).filter(
        Appointment.tenant_id == tenant_id,
        Appointment.scheduled_start >= date
    ).all()
```

**Database schema conventions:**
- All tables include: `id` (UUID primary key), `tenant_id` (UUID foreign key), `created_at`, `updated_at`
- Use soft deletes: `deleted_at` instead of hard DELETE operations
- Financial tables include `metadata JSONB` for Stripe references and audit trails

**Performance considerations:**
- Create composite indexes: `(tenant_id, scheduled_start)` for common queries
- Use connection pooling (SQLAlchemy pool_size=10, max_overflow=20)
- Monitor query performance with `EXPLAIN ANALYZE`
- Add read replicas when we hit 50+ tenants

**Backup strategy:**
- Daily automated backups with 30-day retention
- Point-in-time recovery (PITR) for production
- Test restore process monthly

**Local development:**
- Docker Compose for PostgreSQL 15 container
- Alembic migrations in `backend/alembic/` directory
- Seed data script for development/testing

**Cloud deployment options (to be decided):**
- **AWS RDS:** Most features, highest cost
- **Azure Database for PostgreSQL:** Good Azure integration
- **Heroku Postgres:** Easiest setup, good for beta
- **DigitalOcean Managed PostgreSQL:** Best price/performance for small scale

---

## Superseded By

[None]
