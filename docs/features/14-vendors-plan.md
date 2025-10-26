# Feature Plan: Vendors (External Relationships)

**Feature ID:** 14
**Priority:** P2
**Dependencies:** Users, Schools
**Status:** Planning

## Overview

Vendor management system for tracking external service providers and suppliers that work with the school. This includes food service vendors, supply vendors, maintenance contractors, event vendors, and other external parties.

## Use Cases

### Primary Use Cases
1. **Administrator** manages vendor relationships
2. **Administrator** tracks vendor performance and ratings
3. **Administrator** manages contracts and service agreements
4. **Administrator** processes orders and payments
5. **Vendor** views their service schedule and orders
6. **Vendor** communicates with school administration

### User Stories
- As an administrator, I want to maintain a list of approved vendors
- As an administrator, I want to track vendor contracts and renewal dates
- As an administrator, I want to rate vendor performance
- As an administrator, I want to track orders and payments to vendors
- As a vendor, I want to view my upcoming service schedule
- As a vendor, I want to communicate with the school
- As an administrator, I want to generate vendor reports

## Database Schema

### vendors table
```sql
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Optional link to user account

    -- Company Information
    company_name VARCHAR(255) NOT NULL,
    business_number VARCHAR(50),  -- Tax ID / Business registration

    -- Vendor Classification
    vendor_type VARCHAR(50) NOT NULL,  -- 'food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other'
    category VARCHAR(100),  -- Subcategory (e.g., 'office_supplies', 'cafeteria', 'janitorial')
    services_provided TEXT[],  -- Array of services

    -- Contact Information
    primary_contact_name VARCHAR(255),
    primary_contact_title VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    phone_alt VARCHAR(20),
    website VARCHAR(500),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',

    -- Business Details
    description TEXT,
    certifications TEXT[],  -- Array of certifications
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,

    -- Contract & Financial
    contract_start_date DATE,
    contract_end_date DATE,
    contract_value DECIMAL(12, 2),
    payment_terms VARCHAR(100),  -- 'net_30', 'net_60', 'upon_completion', etc.
    tax_exempt BOOLEAN DEFAULT FALSE,

    -- Performance & Status
    status VARCHAR(20) DEFAULT 'active' NOT NULL,  -- 'active', 'inactive', 'suspended', 'terminated'
    performance_rating DECIMAL(3, 2),  -- 0.00 to 5.00
    total_orders INTEGER DEFAULT 0,

    -- Preferences
    preferred BOOLEAN DEFAULT FALSE,
    notes TEXT,

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by_id UUID REFERENCES users(id),
    updated_by_id UUID REFERENCES users(id),

    CONSTRAINT chk_vendors_type CHECK (vendor_type IN ('food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other')),
    CONSTRAINT chk_vendors_status CHECK (status IN ('active', 'inactive', 'suspended', 'terminated')),
    CONSTRAINT chk_vendors_rating CHECK (performance_rating IS NULL OR (performance_rating >= 0 AND performance_rating <= 5)),
    CONSTRAINT chk_vendors_contract_dates CHECK (contract_end_date IS NULL OR contract_start_date IS NULL OR contract_end_date >= contract_start_date)
);

CREATE INDEX idx_vendors_school_id ON vendors(school_id);
CREATE INDEX idx_vendors_user_id ON vendors(user_id);
CREATE INDEX idx_vendors_type ON vendors(vendor_type);
CREATE INDEX idx_vendors_status ON vendors(status);
CREATE INDEX idx_vendors_deleted_at ON vendors(deleted_at);
CREATE INDEX idx_vendors_company_name ON vendors(company_name);
```

### vendor_orders table (Optional - for order tracking)
```sql
CREATE TABLE vendor_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Order Information
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    required_date DATE,
    delivery_date DATE,

    -- Order Details
    description TEXT,
    items JSONB,  -- Array of items with quantities and prices

    -- Financial
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    tax_amount DECIMAL(12, 2) DEFAULT 0.00,
    shipping_amount DECIMAL(12, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00,

    -- Status
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,  -- 'pending', 'approved', 'ordered', 'delivered', 'completed', 'cancelled'
    payment_status VARCHAR(20) DEFAULT 'unpaid' NOT NULL,  -- 'unpaid', 'partial', 'paid'
    amount_paid DECIMAL(12, 2) DEFAULT 0.00,

    -- Additional Info
    notes TEXT,
    approval_required BOOLEAN DEFAULT TRUE,
    approved_by_id UUID REFERENCES users(id),
    approved_at TIMESTAMP,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    created_by_id UUID REFERENCES users(id),
    updated_by_id UUID REFERENCES users(id),

    CONSTRAINT chk_vendor_orders_status CHECK (status IN ('pending', 'approved', 'ordered', 'delivered', 'completed', 'cancelled')),
    CONSTRAINT chk_vendor_orders_payment_status CHECK (payment_status IN ('unpaid', 'partial', 'paid')),
    CONSTRAINT chk_vendor_orders_amounts CHECK (subtotal >= 0 AND total_amount >= 0 AND amount_paid >= 0)
);

CREATE INDEX idx_vendor_orders_vendor_id ON vendor_orders(vendor_id);
CREATE INDEX idx_vendor_orders_school_id ON vendor_orders(school_id);
CREATE INDEX idx_vendor_orders_status ON vendor_orders(status);
CREATE INDEX idx_vendor_orders_order_date ON vendor_orders(order_date);
```

### vendor_reviews table (Optional - for performance tracking)
```sql
CREATE TABLE vendor_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    order_id UUID REFERENCES vendor_orders(id) ON DELETE SET NULL,

    -- Review Details
    rating DECIMAL(3, 2) NOT NULL,  -- 0.00 to 5.00
    review_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Review Categories
    quality_rating INTEGER,  -- 1-5
    timeliness_rating INTEGER,  -- 1-5
    communication_rating INTEGER,  -- 1-5
    value_rating INTEGER,  -- 1-5

    -- Comments
    comments TEXT,

    -- Recommendation
    would_recommend BOOLEAN,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES users(id),

    CONSTRAINT chk_vendor_reviews_rating CHECK (rating >= 0 AND rating <= 5),
    CONSTRAINT chk_vendor_reviews_quality CHECK (quality_rating IS NULL OR (quality_rating >= 1 AND quality_rating <= 5)),
    CONSTRAINT chk_vendor_reviews_timeliness CHECK (timeliness_rating IS NULL OR (timeliness_rating >= 1 AND timeliness_rating <= 5)),
    CONSTRAINT chk_vendor_reviews_communication CHECK (communication_rating IS NULL OR (communication_rating >= 1 AND communication_rating <= 5)),
    CONSTRAINT chk_vendor_reviews_value CHECK (value_rating IS NULL OR (value_rating >= 1 AND value_rating <= 5))
);

CREATE INDEX idx_vendor_reviews_vendor_id ON vendor_reviews(vendor_id);
CREATE INDEX idx_vendor_reviews_order_id ON vendor_orders(id);
```

## API Endpoints

### Vendor CRUD
- `POST /api/v1/vendors` - Create vendor
- `GET /api/v1/vendors` - List vendors (with filters)
- `GET /api/v1/vendors/{id}` - Get vendor by ID
- `PUT /api/v1/vendors/{id}` - Update vendor
- `DELETE /api/v1/vendors/{id}` - Soft delete vendor
- `PATCH /api/v1/vendors/{id}/status` - Update vendor status
- `PATCH /api/v1/vendors/{id}/rating` - Update performance rating
- `GET /api/v1/vendors/type/{type}` - Get vendors by type
- `GET /api/v1/vendors/search` - Search vendors

### Vendor Orders (Optional Phase 2)
- `POST /api/v1/vendors/{vendor_id}/orders` - Create order
- `GET /api/v1/vendors/{vendor_id}/orders` - Get vendor orders
- `GET /api/v1/vendors/orders/{order_id}` - Get order by ID
- `PUT /api/v1/vendors/orders/{order_id}` - Update order
- `PATCH /api/v1/vendors/orders/{order_id}/status` - Update order status
- `PATCH /api/v1/vendors/orders/{order_id}/approve` - Approve order
- `POST /api/v1/vendors/orders/{order_id}/payment` - Record payment

### Vendor Reviews (Optional Phase 2)
- `POST /api/v1/vendors/{vendor_id}/reviews` - Add review
- `GET /api/v1/vendors/{vendor_id}/reviews` - Get vendor reviews
- `GET /api/v1/vendors/{vendor_id}/rating-summary` - Get rating statistics

### Statistics
- `GET /api/v1/vendors/statistics/summary` - Get vendor statistics

## Business Rules

### Vendor Management
1. Company name must be unique within a school
2. Contact email must be valid format
3. Only administrators can create/edit vendors
4. Vendors can be linked to a user account (persona: vendor)
5. Soft delete maintains audit trail
6. Performance rating must be between 0 and 5

### Contract Management
1. Contract end date must be after start date
2. Alert when contract is expiring (30 days before)
3. Insurance expiry tracking with alerts

### Status Transitions
- Active → Inactive (vendor no longer providing services)
- Active → Suspended (temporary suspension)
- Active/Inactive/Suspended → Terminated (permanent removal)

### Vendor Types
- `food_service` - Cafeteria, catering, vending
- `supplies` - Office supplies, educational materials, equipment
- `maintenance` - Janitorial, repairs, grounds keeping
- `it_services` - Technology support, software
- `transportation` - Bus services, field trip transportation
- `events` - Event planning, entertainment, decorations
- `other` - Miscellaneous vendors

## Sample Data

```sql
-- Sample vendors
INSERT INTO vendors (school_id, company_name, vendor_type, category, email, phone, status) VALUES
('60da2256-81fc-4ca5-bf6b-467b8d371c61', 'Fresh Foods Catering', 'food_service', 'cafeteria', 'orders@freshfoods.com', '+1234567890', 'active'),
('60da2256-81fc-4ca5-bf6b-467b8d371c61', 'Office Depot', 'supplies', 'office_supplies', 'schools@officedepot.com', '+0987654321', 'active'),
('60da2256-81fc-4ca5-bf6b-467b8d371c61', 'Clean & Shine Services', 'maintenance', 'janitorial', 'contact@cleanshine.com', '+1122334455', 'active'),
('60da2256-81fc-4ca5-bf6b-467b8d371c61', 'TechSupport Pro', 'it_services', 'it_support', 'help@techsupportpro.com', '+5544332211', 'active'),
('60da2256-81fc-4ca5-bf6b-467b8d371c61', 'Yellow Bus Company', 'transportation', 'school_bus', 'dispatch@yellowbus.com', '+6677889900', 'active');
```

## Frontend Components

### VendorList.vue
- List all vendors with filters (type, status)
- Search by company name
- Display vendor cards with key info
- Quick actions (view, edit, change status)
- Statistics dashboard

### VendorForm.vue
- Create/edit vendor form
- All vendor fields
- Contract date pickers
- Address fields
- Certification management

### VendorDetail.vue
- Full vendor information display
- Contract details
- Contact information
- Order history (if implemented)
- Review history (if implemented)
- Performance metrics

### VendorReviews.vue (Optional Phase 2)
- Add vendor review
- View review history
- Rating statistics

## TypeScript Types

```typescript
export type VendorType = 'food_service' | 'supplies' | 'maintenance' | 'it_services' | 'transportation' | 'events' | 'other'
export type VendorStatus = 'active' | 'inactive' | 'suspended' | 'terminated'

export interface Vendor {
  id: string
  school_id: string
  user_id?: string

  // Company Info
  company_name: string
  business_number?: string
  vendor_type: VendorType
  category?: string
  services_provided?: string[]

  // Contact
  primary_contact_name?: string
  primary_contact_title?: string
  email?: string
  phone?: string
  phone_alt?: string
  website?: string

  // Address
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string

  // Business Details
  description?: string
  certifications?: string[]
  insurance_policy_number?: string
  insurance_expiry_date?: string

  // Contract
  contract_start_date?: string
  contract_end_date?: string
  contract_value?: number
  payment_terms?: string
  tax_exempt?: boolean

  // Performance
  status: VendorStatus
  performance_rating?: number
  total_orders?: number
  preferred?: boolean
  notes?: string

  // Audit
  created_at: string
  updated_at: string
  deleted_at?: string
}
```

## Implementation Phases

### Phase 1: Core Vendor Management (MVP)
- Vendor CRUD operations
- Basic vendor information
- Status management
- Search and filter
- Frontend UI components

### Phase 2: Orders & Reviews (Future Enhancement)
- Order tracking system
- Payment management
- Vendor review system
- Performance analytics

## Validation Rules

1. **Company Name**: Required, max 255 characters, unique per school
2. **Vendor Type**: Required, must be valid enum value
3. **Email**: Must be valid email format if provided
4. **Phone**: Valid phone number format if provided
5. **Contract Dates**: End date must be after start date if both provided
6. **Performance Rating**: 0.00 to 5.00 if provided
7. **Status**: Must be valid enum value

## Access Control

- **Administrator**: Full access (create, read, update, delete)
- **Teacher**: Read-only access to vendor list
- **Vendor**: Access to own vendor profile and related orders
- **Parent/Student**: No access

## Success Criteria

1. Administrators can create and manage vendor profiles
2. Vendor information is easily searchable and filterable
3. Contract expiry alerts function correctly
4. Performance ratings are accurately calculated
5. Multi-tenancy properly enforced
6. All audit trails maintained

## Future Enhancements

1. Order management system
2. Vendor review and rating system
3. Contract document upload
4. Email notifications for contract renewal
5. Vendor portal for self-service
6. Purchase order workflow
7. Budget tracking integration
8. Vendor comparison reports
