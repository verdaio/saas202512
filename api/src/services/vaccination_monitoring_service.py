"""
Vaccination Monitoring Service
Sprint 4 - Automated vaccination expiry monitoring and alerts

Features:
- Daily scan for expiring vaccinations
- Automated SMS alerts (30, 14, 7 days before expiry)
- Email alerts (optional)
- Vaccination status updates
"""
from datetime import datetime, timedelta, date
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from ..models.vaccination_record import VaccinationRecord
from ..models.pet import Pet
from ..models.owner import Owner
from ..models.tenant import Tenant
from ..integrations.twilio_service import TwilioService


class VaccinationMonitoringService:
    """Service for monitoring vaccination expiries and sending alerts"""

    # Alert thresholds (days before expiry)
    ALERT_THRESHOLDS = [30, 14, 7]

    @staticmethod
    def get_expiring_vaccinations(
        db: Session,
        tenant_id: UUID,
        days_ahead: int
    ) -> List[VaccinationRecord]:
        """
        Get vaccinations expiring in X days

        Args:
            db: Database session
            tenant_id: Tenant ID
            days_ahead: Number of days to look ahead

        Returns:
            List of vaccination records expiring
        """
        target_date = date.today() + timedelta(days=days_ahead)

        vaccinations = db.query(VaccinationRecord).filter(
            VaccinationRecord.tenant_id == tenant_id,
            VaccinationRecord.expiry_date == target_date,
            VaccinationRecord.deleted_at.is_(None)
        ).all()

        return vaccinations

    @staticmethod
    def send_expiry_alert(
        db: Session,
        vaccination: VaccinationRecord,
        days_until_expiry: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Send expiry alert for a vaccination

        Args:
            db: Database session
            vaccination: Vaccination record
            days_until_expiry: Days until expiration

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get pet and owner
            pet = db.query(Pet).filter(Pet.id == vaccination.pet_id).first()
            if not pet:
                return False, "Pet not found"

            owner = db.query(Owner).filter(Owner.id == pet.owner_id).first()
            if not owner or not owner.sms_opted_in:
                return False, "Owner not found or SMS not opted in"

            # Send SMS alert
            result = TwilioService.send_vaccination_reminder(
                db=db,
                owner=owner,
                pet_name=pet.name,
                vaccination_type=vaccination.vaccination_type,
                expiry_date=vaccination.expiry_date,
                days_until_expiry=days_until_expiry
            )

            if result:
                # Mark alert as sent
                vaccination.last_alert_sent = datetime.utcnow()
                vaccination.alert_count = (vaccination.alert_count or 0) + 1
                db.commit()
                return True, None
            else:
                return False, "SMS sending failed"

        except Exception as e:
            return False, str(e)

    @staticmethod
    def run_daily_monitoring(db: Session, tenant_id: UUID) -> Dict[str, int]:
        """
        Run daily vaccination monitoring for a tenant

        This should be called by a scheduler once per day

        Args:
            db: Database session
            tenant_id: Tenant ID

        Returns:
            Dictionary with counts of alerts sent
        """
        results = {
            "total_checked": 0,
            "alerts_sent": 0,
            "alerts_failed": 0
        }

        for days_ahead in VaccinationMonitoringService.ALERT_THRESHOLDS:
            vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
                db, tenant_id, days_ahead
            )

            results["total_checked"] += len(vaccinations)

            for vaccination in vaccinations:
                success, error = VaccinationMonitoringService.send_expiry_alert(
                    db, vaccination, days_ahead
                )

                if success:
                    results["alerts_sent"] += 1
                else:
                    results["alerts_failed"] += 1

        return results

    @staticmethod
    def run_all_tenants_monitoring(db: Session) -> Dict[str, any]:
        """
        Run vaccination monitoring for all active tenants

        This is the main entry point for the daily cron job

        Returns:
            Summary of monitoring results across all tenants
        """
        tenants = db.query(Tenant).filter(
            Tenant.is_active == True,
            Tenant.deleted_at.is_(None)
        ).all()

        overall_results = {
            "tenants_processed": 0,
            "total_alerts_sent": 0,
            "total_alerts_failed": 0,
            "tenant_results": {}
        }

        for tenant in tenants:
            tenant_results = VaccinationMonitoringService.run_daily_monitoring(
                db, tenant.id
            )

            overall_results["tenants_processed"] += 1
            overall_results["total_alerts_sent"] += tenant_results["alerts_sent"]
            overall_results["total_alerts_failed"] += tenant_results["alerts_failed"]
            overall_results["tenant_results"][str(tenant.id)] = tenant_results

        return overall_results

    @staticmethod
    def get_expired_vaccinations(
        db: Session,
        tenant_id: UUID
    ) -> List[VaccinationRecord]:
        """
        Get all expired vaccinations for a tenant

        Args:
            db: Database session
            tenant_id: Tenant ID

        Returns:
            List of expired vaccination records
        """
        today = date.today()

        vaccinations = db.query(VaccinationRecord).filter(
            VaccinationRecord.tenant_id == tenant_id,
            VaccinationRecord.expiry_date < today,
            VaccinationRecord.deleted_at.is_(None)
        ).all()

        return vaccinations

    @staticmethod
    def update_vaccination_statuses(db: Session, tenant_id: UUID) -> int:
        """
        Update vaccination statuses based on expiry dates

        Args:
            db: Database session
            tenant_id: Tenant ID

        Returns:
            Number of vaccinations updated
        """
        today = date.today()
        updated_count = 0

        # Get all vaccinations
        vaccinations = db.query(VaccinationRecord).filter(
            VaccinationRecord.tenant_id == tenant_id,
            VaccinationRecord.deleted_at.is_(None)
        ).all()

        for vaccination in vaccinations:
            old_status = vaccination.is_current

            # Determine new status
            if vaccination.expiry_date and vaccination.expiry_date < today:
                new_status = False  # Expired
            else:
                new_status = True  # Current

            # Update if changed
            if old_status != new_status:
                vaccination.is_current = new_status
                updated_count += 1

        if updated_count > 0:
            db.commit()

        return updated_count

    @staticmethod
    def get_pets_with_expiring_vaccinations(
        db: Session,
        tenant_id: UUID,
        days_ahead: int = 30
    ) -> List[Dict]:
        """
        Get pets with vaccinations expiring soon

        Args:
            db: Database session
            tenant_id: Tenant ID
            days_ahead: Days to look ahead

        Returns:
            List of dictionaries with pet and vaccination info
        """
        target_date = date.today() + timedelta(days=days_ahead)

        vaccinations = db.query(VaccinationRecord).filter(
            VaccinationRecord.tenant_id == tenant_id,
            VaccinationRecord.expiry_date <= target_date,
            VaccinationRecord.expiry_date >= date.today(),
            VaccinationRecord.deleted_at.is_(None)
        ).all()

        result = []
        for vaccination in vaccinations:
            pet = db.query(Pet).filter(Pet.id == vaccination.pet_id).first()
            if pet:
                owner = db.query(Owner).filter(Owner.id == pet.owner_id).first()

                days_until_expiry = (vaccination.expiry_date - date.today()).days

                result.append({
                    "pet_id": str(pet.id),
                    "pet_name": pet.name,
                    "owner_id": str(owner.id) if owner else None,
                    "owner_name": f"{owner.first_name} {owner.last_name}" if owner else None,
                    "vaccination_type": vaccination.vaccination_type,
                    "expiry_date": vaccination.expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "administered_date": vaccination.administered_date.isoformat() if vaccination.administered_date else None
                })

        return result

    @staticmethod
    def schedule_vaccination_alerts(db: Session, tenant_id: UUID) -> Dict:
        """
        Schedule vaccination alerts for upcoming expiries

        This can be used to pre-schedule alerts instead of daily checks

        Returns:
            Summary of scheduled alerts
        """
        scheduled = {
            "30_days": [],
            "14_days": [],
            "7_days": []
        }

        for days in [30, 14, 7]:
            vaccinations = VaccinationMonitoringService.get_expiring_vaccinations(
                db, tenant_id, days
            )

            for vaccination in vaccinations:
                pet = db.query(Pet).filter(Pet.id == vaccination.pet_id).first()
                if pet:
                    owner = db.query(Owner).filter(Owner.id == pet.owner_id).first()
                    if owner and owner.sms_opted_in:
                        scheduled[f"{days}_days"].append({
                            "vaccination_id": str(vaccination.id),
                            "pet_name": pet.name,
                            "owner_email": owner.email,
                            "expiry_date": vaccination.expiry_date.isoformat()
                        })

        return scheduled
