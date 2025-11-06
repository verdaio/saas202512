"""
No-Show Detection Task
Sprint 4 - Daily task to detect and process no-show appointments

Usage:
    python -m src.tasks.no_show_detector
    or
    python src/tasks/no_show_detector.py
"""
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.tenant import Tenant
from ..services.no_show_service import NoShowService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_no_show_detection(db: Session) -> dict:
    """
    Run no-show detection for all active tenants

    Returns:
        Summary of detection results
    """
    logger.info("Starting no-show detection task")

    total_results = {
        "tenants_processed": 0,
        "total_detected": 0,
        "total_fees_applied": 0,
        "total_errors": 0
    }

    tenants = db.query(Tenant).filter(
        Tenant.is_active == True,
        Tenant.deleted_at.is_(None)
    ).all()

    for tenant in tenants:
        logger.info(f"Processing tenant: {tenant.name} ({tenant.subdomain})")

        results = NoShowService.process_daily_no_show_detection(
            db=db,
            tenant_id=tenant.id
        )

        total_results["tenants_processed"] += 1
        total_results["total_detected"] += results["total_detected"]
        total_results["total_fees_applied"] += results["fees_applied"]
        total_results["total_errors"] += results["errors"]

        logger.info(f"  Detected: {results['total_detected']}, "
                   f"Fees applied: {results['fees_applied']}, "
                   f"Errors: {results['errors']}")

    logger.info(f"No-show detection complete: {total_results['tenants_processed']} tenants processed")
    logger.info(f"Total detected: {total_results['total_detected']}, "
               f"Fees applied: {total_results['total_fees_applied']}")

    return total_results


def main():
    """Main entry point for no-show detection task"""
    logger.info("=" * 80)
    logger.info(f"No-Show Detection Task - Started at {datetime.utcnow()}")
    logger.info("=" * 80)

    db = SessionLocal()
    try:
        results = run_no_show_detection(db)

        logger.info("=" * 80)
        logger.info("Task completed successfully")
        logger.info(f"Summary: {results['total_detected']} no-shows detected, "
                   f"{results['total_fees_applied']} fees applied")
        if results['total_errors'] > 0:
            logger.warning(f"Errors encountered: {results['total_errors']}")
        logger.info("=" * 80)

        return 0 if results['total_errors'] == 0 else 1

    except Exception as e:
        logger.error(f"Error in no-show detection task: {e}", exc_info=True)
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
