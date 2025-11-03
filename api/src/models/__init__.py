"""
Database models registry
"""
from .tenant import Tenant, TenantStatus
from .user import User, UserRole
from .staff import Staff
from .owner import Owner
from .pet import Pet, PetGender
from .service import Service
from .resource import Resource, ResourceType
from .appointment import Appointment, AppointmentStatus, AppointmentSource
from .package import Package, PackageType, PackageStatus
from .payment import Payment, PaymentStatus, PaymentType, PaymentMethod
from .vaccination_record import VaccinationRecord, VaccinationType, VaccinationStatus

__all__ = [
    # Models
    "Tenant",
    "User",
    "Staff",
    "Owner",
    "Pet",
    "Service",
    "Resource",
    "Appointment",
    "Package",
    "Payment",
    "VaccinationRecord",
    # Enums
    "TenantStatus",
    "UserRole",
    "PetGender",
    "ResourceType",
    "AppointmentStatus",
    "AppointmentSource",
    "PackageType",
    "PackageStatus",
    "PaymentStatus",
    "PaymentType",
    "PaymentMethod",
    "VaccinationType",
    "VaccinationStatus",
]
