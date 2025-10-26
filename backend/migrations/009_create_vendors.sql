-- Migration: Create Vendors Table
-- Feature: Vendor Management (External Relationships)
-- Description: Manages external service providers and suppliers

CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Optional link to user account

    -- Company Information
    company_name VARCHAR(255) NOT NULL,
    business_number VARCHAR(50),  -- Tax ID / Business registration

    -- Vendor Classification
    vendor_type VARCHAR(50) NOT NULL,  -- 'food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other'
    category VARCHAR(100),  -- Subcategory
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

    -- Constraints
    CONSTRAINT chk_vendors_type CHECK (vendor_type IN ('food_service', 'supplies', 'maintenance', 'it_services', 'transportation', 'events', 'other')),
    CONSTRAINT chk_vendors_status CHECK (status IN ('active', 'inactive', 'suspended', 'terminated')),
    CONSTRAINT chk_vendors_rating CHECK (performance_rating IS NULL OR (performance_rating >= 0 AND performance_rating <= 5)),
    CONSTRAINT chk_vendors_contract_dates CHECK (contract_end_date IS NULL OR contract_start_date IS NULL OR contract_end_date >= contract_start_date),
    CONSTRAINT chk_vendors_contract_value CHECK (contract_value IS NULL OR contract_value >= 0),
    CONSTRAINT chk_vendors_total_orders CHECK (total_orders >= 0)
);

-- Indexes for performance
CREATE INDEX idx_vendors_school_id ON vendors(school_id);
CREATE INDEX idx_vendors_user_id ON vendors(user_id);
CREATE INDEX idx_vendors_type ON vendors(vendor_type);
CREATE INDEX idx_vendors_status ON vendors(status);
CREATE INDEX idx_vendors_deleted_at ON vendors(deleted_at);
CREATE INDEX idx_vendors_company_name ON vendors(company_name);
CREATE INDEX idx_vendors_contract_end ON vendors(contract_end_date) WHERE contract_end_date IS NOT NULL;

-- Row Level Security (RLS) Policies
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access vendors from their school
CREATE POLICY vendors_school_isolation ON vendors
    FOR ALL
    USING (school_id = current_setting('app.current_school_id', TRUE)::UUID);

-- Comments
COMMENT ON TABLE vendors IS 'External service providers and suppliers for schools';
COMMENT ON COLUMN vendors.vendor_type IS 'Type of vendor: food_service, supplies, maintenance, it_services, transportation, events, other';
COMMENT ON COLUMN vendors.status IS 'Vendor status: active, inactive, suspended, terminated';
COMMENT ON COLUMN vendors.performance_rating IS 'Average performance rating from 0.00 to 5.00';
COMMENT ON COLUMN vendors.services_provided IS 'Array of services the vendor provides';
COMMENT ON COLUMN vendors.certifications IS 'Array of vendor certifications';
COMMENT ON COLUMN vendors.tax_exempt IS 'Whether the vendor is tax exempt';
COMMENT ON COLUMN vendors.preferred IS 'Whether this is a preferred vendor';
