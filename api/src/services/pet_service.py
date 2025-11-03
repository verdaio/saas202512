"""
Pet service with business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import uuid

from ..models.pet import Pet
from ..models.owner import Owner
from ..models.tenant import Tenant
from ..schemas.pet import PetCreate, PetUpdate


class PetService:
    """Business logic for pet management"""

    @staticmethod
    def create_pet(
        db: Session,
        tenant: Tenant,
        pet_data: PetCreate
    ) -> Pet:
        """
        Create new pet with validation
        """
        # Verify owner exists
        owner = db.query(Owner).filter(
            Owner.id == pet_data.owner_id,
            Owner.tenant_id == tenant.id
        ).first()

        if not owner:
            raise ValueError("Owner not found")

        pet = Pet(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            **pet_data.model_dump()
        )

        db.add(pet)
        db.commit()
        db.refresh(pet)

        return pet

    @staticmethod
    def get_pet(
        db: Session,
        tenant: Tenant,
        pet_id: UUID
    ) -> Optional[Pet]:
        """Get pet by ID"""
        return db.query(Pet).filter(
            Pet.id == pet_id,
            Pet.tenant_id == tenant.id
        ).first()

    @staticmethod
    def list_pets(
        db: Session,
        tenant: Tenant,
        skip: int = 0,
        limit: int = 100,
        owner_id: UUID = None,
        species: str = None,
        is_active: bool = None
    ) -> List[Pet]:
        """List pets with filters"""
        query = db.query(Pet).filter(Pet.tenant_id == tenant.id)

        if owner_id:
            query = query.filter(Pet.owner_id == owner_id)

        if species:
            query = query.filter(Pet.species == species)

        if is_active is not None:
            query = query.filter(Pet.is_active == is_active)

        return query.order_by(Pet.name).offset(skip).limit(limit).all()

    @staticmethod
    def get_pets_by_owner(
        db: Session,
        tenant: Tenant,
        owner_id: UUID
    ) -> List[Pet]:
        """Get all pets for an owner"""
        return db.query(Pet).filter(
            Pet.tenant_id == tenant.id,
            Pet.owner_id == owner_id,
            Pet.is_active == True
        ).all()

    @staticmethod
    def update_pet(
        db: Session,
        tenant: Tenant,
        pet_id: UUID,
        pet_data: PetUpdate
    ) -> Optional[Pet]:
        """Update pet"""
        pet = PetService.get_pet(db, tenant, pet_id)

        if not pet:
            return None

        # Update fields
        for field, value in pet_data.model_dump(exclude_unset=True).items():
            setattr(pet, field, value)

        db.commit()
        db.refresh(pet)

        return pet

    @staticmethod
    def deactivate_pet(
        db: Session,
        tenant: Tenant,
        pet_id: UUID
    ) -> bool:
        """Deactivate pet"""
        pet = PetService.get_pet(db, tenant, pet_id)

        if not pet:
            return False

        pet.is_active = False
        db.commit()

        return True

    @staticmethod
    def check_vaccination_status(
        db: Session,
        tenant: Tenant,
        pet_id: UUID
    ) -> dict:
        """
        Check pet's vaccination status
        Returns dict with status and days until expiry
        """
        pet = PetService.get_pet(db, tenant, pet_id)

        if not pet:
            raise ValueError("Pet not found")

        from datetime import date

        result = {
            "status": pet.vaccination_status,
            "expires_at": pet.vaccination_expires_at,
            "is_current": False,
            "days_until_expiry": None
        }

        if pet.vaccination_expires_at:
            today = date.today()
            delta = pet.vaccination_expires_at - today
            result["days_until_expiry"] = delta.days
            result["is_current"] = delta.days > 0

        return result
