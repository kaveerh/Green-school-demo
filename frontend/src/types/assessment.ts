/**
 * Assessment Types
 *
 * TypeScript type definitions for student assessments, grading, and evaluation
 */

export type AssessmentType =
  | 'test'
  | 'quiz'
  | 'project'
  | 'assignment'
  | 'exam'
  | 'presentation'
  | 'homework'
  | 'lab'
  | 'other'

export type AssessmentStatus =
  | 'pending'
  | 'submitted'
  | 'graded'
  | 'returned'
  | 'late'
  | 'missing'
  | 'excused'

export type Quarter = 'Q1' | 'Q2' | 'Q3' | 'Q4'

export type LetterGrade =
  | 'A+'
  | 'A'
  | 'A-'
  | 'B+'
  | 'B'
  | 'B-'
  | 'C+'
  | 'C'
  | 'C-'
  | 'D+'
  | 'D'
  | 'D-'
  | 'F'

export interface StudentBasic {
  id: string
  student_id: string
  grade_level: number
  name?: string
}

export interface TeacherBasic {
  id: string
  name?: string
}

export interface SubjectBasic {
  id: string
  code: string
  name: string
}

export interface ClassBasic {
  id: string
  name: string
  code: string
}

export interface Assessment {
  id: string
  school_id: string
  student_id: string
  class_id: string
  subject_id: string
  teacher_id: string

  // Assessment Details
  title: string
  description?: string
  assessment_type: AssessmentType
  quarter: Quarter
  assessment_date: string // ISO date string
  due_date?: string // ISO date string

  // Grading
  total_points: number
  points_earned?: number
  percentage?: number
  letter_grade?: LetterGrade

  // Status and Feedback
  status: AssessmentStatus
  feedback?: string
  graded_at?: string // ISO datetime string
  returned_at?: string // ISO datetime string

  // Metadata
  weight: number
  is_extra_credit: boolean
  is_makeup: boolean

  // Computed Properties
  is_graded: boolean
  is_passing: boolean
  is_overdue: boolean
  grade_display: string

  // Relationship data (when loaded)
  student?: StudentBasic
  teacher?: TeacherBasic
  subject?: SubjectBasic
  class?: ClassBasic

  // Timestamps
  created_at: string
  updated_at: string
}

export interface AssessmentCreateRequest {
  school_id: string
  student_id: string
  class_id: string
  subject_id: string
  teacher_id: string
  title: string
  description?: string
  assessment_type: AssessmentType
  quarter: Quarter
  assessment_date: string
  due_date?: string
  total_points: number
  points_earned?: number
  status?: AssessmentStatus
  weight?: number
  is_extra_credit?: boolean
  is_makeup?: boolean
}

export interface AssessmentUpdateRequest {
  title?: string
  description?: string
  assessment_type?: AssessmentType
  assessment_date?: string
  due_date?: string
  total_points?: number
  weight?: number
  status?: AssessmentStatus
  is_extra_credit?: boolean
  is_makeup?: boolean
}

export interface AssessmentGradeRequest {
  points_earned: number
  feedback?: string
}

export interface AssessmentListResponse {
  assessments: Assessment[]
  total: number
  page: number
  limit: number
}

export interface AssessmentStatistics {
  total_assessments: number
  graded_assessments: number
  pending_assessments: number
  average_score: number
  by_type: Record<string, number>
}

export interface AssessmentFilters {
  page?: number
  limit?: number
  quarter?: Quarter
  subject_id?: string
  assessment_type?: AssessmentType
  status?: AssessmentStatus
}

export interface StudentAssessmentParams extends AssessmentFilters {
  student_id: string
}

export interface ClassAssessmentParams extends AssessmentFilters {
  class_id: string
}

export interface TeacherAssessmentParams extends AssessmentFilters {
  teacher_id: string
}

export interface AssessmentStatisticsParams {
  school_id: string
  quarter?: Quarter
}
