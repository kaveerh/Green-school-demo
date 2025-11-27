#!/bin/bash

# Script to update hardcoded school IDs to use useSchool composable
# Run from project root: bash update-school-ids.sh

set -e

echo "🔄 Updating school IDs to use auth store..."
echo ""

# Function to update a file
update_file() {
    local file=$1
    local pattern=$2
    local replacement=$3

    if [ -f "$file" ]; then
        echo "📝 Updating $file..."

        # Check if useSchool import already exists
        if ! grep -q "import.*useSchool" "$file"; then
            # Find the last import line and add useSchool import after it
            sed -i.bak "/^import.*from.*@\/stores\//a\\
import { useSchool } from '@/composables/useSchool'
" "$file"
        fi

        # Replace the hardcoded school ID
        sed -i.bak "s/$pattern/$replacement/g" "$file"

        echo "   ✅ Done"
    else
        echo "   ⚠️  File not found: $file"
    fi
}

# Update views with Pattern 1: const currentSchoolId = ref('60da2256...')
echo "🎯 Updating views (Pattern 1: currentSchoolId)..."
for file in \
    "frontend/src/views/AssessmentForm.vue" \
    "frontend/src/views/AssessmentList.vue" \
    "frontend/src/views/LessonList.vue"
do
    if [ -f "$file" ]; then
        echo "📝 $file"

        # Add import if not exists
        if ! grep -q "import.*useSchool" "$file"; then
            # Find last store import and add after it
            awk '/import.*from.*@\/stores\// {print; print "import { useSchool } from '\''@/composables/useSchool'\''"; next}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        fi

        # Replace hardcoded school ID
        sed -i.bak "s/const currentSchoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61').*$/const { currentSchoolId } = useSchool()/" "$file"
        echo "   ✅ Done"
    fi
done

# Update views with Pattern 2: const schoolId = ref('60da2256...')
echo ""
echo "🎯 Updating views (Pattern 2: schoolId ref)..."
for file in \
    "frontend/src/views/AttendanceForm.vue" \
    "frontend/src/views/AttendanceList.vue"
do
    if [ -f "$file" ]; then
        echo "📝 $file"

        # Add import if not exists
        if ! grep -q "import.*useSchool" "$file"; then
            awk '/import.*from.*@\/stores\// {print; print "import { useSchool } from '\''@/composables/useSchool'\''"; next}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        fi

        # Replace hardcoded school ID and rename to currentSchoolId
        sed -i.bak "s/const schoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61').*$/const { currentSchoolId } = useSchool()/" "$file"

        # Update all usages from schoolId.value to currentSchoolId.value
        sed -i.bak "s/schoolId\.value/currentSchoolId.value/g" "$file"

        echo "   ✅ Done"
    fi
done

# Update views with Pattern 3: const schoolId = '60da2256...' (no ref)
echo ""
echo "🎯 Updating views (Pattern 3: schoolId without ref)..."
for file in \
    "frontend/src/views/ActivityForm.vue" \
    "frontend/src/views/EventForm.vue" \
    "frontend/src/views/EventList.vue"
do
    if [ -f "$file" ]; then
        echo "📝 $file"

        # Add import if not exists
        if ! grep -q "import.*useSchool" "$file"; then
            awk '/import.*from.*@\/stores\// {print; print "import { useSchool } from '\''@/composables/useSchool'\''"; next}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        fi

        # Replace hardcoded school ID
        sed -i.bak "s/const schoolId = '60da2256-81fc-4ca5-bf6b-467b8d371c61'.*$/const { currentSchoolId } = useSchool()/" "$file"

        # Update usages from schoolId to currentSchoolId.value
        sed -i.bak "s/\bschoolId\b/currentSchoolId.value/g" "$file"

        echo "   ✅ Done"
    fi
done

# Update components
echo ""
echo "🎯 Updating components..."
for file in \
    "frontend/src/components/ClassList.vue" \
    "frontend/src/components/RoomForm.vue" \
    "frontend/src/components/ClassForm.vue"
do
    if [ -f "$file" ]; then
        echo "📝 $file"

        # Add import if not exists
        if ! grep -q "import.*useSchool" "$file"; then
            awk '/import.*from.*@\/stores\// {print; print "import { useSchool } from '\''@/composables/useSchool'\''"; next}1' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        fi

        # Replace hardcoded school ID
        sed -i.bak "s/const schoolId = '60da2256-81fc-4ca5-bf6b-467b8d371c61'.*$/const { currentSchoolId } = useSchool()/" "$file"

        # Update usages
        sed -i.bak "s/\bschoolId\b/currentSchoolId.value/g" "$file"

        echo "   ✅ Done"
    fi
done

# Clean up backup files
echo ""
echo "🧹 Cleaning up backup files..."
find frontend/src -name "*.bak" -delete

echo ""
echo "✨ All files updated successfully!"
echo ""
echo "📋 Summary:"
echo "   - Added useSchool composable import to all files"
echo "   - Replaced hardcoded school IDs with currentSchoolId from auth store"
echo "   - Updated all usages to reference currentSchoolId.value"
echo ""
echo "🧪 Next steps:"
echo "   1. Review the changes"
echo "   2. Test school switching functionality"
echo "   3. Verify all forms and lists work correctly"
echo ""
