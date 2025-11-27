/**
 * Student Fee Types and Interfaces
 * TypeScript definitions for student fee assignment and management data structures
 */

export type StudentFeeStatus = 'pending' | 'partial' | 'paid' | 'overdue' | 'waived'
export type StudentFeePaymentFrequency = 'weekly' | 'monthly' | 'yearly'

export interface StudentFee {
  id: string
  school_id: string
  student_id: string
  academic_year: string
  payment_frequency: StudentFeePaymentFrequency

  // Fee breakdown
  base_tuition_amount: number
  activity_fees_amount: number
  material_fees_amount: number
  other_fees_amount: number

  // Discounts
  payment_discount_percent: number
  payment_discount_amount: number
  sibling_discount_percent: number
  sibling_discount_amount: number
  sibling_order: number

  // Bursary
  bursary_id?: string
  bursary_amount: number

  // Totals
  total_before_discounts: number
  total_discounts: number
  total_amount_due: number
  total_paid: number
  balance_due: number

  // Status and dates
  status: StudentFeeStatus
  due_date?: string
  last_payment_date?: string
  notes?: string

  created_at: string
  updated_at: string

  // Computed properties
  is_fully_paid?: boolean
  is_overdue?: boolean
  payment_progress_percent?: number
  has_bursary?: boolean

  // Relationships
  student?: {
    id: string
    student_id: string
    name: string
    grade_level: number
  }
  bursary?: {
    id: string
    name: string
    type: string
  }
}

export interface StudentFeeCreateInput {
  school_id: string
  student_id: string
  academic_year: string
  payment_frequency: StudentFeePaymentFrequency
  bursary_id?: string
  material_fees?: number
  other_fees?: number
  notes?: string
}

export interface StudentFeeUpdateInput {
  payment_frequency?: StudentFeePaymentFrequency
  bursary_id?: string
  material_fees?: number
  other_fees?: number
  notes?: string
  recalculate?: boolean
}

export interface StudentFeeSearchParams {
  school_id: string
  academic_year?: string
  status?: StudentFeeStatus
  payment_frequency?: StudentFeePaymentFrequency
  has_bursary?: boolean
  page?: number
  limit?: number
}

export interface StudentFeePreview {
  student_id: string
  student_name: string
  grade_level: number
  academic_year: string
  payment_frequency: string
  sibling_order: number

  // Fee breakdown
  base_tuition: number
  activity_fees: number
  material_fees: number
  other_fees: number
  total_before_discounts: number

  // Discounts
  payment_discount: {
    percent: number
    amount: number
  }
  sibling_discount: {
    percent: number
    amount: number
  }
  total_discounts: number
  total_after_discounts: number

  // Bursary
  bursary?: {
    id: string
    name: string
    type: string
    coverage_type: string
    coverage_value: number
    amount: number
  }
  bursary_amount: number

  // Final
  total_amount_due: number
  balance_due: number
  due_date?: string

  // Additional info
  activities: Array<{
    id: string
    name: string
    fee_amount: number
  }>
  fee_structure_id: string
}

export interface StudentFeeStatistics {
  total_fees: number
  total_amount_due: number
  total_collected: number
  total_outstanding: number
  by_status: Record<string, number>
  by_payment_frequency: Record<string, number>
  overdue_count: number
  overdue_amount: number
}

export interface StudentFeeListResponse {
  data: StudentFee[]
  total: number
  page: number
  limit: number
  pages: number
}
