# Sprint 4 - Vaccination & No-Show Defense

**Sprint Duration:** Week 7-8 (February 17-28, 2025)
**Sprint Goal:** Implement vaccination tracking with lifecycle management and no-show prevention systems
**Status:** Planning

---

## Sprint Goal

Build systems to reduce liability and revenue loss:
1. **Vaccination tracking** - Upload vax cards, track expiry, auto-reminders
2. **Booking blocks** - Prevent bookings if vaccination expired
3. **Manual overrides** - Staff can override vaccination requirements with documentation
4. **Cancellation policies** - Define and enforce cancellation windows
5. **No-show tracking** - Flag chronic no-shows, apply fees
6. **Waitlist autofill** - Fill cancelled slots from waitlist automatically

Success means reduced liability risk from unvaccinated pets and 30%+ reduction in no-shows via policies and deposits.

---

## Sprint Capacity

**Available Days:** 10 working days
**Capacity:** ~60-70 hours
**Dependencies:** Sprint 3 (payment system) must be complete

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-060 | Create vaccination record model and storage | M | Chris | 📋 Todo |
| US-061 | Build vaccination card upload (photo/PDF) | M | Chris | 📋 Todo |
| US-062 | Implement expiry tracking and calculations | M | Chris | 📋 Todo |
| US-063 | Build automated expiry reminder system | M | Chris | 📋 Todo |
| US-064 | Create booking block logic for expired vaccinations | L | Chris | 📋 Todo |
| US-065 | Implement staff override workflow | M | Chris | 📋 Todo |
| US-066 | Define cancellation policy model | M | Chris | 📋 Todo |
| US-067 | Build cancellation fee calculation engine | M | Chris | 📋 Todo |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-068 | Create no-show tracking and flagging system | M | Chris | 📋 Todo |
| US-069 | Build waitlist autofill on cancellation | M | Chris | 📋 Todo |
| US-070 | Implement late cancellation fee charging | M | Chris | 📋 Todo |
| US-071 | Create vaccination compliance dashboard | S | Chris | 📋 Todo |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-072 | Build vaccination reminder SMS template customization | S | Chris | 📋 Todo |
| US-073 | Create pet health record integration | M | Chris | 📋 Todo |

---

## Detailed Story Breakdown

### US-060: Create vaccination record model

**Acceptance Criteria:**
- ✅ Database model for vaccination records
- ✅ Support multiple vaccination types (rabies, DHPP, bordetella, etc.)
- ✅ Store vaccination date and expiry date
- ✅ Link to uploaded file (photo/PDF of vax card)
- ✅ Track verification status (pending/verified/expired)

**Vaccination Record Model:**
```python
class VaccinationRecord:
    id: UUID
    tenant_id: UUID
    pet_id: UUID (foreign key)
    vaccination_type: str  # "rabies", "dhpp", "bordetella", etc.
    vaccination_date: date
    expiry_date: date
    file_url: str  # S3/storage URL for vax card photo
    verified_by: UUID | None  # staff who verified
    verified_at: datetime | None
    status: "pending" | "verified" | "expired" | "revoked"
    notes: text
    created_at: datetime
    updated_at: datetime
```

**Common Vaccination Types:**
- Rabies (required, 1-3 year expiry)
- DHPP (distemper combo, annual)
- Bordetella (kennel cough, 6 months)
- Leptospirosis (annual)
- Influenza (annual)
- Lyme (annual, regional)

---

### US-061: Build vaccination card upload

**Acceptance Criteria:**
- ✅ File upload UI (mobile-friendly, camera support)
- ✅ Support images (JPG, PNG) and PDF
- ✅ File size limit (10MB max)
- ✅ Store in tenant-prefixed cloud storage (S3 or equivalent)
- ✅ OCR extraction of dates (future enhancement, manual entry for MVP)
- ✅ Thumbnail generation for previews

**Upload Flow:**
1. Owner uploads photo of vax card (mobile camera or file picker)
2. File uploaded to cloud storage with tenant prefix: `{tenant_id}/vax-cards/{pet_id}/{filename}`
3. Create vaccination record with file_url
4. Staff reviews and verifies dates
5. Mark as verified

**Storage Structure:**
```
/pet-care-uploads/
  {tenant_id}/
    vax-cards/
      {pet_id}/
        {vax_record_id}_rabies.jpg
        {vax_record_id}_dhpp.pdf
    before-after/
      {appointment_id}/
        before.jpg
        after.jpg
```

---

### US-062: Implement expiry tracking

**Acceptance Criteria:**
- ✅ Calculate days until expiry
- ✅ Flag vaccinations as expired automatically
- ✅ Background job checks expiry daily
- ✅ Owner and staff notifications before expiry

**Expiry Calculation:**
```python
def check_vaccination_status(vax_record):
    today = date.today()
    days_until_expiry = (vax_record.expiry_date - today).days

    if days_until_expiry < 0:
        return "expired"
    elif days_until_expiry <= 7:
        return "expiring_soon"
    elif days_until_expiry <= 30:
        return "expires_soon"
    else:
        return "current"
```

**Daily Background Job:**
- Run at 6 AM daily
- Check all vaccination records
- Update status field
- Queue reminder SMS for expiring vaccinations (30, 14, 7 days before)

---

### US-063: Build automated expiry reminder system

**Acceptance Criteria:**
- ✅ SMS reminders at 30, 14, and 7 days before expiry
- ✅ Email reminders (fallback)
- ✅ Link to upload new vaccination card
- ✅ Reminder history tracked

**SMS Template:**
```
Hi {owner_name}, {pet_name}'s {vax_type} vaccination expires in {days} days ({expiry_date}).

Please upload an updated vaccination card to keep your account active.

Upload here: {booking_url}/pets/{pet_id}/vaccinations
```

**Reminder Schedule:**
- 30 days before: First reminder
- 14 days before: Second reminder
- 7 days before: Final reminder
- 1 day after expiry: Account restricted, must upload to book

---

### US-064: Create booking block logic for expired vaccinations

**Acceptance Criteria:**
- ✅ Check vaccination status during booking
- ✅ Block booking if required vaccination expired
- ✅ Display clear message to owner
- ✅ Provide link to upload vaccination
- ✅ Service-level vaccination requirements

**Booking Validation:**
```python
def validate_vaccination_requirements(pet, service):
    if not service.requires_vaccination:
        return True, None

    # Check required vaccination types
    required_vax_types = service.required_vaccinations or ["rabies", "dhpp"]

    for vax_type in required_vax_types:
        vax_record = get_latest_vaccination(pet.id, vax_type)

        if not vax_record:
            return False, f"Missing required vaccination: {vax_type}"

        if vax_record.status == "expired":
            return False, f"{vax_type} vaccination expired on {vax_record.expiry_date}"

        if vax_record.status != "verified":
            return False, f"{vax_type} vaccination pending verification"

    return True, None
```

**Service Configuration:**
```python
class Service:
    requires_vaccination: bool
    required_vaccinations: list[str] | None  # ["rabies", "dhpp", "bordetella"]
    allow_vaccination_override: bool  # Staff can override
```

---

### US-065: Implement staff override workflow

**Acceptance Criteria:**
- ✅ Staff can override vaccination requirement for specific booking
- ✅ Override reason must be documented
- ✅ Override logged in appointment notes and audit log
- ✅ Owner signs waiver (checkbox acknowledgment)
- ✅ Override expires after appointment (doesn't apply to future bookings)

**Override Flow:**
1. Staff attempts to book appointment for pet with expired vax
2. System shows vaccination block message
3. Staff clicks "Override vaccination requirement"
4. Staff must enter reason: "Owner will provide updated vax card at appointment" or "Puppies under 16 weeks exempt"
5. Owner must acknowledge waiver (if booking online, email waiver link)
6. Appointment created with override flag
7. Appointment notes show: "⚠️ Vaccination override applied by {staff_name} on {date}. Reason: {reason}"

**Audit Log:**
- Track all vaccination overrides
- Include staff who approved, date, reason
- Report on override frequency (prevent abuse)

---

### US-066: Define cancellation policy model

**Acceptance Criteria:**
- ✅ Tenant-level cancellation policy configuration
- ✅ Service-level overrides (different policies per service)
- ✅ Time-based fee structure
- ✅ No-show fee configuration
- ✅ Refund rules

**Cancellation Policy Model:**
```python
class CancellationPolicy:
    id: UUID
    tenant_id: UUID
    service_id: UUID | None  # null = default policy
    name: str

    # Time windows (hours before appointment)
    free_cancellation_hours: int  # e.g., 24 (free if >24hrs)
    partial_refund_hours: int  # e.g., 12 (50% refund if 12-24hrs)
    no_refund_hours: int  # e.g., 2 (no refund if <2hrs)

    # Fee structure
    late_cancellation_fee_type: "fixed" | "percentage"
    late_cancellation_fee_amount: int  # cents or percentage
    no_show_fee_type: "fixed" | "percentage" | "full_charge"
    no_show_fee_amount: int

    # Deposit handling
    deposit_refundable_hours: int  # Refund deposit if cancelled early enough

    is_active: bool
    created_at: datetime
```

**Example Policy:**
- Free cancellation if >24 hours before
- $20 fee if cancelled 12-24 hours before
- 50% service charge if cancelled 2-12 hours before
- Full service charge if cancelled <2 hours before
- No-show = full service charge + flag account

---

### US-067: Build cancellation fee calculation engine

**Acceptance Criteria:**
- ✅ Calculate fee based on cancellation time and policy
- ✅ Charge card on file automatically (or manual charge)
- ✅ Send cancellation confirmation with fee breakdown
- ✅ Refund logic for deposits
- ✅ Exception handling for failed charges

**Cancellation Flow:**
```python
def process_cancellation(appointment, cancelled_by, cancellation_reason):
    # Calculate hours before appointment
    hours_before = (appointment.scheduled_start - datetime.now()).total_seconds() / 3600

    # Get applicable policy
    policy = get_cancellation_policy(appointment.service_id, appointment.tenant_id)

    # Calculate fee
    if hours_before >= policy.free_cancellation_hours:
        fee = 0
        refund_deposit = True
    elif hours_before >= policy.partial_refund_hours:
        fee = calculate_fee(policy.late_cancellation_fee_type, policy.late_cancellation_fee_amount, appointment.service.price)
        refund_deposit = False
    elif hours_before >= policy.no_refund_hours:
        fee = appointment.service.price * 0.5  # 50% charge
        refund_deposit = False
    else:
        fee = appointment.service.price  # Full charge
        refund_deposit = False

    # Process charges
    if fee > 0:
        charge_card_on_file(appointment.owner_id, fee, "Cancellation fee")

    if refund_deposit and appointment.deposit_payment_id:
        refund_payment(appointment.deposit_payment_id)

    # Update appointment
    appointment.status = "cancelled"
    appointment.cancellation_reason = cancellation_reason
    appointment.cancellation_fee = fee
    appointment.cancelled_at = datetime.now()
    appointment.cancelled_by = cancelled_by

    # Send confirmation
    send_cancellation_sms(appointment, fee, refund_deposit)

    # Fill from waitlist
    fill_from_waitlist(appointment)
```

---

### US-068: Create no-show tracking system

**Acceptance Criteria:**
- ✅ Mark appointment as no-show
- ✅ Track no-show count per owner
- ✅ Flag accounts with 2+ no-shows
- ✅ Require deposit for flagged accounts
- ✅ Charge no-show fee automatically

**No-Show Tracking:**
```python
class Owner:
    no_show_count: int
    last_no_show_date: date | None
    is_flagged: bool  # true if no_show_count >= 2
    flagged_at: datetime | None
```

**No-Show Flow:**
1. Appointment time passes, owner doesn't show
2. Staff marks appointment as no-show
3. System charges no-show fee (card on file)
4. Increment owner.no_show_count
5. If no_show_count >= 2: set is_flagged = true
6. Send SMS: "We missed you today. A no-show fee of ${fee} has been charged. Please contact us if there was an issue."

**Flagged Account Restrictions:**
- Must provide deposit for all future bookings (even if normally not required)
- May require pre-payment instead of deposit
- Staff notification when flagged account books

**Unflagging:**
- After 3 successful appointments, remove flag
- Staff can manually remove flag with note

---

### US-069: Build waitlist autofill on cancellation

**Acceptance Criteria:**
- ✅ When appointment cancelled, check waitlist
- ✅ Notify first person on waitlist via SMS
- ✅ Give 2-hour window to claim slot
- ✅ If not claimed, notify next person
- ✅ Automatic booking if owner clicks claim link

**Autofill Flow:**
```python
def fill_from_waitlist(cancelled_appointment):
    # Find matching waitlist entries
    waitlist_entries = Waitlist.query.filter(
        Waitlist.tenant_id == cancelled_appointment.tenant_id,
        Waitlist.service_id == cancelled_appointment.service_id,
        Waitlist.status == "active",
        Waitlist.preferred_date == cancelled_appointment.scheduled_start.date()
    ).order_by(Waitlist.created_at).all()

    if not waitlist_entries:
        return  # No one waiting

    # Notify first person
    entry = waitlist_entries[0]
    send_waitlist_notification(entry, cancelled_appointment)

    # Mark as notified with expiry
    entry.status = "notified"
    entry.notified_at = datetime.now()
    entry.expires_at = datetime.now() + timedelta(hours=2)

    # Schedule job to check if claimed after 2 hours
    schedule_task("check_waitlist_expiry", delay=timedelta(hours=2), args=[entry.id])
```

**SMS Template:**
```
Great news! A slot opened for {service_name} on {date} at {time}.

Claim it now: {claim_url}

This offer expires in 2 hours.
```

---

## Sprint Success Criteria

Sprint 4 is successful if:
- ✅ Vaccination upload working (photos processed and stored securely)
- ✅ Expiry tracking automated (daily job running)
- ✅ Booking blocks enforced for expired vaccinations
- ✅ Staff override workflow functional
- ✅ Cancellation policies configured and enforced
- ✅ No-show fees charging automatically
- ✅ Waitlist autofill working (cancelled slots filled within 2 hours)
- ✅ Compliance documentation complete (waivers, terms)
- ✅ Ready for Sprint 5 (two-way SMS)

---

## Links & References

- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Legal: Terms of Service must include vaccination waiver language
- Compliance: HIPAA considerations for pet health records (generally not applicable, but document)
