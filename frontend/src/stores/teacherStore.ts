/**
 * Teacher Store
 * Pinia store for teacher state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Teacher,
  TeacherCreateInput,
  TeacherUpdateInput,
  TeacherSearchParams,
  PaginatedResponse,
  TeacherStatistics,
  TeacherStatus,
  EmploymentType
} from '@/types'

export const useTeacherStore = defineStore('teacher', () => {
  // State
  const teachers = ref<Teacher[]>([])
  const selectedTeacher = ref<Teacher | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const statistics = ref<TeacherStatistics | null>(null)

  // Getters
  const totalTeachers = computed(() => pagination.value.total)
  const hasTeachers = computed(() => teachers.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const teachersByStatus = computed(() => {
    return (status: TeacherStatus) => teachers.value.filter(t => t.status === status)
  })

  const activeTeachers = computed(() =>
    teachers.value.filter(t => t.status === 'active' && t.is_currently_employed)
  )

  const inactiveTeachers = computed(() =>
    teachers.value.filter(t => t.status !== 'active' || !t.is_currently_employed)
  )

  const teachersByEmploymentType = computed(() => {
    return (type: EmploymentType) => teachers.value.filter(t => t.employment_type === type)
  })

  const fullTimeTeachers = computed(() =>
    teachers.value.filter(t => t.employment_type === 'full-time')
  )

  const partTimeTeachers = computed(() =>
    teachers.value.filter(t => t.employment_type === 'part-time')
  )

  const teachersByGrade = computed(() => {
    return (grade: number) => teachers.value.filter(t => t.grade_levels?.includes(grade))
  })

  const teachersWithExpiringCertifications = computed(() =>
    teachers.value.filter(t => !t.is_certification_valid)
  )

  // Actions
  async function fetchTeachers(params?: TeacherSearchParams) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const response = await teacherService.getTeachers(params)

      teachers.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teachers'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTeacherById(id: string) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacher = await teacherService.getTeacherById(id)

      selectedTeacher.value = teacher
      return teacher
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teacher'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTeacherByUserId(userId: string) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacher = await teacherService.getTeacherByUserId(userId)

      selectedTeacher.value = teacher
      return teacher
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teacher by user ID'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTeacherByEmployeeId(employeeId: string) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacher = await teacherService.getTeacherByEmployeeId(employeeId)

      selectedTeacher.value = teacher
      return teacher
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teacher by employee ID'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchActiveTeachers(page: number = 1, limit: number = 20) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const response = await teacherService.getActiveTeachers(page, limit)

      teachers.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch active teachers'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTeachersByGrade(grade: number) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacherList = await teacherService.getTeachersByGrade(grade)

      return teacherList
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teachers by grade'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTeachersBySpecialization(specialization: string) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacherList = await teacherService.getTeachersBySpecialization(specialization)

      return teacherList
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch teachers by specialization'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createTeacher(teacherData: TeacherCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const teacher = await teacherService.createTeacher(teacherData)

      // Add to local state
      teachers.value.unshift(teacher)
      pagination.value.total++

      return teacher
    } catch (err: any) {
      error.value = err.message || 'Failed to create teacher'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateTeacher(id: string, teacherData: TeacherUpdateInput) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const updatedTeacher = await teacherService.updateTeacher(id, teacherData)

      // Update in local state
      const index = teachers.value.findIndex(t => t.id === id)
      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (selectedTeacher.value?.id === id) {
        selectedTeacher.value = updatedTeacher
      }

      return updatedTeacher
    } catch (err: any) {
      error.value = err.message || 'Failed to update teacher'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteTeacher(id: string) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      await teacherService.deleteTeacher(id)

      // Remove from local state
      teachers.value = teachers.value.filter(t => t.id !== id)
      pagination.value.total--

      if (selectedTeacher.value?.id === id) {
        selectedTeacher.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete teacher'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changeTeacherStatus(id: string, status: TeacherStatus) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const updatedTeacher = await teacherService.changeTeacherStatus(id, status)

      // Update in local state
      const index = teachers.value.findIndex(t => t.id === id)
      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (selectedTeacher.value?.id === id) {
        selectedTeacher.value = updatedTeacher
      }

      return updatedTeacher
    } catch (err: any) {
      error.value = err.message || 'Failed to change teacher status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function assignGrades(id: string, gradeLevels: number[]) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const updatedTeacher = await teacherService.assignGrades(id, gradeLevels)

      // Update in local state
      const index = teachers.value.findIndex(t => t.id === id)
      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (selectedTeacher.value?.id === id) {
        selectedTeacher.value = updatedTeacher
      }

      return updatedTeacher
    } catch (err: any) {
      error.value = err.message || 'Failed to assign grades'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function assignSpecializations(id: string, specializations: string[]) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const updatedTeacher = await teacherService.assignSpecializations(id, specializations)

      // Update in local state
      const index = teachers.value.findIndex(t => t.id === id)
      if (index !== -1) {
        teachers.value[index] = updatedTeacher
      }

      if (selectedTeacher.value?.id === id) {
        selectedTeacher.value = updatedTeacher
      }

      return updatedTeacher
    } catch (err: any) {
      error.value = err.message || 'Failed to assign specializations'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics() {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const stats = await teacherService.getStatistics()

      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchTeachers(query: string, params?: Omit<TeacherSearchParams, 'search'>) {
    loading.value = true
    error.value = null

    try {
      const { teacherService } = await import('@/services/teacherService')
      const response = await teacherService.searchTeachers(query, params)

      teachers.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to search teachers'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedTeacher(teacher: Teacher | null) {
    selectedTeacher.value = teacher
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    teachers.value = []
    selectedTeacher.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    }
    statistics.value = null
  }

  return {
    // State
    teachers,
    selectedTeacher,
    loading,
    error,
    pagination,
    statistics,

    // Getters
    totalTeachers,
    hasTeachers,
    isLoading,
    hasError,
    teachersByStatus,
    activeTeachers,
    inactiveTeachers,
    teachersByEmploymentType,
    fullTimeTeachers,
    partTimeTeachers,
    teachersByGrade,
    teachersWithExpiringCertifications,

    // Actions
    fetchTeachers,
    fetchTeacherById,
    fetchTeacherByUserId,
    fetchTeacherByEmployeeId,
    fetchActiveTeachers,
    fetchTeachersByGrade,
    fetchTeachersBySpecialization,
    createTeacher,
    updateTeacher,
    deleteTeacher,
    changeTeacherStatus,
    assignGrades,
    assignSpecializations,
    fetchStatistics,
    searchTeachers,
    setSelectedTeacher,
    clearError,
    resetState
  }
})
