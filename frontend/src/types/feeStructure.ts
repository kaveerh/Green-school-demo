/**
 * Fee Structure Types and Interfaces
 * TypeScript definitions for fee structure (tuition pricing) data structures
 */

export type PaymentFrequency = 'weekly' | 'monthly' | 'yearly'

export interface FeeStructure {
  id: string
  school_id: string
  grade_level: number
  academic_year: string

  // Tuition amounts
  yearly_amount: number
  monthly_amount: number
  weekly_amount: number

  // Payment frequency discounts
  yearly_discount: number
  monthly_discount: number
  weekly_discount: number

  // Sibling discounts
  sibling_2_discount: number
  sibling_3_discount: number
  sibling_4_plus_discount: number
  apply_sibling_to_all: boolean

  is_active: boolean
  created_at: string
  updated_at: string

  // Computed properties
  has_sibling_discounts?: boolean
  has_payment_discounts?: boolean
  grade_display?: string
}

export interface FeeStructureCreateInput {
  school_id: string
  grade_level: number
  academic_year: string
  yearly_amount: number
  monthly_amount: number
  weekly_amount: number
  yearly_discount?: number
  monthly_discount?: number
  weekly_discount?: number
  sibling_2_discount?: number
  sibling_3_discount?: number
  sibling_4_plus_discount?: number
  apply_sibling_to_all?: boolean
  is_active?: boolean
}

export interface FeeStructureUpdateInput {
  yearly_amount?: number
  monthly_amount?: number
  weekly_amount?: number
  yearly_discount?: number
  monthly_discount?: number
  weekly_discount?: number
  sibling_2_discount?: number
  sibling_3_discount?: number
  sibling_4_plus_discount?: number
  apply_sibling_to_all?: boolean
  is_active?: boolean
}

export interface FeeStructureSearchParams {
  school_id: string
  academic_year?: string
  grade_level?: number
  is_active?: boolean
  page?: number
  limit?: number
}

export interface FeeStructureStatistics {
  total_fee_structures: number
  active_fee_structures: number
  academic_years: string[]
  grades_covered: number[]
  total_students_assigned: number
}

export interface FeeStructureListResponse {
  data: FeeStructure[]
  total: number
  page: number
  limit: number
  pages: number
}
