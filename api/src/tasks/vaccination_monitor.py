"""
Vaccination Monitoring Task
Sprint 4 - Daily task to check expiring vaccinations and send alerts

Usage:
    python -m src.tasks.vaccination_monitor
    or
    python src/tasks/vaccination_monitor.py
"""
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.tenant import Tenant
from ..services.vaccination_monitoring_service import VaccinationMonitoringService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_vaccination_monitoring(db: Session) -> dict:
    """
    Run vaccination monitoring for all active tenants

    Returns:
        Summary of monitoring results
    """
    logger.info("Starting vaccination monitoring task")

    results = VaccinationMonitoringService.run_all_tenants_monitoring(db)

    logger.info(f"Vaccination monitoring complete: {results['tenants_processed']} tenants processed")
    logger.info(f"Alerts sent: {results['total_alerts_sent']}, Failed: {results['total_alerts_failed']}")

    return results


def run_vaccination_status_update(db: Session) -> int:
    """
    Update vaccination statuses for all active tenants

    Returns:
        Total number of vaccinations updated
    """
    logger.info("Starting vaccination status update task")

    total_updated = 0
    tenants = db.query(Tenant).filter(
        Tenant.is_active == True,
        Tenant.deleted_at.is_(None)
    ).all()

    for tenant in tenants:
        updated = VaccinationMonitoringService.update_vaccination_statuses(
            db=db,
            tenant_id=tenant.id
        )
        total_updated += updated
        logger.info(f"Updated {updated} vaccinations for tenant {tenant.name}")

    logger.info(f"Vaccination status update complete: {total_updated} total updated")

    return total_updated


def main():
    """Main entry point for vaccination monitoring task"""
    logger.info("=" * 80)
    logger.info(f"Vaccination Monitoring Task - Started at {datetime.utcnow()}")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Run monitoring
        monitoring_results = run_vaccination_monitoring(db)

        # Run status updates
        status_updates = run_vaccination_status_update(db)

        logger.info("=" * 80)
        logger.info("Task completed successfully")
        logger.info(f"Summary: {monitoring_results['total_alerts_sent']} alerts sent, "
                   f"{status_updates} statuses updated")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error in vaccination monitoring task: {e}", exc_info=True)
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
