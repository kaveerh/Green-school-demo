/**
 * Parent Service
 *
 * API client for Parent operations.
 */

import type {
  Parent,
  ParentCreateInput,
  ParentUpdateInput,
  ParentListResponse,
  ParentSearchParams,
  ParentStudentLinkInput,
  ParentStudentRelationship,
  ParentStatistics
} from '@/types/parent'
import type { Student } from '@/types/student'

const API_BASE_URL = 'http://localhost:8000/api/v1'

class ParentService {
  /**
   * Create a new parent
   */
  async createParent(parentData: ParentCreateInput): Promise<Parent> {
    const response = await fetch(`${API_BASE_URL}/parents`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(parentData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create parent')
    }

    return response.json()
  }

  /**
   * Get all parents with pagination
   */
  async getParents(params: ParentSearchParams = {}): Promise<ParentListResponse> {
    const searchParams = new URLSearchParams()

    if (params.school_id) {
      searchParams.append('school_id', params.school_id)
    }

    if (params.page) {
      searchParams.append('page', params.page.toString())
    }

    if (params.limit) {
      searchParams.append('limit', params.limit.toString())
    }

    const response = await fetch(`${API_BASE_URL}/parents?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to fetch parents')
    }

    return response.json()
  }

  /**
   * Get parent by ID
   */
  async getParentById(id: string): Promise<Parent> {
    const response = await fetch(`${API_BASE_URL}/parents/${id}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Parent not found')
      }
      throw new Error('Failed to fetch parent')
    }

    return response.json()
  }

  /**
   * Update parent
   */
  async updateParent(id: string, parentData: ParentUpdateInput): Promise<Parent> {
    const response = await fetch(`${API_BASE_URL}/parents/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(parentData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update parent')
    }

    return response.json()
  }

  /**
   * Delete parent
   */
  async deleteParent(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/parents/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Parent not found')
      }
      throw new Error('Failed to delete parent')
    }
  }

  /**
   * Link parent to student
   */
  async linkStudent(
    parentId: string,
    linkData: ParentStudentLinkInput
  ): Promise<ParentStudentRelationship> {
    const response = await fetch(`${API_BASE_URL}/parents/${parentId}/link-student`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(linkData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to link student')
    }

    return response.json()
  }

  /**
   * Unlink parent from student
   */
  async unlinkStudent(parentId: string, studentId: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/parents/${parentId}/unlink-student/${studentId}`,
      {
        method: 'DELETE',
      }
    )

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Relationship not found')
      }
      throw new Error('Failed to unlink student')
    }
  }

  /**
   * Get parent's children
   */
  async getParentChildren(parentId: string): Promise<Student[]> {
    const response = await fetch(`${API_BASE_URL}/parents/${parentId}/students`)

    if (!response.ok) {
      throw new Error('Failed to fetch parent children')
    }

    return response.json()
  }

  /**
   * Search parents
   */
  async searchParents(
    query: string,
    params: ParentSearchParams = {}
  ): Promise<ParentListResponse> {
    const searchParams = new URLSearchParams()
    searchParams.append('q', query)

    if (params.school_id) {
      searchParams.append('school_id', params.school_id)
    }

    if (params.page) {
      searchParams.append('page', params.page.toString())
    }

    if (params.limit) {
      searchParams.append('limit', params.limit.toString())
    }

    const response = await fetch(`${API_BASE_URL}/parents/search/query?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to search parents')
    }

    return response.json()
  }

  /**
   * Get student's parents
   */
  async getStudentParents(studentId: string): Promise<Parent[]> {
    const response = await fetch(`${API_BASE_URL}/parents/by-student/${studentId}`)

    if (!response.ok) {
      throw new Error('Failed to fetch student parents')
    }

    return response.json()
  }

  /**
   * Get parent statistics
   */
  async getStatistics(schoolId?: string): Promise<ParentStatistics> {
    const searchParams = new URLSearchParams()

    if (schoolId) {
      searchParams.append('school_id', schoolId)
    }

    const response = await fetch(`${API_BASE_URL}/parents/statistics/summary?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to fetch statistics')
    }

    return response.json()
  }
}

// Export singleton instance
export const parentService = new ParentService()
export default parentService
