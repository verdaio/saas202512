"""
Reputation Score Updater Task
Sprint 4 - Weekly task to apply score recovery for good behavior

Usage:
    python -m src.tasks.reputation_updater
    or
    python src/tasks/reputation_updater.py
"""
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.tenant import Tenant
from ..services.reputation_service import ReputationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_reputation_recovery(db: Session, days_since_last_event: int = 90, recovery_points: int = 5) -> dict:
    """
    Run reputation score recovery for all active tenants

    Args:
        db: Database session
        days_since_last_event: Days of good behavior required (default: 90)
        recovery_points: Points to add for recovery (default: 5)

    Returns:
        Summary of recovery results
    """
    logger.info(f"Starting reputation recovery task (threshold: {days_since_last_event} days, "
               f"recovery: {recovery_points} points)")

    total_results = {
        "tenants_processed": 0,
        "total_checked": 0,
        "total_improved": 0
    }

    tenants = db.query(Tenant).filter(
        Tenant.is_active == True,
        Tenant.deleted_at.is_(None)
    ).all()

    for tenant in tenants:
        logger.info(f"Processing tenant: {tenant.name} ({tenant.subdomain})")

        results = ReputationService.apply_score_decay(
            db=db,
            tenant_id=tenant.id,
            days_since_last_event=days_since_last_event,
            recovery_points=recovery_points
        )

        total_results["tenants_processed"] += 1
        total_results["total_checked"] += results["customers_checked"]
        total_results["total_improved"] += results["scores_improved"]

        logger.info(f"  Checked: {results['customers_checked']}, "
                   f"Improved: {results['scores_improved']}")

    logger.info(f"Reputation recovery complete: {total_results['tenants_processed']} tenants processed")
    logger.info(f"Total checked: {total_results['total_checked']}, "
               f"Improved: {total_results['total_improved']}")

    return total_results


def main():
    """Main entry point for reputation updater task"""
    logger.info("=" * 80)
    logger.info(f"Reputation Score Recovery Task - Started at {datetime.utcnow()}")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        # Run with default settings: 90 days good behavior, +5 points recovery
        results = run_reputation_recovery(
            db=db,
            days_since_last_event=90,
            recovery_points=5
        )

        logger.info("=" * 80)
        logger.info("Task completed successfully")
        logger.info(f"Summary: {results['total_checked']} customers checked, "
                   f"{results['total_improved']} scores improved")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error in reputation recovery task: {e}", exc_info=True)
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
