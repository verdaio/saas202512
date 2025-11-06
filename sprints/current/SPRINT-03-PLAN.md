# Sprint 3 Plan: Booking & Payments

**Sprint**: 3 of 6
**Status**: In Progress
**Start Date**: 2025-11-05
**Estimated Duration**: 50-60 hours

---

## 🎯 Sprint Goals

**Primary Objective**: Enable end-to-end online booking with payment processing and automated notifications.

**Key Deliverables**:
1. Stripe payment integration for deposits and full payments
2. Twilio SMS notifications for appointment lifecycle
3. Next.js booking widget for customer self-service
4. Webhook handling for payment events
5. Notification templates and delivery tracking

---

## 📋 User Stories

### Payment Processing

**US-3.1**: As a customer, I want to pay a deposit online so that I can secure my appointment
- Acceptance: Customer can pay deposit via Stripe
- Acceptance: Payment status tracked in appointment record
- Acceptance: Failed payments prevent booking confirmation

**US-3.2**: As a business owner, I want to process refunds so that I can handle cancellations
- Acceptance: Full and partial refunds supported
- Acceptance: Refund status tracked
- Acceptance: Refund webhooks update appointment

**US-3.3**: As a system, I want to handle payment webhooks so that appointment status stays in sync
- Acceptance: Payment success confirms appointment
- Acceptance: Payment failure notifies customer
- Acceptance: Webhook signature verification for security

### SMS Notifications

**US-3.4**: As a customer, I want to receive SMS confirmation so that I know my booking is successful
- Acceptance: SMS sent immediately after booking
- Acceptance: Includes appointment details
- Acceptance: Only sent if customer opted in

**US-3.5**: As a customer, I want to receive appointment reminders so that I don't forget
- Acceptance: 24-hour reminder sent
- Acceptance: 2-hour reminder sent
- Acceptance: Includes appointment details and cancellation link

**US-3.6**: As a customer, I want to receive cancellation confirmation so that I know it was processed
- Acceptance: SMS sent immediately after cancellation
- Acceptance: Includes refund information if applicable

### Booking Widget

**US-3.7**: As a customer, I want to browse available services so that I can choose what I need
- Acceptance: Services displayed with pricing and duration
- Acceptance: Filter by category (grooming, training, etc.)
- Acceptance: Service details clearly shown

**US-3.8**: As a customer, I want to select a date and time so that I can book when convenient
- Acceptance: Calendar shows available dates
- Acceptance: Time slots shown for selected date
- Acceptance: Only available slots displayed
- Acceptance: Real-time availability checking

**US-3.9**: As a customer, I want to enter my pet's information so that staff are prepared
- Acceptance: Owner contact info collected
- Acceptance: Pet details collected (name, breed, age)
- Acceptance: Vaccination status captured
- Acceptance: Special instructions field available

**US-3.10**: As a customer, I want to pay securely online so that my appointment is confirmed
- Acceptance: Stripe payment form integrated
- Acceptance: Payment processed before confirmation
- Acceptance: Confirmation screen shows booking details
- Acceptance: Confirmation email/SMS sent

---

## 🏗️ Technical Architecture

### Backend Components

```
api/
├── src/
│   ├── integrations/
│   │   ├── stripe_service.py        # Stripe API wrapper
│   │   └── twilio_service.py        # Twilio SMS API wrapper
│   ├── services/
│   │   ├── payment_service.py       # Enhanced with Stripe
│   │   └── notification_service.py  # SMS notification logic
│   └── api/
│       └── webhooks.py              # Enhanced with Stripe webhooks
```

### Frontend Components

```
web/
├── src/
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   └── book/
│   │       ├── page.tsx             # Booking flow entry
│   │       ├── services/            # Service selection
│   │       ├── datetime/            # Date/time picker
│   │       ├── details/             # Customer/pet info
│   │       ├── payment/             # Payment form
│   │       └── confirmation/        # Booking confirmation
│   ├── components/
│   │   ├── ServiceCard.tsx
│   │   ├── DateTimePicker.tsx
│   │   ├── PetForm.tsx
│   │   └── PaymentForm.tsx
│   └── lib/
│       ├── api-client.ts            # API wrapper
│       └── stripe.ts                # Stripe client setup
```

---

## 🔧 Implementation Tasks

### Phase 1: Stripe Integration (15-20 hours)

#### 1.1 Stripe Service (`api/src/integrations/stripe_service.py`)

**Methods to implement**:
- `create_payment_intent()` - Create payment for deposit/full amount
- `confirm_payment_intent()` - Confirm payment
- `create_customer()` - Create Stripe customer record
- `attach_payment_method()` - Save payment method
- `create_refund()` - Process refund
- `verify_webhook_signature()` - Webhook security

**Configuration**:
- Stripe API keys (test and production)
- Webhook secret
- Currency settings (USD)
- Payment method types (card)

**Error Handling**:
- Invalid card errors
- Insufficient funds
- Network failures
- Webhook verification failures

#### 1.2 Webhook Handlers (`api/src/api/webhooks.py`)

**Events to handle**:
- `payment_intent.succeeded` - Confirm appointment
- `payment_intent.payment_failed` - Notify customer
- `charge.refunded` - Update appointment status
- `customer.updated` - Sync customer data

**Security**:
- Signature verification
- Idempotency handling
- Event deduplication

#### 1.3 Payment Service Updates (`api/src/services/payment_service.py`)

**Enhancements**:
- Integrate Stripe payment intent creation
- Store Stripe payment ID
- Handle payment status updates
- Process refunds via Stripe

---

### Phase 2: SMS Notifications (10-15 hours)

#### 2.1 Twilio Service (`api/src/integrations/twilio_service.py`)

**Methods to implement**:
- `send_sms()` - Send SMS with error handling
- `validate_phone_number()` - Format validation
- `check_opt_in_status()` - Verify customer consent
- `get_delivery_status()` - Check SMS delivery

**Configuration**:
- Twilio account SID
- Auth token
- From phone number
- Messaging service SID (optional)

#### 2.2 Notification Service (`api/src/services/notification_service.py`)

**Templates to create**:
```python
TEMPLATES = {
    "booking_confirmation": """
        Hi {customer_name}! Your {service_name} appointment is confirmed for {date} at {time}.
        Location: {business_address}
        Cancel: {cancellation_link}
    """,

    "reminder_24h": """
        Reminder: {service_name} appointment tomorrow at {time}.
        Location: {business_address}
        Need to cancel? {cancellation_link}
    """,

    "reminder_2h": """
        Your {service_name} appointment starts in 2 hours at {time}.
        Location: {business_address}
    """,

    "cancellation": """
        Your appointment for {date} at {time} has been cancelled.
        {refund_info}
    """
}
```

**Methods to implement**:
- `send_booking_confirmation()` - Send confirmation SMS
- `send_reminder()` - Send reminder SMS
- `send_cancellation()` - Send cancellation SMS
- `render_template()` - Template rendering with data
- `schedule_reminders()` - Queue reminder jobs

**Opt-in Management**:
- Check customer SMS opt-in status
- Track delivery success/failure
- Handle opt-out requests

---

### Phase 3: Frontend Development (25-30 hours)

#### 3.1 Project Setup

**Technology Stack**:
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React Hook Form
- Zod validation
- Stripe.js

**Installation**:
```bash
cd web
npx create-next-app@latest . --typescript --tailwind --app
npm install @stripe/stripe-js @stripe/react-stripe-js
npm install react-hook-form zod @hookform/resolvers
npm install date-fns lucide-react
npm install -D @types/node
```

#### 3.2 API Client (`web/src/lib/api-client.ts`)

**Endpoints to wrap**:
- GET `/services` - List services
- GET `/schedule/available-slots` - Get time slots
- POST `/owners` - Create owner
- POST `/pets` - Create pet
- POST `/appointments` - Create appointment
- POST `/payments` - Process payment

**Features**:
- TypeScript types for all requests/responses
- Error handling with user-friendly messages
- Loading states
- Retry logic for failed requests

#### 3.3 Booking Flow Components

**Page 1: Service Selection** (`web/src/app/book/services/page.tsx`)
- Display all available services
- Show pricing, duration, description
- Filter by category
- "Select" button to next step

**Page 2: Date & Time** (`web/src/app/book/datetime/page.tsx`)
- Calendar component for date selection
- Time slot grid for selected date
- Real-time availability checking
- Staff selection (optional)
- "Next" button to proceed

**Page 3: Customer & Pet Details** (`web/src/app/book/details/page.tsx`)
- Owner information form
  - Name, email, phone
  - SMS opt-in checkbox
- Pet information form
  - Pet name, breed, age
  - Vaccination status
  - Special instructions
- "Next" to payment

**Page 4: Payment** (`web/src/app/book/payment/page.tsx`)
- Booking summary
- Deposit amount display
- Stripe payment element
- Terms and conditions
- "Pay & Confirm" button

**Page 5: Confirmation** (`web/src/app/book/confirmation/page.tsx`)
- Success message
- Appointment details
- Receipt/invoice
- Calendar add button
- "Book Another" button

#### 3.4 UI Components

**ServiceCard** (`web/src/components/ServiceCard.tsx`)
- Service image
- Name, description
- Duration and price
- Select button

**DateTimePicker** (`web/src/components/DateTimePicker.tsx`)
- Calendar grid
- Time slot buttons
- Loading states for availability
- Selected date/time display

**PetForm** (`web/src/components/PetForm.tsx`)
- Form fields with validation
- Vaccination status selector
- Special instructions textarea

**PaymentForm** (`web/src/components/PaymentForm.tsx`)
- Stripe Elements integration
- Card input with validation
- Submit button with loading state
- Error message display

---

## 📊 Data Models

### Payment Record (Enhanced)

```python
class Payment:
    # Existing fields
    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    amount: int  # cents
    status: PaymentStatus  # pending, completed, failed, refunded

    # New Stripe fields
    stripe_payment_intent_id: str
    stripe_customer_id: str
    stripe_payment_method_id: str
    stripe_charge_id: str
    stripe_refund_id: str

    # Metadata
    payment_method_type: str  # card, etc.
    last_4: str
    card_brand: str
    refund_amount: int  # cents
    refund_reason: str
```

### SMS Log (New)

```python
class SMSLog:
    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    owner_id: UUID

    # Message details
    phone_number: str
    message_type: str  # confirmation, reminder_24h, reminder_2h, cancellation
    message_body: str

    # Delivery tracking
    twilio_sid: str
    status: str  # queued, sent, delivered, failed
    sent_at: datetime
    delivered_at: datetime
    error_message: str

    created_at: datetime
```

---

## 🔐 Security Considerations

### Stripe Security
- ✅ Never expose secret API keys to frontend
- ✅ Use Stripe.js for PCI compliance (no card data touches server)
- ✅ Verify webhook signatures
- ✅ Use idempotency keys for payment operations
- ✅ Store only last 4 digits of card
- ✅ Use Stripe test mode for development

### SMS Security
- ✅ Verify customer consent before sending SMS
- ✅ Include opt-out instructions
- ✅ Rate limit SMS sending
- ✅ Validate phone numbers
- ✅ Don't include sensitive data in SMS
- ✅ Secure Twilio credentials

### Frontend Security
- ✅ Validate all inputs
- ✅ Sanitize user data
- ✅ Use HTTPS only
- ✅ CORS configuration
- ✅ Rate limiting on booking endpoint
- ✅ CAPTCHA for bot prevention (optional)

---

## 🧪 Testing Strategy

### Unit Tests

**Payment Service Tests**:
- Payment intent creation
- Refund processing
- Webhook signature verification
- Error handling

**Notification Service Tests**:
- Template rendering
- Opt-in checking
- SMS sending
- Delivery tracking

### Integration Tests

**Payment Flow Tests**:
1. Create appointment → Payment intent → Confirm payment → Appointment confirmed
2. Payment failure → Appointment remains pending
3. Refund → Appointment cancelled → Customer notified

**Booking Flow Tests**:
1. Select service → Choose time → Enter details → Pay → Confirm
2. Failed payment → Return to payment step
3. Expired time slot → Show error, return to selection

### End-to-End Tests

**Complete User Journey**:
1. Customer visits booking page
2. Selects grooming service
3. Chooses next available slot
4. Enters contact and pet info
5. Pays deposit with test card
6. Receives confirmation SMS
7. Receives 24h reminder
8. Receives 2h reminder

---

## 📁 File Structure

```
api/
├── src/
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── stripe_service.py        # NEW - 400 lines
│   │   └── twilio_service.py        # NEW - 300 lines
│   ├── services/
│   │   ├── payment_service.py       # ENHANCED - +200 lines
│   │   └── notification_service.py  # NEW - 400 lines
│   ├── api/
│   │   └── webhooks.py              # ENHANCED - +200 lines
│   └── models/
│       └── sms_log.py               # NEW - 50 lines
├── tests/
│   ├── test_stripe.py               # NEW - 300 lines
│   ├── test_twilio.py               # NEW - 200 lines
│   └── test_notification.py         # NEW - 250 lines

web/
├── src/
│   ├── app/
│   │   ├── layout.tsx               # NEW - 100 lines
│   │   ├── page.tsx                 # NEW - 150 lines
│   │   └── book/
│   │       ├── layout.tsx           # NEW - 50 lines
│   │       ├── services/
│   │       │   └── page.tsx         # NEW - 200 lines
│   │       ├── datetime/
│   │       │   └── page.tsx         # NEW - 250 lines
│   │       ├── details/
│   │       │   └── page.tsx         # NEW - 300 lines
│   │       ├── payment/
│   │       │   └── page.tsx         # NEW - 250 lines
│   │       └── confirmation/
│   │           └── page.tsx         # NEW - 150 lines
│   ├── components/
│   │   ├── ServiceCard.tsx          # NEW - 100 lines
│   │   ├── DateTimePicker.tsx       # NEW - 200 lines
│   │   ├── PetForm.tsx              # NEW - 150 lines
│   │   ├── PaymentForm.tsx          # NEW - 150 lines
│   │   └── BookingSummary.tsx       # NEW - 100 lines
│   └── lib/
│       ├── api-client.ts            # NEW - 300 lines
│       ├── stripe.ts                # NEW - 50 lines
│       ├── types.ts                 # NEW - 200 lines
│       └── utils.ts                 # NEW - 100 lines
├── public/
│   └── images/
├── package.json                     # NEW
├── tsconfig.json                    # NEW
├── tailwind.config.ts               # NEW
└── next.config.js                   # NEW

**Total Estimated**: ~5,000 lines across 35+ files
```

---

## 🎯 Success Criteria

### Must Have (P0)
- [x] Stripe payment intent creation working
- [x] Webhook handling for payment events
- [x] SMS confirmation sending
- [x] Basic booking widget (service → time → details → payment)
- [x] Payment form with Stripe Elements
- [x] Appointment creation with payment

### Should Have (P1)
- [x] SMS reminders (24h, 2h)
- [x] Refund processing
- [x] Responsive mobile UI
- [x] Loading states and error handling
- [x] Booking confirmation page

### Nice to Have (P2)
- [ ] Multiple payment methods
- [ ] Save payment method for future
- [ ] Email notifications (in addition to SMS)
- [ ] Customer portal for managing bookings
- [ ] Admin dashboard for viewing bookings

---

## 📈 Metrics to Track

**Payment Metrics**:
- Payment success rate
- Average payment processing time
- Refund rate
- Failed payment reasons

**SMS Metrics**:
- Delivery rate
- Opt-in rate
- Click-through rate on cancellation links
- Cost per SMS

**Booking Metrics**:
- Conversion rate (visitors → bookings)
- Drop-off by step
- Average time to complete booking
- Most popular services
- Most popular time slots

---

## 🚀 Deployment Plan

### Environment Configuration

**Backend (.env)**:
```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8012
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Deployment Steps

1. **Backend**:
   - Run database migrations for new models
   - Deploy updated API to Azure App Service
   - Configure webhook endpoint in Stripe dashboard
   - Test webhook delivery

2. **Frontend**:
   - Build production bundle
   - Deploy to Vercel
   - Configure environment variables
   - Test booking flow end-to-end

---

## 📝 Documentation Deliverables

- [x] Sprint 3 plan (this document)
- [ ] Stripe integration guide
- [ ] Twilio setup guide
- [ ] Frontend deployment guide
- [ ] API documentation updates
- [ ] Sprint 3 completion summary

---

**Status**: Ready to begin implementation
**Next Step**: Implement Stripe service

**Estimated Timeline**:
- Phase 1 (Stripe): 15-20 hours
- Phase 2 (SMS): 10-15 hours
- Phase 3 (Frontend): 25-30 hours
- **Total**: 50-65 hours
