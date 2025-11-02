# API Endpoints - Quick Reference

**Project:** Pet Care Scheduler (saas202512)
**Base URL:** http://localhost:8012/api/v1
**API Docs:** http://localhost:8012/docs (Swagger UI)

---

## Authentication

### POST /auth/register
Register new user account

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "tenant_id": "uuid"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "tenant_id": "uuid",
  "created_at": "2025-01-20T10:00:00Z"
}
```

---

### POST /auth/login
Authenticate and get JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### GET /auth/me
Get current user info

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "owner",
  "tenant_id": "uuid"
}
```

---

## Tenants

### POST /tenants
Create new tenant (business signup)

**Request:**
```json
{
  "subdomain": "happypaws",
  "business_name": "Happy Paws Grooming",
  "owner_email": "owner@happypaws.com",
  "owner_password": "SecurePass123"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "subdomain": "happypaws",
  "business_name": "Happy Paws Grooming",
  "plan": "starter",
  "status": "trial"
}
```

---

### GET /tenants/{id}
Get tenant details

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "subdomain": "happypaws",
  "business_name": "Happy Paws Grooming",
  "plan": "starter",
  "status": "active",
  "settings": {}
}
```

---

## Pets

### GET /pets
List all pets (tenant-scoped)

**Headers:** `Authorization: Bearer <token>`

**Query Params:**
- `owner_id` (optional): Filter by owner
- `is_active` (optional): true/false
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "owner_id": "uuid",
      "name": "Bella",
      "breed": "Golden Retriever",
      "age": 3,
      "weight": 65,
      "is_active": true
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

---

### POST /pets
Create new pet

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "owner_id": "uuid",
  "name": "Bella",
  "breed": "Golden Retriever",
  "age": 3,
  "weight": 65,
  "medical_notes": "Allergic to chicken",
  "behavioral_notes": "Friendly, loves treats"
}
```

**Response:** `201 Created`

---

### GET /pets/{id}
Get pet details

**Response:** `200 OK`

---

### PUT /pets/{id}
Update pet

**Request:** (same as POST, all fields optional)

**Response:** `200 OK`

---

### DELETE /pets/{id}
Soft delete pet

**Response:** `204 No Content`

---

## Owners

### GET /owners
List all owners (tenant-scoped)

**Response:** `200 OK` (paginated)

---

### POST /owners
Create new owner

**Request:**
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": {
    "street": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "zip": "78701"
  }
}
```

**Response:** `201 Created`

---

### GET /owners/{id}
Get owner details with pets

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "+1234567890",
  "pets": [
    {"id": "uuid", "name": "Bella", "breed": "Golden Retriever"}
  ]
}
```

---

## Services

### GET /services
List all services (tenant-scoped)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Full Groom",
      "duration_minutes": 90,
      "buffer_before_minutes": 10,
      "buffer_after_minutes": 15,
      "price": 7500,
      "requires_vaccination": true
    }
  ]
}
```

---

### POST /services
Create new service

**Request:**
```json
{
  "name": "Full Groom",
  "description": "Complete grooming service",
  "duration_minutes": 90,
  "buffer_before_minutes": 10,
  "buffer_after_minutes": 15,
  "price": 7500,
  "requires_vaccination": true,
  "required_vaccinations": ["rabies", "dhpp"]
}
```

**Response:** `201 Created`

---

## Appointments

### GET /appointments
List appointments (tenant-scoped)

**Query Params:**
- `start_date`: Filter by date range
- `end_date`: Filter by date range
- `staff_id`: Filter by staff
- `pet_id`: Filter by pet
- `status`: scheduled/confirmed/completed/cancelled/no_show

**Response:** `200 OK` (paginated)

---

### POST /appointments
Create new appointment (with availability check)

**Request:**
```json
{
  "pet_id": "uuid",
  "service_id": "uuid",
  "staff_id": "uuid",
  "resource_id": "uuid",
  "scheduled_start": "2025-01-20T10:00:00Z",
  "notes": "First visit"
}
```

**Response:** `201 Created` or `409 Conflict` (if double-booking detected)

---

### GET /appointments/{id}
Get appointment details

**Response:** `200 OK`

---

### PUT /appointments/{id}/reschedule
Reschedule appointment

**Request:**
```json
{
  "scheduled_start": "2025-01-21T14:00:00Z"
}
```

**Response:** `200 OK` or `409 Conflict`

---

### PUT /appointments/{id}/cancel
Cancel appointment (with fee calculation)

**Request:**
```json
{
  "reason": "Client requested cancellation"
}
```

**Response:** `200 OK`
```json
{
  "cancellation_fee": 2000,
  "deposit_refunded": false
}
```

---

### GET /appointments/availability
Check availability for time slot

**Query Params:**
- `service_id`: Required
- `pet_id`: Required
- `start_time`: ISO 8601 timestamp
- `staff_id` (optional)
- `resource_id` (optional)

**Response:** `200 OK`
```json
{
  "is_available": true,
  "conflicts": [],
  "suggested_times": [
    {"start": "2025-01-20T14:00:00Z", "staff_id": "uuid"},
    {"start": "2025-01-20T15:30:00Z", "staff_id": "uuid"}
  ]
}
```

---

## Vaccinations

### GET /pets/{pet_id}/vaccinations
List pet's vaccination records

**Response:** `200 OK`

---

### POST /pets/{pet_id}/vaccinations
Upload vaccination record

**Request:** (multipart/form-data)
```
vaccination_type: "rabies"
vaccination_date: "2024-01-15"
expiry_date: "2027-01-15"
file: <vaccination card image/PDF>
```

**Response:** `201 Created`

---

### GET /vaccinations/expiring
Get vaccinations expiring soon

**Query Params:**
- `days`: Number of days threshold (default: 30)

**Response:** `200 OK`

---

## Payments

### POST /payments/intent
Create payment intent (for deposits, tips, packages)

**Request:**
```json
{
  "amount": 2000,
  "type": "deposit",
  "appointment_id": "uuid"
}
```

**Response:** `200 OK`
```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

---

### POST /payments/webhook
Stripe webhook handler

**Headers:** `Stripe-Signature`

**Response:** `200 OK`

---

## SMS

### POST /sms/send
Send SMS to owner

**Request:**
```json
{
  "to": "+1234567890",
  "template": "confirmation",
  "variables": {
    "pet_name": "Bella",
    "date": "Tomorrow",
    "time": "2:00 PM"
  }
}
```

**Response:** `200 OK`

---

### POST /sms/webhook
Twilio inbound SMS webhook

**Response:** TwiML

---

### GET /sms/conversations
Get SMS conversation threads

**Response:** `200 OK` (paginated)

---

## Reports

### GET /reports/revenue
Revenue report

**Query Params:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `group_by`: day/week/month

**Response:** `200 OK`

---

### GET /reports/no-shows
No-show report

**Response:** `200 OK`

---

### GET /reports/utilization
Resource utilization report

**Response:** `200 OK`

---

## Health & System

### GET /health
Health check endpoint

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error",
  "details": [
    {"field": "email", "message": "Invalid email format"}
  ]
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "Resource not found"
}
```

### 409 Conflict
```json
{
  "error": "Conflict",
  "message": "Staff has conflicting appointment at 2:00 PM",
  "conflicts": [
    {
      "type": "staff_conflict",
      "appointment_id": "uuid",
      "time": "2025-01-20T14:00:00Z"
    }
  ]
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Business rule violation",
  "message": "Pet's rabies vaccination has expired"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Common Headers

### Request Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Tenant-ID: <tenant_uuid>  # Optional, auto-detected from subdomain
```

### Response Headers
```
Content-Type: application/json
X-Request-ID: <uuid>  # For tracing
X-RateLimit-Remaining: 100
```

---

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /pets?page=2&limit=20
```

**Response:**
```json
{
  "data": [...],
  "total": 45,
  "page": 2,
  "limit": 20,
  "pages": 3
}
```

---

## Rate Limiting

- **Default:** 100 requests/minute per user
- **Login:** 5 requests/minute per IP
- **Payment:** 10 requests/minute per user

**Response when rate limit exceeded:** `429 Too Many Requests`

---

## References

- **Swagger UI:** http://localhost:8012/docs
- **ReDoc:** http://localhost:8012/redoc
- **Developer Guide:** `docs/DEVELOPER-GUIDE.md`
- **Sprint Plans:** `sprints/current/sprint-*.md`

---

**Note:** This is a reference guide. Endpoints will be implemented during Sprints 1-6. Check Swagger UI for the most up-to-date API documentation.
