# Fees Management Feature Plan

## Overview
Comprehensive fees and payment management system for tracking student tuition, activity fees, payment schedules, discounts (sibling & payment type), and bursary support.

## Business Requirements

### Fee Structures
- **Payment Frequencies**: Yearly, Monthly, Weekly
- **Fee Types**:
  - Tuition fees (base school fees)
  - Activity fees (linked to enrolled activities)
  - Material fees
  - Other fees (customizable)

### Discount Types
1. **Payment Frequency Discounts**
   - Yearly payment: Higher discount (e.g., 10%)
   - Monthly payment: Medium discount (e.g., 5%)
   - Weekly payment: No discount or minimal (e.g., 0-2%)

2. **Sibling Discounts**
   - 2nd child: 10% off
   - 3rd child: 15% off
   - 4th+ child: 20% off
   - Applied to all siblings or only younger siblings (configurable)

3. **Bursary Support**
   - Partial or full fee coverage
   - Merit-based or need-based
   - Tracked separately for reporting
   - Can combine with other discounts (configurable)

### Payment Tracking
- Payment status: Pending, Partial, Paid, Overdue, Waived
- Payment method: Cash, Card, Bank Transfer, Check, Online
- Payment reconciliation and receipt generation
- Payment history and audit trail
- Parent payment portal access

### Activity Fees
- Activities can have associated costs
- Activity fees added to student's total fees
- Pro-rated for mid-term enrollment
- Separate tracking from tuition

## Database Schema

### Table: fee_structures
Master fee structure per school/grade level
```sql
CREATE TABLE fee_structures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    grade_level INTEGER NOT NULL CHECK (grade_level BETWEEN 1 AND 7),
    academic_year VARCHAR(9) NOT NULL, -- e.g., "2025-2026"

    -- Base fees
    yearly_amount DECIMAL(10, 2) NOT NULL,
    monthly_amount DECIMAL(10, 2) NOT NULL,
    weekly_amount DECIMAL(10, 2) NOT NULL,

    -- Payment frequency discounts (percentage)
    yearly_discount DECIMAL(5, 2) DEFAULT 0.00,
    monthly_discount DECIMAL(5, 2) DEFAULT 0.00,
    weekly_discount DECIMAL(5, 2) DEFAULT 0.00,

    -- Sibling discount configuration
    sibling_2_discount DECIMAL(5, 2) DEFAULT 10.00,
    sibling_3_discount DECIMAL(5, 2) DEFAULT 15.00,
    sibling_4_plus_discount DECIMAL(5, 2) DEFAULT 20.00,
    apply_sibling_to_all BOOLEAN DEFAULT false, -- or just younger siblings

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),

    UNIQUE(school_id, grade_level, academic_year)
);
```

### Table: student_fees
Individual student fee records
```sql
CREATE TABLE student_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    academic_year VARCHAR(9) NOT NULL,

    -- Payment configuration
    payment_frequency VARCHAR(20) NOT NULL CHECK (payment_frequency IN ('yearly', 'monthly', 'weekly')),

    -- Base fee calculation
    base_tuition_amount DECIMAL(10, 2) NOT NULL,
    activity_fees_amount DECIMAL(10, 2) DEFAULT 0.00,
    material_fees_amount DECIMAL(10, 2) DEFAULT 0.00,
    other_fees_amount DECIMAL(10, 2) DEFAULT 0.00,

    -- Discounts applied
    payment_discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    payment_discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    sibling_discount_percent DECIMAL(5, 2) DEFAULT 0.00,
    sibling_discount_amount DECIMAL(10, 2) DEFAULT 0.00,

    -- Bursary
    bursary_id UUID REFERENCES bursaries(id),
    bursary_amount DECIMAL(10, 2) DEFAULT 0.00,

    -- Final amounts
    total_before_discounts DECIMAL(10, 2) NOT NULL,
    total_discounts DECIMAL(10, 2) DEFAULT 0.00,
    total_amount_due DECIMAL(10, 2) NOT NULL,
    total_paid DECIMAL(10, 2) DEFAULT 0.00,
    balance_due DECIMAL(10, 2) NOT NULL,

    -- Status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'partial', 'paid', 'overdue', 'waived')),
    due_date DATE,

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),

    UNIQUE(school_id, student_id, academic_year)
);
```

### Table: bursaries
Bursary/scholarship programs
```sql
CREATE TABLE bursaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,
    bursary_type VARCHAR(20) NOT NULL CHECK (bursary_type IN ('merit', 'need', 'sports', 'academic', 'other')),

    -- Coverage
    coverage_type VARCHAR(20) NOT NULL CHECK (coverage_type IN ('percentage', 'fixed_amount')),
    coverage_value DECIMAL(10, 2) NOT NULL, -- percentage (0-100) or fixed amount
    max_coverage_amount DECIMAL(10, 2), -- cap for percentage-based

    -- Eligibility
    academic_year VARCHAR(9) NOT NULL,
    eligible_grades INTEGER[], -- array of grades 1-7
    max_recipients INTEGER, -- null = unlimited
    current_recipients INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT true,
    application_deadline DATE,

    -- Metadata
    sponsor_name VARCHAR(255),
    sponsor_contact TEXT,
    terms_and_conditions TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);
```

### Table: payments
Individual payment transactions
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    student_fee_id UUID NOT NULL REFERENCES student_fees(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,

    -- Payment details
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('cash', 'card', 'bank_transfer', 'check', 'online', 'other')),

    -- Transaction tracking
    transaction_reference VARCHAR(255), -- bank ref, check number, etc.
    receipt_number VARCHAR(100) UNIQUE,

    -- Payment allocation
    allocation_notes TEXT, -- which fees this payment covers

    -- Status
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'cancelled')),

    -- Metadata
    processed_by UUID REFERENCES users(id),
    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table: activity_fees
Fee structure for activities
```sql
CREATE TABLE activity_fees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,

    -- Fee structure
    academic_year VARCHAR(9) NOT NULL,
    fee_amount DECIMAL(10, 2) NOT NULL,
    fee_frequency VARCHAR(20) NOT NULL CHECK (fee_frequency IN ('one_time', 'yearly', 'quarterly', 'monthly')),

    -- Prorating
    allow_prorate BOOLEAN DEFAULT true,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(school_id, activity_id, academic_year)
);
```

### Indexes
```sql
CREATE INDEX idx_fee_structures_school_year ON fee_structures(school_id, academic_year);
CREATE INDEX idx_student_fees_school_student ON student_fees(school_id, student_id);
CREATE INDEX idx_student_fees_status ON student_fees(status);
CREATE INDEX idx_student_fees_year ON student_fees(academic_year);
CREATE INDEX idx_payments_student_fee ON payments(student_fee_id);
CREATE INDEX idx_payments_student ON payments(student_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_bursaries_school_year ON bursaries(school_id, academic_year);
CREATE INDEX idx_activity_fees_activity ON activity_fees(activity_id);
```

## API Endpoints

### Fee Structures
- `POST /api/v1/fee-structures` - Create fee structure
- `GET /api/v1/fee-structures` - List fee structures (filter by school, year, grade)
- `GET /api/v1/fee-structures/{id}` - Get single fee structure
- `PUT /api/v1/fee-structures/{id}` - Update fee structure
- `DELETE /api/v1/fee-structures/{id}` - Delete fee structure

### Student Fees
- `POST /api/v1/student-fees` - Create student fee record
- `POST /api/v1/student-fees/calculate` - Calculate fees for student (preview)
- `GET /api/v1/student-fees` - List student fees (filter by school, student, year, status)
- `GET /api/v1/student-fees/{id}` - Get single student fee record
- `GET /api/v1/student-fees/student/{student_id}` - Get all fees for a student
- `PUT /api/v1/student-fees/{id}` - Update student fee record
- `PATCH /api/v1/student-fees/{id}/status` - Update fee status
- `DELETE /api/v1/student-fees/{id}` - Delete student fee record

### Payments
- `POST /api/v1/payments` - Record new payment
- `GET /api/v1/payments` - List payments (filter by school, student, date range, method)
- `GET /api/v1/payments/{id}` - Get single payment
- `GET /api/v1/payments/student/{student_id}` - Get all payments for a student
- `GET /api/v1/payments/{id}/receipt` - Generate payment receipt (PDF)
- `PUT /api/v1/payments/{id}` - Update payment
- `POST /api/v1/payments/{id}/refund` - Process refund
- `DELETE /api/v1/payments/{id}` - Delete payment

### Bursaries
- `POST /api/v1/bursaries` - Create bursary program
- `GET /api/v1/bursaries` - List bursaries (filter by school, year, type)
- `GET /api/v1/bursaries/{id}` - Get single bursary
- `GET /api/v1/bursaries/{id}/recipients` - List bursary recipients
- `POST /api/v1/bursaries/{id}/assign` - Assign bursary to student
- `PUT /api/v1/bursaries/{id}` - Update bursary
- `DELETE /api/v1/bursaries/{id}` - Delete bursary

### Activity Fees
- `POST /api/v1/activity-fees` - Create activity fee structure
- `GET /api/v1/activity-fees` - List activity fees
- `GET /api/v1/activity-fees/{id}` - Get single activity fee
- `PUT /api/v1/activity-fees/{id}` - Update activity fee
- `DELETE /api/v1/activity-fees/{id}` - Delete activity fee

### Reports
- `GET /api/v1/reports/fees/summary` - School-wide fee summary (by year, grade, status)
- `GET /api/v1/reports/fees/outstanding` - Outstanding balances report
- `GET /api/v1/reports/payments/revenue` - Revenue report (by date range, method)
- `GET /api/v1/reports/bursaries/usage` - Bursary utilization report

## Business Logic

### Fee Calculation Algorithm
```
1. Get base tuition from fee_structure for student's grade and year
2. Apply payment frequency discount
3. Calculate sibling discount:
   - Query all students with same parent(s)
   - Determine sibling order (by age or enrollment date)
   - Apply appropriate sibling discount
4. Add activity fees from enrolled activities
5. Apply bursary (if assigned)
6. Calculate final totals:
   total_before_discounts = base_tuition + activity_fees + other_fees
   total_discounts = payment_discount + sibling_discount
   total_after_discounts = total_before_discounts - total_discounts
   total_amount_due = total_after_discounts - bursary_amount
   balance_due = total_amount_due - total_paid
```

### Payment Processing
```
1. Validate payment amount > 0
2. Validate student_fee exists and is not fully paid
3. Create payment record
4. Update student_fee.total_paid += payment.amount
5. Update student_fee.balance_due = total_amount_due - total_paid
6. Update student_fee.status:
   - 'paid' if balance_due <= 0
   - 'partial' if 0 < balance_due < total_amount_due
   - 'pending' if total_paid == 0
7. Generate receipt number (format: RCPT-YYYY-NNNN)
8. Create audit log entry
9. Send payment confirmation email to parent
```

### Overdue Detection
```
- Run nightly job to check student_fees.due_date
- If due_date < today AND balance_due > 0:
  - Update status to 'overdue'
  - Send reminder email to parent
  - Flag account for follow-up
```

## UX Flows

### Administrator Flows
1. **Setup Fee Structures** (start of academic year)
   - Navigate to Fees > Fee Structures
   - Create fee structure per grade level
   - Set payment frequency discounts
   - Configure sibling discounts
   - Save and activate

2. **Create Bursary Programs**
   - Navigate to Fees > Bursaries
   - Create new bursary
   - Set coverage type and value
   - Define eligibility criteria
   - Save program

3. **Assign Fees to Students** (bulk or individual)
   - Navigate to Fees > Student Fees
   - Select academic year and grade
   - Bulk assign fees to all students OR
   - Create individual fee record
   - System calculates discounts automatically
   - Review and confirm

4. **Record Payments**
   - Navigate to Fees > Payments
   - Search for student
   - Enter payment amount and method
   - Generate receipt
   - Send receipt to parent

5. **View Reports**
   - Navigate to Reports > Fees
   - Select report type (summary, outstanding, revenue)
   - Apply filters (date range, grade, status)
   - Export to PDF/Excel

### Parent Portal Flows
1. **View Fee Statement**
   - Login to parent portal
   - Navigate to Fees section
   - View current balance and payment history
   - Download statement

2. **Make Online Payment** (future enhancement)
   - View outstanding balance
   - Click "Pay Now"
   - Enter payment details
   - Confirm payment
   - Receive digital receipt

### Teacher Flows
1. **View Student Fee Status**
   - Access student profile
   - View fee status indicator (paid/partial/overdue)
   - View payment history (read-only)

## Validation Rules

### Fee Structure
- yearly_amount must be > 0
- monthly_amount * 12 should be >= yearly_amount (yearly discount)
- weekly_amount * 52 should be >= yearly_amount (yearly discount)
- Discount percentages: 0-100
- grade_level: 1-7
- academic_year format: "YYYY-YYYY" (e.g., "2025-2026")

### Student Fee
- payment_frequency must match available fee structure
- Cannot create duplicate for same student + academic year
- total_amount_due must be >= 0
- balance_due = total_amount_due - total_paid
- status transitions: pending → partial → paid OR pending → overdue

### Payment
- amount must be > 0
- amount cannot exceed student_fee.balance_due (overpayment prevention)
- payment_date cannot be in future
- receipt_number must be unique

### Bursary
- coverage_value: 0-100 for percentage, > 0 for fixed
- Cannot exceed max_recipients
- Cannot assign if bursary is inactive
- Cannot combine multiple bursaries per student (configurable)

## Security & Compliance

### Multi-Tenancy
- All tables include school_id
- RLS policies enforce data isolation
- Parents can only view their children's fees
- Teachers have read-only access to student fee status

### GDPR Compliance
- Audit all payment transactions
- Allow data export for parents
- Support data deletion (archive payments before deletion)
- Anonymize financial data on student deletion (optional)

### Role-Based Access
- **Administrator**: Full CRUD on all fee entities
- **Accountant** (new role?): Manage fees and payments, view reports
- **Teacher**: Read-only view of student fee status
- **Parent**: View own children's fees and payment history
- **Student**: View own fee status (read-only)

## Testing Scenarios

### Unit Tests
- Fee calculation with various discount combinations
- Sibling discount calculation (2, 3, 4+ siblings)
- Bursary application (percentage vs fixed)
- Payment allocation and balance updates
- Overdue status detection

### Integration Tests
- Create fee structure → assign to students → verify calculations
- Record payment → verify balance update → check status change
- Assign bursary → verify discount application
- Enroll in activity → verify activity fee added

### E2E Tests (Playwright)
- Admin creates fee structure
- Admin assigns fees to student
- Admin records payment
- Parent views fee statement
- Generate and download receipt

## Migration Strategy

### Phase 1: Database Setup (Week 1)
- Create migration file with all tables
- Apply migration to dev environment
- Create sample data (3 fee structures, 10 student fees, 5 payments)
- Test data integrity and relationships

### Phase 2: Backend API (Week 2)
- Implement models, repositories, services
- Create controllers with validation
- Test all endpoints manually
- Write unit and integration tests

### Phase 3: Frontend UI (Week 3)
- Create TypeScript types and API services
- Build Pinia stores
- Create Vue components (lists, forms, detail views)
- Implement routing and navigation

### Phase 4: Reports & Portal (Week 4)
- Build reporting endpoints
- Create report UI components
- Implement parent portal views
- Add receipt generation

### Phase 5: Testing & Documentation (Week 5)
- Complete E2E test suite
- Performance testing with large datasets
- Update all documentation
- User acceptance testing

## Future Enhancements
- Online payment gateway integration (Stripe, PayPal)
- Recurring payment automation
- Late fee calculation and penalties
- Payment plans and installment scheduling
- Multi-currency support
- Email/SMS payment reminders
- Parent payment portal with dashboard
- Financial aid application workflow
- Scholarship management
- Invoice customization and branding
