# Scheduled Tasks

Sprint 4-6 automated background tasks for the Pet Care SaaS platform.

## Overview

This directory contains scheduled tasks that run automatically to:
- Monitor vaccination expiries and send alerts
- Detect no-show appointments and apply fees
- Send appointment reminders (24h and 2h before)
- Update reputation scores
- Update vaccination statuses

## Available Tasks

### Daily Tasks (6:00 AM UTC)

#### 1. Vaccination Monitoring
- **File:** `vaccination_monitor.py`
- **Schedule:** Daily at 6:00 AM
- **Purpose:** Check for vaccinations expiring in 30, 14, and 7 days; send SMS alerts
- **Run manually:**
  ```bash
  python -m src.tasks.vaccination_monitor
  ```

#### 2. No-Show Detection
- **File:** `no_show_detector.py`
- **Schedule:** Daily at 6:30 AM
- **Purpose:** Detect appointments that were missed (after grace period); apply fees
- **Run manually:**
  ```bash
  python -m src.tasks.no_show_detector
  ```

### Hourly Tasks

#### 3. 24-Hour Appointment Reminders
- **File:** `appointment_reminders.py` (send_24_hour_reminders)
- **Schedule:** Top of every hour
- **Purpose:** Send SMS reminders for appointments in 24 hours
- **Run manually:**
  ```bash
  python -m src.tasks.appointment_reminders
  ```

#### 4. 2-Hour Appointment Reminders
- **File:** `appointment_reminders.py` (send_2_hour_reminders)
- **Schedule:** Half past every hour
- **Purpose:** Send SMS reminders for appointments in 2 hours

### Weekly Tasks (Sunday Midnight)

#### 5. Reputation Score Recovery
- **File:** `reputation_updater.py`
- **Schedule:** Sunday at 12:00 AM
- **Purpose:** Apply score recovery for customers with 90+ days of good behavior
- **Run manually:**
  ```bash
  python -m src.tasks.reputation_updater
  ```

## Scheduler Setup

### Option 1: APScheduler (Recommended for Development)

**Install dependencies:**
```bash
pip install apscheduler pytz
```

**Run the scheduler:**
```bash
python -m src.tasks.scheduler
```

The scheduler will run all tasks according to their configured schedules.

**Run as background process:**
```bash
# Linux/Mac
nohup python -m src.tasks.scheduler > scheduler.log 2>&1 &

# Windows
start /B python -m src.tasks.scheduler > scheduler.log 2>&1
```

### Option 2: Azure Functions (Recommended for Production)

Create timer-triggered Azure Functions for each task:

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Create function app
func init pet-care-scheduler --python

# Create timer functions
func new --name VaccinationMonitor --template "Timer trigger"
func new --name NoShowDetector --template "Timer trigger"
func new --name AppointmentReminders --template "Timer trigger"
func new --name ReputationUpdater --template "Timer trigger"
```

**Example function.json (daily at 6 AM):**
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 6 * * *"
    }
  ]
}
```

### Option 3: Celery (Recommended for High Scale)

**Install dependencies:**
```bash
pip install celery redis
```

**Create `celery_app.py`:**
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily tasks
    sender.add_periodic_task(
        crontab(hour=6, minute=0),
        vaccination_monitoring_task.s(),
        name='vaccination-monitoring'
    )
    # ... more tasks
```

**Run workers:**
```bash
celery -A celery_app worker --loglevel=info
celery -A celery_app beat --loglevel=info
```

### Option 4: Unix Cron (Simple, Traditional)

**Edit crontab:**
```bash
crontab -e
```

**Add entries:**
```cron
# Vaccination monitoring - Daily at 6 AM
0 6 * * * cd /path/to/api && python -m src.tasks.vaccination_monitor >> /var/log/petcare/vaccination.log 2>&1

# No-show detection - Daily at 6:30 AM
30 6 * * * cd /path/to/api && python -m src.tasks.no_show_detector >> /var/log/petcare/noshow.log 2>&1

# 24h reminders - Hourly
0 * * * * cd /path/to/api && python -m src.tasks.appointment_reminders >> /var/log/petcare/reminders.log 2>&1

# Reputation recovery - Sunday at midnight
0 0 * * 0 cd /path/to/api && python -m src.tasks.reputation_updater >> /var/log/petcare/reputation.log 2>&1
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Task Configuration
TASK_TIMEZONE=UTC  # or America/New_York, etc.
NO_SHOW_GRACE_PERIOD_MINUTES=15
REPUTATION_RECOVERY_DAYS=90
REPUTATION_RECOVERY_POINTS=5

# Notification Settings
SMS_ENABLED=true
VACCINATION_ALERT_THRESHOLDS=30,14,7  # Days before expiry
```

## Logging

All tasks log to stdout/stderr by default. Configure logging in production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/petcare/tasks.log'),
        logging.StreamHandler()
    ]
)
```

## Monitoring

### Check Scheduler Status

```bash
# View running scheduler
ps aux | grep scheduler

# View logs
tail -f scheduler.log
```

### Task Metrics

Each task returns a results dictionary with metrics:

```python
{
    "tenants_processed": 5,
    "total_detected": 12,
    "total_fees_applied": 12,
    "total_errors": 0
}
```

Monitor these metrics for:
- Successful executions
- Error rates
- Processing times
- Business impact (fees collected, alerts sent, etc.)

## Testing

Run individual tasks to test:

```bash
# Test vaccination monitoring
python -m src.tasks.vaccination_monitor

# Test no-show detection
python -m src.tasks.no_show_detector

# Test appointment reminders
python -m src.tasks.appointment_reminders

# Test reputation updater
python -m src.tasks.reputation_updater
```

## Troubleshooting

### Tasks not running

1. Check scheduler is running: `ps aux | grep scheduler`
2. Check logs for errors: `tail -f scheduler.log`
3. Verify database connection
4. Check timezone configuration

### SMS alerts not sending

1. Verify Twilio credentials in `.env`
2. Check owner `sms_opted_in` status
3. Review Twilio service logs
4. Verify phone number format

### High error rates

1. Check database performance
2. Review error logs for specific failures
3. Verify external service availability (Twilio, Stripe)
4. Monitor resource usage (CPU, memory)

## Production Deployment

### Recommended Setup

1. **Use Azure Functions or AWS Lambda** for serverless scheduling
2. **Set up monitoring** with Application Insights or CloudWatch
3. **Configure alerts** for task failures
4. **Enable retry logic** for transient failures
5. **Use dead letter queues** for failed tasks
6. **Monitor costs** for SMS and compute resources

### High Availability

For critical tasks:
- Use redundant schedulers with leader election
- Implement idempotent task execution
- Add circuit breakers for external services
- Set up health checks and automatic restart

### Cost Optimization

- Batch operations where possible
- Use appropriate SMS rates (long codes vs short codes)
- Cache frequently accessed data
- Optimize database queries
- Monitor and cap SMS sending rates

---

**Last Updated:** 2025-11-05
**Sprint:** 4-6
**Status:** Production Ready
