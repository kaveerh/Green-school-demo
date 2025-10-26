/**
 * Attendance Store
 *
 * Pinia store for attendance state management
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import attendanceService from '@/services/attendanceService'
import type {
  Attendance,
  AttendanceCreateRequest,
  AttendanceBulkCreateRequest,
  AttendanceUpdateRequest,
  AttendanceStatistics,
  AttendanceStatus
} from '@/types/attendance'

export const useAttendanceStore = defineStore('attendance', () => {
  // State
  const studentAttendance = ref<Attendance[]>([])
  const classAttendance = ref<Attendance[]>([])
  const schoolAttendance = ref<Attendance[]>([])
  const unnotifiedAbsences = ref<Attendance[]>([])
  const currentAttendance = ref<Attendance | null>(null)
  const statistics = ref<AttendanceStatistics | null>(null)

  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const studentTotal = ref(0)
  const classTotal = ref(0)
  const schoolTotal = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(50)

  // Computed
  const hasStudentAttendance = computed(() => studentAttendance.value.length > 0)
  const hasClassAttendance = computed(() => classAttendance.value.length > 0)
  const hasUnnotifiedAbsences = computed(() => unnotifiedAbsences.value.length > 0)

  const studentAttendanceByDate = computed(() => {
    const grouped: Record<string, Attendance[]> = {}
    studentAttendance.value.forEach((record) => {
      if (!grouped[record.attendance_date]) {
        grouped[record.attendance_date] = []
      }
      grouped[record.attendance_date].push(record)
    })
    return grouped
  })

  const presentCount = computed(() => {
    return classAttendance.value.filter((a) => a.status === 'present').length
  })

  const absentCount = computed(() => {
    return classAttendance.value.filter((a) => a.status === 'absent' || a.status === 'sick')
      .length
  })

  const tardyCount = computed(() => {
    return classAttendance.value.filter((a) => a.status === 'tardy').length
  })

  const attendanceRate = computed(() => {
    const total = classAttendance.value.length
    if (total === 0) return 0
    return (presentCount.value / total) * 100
  })

  // Actions

  /**
   * Create a single attendance record
   */
  async function createAttendance(data: AttendanceCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const attendance = await attendanceService.createAttendance(data)
      return attendance
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Bulk create attendance for a class
   */
  async function bulkCreateAttendance(data: AttendanceBulkCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const attendanceRecords = await attendanceService.bulkCreateAttendance(data)
      classAttendance.value = attendanceRecords
      return attendanceRecords
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch attendance by ID
   */
  async function fetchAttendanceById(id: string) {
    loading.value = true
    error.value = null

    try {
      currentAttendance.value = await attendanceService.getAttendanceById(id)
      return currentAttendance.value
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update attendance record
   */
  async function updateAttendance(id: string, data: AttendanceUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updated = await attendanceService.updateAttendance(id, data)
      currentAttendance.value = updated

      // Update in lists if present
      const updateInList = (list: Attendance[]) => {
        const index = list.findIndex((a) => a.id === id)
        if (index !== -1) {
          list[index] = updated
        }
      }

      updateInList(studentAttendance.value)
      updateInList(classAttendance.value)
      updateInList(schoolAttendance.value)

      return updated
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete attendance record
   */
  async function deleteAttendance(id: string) {
    loading.value = true
    error.value = null

    try {
      await attendanceService.deleteAttendance(id)

      // Remove from all lists
      studentAttendance.value = studentAttendance.value.filter((a) => a.id !== id)
      classAttendance.value = classAttendance.value.filter((a) => a.id !== id)
      schoolAttendance.value = schoolAttendance.value.filter((a) => a.id !== id)

      if (currentAttendance.value?.id === id) {
        currentAttendance.value = null
      }
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch student attendance
   */
  async function fetchStudentAttendance(
    studentId: string,
    filters: {
      start_date?: string
      end_date?: string
      status?: AttendanceStatus
      page?: number
      limit?: number
    } = {}
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await attendanceService.getStudentAttendance({
        student_id: studentId,
        ...filters,
        page: filters.page || currentPage.value,
        limit: filters.limit || pageSize.value
      })

      studentAttendance.value = response.attendance
      studentTotal.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch class attendance for a specific date
   */
  async function fetchClassAttendance(classId: string, attendanceDate: string) {
    loading.value = true
    error.value = null

    try {
      const response = await attendanceService.getClassAttendance({
        class_id: classId,
        attendance_date: attendanceDate
      })

      classAttendance.value = response.attendance
      classTotal.value = response.total

      return response
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch school attendance for a specific date
   */
  async function fetchSchoolAttendance(
    schoolId: string,
    attendanceDate: string,
    status?: AttendanceStatus
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await attendanceService.getSchoolAttendance({
        school_id: schoolId,
        attendance_date: attendanceDate,
        status
      })

      schoolAttendance.value = response.attendance
      schoolTotal.value = response.total

      return response
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch unnotified absences
   */
  async function fetchUnnotifiedAbsences(schoolId: string, attendanceDate?: string) {
    loading.value = true
    error.value = null

    try {
      const response = await attendanceService.getUnnotifiedAbsences({
        school_id: schoolId,
        attendance_date: attendanceDate
      })

      unnotifiedAbsences.value = response.absences
      return response
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Mark parent as notified
   */
  async function markParentNotified(attendanceIds: string[]) {
    loading.value = true
    error.value = null

    try {
      const result = await attendanceService.markParentNotified(attendanceIds)

      // Update records in all lists
      const updateRecords = (list: Attendance[]) => {
        list.forEach((record) => {
          if (attendanceIds.includes(record.id)) {
            record.parent_notified = true
            record.notified_at = new Date().toISOString()
          }
        })
      }

      updateRecords(unnotifiedAbsences.value)
      updateRecords(classAttendance.value)
      updateRecords(schoolAttendance.value)

      // Remove from unnotified list
      unnotifiedAbsences.value = unnotifiedAbsences.value.filter(
        (a) => !attendanceIds.includes(a.id)
      )

      return result
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch attendance statistics
   */
  async function fetchStatistics(
    schoolId: string,
    startDate: string,
    endDate: string,
    classId?: string
  ) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await attendanceService.getStatistics({
        school_id: schoolId,
        start_date: startDate,
        end_date: endDate,
        class_id: classId
      })

      return statistics.value
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear all attendance data
   */
  function clearAttendance() {
    studentAttendance.value = []
    classAttendance.value = []
    schoolAttendance.value = []
    unnotifiedAbsences.value = []
    currentAttendance.value = null
    statistics.value = null
    error.value = null
    studentTotal.value = 0
    classTotal.value = 0
    schoolTotal.value = 0
  }

  return {
    // State
    studentAttendance,
    classAttendance,
    schoolAttendance,
    unnotifiedAbsences,
    currentAttendance,
    statistics,
    loading,
    error,
    studentTotal,
    classTotal,
    schoolTotal,
    currentPage,
    pageSize,

    // Computed
    hasStudentAttendance,
    hasClassAttendance,
    hasUnnotifiedAbsences,
    studentAttendanceByDate,
    presentCount,
    absentCount,
    tardyCount,
    attendanceRate,

    // Actions
    createAttendance,
    bulkCreateAttendance,
    fetchAttendanceById,
    updateAttendance,
    deleteAttendance,
    fetchStudentAttendance,
    fetchClassAttendance,
    fetchSchoolAttendance,
    fetchUnnotifiedAbsences,
    markParentNotified,
    fetchStatistics,
    clearAttendance
  }
})
