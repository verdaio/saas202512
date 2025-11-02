# Sprint 6 - Ops Tools & Reports

**Sprint Duration:** Week 11-12 (March 17-28, 2025)
**Sprint Goal:** Build daily operations dashboard, before/after photos, reporting, and beta onboarding
**Status:** Planning

---

## Sprint Goal

Complete the product with staff-facing operational tools and launch readiness:
1. **Ops day view** - Calendar view by table/van/trainer for daily operations
2. **Before/after photos** - Photo upload with appointment completion
3. **Incident logging** - Track injuries, behavioral issues, special notes
4. **Basic reporting** - Revenue, no-shows, utilization, vaccination compliance
5. **Beta onboarding flow** - Smooth 60-minute migration for beta shops
6. **Launch readiness** - Final testing, monitoring, documentation

Success means beta shops can run their entire operation in Pet Care with zero need for external tools.

---

## Sprint Capacity

**Available Days:** 10 working days
**Capacity:** ~60-70 hours
**Goal:** Beta launch ready by end of sprint

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-100 | Build ops calendar day view by resource | L | Chris | 📋 Todo |
| US-101 | Implement drag-and-drop rescheduling | M | Chris | 📋 Todo |
| US-102 | Create before/after photo upload system | M | Chris | 📋 Todo |
| US-103 | Build incident log and notes system | M | Chris | 📋 Todo |
| US-104 | Create revenue reporting dashboard | M | Chris | 📋 Todo |
| US-105 | Build no-show and utilization reports | M | Chris | 📋 Todo |
| US-106 | Implement vaccination compliance dashboard | S | Chris | 📋 Todo |
| US-107 | Create beta onboarding workflow | L | Chris | 📋 Todo |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-108 | Build staff schedule management | M | Chris | 📋 Todo |
| US-109 | Create appointment quick status updates | S | Chris | 📋 Todo |
| US-110 | Implement data export (CSV/PDF) for reports | M | Chris | 📋 Todo |
| US-111 | Build client communication history view | S | Chris | 📋 Todo |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-112 | Create route optimization for mobile services | M | Chris | 📋 Todo |
| US-113 | Build capacity forecasting reports | S | Chris | 📋 Todo |

---

## Detailed Story Breakdown

### US-100: Build ops calendar day view

**Acceptance Criteria:**
- ✅ Calendar view filtered by resource (table 1, van 2, trainer name)
- ✅ Hourly time slots (e.g., 8 AM - 6 PM)
- ✅ Appointments displayed as colored blocks
- ✅ Show pet name, owner name, service, status
- ✅ Click appointment to see details
- ✅ Visual indicators for status (scheduled, in-progress, completed, cancelled)
- ✅ Buffer times visible (lighter shade before/after appointments)

**View Options:**
- **By Resource:** See Table 1's full day schedule
- **By Staff:** See Sarah's full day schedule
- **By Date:** Navigate between days (today, tomorrow, week view)

**UI Design:**
```
[Date Picker: Tuesday, March 18, 2025]
[View By: Table 1 ▾]

 8:00 AM  |
 8:30     |  [Buffer: 10 min - Light blue]
 9:00     |  [Appointment: Bella - Full Groom - Owner: Smith - Green]
10:00     |
10:30     |  [Buffer: 15 min - Light blue]
11:00     |  [Appointment: Max - Bath & Brush - Owner: Johnson - Yellow]
11:30     |
12:00 PM  |  [Buffer: 15 min - Light blue]
12:30     |  [LUNCH BREAK - Gray]
 1:00     |  [Available]
 1:30     |  [Appointment: Charlie - Training - Owner: Davis - Blue]
 2:00     |  [In Progress - Charlie - Darker Blue]
```

**Color Coding:**
- Green = Scheduled (upcoming)
- Blue = In Progress
- Gray = Completed
- Red = Cancelled/No-Show
- Yellow = Needs attention (late, vaccination issue)

---

### US-101: Implement drag-and-drop rescheduling

**Acceptance Criteria:**
- ✅ Drag appointment block to new time slot
- ✅ Validate new time (run availability check)
- ✅ Show conflicts if any
- ✅ Confirm reschedule with popup
- ✅ Send SMS notification of reschedule
- ✅ Update appointment and log change

**Drag-and-Drop Flow:**
1. Staff clicks and holds appointment block
2. Drags to new time slot
3. On drop:
   - Check availability for new time
   - If available: Show confirm dialog "Reschedule Bella's grooming to 2:00 PM? Owner will be notified via SMS."
   - If conflict: Show error "Table 1 is booked at 2:00 PM. Try a different time."
4. On confirm:
   - Update appointment
   - Send SMS to owner
   - Refresh calendar view
   - Show success toast

---

### US-102: Create before/after photo upload

**Acceptance Criteria:**
- ✅ Photo upload during appointment or at completion
- ✅ Support multiple photos (2-5 per appointment)
- ✅ Store in tenant-prefixed cloud storage
- ✅ Display in appointment details and completion SMS
- ✅ Image compression (optimize for web/mobile)
- ✅ Photo approval before sending to owner (optional)

**Photo Upload Flow:**

**During Appointment:**
1. Staff clicks "Add Photos" on appointment
2. Upload before photos (during check-in)
3. Complete grooming
4. Upload after photos
5. Mark appointment as complete
6. System sends SMS with photos: "{pet_name} is ready! Check out the photos: {url}"

**Storage:**
```
/pet-care-uploads/
  {tenant_id}/
    before-after/
      {appointment_id}/
        before_1.jpg
        before_2.jpg
        after_1.jpg
        after_2.jpg
```

**SMS with Photos:**
```
{pet_name} is all done and looking great! 🐾

See the photos: https://petcare.app/photos/{appointment_id}

Total: ${amount}. Thanks for your business!
```

---

### US-103: Build incident log and notes system

**Acceptance Criteria:**
- ✅ Add notes to any appointment
- ✅ Flag incidents (injury, behavioral issue, health concern)
- ✅ Categorize incidents (severity: low/medium/high)
- ✅ Notify owner of incidents via SMS
- ✅ Search and report on incident history
- ✅ Incident form with required fields

**Incident Types:**
- Minor injury (small cut, nail quick bleeding)
- Behavioral issue (aggression, anxiety, fear)
- Health concern (observed limping, skin issue, etc.)
- Property damage (chewed item, accident)
- Special note (positive or negative)

**Incident Log Model:**
```python
class IncidentLog:
    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    pet_id: UUID
    owner_id: UUID
    incident_type: "injury" | "behavioral" | "health" | "property" | "note"
    severity: "low" | "medium" | "high"
    description: text
    action_taken: text
    notify_owner: bool
    notified_at: datetime | None
    logged_by: UUID  # Staff member
    created_at: datetime
```

**Workflow:**
1. During appointment, issue occurs
2. Staff clicks "Log Incident"
3. Fill form:
   - Type: Behavioral
   - Severity: Medium
   - Description: "Dog became anxious during nail trim, growled at groomer"
   - Action taken: "Paused grooming, gave break, completed without further issues"
   - Notify owner: Yes
4. Save incident
5. If notify_owner: Send SMS "There was a minor incident during {pet_name}'s visit today. Details have been noted in your account. Please call us if you have questions."

---

### US-104: Create revenue reporting dashboard

**Acceptance Criteria:**
- ✅ Total revenue by date range (day/week/month/year)
- ✅ Revenue by service type
- ✅ Revenue by staff member
- ✅ Revenue trend chart (line graph)
- ✅ Top customers by revenue
- ✅ Average transaction value

**Revenue Report:**
```
Period: March 1-14, 2025

Total Revenue: $4,580
  - Grooming: $3,200 (70%)
  - Training: $980 (21%)
  - Daycare: $400 (9%)

Revenue by Staff:
  - Sarah: $2,100
  - Mike: $1,800
  - Jenny: $680

Top Customers:
  1. Smith Family - $340 (3 appointments)
  2. Johnson Family - $280 (2 appointments)
  3. Davis Family - $220 (2 appointments)

[Line graph showing daily revenue trend]
```

**Filters:**
- Date range picker
- Group by: day/week/month
- Filter by staff, service type, payment status

---

### US-105: Build no-show and utilization reports

**Acceptance Criteria:**
- ✅ No-show rate by period
- ✅ No-show count by owner (identify chronic offenders)
- ✅ Resource utilization percentage
- ✅ Staff utilization percentage
- ✅ Peak hours analysis
- ✅ Available slots vs booked slots

**No-Show Report:**
```
Period: March 1-14, 2025

No-Show Rate: 8.3% (5 of 60 appointments)

Chronic No-Shows (2+ in period):
  - Owner: Johnson (2 no-shows)
  - Owner: Williams (2 no-shows)

No-Show Recovery:
  - Fees collected: $100
  - Waitlist fills: 2 (40%)
```

**Utilization Report:**
```
Resource Utilization:

Table 1: 82% (33 of 40 hours booked)
Table 2: 65% (26 of 40 hours booked)
Van 1: 90% (27 of 30 hours booked)

Staff Utilization:

Sarah: 85% (34 of 40 hours)
Mike: 78% (31 of 40 hours)

Peak Hours:
  - 9:00 AM - 11:00 AM: 95% utilization
  - 1:00 PM - 3:00 PM: 88% utilization
  - 4:00 PM - 6:00 PM: 60% utilization

Recommendation: Add more morning slots, reduce late afternoon availability.
```

---

### US-106: Vaccination compliance dashboard

**Acceptance Criteria:**
- ✅ Total pets with current vaccinations
- ✅ Pets with expiring vaccinations (30 days)
- ✅ Pets with expired vaccinations
- ✅ Compliance percentage
- ✅ Vaccination reminders sent vs uploaded

**Vaccination Dashboard:**
```
Vaccination Compliance

Total Active Pets: 45

✅ Current: 38 (84%)
⚠️  Expiring Soon (30 days): 5 (11%)
❌ Expired: 2 (5%)

Recent Activity:
  - Reminders sent: 12
  - Vax cards uploaded: 8
  - Upload rate: 67%

Action Items:
  - Follow up with 2 expired pets (manual call)
  - Send 5 expiring-soon reminders this week
```

---

### US-107: Create beta onboarding workflow

**Acceptance Criteria:**
- ✅ Business signup form (name, subdomain, contact)
- ✅ Guided setup wizard (5 steps, ~60 minutes total)
- ✅ Import existing data (CSV templates for pets, owners, services)
- ✅ Configure services and pricing
- ✅ Set up staff accounts
- ✅ Configure Twilio and Stripe
- ✅ Test booking flow
- ✅ Go-live checklist

**Onboarding Wizard Steps:**

**Step 1: Business Profile (10 min)**
- Business name, address, phone
- Operating hours (by day of week)
- Timezone
- Logo upload (optional)

**Step 2: Services Setup (15 min)**
- Pre-populated grooming service templates
- Customize duration, buffers, pricing
- Set vaccination requirements per service
- Configure deposits and cancellation policies

**Step 3: Resources & Staff (10 min)**
- Add grooming tables/vans/rooms
- Add staff members (name, email, role, skills)
- Set staff working hours

**Step 4: Import Existing Data (20 min)**
- Download CSV templates
- Import pets and owners
- Map columns
- Preview and confirm
- Alternative: Manual entry for small businesses

**Step 5: Integrations (5 min)**
- Connect Stripe (OAuth flow)
- Connect Twilio (provide API keys)
- Test SMS sending
- Test payment processing

**Go-Live Checklist:**
- [ ] All services configured
- [ ] Staff accounts created
- [ ] Test booking completed end-to-end
- [ ] SMS sending tested
- [ ] Payment processing tested (test mode)
- [ ] Public booking link shared with first customer
- [ ] Twilio A2P/10DLC submitted (pending approval)
- [ ] Training call scheduled (optional)

---

### US-108: Build staff schedule management

**Acceptance Criteria:**
- ✅ Set working hours per staff member
- ✅ Mark time off / vacation
- ✅ Recurring schedule templates (weekly)
- ✅ Override specific days
- ✅ Block booking during time off

**Staff Schedule:**
```
Sarah's Schedule:

Weekly:
  Monday: 8 AM - 5 PM
  Tuesday: 8 AM - 5 PM
  Wednesday: OFF
  Thursday: 9 AM - 6 PM
  Friday: 8 AM - 4 PM
  Saturday: 9 AM - 2 PM
  Sunday: OFF

Time Off:
  March 20-22: Vacation (blocked)
  March 25: Half day (8 AM - 12 PM only)
```

---

### US-109: Appointment quick status updates

**Acceptance Criteria:**
- ✅ One-click status updates (started, running late, completed)
- ✅ Send SMS automatically on status change
- ✅ Update appointment timeline
- ✅ Mobile-friendly (for staff on the floor)

**Quick Actions:**
- "Start" - Mark in-progress, start timer
- "Running Late" - Trigger late-running SMS with delay selection
- "Complete" - Mark done, prompt for photos, process final payment
- "No Show" - Mark no-show, charge fee, fill from waitlist

---

## Launch Readiness Tasks

### Testing
- [ ] End-to-end booking flow tested (10+ test bookings)
- [ ] Multi-tenant isolation verified (create 3 test tenants, verify no data leaks)
- [ ] Payment processing tested (deposits, full payments, refunds)
- [ ] SMS delivery tested (confirmations, reminders, replies)
- [ ] Scheduling conflicts tested (stress test: 100 concurrent bookings)
- [ ] Vaccination blocking tested (expired vax cannot book)
- [ ] Cancellation fees tested (various time windows)
- [ ] Load testing (1000+ appointments, 100+ concurrent users)

### Monitoring & Alerts
- [ ] Error tracking configured (Sentry or similar)
- [ ] Uptime monitoring (UptimeRobot or similar)
- [ ] SMS delivery monitoring (Twilio webhooks)
- [ ] Payment failure alerts
- [ ] Database performance monitoring

### Documentation
- [ ] User guide for beta shops
- [ ] API documentation (if needed)
- [ ] Troubleshooting guide
- [ ] Terms of Service published
- [ ] Privacy Policy published
- [ ] SMS opt-in compliance documented

### Security
- [ ] Security audit (OWASP top 10)
- [ ] Penetration testing (basic)
- [ ] SSL certificates configured
- [ ] Environment secrets secured
- [ ] Database backups automated
- [ ] Disaster recovery plan documented

---

## Sprint Success Criteria

Sprint 6 is successful if:
- ✅ Ops dashboard fully functional (staff can run daily operations)
- ✅ Before/after photos working (tested with real photos)
- ✅ Incident logging complete
- ✅ All 3 reports working (revenue, no-show, vaccination)
- ✅ Beta onboarding wizard tested (3 internal test tenants completed setup)
- ✅ All launch readiness tasks completed
- ✅ First beta shop can migrate in <60 minutes
- ✅ **READY FOR BETA LAUNCH** 🚀

---

## Beta Launch Plan (Post-Sprint)

**Week 13-14: Beta Recruitment**
- Direct outreach to 100 local pet care businesses
- Leverage personal network
- Partner channels (grooming schools, van upfitters)
- Goal: 20 beta shops enrolled

**Week 15-18: Beta Operation**
- Support beta shops daily
- Gather feedback and bug reports
- Iterate on pain points
- Track success metrics (no-show reduction, booking completion, utilization)

**Week 19-20: Beta Review & Public Launch Prep**
- Analyze beta metrics
- Create case studies from successful shops
- Prepare for public launch (pricing page, marketing site)
- Plan for scale

---

## Links & References

- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Beta Launch Checklist: (to be created)
- Training Materials: (to be created)
