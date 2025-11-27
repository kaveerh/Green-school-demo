/**
 * Payment Types and Interfaces
 * TypeScript definitions for payment-related data structures
 */

export type PaymentMethod = 'cash' | 'card' | 'bank_transfer' | 'check' | 'online' | 'other'
export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled'

export interface Payment {
  id: string
  school_id: string
  student_fee_id: string
  student_id: string
  amount: number
  payment_date: string
  payment_method: PaymentMethod
  transaction_reference?: string
  receipt_number: string
  allocation_notes?: string
  status: PaymentStatus
  refund_reason?: string
  refunded_at?: string
  notes?: string
  created_at: string
  updated_at: string

  // Computed properties
  is_completed?: boolean
  is_pending?: boolean
  is_refunded?: boolean
  can_be_refunded?: boolean
  display_amount?: string
  payment_method_display?: string

  // Relationships
  student?: {
    id: string
    student_id: string
    name: string
  }
  student_fee?: {
    id: string
    academic_year: string
    total_amount_due: number
    balance_due: number
  }
  processed_by?: {
    id: string
    name: string
  }
}

export interface PaymentCreateInput {
  school_id: string
  student_fee_id: string
  amount: number
  payment_method: PaymentMethod
  payment_date?: string
  transaction_reference?: string
  allocation_notes?: string
  notes?: string
  auto_generate_receipt?: boolean
}

export interface PaymentPendingCreateInput {
  school_id: string
  student_fee_id: string
  amount: number
  payment_method: PaymentMethod
  transaction_reference?: string
  notes?: string
}

export interface PaymentUpdateInput {
  transaction_reference?: string
  allocation_notes?: string
  notes?: string
}

export interface PaymentConfirmInput {
  transaction_reference?: string
}

export interface PaymentRefundInput {
  refund_reason: string
}

export interface PaymentSearchParams {
  school_id: string
  payment_status?: PaymentStatus
  payment_method?: PaymentMethod
  start_date?: string
  end_date?: string
  page?: number
  limit?: number
}

export interface PaymentReceipt {
  receipt_number: string
  payment_date: string
  payment_method: string
  amount: number
  display_amount: string

  student: {
    id: string
    name: string
    student_id: string
    grade_level: number
  }

  fee: {
    academic_year: string
    payment_frequency: string
    total_amount_due: number
    total_paid: number
    balance_due: number
    status: string
  }

  transaction_reference?: string
  allocation_notes?: string
  notes?: string

  processed_by?: {
    id: string
    name: string
  }

  status: string
  is_refunded: boolean
  refund_reason?: string
}

export interface RevenueReport {
  total_revenue: number
  total_payments: number
  average_payment: number
  by_payment_method: Record<string, {
    count: number
    total: number
  }>
  by_period: Array<{
    period: string
    count: number
    total: number
  }>
}

export interface PaymentListResponse {
  data: Payment[]
  total: number
  page: number
  limit: number
  pages: number
}
