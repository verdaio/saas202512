# Sprint 2 - Scheduling Engine

**Sprint Duration:** Week 3-4 (January 20-31, 2025)
**Sprint Goal:** Build the "impossible to double-book" scheduling engine with resource constraints and buffer management
**Status:** Planning

---

## Sprint Goal

Deliver the core scheduling engine that differentiates Pet Care from competitors:
1. **Conflict detection algorithm** - Check staff, resource, and pet availability before allowing bookings
2. **Buffer time management** - Enforce setup/cleanup buffers and travel time for mobile services
3. **Multi-pet appointment handling** - Support booking multiple pets in same time slot with proper resource allocation
4. **Resource constraint enforcement** - Tables, vans, and rooms can't be double-booked
5. **Channel guardrails** - Different booking rules for online vs manual (staff) bookings

This is the **highest-value sprint** - the scheduling engine is our primary differentiator. If this works flawlessly, we win the market.

---

## Sprint Capacity

**Available Days:** 10 working days (2 weeks)
**Capacity:** ~60-70 hours (solo founder, 6-7 hours/day)
**Commitments/Time Off:** None

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-020 | Design scheduling conflict detection algorithm | L | Chris | 📋 Todo | Core business logic |
| US-021 | Implement availability checking service | L | Chris | 📋 Todo | Check staff/resource/pet availability |
| US-022 | Build buffer time calculation engine | M | Chris | 📋 Todo | Service buffers + travel time |
| US-023 | Create appointment booking service with validation | L | Chris | 📋 Todo | Validates all constraints before booking |
| US-024 | Implement multi-pet appointment logic | M | Chris | 📋 Todo | Same time slot, proper resource allocation |
| US-025 | Build resource locking mechanism | M | Chris | 📋 Todo | Prevent race conditions in bookings |
| US-026 | Create appointment calendar view API | M | Chris | 📋 Todo | Get availability by date range, resource, staff |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-027 | Implement appointment rescheduling logic | M | Chris | 📋 Todo | Cancel + rebook with validation |
| US-028 | Build waitlist system for fully-booked slots | M | Chris | 📋 Todo | Auto-notify when slot opens |
| US-029 | Create recurring appointment templates | M | Chris | 📋 Todo | Weekly training sessions, etc. |
| US-030 | Add time slot suggestion algorithm | M | Chris | 📋 Todo | Suggest next available time |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status | Notes |
|-------|-------------|----------|----------|--------|-------|
| US-031 | Build appointment conflict dashboard | S | Chris | 📋 Todo | View all scheduling conflicts |
| US-032 | Implement overbooking rules (advanced) | S | Chris | 📋 Todo | Allow intentional overbooking with limits |
| US-033 | Create capacity planning reports | S | Chris | 📋 Todo | Utilization forecasting |

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

- [ ] Write comprehensive unit tests for scheduling logic (critical for reliability)
- [ ] Add integration tests for concurrent booking scenarios
- [ ] Performance test scheduling with 1000+ appointments
- [ ] Document scheduling algorithm in technical/architecture/scheduling-engine.md

---

## Detailed Story Breakdown

### US-020: Design scheduling conflict detection algorithm

**Acceptance Criteria:**
- ✅ Document algorithm flowchart and pseudo-code
- ✅ Define all constraint types (staff, resource, pet, buffer, vaccination)
- ✅ Handle edge cases (overnight appointments, timezone boundaries)
- ✅ Performance target: <200ms for conflict check on 10,000 appointments

**Algorithm Overview:**
```
For a proposed appointment (pet, service, staff, resource, start_time):
1. Calculate time window:
   - start = requested_start - service.buffer_before
   - end = requested_start + service.duration + service.buffer_after

2. Check constraints:
   a) Staff availability:
      - Is staff working during [start, end]?
      - Does staff have conflicting appointments?
      - Does staff have the required skills?

   b) Resource availability:
      - Is resource available during [start, end]?
      - Does resource have conflicting appointments?

   c) Pet availability:
      - Does pet have conflicting appointment?
      - Is pet's vaccination current (if required)?

   d) Buffer compliance:
      - Does this create buffer conflicts with adjacent appointments?

   e) Travel time (for mobile services):
      - If van/mobile, check travel time from previous location
      - Add travel buffer if needed

3. Return:
   - available: true/false
   - conflicts: array of conflict reasons
   - suggested_times: next 3 available slots
```

**Constraint Priority:**
1. **Hard constraints** (cannot be overridden): Resource double-booking, staff double-booking, pet double-booking
2. **Soft constraints** (can override with permission): Buffer violations, vaccination expiry
3. **Warning constraints** (notify but allow): Overbooking threshold, same-day bookings

---

### US-021: Implement availability checking service

**Acceptance Criteria:**
- ✅ Service class: `AvailabilityChecker`
- ✅ Method: `check_availability(appointment_request) -> AvailabilityResult`
- ✅ Handles all constraint types
- ✅ Returns detailed conflict information
- ✅ Unit tests with 95%+ coverage
- ✅ Performance: <200ms for standard checks

**AvailabilityResult:**
```python
{
  "is_available": boolean,
  "conflicts": [
    {
      "type": "staff_conflict" | "resource_conflict" | "pet_conflict" | "buffer_violation",
      "message": "Staff 'Sarah' has appointment at 2:00 PM",
      "conflicting_appointment_id": uuid,
      "severity": "hard" | "soft" | "warning"
    }
  ],
  "suggested_times": [
    {"start": "2025-01-20T15:00:00Z", "staff_id": uuid, "resource_id": uuid},
    {"start": "2025-01-20T16:30:00Z", "staff_id": uuid, "resource_id": uuid},
  ]
}
```

**Key Methods:**
- `check_staff_availability(staff_id, start, end)` → boolean + conflicts
- `check_resource_availability(resource_id, start, end)` → boolean + conflicts
- `check_pet_availability(pet_id, start, end)` → boolean + conflicts
- `check_buffer_compliance(appointment_request)` → boolean + violations
- `suggest_next_available_times(appointment_request, limit=3)` → array of suggestions

---

### US-022: Build buffer time calculation engine

**Acceptance Criteria:**
- ✅ Calculate total buffer for any service
- ✅ Handle mobile service travel time
- ✅ Support custom buffer overrides per staff member
- ✅ Unit tests for all buffer scenarios

**Buffer Types:**
1. **Service buffer (before)** - Setup time (e.g., 10 min to prepare grooming station)
2. **Service buffer (after)** - Cleanup time (e.g., 15 min to clean and sanitize)
3. **Travel buffer** - For mobile services (calculated based on distance or fixed per appointment)
4. **Staff buffer override** - Some staff are faster/slower

**Calculation:**
```python
def calculate_total_window(service, staff, is_mobile, prev_appointment=None):
    buffer_before = service.buffer_before_minutes
    duration = service.duration_minutes
    buffer_after = service.buffer_after_minutes

    # Staff-specific adjustments
    if staff.buffer_multiplier:
        buffer_before *= staff.buffer_multiplier
        buffer_after *= staff.buffer_multiplier

    # Travel time for mobile
    if is_mobile and prev_appointment:
        travel_time = estimate_travel_time(prev_appointment.location, new_location)
        buffer_before += travel_time

    total_start = requested_start - buffer_before
    total_end = requested_start + duration + buffer_after

    return (total_start, total_end)
```

**Travel Time Estimation:**
- Phase 1 (MVP): Fixed travel buffer (e.g., 30 minutes between mobile appointments)
- Phase 2 (Future): Google Maps API integration for actual travel time

---

### US-023: Create appointment booking service with validation

**Acceptance Criteria:**
- ✅ Service class: `AppointmentBookingService`
- ✅ Method: `book_appointment(appointment_request) -> Appointment | ValidationError`
- ✅ Atomic transaction (all-or-nothing booking)
- ✅ Lock resources to prevent race conditions
- ✅ Send booking confirmation (SMS placeholder for Sprint 3)
- ✅ Integration tests with concurrent booking attempts

**Booking Flow:**
```
1. Start database transaction
2. Lock resources (staff, resource, pet) using SELECT FOR UPDATE
3. Run availability check
4. If conflicts exist:
   - Rollback transaction
   - Return validation error with conflicts
5. If available:
   - Create appointment record
   - Create initial payment record (if deposit required)
   - Log booking event
   - Commit transaction
   - Queue SMS confirmation (for Sprint 3)
   - Return appointment
```

**Error Handling:**
- 409 Conflict: Resource already booked (race condition caught)
- 400 Bad Request: Invalid appointment data
- 422 Unprocessable: Business rule violation (vaccination expired, etc.)
- 500 Internal Server Error: Unexpected failure (rollback transaction)

---

### US-024: Implement multi-pet appointment logic

**Acceptance Criteria:**
- ✅ Support booking 2+ pets in same appointment slot
- ✅ Validate resource capacity (e.g., table can handle 2 small dogs, not 3 large dogs)
- ✅ Calculate combined duration (sequential or parallel based on service)
- ✅ Adjust pricing for multi-pet (discount rules)
- ✅ Unit tests for multi-pet scenarios

**Multi-Pet Rules:**
1. **Same service, same time:**
   - Multiple pets get groomed simultaneously (if resource supports it)
   - Resource capacity check (table size, van space)

2. **Same service, sequential:**
   - Pets groomed one after another
   - Duration = sum of individual durations (with reduced buffer)

3. **Different services:**
   - Not allowed in same appointment (book separately)

**Capacity Model:**
```python
# Resource capacity
resource.capacity = {
  "max_pets": 2,  # Max 2 pets at once
  "max_weight_lbs": 150,  # Combined weight limit
  "size_restrictions": ["small", "medium"]  # No large dogs
}

# Validation
def validate_multi_pet_capacity(resource, pets):
    if len(pets) > resource.capacity.max_pets:
        return False, "Exceeds max pets"

    total_weight = sum(pet.weight for pet in pets)
    if total_weight > resource.capacity.max_weight_lbs:
        return False, "Exceeds weight limit"

    for pet in pets:
        if pet.size not in resource.capacity.size_restrictions:
            return False, f"Pet size '{pet.size}' not supported"

    return True, None
```

---

### US-025: Build resource locking mechanism

**Acceptance Criteria:**
- ✅ PostgreSQL row-level locks on resources during booking
- ✅ Timeout handling (release lock after 30 seconds)
- ✅ Deadlock detection and retry logic
- ✅ Concurrent booking test (100 simultaneous requests, zero double-books)

**Locking Strategy:**
```sql
-- During booking transaction
BEGIN;

-- Lock the resource to prevent concurrent bookings
SELECT * FROM resources
WHERE id = :resource_id
AND tenant_id = :tenant_id
FOR UPDATE NOWAIT;

-- If lock acquired, proceed with availability check
-- If lock fails (NOWAIT), return 409 Conflict immediately

-- Create appointment if available

COMMIT;
```

**Handling Lock Contention:**
1. **NOWAIT approach:** Fail fast, return 409, let client retry
2. **Timeout approach:** Wait up to 5 seconds, then fail
3. **Retry logic:** Frontend retries up to 3 times with exponential backoff

**Testing:**
- Simulate 100 concurrent booking requests for same time slot
- Verify only 1 booking succeeds
- Verify 99 requests get proper conflict error
- Verify no deadlocks or hung transactions

---

### US-026: Create appointment calendar view API

**Acceptance Criteria:**
- ✅ Endpoint: GET /appointments/calendar
- ✅ Filter by: date range, staff, resource, pet
- ✅ Return: appointments with calculated time windows (including buffers)
- ✅ Performance: <500ms for 1000 appointments
- ✅ Pagination support

**Endpoint Design:**
```
GET /appointments/calendar?
  start_date=2025-01-20&
  end_date=2025-01-27&
  staff_id=uuid&
  resource_id=uuid&
  view=day|week|month

Response:
{
  "appointments": [
    {
      "id": uuid,
      "pet": {...},
      "owner": {...},
      "service": {...},
      "staff": {...},
      "resource": {...},
      "scheduled_start": "2025-01-20T14:00:00Z",
      "scheduled_end": "2025-01-20T15:30:00Z",
      "buffer_start": "2025-01-20T13:50:00Z",  # includes buffer_before
      "buffer_end": "2025-01-20T15:45:00Z",     # includes buffer_after
      "status": "scheduled",
      "notes": "First visit, nervous dog"
    }
  ],
  "resource_utilization": {
    "resource_id": uuid,
    "available_slots": [...],
    "booked_slots": [...],
    "utilization_percentage": 73.2
  }
}
```

**Performance Optimization:**
- Index on (tenant_id, scheduled_start, scheduled_end)
- Index on (tenant_id, staff_id, scheduled_start)
- Index on (tenant_id, resource_id, scheduled_start)
- Use database query optimization for date range filtering

---

### US-027: Implement appointment rescheduling logic

**Acceptance Criteria:**
- ✅ Validate new time slot before rescheduling
- ✅ Preserve appointment history (log original time)
- ✅ Check cancellation policy (time window restrictions)
- ✅ Send reschedule confirmation (SMS placeholder for Sprint 3)
- ✅ Handle reschedule fees (if applicable)

**Reschedule Flow:**
```
1. Validate request:
   - Is appointment in future?
   - Is reschedule within allowed window (e.g., 24 hours before)?
   - Does user have permission?

2. Check new time availability:
   - Run full availability check for new time
   - If conflicts, return error with suggestions

3. Update appointment:
   - Log original time in appointment_history
   - Update scheduled_start, scheduled_end
   - Update status to "rescheduled"
   - Log reschedule event

4. Apply reschedule fee (if applicable):
   - Check cancellation policy
   - Create fee charge if within restricted window

5. Send notifications:
   - Queue SMS to owner
   - Notify staff of schedule change
```

**Cancellation Policy:**
```python
# Example policy
policy = {
  "free_reschedule_hours": 24,  # Free if >24hrs before
  "reschedule_fee_cents": 1000,  # $10 fee if <24hrs
  "no_reschedule_hours": 2,      # Cannot reschedule if <2hrs
}
```

---

### US-028: Build waitlist system for fully-booked slots

**Acceptance Criteria:**
- ✅ Add pet to waitlist for desired time slot
- ✅ Auto-notify when slot opens (cancellation or new availability)
- ✅ FIFO ordering (first on waitlist gets first notification)
- ✅ Waitlist expiration (notification expires after 2 hours)
- ✅ Owner can join multiple waitlists

**Waitlist Model:**
```python
class Waitlist:
    id: UUID
    tenant_id: UUID
    pet_id: UUID
    owner_id: UUID
    service_id: UUID
    preferred_staff_id: UUID | None
    preferred_date: date
    preferred_time_range: (time, time)  # e.g., (9:00, 12:00)
    status: "active" | "notified" | "booked" | "expired"
    created_at: datetime
    notified_at: datetime | None
    expires_at: datetime | None
```

**Workflow:**
1. Owner tries to book, slot is full
2. System offers waitlist option
3. Owner joins waitlist with preferences
4. When appointment cancels or new availability:
   - Query active waitlist entries matching criteria
   - Sort by created_at (FIFO)
   - Send SMS notification to first person
   - Mark as "notified", set expires_at = now + 2 hours
5. If owner books within 2 hours, mark "booked"
6. If 2 hours pass without booking, mark "expired" and notify next person

---

### US-029: Create recurring appointment templates

**Acceptance Criteria:**
- ✅ Define recurring pattern (weekly, biweekly, monthly)
- ✅ Create series of appointments with one action
- ✅ Handle skipped dates (holidays, staff unavailability)
- ✅ Allow editing one instance or entire series
- ✅ Cancellation of entire series or single instance

**Recurring Pattern:**
```python
class RecurringPattern:
    frequency: "weekly" | "biweekly" | "monthly"
    day_of_week: int  # 0=Monday, 6=Sunday (for weekly)
    day_of_month: int | None  # For monthly
    time: time  # Preferred time
    end_date: date | None  # When to stop recurring
    occurrences: int | None  # Or max number of occurrences
```

**Use Cases:**
- Weekly training classes (every Tuesday at 6 PM)
- Monthly grooming (first Saturday of month)
- Biweekly dog walking (every other Wednesday)

**Implementation:**
1. Create parent "recurring series" record
2. Generate child appointments for next 3-6 months
3. Link child appointments to parent series
4. When editing:
   - "This instance only" - edit single appointment
   - "This and future" - edit pattern, regenerate future appointments
   - "All instances" - edit pattern, update all appointments

---

### US-030: Add time slot suggestion algorithm

**Acceptance Criteria:**
- ✅ Return next 5 available time slots
- ✅ Consider staff/resource availability, buffers, constraints
- ✅ Optimize for minimal wait time
- ✅ Support preferences (morning vs afternoon, specific staff)
- ✅ Performance: <300ms

**Algorithm:**
```python
def suggest_available_times(
    service_id,
    pet_id,
    preferences={},
    limit=5
):
    # Start with next business day (or today if early enough)
    search_date = get_next_search_date()
    suggestions = []

    # Search up to 14 days ahead
    for day_offset in range(14):
        date = search_date + timedelta(days=day_offset)

        # Get business hours for this day
        hours = get_business_hours(date)

        # Generate time slots (e.g., every 30 minutes)
        for time_slot in generate_time_slots(hours, interval=30):
            # Check availability
            result = check_availability({
                "service_id": service_id,
                "pet_id": pet_id,
                "start_time": datetime.combine(date, time_slot),
                "staff_id": preferences.get("staff_id"),
                "resource_id": preferences.get("resource_id")
            })

            if result.is_available:
                suggestions.append(result)

                if len(suggestions) >= limit:
                    return suggestions

    return suggestions
```

**Preference Weighting:**
- Preferred staff: +10 points
- Preferred time of day: +5 points
- Earlier date: +3 points
- Sort suggestions by total score

---

## Daily Progress

*(To be filled in during sprint execution)*

---

## Sprint Metrics

### Planned vs Actual
- **Planned:** 7 high-priority stories + 4 medium-priority stories
- **Completed:** (TBD at sprint end)
- **Completion Rate:** (TBD)%

### Velocity
- **Previous Sprint:** (TBD from Sprint 1)
- **This Sprint:** (TBD) points
- **Trend:** (TBD)

---

## Wins & Learnings

*(To be completed at end of sprint)*

---

## Sprint Review Notes

*(To be completed at end of sprint)*

---

## Links & References

- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Scheduling Algorithm Doc: `technical/architecture/scheduling-engine.md` (to be created)
- Multi-Tenant Architecture: `technical/multi-tenant-architecture.md`

---

## Sprint Success Criteria

Sprint 2 is successful if:
- ✅ Zero double-bookings possible (verified with stress tests)
- ✅ All constraint types enforced (staff, resource, pet, buffer)
- ✅ Multi-pet appointments working
- ✅ Reschedule logic functional
- ✅ Calendar view API performant (<500ms)
- ✅ Comprehensive test coverage (90%+ for scheduling logic)
- ✅ Ready for Sprint 3 (booking widget integration)
- ✅ **Most importantly:** The scheduling engine is our competitive moat - it must be rock solid
