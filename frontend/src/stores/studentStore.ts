/**
 * Student Store
 * Pinia store for student state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Student,
  StudentCreateInput,
  StudentUpdateInput,
  StudentSearchParams,
  StudentStatistics,
  ParentStudentRelationship,
  ParentStudentLinkInput
} from '@/types/student'
import type { PaginatedResponse } from '@/types/user'

export const useStudentStore = defineStore('student', () => {
  // State
  const students = ref<Student[]>([])
  const selectedStudent = ref<Student | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const statistics = ref<StudentStatistics | null>(null)
  const studentParents = ref<ParentStudentRelationship[]>([])

  // Getters
  const totalStudents = computed(() => pagination.value.total)
  const hasStudents = computed(() => students.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const studentsByGrade = computed(() => {
    return (grade: number) => students.value.filter(s => s.grade_level === grade)
  })

  const enrolledStudents = computed(() =>
    students.value.filter(s => s.is_currently_enrolled)
  )

  const studentsByStatus = computed(() => {
    return (status: string) => students.value.filter(s => s.status === status)
  })

  const graduatedStudents = computed(() =>
    students.value.filter(s => s.status === 'graduated')
  )

  const promotableStudents = computed(() =>
    students.value.filter(s => s.can_promote)
  )

  // Actions
  async function fetchStudents(params?: StudentSearchParams) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const response = await studentService.getStudents(params)

      students.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch students'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentById(id: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const student = await studentService.getStudentById(id)

      selectedStudent.value = student
      return student
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentByUserId(userId: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const student = await studentService.getStudentByUserId(userId)

      selectedStudent.value = student
      return student
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student by user ID'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentByStudentId(studentId: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const student = await studentService.getStudentByStudentId(studentId)

      selectedStudent.value = student
      return student
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student by student ID'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchEnrolledStudents(params?: { page?: number; limit?: number }) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const response = await studentService.getEnrolledStudents(params)

      students.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch enrolled students'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentsByGrade(grade: number, params?: { page?: number; limit?: number }) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const response = await studentService.getStudentsByGrade(grade, params)

      students.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch students by grade'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createStudent(studentData: StudentCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const student = await studentService.createStudent(studentData)

      // Add to local state
      students.value.unshift(student)
      pagination.value.total++

      return student
    } catch (err: any) {
      error.value = err.message || 'Failed to create student'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateStudent(id: string, studentData: StudentUpdateInput) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const updatedStudent = await studentService.updateStudent(id, studentData)

      // Update in local state
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1) {
        students.value[index] = updatedStudent
      }

      if (selectedStudent.value?.id === id) {
        selectedStudent.value = updatedStudent
      }

      return updatedStudent
    } catch (err: any) {
      error.value = err.message || 'Failed to update student'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteStudent(id: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      await studentService.deleteStudent(id)

      // Remove from local state
      students.value = students.value.filter(s => s.id !== id)
      pagination.value.total--

      if (selectedStudent.value?.id === id) {
        selectedStudent.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete student'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changeStudentStatus(id: string, status: 'enrolled' | 'graduated' | 'transferred' | 'withdrawn' | 'suspended') {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const updatedStudent = await studentService.changeStudentStatus(id, status)

      // Update in local state
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1) {
        students.value[index] = updatedStudent
      }

      if (selectedStudent.value?.id === id) {
        selectedStudent.value = updatedStudent
      }

      return updatedStudent
    } catch (err: any) {
      error.value = err.message || 'Failed to change student status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function promoteStudent(id: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const updatedStudent = await studentService.promoteStudent(id)

      // Update in local state
      const index = students.value.findIndex(s => s.id === id)
      if (index !== -1) {
        students.value[index] = updatedStudent
      }

      if (selectedStudent.value?.id === id) {
        selectedStudent.value = updatedStudent
      }

      return updatedStudent
    } catch (err: any) {
      error.value = err.message || 'Failed to promote student'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function linkParent(studentId: string, linkData: ParentStudentLinkInput) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const relationship = await studentService.linkParent(studentId, linkData)

      // Add to local state
      studentParents.value.push(relationship)

      return relationship
    } catch (err: any) {
      error.value = err.message || 'Failed to link parent'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function unlinkParent(studentId: string, parentId: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      await studentService.unlinkParent(studentId, parentId)

      // Remove from local state
      studentParents.value = studentParents.value.filter(
        r => !(r.student_id === studentId && r.parent_id === parentId)
      )

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to unlink parent'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentParents(studentId: string) {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const response = await studentService.getStudentParents(studentId)

      studentParents.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student parents'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics() {
    loading.value = true
    error.value = null

    try {
      const { studentService } = await import('@/services/studentService')
      const stats = await studentService.getStatistics()

      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedStudent(student: Student | null) {
    selectedStudent.value = student
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    students.value = []
    selectedStudent.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    }
    statistics.value = null
    studentParents.value = []
  }

  return {
    // State
    students,
    selectedStudent,
    loading,
    error,
    pagination,
    statistics,
    studentParents,

    // Getters
    totalStudents,
    hasStudents,
    isLoading,
    hasError,
    studentsByGrade,
    enrolledStudents,
    studentsByStatus,
    graduatedStudents,
    promotableStudents,

    // Actions
    fetchStudents,
    fetchStudentById,
    fetchStudentByUserId,
    fetchStudentByStudentId,
    fetchEnrolledStudents,
    fetchStudentsByGrade,
    createStudent,
    updateStudent,
    deleteStudent,
    changeStudentStatus,
    promoteStudent,
    linkParent,
    unlinkParent,
    fetchStudentParents,
    fetchStatistics,
    setSelectedStudent,
    clearError,
    resetState
  }
})
