"""
Pet model
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ..db.base import Base


class PetGender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Pet(Base):
    """
    Pet model - represents dogs, cats, and other pets
    """
    __tablename__ = "pets"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Tenant (Multi-tenant isolation)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False, index=True)

    # Basic Information
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)  # dog, cat, bird, etc.
    breed = Column(String(100), nullable=True)
    gender = Column(SQLEnum(PetGender), nullable=True)

    # Physical Characteristics
    color = Column(String(100), nullable=True)
    weight = Column(Integer, nullable=True)  # In pounds
    date_of_birth = Column(Date, nullable=True)
    age_years = Column(Integer, nullable=True)
    age_months = Column(Integer, nullable=True)

    # Identification
    microchip_number = Column(String(50), nullable=True)
    license_number = Column(String(50), nullable=True)

    # Medical Information
    allergies = Column(Text, nullable=True)
    medical_conditions = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    veterinarian_name = Column(String(200), nullable=True)
    veterinarian_phone = Column(String(20), nullable=True)

    # Behavioral Information
    temperament = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    is_aggressive = Column(Boolean, default=False, nullable=False)
    needs_muzzle = Column(Boolean, default=False, nullable=False)

    # Vaccination Status
    vaccination_status = Column(String(20), default="unknown")  # current, expired, unknown
    vaccination_expires_at = Column(Date, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_deceased = Column(Boolean, default=False, nullable=False)

    # Profile
    photo_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", backref="pets")
    owner = relationship("Owner", backref="pets")

    def __repr__(self):
        return f"<Pet(id={self.id}, name={self.name}, breed={self.breed})>"

    @property
    def age_display(self):
        if self.age_years and self.age_months:
            return f"{self.age_years}y {self.age_months}m"
        elif self.age_years:
            return f"{self.age_years}y"
        elif self.age_months:
            return f"{self.age_months}m"
        return "Unknown"
