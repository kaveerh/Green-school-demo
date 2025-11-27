/**
 * Activity Fee Types and Interfaces
 * TypeScript definitions for activity fee (extracurricular fees) data structures
 */

export type ActivityFeeFrequency = 'one_time' | 'yearly' | 'quarterly' | 'monthly'
export type ActivityFeeProrateCalculation = 'monthly' | 'weekly' | 'daily' | 'none'

export interface ActivityFee {
  id: string
  school_id: string
  activity_id: string
  academic_year: string
  fee_amount: number
  fee_frequency: ActivityFeeFrequency
  allow_prorate: boolean
  prorate_calculation?: ActivityFeeProrateCalculation
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string

  // Computed properties
  can_prorate?: boolean
  frequency_display?: string

  // Relationships
  activity?: {
    id: string
    name: string
    activity_type: string
  }
}

export interface ActivityFeeCreateInput {
  school_id: string
  activity_id: string
  academic_year: string
  fee_amount: number
  fee_frequency: ActivityFeeFrequency
  allow_prorate?: boolean
  prorate_calculation?: ActivityFeeProrateCalculation
  description?: string
  is_active?: boolean
}

export interface ActivityFeeUpdateInput {
  fee_amount?: number
  fee_frequency?: ActivityFeeFrequency
  allow_prorate?: boolean
  prorate_calculation?: ActivityFeeProrateCalculation
  description?: string
  is_active?: boolean
}

export interface ActivityFeeSearchParams {
  school_id: string
  academic_year?: string
  fee_frequency?: ActivityFeeFrequency
  is_active?: boolean
  page?: number
  limit?: number
}

export interface ActivityFeeProrateResult {
  activity_fee_id: string
  original_amount: number
  fee_frequency: string
  can_prorate: boolean
  months_remaining: number
  prorated_amount: number
  savings: number
}

export interface ActivityFeeStatistics {
  total_activity_fees: number
  active_activity_fees: number
  total_revenue: number
  by_frequency: Record<string, number>
  by_activity: Array<{
    activity_id: string
    activity_name: string
    fee_count: number
    total_revenue: number
  }>
}

export interface ActivityFeeListResponse {
  data: ActivityFee[]
  total: number
  page: number
  limit: number
  pages: number
}
