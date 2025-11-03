"""
Vaccination record model for tracking pet vaccinations
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class VaccinationType(str, enum.Enum):
    RABIES = "rabies"
    DISTEMPER = "distemper"
    PARVO = "parvo"
    BORDETELLA = "bordetella"
    LEUKEMIA = "leukemia"
    LYME = "lyme"
    DHPP = "dhpp"
    FVRCP = "fvrcp"
    OTHER = "other"


class VaccinationStatus(str, enum.Enum):
    CURRENT = "current"
    EXPIRING_SOON = "expiring_soon"  # Within 30 days
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class VaccinationRecord(Base):
    """
    Vaccination Record model - tracks pet vaccination history
    """
    __tablename__ = "vaccination_records"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Pet
    pet_id = Column(UUID(as_uuid=True), ForeignKey("pets.id"), nullable=False, index=True)

    # Vaccination Information
    type = Column(SQLEnum(VaccinationType), nullable=False)
    name = Column(String(200), nullable=True)  # Specific vaccine name/brand
    status = Column(SQLEnum(VaccinationStatus), default=VaccinationStatus.UNKNOWN, nullable=False)

    # Dates
    administered_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    reminder_sent_30d = Column(Boolean, default=False, nullable=False)
    reminder_sent_14d = Column(Boolean, default=False, nullable=False)
    reminder_sent_7d = Column(Boolean, default=False, nullable=False)

    # Veterinarian Information
    veterinarian_name = Column(String(200), nullable=True)
    veterinarian_clinic = Column(String(200), nullable=True)
    veterinarian_phone = Column(String(20), nullable=True)
    license_number = Column(String(100), nullable=True)

    # Documentation
    certificate_url = Column(String(500), nullable=True)  # URL to uploaded certificate
    lot_number = Column(String(100), nullable=True)
    manufacturer = Column(String(200), nullable=True)

    # Verification
    verified_by_staff = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="vaccination_records")
    pet = relationship("Pet", backref="vaccination_records")
    verified_by_user = relationship("User", backref="verified_vaccinations")

    def __repr__(self):
        return f"<VaccinationRecord(id={self.id}, type={self.type}, pet_id={self.pet_id}, expires={self.expiry_date})>"

    def update_status(self):
        """Update vaccination status based on expiry date"""
        from datetime import date, timedelta

        today = date.today()

        if self.expiry_date < today:
            self.status = VaccinationStatus.EXPIRED
        elif self.expiry_date <= today + timedelta(days=30):
            self.status = VaccinationStatus.EXPIRING_SOON
        else:
            self.status = VaccinationStatus.CURRENT

    @property
    def is_current(self):
        """Check if vaccination is current"""
        from datetime import date
        return self.expiry_date >= date.today()

    @property
    def days_until_expiry(self):
        """Days until expiration"""
        from datetime import date
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None
