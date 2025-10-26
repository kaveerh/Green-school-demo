"""
Vendor Repository

Data access layer for Vendor operations with specialized queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from models.vendor import Vendor
from repositories.base_repository import BaseRepository
from datetime import date, timedelta
import uuid


class VendorRepository(BaseRepository[Vendor]):
    """Repository for Vendor data access"""

    def __init__(self, session: AsyncSession):
        super().__init__(Vendor, session)

    async def get_by_school(
        self,
        school_id: uuid.UUID,
        vendor_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Vendor], int]:
        """Get vendors for a school with optional filters"""
        offset = (page - 1) * limit

        # Build base conditions
        conditions = [
            Vendor.school_id == school_id,
            Vendor.deleted_at.is_(None)
        ]

        if vendor_type:
            conditions.append(Vendor.vendor_type == vendor_type)
        if status:
            conditions.append(Vendor.status == status)

        # Count query
        count_query = select(func.count(Vendor.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Vendor).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            desc(Vendor.preferred),
            asc(Vendor.company_name)
        )

        result = await self.session.execute(query)
        vendors = result.scalars().all()

        return list(vendors), total

    async def get_by_type(
        self,
        school_id: uuid.UUID,
        vendor_type: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Vendor], int]:
        """Get vendors by type"""
        return await self.get_by_school(
            school_id=school_id,
            vendor_type=vendor_type,
            page=page,
            limit=limit
        )

    async def get_by_status(
        self,
        school_id: uuid.UUID,
        status: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Vendor], int]:
        """Get vendors by status"""
        return await self.get_by_school(
            school_id=school_id,
            status=status,
            page=page,
            limit=limit
        )

    async def get_preferred(
        self,
        school_id: uuid.UUID,
        limit: int = 20
    ) -> List[Vendor]:
        """Get preferred vendors for a school"""
        conditions = [
            Vendor.school_id == school_id,
            Vendor.preferred == True,
            Vendor.status == 'active',
            Vendor.deleted_at.is_(None)
        ]

        query = select(Vendor).where(and_(*conditions)).limit(limit).order_by(
            desc(Vendor.performance_rating),
            asc(Vendor.company_name)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        school_id: uuid.UUID,
        query_text: str,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Vendor], int]:
        """Search vendors by company name, description, or category"""
        offset = (page - 1) * limit
        search_pattern = f"%{query_text}%"

        conditions = [
            Vendor.school_id == school_id,
            or_(
                Vendor.company_name.ilike(search_pattern),
                Vendor.description.ilike(search_pattern),
                Vendor.category.ilike(search_pattern)
            ),
            Vendor.deleted_at.is_(None)
        ]

        # Count query
        count_query = select(func.count(Vendor.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Data query
        query = select(Vendor).where(and_(*conditions)).offset(offset).limit(limit).order_by(
            asc(Vendor.company_name)
        )

        result = await self.session.execute(query)
        vendors = result.scalars().all()

        return list(vendors), total

    async def get_by_company_name(
        self,
        school_id: uuid.UUID,
        company_name: str
    ) -> Optional[Vendor]:
        """Get vendor by company name (for uniqueness check)"""
        conditions = [
            Vendor.school_id == school_id,
            Vendor.company_name == company_name,
            Vendor.deleted_at.is_(None)
        ]

        query = select(Vendor).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_expiring_contracts(
        self,
        school_id: uuid.UUID,
        days_ahead: int = 30
    ) -> List[Vendor]:
        """Get vendors with contracts expiring within specified days"""
        today = date.today()
        expiry_date = today + timedelta(days=days_ahead)

        conditions = [
            Vendor.school_id == school_id,
            Vendor.contract_end_date.isnot(None),
            Vendor.contract_end_date >= today,
            Vendor.contract_end_date <= expiry_date,
            Vendor.status == 'active',
            Vendor.deleted_at.is_(None)
        ]

        query = select(Vendor).where(and_(*conditions)).order_by(
            asc(Vendor.contract_end_date)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_expired_insurance(
        self,
        school_id: uuid.UUID
    ) -> List[Vendor]:
        """Get vendors with expired insurance"""
        today = date.today()

        conditions = [
            Vendor.school_id == school_id,
            Vendor.insurance_expiry_date.isnot(None),
            Vendor.insurance_expiry_date < today,
            Vendor.status == 'active',
            Vendor.deleted_at.is_(None)
        ]

        query = select(Vendor).where(and_(*conditions)).order_by(
            asc(Vendor.insurance_expiry_date)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: uuid.UUID
    ) -> Optional[Vendor]:
        """Get vendor by linked user account"""
        conditions = [
            Vendor.user_id == user_id,
            Vendor.deleted_at.is_(None)
        ]

        query = select(Vendor).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_statistics(
        self,
        school_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get vendor statistics for a school"""
        conditions = [
            Vendor.school_id == school_id,
            Vendor.deleted_at.is_(None)
        ]

        # Total vendors
        total_query = select(func.count(Vendor.id)).where(and_(*conditions))
        total_result = await self.session.execute(total_query)
        total_vendors = total_result.scalar()

        # By type
        type_query = select(
            Vendor.vendor_type,
            func.count(Vendor.id).label('count')
        ).where(and_(*conditions)).group_by(Vendor.vendor_type)
        type_result = await self.session.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result}

        # By status
        status_query = select(
            Vendor.status,
            func.count(Vendor.id).label('count')
        ).where(and_(*conditions)).group_by(Vendor.status)
        status_result = await self.session.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result}

        # Active vendors
        active_conditions = conditions + [Vendor.status == 'active']
        active_query = select(func.count(Vendor.id)).where(and_(*active_conditions))
        active_result = await self.session.execute(active_query)
        active_vendors = active_result.scalar()

        # Preferred vendors
        preferred_conditions = conditions + [Vendor.preferred == True]
        preferred_query = select(func.count(Vendor.id)).where(and_(*preferred_conditions))
        preferred_result = await self.session.execute(preferred_query)
        preferred_vendors = preferred_result.scalar()

        # Average rating
        rating_query = select(func.avg(Vendor.performance_rating)).where(
            and_(*conditions, Vendor.performance_rating.isnot(None))
        )
        rating_result = await self.session.execute(rating_query)
        avg_rating = rating_result.scalar()

        # Total contract value
        contract_query = select(func.sum(Vendor.contract_value)).where(
            and_(*conditions, Vendor.contract_value.isnot(None), Vendor.status == 'active')
        )
        contract_result = await self.session.execute(contract_query)
        total_contract_value = contract_result.scalar()

        # Expiring contracts (30 days)
        expiring = await self.get_expiring_contracts(school_id, days_ahead=30)
        expiring_contracts = len(expiring)

        return {
            "total_vendors": total_vendors,
            "by_type": by_type,
            "by_status": by_status,
            "active_vendors": active_vendors,
            "preferred_vendors": preferred_vendors,
            "average_rating": round(float(avg_rating), 2) if avg_rating else 0.0,
            "total_contract_value": float(total_contract_value) if total_contract_value else 0.0,
            "expiring_contracts": expiring_contracts
        }
