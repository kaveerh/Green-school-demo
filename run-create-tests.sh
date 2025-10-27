#!/bin/bash

# Run CREATE Form Tests for All Features

echo "🎯 CREATE Form Testing Suite"
echo "=================================================="
echo ""

# Check frontend
echo "📡 Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is not running. Start with: cd frontend && npm run dev"
    exit 1
fi

# Check backend
echo "📡 Checking if backend is running..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend is not running. Some tests may fail."
fi

echo ""
echo "🚀 Running CREATE form tests..."
echo ""

npx playwright test tests/ux-create-forms-v2.spec.ts \
    --reporter=list

echo ""
echo "📊 Test Results:"
echo ""
find test-results/screenshots -name "create-*.png" 2>/dev/null | wc -l | xargs echo "Screenshots captured:"
echo ""
echo "📁 View screenshots:"
echo "   open test-results/screenshots/"
echo ""
echo "✨ Done!"
