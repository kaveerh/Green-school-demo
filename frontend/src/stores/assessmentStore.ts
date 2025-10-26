/**
 * Assessment Store
 *
 * Pinia store for assessment state management
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Assessment,
  AssessmentCreateRequest,
  AssessmentUpdateRequest,
  AssessmentGradeRequest,
  AssessmentStatistics,
  StudentAssessmentParams,
  ClassAssessmentParams,
  TeacherAssessmentParams,
  AssessmentStatisticsParams
} from '@/types/assessment'
import { assessmentService } from '@/services/assessmentService'

export const useAssessmentStore = defineStore('assessment', () => {
  // State
  const assessments = ref<Assessment[]>([])
  const currentAssessment = ref<Assessment | null>(null)
  const studentAssessments = ref<Assessment[]>([])
  const classAssessments = ref<Assessment[]>([])
  const teacherAssessments = ref<Assessment[]>([])
  const statistics = ref<AssessmentStatistics | null>(null)

  const total = ref(0)
  const currentPage = ref(1)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasAssessments = computed(() => assessments.value.length > 0)
  const hasStudentAssessments = computed(() => studentAssessments.value.length > 0)
  const hasClassAssessments = computed(() => classAssessments.value.length > 0)
  const hasTeacherAssessments = computed(() => teacherAssessments.value.length > 0)

  const pendingAssessments = computed(() =>
    assessments.value.filter((a) => a.status === 'pending' || a.status === 'submitted')
  )

  const gradedAssessments = computed(() =>
    assessments.value.filter((a) => a.status === 'graded' || a.status === 'returned')
  )

  const overdueAssessments = computed(() => assessments.value.filter((a) => a.is_overdue))

  // Actions

  /**
   * Fetch assessments for a student
   */
  async function fetchStudentAssessments(params: StudentAssessmentParams) {
    loading.value = true
    error.value = null

    try {
      const response = await assessmentService.getStudentAssessments(params)
      studentAssessments.value = response.assessments
      total.value = response.total
      currentPage.value = response.page
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch student assessments'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch assessments for a class
   */
  async function fetchClassAssessments(params: ClassAssessmentParams) {
    loading.value = true
    error.value = null

    try {
      const response = await assessmentService.getClassAssessments(params)
      classAssessments.value = response.assessments
      total.value = response.total
      currentPage.value = response.page
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch class assessments'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch assessments for a teacher
   */
  async function fetchTeacherAssessments(params: TeacherAssessmentParams) {
    loading.value = true
    error.value = null

    try {
      const response = await assessmentService.getTeacherAssessments(params)
      teacherAssessments.value = response.assessments
      assessments.value = response.assessments
      total.value = response.total
      currentPage.value = response.page
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch teacher assessments'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch statistics
   */
  async function fetchStatistics(params: AssessmentStatisticsParams) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await assessmentService.getStatistics(params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch assessment by ID
   */
  async function fetchAssessmentById(id: string) {
    loading.value = true
    error.value = null

    try {
      currentAssessment.value = await assessmentService.getAssessmentById(id)
      return currentAssessment.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch assessment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new assessment
   */
  async function createAssessment(data: AssessmentCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const newAssessment = await assessmentService.createAssessment(data)
      assessments.value.unshift(newAssessment)
      total.value++
      return newAssessment
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create assessment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update an assessment
   */
  async function updateAssessment(id: string, data: AssessmentUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updatedAssessment = await assessmentService.updateAssessment(id, data)

      // Update in list
      const index = assessments.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        assessments.value[index] = updatedAssessment
      }

      // Update current if it's the same
      if (currentAssessment.value?.id === id) {
        currentAssessment.value = updatedAssessment
      }

      return updatedAssessment
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update assessment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Grade an assessment
   */
  async function gradeAssessment(id: string, data: AssessmentGradeRequest) {
    loading.value = true
    error.value = null

    try {
      const gradedAssessment = await assessmentService.gradeAssessment(id, data)

      // Update in list
      const index = assessments.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        assessments.value[index] = gradedAssessment
      }

      // Update in teacher assessments
      const teacherIndex = teacherAssessments.value.findIndex((a) => a.id === id)
      if (teacherIndex !== -1) {
        teacherAssessments.value[teacherIndex] = gradedAssessment
      }

      // Update in class assessments
      const classIndex = classAssessments.value.findIndex((a) => a.id === id)
      if (classIndex !== -1) {
        classAssessments.value[classIndex] = gradedAssessment
      }

      // Update in student assessments
      const studentIndex = studentAssessments.value.findIndex((a) => a.id === id)
      if (studentIndex !== -1) {
        studentAssessments.value[studentIndex] = gradedAssessment
      }

      // Update current if it's the same
      if (currentAssessment.value?.id === id) {
        currentAssessment.value = gradedAssessment
      }

      return gradedAssessment
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to grade assessment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete an assessment
   */
  async function deleteAssessment(id: string) {
    loading.value = true
    error.value = null

    try {
      await assessmentService.deleteAssessment(id)

      // Remove from all lists
      assessments.value = assessments.value.filter((a) => a.id !== id)
      teacherAssessments.value = teacherAssessments.value.filter((a) => a.id !== id)
      classAssessments.value = classAssessments.value.filter((a) => a.id !== id)
      studentAssessments.value = studentAssessments.value.filter((a) => a.id !== id)
      total.value--

      // Clear current if it's the same
      if (currentAssessment.value?.id === id) {
        currentAssessment.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete assessment'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrent() {
    currentAssessment.value = null
  }

  function reset() {
    assessments.value = []
    currentAssessment.value = null
    studentAssessments.value = []
    classAssessments.value = []
    teacherAssessments.value = []
    statistics.value = null
    total.value = 0
    currentPage.value = 1
    loading.value = false
    error.value = null
  }

  return {
    // State
    assessments,
    currentAssessment,
    studentAssessments,
    classAssessments,
    teacherAssessments,
    statistics,
    total,
    currentPage,
    loading,
    error,

    // Computed
    hasAssessments,
    hasStudentAssessments,
    hasClassAssessments,
    hasTeacherAssessments,
    pendingAssessments,
    gradedAssessments,
    overdueAssessments,

    // Actions
    fetchStudentAssessments,
    fetchClassAssessments,
    fetchTeacherAssessments,
    fetchStatistics,
    fetchAssessmentById,
    createAssessment,
    updateAssessment,
    gradeAssessment,
    deleteAssessment,
    clearError,
    clearCurrent,
    reset
  }
})
