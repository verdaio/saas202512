# Sprint 4-6 Combined Plan: Advanced Features & Operations

**Sprints**: 4, 5, 6 of 6
**Status**: In Progress
**Start Date**: 2025-11-05
**Estimated Duration**: 80-100 hours

---

## 🎯 Combined Goals

**Primary Objective**: Complete the SaaS platform with advanced automation, operational tools, and business intelligence.

**Key Deliverables**:
1. **Sprint 4**: Vaccination tracking, no-show defense, reputation scoring
2. **Sprint 5**: SMS workflow automation, conditional messaging, templates
3. **Sprint 6**: Admin dashboard, reporting, analytics, business intelligence

---

## 📋 Sprint 4: Vaccination & No-Show Defense

### User Stories

**US-4.1**: As a system, I want to monitor vaccination expiry so that I can alert customers proactively
- Acceptance: Daily check for expiring vaccinations
- Acceptance: Alerts at 30, 14, 7 days before expiry
- Acceptance: SMS sent automatically

**US-4.2**: As a business owner, I want to track no-shows so that I can reduce lost revenue
- Acceptance: Automatic no-show detection
- Acceptance: No-show fee application
- Acceptance: Repeat offender tracking

**US-4.3**: As a system, I want to score customer reputation so that I can prevent abuse
- Acceptance: Score based on no-shows, cancellations, on-time arrivals
- Acceptance: Automatic booking restrictions for low scores
- Acceptance: Score recovery over time

### Features to Implement

1. **Vaccination Monitoring Service**
   - Daily scan for expiring vaccinations
   - Alert scheduling (30, 14, 7 days)
   - SMS delivery via Twilio
   - Vaccination status updates

2. **No-Show Tracking**
   - Automatic no-show detection (appointment time + grace period)
   - No-show fee calculation and application
   - No-show history tracking
   - Penalty escalation for repeat offenders

3. **Reputation Scoring**
   - Customer reputation score (0-100)
   - Factors: no-shows (-20), late cancellations (-10), on-time (+5)
   - Automatic booking restrictions (score < 30)
   - Score decay/recovery (improve over time)

---

## 📋 Sprint 5: SMS Workflow Automation

### User Stories

**US-5.1**: As a business owner, I want to automate SMS campaigns so that I reduce manual work
- Acceptance: Define SMS workflows with conditions
- Acceptance: Automatic execution based on triggers
- Acceptance: Template library with variables

**US-5.2**: As a system, I want to send targeted messages so that customers receive relevant info
- Acceptance: Conditional logic (if vaccination expired, send alert)
- Acceptance: Customer segmentation
- Acceptance: Opt-in/opt-out management

**US-5.3**: As a business owner, I want to track SMS performance so that I can optimize messaging
- Acceptance: Delivery rates tracked
- Acceptance: Response rates measured
- Acceptance: Cost tracking per campaign

### Features to Implement

1. **SMS Workflow Engine**
   - Workflow definition (trigger → conditions → actions)
   - Trigger types: time-based, event-based, manual
   - Condition evaluation (customer data, appointment status, etc.)
   - Action execution (send SMS, update record, log event)

2. **Workflow Templates**
   - Pre-built workflows (reminders, follow-ups, promotions)
   - Customizable message templates
   - Variable substitution
   - A/B testing support

3. **SMS Analytics**
   - Delivery rate tracking
   - Click-through rate (if URLs included)
   - Response rate
   - Cost per SMS
   - Campaign ROI

---

## 📋 Sprint 6: Operations & Reporting

### User Stories

**US-6.1**: As a business owner, I want to view revenue reports so that I can track performance
- Acceptance: Daily, weekly, monthly revenue reports
- Acceptance: Revenue by service type
- Acceptance: Payment method breakdown

**US-6.2**: As a business owner, I want to analyze appointments so that I can optimize scheduling
- Acceptance: Appointment volume trends
- Acceptance: Peak time analysis
- Acceptance: Staff utilization metrics
- Acceptance: No-show rate tracking

**US-6.3**: As a business owner, I want customer insights so that I can improve retention
- Acceptance: Customer lifetime value
- Acceptance: Repeat customer rate
- Acceptance: Churn analysis
- Acceptance: Top customers report

**US-6.4**: As an admin, I want an operational dashboard so that I can monitor the business
- Acceptance: Real-time metrics
- Acceptance: Today's appointments
- Acceptance: Alerts and notifications
- Acceptance: Quick actions

### Features to Implement

1. **Admin Dashboard**
   - Real-time metrics (today's revenue, appointments, etc.)
   - Quick stats cards
   - Today's schedule view
   - Recent activity feed
   - Alert notifications

2. **Revenue Reporting**
   - Revenue by period (day, week, month, year)
   - Revenue by service
   - Revenue by staff member
   - Payment method breakdown
   - Refund tracking

3. **Appointment Analytics**
   - Appointment volume trends
   - Peak times/days analysis
   - Average appointment value
   - Cancellation rate
   - No-show rate
   - Booking source (online vs phone)

4. **Customer Analytics**
   - Customer lifetime value (CLV)
   - Repeat customer rate
   - Customer acquisition cost
   - Churn rate
   - Top customers (by revenue)
   - Customer segments

5. **Staff Performance**
   - Appointments per staff member
   - Revenue per staff member
   - Average rating (if reviews implemented)
   - Utilization rate

---

## 🏗️ Implementation Plan

### Phase 1: Sprint 4 - Vaccination & No-Show (25-30 hours)

#### 1.1 Vaccination Monitoring Service

**File**: `api/src/services/vaccination_monitoring_service.py`

```python
class VaccinationMonitoringService:
    @staticmethod
    def get_expiring_vaccinations(days_ahead: int) -> List[VaccinationRecord]

    @staticmethod
    def send_expiry_alerts()

    @staticmethod
    def schedule_daily_monitoring()
```

**Features**:
- Daily cron job to check expiring vaccinations
- Alert thresholds: 30, 14, 7 days
- SMS delivery via Twilio
- Email alerts (optional)
- Log all alerts sent

#### 1.2 No-Show Tracking Service

**File**: `api/src/services/no_show_service.py`

```python
class NoShowService:
    @staticmethod
    def detect_no_shows() -> List[Appointment]

    @staticmethod
    def apply_no_show_fee(appointment_id: UUID, fee_amount: int)

    @staticmethod
    def get_customer_no_show_history(owner_id: UUID) -> Dict

    @staticmethod
    def calculate_no_show_penalty(no_show_count: int) -> int
```

**Features**:
- Automatic detection (appointment time + 15 min grace period)
- Configurable no-show fees
- Escalating penalties for repeat offenders
- No-show history tracking
- SMS notification of fee

#### 1.3 Reputation Scoring Service

**File**: `api/src/services/reputation_service.py`

```python
class ReputationService:
    @staticmethod
    def calculate_reputation_score(owner_id: UUID) -> int

    @staticmethod
    def update_reputation_after_event(owner_id: UUID, event_type: str)

    @staticmethod
    def can_book_appointment(owner_id: UUID) -> Tuple[bool, Optional[str]]

    @staticmethod
    def get_reputation_history(owner_id: UUID) -> List[Dict]
```

**Scoring Logic**:
- Base score: 100
- No-show: -20 points
- Late cancellation (< 24h): -10 points
- On-time arrival: +5 points
- Completed appointment: +2 points
- Score minimum: 0, maximum: 100
- Booking restriction: score < 30

**Database Updates**:
Add to Owner model:
- `reputation_score: int (default 100)`
- `no_show_count: int (default 0)`
- `late_cancellation_count: int (default 0)`
- `completed_appointment_count: int (default 0)`

Add new model: `ReputationEvent`
- Track all events affecting reputation
- Allows audit trail

---

### Phase 2: Sprint 5 - SMS Workflows (25-30 hours)

#### 2.1 SMS Workflow Engine

**File**: `api/src/services/sms_workflow_service.py`

```python
class WorkflowTriggerType(str, enum.Enum):
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_COMPLETED = "appointment_completed"
    TIME_BASED = "time_based"
    VACCINATION_EXPIRING = "vaccination_expiring"
    NO_SHOW_DETECTED = "no_show_detected"

class SMSWorkflowService:
    @staticmethod
    def create_workflow(workflow_data: Dict) -> Workflow

    @staticmethod
    def execute_workflow(workflow_id: UUID, trigger_data: Dict)

    @staticmethod
    def evaluate_conditions(conditions: List[Dict], context: Dict) -> bool

    @staticmethod
    def execute_actions(actions: List[Dict], context: Dict)
```

**Workflow Structure**:
```json
{
  "name": "Post-Appointment Follow-up",
  "trigger": {
    "type": "appointment_completed",
    "delay_hours": 2
  },
  "conditions": [
    {
      "field": "owner.sms_opted_in",
      "operator": "equals",
      "value": true
    }
  ],
  "actions": [
    {
      "type": "send_sms",
      "template": "post_appointment_thanks",
      "variables": {"owner_name": "<owner.first_name>"}
    },
    {
      "type": "log_event",
      "message": "Follow-up SMS sent"
    }
  ]
}
```

#### 2.2 Workflow Models

**New Models**:

`Workflow`:
- `id, tenant_id, name, description`
- `trigger_type, trigger_config (JSON)`
- `conditions (JSON), actions (JSON)`
- `is_active, created_at, updated_at`

`WorkflowExecution`:
- `id, workflow_id, trigger_data (JSON)`
- `executed_at, status, result (JSON)`

`WorkflowTemplate`:
- `id, name, description, category`
- `template_data (JSON)`

#### 2.3 SMS Analytics Service

**File**: `api/src/services/sms_analytics_service.py`

```python
class SMSAnalyticsService:
    @staticmethod
    def get_delivery_stats(start_date: date, end_date: date) -> Dict

    @staticmethod
    def get_campaign_performance(campaign_id: UUID) -> Dict

    @staticmethod
    def get_cost_analysis(month: int, year: int) -> Dict
```

**Metrics**:
- Total SMS sent
- Delivery rate (delivered / sent)
- Failure rate
- Response rate (if tracking replies)
- Cost per SMS
- Total cost

---

### Phase 3: Sprint 6 - Operations & Reports (30-40 hours)

#### 3.1 Admin Dashboard API

**File**: `api/src/api/admin/dashboard.py`

```python
@router.get("/dashboard/overview")
async def get_dashboard_overview(
    date: date = Query(default=date.today())
) -> Dict:
    """
    Get dashboard overview for a specific date
    Returns: revenue, appointments, customers, alerts
    """
```

**Dashboard Metrics**:
- Today's revenue
- Today's appointments (total, confirmed, pending)
- New customers this week
- Outstanding payments
- Upcoming appointments (next 2 hours)
- Recent no-shows
- Low inventory alerts (if applicable)

#### 3.2 Reporting Service

**File**: `api/src/services/reporting_service.py`

```python
class ReportingService:
    # Revenue Reports
    @staticmethod
    def get_revenue_report(start_date: date, end_date: date, group_by: str) -> Dict

    @staticmethod
    def get_revenue_by_service(start_date: date, end_date: date) -> List[Dict]

    @staticmethod
    def get_payment_method_breakdown(start_date: date, end_date: date) -> Dict

    # Appointment Reports
    @staticmethod
    def get_appointment_volume_report(start_date: date, end_date: date) -> Dict

    @staticmethod
    def get_peak_times_analysis(start_date: date, end_date: date) -> Dict

    @staticmethod
    def get_cancellation_report(start_date: date, end_date: date) -> Dict

    # Customer Reports
    @staticmethod
    def get_customer_lifetime_value(owner_id: UUID) -> Decimal

    @staticmethod
    def get_top_customers(limit: int = 10) -> List[Dict]

    @staticmethod
    def get_customer_retention_report(start_date: date, end_date: date) -> Dict

    # Staff Reports
    @staticmethod
    def get_staff_performance(staff_id: UUID, start_date: date, end_date: date) -> Dict
```

#### 3.3 Analytics Queries

**File**: `api/src/services/analytics_service.py`

Complex queries for business intelligence:
- Customer acquisition trends
- Service popularity over time
- Staff utilization rates
- Seasonal trends
- Customer churn prediction
- Revenue forecasting

#### 3.4 Report Endpoints

**File**: `api/src/api/admin/reports.py`

```python
@router.get("/reports/revenue")
async def get_revenue_report(...)

@router.get("/reports/appointments")
async def get_appointment_report(...)

@router.get("/reports/customers")
async def get_customer_report(...)

@router.get("/reports/staff")
async def get_staff_report(...)

@router.get("/reports/export/{report_type}")
async def export_report(report_type: str, format: str = "csv")
```

**Export Formats**:
- CSV
- PDF (using ReportLab)
- Excel (using openpyxl)
- JSON

---

## 📁 File Structure

```
api/
├── src/
│   ├── services/
│   │   ├── vaccination_monitoring_service.py  # NEW - Sprint 4
│   │   ├── no_show_service.py                 # NEW - Sprint 4
│   │   ├── reputation_service.py              # NEW - Sprint 4
│   │   ├── sms_workflow_service.py            # NEW - Sprint 5
│   │   ├── sms_analytics_service.py           # NEW - Sprint 5
│   │   ├── reporting_service.py               # NEW - Sprint 6
│   │   └── analytics_service.py               # NEW - Sprint 6
│   ├── api/
│   │   └── admin/
│   │       ├── __init__.py                    # NEW
│   │       ├── dashboard.py                   # NEW - Sprint 6
│   │       ├── reports.py                     # NEW - Sprint 6
│   │       └── workflows.py                   # NEW - Sprint 5
│   ├── models/
│   │   ├── workflow.py                        # NEW - Sprint 5
│   │   ├── workflow_execution.py              # NEW - Sprint 5
│   │   ├── reputation_event.py                # NEW - Sprint 4
│   │   └── no_show_record.py                  # NEW - Sprint 4
│   ├── tasks/
│   │   ├── __init__.py                        # NEW
│   │   ├── vaccination_monitor.py             # NEW - Sprint 4
│   │   ├── no_show_detector.py                # NEW - Sprint 4
│   │   └── workflow_scheduler.py              # NEW - Sprint 5
│   └── utils/
│       ├── export.py                          # NEW - Sprint 6
│       └── scheduler.py                       # NEW - All sprints

web/
├── src/
│   ├── app/
│   │   └── admin/
│   │       ├── layout.tsx                     # NEW - Sprint 6
│   │       ├── page.tsx                       # Dashboard
│   │       ├── reports/
│   │       │   ├── revenue/page.tsx
│   │       │   ├── appointments/page.tsx
│   │       │   └── customers/page.tsx
│   │       └── workflows/
│   │           ├── page.tsx
│   │           └── [id]/page.tsx
│   └── components/
│       └── admin/
│           ├── DashboardCard.tsx
│           ├── RevenueChart.tsx
│           ├── AppointmentList.tsx
│           └── WorkflowBuilder.tsx
```

---

## 🗓️ Automated Tasks

### Scheduled Jobs

**Daily Tasks** (run at 6:00 AM):
- Vaccination expiry check (send 30/14/7 day alerts)
- No-show detection (previous day's appointments)
- Reputation score updates
- Daily revenue summary
- Backup database

**Hourly Tasks**:
- 24-hour reminder check
- 2-hour reminder check
- Workflow execution (time-based triggers)

**Weekly Tasks** (Sunday at midnight):
- Weekly performance report
- Customer retention analysis
- Staff utilization summary

**Monthly Tasks** (1st of month):
- Monthly revenue report
- Customer churn analysis
- Invoice generation

**Implementation**:
- Use APScheduler (Python) or celery
- Or use Azure Functions for serverless cron

---

## 📊 Database Schema Updates

### New Tables

**reputation_events**:
```sql
CREATE TABLE reputation_events (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    owner_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- no_show, late_cancel, on_time, completed
    event_date TIMESTAMP NOT NULL,
    points_change INT NOT NULL,
    new_score INT NOT NULL,
    related_appointment_id UUID,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**no_show_records**:
```sql
CREATE TABLE no_show_records (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    appointment_id UUID NOT NULL,
    owner_id UUID NOT NULL,
    fee_amount INT,  -- in cents
    fee_charged BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP NOT NULL,
    grace_period_minutes INT DEFAULT 15,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**workflows**:
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB,
    conditions JSONB,
    actions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**workflow_executions**:
```sql
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL,
    trigger_data JSONB,
    executed_at TIMESTAMP NOT NULL,
    status VARCHAR(20),  -- success, failed, pending
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Model Updates

**Owner model** - add fields:
```python
reputation_score = Column(Integer, default=100, nullable=False)
no_show_count = Column(Integer, default=0, nullable=False)
late_cancellation_count = Column(Integer, default=0, nullable=False)
completed_appointment_count = Column(Integer, default=0, nullable=False)
last_reputation_update = Column(DateTime(timezone=True), nullable=True)
```

**Appointment model** - add fields:
```python
is_no_show = Column(Boolean, default=False, nullable=False)
no_show_fee_charged = Column(Integer, default=0, nullable=False)
arrived_at = Column(DateTime(timezone=True), nullable=True)
```

---

## 🎯 Success Criteria

### Sprint 4
- [x] Vaccination monitoring running daily
- [x] Alerts sent at 30, 14, 7 days
- [x] No-show detection automated
- [x] No-show fees applied
- [x] Reputation scoring functional
- [x] Booking restrictions enforced

### Sprint 5
- [x] Workflow engine operational
- [x] 5+ pre-built workflow templates
- [x] SMS analytics tracking
- [x] Workflow execution logging
- [x] Admin UI for workflow management

### Sprint 6
- [x] Admin dashboard live
- [x] Revenue reports functional
- [x] Appointment analytics working
- [x] Customer insights available
- [x] Export functionality (CSV, PDF)
- [x] Scheduled reports

---

## 🚀 Deployment Considerations

### Environment Variables

```bash
# Scheduler
SCHEDULER_ENABLED=true
TIMEZONE=America/New_York

# No-Show Settings
NO_SHOW_GRACE_PERIOD_MINUTES=15
NO_SHOW_FEE_AMOUNT=2500  # $25 in cents
NO_SHOW_FEE_ESCALATION=true

# Reputation Settings
REPUTATION_MIN_SCORE=0
REPUTATION_MAX_SCORE=100
REPUTATION_BOOKING_THRESHOLD=30

# Reporting
REPORT_EXPORT_PATH=/tmp/reports/
REPORT_EMAIL_RECIPIENTS=owner@business.com
```

### Scheduled Tasks Setup

**Option 1: APScheduler** (in-app):
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(vaccination_monitor_task, 'cron', hour=6)
scheduler.add_job(no_show_detector_task, 'cron', hour=0)
scheduler.start()
```

**Option 2: Azure Functions** (serverless):
- Create timer-triggered functions
- More scalable for production
- Easier monitoring

**Option 3: Celery** (task queue):
- For high-volume operations
- Better error handling
- Supports distributed workers

---

## 📈 Performance Optimization

### Database Indexing
```sql
CREATE INDEX idx_vaccinations_expiry ON vaccination_records(expiry_date, tenant_id);
CREATE INDEX idx_appointments_scheduled ON appointments(scheduled_start, tenant_id, status);
CREATE INDEX idx_reputation_owner ON reputation_events(owner_id, event_date DESC);
CREATE INDEX idx_payments_date ON payments(created_at, tenant_id);
```

### Caching Strategy
- Cache dashboard metrics (5 min TTL)
- Cache report results (1 hour TTL)
- Cache customer reputation scores (10 min TTL)
- Use Redis for caching

### Query Optimization
- Use database views for complex reports
- Implement pagination for large result sets
- Use EXPLAIN to optimize slow queries
- Consider read replicas for reporting

---

## 🧪 Testing Requirements

### Unit Tests
- Reputation score calculation
- No-show detection logic
- Workflow condition evaluation
- Report data aggregation

### Integration Tests
- Vaccination monitoring flow
- No-show fee application
- Workflow execution end-to-end
- Report generation

### Load Tests
- Dashboard under concurrent users
- Report generation performance
- Workflow execution at scale

---

**Total Estimated Lines**: ~4,000-5,000 lines
**Total Files**: ~25-30 files
**Timeline**: 80-100 hours (2-3 weeks full-time)

---

**Ready to implement!** 🚀
