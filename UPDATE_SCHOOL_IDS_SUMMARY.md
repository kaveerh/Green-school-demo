# School ID Update Summary

## Completed
- ✅ frontend/src/views/LessonForm.vue - Updated to use useSchool() composable

## Remaining Views to Update

### Pattern 1: `const currentSchoolId = ref('60da2256...')`
- frontend/src/views/AssessmentForm.vue (line ~216)
- frontend/src/views/AssessmentList.vue (line ~178)
- frontend/src/views/LessonList.vue (line ~131)

### Pattern 2: `const schoolId = ref('60da2256...')`
- frontend/src/views/AttendanceForm.vue (line ~277)
- frontend/src/views/AttendanceList.vue (line ~248)

### Pattern 3: `const schoolId = '60da2256...'` (no ref)
- frontend/src/views/ActivityForm.vue (line ~507)
- frontend/src/views/EventForm.vue (line ~350)
- frontend/src/views/EventList.vue (lines ~243, 264, 303)

## Remaining Components to Update

### Pattern: `const schoolId = '60da2256...'`
- frontend/src/components/ClassList.vue (line ~522)
- frontend/src/components/RoomForm.vue (line ~328)
- frontend/src/components/SubjectForm.vue
- frontend/src/components/SubjectList.vue
- frontend/src/components/ClassForm.vue
- frontend/src/components/RoomList.vue

### Pattern: Hardcoded in store
- frontend/src/stores/dashboardStore.ts

## Update Strategy

For each file:
1. Add `import { useSchool } from '@/composables/useSchool'`
2. Replace hardcoded school ID with `const { currentSchoolId } = useSchool()`
3. Update any usage from `.value` syntax (if necessary - refs stay the same)

Note: For Pattern 3 files (non-ref), need to change usage from `schoolId` to `currentSchoolId.value`
