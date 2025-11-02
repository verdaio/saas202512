# Product Roadmap - Q1 2025

**Period:** Q1 2025 (January - March 2025)
**Owner:** Chris Stephens
**Last Updated:** 2025-11-02
**Status:** Approved
**Build Approach:** Complete Build (60-90 days)

---

## Vision & Strategy

### Product Vision

Pet Care is a specialized scheduling platform for mobile groomers, solo trainers, and small pet care salons. We solve the critical pain points of double-booking chaos, no-show losses, and manual vaccination tracking that plague the fragmented pet care SMB market.

Our vision is to become the **de facto scheduling standard** for pet care professionals by delivering what incumbents miss: SMS-first workflows, impossible-to-double-book safeguards, and integrated vaccination lifecycle management. We're building tight, selling narrow to our wedge market (mobile groomers and solo trainers), and will expand from there.

### Strategic Themes for Q1 2025

1. **Double-Booking Prevention** - Build the industry's most reliable scheduling engine with strict resource constraints and buffer management
2. **SMS-First Operations** - Make SMS the primary communication channel with two-way messaging, confirmations, and two-tap rescheduling
3. **Vaccination Lifecycle** - Bake in vaccination tracking with expiry alerts, upload workflows, and booking blocks/overrides
4. **Complete Build for Launch** - Ship all 6 MVP areas in 60-90 days; no partial releases, full feature set at beta

---

## Roadmap Overview

### Now (Weeks 1-4: January 2025)

**Focus:** Foundation & Core Scheduling Engine

| Feature/Initiative | Status | Sprint | Target Date | Priority |
|--------------------|--------|--------|-------------|----------|
| Multi-tenant database schema & models | Not Started | Sprint 1 | Week 2 | P0 |
| Core entities (pets, owners, staff, services, resources) | Not Started | Sprint 1 | Week 2 | P0 |
| Calendar engine with buffers & resource constraints | Not Started | Sprint 2 | Week 4 | P0 |
| Double-booking prevention logic | Not Started | Sprint 2 | Week 4 | P0 |
| Multi-pet booking flow | Not Started | Sprint 2 | Week 4 | P1 |

### Next (Weeks 5-8: February 2025)

**Focus:** Booking Flows, Payments & Vaccination System

| Feature/Initiative | Description | Strategic Theme | Target Date | Priority |
|--------------------|-------------|-----------------|-------------|----------|
| Mobile booking widget | Owner-facing booking interface | SMS-First | Week 6 | P0 |
| Deposit & payment processing | Stripe integration for deposits/tips/packages | Complete Build | Week 6 | P0 |
| SMS reminder system | Automated booking confirmations & reminders | SMS-First | Week 6 | P0 |
| Pet profile & vax tracking | Upload vax cards, expiry tracking | Vaccination Lifecycle | Week 8 | P0 |
| Vaccination blocks/overrides | Prevent booking if vax expired | Vaccination Lifecycle | Week 8 | P0 |
| No-show defense: card-on-file | Require card for booking | Complete Build | Week 8 | P1 |

### Later (Weeks 9-12: March 2025)

**Focus:** SMS Workflows, Ops Tools & Launch Readiness

| Feature/Initiative | Description | Strategic Theme | Estimated Week | Priority |
|--------------------|-------------|-----------------|----------------|----------|
| Two-way SMS inbox | Inbound SMS handling with templates | SMS-First | Week 10 | P0 |
| SMS quick actions | Two-tap reschedule, late-running alerts | SMS-First | Week 10 | P0 |
| Ops day view | Schedule by table/van/trainer | Complete Build | Week 11 | P0 |
| Before/after photos | Photo upload for completed appointments | Complete Build | Week 11 | P1 |
| Basic reporting | Revenue, no-shows, utilization | Complete Build | Week 12 | P0 |
| Beta onboarding flow | 20-shop beta program setup | Complete Build | Week 12 | P0 |

### Future/Backlog (Post-Launch: Q2 2025+)

Ideas and initiatives for post-beta expansion:
- Multi-location support for Pro tier customers
- Route optimization for mobile van businesses
- Class roster management for trainers (packages/credits, waitlists)
- Gift card system
- Advanced reporting & analytics dashboard
- Branded custom domains for businesses
- Calendar import from Calendly/Square/Google Calendar
- White-label options for franchise businesses

---

## Detailed Feature Breakdown

### 1. Multi-Tenant Architecture & Core Models

**Problem:** Need secure tenant isolation for each pet care business with proper data separation
**Solution:** PostgreSQL schema with `tenant_id` on all tables, subdomain routing, tenant-scoped queries
**Impact:** Foundation for SaaS model; enables secure multi-customer deployment
**Effort:** Medium
**Dependencies:** None (foundational)
**Status:** Not Started
**Sprint:** Sprint 1 (Weeks 1-2)
**PRD:** [To be created in Sprint 1]

**Key Entities:**
- Pets (name, breed, age, medical notes, vaccination records)
- Owners (contact info, family accounts, payment methods)
- Staff (groomers/trainers, availability, skills)
- Services (type, duration, buffer times, price)
- Resources (tables, vans, rooms)
- Packages (punch cards, class credits)
- Appointments (scheduling records)
- Payments (transactions, deposits, tips)

---

### 2. Calendar Scheduling Engine

**Problem:** Existing tools allow double-bookings, don't handle buffers properly, and can't manage complex resource constraints
**Solution:** Custom scheduling engine with strict resource locking, configurable buffers per service/staff/pet, channel guardrails
**Impact:** Core differentiator - "impossible to double-book" safeguards
**Effort:** Large
**Dependencies:** Core models must be complete
**Status:** Not Started
**Sprint:** Sprint 2 (Weeks 3-4)
**PRD:** [To be created]

**Features:**
- Resource availability checking (staff, tables, vans)
- Buffer time management (setup, cleanup, travel between appointments)
- Multi-pet appointment handling
- Conflict detection and prevention
- Channel-based guardrails (online vs manual booking)

---

### 3. Mobile Booking Widget

**Problem:** Pet owners need easy mobile-first way to book appointments without phone calls
**Solution:** Responsive booking widget with availability display, multi-pet selection, deposit payment
**Impact:** Reduces admin overhead for businesses; improves booking conversion
**Effort:** Medium
**Dependencies:** Scheduling engine, payment processing
**Status:** Not Started
**Sprint:** Sprint 3 (Weeks 5-6)
**PRD:** [To be created]

**Features:**
- Real-time availability display
- Family account support (multiple pets)
- Service selection with duration/price
- Staff preference (or auto-assign)
- Deposit payment at booking
- SMS confirmation on completion

---

### 4. Payment Processing System

**Problem:** Businesses lose revenue to no-shows and need easy way to collect deposits, tips, and package payments
**Solution:** Stripe integration for card-on-file, deposits, tips, packages/punch cards, gift cards
**Impact:** Reduces no-shows by 30%+; enables package revenue model
**Effort:** Medium
**Dependencies:** Core models
**Status:** Not Started
**Sprint:** Sprint 3 (Weeks 5-6)
**PRD:** [To be created]

**Features:**
- Card-on-file requirement for bookings
- Deposit collection (configurable per service)
- Tip processing (post-appointment)
- Package/punch card purchasing
- Gift card sales and redemption
- Cancellation policy enforcement with charge logic

---

### 5. SMS Reminder & Notification System

**Problem:** High no-show rates due to missed appointments; manual reminder calls are time-consuming
**Solution:** Automated SMS reminders via Twilio with 24hr/2hr confirmations, late-running alerts
**Impact:** Improves booking completion to 70%+; reduces manual admin work
**Effort:** Medium
**Dependencies:** Twilio account, A2P/10DLC registration
**Status:** Not Started
**Sprint:** Sprint 3 (Weeks 5-6)
**PRD:** [To be created]

**Features:**
- 24-hour advance reminder
- 2-hour pre-appointment reminder
- Booking confirmation on creation
- Late-running notifications (if groomer delayed)
- Appointment completion confirmation
- Waitlist notifications

**Compliance:**
- A2P/10DLC registration required
- Opt-in workflow for SMS communications
- Template verification for carriers

---

### 6. Vaccination Tracking & Lifecycle Management

**Problem:** Groomers/trainers must verify pet vaccinations; manual tracking is error-prone and risky
**Solution:** Pet profile with vax card upload, expiry tracking, auto-reminders to owners, booking blocks if expired
**Impact:** Reduces liability risk; automates compliance; differentiates from competitors
**Effort:** Medium
**Dependencies:** Core models, file upload system
**Status:** Not Started
**Sprint:** Sprint 4 (Weeks 7-8)
**PRD:** [To be created]

**Features:**
- Vaccination record upload (photo of vax card)
- Expiry date tracking per vaccination type
- Auto-reminders to owners 30/14/7 days before expiry
- Booking block if vax expired (configurable)
- Manual override capability for staff
- Vaccination status display in booking widget

---

### 7. Two-Way SMS Inbox & Quick Actions

**Problem:** Businesses need to respond to customer questions, reschedule requests, and status updates via SMS
**Solution:** Two-way SMS inbox with templates, quick actions, and two-tap reschedule workflow
**Impact:** Core differentiator; enables true SMS-first operations
**Effort:** Large
**Dependencies:** SMS reminder system, Twilio integration
**Status:** Not Started
**Sprint:** Sprint 5 (Weeks 9-10)
**PRD:** [To be created]

**Features:**
- Inbox view of all SMS conversations (tenant-scoped)
- Message templates for common responses
- Two-tap reschedule: "Reply 1 for tomorrow 2pm, 2 for Friday 10am"
- Quick actions: confirm, cancel, request callback
- Staff assignment of conversations
- SMS conversation history per pet owner

---

### 8. Ops Tools: Day View & Workflow Management

**Problem:** Groomers/trainers need clear view of daily schedule, ability to log notes, and track before/after photos
**Solution:** Day view optimized for table/van/trainer resource, notes, photo upload, incident logging
**Impact:** Improves daily operations; provides proof of work; enables better service quality
**Effort:** Medium
**Dependencies:** Core scheduling system
**Status:** Not Started
**Sprint:** Sprint 6 (Weeks 11-12)
**PRD:** [To be created]

**Features:**
- Calendar view by resource (table 1, van 2, trainer name)
- Drag-and-drop rescheduling
- Appointment notes field
- Before/after photo upload (stored with tenant prefix)
- Incident log (injuries, behavior issues)
- Quick status updates (in-progress, running late, completed)

---

### 9. Reporting & Analytics Dashboard

**Problem:** Businesses need visibility into revenue, no-show rates, staff utilization, and booking trends
**Solution:** Basic reporting dashboard with key metrics and export capability
**Impact:** Enables data-driven operations; validates our success metrics
**Effort:** Small-Medium
**Dependencies:** All core features complete
**Status:** Not Started
**Sprint:** Sprint 6 (Weeks 11-12)
**PRD:** [To be created]

**Reports:**
- Revenue by period (day/week/month)
- No-show rate tracking
- Staff/resource utilization percentage
- Booking source breakdown (online vs manual)
- Top services by revenue/volume
- Vaccination compliance rate

---

## Success Metrics

### Key Results for Q1 2025 (Beta Launch)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Beta Shops Enrolled** | 0 | 20 | 🔵 Not Started |
| **No-Show Reduction** | N/A | ≥30% vs baseline | 🔵 Not Started |
| **Booking Completion Rate** | N/A | ≥70% post-reminder | 🔵 Not Started |
| **Utilization Increase** | N/A | +10-15% | 🔵 Not Started |
| **SMS Delivery Rate** | N/A | ≥95% | 🔵 Not Started |
| **Migration Time** | N/A | ≤60 minutes | 🔵 Not Started |
| **System Uptime** | N/A | ≥99.5% | 🔵 Not Started |

### Post-Beta Metrics (Q2 2025+)

| Metric | Target |
|--------|--------|
| Monthly Churn | <2% |
| Payback Period | <3 months |
| ARPU | $80-120/mo |
| CAC | $150-300 |
| LTV | ≈$2,400 |

---

## Resource Allocation

### Team Capacity
- **Engineering:** Solo founder (full-stack)
- **Design:** Solo founder + design tools/templates
- **Product:** Solo founder

### Effort Distribution (12-week build period)
- 75% - Core feature development (6 MVP areas)
- 15% - Testing & QA (prevent bugs before beta)
- 10% - Infrastructure setup (hosting, CI/CD, monitoring)

### Time Budget by Sprint
- **Sprint 1 (2 weeks):** Database schema, core models, authentication
- **Sprint 2 (2 weeks):** Scheduling engine, double-booking prevention
- **Sprint 3 (2 weeks):** Booking widget, payments, SMS reminders
- **Sprint 4 (2 weeks):** Vaccination system, no-show defense
- **Sprint 5 (2 weeks):** Two-way SMS, quick actions
- **Sprint 6 (2 weeks):** Ops tools, reporting, beta onboarding

---

## Risks and Dependencies

| Risk/Dependency | Impact | Mitigation | Owner |
|-----------------|--------|------------|-------|
| **A2P/10DLC SMS Registration Delay** | High - Could block SMS features | Start registration in Sprint 1; have fallback email system | Chris |
| **Stripe Integration Complexity** | Medium - Payments are critical | Use well-documented Stripe SDK; build simple first | Chris |
| **Twilio SMS Delivery Issues** | High - Core differentiator at risk | Register properly, verify templates, monitor delivery rates | Chris |
| **Scope Creep** | High - Could delay launch | Strict adherence to 6 MVP areas only; no additions | Chris |
| **Solo Founder Capacity** | High - Timeline depends on one person | Realistic sprint planning, focus on essentials only | Chris |
| **Beta Shop Recruitment** | Medium - Need 20 shops to validate | Start outreach in Week 8; leverage personal network | Chris |

---

## What We're NOT Doing (Q1 2025)

It's important to be explicit about what we're deprioritizing for the complete build:

- ❌ **Multi-location support** - Only single-location businesses in MVP
- ❌ **Route optimization** - Basic travel-time blocks only, no intelligent routing
- ❌ **Calendar imports** - Beta shops will manual-enter or migrate via CSV (post-beta feature)
- ❌ **Class roster management** - Trainers can use packages/punch cards but no dedicated class UI
- ❌ **Advanced reporting** - Basic reports only; detailed analytics post-launch
- ❌ **Branded domains** - All beta shops on standard subdomains
- ❌ **White-label options** - Standard branding only
- ❌ **Mobile native apps** - Mobile-optimized web app only
- ❌ **Integration APIs** - No third-party integrations in beta

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-02 | Complete Build approach (60-90 days) | All 6 MVP areas needed to differentiate from incumbents; partial release wouldn't solve core pain points |
| 2025-11-02 | Focus on mobile groomers & solo trainers | Smallest viable wedge with highest pain; easier to sell narrow than broad |
| 2025-11-02 | Twilio for SMS (not alternatives) | Industry standard, reliable delivery, well-documented, A2P/10DLC compliant |
| 2025-11-02 | Stripe for payments (not alternatives) | Easiest integration, best documentation, standard in SaaS, supports deposits/tips/packages |
| 2025-11-02 | Multi-tenant from day 1 | SaaS model requires it; harder to retrofit later; foundational decision |
| 2025-11-02 | Subdomain tenant model | Easier than path-based, cleaner UX, simpler routing |

---

## Beta Launch Criteria (End of Week 12)

Before launching beta with 20 shops, we must have:

✅ All 6 MVP areas complete and tested
✅ Multi-tenant isolation verified (cross-tenant data leaks = show-stopper)
✅ SMS delivery rate ≥95% (A2P/10DLC fully registered)
✅ Stripe payment processing tested with real transactions
✅ Mobile booking widget responsive on iOS/Android
✅ Double-booking prevention verified under load
✅ Vaccination blocking logic tested with edge cases
✅ Two-way SMS inbox functional with templates
✅ Ops day view tested with real grooming schedules
✅ Basic reports accurate and exportable
✅ Onboarding flow smooth (≤60 minute migration time)
✅ Terms of service & privacy policy published
✅ Support email/SMS system in place
✅ Monitoring & alerting configured
✅ Backup & disaster recovery tested

---

## Feedback and Questions

**For Beta Shops:**
- What's your biggest pain point today? (Validate our focus)
- Would SMS-first workflow actually help, or is it overkill?
- What's your tolerance for bugs in beta?
- What would make you switch from current tool?

**For Development:**
- Is 60-90 days realistic for solo founder?
- Should we cut any of the 6 MVP areas to launch faster?
- Which integrations are most critical (Stripe vs Twilio priority)?

---

## Revision History

| Date | Changes | Updated By |
|------|---------|------------|
| 2025-11-02 | Initial Q1 roadmap created | Chris Stephens |
