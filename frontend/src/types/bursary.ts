/**
 * Bursary Types and Interfaces
 * TypeScript definitions for bursary (financial aid) data structures
 */

export type BursaryType = 'need_based' | 'merit' | 'athletic' | 'academic' | 'community_service' | 'other'
export type BursaryCoverageType = 'percentage' | 'fixed_amount' | 'full_tuition'
export type BursaryStatus = 'draft' | 'active' | 'paused' | 'closed'

export interface Bursary {
  id: string
  school_id: string
  name: string
  bursary_type: BursaryType
  description?: string
  coverage_type: BursaryCoverageType
  coverage_value: number
  max_recipients?: number
  current_recipients: number
  academic_year: string
  application_deadline?: string
  min_grade?: number
  max_grade?: number
  eligibility_criteria?: string
  required_documents?: string
  status: BursaryStatus
  is_active: boolean
  created_at: string
  updated_at: string

  // Computed properties
  can_accept_applications?: boolean
  is_full?: boolean
  slots_available?: number
  coverage_display?: string
}

export interface BursaryCreateInput {
  school_id: string
  name: string
  bursary_type: BursaryType
  description?: string
  coverage_type: BursaryCoverageType
  coverage_value: number
  max_recipients?: number
  academic_year: string
  application_deadline?: string
  min_grade?: number
  max_grade?: number
  eligibility_criteria?: string
  required_documents?: string
  status?: BursaryStatus
  is_active?: boolean
}

export interface BursaryUpdateInput {
  name?: string
  description?: string
  coverage_value?: number
  max_recipients?: number
  application_deadline?: string
  min_grade?: number
  max_grade?: number
  eligibility_criteria?: string
  required_documents?: string
  status?: BursaryStatus
  is_active?: boolean
}

export interface BursarySearchParams {
  school_id: string
  academic_year?: string
  bursary_type?: BursaryType
  is_active?: boolean
  status?: BursaryStatus
  page?: number
  limit?: number
}

export interface BursaryStatistics {
  total_bursaries: number
  active_bursaries: number
  total_recipients: number
  total_funding_allocated: number
  by_type: Record<string, number>
  academic_years: string[]
}

export interface BursaryListResponse {
  data: Bursary[]
  total: number
  page: number
  limit: number
  pages: number
}
