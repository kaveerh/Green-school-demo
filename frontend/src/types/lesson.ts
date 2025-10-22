/**
 * Lesson Types
 *
 * TypeScript type definitions for lesson planning and curriculum management
 */

export type LessonStatus = 'draft' | 'scheduled' | 'in_progress' | 'completed' | 'cancelled'

export interface Lesson {
  id: string
  school_id: string
  class_id: string
  teacher_id: string
  subject_id: string

  // Identification
  title: string
  lesson_number: number

  // Scheduling
  scheduled_date: string // ISO date string
  duration_minutes: number

  // Content
  description?: string
  learning_objectives: string[]
  materials_needed: string[]
  curriculum_standards: string[]

  // Lesson plan sections
  introduction?: string
  main_activity?: string
  assessment?: string
  homework?: string
  notes?: string

  // Resources
  attachments: LessonAttachment[]
  links: string[]

  // Status & Progress
  status: LessonStatus
  completion_percentage: number
  actual_duration_minutes?: number

  // Reflection
  reflection?: string
  what_went_well?: string
  what_to_improve?: string
  modifications_needed?: string

  // Display
  color?: string
  is_template: boolean
  template_id?: string

  // Computed fields
  is_past_due?: boolean
  is_upcoming?: boolean
  is_completed?: boolean
  duration_display?: string

  // Relationship data (when loaded)
  class_name?: string
  class_code?: string
  subject_name?: string
  subject_code?: string
  teacher_name?: string

  // Timestamps
  created_at: string
  updated_at: string
  deleted_at?: string
}

export interface LessonAttachment {
  id: string
  name: string
  url: string
  size: number
  type: string
  uploaded_at: string
}

export interface LessonCreateRequest {
  title: string
  description?: string
  class_id: string
  teacher_id: string
  subject_id: string
  scheduled_date: string
  duration_minutes?: number
  lesson_number?: number

  // Content
  learning_objectives?: string[]
  materials_needed?: string[]
  curriculum_standards?: string[]

  // Lesson plan
  introduction?: string
  main_activity?: string
  assessment?: string
  homework?: string
  notes?: string

  // Resources
  links?: string[]

  // Display
  color?: string
  is_template?: boolean
  template_id?: string
}

export interface LessonUpdateRequest {
  title?: string
  description?: string
  scheduled_date?: string
  duration_minutes?: number
  lesson_number?: number

  // Content
  learning_objectives?: string[]
  materials_needed?: string[]
  curriculum_standards?: string[]

  // Lesson plan
  introduction?: string
  main_activity?: string
  assessment?: string
  homework?: string
  notes?: string

  // Resources
  links?: string[]

  // Display
  color?: string

  // Relationships
  class_id?: string
  teacher_id?: string
  subject_id?: string
}

export interface LessonCompleteRequest {
  completion_percentage?: number
  actual_duration_minutes?: number
  reflection?: string
  what_went_well?: string
  what_to_improve?: string
  modifications_needed?: string
}

export interface LessonFromTemplateRequest {
  template_id: string
  class_id: string
  scheduled_date: string
  lesson_number?: number
  title?: string
  color?: string
}

export interface LessonDuplicateRequest {
  new_scheduled_date: string
  new_class_id?: string
  new_lesson_number?: number
}

export interface LessonListResponse {
  lessons: Lesson[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface LessonStatistics {
  total_lessons: number
  by_status: Record<LessonStatus, number>
  by_subject: Record<string, number>
  average_duration: number
  average_actual_duration: number
  total_teaching_minutes: number
  completion_rate: number
  average_completion_percentage: number
}

export interface LessonFilters {
  page?: number
  limit?: number
  class_id?: string
  teacher_id?: string
  subject_id?: string
  status?: LessonStatus
  start_date?: string
  end_date?: string
  is_template?: boolean
}

export interface LessonSearchParams {
  query: string
  teacher_id?: string
  subject_id?: string
  limit?: number
}

export interface LessonDateRangeParams {
  start_date: string
  end_date: string
  teacher_id?: string
  class_id?: string
  subject_id?: string
}

export interface LessonUpcomingParams {
  teacher_id?: string
  days?: number
  limit?: number
}

export interface LessonTemplateParams {
  teacher_id?: string
  subject_id?: string
}

export interface LessonStatisticsParams {
  teacher_id?: string
  start_date?: string
  end_date?: string
}

// UI Helper types
export interface LessonFormData extends LessonCreateRequest {
  // Additional UI-only fields
}

export interface LessonCalendarEvent {
  id: string
  title: string
  start: Date
  end: Date
  color?: string
  lesson: Lesson
}

// Status display helpers
export const LessonStatusLabels: Record<LessonStatus, string> = {
  draft: 'Draft',
  scheduled: 'Scheduled',
  in_progress: 'In Progress',
  completed: 'Completed',
  cancelled: 'Cancelled'
}

export const LessonStatusColors: Record<LessonStatus, string> = {
  draft: 'gray',
  scheduled: 'blue',
  in_progress: 'orange',
  completed: 'green',
  cancelled: 'red'
}
