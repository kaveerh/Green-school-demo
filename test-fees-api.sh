#!/bin/bash

# Fees Management API Testing Script
# Comprehensive test suite for all 30+ fee endpoints

# Test Data IDs
SCHOOL_ID="60da2256-81fc-4ca5-bf6b-467b8d371c61"
ADMIN_ID="ea2ad94a-b077-48c2-ae25-6e3e8dc54499"
STUDENT_ID="c7d715a4-cca0-4133-9a6d-172d585a10e6"
FEE_STRUCTURE_ID="83080fc3-d597-40ac-89e0-38c4177b1288"
BURSARY_ID="f3c0b6e8-a688-4d61-bb80-2b1e3ecc1f27"

BASE_URL="http://localhost:8000/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="${5:-200}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${YELLOW}Test $TOTAL_TESTS: $name${NC}"

    if [ "$method" = "GET" ] || [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_status" ] || [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(json.dumps(d, indent=2)[:200] + '...')" 2>/dev/null || echo "$body" | head -c 200
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "$body" | head -c 300
    fi
}

echo "======================================"
echo "  FEES MANAGEMENT API TEST SUITE"
echo "======================================"
echo "Testing against: $BASE_URL"
echo ""

# ============================================================================
# FEE STRUCTURES ENDPOINTS
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  FEE STRUCTURES API (7 endpoints)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint \
    "GET all fee structures" \
    "GET" \
    "/fee-structures?school_id=$SCHOOL_ID"

test_endpoint \
    "GET fee structure by ID" \
    "GET" \
    "/fee-structures/$FEE_STRUCTURE_ID"

test_endpoint \
    "GET fee structure by grade and year" \
    "GET" \
    "/fee-structures/grade/1/year/2025-2026?school_id=$SCHOOL_ID"

test_endpoint \
    "CREATE fee structure (Grade 2)" \
    "POST" \
    "/fee-structures" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "grade_level": 2,
        "academic_year": "2025-2026",
        "yearly_amount": 8500.00,
        "monthly_amount": 800.00,
        "weekly_amount": 215.00,
        "yearly_discount": 10.00,
        "monthly_discount": 5.00,
        "weekly_discount": 0.00
    }' \
    201

# Save the created ID for update/delete tests
CREATED_FEE_ID=$(curl -s -X POST "$BASE_URL/fee-structures" \
    -H "Content-Type: application/json" \
    -d '{
        "school_id": "'$SCHOOL_ID'",
        "grade_level": 4,
        "academic_year": "2025-2026",
        "yearly_amount": 9200.00,
        "monthly_amount": 870.00,
        "weekly_amount": 230.00
    }' | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

test_endpoint \
    "UPDATE fee structure" \
    "PUT" \
    "/fee-structures/$FEE_STRUCTURE_ID" \
    '{
        "yearly_amount": 8100.00,
        "monthly_amount": 760.00,
        "weekly_amount": 205.00
    }'

test_endpoint \
    "DELETE fee structure (soft delete)" \
    "DELETE" \
    "/fee-structures/$CREATED_FEE_ID" \
    "" \
    204

# ============================================================================
# BURSARIES ENDPOINTS
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  BURSARIES API (7 endpoints)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint \
    "GET all bursaries" \
    "GET" \
    "/bursaries?school_id=$SCHOOL_ID"

test_endpoint \
    "GET bursary by ID" \
    "GET" \
    "/bursaries/$BURSARY_ID"

test_endpoint \
    "GET active bursaries" \
    "GET" \
    "/bursaries/active?school_id=$SCHOOL_ID"

test_endpoint \
    "GET bursaries by student" \
    "GET" \
    "/bursaries/student/$STUDENT_ID?school_id=$SCHOOL_ID"

test_endpoint \
    "CREATE bursary" \
    "POST" \
    "/bursaries" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "name": "STEM Excellence Award",
        "description": "For outstanding science and math students",
        "bursary_type": "academic",
        "coverage_type": "percentage",
        "coverage_value": 50.00,
        "academic_year": "2025-2026",
        "eligible_grades": [5, 6, 7],
        "max_recipients": 10
    }' \
    201

test_endpoint \
    "UPDATE bursary" \
    "PUT" \
    "/bursaries/$BURSARY_ID" \
    '{
        "name": "Merit Scholarship - Updated",
        "coverage_value": 60.00
    }'

test_endpoint \
    "UPDATE bursary status" \
    "PATCH" \
    "/bursaries/$BURSARY_ID/status" \
    '{
        "is_active": true
    }'

# ============================================================================
# STUDENT FEES ENDPOINTS
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  STUDENT FEES API (7 endpoints)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint \
    "GET all student fees" \
    "GET" \
    "/student-fees?school_id=$SCHOOL_ID"

test_endpoint \
    "GET student fees by student ID" \
    "GET" \
    "/student-fees/student/$STUDENT_ID?school_id=$SCHOOL_ID"

test_endpoint \
    "GET overdue student fees" \
    "GET" \
    "/student-fees/overdue?school_id=$SCHOOL_ID"

test_endpoint \
    "CREATE student fee" \
    "POST" \
    "/student-fees" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "student_id": "'$STUDENT_ID'",
        "academic_year": "2025-2026",
        "payment_frequency": "monthly",
        "base_amount": 800.00,
        "total_amount": 800.00,
        "amount_paid": 0.00,
        "balance": 800.00,
        "due_date": "2025-12-15",
        "status": "pending"
    }' \
    201

# Get a student fee ID for update/delete
STUDENT_FEE_ID=$(curl -s "$BASE_URL/student-fees?school_id=$SCHOOL_ID&limit=1" | \
    python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else '')" 2>/dev/null)

test_endpoint \
    "UPDATE student fee" \
    "PUT" \
    "/student-fees/$STUDENT_FEE_ID" \
    '{
        "amount_paid": 200.00,
        "balance": 600.00
    }'

test_endpoint \
    "BULK generate student fees" \
    "POST" \
    "/student-fees/bulk-generate" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "grade_level": 1,
        "academic_year": "2025-2026"
    }' \
    201

# ============================================================================
# PAYMENTS ENDPOINTS
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  PAYMENTS API (8 endpoints)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint \
    "GET all payments" \
    "GET" \
    "/payments?school_id=$SCHOOL_ID"

test_endpoint \
    "GET payments by student" \
    "GET" \
    "/payments/student/$STUDENT_ID?school_id=$SCHOOL_ID"

test_endpoint \
    "GET pending payments" \
    "GET" \
    "/payments/pending?school_id=$SCHOOL_ID"

test_endpoint \
    "CREATE payment" \
    "POST" \
    "/payments" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "student_id": "'$STUDENT_ID'",
        "student_fee_id": "'$STUDENT_FEE_ID'",
        "amount": 200.00,
        "payment_date": "2025-11-16",
        "payment_method": "cash",
        "status": "completed",
        "reference_number": "PAY-TEST-001"
    }' \
    201

# Get payment ID for reconcile/refund tests
PAYMENT_ID=$(curl -s "$BASE_URL/payments?school_id=$SCHOOL_ID&limit=1" | \
    python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else '')" 2>/dev/null)

test_endpoint \
    "GET payment by ID" \
    "GET" \
    "/payments/$PAYMENT_ID"

test_endpoint \
    "RECONCILE payment" \
    "POST" \
    "/payments/$PAYMENT_ID/reconcile" \
    '{
        "reconciled": true,
        "reconciliation_notes": "Verified with bank statement"
    }'

test_endpoint \
    "UPDATE payment" \
    "PUT" \
    "/payments/$PAYMENT_ID" \
    '{
        "notes": "Payment verified and processed"
    }'

# ============================================================================
# ACTIVITY FEES ENDPOINTS
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  ACTIVITY FEES API (6 endpoints)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Get an activity ID
ACTIVITY_ID=$(docker-compose exec -T database psql -U postgres -d greenschool -t -c "SELECT id FROM activities LIMIT 1;" | tr -d ' ')

test_endpoint \
    "GET all activity fees" \
    "GET" \
    "/activity-fees?school_id=$SCHOOL_ID"

test_endpoint \
    "GET activity fees by activity" \
    "GET" \
    "/activity-fees/activity/$ACTIVITY_ID?school_id=$SCHOOL_ID"

test_endpoint \
    "GET activity fees by student" \
    "GET" \
    "/activity-fees/student/$STUDENT_ID?school_id=$SCHOOL_ID"

test_endpoint \
    "CREATE activity fee" \
    "POST" \
    "/activity-fees" \
    '{
        "school_id": "'$SCHOOL_ID'",
        "activity_id": "'$ACTIVITY_ID'",
        "academic_year": "2025-2026",
        "fee_name": "Soccer Team Registration",
        "amount": 150.00,
        "is_mandatory": false,
        "payment_deadline": "2025-12-01"
    }' \
    201

ACTIVITY_FEE_ID=$(curl -s "$BASE_URL/activity-fees?school_id=$SCHOOL_ID&limit=1" | \
    python3 -c "import sys, json; d=json.load(sys.stdin); print(d['data'][0]['id'] if d.get('data') else '')" 2>/dev/null)

test_endpoint \
    "GET activity fee by ID" \
    "GET" \
    "/activity-fees/$ACTIVITY_FEE_ID"

test_endpoint \
    "UPDATE activity fee" \
    "PUT" \
    "/activity-fees/$ACTIVITY_FEE_ID" \
    '{
        "amount": 175.00,
        "is_mandatory": true
    }'

# ============================================================================
# TEST SUMMARY
# ============================================================================
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  TEST SUMMARY${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nTotal Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
