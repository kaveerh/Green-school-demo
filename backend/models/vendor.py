"""
Vendor Model

External service providers and suppliers for schools.
"""

from sqlalchemy import Column, String, Date, Boolean, Integer, Text, CheckConstraint, Index, ForeignKey, ARRAY, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import date as date_type
import uuid


class Vendor(BaseModel):
    """Vendor model for external service providers and suppliers"""
    __tablename__ = "vendors"

    # Foreign Keys
    school_id = Column(PG_UUID(as_uuid=True), ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Company Information
    company_name = Column(String(255), nullable=False)
    business_number = Column(String(50), nullable=True)

    # Vendor Classification
    vendor_type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)
    services_provided = Column(ARRAY(Text), nullable=True)

    # Contact Information
    primary_contact_name = Column(String(255), nullable=True)
    primary_contact_title = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    phone_alt = Column(String(20), nullable=True)
    website = Column(String(500), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="USA", nullable=True)

    # Business Details
    description = Column(Text, nullable=True)
    certifications = Column(ARRAY(Text), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    insurance_expiry_date = Column(Date, nullable=True)

    # Contract & Financial
    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    contract_value = Column(DECIMAL(12, 2), nullable=True)
    payment_terms = Column(String(100), nullable=True)
    tax_exempt = Column(Boolean, default=False, nullable=True)

    # Performance & Status
    status = Column(String(20), default="active", nullable=False)
    performance_rating = Column(DECIMAL(3, 2), nullable=True)
    total_orders = Column(Integer, default=0, nullable=True)

    # Preferences
    preferred = Column(Boolean, default=False, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    school = relationship("School", foreign_keys=[school_id])
    user = relationship("User", foreign_keys=[user_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "vendor_type IN ('food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other')",
            name="chk_vendors_type"
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'terminated')",
            name="chk_vendors_status"
        ),
        CheckConstraint(
            "performance_rating IS NULL OR (performance_rating >= 0 AND performance_rating <= 5)",
            name="chk_vendors_rating"
        ),
        CheckConstraint(
            "contract_end_date IS NULL OR contract_start_date IS NULL OR contract_end_date >= contract_start_date",
            name="chk_vendors_contract_dates"
        ),
        CheckConstraint(
            "contract_value IS NULL OR contract_value >= 0",
            name="chk_vendors_contract_value"
        ),
        CheckConstraint(
            "total_orders >= 0",
            name="chk_vendors_total_orders"
        ),
        Index('idx_vendors_school_id', 'school_id'),
        Index('idx_vendors_user_id', 'user_id'),
        Index('idx_vendors_type', 'vendor_type'),
        Index('idx_vendors_status', 'status'),
        Index('idx_vendors_deleted_at', 'deleted_at'),
        Index('idx_vendors_company_name', 'company_name'),
    )

    def __repr__(self):
        return f"<Vendor(id={self.id}, company_name={self.company_name}, type={self.vendor_type})>"

    @property
    def is_active(self) -> bool:
        """Check if vendor is currently active"""
        return self.status == 'active'

    @property
    def contract_active(self) -> bool:
        """Check if contract is currently active"""
        if not self.contract_start_date or not self.contract_end_date:
            return False
        today = date_type.today()
        return self.contract_start_date <= today <= self.contract_end_date

    @property
    def contract_expiring_soon(self) -> bool:
        """Check if contract expires within 30 days"""
        if not self.contract_end_date:
            return False
        today = date_type.today()
        days_until_expiry = (self.contract_end_date - today).days
        return 0 <= days_until_expiry <= 30

    @property
    def insurance_expired(self) -> bool:
        """Check if insurance has expired"""
        if not self.insurance_expiry_date:
            return False
        return self.insurance_expiry_date < date_type.today()

    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)

        city_state_zip = []
        if self.city:
            city_state_zip.append(self.city)
        if self.state:
            city_state_zip.append(self.state)
        if self.postal_code:
            city_state_zip.append(self.postal_code)

        if city_state_zip:
            parts.append(", ".join(city_state_zip))

        if self.country and self.country != "USA":
            parts.append(self.country)

        return ", ".join(parts) if parts else ""

    def to_dict(self, include_relationships: bool = False):
        """Convert vendor to dictionary"""
        data = super().to_dict()

        # Convert date objects to strings
        if self.insurance_expiry_date:
            data['insurance_expiry_date'] = self.insurance_expiry_date.isoformat()
        if self.contract_start_date:
            data['contract_start_date'] = self.contract_start_date.isoformat()
        if self.contract_end_date:
            data['contract_end_date'] = self.contract_end_date.isoformat()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()

        # Convert decimal to float
        if self.contract_value:
            data['contract_value'] = float(self.contract_value)
        if self.performance_rating:
            data['performance_rating'] = float(self.performance_rating)

        # Add computed properties
        data['is_active'] = self.is_active
        data['contract_active'] = self.contract_active
        data['contract_expiring_soon'] = self.contract_expiring_soon
        data['insurance_expired'] = self.insurance_expired
        data['full_address'] = self.full_address

        # Convert arrays to lists
        if self.services_provided:
            data['services_provided'] = list(self.services_provided)
        if self.certifications:
            data['certifications'] = list(self.certifications)

        if include_relationships:
            try:
                if self.user:
                    data["user"] = {
                        "id": str(self.user.id),
                        "name": f"{self.user.first_name} {self.user.last_name}",
                        "email": self.user.email
                    }
            except:
                pass

        return data
