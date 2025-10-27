-- Sample Data: Merits
-- 5 sample merit records for testing

-- Get references
DO $$
DECLARE
    v_school_id UUID := '60da2256-81fc-4ca5-bf6b-467b8d371c61';
    v_teacher_id UUID := 'a7a76304-04d0-4d74-a0ea-50584666b990';
    v_student_id UUID := 'c7d715a4-cca0-4133-9a6d-172d585a10e6';
    v_class_id UUID := '2e008ff4-dc05-4c6b-8059-ca92fceb3f9a';
    v_subject_id UUID := '94473bd5-c1de-4e8c-9ef3-bde10cacc143';
BEGIN

    -- Merit 1: Academic Excellence - Math Test
    INSERT INTO merits (
        school_id, student_id, awarded_by_id, class_id, subject_id,
        category, points, reason, quarter, academic_year, awarded_date,
        is_class_award, created_at
    ) VALUES (
        v_school_id, v_student_id, v_teacher_id, v_class_id, v_subject_id,
        'academic', 10, 'Scored 100% on the fractions unit test. Showed exceptional understanding of complex fraction operations.',
        'Q2', '2024-2025', '2025-10-20',
        FALSE, CURRENT_TIMESTAMP
    );

    -- Merit 2: Helping Classmate - Good Behavior
    INSERT INTO merits (
        school_id, student_id, awarded_by_id, class_id, subject_id,
        category, points, reason, quarter, academic_year, awarded_date,
        is_class_award, created_at
    ) VALUES (
        v_school_id, v_student_id, v_teacher_id, v_class_id, NULL,
        'behavior', 5, 'Spent extra time helping a struggling classmate understand multiplication. Demonstrated patience and kindness.',
        'Q2', '2024-2025', '2025-10-21',
        FALSE, CURRENT_TIMESTAMP
    );

    -- Merit 3: Perfect Attendance - Weekly Award
    INSERT INTO merits (
        school_id, student_id, awarded_by_id, class_id, subject_id,
        category, points, reason, quarter, academic_year, awarded_date,
        is_class_award, created_at
    ) VALUES (
        v_school_id, v_student_id, v_teacher_id, v_class_id, NULL,
        'attendance', 3, 'Perfect attendance for the entire week. Always on time and ready to learn.',
        'Q2', '2024-2025', '2025-10-25',
        FALSE, CURRENT_TIMESTAMP
    );

    -- Merit 4: Class Participation - Active Engagement
    INSERT INTO merits (
        school_id, student_id, awarded_by_id, class_id, subject_id,
        category, points, reason, quarter, academic_year, awarded_date,
        is_class_award, created_at
    ) VALUES (
        v_school_id, v_student_id, v_teacher_id, v_class_id, v_subject_id,
        'participation', 4, 'Consistently raises hand to answer questions and contributes thoughtful ideas during class discussions.',
        'Q2', '2024-2025', '2025-10-23',
        FALSE, CURRENT_TIMESTAMP
    );

    -- Merit 5: Leadership - Group Project Leader
    INSERT INTO merits (
        school_id, student_id, awarded_by_id, class_id, subject_id,
        category, points, reason, quarter, academic_year, awarded_date,
        is_class_award, created_at
    ) VALUES (
        v_school_id, v_student_id, v_teacher_id, v_class_id, v_subject_id,
        'leadership', 7, 'Led group science project with excellence. Ensured all team members contributed and understood the material.',
        'Q2', '2024-2025', '2025-10-22',
        FALSE, CURRENT_TIMESTAMP
    );

END $$;
