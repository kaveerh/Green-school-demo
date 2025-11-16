-- Sample Data for Fees Management
-- Creates realistic test data for fee structures, bursaries, student fees, and payments

-- Get the test school ID
DO $$
DECLARE
    v_school_id UUID;
    v_admin_id UUID;
    v_student1_id UUID;
    v_student2_id UUID;
    v_student3_id UUID;
    v_fee_struct_grade1_id UUID;
    v_fee_struct_grade3_id UUID;
    v_fee_struct_grade5_id UUID;
    v_bursary_merit_id UUID;
    v_bursary_need_id UUID;
    v_student_fee1_id UUID;
    v_student_fee2_id UUID;
    v_student_fee3_id UUID;
    v_payment1_id UUID;
    v_payment2_id UUID;
    v_activity1_id UUID;
    v_activity2_id UUID;
BEGIN
    -- Get existing test data IDs
    SELECT id INTO v_school_id FROM schools LIMIT 1;
    SELECT id INTO v_admin_id FROM users WHERE persona = 'administrator' LIMIT 1;

    -- Get some student IDs for fee assignment
    SELECT id INTO v_student1_id FROM students ORDER BY created_at LIMIT 1 OFFSET 0;
    SELECT id INTO v_student2_id FROM students ORDER BY created_at LIMIT 1 OFFSET 1;
    SELECT id INTO v_student3_id FROM students ORDER BY created_at LIMIT 1 OFFSET 2;

    -- Get activity IDs
    SELECT id INTO v_activity1_id FROM activities ORDER BY created_at LIMIT 1 OFFSET 0;
    SELECT id INTO v_activity2_id FROM activities ORDER BY created_at LIMIT 1 OFFSET 1;

    -- =========================================================================
    -- FEE STRUCTURES (3 grade levels for 2025-2026)
    -- =========================================================================

    -- Grade 1 Fee Structure
    INSERT INTO fee_structures (
        id, school_id, grade_level, academic_year,
        yearly_amount, monthly_amount, weekly_amount,
        yearly_discount, monthly_discount, weekly_discount,
        sibling_2_discount, sibling_3_discount, sibling_4_plus_discount,
        apply_sibling_to_all, is_active, created_by
    ) VALUES (
        gen_random_uuid(), v_school_id, 1, '2025-2026',
        8000.00, 750.00, 200.00,  -- yearly is cheaper per month than monthly/weekly
        10.00, 5.00, 0.00,  -- 10% off yearly, 5% off monthly, 0% off weekly
        10.00, 15.00, 20.00,  -- sibling discounts
        false, true, v_admin_id
    ) RETURNING id INTO v_fee_struct_grade1_id;

    -- Grade 3 Fee Structure (slightly higher fees)
    INSERT INTO fee_structures (
        id, school_id, grade_level, academic_year,
        yearly_amount, monthly_amount, weekly_amount,
        yearly_discount, monthly_discount, weekly_discount,
        sibling_2_discount, sibling_3_discount, sibling_4_plus_discount,
        apply_sibling_to_all, is_active, created_by
    ) VALUES (
        gen_random_uuid(), v_school_id, 3, '2025-2026',
        9000.00, 850.00, 225.00,
        10.00, 5.00, 0.00,
        10.00, 15.00, 20.00,
        false, true, v_admin_id
    ) RETURNING id INTO v_fee_struct_grade3_id;

    -- Grade 5 Fee Structure (highest fees for upper grades)
    INSERT INTO fee_structures (
        id, school_id, grade_level, academic_year,
        yearly_amount, monthly_amount, weekly_amount,
        yearly_discount, monthly_discount, weekly_discount,
        sibling_2_discount, sibling_3_discount, sibling_4_plus_discount,
        apply_sibling_to_all, is_active, created_by
    ) VALUES (
        gen_random_uuid(), v_school_id, 5, '2025-2026',
        10000.00, 950.00, 250.00,
        10.00, 5.00, 0.00,
        10.00, 15.00, 20.00,
        false, true, v_admin_id
    ) RETURNING id INTO v_fee_struct_grade5_id;

    -- =========================================================================
    -- BURSARIES (2 programs)
    -- =========================================================================

    -- Merit-based Bursary (50% coverage)
    INSERT INTO bursaries (
        id, school_id, name, description, bursary_type,
        coverage_type, coverage_value, max_coverage_amount,
        academic_year, eligible_grades, max_recipients, current_recipients,
        is_active, application_deadline,
        sponsor_name, sponsor_contact,
        created_by
    ) VALUES (
        gen_random_uuid(), v_school_id,
        'Academic Excellence Scholarship',
        'Merit-based scholarship for students with outstanding academic performance',
        'merit',
        'percentage', 50.00, 5000.00,  -- 50% coverage, max $5000
        '2025-2026', ARRAY[1,2,3,4,5,6,7], 10, 0,
        true, '2025-08-15',
        'Green School Foundation',
        'foundation@greenschool.edu',
        v_admin_id
    ) RETURNING id INTO v_bursary_merit_id;

    -- Need-based Bursary (fixed amount)
    INSERT INTO bursaries (
        id, school_id, name, description, bursary_type,
        coverage_type, coverage_value, max_coverage_amount,
        academic_year, eligible_grades, max_recipients, current_recipients,
        is_active, application_deadline,
        sponsor_name, sponsor_contact,
        created_by
    ) VALUES (
        gen_random_uuid(), v_school_id,
        'Community Assistance Fund',
        'Need-based financial aid for families requiring support',
        'need',
        'fixed_amount', 2000.00, NULL,  -- fixed $2000 per recipient
        '2025-2026', ARRAY[1,2,3,4,5,6,7], 20, 0,
        true, '2025-09-01',
        'Green Community Partners',
        'partners@greencommunity.org',
        v_admin_id
    ) RETURNING id INTO v_bursary_need_id;

    -- =========================================================================
    -- ACTIVITY FEES (2 activities)
    -- =========================================================================

    IF v_activity1_id IS NOT NULL THEN
        INSERT INTO activity_fees (
            school_id, activity_id, academic_year,
            fee_amount, fee_frequency, allow_prorate,
            description, is_active, created_by
        ) VALUES (
            v_school_id, v_activity1_id, '2025-2026',
            300.00, 'yearly', true,
            'Annual activity fee for sports/arts programs',
            true, v_admin_id
        );
    END IF;

    IF v_activity2_id IS NOT NULL THEN
        INSERT INTO activity_fees (
            school_id, activity_id, academic_year,
            fee_amount, fee_frequency, allow_prorate,
            description, is_active, created_by
        ) VALUES (
            v_school_id, v_activity2_id, '2025-2026',
            150.00, 'quarterly', true,
            'Quarterly fee for specialized activities',
            true, v_admin_id
        );
    END IF;

    -- =========================================================================
    -- STUDENT FEES (3 students with different scenarios)
    -- =========================================================================

    -- Student 1: Yearly payment with no discounts, no bursary
    IF v_student1_id IS NOT NULL THEN
        INSERT INTO student_fees (
            id, school_id, student_id, academic_year,
            payment_frequency,
            base_tuition_amount, activity_fees_amount, material_fees_amount, other_fees_amount,
            payment_discount_percent, payment_discount_amount,
            sibling_discount_percent, sibling_discount_amount, sibling_order,
            bursary_id, bursary_amount,
            total_before_discounts, total_discounts, total_amount_due,
            total_paid, balance_due,
            status, due_date, created_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student1_id, '2025-2026',
            'yearly',
            8000.00, 300.00, 0.00, 0.00,  -- tuition + activity fee
            10.00, 800.00,  -- 10% yearly discount = $800
            0.00, 0.00, 1,  -- no sibling discount (first child)
            NULL, 0.00,  -- no bursary
            8300.00, 800.00, 7500.00,  -- totals
            0.00, 7500.00,  -- not paid yet
            'pending', '2025-09-15', v_admin_id
        ) RETURNING id INTO v_student_fee1_id;
    END IF;

    -- Student 2: Monthly payment with sibling discount (2nd child) + merit bursary
    IF v_student2_id IS NOT NULL THEN
        INSERT INTO student_fees (
            id, school_id, student_id, academic_year,
            payment_frequency,
            base_tuition_amount, activity_fees_amount, material_fees_amount, other_fees_amount,
            payment_discount_percent, payment_discount_amount,
            sibling_discount_percent, sibling_discount_amount, sibling_order,
            bursary_id, bursary_amount,
            total_before_discounts, total_discounts, total_amount_due,
            total_paid, balance_due,
            status, due_date, created_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student2_id, '2025-2026',
            'monthly',
            9000.00, 0.00, 0.00, 0.00,  -- tuition only
            5.00, 450.00,  -- 5% monthly discount = $450
            10.00, 900.00, 2,  -- 10% sibling discount (2nd child) = $900
            v_bursary_merit_id, 3825.00,  -- 50% of remaining after discounts
            9000.00, 1350.00, 7650.00,  -- totals before bursary
            3000.00, 825.00,  -- partial payment made
            'partial', '2025-10-01', v_admin_id
        ) RETURNING id INTO v_student_fee2_id;
    END IF;

    -- Student 3: Weekly payment with 3rd child sibling discount + need-based bursary
    IF v_student3_id IS NOT NULL THEN
        INSERT INTO student_fees (
            id, school_id, student_id, academic_year,
            payment_frequency,
            base_tuition_amount, activity_fees_amount, material_fees_amount, other_fees_amount,
            payment_discount_percent, payment_discount_amount,
            sibling_discount_percent, sibling_discount_amount, sibling_order,
            bursary_id, bursary_amount,
            total_before_discounts, total_discounts, total_amount_due,
            total_paid, balance_due,
            status, due_date, created_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student3_id, '2025-2026',
            'weekly',
            10000.00, 300.00, 100.00, 0.00,  -- tuition + activity + materials
            0.00, 0.00,  -- no payment frequency discount for weekly
            15.00, 1500.00, 3,  -- 15% sibling discount (3rd child) = $1500
            v_bursary_need_id, 2000.00,  -- $2000 fixed bursary
            10400.00, 1500.00, 8900.00,  -- totals before bursary
            6900.00, 0.00,  -- fully paid!
            'paid', '2025-09-01', v_admin_id
        ) RETURNING id INTO v_student_fee3_id;
    END IF;

    -- =========================================================================
    -- PAYMENTS (5 payment transactions)
    -- =========================================================================

    -- Payment 1: Partial payment for Student 2 - first installment
    IF v_student_fee2_id IS NOT NULL THEN
        INSERT INTO payments (
            id, school_id, student_fee_id, student_id,
            amount, payment_date, payment_method,
            transaction_reference, receipt_number,
            allocation_notes, status, processed_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student_fee2_id, v_student2_id,
            2000.00, '2025-09-05', 'bank_transfer',
            'TXN-20250905-12345', 'RCPT-2025-0001',
            'First monthly installment - September payment',
            'completed', v_admin_id
        ) RETURNING id INTO v_payment1_id;
    END IF;

    -- Payment 2: Second partial payment for Student 2
    IF v_student_fee2_id IS NOT NULL THEN
        INSERT INTO payments (
            id, school_id, student_fee_id, student_id,
            amount, payment_date, payment_method,
            transaction_reference, receipt_number,
            allocation_notes, status, processed_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student_fee2_id, v_student2_id,
            1000.00, '2025-10-05', 'card',
            'CARD-20251005-98765', 'RCPT-2025-0002',
            'October monthly installment',
            'completed', v_admin_id
        ) RETURNING id INTO v_payment2_id;
    END IF;

    -- Payment 3: Full payment for Student 3 - paid in full
    IF v_student_fee3_id IS NOT NULL THEN
        INSERT INTO payments (
            id, school_id, student_fee_id, student_id,
            amount, payment_date, payment_method,
            transaction_reference, receipt_number,
            allocation_notes, status, processed_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student_fee3_id, v_student3_id,
            6900.00, '2025-08-20', 'cash',
            NULL, 'RCPT-2025-0003',
            'Full year payment - cash (after bursary and discounts)',
            'completed', v_admin_id
        );
    END IF;

    -- Payment 4: Pending payment (authorization hold)
    IF v_student_fee1_id IS NOT NULL THEN
        INSERT INTO payments (
            id, school_id, student_fee_id, student_id,
            amount, payment_date, payment_method,
            transaction_reference, receipt_number,
            allocation_notes, status, processed_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student_fee1_id, v_student1_id,
            7500.00, CURRENT_DATE, 'online',
            'PENDING-AUTH-12345', 'RCPT-2025-0004',
            'Online payment pending authorization',
            'pending', v_admin_id
        );
    END IF;

    -- Payment 5: Refunded payment (example of refund scenario)
    IF v_student_fee2_id IS NOT NULL THEN
        INSERT INTO payments (
            id, school_id, student_fee_id, student_id,
            amount, payment_date, payment_method,
            transaction_reference, receipt_number,
            allocation_notes, status, refund_reason, refunded_at, processed_by
        ) VALUES (
            gen_random_uuid(), v_school_id, v_student_fee2_id, v_student2_id,
            500.00, '2025-09-10', 'check',
            'CHECK-5678', 'RCPT-2025-0005',
            'Overpayment - returned to parent',
            'refunded', 'Check was written for wrong amount', '2025-09-12 10:30:00', v_admin_id
        );
    END IF;

    -- Update bursary recipient counts
    UPDATE bursaries SET current_recipients = 1 WHERE id = v_bursary_merit_id;
    UPDATE bursaries SET current_recipients = 1 WHERE id = v_bursary_need_id;

    RAISE NOTICE 'Sample data created successfully!';
    RAISE NOTICE 'Fee Structures: 3 (Grades 1, 3, 5)';
    RAISE NOTICE 'Bursaries: 2 (Merit and Need-based)';
    RAISE NOTICE 'Student Fees: 3 (Various payment scenarios)';
    RAISE NOTICE 'Payments: 5 (Including completed, pending, and refunded)';
    RAISE NOTICE 'Activity Fees: 2 (Linked to existing activities)';
END $$;
