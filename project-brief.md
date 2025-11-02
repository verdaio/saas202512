# Project Brief: Pet Care Scheduler

**Trade Name:** Pet Care
**Project ID:** saas202512
**Created:** 2025-11-02
**Status:** Planning
**Last Updated:** 2025-11-02
**Source:** Pet_Care_Scheduler_Viability_Summary.pdf

---

## Verdict

**Viable.** Focus on SMS-first ops and double-booking prevention. Start with mobile groomers and solo trainers.

---

## Market Analysis

### Market Characteristics
- **Fragmented SMB market** - Moderate TAM with high pain from admin overhead
- **Incumbent weakness** - Existing solutions weak on routing, class packages, and strict overlap rules
- **Switching costs** - Real but manageable. Offer migration support and parallel run capability

### Opportunity
High pain point in pet care scheduling with inadequate existing solutions. Clear gap in market for SMS-first, double-booking prevention focused tool.

---

## ICP & Wedge Strategy

### Primary Target (Initial Focus)
- Mobile groomers
- Solo trainers

### Secondary Target (Expansion)
- Small salons (1–3 tables)
- Boutiques running classes/packages

---

## MVP Scope (Complete Build: 60-90 Days)

### 1. Scheduling Engine
- Buffers per service/staffer/pet
- Multi-pet flow
- Channel guardrails
- **Key differentiator:** "Impossible to double-book" safeguards

### 2. Vaccination & Intake
- Pet profile management
- Expiry tracking
- Owner-upload vax cards
- Auto reminders
- Vaccination lifecycle with blocks and overrides

### 3. No-Show Defense
- Card-on-file
- Deposits
- Cancellation windows
- Waitlist autofill

### 4. Payments
- Deposits
- Tips
- Packages/punch cards
- Gift cards

### 5. Owner UX
- Mobile booking link
- Family account
- Reschedule via text
- SMS-first workflows (confirmations, late-running, two-tap reschedule)

### 6. Ops Tools
- Day view by table/van/trainer
- Notes
- Photo before/after
- Incident log
- Route clustering for vans with travel-time blocks

---

## Key Differentiators

1. **"Impossible to double-book" safeguards** - Core technical focus
2. **SMS-first workflows** - Confirmations, late-running alerts, two-tap reschedule
3. **Vaccination lifecycle** - Baked in with blocks and overrides
4. **Trainer packages/credits** - Class rosters with waitlists
5. **Route clustering** - Travel-time blocks for mobile vans

---

## Pricing Strategy

### Subscription Tiers
- **Starter:** $49/mo (solo operator)
- **Standard:** $99/mo (2–5 staff)
- **Pro:** $199/mo (multi-location, advanced reporting)

### Add-Ons
- SMS overage fees
- Payments margin
- Branded domain

### Incentives
- **Annual:** 2 months free
- **White-glove setup** included

---

## Go-To-Market Strategy

### Direct Outreach
- Target 100 local businesses
- Promise 60-minute calendar migration
- Focus on ease of switching

### Partnership Channels
- Grooming schools
- Van upfitters
- Facebook groups
- Revenue-share model

### Migration Support
- Importers for Calendly/Square/spreadsheets
- Weekend migration windows
- 2-week parallel mode option

### Launch Strategy
- Invite-only beta with 20 shops
- Develop case studies
- Build social proof

---

## Success Metrics

### Key Performance Indicators
- **No-shows down:** ≥30%
- **Booking completion:** ≥70% post-reminder
- **Utilization increase:** +10–15%
- **Monthly churn:** <2%
- **Payback period:** <3 months

---

## Unit Economics (Targets)

### Revenue
- **ARPU:** $80–120/mo
- **Gross margin:** 80–85% after SMS and support

### Costs
- **SMS:** $0.02–0.03/message
- **Messages per booking:** 8–15 messages per lifecycle
- **CAC:** $150–300
- **LTV:** ≈$2,400 at $99/mo for 24 months

---

## Risks & Mitigations

### Competitive Risk
- **Risk:** Incumbents respond with similar features
- **Mitigation:** Focus on routing, classes, strict anti-overlap features they can't easily replicate

### Switching Friction
- **Risk:** Businesses reluctant to migrate from current tools
- **Mitigation:** Build importers, offer weekend migration, provide 2-week parallel mode

### Regulatory (A2P/10DLC)
- **Risk:** SMS delivery issues, compliance complexity
- **Mitigation:** Register properly, verify templates, implement opt-in flows

### Payment Risk
- **Risk:** Chargebacks from disputed charges
- **Mitigation:** Firm policies, signed terms, photo/time-stamp evidence

---

## Build Order (60–90 Days)

### Phase 1: Foundation (Weeks 1-2)
Core models: pets, owners, staff, services, rooms/vans, packages, appts, payments

### Phase 2: Calendar Engine (Weeks 3-4)
Calendar engine with buffers and resource constraints

### Phase 3: Booking & Payments (Weeks 5-6)
Booking widget + deposits + SMS reminders

### Phase 4: Vaccination System (Weeks 7-8)
Vax upload and expiry logic

### Phase 5: SMS Workflows (Weeks 9-10)
Two-way SMS inbox with templates and quick actions

### Phase 6: Reporting (Weeks 11-12)
Basic reports: revenue, no-shows, utilization

---

## Pre-Build Validation

### Wizard-of-Oz Pilot
- Use Google Calendar + Stripe + Twilio behind custom form
- Test workflows without full build

### Landing Page Test
- Price test with real $1 trial checkout
- Validate willingness to pay

### Shadow Study
- Shadow 1 salon and 1 van for full day
- Log edge cases and workflow details

---

## Bottom Line

**Green light** if you:
1. Ship SMS-first workflows
2. Enforce no double-booking
3. Execute clean migration playbook

**Strategy:** Build tight. Sell narrow. Expand from the wedge.

---

## Multi-Tenant Considerations

**This project is multi-tenant enabled (subdomain model).**

Key architectural considerations:
- All pet care business data must be tenant-isolated
- Each business gets their own subdomain (e.g., happypaws.petcare.com)
- Database schema must include `tenant_id` on all tables
- API endpoints must be tenant-scoped
- File storage (vax cards, before/after photos) must use tenant prefix
- SMS workflows must be tenant-specific (proper sender identification)

---

## Technical Stack Implications

### Critical Requirements
- **SMS Integration:** Twilio (high priority, core differentiator)
- **Payment Processing:** Stripe (deposits, tips, packages)
- **Calendar Engine:** Custom build with strict resource constraints
- **File Upload:** Vaccination cards, before/after photos
- **Mobile-First:** Responsive booking widget
- **Real-Time:** SMS two-way communication

### Compliance & Security
- **A2P/10DLC Registration** - Required for SMS delivery
- **PCI Compliance** - For payment processing
- **Data Privacy** - Pet owner personal information
- **Signed Terms** - For cancellation policies and deposits
