# Sprint 3 - Booking & Payments

**Sprint Duration:** Week 5-6 (February 3-14, 2025)
**Sprint Goal:** Build owner-facing booking widget, Stripe payment integration, and SMS reminder system
**Status:** Planning

---

## Sprint Goal

Enable pet owners to self-book appointments and implement payment processing:
1. **Mobile booking widget** - Responsive, mobile-first booking interface for pet owners
2. **Stripe integration** - Deposits, tips, packages, card-on-file
3. **SMS reminder system** - Automated confirmations and reminders via Twilio
4. **Family accounts** - Multiple pets per owner with shared booking flow
5. **Public booking page** - Each tenant gets public booking link

Success means owners can book online without phone calls, payments are processed securely, and automated reminders reduce no-shows.

---

## Sprint Capacity

**Available Days:** 10 working days
**Capacity:** ~60-70 hours
**Dependencies:** Sprint 2 scheduling engine must be complete

---

## Sprint Backlog

### High Priority (Must Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-040 | Create public booking widget UI (mobile-first) | L | Chris | 📋 Todo |
| US-041 | Integrate booking widget with scheduling engine | M | Chris | 📋 Todo |
| US-042 | Set up Stripe account and API integration | M | Chris | 📋 Todo |
| US-043 | Implement deposit payment flow | L | Chris | 📋 Todo |
| US-044 | Build card-on-file system | M | Chris | 📋 Todo |
| US-045 | Set up Twilio account and SMS sending | M | Chris | 📋 Todo |
| US-046 | Implement automated SMS confirmation system | M | Chris | 📋 Todo |
| US-047 | Build 24hr and 2hr reminder scheduling | M | Chris | 📋 Todo |

### Medium Priority (Should Complete)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-048 | Create family account multi-pet selection | M | Chris | 📋 Todo |
| US-049 | Implement package/punch card purchasing | M | Chris | 📋 Todo |
| US-050 | Build tip processing (post-appointment) | S | Chris | 📋 Todo |
| US-051 | Create booking confirmation email (fallback) | S | Chris | 📋 Todo |

### Low Priority (Nice to Have)

| Story | Description | Estimate | Assignee | Status |
|-------|-------------|----------|----------|--------|
| US-052 | Add gift card purchasing and redemption | M | Chris | 📋 Todo |
| US-053 | Build promo code system | S | Chris | 📋 Todo |

---

## Detailed Story Breakdown

### US-040: Create public booking widget UI

**Acceptance Criteria:**
- ✅ Mobile-responsive design (mobile-first approach)
- ✅ Step-by-step flow: Service → Pet → Date/Time → Payment
- ✅ Real-time availability display
- ✅ Staff preference option (or auto-assign)
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Loading states and error handling

**Booking Flow:**
1. Select service (grooming, training, etc.)
2. Select/create pet profile (name, breed, weight)
3. Choose date and time from available slots
4. Optional: Prefer specific staff member
5. Review booking details
6. Enter payment info (deposit)
7. Confirmation screen with SMS sent

**UI Components:**
- Service selector (grid/list with images)
- Calendar date picker
- Time slot picker (shows available times only)
- Pet selector (existing pets + "Add new pet")
- Payment form (Stripe Elements)
- Confirmation screen with QR code

---

### US-042: Set up Stripe account and API integration

**Acceptance Criteria:**
- ✅ Stripe account created (test mode)
- ✅ API keys configured in environment
- ✅ Stripe SDK integrated (backend)
- ✅ Payment Intent API working
- ✅ Webhook endpoint for payment events
- ✅ Test payments successful

**Stripe Setup:**
- Create Stripe Connect account (for multi-tenant)
- Each tenant gets Stripe Connect sub-account
- Platform fee structure: 2% + Stripe fees
- Webhook events: payment_intent.succeeded, payment_intent.failed, charge.refunded

**Security:**
- Never store card details (use Stripe tokens)
- PCI DSS compliance via Stripe
- HTTPS required for all payment pages

---

### US-043: Implement deposit payment flow

**Acceptance Criteria:**
- ✅ Configurable deposit amount per service (fixed or percentage)
- ✅ Deposit collected at booking time
- ✅ Remaining balance charged after appointment
- ✅ Refund logic for cancellations (based on policy)
- ✅ Payment records linked to appointments

**Deposit Rules:**
- Service-level config: deposit_type ("fixed" | "percentage"), deposit_amount
- Example: $20 fixed deposit for grooming, or 50% of service price
- Deposit is non-refundable if cancelled within 24 hours
- Full refund if cancelled >24 hours before

**Stripe Flow:**
```
1. Create PaymentIntent for deposit amount
2. Client confirms payment with Stripe Elements
3. On success:
   - Create appointment
   - Store payment_intent_id
   - Send SMS confirmation
4. After appointment completion:
   - Calculate remaining balance
   - Charge card on file
   - Send receipt
```

---

### US-044: Build card-on-file system

**Acceptance Criteria:**
- ✅ Stripe Customer created for each pet owner
- ✅ Save payment method to customer
- ✅ Set default payment method
- ✅ Ability to update/remove cards
- ✅ Charge card without re-entering details

**Implementation:**
- On first booking: create Stripe Customer, attach PaymentMethod
- Store stripe_customer_id on Owner record
- For future bookings: use saved PaymentMethod
- For no-show fees: charge default PaymentMethod automatically

---

### US-045 & US-046: Twilio SMS system

**Acceptance Criteria:**
- ✅ Twilio account created and configured
- ✅ A2P/10DLC registration started (required for reliable delivery)
- ✅ SMS sending service implemented
- ✅ Delivery status tracking (webhooks)
- ✅ Opt-in/opt-out management
- ✅ SMS rate limiting (prevent spam)

**SMS Templates:**
1. **Booking Confirmation:** "Hi {owner_name}, {pet_name}'s {service} is confirmed for {date} at {time} with {staff_name}. Reply HELP for support."
2. **24hr Reminder:** "{pet_name}'s grooming is tomorrow at {time}. Reply C to confirm or R to reschedule."
3. **2hr Reminder:** "{pet_name}'s appointment is in 2 hours at {time}. See you soon!"
4. **Late Running:** "Running 15 minutes late for {pet_name}'s appointment. Thanks for your patience!"
5. **Completion:** "{pet_name} is ready for pickup! Total: ${amount}. Photos attached."

**Compliance:**
- A2P/10DLC registration (required for US carriers)
- Template pre-approval with carriers
- Opt-in checkbox on booking form
- STOP/UNSUBSCRIBE handling
- TCPA compliance (no marketing without consent)

---

### US-047: Build reminder scheduling system

**Acceptance Criteria:**
- ✅ Background job scheduler (Celery or similar)
- ✅ 24-hour reminder queued at booking time
- ✅ 2-hour reminder queued at booking time
- ✅ Skip reminders if appointment cancelled
- ✅ Retry logic for failed SMS delivery

**Scheduler Implementation:**
- Use Celery with Redis for task queue
- Schedule tasks at booking time:
  - Task 1: send_reminder at appointment_time - 24 hours
  - Task 2: send_reminder at appointment_time - 2 hours
- Cancel tasks if appointment rescheduled or cancelled
- Track delivery status and retry failed sends

---

### US-048: Create family account multi-pet selection

**Acceptance Criteria:**
- ✅ Owner can select multiple pets in one booking flow
- ✅ Different services for different pets (if allowed)
- ✅ Combined or separate time slots (based on service)
- ✅ Single payment for all pets
- ✅ Discount logic for multiple pets

**Multi-Pet Booking:**
- "Book for multiple pets" checkbox
- Select pets from family account
- Option 1: Same service, same time (book together)
- Option 2: Same service, sequential times (book back-to-back)
- Apply multi-pet discount if configured

---

## Technical Debt / Maintenance

- [ ] A2P/10DLC registration with carriers (can take 1-2 weeks)
- [ ] Stripe webhook signature verification
- [ ] Payment error handling and retry logic
- [ ] SMS delivery monitoring and alerts
- [ ] PCI compliance documentation

---

## Sprint Success Criteria

Sprint 3 is successful if:
- ✅ Public booking widget is live and mobile-friendly
- ✅ Owners can book appointments end-to-end without assistance
- ✅ Stripe payments processing correctly (test mode)
- ✅ SMS confirmations sending reliably
- ✅ 24hr and 2hr reminders working
- ✅ Zero payment data stored locally (PCI compliant)
- ✅ A2P/10DLC registration submitted (approval pending)
- ✅ Ready for Sprint 4 (vaccination system)

---

## Links & References

- Roadmap: `product/roadmap/2025-Q1-roadmap.md`
- Stripe API Docs: https://stripe.com/docs/api
- Twilio SMS Docs: https://www.twilio.com/docs/sms
- A2P/10DLC Guide: https://www.twilio.com/docs/sms/a2p-10dlc
