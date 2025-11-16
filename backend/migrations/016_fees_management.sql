-- Migration: 016_fees_management.sql
-- Description: Comprehensive fees and payment management system
-- Features: Multi-frequency payments, sibling discounts, bursaries, activity fees

-- ============================================================================
-- TABLE: fee_structures
-- Master fee structure per school/grade level with discount configurations
-- ============================================================================
CREATE TABLE fee_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    grade_level INTEGER NOT NULL CHECK (grade_level BETWEEN 1 AND 7),
    academic_year VARCHAR(9) NOT NULL, -- e.g., "2025-2026"

    -- Base fees for different payment frequencies
    yearly_amount DECIMAL(10, 2) NOT NULL CHECK (yearly_amount > 0),
    monthly_amount DECIMAL(10, 2) NOT NULL CHECK (monthly_amount > 0),
    weekly_amount DECIMAL(10, 2) NOT NULL CHECK (weekly_amount > 0),

    -- Payment frequency discounts (percentage 0-100)
    yearly_discount DECIMAL(5, 2) DEFAULT 0.00 CHECK (yearly_discount BETWEEN 0 AND 100),
    monthly_discount DECIMAL(5, 2) DEFAULT 0.00 CHECK (monthly_discount BETWEEN 0 AND 100),
    weekly_discount DECIMAL(5, 2) DEFAULT 0.00 CHECK (weekly_discount BETWEEN 0 AND 100),

    -- Sibling discount configuration (percentage 0-100)
    sibling_2_discount DECIMAL(5, 2) DEFAULT 10.00 CHECK (sibling_2_discount BETWEEN 0 AND 100),
    sibling_3_discount DECIMAL(5, 2) DEFAULT 15.00 CHECK (sibling_3_discount BETWEEN 0 AND 100),
    sibling_4_plus_discount DECIMAL(5, 2) DEFAULT 20.00 CHECK (sibling_4_plus_discount BETWEEN 0 AND 100),
    apply_sibling_to_all BOOLEAN DEFAULT false, -- true = all siblings, false = only younger

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),

    -- Ensure one active fee structure per school/grade/year
    UNIQUE(school_id, grade_level, academic_year)
);

CREATE INDEX idx_fee_structures_school_year ON fee_structures(school_id, academic_year);
CREATE INDEX idx_fee_structures_active ON fee_structures(is_active) WHERE is_active = true;

-- ============================================================================
-- TABLE: bursaries
-- Bursary/scholarship programs for financial aid
-- ============================================================================
CREATE TABLE bursaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Program details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    bursary_type VARCHAR(20) NOT NULL CHECK (bursary_type IN ('merit', 'need', 'sports', 'academic', 'other')),

    -- Coverage configuration
    coverage_type VARCHAR(20) NOT NULL CHECK (coverage_type IN ('percentage', 'fixed_amount')),
    coverage_value DECIMAL(10, 2) NOT NULL CHECK (coverage_value > 0),
    max_coverage_amount DECIMAL(10, 2), -- cap for percentage-based bursaries

    -- Eligibility
    academic_year VARCHAR(9) NOT NULL,
    eligible_grades INTEGER[] NOT NULL, -- array of grades 1-7
    max_recipients INTEGER, -- null = unlimited
    current_recipients INTEGER DEFAULT 0 CHECK (current_recipients >= 0),

    -- Status
    is_active BOOLEAN DEFAULT true,
    application_deadline DATE,

    -- Sponsor information
    sponsor_name VARCHAR(255),
    sponsor_contact TEXT,
    terms_and_conditions TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_bursaries_school_year ON bursaries(school_id, academic_year);
CREATE INDEX idx_bursaries_type ON bursaries(bursary_type);
CREATE INDEX idx_bursaries_active ON bursaries(is_active) WHERE is_active = true;

-- ============================================================================
-- TABLE: student_fees
-- Individual student fee records with calculated amounts
-- ============================================================================
CREATE TABLE student_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    academic_year VARCHAR(9) NOT NULL,

    -- Payment configuration
    payment_frequency VARCHAR(20) NOT NULL CHECK (payment_frequency IN ('yearly', 'monthly', 'weekly')),

    -- Base fee components
    base_tuition_amount DECIMAL(10, 2) NOT NULL CHECK (base_tuition_amount >= 0),
    activity_fees_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (activity_fees_amount >= 0),
    material_fees_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (material_fees_amount >= 0),
    other_fees_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (other_fees_amount >= 0),

    -- Payment frequency discount
    payment_discount_percent DECIMAL(5, 2) DEFAULT 0.00 CHECK (payment_discount_percent BETWEEN 0 AND 100),
    payment_discount_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (payment_discount_amount >= 0),

    -- Sibling discount
    sibling_discount_percent DECIMAL(5, 2) DEFAULT 0.00 CHECK (sibling_discount_percent BETWEEN 0 AND 100),
    sibling_discount_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (sibling_discount_amount >= 0),
    sibling_order INTEGER, -- 1st, 2nd, 3rd, 4th+ child

    -- Bursary
    bursary_id UUID REFERENCES bursaries(id),
    bursary_amount DECIMAL(10, 2) DEFAULT 0.00 CHECK (bursary_amount >= 0),

    -- Calculated totals
    total_before_discounts DECIMAL(10, 2) NOT NULL CHECK (total_before_discounts >= 0),
    total_discounts DECIMAL(10, 2) DEFAULT 0.00 CHECK (total_discounts >= 0),
    total_amount_due DECIMAL(10, 2) NOT NULL CHECK (total_amount_due >= 0),
    total_paid DECIMAL(10, 2) DEFAULT 0.00 CHECK (total_paid >= 0),
    balance_due DECIMAL(10, 2) NOT NULL CHECK (balance_due >= 0),

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'partial', 'paid', 'overdue', 'waived')),
    due_date DATE,
    last_payment_date DATE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),

    -- One fee record per student per academic year
    UNIQUE(school_id, student_id, academic_year)
);

CREATE INDEX idx_student_fees_school_student ON student_fees(school_id, student_id);
CREATE INDEX idx_student_fees_status ON student_fees(status);
CREATE INDEX idx_student_fees_year ON student_fees(academic_year);
CREATE INDEX idx_student_fees_overdue ON student_fees(due_date) WHERE status IN ('pending', 'partial', 'overdue');
CREATE INDEX idx_student_fees_bursary ON student_fees(bursary_id);

-- ============================================================================
-- TABLE: payments
-- Individual payment transactions
-- ============================================================================
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_fee_id UUID NOT NULL REFERENCES student_fees(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,

    -- Payment details
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('cash', 'card', 'bank_transfer', 'check', 'online', 'other')),

    -- Transaction tracking
    transaction_reference VARCHAR(255),
    receipt_number VARCHAR(100) UNIQUE NOT NULL,

    -- Payment allocation
    allocation_notes TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled')),
    refund_reason TEXT,
    refunded_at TIMESTAMP,

    -- Metadata
    processed_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_student_fee ON payments(student_fee_id);
CREATE INDEX idx_payments_student ON payments(student_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_payments_method ON payments(payment_method);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_receipt ON payments(receipt_number);

-- ============================================================================
-- TABLE: activity_fees
-- Fee structure for extracurricular activities
-- ============================================================================
CREATE TABLE activity_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,

    -- Fee structure
    academic_year VARCHAR(9) NOT NULL,
    fee_amount DECIMAL(10, 2) NOT NULL CHECK (fee_amount >= 0),
    fee_frequency VARCHAR(20) NOT NULL CHECK (fee_frequency IN ('one_time', 'yearly', 'quarterly', 'monthly')),

    -- Prorating for mid-term enrollment
    allow_prorate BOOLEAN DEFAULT true,
    prorate_calculation TEXT, -- description of prorating method

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),

    -- One fee structure per activity per year
    UNIQUE(school_id, activity_id, academic_year)
);

CREATE INDEX idx_activity_fees_activity ON activity_fees(activity_id);
CREATE INDEX idx_activity_fees_year ON activity_fees(academic_year);
CREATE INDEX idx_activity_fees_active ON activity_fees(is_active) WHERE is_active = true;

-- ============================================================================
-- TRIGGER: Update updated_at timestamps
-- ============================================================================
CREATE OR REPLACE FUNCTION update_fees_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_fee_structures_updated_at
    BEFORE UPDATE ON fee_structures
    FOR EACH ROW
    EXECUTE FUNCTION update_fees_updated_at();

CREATE TRIGGER update_student_fees_updated_at
    BEFORE UPDATE ON student_fees
    FOR EACH ROW
    EXECUTE FUNCTION update_fees_updated_at();

CREATE TRIGGER update_bursaries_updated_at
    BEFORE UPDATE ON bursaries
    FOR EACH ROW
    EXECUTE FUNCTION update_fees_updated_at();

CREATE TRIGGER update_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_fees_updated_at();

CREATE TRIGGER update_activity_fees_updated_at
    BEFORE UPDATE ON activity_fees
    FOR EACH ROW
    EXECUTE FUNCTION update_fees_updated_at();

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES (Multi-Tenancy)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE fee_structures ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_fees ENABLE ROW LEVEL SECURITY;
ALTER TABLE bursaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_fees ENABLE ROW LEVEL SECURITY;

-- Fee Structures Policies
CREATE POLICY fee_structures_isolation ON fee_structures
    USING (school_id IN (SELECT id FROM schools WHERE id = current_setting('app.current_school_id')::UUID));

-- Student Fees Policies
CREATE POLICY student_fees_isolation ON student_fees
    USING (school_id IN (SELECT id FROM schools WHERE id = current_setting('app.current_school_id')::UUID));

-- Bursaries Policies
CREATE POLICY bursaries_isolation ON bursaries
    USING (school_id IN (SELECT id FROM schools WHERE id = current_setting('app.current_school_id')::UUID));

-- Payments Policies
CREATE POLICY payments_isolation ON payments
    USING (school_id IN (SELECT id FROM schools WHERE id = current_setting('app.current_school_id')::UUID));

-- Activity Fees Policies
CREATE POLICY activity_fees_isolation ON activity_fees
    USING (school_id IN (SELECT id FROM schools WHERE id = current_setting('app.current_school_id')::UUID));

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON fee_structures TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON student_fees TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON bursaries TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON payments TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON activity_fees TO postgres;

-- ============================================================================
-- COMMENTS
-- ============================================================================
COMMENT ON TABLE fee_structures IS 'Master fee structure templates per school/grade/year with discount configurations';
COMMENT ON TABLE student_fees IS 'Individual student fee records with calculated amounts and payment tracking';
COMMENT ON TABLE bursaries IS 'Bursary and scholarship programs for financial aid';
COMMENT ON TABLE payments IS 'Payment transaction records with receipt tracking';
COMMENT ON TABLE activity_fees IS 'Fee structures for extracurricular activities';

COMMENT ON COLUMN fee_structures.yearly_discount IS 'Discount percentage for yearly payment (e.g., 10.00 = 10%)';
COMMENT ON COLUMN fee_structures.sibling_2_discount IS 'Discount for 2nd sibling (default 10%)';
COMMENT ON COLUMN fee_structures.apply_sibling_to_all IS 'Apply discount to all siblings or only younger ones';

COMMENT ON COLUMN student_fees.total_before_discounts IS 'Sum of all fees before any discounts';
COMMENT ON COLUMN student_fees.total_discounts IS 'Sum of payment + sibling discounts';
COMMENT ON COLUMN student_fees.total_amount_due IS 'Final amount after discounts and bursary';
COMMENT ON COLUMN student_fees.balance_due IS 'Remaining amount to be paid (total_amount_due - total_paid)';

COMMENT ON COLUMN bursaries.coverage_type IS 'percentage = % of fees, fixed_amount = specific dollar amount';
COMMENT ON COLUMN bursaries.coverage_value IS 'Percentage (0-100) or fixed dollar amount based on coverage_type';

COMMENT ON COLUMN payments.receipt_number IS 'Unique receipt identifier (format: RCPT-YYYY-NNNN)';
COMMENT ON COLUMN payments.transaction_reference IS 'External reference (bank confirmation, check number, etc.)';

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
