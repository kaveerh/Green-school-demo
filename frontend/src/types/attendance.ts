/**
 * Attendance Types
 *
 * TypeScript type definitions for attendance tracking
 */

export type AttendanceStatus = 'present' | 'absent' | 'tardy' | 'excused' | 'sick'

export interface Attendance {
  id: string
  school_id: string
  student_id: string
  class_id: string | null
  attendance_date: string // ISO date string
  status: AttendanceStatus
  check_in_time: string | null // HH:MM:SS format
  check_out_time: string | null // HH:MM:SS format
  notes: string | null
  recorded_by: string | null
  parent_notified: boolean
  notified_at: string | null // ISO datetime
  created_at: string
  updated_at: string

  // Computed properties
  is_present: boolean
  is_absent: boolean
  needs_parent_notification: boolean
  duration_minutes: number

  // Relationships
  student?: {
    id: string
    student_id: string
    grade_level: number
    name: string
  }
  class?: {
    id: string
    name: string
    code: string
  }
  recorded_by_name?: string
}

export interface AttendanceCreateRequest {
  school_id: string
  student_id: string
  attendance_date: string
  status: AttendanceStatus
  class_id?: string | null
  check_in_time?: string | null
  check_out_time?: string | null
  notes?: string | null
  recorded_by?: string | null
}

export interface AttendanceBulkCreateRequest {
  school_id: string
  class_id: string
  attendance_date: string
  students: {
    student_id: string
    status: AttendanceStatus
    check_in_time?: string | null
    check_out_time?: string | null
    notes?: string | null
  }[]
}

export interface AttendanceUpdateRequest {
  status?: AttendanceStatus
  check_in_time?: string | null
  check_out_time?: string | null
  notes?: string | null
}

export interface AttendanceListResponse {
  attendance: Attendance[]
  total: number
  page: number
  limit: number
}

export interface AttendanceStatistics {
  total_records: number
  unique_students: number
  days_tracked: number
  avg_daily_attendance: number
  by_status: Record<string, number>
  present_count: number
  absent_count: number
  tardy_count: number
  excused_count: number
  attendance_rate: number
  absence_rate: number
}

export interface StudentAttendanceParams {
  student_id: string
  start_date?: string
  end_date?: string
  status?: AttendanceStatus
  page?: number
  limit?: number
}

export interface ClassAttendanceParams {
  class_id: string
  attendance_date: string
  page?: number
  limit?: number
}

export interface SchoolAttendanceParams {
  school_id: string
  attendance_date: string
  status?: AttendanceStatus
  page?: number
  limit?: number
}

export interface AttendanceDateRangeParams {
  school_id: string
  start_date: string
  end_date: string
  class_id?: string
  student_id?: string
  status?: AttendanceStatus
}

export interface AttendanceStatisticsParams {
  school_id: string
  start_date: string
  end_date: string
  class_id?: string
}

export interface UnnotifiedAbsencesParams {
  school_id: string
  attendance_date?: string
}

export interface UnnotifiedAbsencesResponse {
  absences: Attendance[]
  count: number
}

// Helper function to get status color
export function getStatusColor(status: AttendanceStatus): string {
  const colors: Record<AttendanceStatus, string> = {
    present: 'green',
    absent: 'red',
    tardy: 'yellow',
    excused: 'blue',
    sick: 'orange'
  }
  return colors[status] || 'gray'
}

// Helper function to get status label
export function getStatusLabel(status: AttendanceStatus): string {
  const labels: Record<AttendanceStatus, string> = {
    present: 'Present',
    absent: 'Absent',
    tardy: 'Tardy',
    excused: 'Excused',
    sick: 'Sick'
  }
  return labels[status] || status
}

// Helper function to format time
export function formatTime(time: string | null): string {
  if (!time) return '--'

  const [hours, minutes] = time.split(':')
  const hour = parseInt(hours, 10)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const hour12 = hour % 12 || 12

  return `${hour12}:${minutes} ${ampm}`
}

// Helper function to format duration
export function formatDuration(minutes: number): string {
  if (minutes === 0) return '--'

  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60

  if (hours === 0) return `${mins}m`
  if (mins === 0) return `${hours}h`
  return `${hours}h ${mins}m`
}
