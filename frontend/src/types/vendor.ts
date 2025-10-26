/**
 * Vendor Types
 * TypeScript interfaces for Vendor entities
 */

export enum VendorType {
  FOOD_SERVICE = 'food_service',
  SUPPLIES = 'supplies',
  MAINTENANCE = 'maintenance',
  IT_SERVICES = 'it_services',
  TRANSPORTATION = 'transportation',
  EVENTS = 'events',
  OTHER = 'other',
}

export enum VendorStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  TERMINATED = 'terminated',
}

export interface Vendor {
  id: string
  school_id: string
  user_id: string | null

  // Company Information
  company_name: string
  business_number: string | null

  // Vendor Classification
  vendor_type: VendorType
  category: string | null
  services_provided: string[] | null

  // Contact Information
  primary_contact_name: string | null
  primary_contact_title: string | null
  email: string | null
  phone: string | null
  phone_alt: string | null
  website: string | null

  // Address
  address_line1: string | null
  address_line2: string | null
  city: string | null
  state: string | null
  postal_code: string | null
  country: string | null

  // Business Details
  description: string | null
  certifications: string[] | null
  insurance_policy_number: string | null
  insurance_expiry_date: string | null

  // Contract & Financial
  contract_start_date: string | null
  contract_end_date: string | null
  contract_value: number | null
  payment_terms: string | null
  tax_exempt: boolean | null

  // Performance & Status
  status: VendorStatus
  performance_rating: number | null
  total_orders: number | null

  // Preferences
  preferred: boolean | null
  notes: string | null

  // Audit
  created_at: string
  updated_at: string
  deleted_at: string | null

  // Computed Properties
  is_active: boolean
  contract_active: boolean
  contract_expiring_soon: boolean
  insurance_expired: boolean
  full_address: string
}

export interface VendorCreateInput {
  school_id: string
  user_id?: string
  company_name: string
  business_number?: string
  vendor_type: VendorType
  category?: string
  services_provided?: string[]
  primary_contact_name?: string
  primary_contact_title?: string
  email?: string
  phone?: string
  phone_alt?: string
  website?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string
  description?: string
  certifications?: string[]
  insurance_policy_number?: string
  insurance_expiry_date?: string
  contract_start_date?: string
  contract_end_date?: string
  contract_value?: number
  payment_terms?: string
  tax_exempt?: boolean
  status?: VendorStatus
  performance_rating?: number
  total_orders?: number
  preferred?: boolean
  notes?: string
}

export interface VendorUpdateInput {
  user_id?: string
  company_name?: string
  business_number?: string
  vendor_type?: VendorType
  category?: string
  services_provided?: string[]
  primary_contact_name?: string
  primary_contact_title?: string
  email?: string
  phone?: string
  phone_alt?: string
  website?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string
  description?: string
  certifications?: string[]
  insurance_policy_number?: string
  insurance_expiry_date?: string
  contract_start_date?: string
  contract_end_date?: string
  contract_value?: number
  payment_terms?: string
  tax_exempt?: boolean
  status?: VendorStatus
  performance_rating?: number
  total_orders?: number
  preferred?: boolean
  notes?: string
}

export interface VendorListResponse {
  vendors: Vendor[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface VendorStatistics {
  total_vendors: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  active_vendors: number
  preferred_vendors: number
  average_rating: number
  total_contract_value: number
  expiring_contracts: number
}

export interface VendorAlert {
  vendor_id: string
  company_name: string
  contract_end_date?: string
  days_until_expiry?: number
  insurance_expiry_date?: string
  days_expired?: number
}

export interface VendorAlertsResponse {
  expiring_contracts: VendorAlert[]
  expired_insurance: VendorAlert[]
}

export interface VendorFilters {
  vendor_type?: VendorType | string
  vendor_status?: VendorStatus | string
  page?: number
  limit?: number
}
