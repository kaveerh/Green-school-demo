/**
 * User Types and Interfaces
 * TypeScript definitions for user-related data structures
 */

export type UserPersona = 'administrator' | 'teacher' | 'student' | 'parent' | 'vendor'
export type UserStatus = 'active' | 'inactive' | 'suspended'

export interface User {
  id: string
  school_id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  persona: UserPersona
  status: UserStatus
  is_active: boolean
  keycloak_id?: string
  phone?: string
  avatar_url?: string
  bio?: string
  metadata: Record<string, any>
  last_login_at?: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface UserCreateInput {
  email: string
  first_name: string
  last_name: string
  persona: UserPersona
  password: string
  school_id: string
  phone?: string
  avatar_url?: string
  bio?: string
  metadata?: Record<string, any>
}

export interface UserUpdateInput {
  first_name?: string
  last_name?: string
  phone?: string
  avatar_url?: string
  bio?: string
  metadata?: Record<string, any>
}

export interface UserStatusChangeInput {
  status: UserStatus
}

export interface UserPersonaChangeInput {
  persona: UserPersona
}

export interface UserSearchParams {
  search?: string
  persona?: UserPersona
  status?: UserStatus
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: Pagination
}

export interface UserStatistics {
  total: number
  by_persona: {
    administrators: number
    teachers: number
    students: number
    parents: number
    vendors: number
  }
  by_status: {
    active: number
    inactive: number
    suspended: number
  }
  recent_signups: number
  active_users: number
}
