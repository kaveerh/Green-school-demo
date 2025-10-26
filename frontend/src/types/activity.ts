/**
 * Activity Types
 *
 * TypeScript type definitions for extracurricular activities.
 */

// Activity type enum
export type ActivityType =
  | 'sports'
  | 'club'
  | 'art'
  | 'music'
  | 'academic'
  | 'other'

// Activity status enum
export type ActivityStatus =
  | 'active'
  | 'full'
  | 'cancelled'
  | 'completed'

// Enrollment status enum
export type EnrollmentStatus =
  | 'active'
  | 'waitlisted'
  | 'withdrawn'
  | 'completed'

// Payment status enum
export type PaymentStatus =
  | 'pending'
  | 'partial'
  | 'paid'
  | 'waived'

// Schedule interface
export interface ActivitySchedule {
  days: string[] // e.g., ["Monday", "Wednesday", "Friday"]
  start_time: string // e.g., "15:30"
  end_time: string // e.g., "17:00"
}

// Nested types for relationships
export interface ActivityCoordinator {
  id: string
  name: string
  email: string
}

export interface ActivityRoom {
  id: string
  name: string
  room_number: string | null
}

export interface ActivityStudent {
  id: string
  name: string | null
  grade_level: number | null
}

// Main Activity interface
export interface Activity {
  id: string
  school_id: string
  coordinator_id: string | null

  // Identification
  name: string
  code: string | null

  // Classification
  activity_type: ActivityType
  category: string | null
  description: string | null

  // Eligibility
  grade_levels: number[]
  max_participants: number | null
  min_participants: number | null

  // Scheduling
  schedule: ActivitySchedule | null
  start_date: string | null
  end_date: string | null

  // Location
  location: string | null
  room_id: string | null

  // Financial
  cost: number
  registration_fee: number
  equipment_fee: number

  // Requirements
  requirements: string[] | null
  equipment_needed: string[] | null
  uniform_required: boolean

  // Contact
  contact_email: string | null
  contact_phone: string | null
  parent_info: string | null

  // Status
  status: ActivityStatus
  is_featured: boolean
  registration_open: boolean

  // Display
  photo_url: string | null
  color: string | null

  // Audit
  created_at: string
  updated_at: string

  // Computed fields
  total_cost?: number
  enrollment_count?: number
  available_slots?: number
  is_full?: boolean
  is_active?: boolean
  is_upcoming?: boolean
  is_completed?: boolean

  // Relationships
  coordinator?: ActivityCoordinator
  room?: ActivityRoom
}

// Activity Enrollment interface
export interface ActivityEnrollment {
  id: string
  activity_id: string
  student_id: string

  // Enrollment details
  enrollment_date: string
  status: EnrollmentStatus

  // Payment
  payment_status: PaymentStatus
  amount_paid: number
  payment_date: string | null

  // Attendance
  attendance_count: number
  total_sessions: number | null

  // Performance
  performance_notes: string | null
  achievements: string[] | null

  // Consent & Requirements
  parent_consent: boolean
  parent_consent_date: string | null
  medical_clearance: boolean
  emergency_contact_provided: boolean

  // Withdrawal
  withdrawn_at: string | null
  withdrawn_reason: string | null

  // Audit
  created_at: string
  updated_at: string

  // Computed fields
  attendance_percentage?: number
  is_active?: boolean
  payment_complete?: boolean

  // Relationships
  activity?: Activity
  student?: ActivityStudent
}

// Create/Update DTOs
export interface ActivityCreateInput {
  school_id: string
  name: string
  code?: string
  activity_type: ActivityType
  category?: string
  description?: string
  grade_levels: number[]
  max_participants?: number
  min_participants?: number
  schedule?: ActivitySchedule
  start_date?: string
  end_date?: string
  location?: string
  room_id?: string
  cost?: number
  registration_fee?: number
  equipment_fee?: number
  requirements?: string[]
  equipment_needed?: string[]
  uniform_required?: boolean
  contact_email?: string
  contact_phone?: string
  parent_info?: string
  coordinator_id?: string
  status?: ActivityStatus
  is_featured?: boolean
  registration_open?: boolean
  photo_url?: string
  color?: string
}

export interface ActivityUpdateInput {
  name?: string
  code?: string
  activity_type?: ActivityType
  category?: string
  description?: string
  grade_levels?: number[]
  max_participants?: number
  min_participants?: number
  schedule?: ActivitySchedule
  start_date?: string
  end_date?: string
  location?: string
  room_id?: string
  cost?: number
  registration_fee?: number
  equipment_fee?: number
  requirements?: string[]
  equipment_needed?: string[]
  uniform_required?: boolean
  contact_email?: string
  contact_phone?: string
  parent_info?: string
  coordinator_id?: string
  status?: ActivityStatus
  is_featured?: boolean
  registration_open?: boolean
  photo_url?: string
  color?: string
}

export interface EnrollmentCreateInput {
  student_id: string
  parent_consent?: boolean
  medical_clearance?: boolean
  emergency_contact_provided?: boolean
}

export interface EnrollmentWithdrawInput {
  reason?: string
}

export interface PaymentRecordInput {
  amount: number
  payment_date?: string
}

// Response types
export interface ActivityListResponse {
  activities: Activity[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface RosterResponse {
  activity: Activity
  active_enrollments: ActivityEnrollment[]
  waitlisted_enrollments: ActivityEnrollment[]
  total_enrolled: number
  total_waitlisted: number
  available_slots: number
}

export interface PaymentSummary {
  activity_id: string
  activity_name: string
  total_expected: number
  total_collected: number
  total_outstanding: number
  payment_breakdown: Record<PaymentStatus, number>
}

export interface ActivityStatistics {
  total_activities: number
  by_type: Record<ActivityType, number>
  by_status: Record<ActivityStatus, number>
  total_enrollments: number
  average_enrollment_per_activity: number
  total_revenue: number
  total_outstanding: number
}

// Filter types
export interface ActivityFilters {
  activity_type?: ActivityType
  status?: ActivityStatus
  grade_level?: number
  registration_open?: boolean
  search?: string
  page?: number
  limit?: number
}
