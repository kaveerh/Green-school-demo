/**
 * Subject Service
 *
 * API client for Subject operations.
 */

import type {
  Subject,
  SubjectCreateInput,
  SubjectUpdateInput,
  SubjectListResponse,
  SubjectSearchParams,
  SubjectStatistics
} from '@/types/subject'

const API_BASE_URL = 'http://localhost:8000/api/v1'

class SubjectService {
  /**
   * Create a new subject
   */
  async createSubject(subjectData: SubjectCreateInput): Promise<Subject> {
    const response = await fetch(`${API_BASE_URL}/subjects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subjectData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create subject')
    }

    return response.json()
  }

  /**
   * Get all subjects with pagination and filters
   */
  async getSubjects(params: SubjectSearchParams = {}): Promise<SubjectListResponse> {
    const searchParams = new URLSearchParams()

    if (params.school_id) {
      searchParams.append('school_id', params.school_id)
    }

    if (params.category) {
      searchParams.append('category', params.category)
    }

    if (params.subject_type) {
      searchParams.append('subject_type', params.subject_type)
    }

    if (params.is_active !== undefined) {
      searchParams.append('is_active', params.is_active.toString())
    }

    if (params.is_required !== undefined) {
      searchParams.append('is_required', params.is_required.toString())
    }

    if (params.page) {
      searchParams.append('page', params.page.toString())
    }

    if (params.limit) {
      searchParams.append('limit', params.limit.toString())
    }

    const response = await fetch(`${API_BASE_URL}/subjects?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to fetch subjects')
    }

    return response.json()
  }

  /**
   * Get subject by ID
   */
  async getSubjectById(id: string): Promise<Subject> {
    const response = await fetch(`${API_BASE_URL}/subjects/${id}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Subject not found')
      }
      throw new Error('Failed to fetch subject')
    }

    return response.json()
  }

  /**
   * Get subject by code
   */
  async getSubjectByCode(code: string, schoolId: string): Promise<Subject> {
    const response = await fetch(
      `${API_BASE_URL}/subjects/code/${code}?school_id=${schoolId}`
    )

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Subject not found')
      }
      throw new Error('Failed to fetch subject')
    }

    return response.json()
  }

  /**
   * Update subject
   */
  async updateSubject(id: string, subjectData: SubjectUpdateInput): Promise<Subject> {
    const response = await fetch(`${API_BASE_URL}/subjects/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(subjectData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update subject')
    }

    return response.json()
  }

  /**
   * Delete subject
   */
  async deleteSubject(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/subjects/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Subject not found')
      }
      throw new Error('Failed to delete subject')
    }
  }

  /**
   * Toggle subject status
   */
  async toggleStatus(id: string): Promise<Subject> {
    const response = await fetch(`${API_BASE_URL}/subjects/${id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to toggle status')
    }

    return response.json()
  }

  /**
   * Get subjects by category
   */
  async getSubjectsByCategory(category: string, schoolId: string): Promise<Subject[]> {
    const response = await fetch(
      `${API_BASE_URL}/subjects/category/${category}?school_id=${schoolId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch subjects by category')
    }

    return response.json()
  }

  /**
   * Get subjects by grade level
   */
  async getSubjectsByGrade(grade: number, schoolId: string): Promise<Subject[]> {
    const response = await fetch(
      `${API_BASE_URL}/subjects/grade/${grade}?school_id=${schoolId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch subjects by grade')
    }

    return response.json()
  }

  /**
   * Search subjects
   */
  async searchSubjects(
    query: string,
    params: SubjectSearchParams = {}
  ): Promise<SubjectListResponse> {
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

    const response = await fetch(`${API_BASE_URL}/subjects/search/query?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to search subjects')
    }

    return response.json()
  }

  /**
   * Get subject statistics
   */
  async getStatistics(schoolId?: string): Promise<SubjectStatistics> {
    const searchParams = new URLSearchParams()

    if (schoolId) {
      searchParams.append('school_id', schoolId)
    }

    const response = await fetch(
      `${API_BASE_URL}/subjects/statistics/summary?${searchParams}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch statistics')
    }

    return response.json()
  }
}

// Export singleton instance
export const subjectService = new SubjectService()
export default subjectService
