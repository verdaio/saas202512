# Testing Guide - Pet Care Scheduler

**Last Updated:** 2025-11-02
**Project:** saas202512 (Pet Care)

---

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Smoke Tests](#smoke-tests)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [End-to-End Testing](#end-to-end-testing)
- [PR Testing Checklist](#pr-testing-checklist)
- [CI/CD Integration](#cicd-integration)

---

## Testing Philosophy

**Test Goals:**
1. **Reliability** - Prevent bugs from reaching production
2. **Confidence** - Deploy with confidence
3. **Documentation** - Tests serve as living documentation
4. **Speed** - Fast feedback loop for developers

**Testing Pyramid:**
```
        /\
       /E2E\      ← Few, critical user flows
      /------\
     /Integr.\   ← API endpoints, database interactions
    /----------\
   /Unit Tests \  ← Most tests, fast and focused
  /--------------\
```

---

## Test Types

| Type | Scope | Speed | Quantity | Example |
|------|-------|-------|----------|---------|
| **Unit** | Single function/class | Fast (<1s) | Many (100s) | Test availability checker logic |
| **Integration** | Multiple components | Medium (1-5s) | Moderate (50s) | Test booking API with database |
| **E2E** | Full user workflow | Slow (10-30s) | Few (10s) | Test complete booking flow in browser |
| **Smoke** | Quick validation | Very fast (<1s) | Critical paths | Test health endpoint returns 200 |

---

## Smoke Tests

**Purpose:** Quick validation that critical functionality works. Run before submitting PR.

### Backend Smoke Tests

```bash
# 1. Health check
curl http://localhost:8012/health
# Expected: {"status":"healthy","database":"connected"}

# 2. API docs accessible
curl -I http://localhost:8012/docs
# Expected: HTTP/1.1 200 OK

# 3. Database connection
docker compose exec postgres pg_isready
# Expected: /var/run/postgresql:5432 - accepting connections

# 4. Run pytest suite
cd backend
pytest -v
# Expected: All tests pass (green)

# 5. Check for lint errors
black --check app/
isort --check app/
# Expected: No errors
```

### Frontend Smoke Tests

```bash
# 1. Development server starts
npm run dev
# Expected: Server running on http://localhost:3012

# 2. Health check (if implemented)
curl http://localhost:3012/api/health
# Expected: {"status":"ok"}

# 3. Run test suite
npm test
# Expected: All tests pass

# 4. Build succeeds
npm run build
# Expected: Build completes without errors

# 5. Lint check
npm run lint
# Expected: No errors
```

### Infrastructure Smoke Tests

```bash
# 1. Docker Compose config validates
docker compose config
# Expected: Valid YAML output, no errors

# 2. All services start
docker compose up -d
docker compose ps
# Expected: All services show "running" status

# 3. Check logs for errors
docker compose logs | grep -i error
# Expected: No critical errors

# 4. Port accessibility
nc -zv localhost 5412  # PostgreSQL
nc -zv localhost 8012  # Backend
nc -zv localhost 3012  # Frontend
# Expected: All ports accessible
```

### Generated Artifacts Smoke Tests

**Example: Generated document validation**

```bash
# Run document generator script
node scripts/create-pitch-deck.js

# Verify output exists
ls -lh artifacts/02-PITCH-DECK.docx
# Expected: File exists, reasonable size (>50KB)

# Take screenshot for PR
# (Manual step: Open in Word, take screenshot)

# Clean up (don't commit)
rm artifacts/02-PITCH-DECK.docx
```

**For PRs with generated output:**
1. Run generator locally
2. Verify output looks correct
3. Take screenshot showing output
4. Include screenshot in PR description
5. Do NOT commit the generated file

---

## Unit Testing

### Backend Unit Tests (Python/pytest)

**Location:** `backend/tests/unit/`

**Example: Test availability checker**

```python
# backend/tests/unit/test_availability.py
import pytest
from datetime import datetime, timedelta
from app.services.availability import AvailabilityChecker
from app.models import Appointment, Service, Staff

def test_check_availability_no_conflicts():
    """Test availability check when no conflicts exist."""
    checker = AvailabilityChecker()
    service = Service(duration_minutes=60, buffer_before=10, buffer_after=15)
    staff = Staff(id="staff-1")

    start_time = datetime(2025, 1, 20, 10, 0)

    result = checker.check_availability(
        service=service,
        staff=staff,
        start_time=start_time
    )

    assert result.is_available == True
    assert len(result.conflicts) == 0

def test_check_availability_staff_conflict():
    """Test availability check when staff has conflicting appointment."""
    # Setup: Create existing appointment for staff
    existing_appt = Appointment(
        staff_id="staff-1",
        scheduled_start=datetime(2025, 1, 20, 10, 0),
        scheduled_end=datetime(2025, 1, 20, 11, 0)
    )

    checker = AvailabilityChecker(existing_appointments=[existing_appt])
    service = Service(duration_minutes=60)
    staff = Staff(id="staff-1")

    # Try to book overlapping time
    start_time = datetime(2025, 1, 20, 10, 30)

    result = checker.check_availability(
        service=service,
        staff=staff,
        start_time=start_time
    )

    assert result.is_available == False
    assert len(result.conflicts) == 1
    assert result.conflicts[0].type == "staff_conflict"
```

**Run unit tests:**
```bash
cd backend
pytest tests/unit/ -v
```

### Frontend Unit Tests (Jest/React Testing Library)

**Location:** `frontend/__tests__/unit/`

**Example: Test booking widget component**

```typescript
// frontend/__tests__/unit/BookingWidget.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import BookingWidget from '@/components/BookingWidget';

describe('BookingWidget', () => {
  it('renders service selection step', () => {
    render(<BookingWidget />);

    expect(screen.getByText('Select a Service')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /full groom/i })).toBeInTheDocument();
  });

  it('advances to date selection after service chosen', () => {
    render(<BookingWidget />);

    const groomButton = screen.getByRole('button', { name: /full groom/i });
    fireEvent.click(groomButton);

    expect(screen.getByText('Choose Date & Time')).toBeInTheDocument();
  });

  it('validates required fields before submission', async () => {
    render(<BookingWidget />);

    const submitButton = screen.getByRole('button', { name: /book appointment/i });
    fireEvent.click(submitButton);

    expect(await screen.findByText(/please select a service/i)).toBeInTheDocument();
  });
});
```

**Run unit tests:**
```bash
cd frontend
npm test
```

---

## Integration Testing

### Backend Integration Tests

**Location:** `backend/tests/integration/`

**Purpose:** Test API endpoints with real database

**Setup:** Use test database, run migrations

```python
# backend/tests/integration/test_booking_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine

@pytest.fixture(scope="module")
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Test client with database."""
    return TestClient(app)

def test_create_appointment_success(client):
    """Test POST /appointments creates appointment successfully."""
    # Arrange: Create test data (tenant, pet, service, staff)
    tenant_id = create_test_tenant()
    pet_id = create_test_pet(tenant_id)
    service_id = create_test_service(tenant_id)
    staff_id = create_test_staff(tenant_id)

    # Act: POST appointment
    response = client.post(
        "/api/v1/appointments",
        headers={"X-Tenant-ID": tenant_id},
        json={
            "pet_id": pet_id,
            "service_id": service_id,
            "staff_id": staff_id,
            "scheduled_start": "2025-01-20T10:00:00Z"
        }
    )

    # Assert: 201 Created, appointment returned
    assert response.status_code == 201
    data = response.json()
    assert data["pet_id"] == pet_id
    assert data["status"] == "scheduled"
    assert "id" in data

def test_create_appointment_double_booking_prevented(client):
    """Test double-booking prevention."""
    # Arrange: Create first appointment
    appt1 = create_test_appointment(
        staff_id="staff-1",
        start="2025-01-20T10:00:00Z"
    )

    # Act: Try to book overlapping time for same staff
    response = client.post(
        "/api/v1/appointments",
        json={
            "staff_id": "staff-1",
            "scheduled_start": "2025-01-20T10:30:00Z",  # Overlaps
            ...
        }
    )

    # Assert: 409 Conflict
    assert response.status_code == 409
    assert "staff_conflict" in response.json()["error"]
```

**Run integration tests:**
```bash
cd backend

# Start test database
docker compose -f docker-compose.test.yml up -d postgres

# Run tests
pytest tests/integration/ -v

# Cleanup
docker compose -f docker-compose.test.yml down -v
```

---

## End-to-End Testing

### E2E Tests (Playwright or Cypress)

**Location:** `e2e/tests/`

**Purpose:** Test complete user workflows in real browser

**Example: Complete booking flow**

```typescript
// e2e/tests/booking-flow.spec.ts
import { test, expect } from '@playwright/test';

test('owner can book appointment end-to-end', async ({ page }) => {
  // 1. Navigate to booking page
  await page.goto('http://localhost:3012/book/happypaws');

  // 2. Select service
  await page.click('button:has-text("Full Groom")');

  // 3. Select pet
  await page.click('text=Bella (Golden Retriever)');

  // 4. Choose date and time
  await page.click('[data-testid="date-picker"]');
  await page.click('text=Tomorrow');
  await page.click('text=10:00 AM');

  // 5. Enter payment info
  await page.fill('[name="cardNumber"]', '4242424242424242');
  await page.fill('[name="expiry"]', '12/25');
  await page.fill('[name="cvc"]', '123');

  // 6. Submit booking
  await page.click('button:has-text("Confirm Booking")');

  // 7. Verify confirmation
  await expect(page.locator('text=Booking Confirmed')).toBeVisible();
  await expect(page.locator('text=Bella')).toBeVisible();
  await expect(page.locator('text=10:00 AM')).toBeVisible();
});
```

**Run E2E tests:**
```bash
# Install Playwright
npm install --save-dev @playwright/test

# Run tests
npx playwright test

# Run with UI
npx playwright test --ui
```

---

## PR Testing Checklist

Use this checklist before submitting a PR:

### Code Changes

- [ ] All unit tests pass (`pytest` / `npm test`)
- [ ] All integration tests pass
- [ ] Added tests for new functionality
- [ ] Test coverage did not decrease
- [ ] No lint errors (`black`, `isort`, `eslint`, `prettier`)

### Infrastructure Changes

- [ ] `docker compose config` validates without errors
- [ ] All services start successfully (`docker compose up -d`)
- [ ] `docker compose ps` shows all services as "running"
- [ ] No errors in logs (`docker compose logs | grep -i error`)
- [ ] Port conflicts resolved
- [ ] Environment variables documented in `.env.example`

### Database Changes

- [ ] Migration created (`alembic revision --autogenerate`)
- [ ] Migration tested (up and down)
- [ ] Migration is reversible
- [ ] No data loss in migration
- [ ] Indexes added for new queries

### API Changes

- [ ] API documentation updated (OpenAPI/Swagger)
- [ ] Breaking changes documented
- [ ] Backward compatibility maintained (or version bumped)
- [ ] Error responses documented

### Frontend Changes

- [ ] Component tests added
- [ ] Responsive design tested (mobile, tablet, desktop)
- [ ] Accessibility checked (keyboard navigation, screen readers)
- [ ] Screenshots included in PR (if UI changes)

### Generated Artifacts

- [ ] Screenshot of generated output included in PR
- [ ] Generated files NOT committed (unless exception)
- [ ] Smoke test passes (e.g., `node create-pitch-deck.js` → outputs file)

### Security

- [ ] No secrets in code or config files
- [ ] No secrets in `parameters.*.json` files
- [ ] Sensitive data properly encrypted
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified

### Documentation

- [ ] README updated (if setup changes)
- [ ] Developer Guide updated (if new dependencies)
- [ ] ADR created (if architectural decision)
- [ ] Code comments added for complex logic

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: petcare_test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

  infrastructure-validation:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Validate Docker Compose
        run: docker compose config
```

---

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Backend models | 95%+ |
| Backend services | 90%+ |
| Backend API routes | 85%+ |
| Frontend components | 80%+ |
| Frontend utilities | 90%+ |

**View coverage:**
```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

---

## Troubleshooting Tests

### Tests Failing Locally

1. **Check database is running:**
   ```bash
   docker compose ps postgres
   ```

2. **Reset test database:**
   ```bash
   docker compose down -v
   docker compose up -d postgres
   cd backend
   alembic upgrade head
   ```

3. **Clear cache:**
   ```bash
   # Python
   find . -type d -name __pycache__ -exec rm -r {} +

   # Node
   rm -rf node_modules
   npm install
   ```

### Tests Passing Locally but Failing in CI

1. **Check environment differences** (Python version, Node version)
2. **Check timezone issues** (use UTC in tests)
3. **Check database state** (ensure clean state between tests)
4. **Check for race conditions** (async timing issues)

---

## Additional Resources

- **Developer Guide:** `docs/Developer-Guide.md`
- **Contributing Guidelines:** `docs/Contributing.md`
- **Security Guidelines:** `docs/Security.md`
- **Sprint Plans:** `sprints/current/`

---

**Happy testing!** 🧪
