/**
 * Attendance Service
 *
 * API client for attendance operations
 */

import type {
  Attendance,
  AttendanceCreateRequest,
  AttendanceBulkCreateRequest,
  AttendanceUpdateRequest,
  AttendanceListResponse,
  AttendanceStatistics,
  StudentAttendanceParams,
  ClassAttendanceParams,
  SchoolAttendanceParams,
  AttendanceDateRangeParams,
  AttendanceStatisticsParams,
  UnnotifiedAbsencesParams,
  UnnotifiedAbsencesResponse
} from '@/types/attendance'

const API_BASE = '/api/v1'

class AttendanceService {
  /**
   * Create a single attendance record
   */
  async createAttendance(data: AttendanceCreateRequest): Promise<Attendance> {
    const response = await fetch(`${API_BASE}/attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create attendance')
    }

    return response.json()
  }

  /**
   * Bulk create attendance records for a class
   */
  async bulkCreateAttendance(data: AttendanceBulkCreateRequest): Promise<Attendance[]> {
    const response = await fetch(`${API_BASE}/attendance/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to bulk create attendance')
    }

    return response.json()
  }

  /**
   * Get attendance record by ID
   */
  async getAttendanceById(id: string): Promise<Attendance> {
    const response = await fetch(`${API_BASE}/attendance/${id}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get attendance')
    }

    return response.json()
  }

  /**
   * Update attendance record
   */
  async updateAttendance(id: string, data: AttendanceUpdateRequest): Promise<Attendance> {
    const response = await fetch(`${API_BASE}/attendance/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update attendance')
    }

    return response.json()
  }

  /**
   * Delete attendance record
   */
  async deleteAttendance(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/attendance/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete attendance')
    }
  }

  /**
   * Get student attendance records
   */
  async getStudentAttendance(params: StudentAttendanceParams): Promise<AttendanceListResponse> {
    const { student_id, start_date, end_date, status, page = 1, limit = 50 } = params

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })

    if (start_date) queryParams.append('start_date', start_date)
    if (end_date) queryParams.append('end_date', end_date)
    if (status) queryParams.append('status', status)

    const response = await fetch(`${API_BASE}/attendance/student/${student_id}?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get student attendance')
    }

    return response.json()
  }

  /**
   * Get class attendance for a specific date
   */
  async getClassAttendance(params: ClassAttendanceParams): Promise<AttendanceListResponse> {
    const { class_id, attendance_date, page = 1, limit = 100 } = params

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })

    const response = await fetch(
      `${API_BASE}/attendance/class/${class_id}/date/${attendance_date}?${queryParams}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get class attendance')
    }

    return response.json()
  }

  /**
   * Get school attendance for a specific date
   */
  async getSchoolAttendance(params: SchoolAttendanceParams): Promise<AttendanceListResponse> {
    const { school_id, attendance_date, status, page = 1, limit = 100 } = params

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })

    if (status) queryParams.append('status', status)

    const response = await fetch(
      `${API_BASE}/attendance/school/${school_id}/date/${attendance_date}?${queryParams}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get school attendance')
    }

    return response.json()
  }

  /**
   * Get attendance records within a date range
   */
  async getAttendanceByDateRange(params: AttendanceDateRangeParams): Promise<Attendance[]> {
    const { school_id, start_date, end_date, class_id, student_id, status } = params

    const queryParams = new URLSearchParams({
      school_id,
      start_date,
      end_date
    })

    if (class_id) queryParams.append('class_id', class_id)
    if (student_id) queryParams.append('student_id', student_id)
    if (status) queryParams.append('status', status)

    const response = await fetch(`${API_BASE}/attendance/date-range?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get attendance by date range')
    }

    return response.json()
  }

  /**
   * Get unnotified absences for a school
   */
  async getUnnotifiedAbsences(
    params: UnnotifiedAbsencesParams
  ): Promise<UnnotifiedAbsencesResponse> {
    const { school_id, attendance_date } = params

    const queryParams = new URLSearchParams()
    if (attendance_date) queryParams.append('attendance_date', attendance_date)

    const response = await fetch(
      `${API_BASE}/attendance/unnotified-absences/school/${school_id}?${queryParams}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get unnotified absences')
    }

    return response.json()
  }

  /**
   * Mark attendance records as parent notified
   */
  async markParentNotified(attendanceIds: string[]): Promise<{ message: string; count: number }> {
    const response = await fetch(`${API_BASE}/attendance/mark-notified`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ attendance_ids: attendanceIds })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to mark parent notified')
    }

    return response.json()
  }

  /**
   * Get attendance statistics
   */
  async getStatistics(params: AttendanceStatisticsParams): Promise<AttendanceStatistics> {
    const { school_id, start_date, end_date, class_id } = params

    const queryParams = new URLSearchParams({
      school_id,
      start_date,
      end_date
    })

    if (class_id) queryParams.append('class_id', class_id)

    const response = await fetch(`${API_BASE}/attendance/statistics/summary?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to get attendance statistics')
    }

    return response.json()
  }
}

export default new AttendanceService()
