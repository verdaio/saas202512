"""
Task Scheduler
Sprint 4-6 - APScheduler configuration for automated tasks

Usage:
    python -m src.tasks.scheduler
    or
    python src/tasks/scheduler.py
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from ..db.session import SessionLocal
from .vaccination_monitor import run_vaccination_monitoring, run_vaccination_status_update
from .no_show_detector import run_no_show_detection
from .reputation_updater import run_reputation_recovery
from .appointment_reminders import send_24_hour_reminders, send_2_hour_reminders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for the Pet Care SaaS platform"""

    def __init__(self, timezone='UTC'):
        """
        Initialize scheduler

        Args:
            timezone: Timezone for scheduling (default: UTC)
        """
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(timezone))
        self.timezone = timezone

    def setup_jobs(self):
        """Configure all scheduled jobs"""

        # ==================== DAILY TASKS ====================

        # Vaccination monitoring - Daily at 6:00 AM
        self.scheduler.add_job(
            func=self._run_vaccination_monitoring,
            trigger=CronTrigger(hour=6, minute=0, timezone=self.timezone),
            id='vaccination_monitoring',
            name='Vaccination Expiry Monitoring',
            misfire_grace_time=3600  # 1 hour grace period
        )

        # Vaccination status updates - Daily at 6:15 AM
        self.scheduler.add_job(
            func=self._run_vaccination_status_update,
            trigger=CronTrigger(hour=6, minute=15, timezone=self.timezone),
            id='vaccination_status_update',
            name='Vaccination Status Update',
            misfire_grace_time=3600
        )

        # No-show detection - Daily at 6:30 AM
        self.scheduler.add_job(
            func=self._run_no_show_detection,
            trigger=CronTrigger(hour=6, minute=30, timezone=self.timezone),
            id='no_show_detection',
            name='No-Show Detection',
            misfire_grace_time=3600
        )

        # ==================== HOURLY TASKS ====================

        # 24-hour appointment reminders - Every hour
        self.scheduler.add_job(
            func=self._send_24_hour_reminders,
            trigger=CronTrigger(minute=0, timezone=self.timezone),  # Top of every hour
            id='reminders_24h',
            name='24-Hour Appointment Reminders',
            misfire_grace_time=300  # 5 minute grace period
        )

        # 2-hour appointment reminders - Every hour
        self.scheduler.add_job(
            func=self._send_2_hour_reminders,
            trigger=CronTrigger(minute=30, timezone=self.timezone),  # Half past every hour
            id='reminders_2h',
            name='2-Hour Appointment Reminders',
            misfire_grace_time=300
        )

        # ==================== WEEKLY TASKS ====================

        # Reputation score recovery - Sunday at midnight
        self.scheduler.add_job(
            func=self._run_reputation_recovery,
            trigger=CronTrigger(day_of_week='sun', hour=0, minute=0, timezone=self.timezone),
            id='reputation_recovery',
            name='Reputation Score Recovery',
            misfire_grace_time=7200  # 2 hour grace period
        )

        logger.info("All scheduled jobs configured")
        self._print_jobs()

    def _run_vaccination_monitoring(self):
        """Wrapper for vaccination monitoring task"""
        logger.info("Executing vaccination monitoring task")
        db = SessionLocal()
        try:
            results = run_vaccination_monitoring(db)
            logger.info(f"Vaccination monitoring completed: {results}")
        except Exception as e:
            logger.error(f"Error in vaccination monitoring: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _run_vaccination_status_update(self):
        """Wrapper for vaccination status update task"""
        logger.info("Executing vaccination status update task")
        db = SessionLocal()
        try:
            updated = run_vaccination_status_update(db)
            logger.info(f"Vaccination status update completed: {updated} records updated")
        except Exception as e:
            logger.error(f"Error in vaccination status update: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _run_no_show_detection(self):
        """Wrapper for no-show detection task"""
        logger.info("Executing no-show detection task")
        db = SessionLocal()
        try:
            results = run_no_show_detection(db)
            logger.info(f"No-show detection completed: {results}")
        except Exception as e:
            logger.error(f"Error in no-show detection: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _send_24_hour_reminders(self):
        """Wrapper for 24-hour reminder task"""
        logger.info("Executing 24-hour reminder task")
        db = SessionLocal()
        try:
            results = send_24_hour_reminders(db)
            logger.info(f"24-hour reminders completed: {results}")
        except Exception as e:
            logger.error(f"Error in 24-hour reminders: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _send_2_hour_reminders(self):
        """Wrapper for 2-hour reminder task"""
        logger.info("Executing 2-hour reminder task")
        db = SessionLocal()
        try:
            results = send_2_hour_reminders(db)
            logger.info(f"2-hour reminders completed: {results}")
        except Exception as e:
            logger.error(f"Error in 2-hour reminders: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _run_reputation_recovery(self):
        """Wrapper for reputation recovery task"""
        logger.info("Executing reputation recovery task")
        db = SessionLocal()
        try:
            results = run_reputation_recovery(db, days_since_last_event=90, recovery_points=5)
            logger.info(f"Reputation recovery completed: {results}")
        except Exception as e:
            logger.error(f"Error in reputation recovery: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()

    def _print_jobs(self):
        """Print all scheduled jobs"""
        logger.info("=" * 80)
        logger.info("Scheduled Jobs:")
        logger.info("=" * 80)

        jobs = self.scheduler.get_jobs()
        for job in jobs:
            logger.info(f"  {job.name}")
            logger.info(f"    ID: {job.id}")
            logger.info(f"    Next run: {job.next_run_time}")
            logger.info("")

        logger.info("=" * 80)

    def start(self):
        """Start the scheduler"""
        logger.info("Starting task scheduler...")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("Pet Care SaaS - Task Scheduler")
    logger.info("=" * 80)

    scheduler = TaskScheduler(timezone='UTC')
    scheduler.setup_jobs()
    scheduler.start()


if __name__ == "__main__":
    main()
