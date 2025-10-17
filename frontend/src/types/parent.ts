/**
 * Parent Types
 *
 * TypeScript type definitions for Parent entities and related data structures.
 */

import type { User } from './index'
import type { Student } from './student'

// Enums
export type ContactMethod = 'email' | 'phone' | 'sms' | 'app_notification'

export type RelationshipType =
  | 'mother'
  | 'father'
  | 'guardian'
  | 'stepmother'
  | 'stepfather'
  | 'grandparent'
  | 'foster_parent'
  | 'other'

// Parent Interface
export interface Parent {
  id: string
  school_id: string
  user_id: string
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact: boolean
  pickup_authorized: boolean
  receives_newsletter: boolean
  created_at: string
  updated_at: string

  // Nested relationships (optional)
  user?: User
  children?: ParentStudentRelationship[]
}

// Parent-Student Relationship
export interface ParentStudentRelationship {
  id: string
  school_id: string
  parent_id: string
  student_id: string
  relationship_type: RelationshipType
  is_primary_contact: boolean
  has_legal_custody: boolean
  has_pickup_permission: boolean
  created_at: string
  updated_at: string

  // Nested relationships (optional)
  parent?: Parent
  student?: Student
}

// Create/Update Input Types
export interface ParentCreateInput {
  school_id: string
  user_id: string
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact?: boolean
  pickup_authorized?: boolean
  receives_newsletter?: boolean
}

export interface ParentUpdateInput {
  occupation?: string
  workplace?: string
  phone_mobile?: string
  phone_work?: string
  preferred_contact_method?: ContactMethod
  emergency_contact?: boolean
  pickup_authorized?: boolean
  receives_newsletter?: boolean
}

// Link Student Input
export interface ParentStudentLinkInput {
  student_id: string
  relationship_type: RelationshipType
  is_primary_contact?: boolean
  has_legal_custody?: boolean
  has_pickup_permission?: boolean
}

// Statistics
export interface ParentStatistics {
  total_parents: number
  emergency_contacts: number
  pickup_authorized: number
  newsletter_subscribers: number
  parents_with_children: number
  parents_without_children: number
}

// API Response Types
export interface ParentListResponse {
  parents: Parent[]
  total: number
  page: number
  limit: number
}

export interface ParentSearchParams {
  school_id?: string
  page?: number
  limit?: number
  search?: string
}

// Helper Functions
export function getRelationshipTypeLabel(type: RelationshipType): string {
  const labels: Record<RelationshipType, string> = {
    mother: 'Mother',
    father: 'Father',
    guardian: 'Guardian',
    stepmother: 'Stepmother',
    stepfather: 'Stepfather',
    grandparent: 'Grandparent',
    foster_parent: 'Foster Parent',
    other: 'Other'
  }
  return labels[type] || type
}

export function getContactMethodLabel(method: ContactMethod): string {
  const labels: Record<ContactMethod, string> = {
    email: 'Email',
    phone: 'Phone',
    sms: 'SMS',
    app_notification: 'App Notification'
  }
  return labels[method] || method
}

export function formatParentName(parent: Parent): string {
  if (parent.user) {
    return `${parent.user.first_name} ${parent.user.last_name}`
  }
  return 'Unknown Parent'
}

export function getParentContactInfo(parent: Parent): string {
  const contacts: string[] = []

  if (parent.phone_mobile) {
    contacts.push(`Mobile: ${parent.phone_mobile}`)
  }

  if (parent.phone_work) {
    contacts.push(`Work: ${parent.phone_work}`)
  }

  if (parent.user?.email) {
    contacts.push(`Email: ${parent.user.email}`)
  }

  return contacts.join(' | ') || 'No contact info'
}

export const RELATIONSHIP_TYPES: RelationshipType[] = [
  'mother',
  'father',
  'guardian',
  'stepmother',
  'stepfather',
  'grandparent',
  'foster_parent',
  'other'
]

export const CONTACT_METHODS: ContactMethod[] = [
  'email',
  'phone',
  'sms',
  'app_notification'
]
