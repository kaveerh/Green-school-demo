/**
 * Teacher Types and Interfaces
 * TypeScript definitions for teacher-related data structures
 */

import { User } from './user'

export type TeacherStatus = 'active' | 'inactive' | 'on_leave' | 'terminated'
export type EmploymentType = 'full-time' | 'part-time' | 'contract' | 'substitute'
export type EducationLevel = 'High School' | 'Associate' | "Bachelor's" | "Master's" | 'PhD' | 'Other'
export type GradeLevel = 1 | 2 | 3 | 4 | 5 | 6 | 7

export interface Teacher {
  id: string
  school_id: string
  user_id: string

  // Teacher-specific fields
  employee_id: string
  hire_date: string
  termination_date?: string
  department?: string
  job_title?: string

  // Teaching credentials
  certification_number?: string
  certification_expiry?: string
  education_level?: EducationLevel
  university?: string

  // Teaching assignments
  grade_levels: number[]
  specializations: string[]

  // Employment details
  employment_type?: EmploymentType
  salary?: number
  work_hours_per_week?: number

  // Contact and emergency
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relationship?: string

  // Status
  status?: TeacherStatus
  is_active?: boolean

  // Metadata and settings
  bio?: string
  office_room?: string
  office_hours?: Record<string, any>
  preferences?: Record<string, any>

  // Computed fields (from backend)
  is_currently_employed?: boolean
  years_of_service?: number
  is_certification_valid?: boolean
  is_full_time?: boolean

  // Relationships
  user?: User

  // Audit fields
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
  deleted_at?: string
  deleted_by?: string
}

export interface TeacherCreateInput {
  school_id: string
  user_id: string
  employee_id: string
  hire_date: string
  department?: string
  job_title?: string
  certification_number?: string
  certification_expiry?: string
  education_level?: EducationLevel
  university?: string
  grade_levels: number[]
  specializations?: string[]
  employment_type?: EmploymentType
  salary?: number
  work_hours_per_week?: number
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relationship?: string
  bio?: string
  office_room?: string
  office_hours?: Record<string, any>
  preferences?: Record<string, any>
}

export interface TeacherUpdateInput {
  department?: string
  job_title?: string
  certification_number?: string
  certification_expiry?: string
  education_level?: EducationLevel
  university?: string
  grade_levels?: number[]
  specializations?: string[]
  employment_type?: EmploymentType
  salary?: number
  work_hours_per_week?: number
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relationship?: string
  bio?: string
  office_room?: string
  office_hours?: Record<string, any>
  preferences?: Record<string, any>
  termination_date?: string
}

export interface TeacherStatusChangeInput {
  status: TeacherStatus
}

export interface TeacherSearchParams {
  search?: string
  status?: TeacherStatus
  employment_type?: EmploymentType
  department?: string
  grade_level?: number
  specialization?: string
  certification_expiring?: boolean
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface TeacherStatistics {
  total: number
  by_status: {
    active: number
    inactive: number
    on_leave: number
    terminated: number
  }
  by_employment_type: {
    full_time: number
    part_time: number
    contract: number
    substitute: number
  }
  by_grade_level: {
    grade_1: number
    grade_2: number
    grade_3: number
    grade_4: number
    grade_5: number
    grade_6: number
    grade_7: number
  }
  certifications_expiring_soon: number
  average_years_of_service: number
}

export interface TeacherWithDetails extends Teacher {
  user: User
  class_count?: number
  student_count?: number
}
