/**
 * Student Types and Interfaces
 * TypeScript definitions for student-related data structures
 */

import type { User } from './user'

export type StudentStatus = 'enrolled' | 'graduated' | 'transferred' | 'withdrawn' | 'suspended'
export type Gender = 'male' | 'female' | 'other' | 'prefer_not_to_say'
export type RelationshipType = 'mother' | 'father' | 'guardian' | 'grandparent' | 'other'

export interface Student {
  id: string
  school_id: string
  user_id: string
  student_id: string
  grade_level: number
  date_of_birth: string
  gender?: string
  enrollment_date: string
  graduation_date?: string
  allergies?: string
  medical_notes?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relation?: string
  photo_url?: string
  status: string
  user?: User
  is_currently_enrolled?: boolean
  age?: number
  years_enrolled?: number
  can_promote?: boolean
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface StudentCreateInput {
  school_id: string
  user_id: string
  student_id: string
  grade_level: number
  date_of_birth: string
  gender?: Gender
  enrollment_date: string
  graduation_date?: string
  allergies?: string
  medical_notes?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relation?: string
  photo_url?: string
  status?: StudentStatus
}

export interface StudentUpdateInput {
  grade_level?: number
  gender?: Gender
  graduation_date?: string
  allergies?: string
  medical_notes?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relation?: string
  photo_url?: string
  status?: StudentStatus
}

export interface StudentStatusChangeInput {
  status: StudentStatus
}

export interface StudentSearchParams {
  search?: string
  grade_level?: number
  status?: StudentStatus
  gender?: Gender
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface StudentStatistics {
  total: number
  by_status: Record<string, number>
  by_grade_level: Record<string, number>
  by_gender: Record<string, number>
  currently_enrolled: number
  average_age: number
}

export interface ParentStudentRelationship {
  id: string
  parent_id: string
  student_id: string
  relationship_type: string
  is_primary_contact: boolean
  has_pickup_permission: boolean
  created_at: string
}

export interface ParentStudentLinkInput {
  parent_id: string
  student_id: string
  relationship_type: RelationshipType
  is_primary_contact?: boolean
  has_pickup_permission?: boolean
}

export interface ParentStudentRelationshipListResponse {
  data: ParentStudentRelationship[]
}
