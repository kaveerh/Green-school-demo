/**
 * School Context Composable
 * Provides easy access to the currently selected school
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

export function useSchool() {
  const authStore = useAuthStore()

  /**
   * Current school ID (UUID)
   * Returns null if no school is selected
   */
  const currentSchoolId = computed(() => authStore.currentSchoolId)

  /**
   * Current school object
   */
  const currentSchool = computed(() => authStore.selectedSchool)

  /**
   * Current school name
   */
  const currentSchoolName = computed(() => authStore.currentSchoolName)

  /**
   * Check if a school is selected
   */
  const hasSchool = computed(() => !!authStore.currentSchoolId)

  /**
   * Select a school
   */
  function selectSchool(school: any) {
    authStore.selectSchool(school)
  }

  /**
   * Clear selected school
   */
  function clearSchool() {
    authStore.clearSchool()
  }

  return {
    currentSchoolId,
    currentSchool,
    currentSchoolName,
    hasSchool,
    selectSchool,
    clearSchool
  }
}
