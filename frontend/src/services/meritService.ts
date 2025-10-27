/**
 * Merit Service
 * API client for merit operations
 */

import type {
  Merit,
  MeritCreateInput,
  MeritBatchCreateInput,
  MeritUpdateInput,
  MeritListResponse,
  MeritSummary,
  ClassMeritSummary,
  LeaderboardEntry,
  MeritStatistics,
  MeritFilters,
} from '@/types/merit'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class MeritService {
  private baseUrl = `${API_BASE_URL}/api/v1/merits`

  /**
   * Get all merits with optional filters
   */
  async getMerits(
    schoolId: string,
    filters?: MeritFilters
  ): Promise<MeritListResponse> {
    const params = new URLSearchParams({
      school_id: schoolId,
      page: String(filters?.page || 1),
      limit: String(filters?.limit || 50),
    })

    if (filters?.category) {
      params.append('category', filters.category)
    }
    if (filters?.quarter) {
      params.append('quarter', filters.quarter)
    }
    if (filters?.awarded_by_id) {
      params.append('awarded_by_id', filters.awarded_by_id)
    }
    if (filters?.start_date) {
      params.append('start_date', filters.start_date)
    }
    if (filters?.end_date) {
      params.append('end_date', filters.end_date)
    }

    const response = await fetch(`${this.baseUrl}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch merits: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get merit by ID
   */
  async getMeritById(meritId: string): Promise<Merit> {
    const response = await fetch(`${this.baseUrl}/${meritId}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch merit: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Award merit to a student
   */
  async awardMerit(
    meritData: MeritCreateInput,
    awardedById: string
  ): Promise<Merit> {
    const params = new URLSearchParams({ awarded_by_id: awardedById })

    const response = await fetch(`${this.baseUrl}?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(meritData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to award merit: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Award merits to multiple students (batch/class award)
   */
  async awardBatchMerits(
    meritData: MeritBatchCreateInput,
    awardedById: string
  ): Promise<Merit[]> {
    const params = new URLSearchParams({ awarded_by_id: awardedById })

    const response = await fetch(`${this.baseUrl}/batch?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(meritData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to award batch merits: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Update merit
   */
  async updateMerit(
    meritId: string,
    meritData: MeritUpdateInput,
    updatedById: string
  ): Promise<Merit> {
    const params = new URLSearchParams({ updated_by_id: updatedById })

    const response = await fetch(`${this.baseUrl}/${meritId}?${params}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(meritData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to update merit: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Revoke merit (soft delete)
   */
  async revokeMerit(meritId: string, deletedById: string): Promise<void> {
    const params = new URLSearchParams({ deleted_by_id: deletedById })

    const response = await fetch(`${this.baseUrl}/${meritId}?${params}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`Failed to revoke merit: ${response.statusText}`)
    }
  }

  /**
   * Get student merit history
   */
  async getStudentMerits(
    studentId: string,
    filters?: { category?: string; quarter?: string; page?: number; limit?: number }
  ): Promise<MeritListResponse> {
    const params = new URLSearchParams({
      page: String(filters?.page || 1),
      limit: String(filters?.limit || 50),
    })

    if (filters?.category) {
      params.append('category', filters.category)
    }
    if (filters?.quarter) {
      params.append('quarter', filters.quarter)
    }

    const response = await fetch(`${this.baseUrl}/student/${studentId}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch student merits: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get student merit summary
   */
  async getStudentSummary(studentId: string): Promise<MeritSummary> {
    const response = await fetch(`${this.baseUrl}/student/${studentId}/summary`)
    if (!response.ok) {
      throw new Error(`Failed to fetch student summary: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get class merits
   */
  async getClassMerits(
    classId: string,
    filters?: { quarter?: string; category?: string; page?: number; limit?: number }
  ): Promise<MeritListResponse> {
    const params = new URLSearchParams({
      page: String(filters?.page || 1),
      limit: String(filters?.limit || 50),
    })

    if (filters?.quarter) {
      params.append('quarter', filters.quarter)
    }
    if (filters?.category) {
      params.append('category', filters.category)
    }

    const response = await fetch(`${this.baseUrl}/class/${classId}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch class merits: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get class merit summary
   */
  async getClassSummary(classId: string, quarter?: string): Promise<ClassMeritSummary> {
    const params = new URLSearchParams()
    if (quarter) {
      params.append('quarter', quarter)
    }

    const response = await fetch(`${this.baseUrl}/class/${classId}/summary?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch class summary: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get merits awarded by teacher
   */
  async getTeacherMerits(
    teacherId: string,
    filters?: { quarter?: string; page?: number; limit?: number }
  ): Promise<MeritListResponse> {
    const params = new URLSearchParams({
      page: String(filters?.page || 1),
      limit: String(filters?.limit || 50),
    })

    if (filters?.quarter) {
      params.append('quarter', filters.quarter)
    }

    const response = await fetch(`${this.baseUrl}/teacher/${teacherId}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch teacher merits: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get merit leaderboard
   */
  async getLeaderboard(
    schoolId: string,
    gradeLevel?: number,
    quarter?: string,
    limit: number = 20
  ): Promise<LeaderboardEntry[]> {
    const params = new URLSearchParams({
      school_id: schoolId,
      limit: String(limit),
    })

    if (gradeLevel) {
      params.append('grade_level', String(gradeLevel))
    }
    if (quarter) {
      params.append('quarter', quarter)
    }

    const response = await fetch(`${this.baseUrl}/leaderboard/rankings?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch leaderboard: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get merit statistics
   */
  async getStatistics(
    schoolId: string,
    quarter?: string,
    gradeLevel?: number
  ): Promise<MeritStatistics> {
    const params = new URLSearchParams({ school_id: schoolId })

    if (quarter) {
      params.append('quarter', quarter)
    }
    if (gradeLevel) {
      params.append('grade_level', String(gradeLevel))
    }

    const response = await fetch(`${this.baseUrl}/statistics/summary?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch statistics: ${response.statusText}`)
    }
    return response.json()
  }
}

export const meritService = new MeritService()
