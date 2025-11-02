# Pet Care Scheduler

**Trade Name:** Pet Care
**Project ID:** saas202512
**Status:** Planning Complete - Ready for Sprint 1
**Build Approach:** Complete Build (60-90 days)
**Architecture:** Multi-tenant SaaS (subdomain model)

A specialized scheduling platform for mobile groomers, solo trainers, and small pet care salons. Solving the critical pain points of double-booking chaos, no-show losses, and manual vaccination tracking.

---

## 🎯 Product Vision

**The Problem:**
Pet care professionals lose revenue to no-shows (8-15% industry average), struggle with double-booking, and waste time on manual vaccination tracking and phone confirmations.

**Our Solution:**
SMS-first scheduling platform with "impossible to double-book" safeguards, automated vaccination lifecycle management, and two-tap rescheduling workflows.

**Target Market:**
- **Primary:** Mobile groomers, solo trainers (wedge market)
- **Secondary:** Small salons (1-3 tables), boutiques with classes/packages

---

## ⭐ Key Differentiators

1. **"Impossible to Double-Book" Scheduling Engine**
   - Resource locking at database level
   - Buffer time enforcement (setup, cleanup, travel)
   - Real-time conflict detection
   - Multi-pet appointment handling

2. **SMS-First Workflows**
   - Two-way messaging inbox
   - Two-tap reschedule ("Reply 1 for tomorrow 2pm")
   - Late-running alerts
   - Automated confirmations & reminders (24hr + 2hr)

3. **Vaccination Lifecycle Management**
   - Upload vax cards (photo/PDF)
   - Auto-expiry tracking with reminders
   - Booking blocks for expired vaccinations
   - Staff override workflow with documentation

4. **No-Show Prevention**
   - Card-on-file requirement
   - Deposit system with cancellation policies
   - Automatic fee charging
   - Waitlist autofill on cancellations

5. **60-Minute Migration**
   - Guided onboarding wizard
   - CSV import from existing tools
   - Weekend migration support
   - 2-week parallel mode option

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** with Compose v2 (required)
- **Node.js** LTS (20.x+)
- **Python** 3.11+
- **Git** 2.x+

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/ChrisStephens1971/saas202512.git
cd saas202512

# 2. Read the developer guide
cat docs/DEVELOPER-GUIDE.md

# 3. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with your API keys (Twilio, Stripe)

# 4. Start services
docker compose up -d

# 5. Run database migrations
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
alembic upgrade head

# 6. Access the application
# Frontend: http://localhost:3012
# Backend API: http://localhost:8012
# API Docs: http://localhost:8012/docs
```

**Full setup instructions:** See `docs/DEVELOPER-GUIDE.md`

---

## 📁 Project Structure

```
saas202512/
├── docs/                    # Developer documentation
│   ├── DEVELOPER-GUIDE.md  # Setup, Docker, tooling, troubleshooting
│   ├── CONTRIBUTING.md     # Code style, commits, PRs
│   ├── TESTING-GUIDE.md    # Testing procedures, smoke tests
│   └── SECURITY.md         # Secrets management, multi-tenant security
│
├── product/                 # Product planning
│   ├── roadmap/
│   │   └── 2025-Q1-roadmap.md   # Complete build roadmap
│   └── PRDs/               # Product requirements (to be created)
│
├── sprints/                 # Sprint plans
│   └── current/
│       ├── sprint-01-foundation.md
│       ├── sprint-02-scheduling-engine.md
│       ├── sprint-03-booking-payments.md
│       ├── sprint-04-vaccination-no-show-defense.md
│       ├── sprint-05-sms-workflows.md
│       └── sprint-06-ops-tools-reports.md
│
├── business/                # Business planning
│   └── okrs/
│       └── 2025-Q1-okrs.md  # Build & beta validation OKRs
│
├── technical/               # Technical documentation
│   ├── multi-tenant-architecture.md
│   ├── adr-template.md     # For architectural decisions
│   └── infrastructure/     # Deployment guides
│
├── backend/                 # FastAPI backend (to be created)
├── frontend/                # Next.js frontend (to be created)
└── project-brief.md         # Full viability summary
```

---

## 🏗️ Build Timeline

**Approach:** Complete Build (ship all 6 MVP areas before beta)
**Duration:** 60-90 days (12 weeks)
**Target Launch:** March 28, 2025 (Week 12)
**Beta Goal:** 20 shops by March 31, 2025

### Sprint Breakdown

| Sprint | Duration | Focus Area | Key Deliverables |
|--------|----------|------------|------------------|
| **Sprint 1** | Weeks 1-2 | Foundation | Multi-tenant DB, core models, auth |
| **Sprint 2** | Weeks 3-4 | Scheduling Engine | Conflict detection, buffer management |
| **Sprint 3** | Weeks 5-6 | Booking & Payments | Widget, Stripe, SMS reminders |
| **Sprint 4** | Weeks 7-8 | Vaccination & No-Show | Vax tracking, cancellation policies |
| **Sprint 5** | Weeks 9-10 | SMS Workflows | Two-way inbox, quick actions |
| **Sprint 6** | Weeks 11-12 | Ops & Reports | Dashboard, photos, beta onboarding |

**Current Sprint:** Sprint 1 - Foundation (not yet started)

---

## 🎯 Q1 2025 Goals (OKRs)

### Objective 1: Ship Production-Ready MVP
- ✅ Complete all 6 sprint deliverables on schedule
- ✅ Zero critical bugs before beta launch
- ✅ 99.5%+ uptime in production

### Objective 2: Launch Successful Beta Program
- ✅ Enroll 20 beta shops by March 31
- ✅ 60% activation rate (12 active shops)
- ✅ <60 minute average migration time

### Objective 3: Validate Core Product Hypotheses
- ✅ Reduce no-shows by ≥30% vs. baseline
- ✅ 70%+ booking confirmation rate via SMS
- ✅ Zero double-bookings reported in beta

**Full OKRs:** See `business/okrs/2025-Q1-okrs.md`

---

## 💻 Tech Stack

### Frontend
- **Framework:** Next.js 14+ (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **State Management:** React Query

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Authentication:** JWT
- **API Docs:** OpenAPI/Swagger (auto-generated)

### Database & Storage
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7+
- **File Storage:** S3 / Azure Blob (tenant-prefixed)

### Integrations
- **SMS:** Twilio (with A2P/10DLC registration)
- **Payments:** Stripe (Connect for multi-tenant)
- **Email:** SendGrid (fallback to SMS)

### Infrastructure
- **Containerization:** Docker Compose v2
- **Hosting:** TBD (AWS/Azure/Heroku)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry (errors), UptimeRobot (uptime)
- **Secrets:** Azure Key Vault (production)

---

## 📊 Success Metrics

**Target Metrics (Post-Beta):**

| Metric | Target | Current |
|--------|--------|---------|
| No-show reduction | ≥30% | TBD |
| Booking completion | ≥70% | TBD |
| Utilization increase | +10-15% | TBD |
| Monthly churn | <2% | TBD |
| Payback period | <3 months | TBD |

**Unit Economics (Targets):**
- ARPU: $80-120/mo
- Gross margin: 80-85%
- CAC: $150-300
- LTV: ≈$2,400 (24 months at $99/mo)

---

## 🔒 Security & Compliance

**Multi-Tenant Security:**
- Row-level security (RLS) in PostgreSQL
- Tenant ID on all queries (no cross-tenant data access)
- Subdomain-based tenant resolution
- Tenant-prefixed file storage

**Secrets Management:**
- Development: `.env` files (never committed)
- Production: Azure Key Vault
- NO secrets in `parameters.*.json` files
- Managed Identity for Key Vault access

**Compliance:**
- **PCI DSS:** Stripe Elements (never handle raw card data)
- **A2P/10DLC:** SMS registration for reliable delivery
- **TCPA:** Opt-in required, STOP/START handling
- **Data Privacy:** Encryption at rest and in transit

**See:** `docs/SECURITY.md` for comprehensive guidelines

---

## 🧪 Testing

**Testing Strategy:**

| Type | Coverage Target | Run Frequency |
|------|----------------|---------------|
| **Unit Tests** | 90%+ | Every PR |
| **Integration Tests** | 85%+ | Every PR |
| **E2E Tests** | Critical paths | Pre-deployment |
| **Smoke Tests** | All services | Every commit |

**Smoke Test Commands:**
```bash
# Backend health
curl http://localhost:8012/health

# Docker services
docker compose ps

# Run test suite
pytest  # Backend
npm test  # Frontend

# Validate infrastructure
docker compose config
```

**See:** `docs/TESTING-GUIDE.md` for full testing procedures

---

## 📖 Documentation

### For Developers
- **Setup & Environment:** `docs/DEVELOPER-GUIDE.md`
- **Code Style & PRs:** `docs/CONTRIBUTING.md`
- **Testing Procedures:** `docs/TESTING-GUIDE.md`
- **Security Guidelines:** `docs/SECURITY.md`

### For Planning
- **Product Roadmap:** `product/roadmap/2025-Q1-roadmap.md`
- **Sprint Plans:** `sprints/current/sprint-*.md` (1-6)
- **OKRs:** `business/okrs/2025-Q1-okrs.md`
- **Project Brief:** `project-brief.md`

### For Architecture
- **Multi-Tenant Guide:** `technical/multi-tenant-architecture.md`
- **ADR Template:** `technical/adr-template.md`
- **Infrastructure:** `technical/infrastructure/`

---

## 🤝 Contributing

**Before submitting a PR:**

1. ✅ Read `docs/CONTRIBUTING.md` (file naming, code style)
2. ✅ Follow conventional commits format
3. ✅ Run smoke tests and full test suite
4. ✅ Update documentation if needed
5. ✅ No secrets in code or config files
6. ✅ Include screenshots for UI changes

**PR Checklist:** See `docs/TESTING-GUIDE.md`

---

## 🚦 Project Status

**Current Phase:** Planning Complete ✅
**Next Step:** Start Sprint 1 - Foundation
**Team:** Solo founder (Chris Stephens)

**Progress:**
- [x] Project brief created (from viability summary)
- [x] Q1 roadmap complete (all 6 MVP areas)
- [x] Sprint plans created (Sprint 1-6)
- [x] OKRs defined (build & beta validation)
- [x] Developer documentation complete
- [ ] Sprint 1: Not started (infrastructure setup)
- [ ] Sprint 2-6: Pending

---

## 🔗 Links

- **Repository:** https://github.com/ChrisStephens1971/saas202512
- **Viability Summary:** `project-brief.md`
- **Product Roadmap:** `product/roadmap/2025-Q1-roadmap.md`
- **OKRs:** `business/okrs/2025-Q1-okrs.md`

---

## 📞 Contact

**Project Owner:** Chris Stephens
**Email:** chris.stephens@verdaio.com
**Organization:** Verdaio

---

## ⚖️ License

This project is private and proprietary.

---

## 🎉 Acknowledgments

**Built with:**
- Template system by Verdaio
- Planning assistance by Claude Code (claude.ai/code)

**Inspired by:**
- Real pain points from pet care professionals
- SMS-first approach from modern consumer apps
- Best practices from Stripe, Twilio, and SaaS leaders

---

**Let's build something pet care professionals will love!** 🐾🚀
