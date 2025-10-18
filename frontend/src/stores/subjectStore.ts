/**
 * Subject Store
 *
 * Pinia store for managing subject state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { subjectService } from '@/services/subjectService'
import type {
  Subject,
  SubjectCreateInput,
  SubjectUpdateInput,
  SubjectSearchParams,
  SubjectStatistics
} from '@/types/subject'

export const useSubjectStore = defineStore('subject', () => {
  // State
  const subjects = ref<Subject[]>([])
  const selectedSubject = ref<Subject | null>(null)
  const statistics = ref<SubjectStatistics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalSubjects = ref(0)
  const pageSize = ref(50)

  // Computed
  const totalPages = computed(() => Math.ceil(totalSubjects.value / pageSize.value))

  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  const hasPreviousPage = computed(() => currentPage.value > 1)

  // Actions

  /**
   * Fetch all subjects
   */
  async function fetchSubjects(params: SubjectSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await subjectService.getSubjects({
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      subjects.value = response.subjects
      totalSubjects.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch subjects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch subject by ID
   */
  async function fetchSubjectById(id: string) {
    isLoading.value = true
    error.value = null

    try {
      const subject = await subjectService.getSubjectById(id)
      selectedSubject.value = subject
      return subject
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch subject'
      selectedSubject.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch subject by code
   */
  async function fetchSubjectByCode(code: string, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const subject = await subjectService.getSubjectByCode(code, schoolId)
      selectedSubject.value = subject
      return subject
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch subject'
      selectedSubject.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create new subject
   */
  async function createSubject(subjectData: SubjectCreateInput) {
    isLoading.value = true
    error.value = null

    try {
      const newSubject = await subjectService.createSubject(subjectData)

      // Add to list
      subjects.value.unshift(newSubject)
      totalSubjects.value++

      return newSubject
    } catch (err: any) {
      error.value = err.message || 'Failed to create subject'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update subject
   */
  async function updateSubject(id: string, subjectData: SubjectUpdateInput) {
    isLoading.value = true
    error.value = null

    try {
      const updatedSubject = await subjectService.updateSubject(id, subjectData)

      // Update in list
      const index = subjects.value.findIndex((s) => s.id === id)
      if (index !== -1) {
        subjects.value[index] = updatedSubject
      }

      // Update selected if it's the same
      if (selectedSubject.value?.id === id) {
        selectedSubject.value = updatedSubject
      }

      return updatedSubject
    } catch (err: any) {
      error.value = err.message || 'Failed to update subject'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete subject
   */
  async function deleteSubject(id: string) {
    isLoading.value = true
    error.value = null

    try {
      await subjectService.deleteSubject(id)

      // Remove from list
      subjects.value = subjects.value.filter((s) => s.id !== id)
      totalSubjects.value--

      // Clear selected if it's the same
      if (selectedSubject.value?.id === id) {
        selectedSubject.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete subject'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle subject status
   */
  async function toggleStatus(id: string) {
    isLoading.value = true
    error.value = null

    try {
      const updatedSubject = await subjectService.toggleStatus(id)

      // Update in list
      const index = subjects.value.findIndex((s) => s.id === id)
      if (index !== -1) {
        subjects.value[index] = updatedSubject
      }

      // Update selected if it's the same
      if (selectedSubject.value?.id === id) {
        selectedSubject.value = updatedSubject
      }

      return updatedSubject
    } catch (err: any) {
      error.value = err.message || 'Failed to toggle status'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Search subjects
   */
  async function searchSubjects(query: string, params: SubjectSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await subjectService.searchSubjects(query, {
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      subjects.value = response.subjects
      totalSubjects.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to search subjects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch subjects by category
   */
  async function fetchSubjectsByCategory(category: string, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const categorySubjects = await subjectService.getSubjectsByCategory(category, schoolId)
      return categorySubjects
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch subjects by category'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch subjects by grade
   */
  async function fetchSubjectsByGrade(grade: number, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const gradeSubjects = await subjectService.getSubjectsByGrade(grade, schoolId)
      return gradeSubjects
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch subjects by grade'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch statistics
   */
  async function fetchStatistics(schoolId?: string) {
    isLoading.value = true
    error.value = null

    try {
      const stats = await subjectService.getStatistics(schoolId)
      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Go to next page
   */
  async function nextPage() {
    if (hasNextPage.value) {
      currentPage.value++
      await fetchSubjects()
    }
  }

  /**
   * Go to previous page
   */
  async function previousPage() {
    if (hasPreviousPage.value) {
      currentPage.value--
      await fetchSubjects()
    }
  }

  /**
   * Go to specific page
   */
  async function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      await fetchSubjects()
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Clear selected subject
   */
  function clearSelected() {
    selectedSubject.value = null
  }

  /**
   * Reset store
   */
  function $reset() {
    subjects.value = []
    selectedSubject.value = null
    statistics.value = null
    isLoading.value = false
    error.value = null
    currentPage.value = 1
    totalSubjects.value = 0
    pageSize.value = 50
  }

  return {
    // State
    subjects,
    selectedSubject,
    statistics,
    isLoading,
    error,
    currentPage,
    totalSubjects,
    pageSize,

    // Computed
    totalPages,
    hasNextPage,
    hasPreviousPage,

    // Actions
    fetchSubjects,
    fetchSubjectById,
    fetchSubjectByCode,
    createSubject,
    updateSubject,
    deleteSubject,
    toggleStatus,
    searchSubjects,
    fetchSubjectsByCategory,
    fetchSubjectsByGrade,
    fetchStatistics,
    nextPage,
    previousPage,
    goToPage,
    clearError,
    clearSelected,
    $reset,
  }
})
