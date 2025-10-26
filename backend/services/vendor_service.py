"""
Vendor Service

Business logic layer for Vendor operations including validation and processing.
"""

from typing import Optional, List, Dict, Any
from datetime import date
import uuid

from repositories.vendor_repository import VendorRepository
from models.vendor import Vendor


class VendorService:
    """Service for vendor business logic"""

    def __init__(self, repository: VendorRepository):
        self.repository = repository

    async def create_vendor(
        self,
        school_id: uuid.UUID,
        company_name: str,
        vendor_type: str,
        created_by_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Vendor:
        """
        Create a new vendor with validation

        Args:
            school_id: School ID
            company_name: Company name
            vendor_type: Type of vendor
            created_by_id: User creating the vendor
            **kwargs: Additional vendor fields

        Returns:
            Created vendor

        Raises:
            ValueError: If validation fails
        """
        # Validate company name uniqueness
        existing = await self.repository.get_by_company_name(school_id, company_name)
        if existing:
            raise ValueError(f"Vendor with company name '{company_name}' already exists for this school")

        # Validate vendor type
        valid_types = ['food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other']
        if vendor_type not in valid_types:
            raise ValueError(f"Invalid vendor type. Must be one of: {', '.join(valid_types)}")

        # Validate contract dates if provided
        contract_start = kwargs.get('contract_start_date')
        contract_end = kwargs.get('contract_end_date')
        if contract_start and contract_end:
            if isinstance(contract_start, str):
                contract_start = date.fromisoformat(contract_start)
            if isinstance(contract_end, str):
                contract_end = date.fromisoformat(contract_end)
            if contract_end < contract_start:
                raise ValueError("Contract end date must be after start date")

        # Validate performance rating if provided
        rating = kwargs.get('performance_rating')
        if rating is not None:
            if not (0 <= float(rating) <= 5):
                raise ValueError("Performance rating must be between 0 and 5")

        # Create vendor
        vendor_data = {
            'school_id': school_id,
            'company_name': company_name,
            'vendor_type': vendor_type,
            'created_by': created_by_id,
            **kwargs
        }

        vendor = await self.repository.create(vendor_data)
        return vendor

    async def update_vendor(
        self,
        vendor_id: uuid.UUID,
        updated_by_id: Optional[uuid.UUID] = None,
        **kwargs
    ) -> Vendor:
        """
        Update vendor with validation

        Args:
            vendor_id: Vendor ID
            updated_by_id: User updating the vendor
            **kwargs: Fields to update

        Returns:
            Updated vendor

        Raises:
            ValueError: If validation fails
        """
        vendor = await self.repository.get_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with ID {vendor_id} not found")

        # Validate company name uniqueness if changing
        if 'company_name' in kwargs and kwargs['company_name'] != vendor.company_name:
            existing = await self.repository.get_by_company_name(vendor.school_id, kwargs['company_name'])
            if existing and existing.id != vendor_id:
                raise ValueError(f"Vendor with company name '{kwargs['company_name']}' already exists for this school")

        # Validate vendor type if changing
        if 'vendor_type' in kwargs:
            valid_types = ['food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other']
            if kwargs['vendor_type'] not in valid_types:
                raise ValueError(f"Invalid vendor type. Must be one of: {', '.join(valid_types)}")

        # Validate contract dates if provided
        contract_start = kwargs.get('contract_start_date', vendor.contract_start_date)
        contract_end = kwargs.get('contract_end_date', vendor.contract_end_date)
        if contract_start and contract_end:
            if isinstance(contract_start, str):
                contract_start = date.fromisoformat(contract_start)
            if isinstance(contract_end, str):
                contract_end = date.fromisoformat(contract_end)
            if contract_end < contract_start:
                raise ValueError("Contract end date must be after start date")

        # Validate performance rating if provided
        if 'performance_rating' in kwargs:
            rating = kwargs['performance_rating']
            if rating is not None and not (0 <= float(rating) <= 5):
                raise ValueError("Performance rating must be between 0 and 5")

        # Validate status if changing
        if 'status' in kwargs:
            valid_statuses = ['active', 'inactive', 'suspended', 'terminated']
            if kwargs['status'] not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        kwargs['updated_by'] = updated_by_id
        updated_vendor = await self.repository.update(vendor_id, kwargs)
        return updated_vendor

    async def delete_vendor(
        self,
        vendor_id: uuid.UUID,
        deleted_by_id: Optional[uuid.UUID] = None
    ) -> None:
        """
        Soft delete a vendor

        Args:
            vendor_id: Vendor ID
            deleted_by_id: User deleting the vendor
        """
        vendor = await self.repository.get_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with ID {vendor_id} not found")

        await self.repository.delete(vendor_id)

    async def update_status(
        self,
        vendor_id: uuid.UUID,
        status: str,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Vendor:
        """
        Update vendor status

        Args:
            vendor_id: Vendor ID
            status: New status
            updated_by_id: User updating the status

        Returns:
            Updated vendor
        """
        valid_statuses = ['active', 'inactive', 'suspended', 'terminated']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        return await self.update_vendor(vendor_id, updated_by_id=updated_by_id, status=status)

    async def update_rating(
        self,
        vendor_id: uuid.UUID,
        rating: float,
        updated_by_id: Optional[uuid.UUID] = None
    ) -> Vendor:
        """
        Update vendor performance rating

        Args:
            vendor_id: Vendor ID
            rating: Performance rating (0-5)
            updated_by_id: User updating the rating

        Returns:
            Updated vendor
        """
        if not (0 <= rating <= 5):
            raise ValueError("Performance rating must be between 0 and 5")

        return await self.update_vendor(vendor_id, updated_by_id=updated_by_id, performance_rating=rating)

    async def increment_orders(
        self,
        vendor_id: uuid.UUID
    ) -> Vendor:
        """
        Increment total orders count for a vendor

        Args:
            vendor_id: Vendor ID

        Returns:
            Updated vendor
        """
        vendor = await self.repository.get_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with ID {vendor_id} not found")

        new_count = (vendor.total_orders or 0) + 1
        return await self.update_vendor(vendor_id, total_orders=new_count)

    async def get_alerts(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get vendor-related alerts for a school

        Args:
            school_id: School ID

        Returns:
            Dictionary with alerts
        """
        # Get expiring contracts
        expiring_contracts = await self.repository.get_expiring_contracts(school_id, days_ahead=30)

        # Get expired insurance
        expired_insurance = await self.repository.get_expired_insurance(school_id)

        return {
            "expiring_contracts": [
                {
                    "vendor_id": str(v.id),
                    "company_name": v.company_name,
                    "contract_end_date": v.contract_end_date.isoformat() if v.contract_end_date else None,
                    "days_until_expiry": (v.contract_end_date - date.today()).days if v.contract_end_date else None
                }
                for v in expiring_contracts
            ],
            "expired_insurance": [
                {
                    "vendor_id": str(v.id),
                    "company_name": v.company_name,
                    "insurance_expiry_date": v.insurance_expiry_date.isoformat() if v.insurance_expiry_date else None,
                    "days_expired": (date.today() - v.insurance_expiry_date).days if v.insurance_expiry_date else None
                }
                for v in expired_insurance
            ]
        }
