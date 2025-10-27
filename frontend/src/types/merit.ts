/**
 * Merit Types
 * TypeScript interfaces for Merit entities
 */

export enum MeritCategory {
  ACADEMIC = 'academic',
  BEHAVIOR = 'behavior',
  PARTICIPATION = 'participation',
  LEADERSHIP = 'leadership',
  ATTENDANCE = 'attendance',
  OTHER = 'other',
}

export enum Quarter {
  Q1 = 'Q1',
  Q2 = 'Q2',
  Q3 = 'Q3',
  Q4 = 'Q4',
}

export enum PointsTier {
  BRONZE = 'bronze',
  SILVER = 'silver',
  GOLD = 'gold',
  PLATINUM = 'platinum',
}

export interface Merit {
  id: string
  school_id: string
  student_id: string
  awarded_by_id: string
  class_id: string | null
  subject_id: string | null

  // Merit Details
  category: MeritCategory
  points: number
  reason: string

  // Context
  quarter: Quarter | null
  academic_year: string | null
  awarded_date: string

  // Metadata
  is_class_award: boolean
  batch_id: string | null

  // Audit
  created_at: string
  updated_at: string
  deleted_at: string | null

  // Computed Properties
  category_display: string
  points_tier: PointsTier
  is_recent: boolean

  // Optional relationships
  student?: {
    id: string
    name: string
    grade_level: number
  }
  awarded_by?: {
    id: string
    name: string
  }
  class?: {
    id: string
    name: string
  }
  subject?: {
    id: string
    name: string
    code: string
  }
}

export interface MeritCreateInput {
  school_id: string
  student_id: string
  class_id?: string
  subject_id?: string
  category: MeritCategory
  points: number
  reason: string
  quarter?: Quarter
  academic_year?: string
  awarded_date?: string
}

export interface MeritBatchCreateInput {
  school_id: string
  student_ids: string[]
  class_id?: string
  subject_id?: string
  category: MeritCategory
  points: number
  reason: string
  quarter?: Quarter
  academic_year?: string
  awarded_date?: string
}

export interface MeritUpdateInput {
  category?: MeritCategory
  points?: number
  reason?: string
  quarter?: Quarter
  academic_year?: string
}

export interface MeritListResponse {
  merits: Merit[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface MeritSummary {
  total_points: number
  by_category: Record<string, { points: number; count: number }>
  by_quarter: Record<string, number>
  recent_merits: Merit[]
  merit_count: number
}

export interface ClassMeritSummary {
  total_points: number
  average_per_student: number
  by_category: Record<string, number>
  top_students: Array<{ student_id: string; total_points: number }>
}

export interface LeaderboardEntry {
  student_id: string
  total_points: number
  merit_count: number
  rank: number
  student?: {
    name: string
    grade_level: number
  }
}

export interface MeritStatistics {
  total_merits: number
  total_points: number
  by_category: Record<string, { count: number; points: number }>
  by_quarter: Record<string, number>
  unique_students: number
  average_per_student: number
}

export interface MeritFilters {
  category?: MeritCategory | string
  quarter?: Quarter | string
  awarded_by_id?: string
  start_date?: string
  end_date?: string
  page?: number
  limit?: number
}
