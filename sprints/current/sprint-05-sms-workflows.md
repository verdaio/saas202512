# Sprint 5 - SMS Workflows

**Sprint Duration:** Week 9-10 (March 3-14, 2025)
**Sprint Goal:** Build two-way SMS communication system with quick actions and templates
**Status:** Planning

---

## Sprint Goal

Complete the SMS-first workflow vision:
1. **Two-way SMS inbox** - Receive and respond to owner messages
2. **Quick actions** - Two-tap reschedule, confirm, cancel via SMS replies
3. **SMS templates** - Pre-built responses for common scenarios
4. **Conversation management** - Thread messages by owner, searchable history
5. **Late-running alerts** - Proactive communication when running behind

This sprint delivers our core differentiator: truly SMS-first operations that reduce phone calls and improve customer experience.

---

## Sprint Capacity

**Available Days:** 10 working days
**Capacity:** ~60-70 hours
**Dependencies:** Sprint 3 (SMS sending) must be complete

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-080 | Build inbound SMS webhook handler (Twilio) | M | Chris | 📋 Todo |
| US-081 | Create SMS conversation model and storage | M | Chris | 📋 Todo |
| US-082 | Build SMS inbox UI (staff view) | L | Chris | 📋 Todo |
| US-083 | Implement two-tap reschedule workflow | L | Chris | 📋 Todo |
| US-084 | Create SMS template system | M | Chris | 📋 Todo |
| US-085 | Build quick action parser (keyword detection) | M | Chris | 📋 Todo |
| US-086 | Implement late-running alert system | M | Chris | 📋 Todo |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-087 | Add SMS conversation search and filtering | M | Chris | 📋 Todo |
| US-088 | Build automated FAQ responder | M | Chris | 📋 Todo |
| US-089 | Create staff assignment for conversations | S | Chris | 📋 Todo |
| US-090 | Implement SMS conversation notes | S | Chris | 📋 Todo |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-091 | Build SMS analytics dashboard | S | Chris | 📋 Todo |
| US-092 | Add MMS support (send photos) | M | Chris | 📋 Todo |

---

## Detailed Story Breakdown

### US-080: Build inbound SMS webhook handler

**Acceptance Criteria:**
- ✅ Twilio webhook endpoint configured
- ✅ Signature verification for security
- ✅ Parse inbound message (from, to, body, timestamp)
- ✅ Link message to owner/pet by phone number
- ✅ Store message in conversation thread
- ✅ Auto-respond to keywords (STOP, HELP, etc.)

**Webhook Flow:**
```python
@app.post("/webhooks/twilio/sms/inbound")
def handle_inbound_sms(request):
    # Verify Twilio signature
    if not verify_twilio_signature(request):
        return 403

    # Extract message data
    from_number = request.form["From"]
    to_number = request.form["To"]  # Tenant's Twilio number
    body = request.form["Body"]
    message_sid = request.form["MessageSid"]

    # Find tenant by Twilio number
    tenant = get_tenant_by_twilio_number(to_number)

    # Find owner by phone number
    owner = get_owner_by_phone(from_number, tenant.id)

    # Create conversation message
    message = ConversationMessage.create(
        tenant_id=tenant.id,
        owner_id=owner.id if owner else None,
        direction="inbound",
        from_number=from_number,
        to_number=to_number,
        body=body,
        message_sid=message_sid
    )

    # Process quick actions
    if owner:
        process_sms_quick_action(message, owner, tenant)

    # Auto-respond to keywords
    if body.upper() in ["STOP", "UNSUBSCRIBE"]:
        handle_opt_out(owner, from_number, tenant)
        return TwiML response: "You've been unsubscribed. Reply START to resubscribe."

    if body.upper() == "HELP":
        return TwiML response: "Reply C to confirm, R to reschedule, or call us at {phone}."

    return 200
```

---

### US-081: Create SMS conversation model

**Acceptance Criteria:**
- ✅ Database model for conversation messages
- ✅ Thread messages by owner
- ✅ Track direction (inbound/outbound)
- ✅ Link to appointments when applicable
- ✅ Mark messages as read/unread

**Conversation Message Model:**
```python
class ConversationMessage:
    id: UUID
    tenant_id: UUID
    owner_id: UUID | None  # Null if phone number not matched
    from_number: str  # E.164 format
    to_number: str
    direction: "inbound" | "outbound"
    body: text
    message_sid: str  # Twilio message ID
    status: "queued" | "sent" | "delivered" | "failed"
    is_read: bool
    read_at: datetime | None
    read_by: UUID | None  # Staff member who read it
    appointment_id: UUID | None  # If related to appointment
    created_at: datetime

class Conversation:
    id: UUID
    tenant_id: UUID
    owner_id: UUID
    phone_number: str
    last_message_at: datetime
    unread_count: int
    assigned_to: UUID | None  # Staff assigned to conversation
    status: "open" | "closed"
```

---

### US-082: Build SMS inbox UI

**Acceptance Criteria:**
- ✅ Conversation list view (sidebar)
- ✅ Message thread view (main panel)
- ✅ Unread count badges
- ✅ Real-time updates (WebSocket or polling)
- ✅ Send reply functionality
- ✅ Template insertion
- ✅ Mobile-responsive

**Inbox Features:**
- **Left Panel:** List of conversations sorted by last_message_at
  - Owner name + pet(s)
  - Last message preview
  - Unread badge
  - Time ago
- **Right Panel:** Selected conversation thread
  - Messages in chronological order
  - Inbound (left-aligned, gray)
  - Outbound (right-aligned, blue)
  - Timestamp on each message
  - Appointment context if applicable
- **Bottom:** Reply composer
  - Text area
  - Template dropdown
  - Send button
  - Character count (160 chars = 1 SMS)

**Real-Time Updates:**
- Use WebSocket for instant message delivery
- Fallback to polling every 10 seconds if WebSocket fails

---

### US-083: Implement two-tap reschedule workflow

**Acceptance Criteria:**
- ✅ Send reschedule SMS with 2-3 time slot options
- ✅ Parse owner's reply (1, 2, or 3)
- ✅ Automatically reschedule appointment
- ✅ Send confirmation SMS
- ✅ Handle edge cases (slot no longer available)

**Two-Tap Reschedule Flow:**

**Step 1:** Owner requests reschedule (replies "R" to reminder)
```python
# System detects "R" keyword
appointment = get_upcoming_appointment(owner)

# Find next 3 available slots
suggestions = suggest_available_times(
    service_id=appointment.service_id,
    pet_id=appointment.pet_id,
    limit=3
)

# Send options SMS
send_sms(owner.phone, f"""
Thanks for rescheduling {pet.name}'s {service.name}.

Reply with:
1 for {suggestions[0].format("Tomorrow at 2 PM")}
2 for {suggestions[1].format("Wednesday at 10 AM")}
3 for {suggestions[2].format("Friday at 3 PM")}

Or call us for other times.
""")

# Store pending reschedule in session/cache
cache.set(f"reschedule:{owner.id}", {
    "appointment_id": appointment.id,
    "suggestions": suggestions,
    "expires_at": now() + timedelta(hours=2)
})
```

**Step 2:** Owner replies with choice (1, 2, or 3)
```python
# Parse reply
if body in ["1", "2", "3"]:
    choice = int(body) - 1
    pending = cache.get(f"reschedule:{owner.id}")

    if not pending or pending["expires_at"] < now():
        send_sms(owner.phone, "Sorry, that reschedule request expired. Reply R to try again.")
        return

    # Get chosen slot
    new_slot = pending["suggestions"][choice]

    # Attempt reschedule
    try:
        reschedule_appointment(pending["appointment_id"], new_slot)
        send_sms(owner.phone, f"✅ Rescheduled to {new_slot.format()}! See you then.")
    except SlotNoLongerAvailable:
        send_sms(owner.phone, "Sorry, that slot was just booked. Reply R to see new options.")

    # Clear cache
    cache.delete(f"reschedule:{owner.id}")
```

---

### US-084: Create SMS template system

**Acceptance Criteria:**
- ✅ Template model with variables
- ✅ Template library (common responses)
- ✅ Variable replacement (owner_name, pet_name, date, etc.)
- ✅ Template management UI (create, edit, delete)
- ✅ Templates organized by category

**SMS Templates:**

**1. Confirmation:**
- "We've confirmed {pet_name}'s {service} for {date} at {time}. See you then!"

**2. Running Late:**
- "Hi {owner_name}, we're running about {minutes} minutes late for {pet_name}'s appointment. Thanks for your patience!"

**3. Ready for Pickup:**
- "{pet_name} is all done and ready for pickup! Total is ${amount}. We'll see you soon."

**4. Reschedule Options:**
- "We have openings on {date1} at {time1}, {date2} at {time2}, or {date3} at {time3}. Reply 1, 2, or 3 to book."

**5. Vaccination Reminder:**
- "{pet_name}'s {vax_type} vaccination expires in {days} days. Please upload an updated vax card at {url}."

**6. Thank You:**
- "Thanks for bringing {pet_name} in today! We hope to see you again soon. Reply REVIEW to leave us a review!"

**Template Model:**
```python
class SMSTemplate:
    id: UUID
    tenant_id: UUID
    name: str
    category: "confirmation" | "reminder" | "running_late" | "general"
    body_template: text  # With {variables}
    variables: list[str]  # ["pet_name", "date", "time"]
    is_active: bool
    created_by: UUID
    created_at: datetime
```

---

### US-085: Build quick action parser

**Acceptance Criteria:**
- ✅ Detect keywords in inbound messages (C, R, HELP, STOP)
- ✅ Case-insensitive matching
- ✅ Fuzzy matching (e.g., "confirm" matches "C")
- ✅ Context-aware responses
- ✅ Fall back to staff inbox if no match

**Quick Action Keywords:**

| Keyword | Action | Response |
|---------|--------|----------|
| C, CONFIRM, YES | Confirm upcoming appointment | "Thanks! {pet_name}'s appointment is confirmed for {date} at {time}." |
| R, RESCHEDULE | Start reschedule flow | Send 3 time slot options |
| CANCEL | Cancel appointment | Check policy, charge fee if applicable, send confirmation |
| HELP, INFO | Send help message | "Reply C to confirm, R to reschedule, or call {phone}." |
| STOP, UNSUBSCRIBE | Opt out of SMS | "You've unsubscribed. Reply START to resume messages." |
| START, SUBSCRIBE | Opt back in | "Welcome back! You'll now receive appointment reminders." |

**Parser Logic:**
```python
def parse_quick_action(message_body, owner, tenant):
    body = message_body.strip().upper()

    # Check for exact or fuzzy match
    if body in ["C", "CONFIRM", "YES", "OK"]:
        return handle_confirm(owner, tenant)

    if body in ["R", "RESCHEDULE", "CHANGE"]:
        return handle_reschedule_start(owner, tenant)

    if body in ["CANCEL", "NEVERMIND"]:
        return handle_cancel_request(owner, tenant)

    if body in ["HELP", "INFO", "?"]:
        return send_help_message(owner, tenant)

    if body in ["STOP", "UNSUBSCRIBE", "QUIT"]:
        return handle_opt_out(owner, tenant)

    if body in ["START", "SUBSCRIBE", "RESUME"]:
        return handle_opt_in(owner, tenant)

    # No match - route to staff inbox
    return route_to_staff_inbox(message, owner, tenant)
```

---

### US-086: Implement late-running alert system

**Acceptance Criteria:**
- ✅ Staff can trigger "running late" alert
- ✅ Specify delay time (15, 30, 45 minutes)
- ✅ Send SMS to upcoming appointments
- ✅ Update appointment status to "delayed"
- ✅ One-click button in ops dashboard

**Late Alert Flow:**

**Scenario:** Groomer running 20 minutes behind schedule

**Step 1:** Staff clicks "Send Late Alert" in dashboard
- Select delay amount: 15, 20, 30, 45 minutes
- Select which appointments to notify (next 1-3 appointments)

**Step 2:** System sends SMS to affected owners
```
Hi {owner_name}, we're running about {delay_minutes} minutes late for {pet_name}'s {time} appointment.

We apologize for the delay and will be ready for you at {new_time}. Thanks for your patience!
```

**Step 3:** Update appointment records
- Set status to "delayed"
- Log delay in appointment notes
- Optionally adjust scheduled_start (if rebooking whole day)

**Dashboard UI:**
- Big orange button: "Running Late?"
- Shows next 3 appointments
- Checkboxes to select which to notify
- Delay slider (5-60 minutes)
- Preview SMS before sending
- Send button

---

### US-087: SMS conversation search

**Acceptance Criteria:**
- ✅ Search by owner name, pet name, phone number
- ✅ Search message content (full-text search)
- ✅ Filter by date range
- ✅ Filter by read/unread
- ✅ Filter by assigned staff

---

### US-088: Automated FAQ responder

**Acceptance Criteria:**
- ✅ Detect common questions (hours, address, services, pricing)
- ✅ Auto-respond with configured answers
- ✅ Fallback to staff inbox if no match

**FAQ Triggers:**

| Owner Message | Auto Response |
|---------------|---------------|
| "hours", "open", "when" | "We're open Mon-Fri 8am-6pm, Sat 9am-4pm. Closed Sunday. Book online: {url}" |
| "address", "where", "location" | "We're at {address}. Map: {google_maps_url}" |
| "price", "cost", "how much" | "Full groom is ${price}. See all services: {url}" |
| "services", "what do you offer" | "We offer grooming, training, and daycare. Details: {url}" |

---

## Sprint Success Criteria

Sprint 5 is successful if:
- ✅ Two-way SMS fully functional
- ✅ Staff can receive and respond to owner messages
- ✅ Two-tap reschedule working (>70% success rate)
- ✅ SMS templates library complete
- ✅ Quick actions parsing accurately
- ✅ Late-running alerts tested with real scenarios
- ✅ Zero missed inbound messages (webhook reliability 99.9%+)
- ✅ Inbox UI intuitive and fast
- ✅ Ready for Sprint 6 (ops tools)

---

## Links & References

- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Twilio SMS Docs: https://www.twilio.com/docs/sms/tutorials/how-to-receive-and-reply
- Twilio TwiML: https://www.twilio.com/docs/sms/twiml
