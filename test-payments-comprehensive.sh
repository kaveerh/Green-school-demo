#!/bin/bash

# Comprehensive Payments API Test Script
# Tests all 12 payment endpoints

SCHOOL_ID="60da2256-81fc-4ca5-bf6b-467b8d371c61"
STUDENT_ID="fe2fc083-98f6-4881-a9a4-775072ce79dd"
STUDENT_FEE_ID="aad480be-1dac-4731-a677-48fff6d47999"
BASE_URL="http://localhost:8000/api/v1"

PASS_COUNT=0
FAIL_COUNT=0

test_endpoint() {
    local test_name="$1"
    local method="$2"
    local url="$3"
    local data="$4"
    local expected_status="$5"

    echo ""
    echo "=== Testing: $test_name ==="

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$url" -H "Content-Type: application/json" -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        echo "✅ PASS (HTTP $status_code)"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL (Expected $expected_status, got $status_code)"
        echo "Response: $(echo "$body" | head -c 200)"
        ((FAIL_COUNT++))
    fi
}

echo "======================================"
echo "Payments API Comprehensive Test Suite"
echo "======================================"

# 1. List Payments
test_endpoint \
    "GET /payments (List all)" \
    "GET" \
    "$BASE_URL/payments?school_id=$SCHOOL_ID&page=1&limit=5" \
    "" \
    "200"

# 2. Get Student Payments
test_endpoint \
    "GET /payments/student/{id}" \
    "GET" \
    "$BASE_URL/payments/student/$STUDENT_ID?page=1&limit=5" \
    "" \
    "200"

# 3. Get Payment by ID
PAYMENT_ID="1af09b68-25fb-43ae-a0e6-07f3277e3d13"
test_endpoint \
    "GET /payments/{id}" \
    "GET" \
    "$BASE_URL/payments/$PAYMENT_ID" \
    "" \
    "200"

# 4. Get Payment by Receipt Number
test_endpoint \
    "GET /payments/receipt/{receipt_number}" \
    "GET" \
    "$BASE_URL/payments/receipt/RCPT-2025-0001" \
    "" \
    "200"

# 5. Get Receipt Data
test_endpoint \
    "GET /payments/{id}/receipt-data" \
    "GET" \
    "$BASE_URL/payments/$PAYMENT_ID/receipt-data" \
    "" \
    "200"

# 6. Revenue Report
test_endpoint \
    "GET /payments/reports/revenue" \
    "GET" \
    "$BASE_URL/payments/reports/revenue?school_id=$SCHOOL_ID&group_by=month" \
    "" \
    "200"

# 7. Create Payment
test_endpoint \
    "POST /payments (Create)" \
    "POST" \
    "$BASE_URL/payments" \
    "{\"school_id\":\"$SCHOOL_ID\",\"student_fee_id\":\"$STUDENT_FEE_ID\",\"amount\":75.00,\"payment_method\":\"cash\",\"payment_date\":\"2025-11-16\",\"auto_generate_receipt\":true}" \
    "201"

# Save new payment ID for later tests
PAYMENT_ID=$(curl -s -X POST "$BASE_URL/payments" -H "Content-Type: application/json" -d "{\"school_id\":\"$SCHOOL_ID\",\"student_fee_id\":\"$STUDENT_FEE_ID\",\"amount\":25.00,\"payment_method\":\"cash\",\"payment_date\":\"2025-11-16\",\"auto_generate_receipt\":true}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

# 8. Update Payment
test_endpoint \
    "PUT /payments/{id} (Update)" \
    "PUT" \
    "$BASE_URL/payments/$PAYMENT_ID" \
    "{\"notes\":\"Updated payment via test script\"}" \
    "200"

# 9. Create Pending Payment
test_endpoint \
    "POST /payments/pending" \
    "POST" \
    "$BASE_URL/payments/pending" \
    "{\"school_id\":\"$SCHOOL_ID\",\"student_fee_id\":\"$STUDENT_FEE_ID\",\"amount\":30.00,\"payment_method\":\"check\",\"transaction_reference\":\"CHECK-TEST\"}" \
    "201"

# Save pending payment ID
PENDING_ID=$(curl -s -X POST "$BASE_URL/payments/pending" -H "Content-Type: application/json" -d "{\"school_id\":\"$SCHOOL_ID\",\"student_fee_id\":\"$STUDENT_FEE_ID\",\"amount\":20.00,\"payment_method\":\"check\",\"transaction_reference\":\"CHECK-CONFIRM-TEST\"}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

# 10. Confirm Pending Payment
test_endpoint \
    "POST /payments/{id}/confirm" \
    "POST" \
    "$BASE_URL/payments/$PENDING_ID/confirm" \
    "{\"transaction_reference\":\"CHECK-CONFIRMED\"}" \
    "200"

# 11. Create another payment for refund test
REFUND_ID=$(curl -s -X POST "$BASE_URL/payments" -H "Content-Type: application/json" -d "{\"school_id\":\"$SCHOOL_ID\",\"student_fee_id\":\"$STUDENT_FEE_ID\",\"amount\":10.00,\"payment_method\":\"cash\",\"payment_date\":\"2025-11-16\",\"auto_generate_receipt\":true}" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

# 12. Refund Payment
test_endpoint \
    "POST /payments/{id}/refund" \
    "POST" \
    "$BASE_URL/payments/$REFUND_ID/refund" \
    "{\"refund_reason\":\"Test refund\"}" \
    "200"

# Summary
echo ""
echo "======================================"
echo "Test Results Summary"
echo "======================================"
echo "✅ Passed: $PASS_COUNT"
echo "❌ Failed: $FAIL_COUNT"
TOTAL=$((PASS_COUNT + FAIL_COUNT))
PERCENTAGE=$((PASS_COUNT * 100 / TOTAL))
echo "Success Rate: $PERCENTAGE% ($PASS_COUNT/$TOTAL)"
echo "======================================"
