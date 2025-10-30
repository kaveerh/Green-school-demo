/**
 * Lesson Service
 *
 * API client for lesson planning and curriculum management
 */

import type {
  Lesson,
  LessonCreateRequest,
  LessonUpdateRequest,
  LessonCompleteRequest,
  LessonFromTemplateRequest,
  LessonDuplicateRequest,
  LessonListResponse,
  LessonStatistics,
  LessonFilters,
  LessonSearchParams,
  LessonDateRangeParams,
  LessonUpcomingParams,
  LessonTemplateParams,
  LessonStatisticsParams
} from '@/types/lesson'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class LessonService {
  private baseUrl = `${API_BASE_URL}/api/v1/lessons`

  /**
   * Create a new lesson
   */
  async createLesson(schoolId: string, data: LessonCreateRequest): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}?school_id=${schoolId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      let errorMessage = 'Failed to create lesson'
      try {
        const error = await response.json()
        // Handle different error formats
        if (typeof error.detail === 'string') {
          errorMessage = error.detail
        } else if (Array.isArray(error.detail)) {
          // Handle validation errors from FastAPI
          errorMessage = error.detail.map((e: any) =>
            `${e.loc?.join('.') || 'Field'}: ${e.msg}`
          ).join('; ')
        } else if (error.message) {
          errorMessage = error.message
        }
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = `HTTP ${response.status}: ${response.statusText}`
      }
      throw new Error(errorMessage)
    }

    return response.json()
  }

  /**
   * Create a lesson from a template
   */
  async createFromTemplate(
    schoolId: string,
    data: LessonFromTemplateRequest
  ): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/from-template?school_id=${schoolId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create lesson from template')
    }

    return response.json()
  }

  /**
   * Get lessons with filters and pagination
   */
  async getLessons(schoolId: string, filters?: LessonFilters): Promise<LessonListResponse> {
    const params = new URLSearchParams({ school_id: schoolId })

    if (filters) {
      if (filters.page) params.append('page', filters.page.toString())
      if (filters.limit) params.append('limit', filters.limit.toString())
      if (filters.class_id) params.append('class_id', filters.class_id)
      if (filters.teacher_id) params.append('teacher_id', filters.teacher_id)
      if (filters.subject_id) params.append('subject_id', filters.subject_id)
      if (filters.status) params.append('status', filters.status)
      if (filters.start_date) params.append('start_date', filters.start_date)
      if (filters.end_date) params.append('end_date', filters.end_date)
      if (filters.is_template !== undefined)
        params.append('is_template', filters.is_template.toString())
    }

    const response = await fetch(`${this.baseUrl}?${params}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch lessons')
    }

    return response.json()
  }

  /**
   * Get lessons by date range (for calendar view)
   */
  async getLessonsByDateRange(
    schoolId: string,
    params: LessonDateRangeParams
  ): Promise<Lesson[]> {
    const searchParams = new URLSearchParams({
      school_id: schoolId,
      start_date: params.start_date,
      end_date: params.end_date
    })

    if (params.teacher_id) searchParams.append('teacher_id', params.teacher_id)
    if (params.class_id) searchParams.append('class_id', params.class_id)
    if (params.subject_id) searchParams.append('subject_id', params.subject_id)

    const response = await fetch(`${this.baseUrl}/by-date-range?${searchParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch lessons by date range')
    }

    return response.json()
  }

  /**
   * Get upcoming lessons
   */
  async getUpcomingLessons(
    schoolId: string,
    params?: LessonUpcomingParams
  ): Promise<Lesson[]> {
    const searchParams = new URLSearchParams({ school_id: schoolId })

    if (params?.teacher_id) searchParams.append('teacher_id', params.teacher_id)
    if (params?.days) searchParams.append('days', params.days.toString())
    if (params?.limit) searchParams.append('limit', params.limit.toString())

    const response = await fetch(`${this.baseUrl}/upcoming?${searchParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch upcoming lessons')
    }

    return response.json()
  }

  /**
   * Get past due lessons
   */
  async getPastDueLessons(schoolId: string, teacherId?: string, limit = 50): Promise<Lesson[]> {
    const params = new URLSearchParams({ school_id: schoolId, limit: limit.toString() })

    if (teacherId) params.append('teacher_id', teacherId)

    const response = await fetch(`${this.baseUrl}/past-due?${params}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch past due lessons')
    }

    return response.json()
  }

  /**
   * Search lessons
   */
  async searchLessons(schoolId: string, params: LessonSearchParams): Promise<Lesson[]> {
    const searchParams = new URLSearchParams({
      school_id: schoolId,
      query: params.query
    })

    if (params.teacher_id) searchParams.append('teacher_id', params.teacher_id)
    if (params.subject_id) searchParams.append('subject_id', params.subject_id)
    if (params.limit) searchParams.append('limit', params.limit.toString())

    const response = await fetch(`${this.baseUrl}/search?${searchParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to search lessons')
    }

    return response.json()
  }

  /**
   * Get lesson templates
   */
  async getTemplates(schoolId: string, params?: LessonTemplateParams): Promise<Lesson[]> {
    const searchParams = new URLSearchParams({ school_id: schoolId })

    if (params?.teacher_id) searchParams.append('teacher_id', params.teacher_id)
    if (params?.subject_id) searchParams.append('subject_id', params.subject_id)

    const response = await fetch(`${this.baseUrl}/templates?${searchParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch templates')
    }

    return response.json()
  }

  /**
   * Get lesson statistics
   */
  async getStatistics(
    schoolId: string,
    params?: LessonStatisticsParams
  ): Promise<LessonStatistics> {
    const searchParams = new URLSearchParams({ school_id: schoolId })

    if (params?.teacher_id) searchParams.append('teacher_id', params.teacher_id)
    if (params?.start_date) searchParams.append('start_date', params.start_date)
    if (params?.end_date) searchParams.append('end_date', params.end_date)

    const response = await fetch(`${this.baseUrl}/statistics?${searchParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch statistics')
    }

    return response.json()
  }

  /**
   * Get lesson by ID
   */
  async getLessonById(id: string): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch lesson')
    }

    return response.json()
  }

  /**
   * Update lesson
   */
  async updateLesson(id: string, data: LessonUpdateRequest): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update lesson')
    }

    return response.json()
  }

  /**
   * Update lesson status
   */
  async updateStatus(id: string, status: string): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update status')
    }

    return response.json()
  }

  /**
   * Start lesson
   */
  async startLesson(id: string): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/start`, {
      method: 'POST'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to start lesson')
    }

    return response.json()
  }

  /**
   * Complete lesson
   */
  async completeLesson(id: string, data: LessonCompleteRequest): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/complete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to complete lesson')
    }

    return response.json()
  }

  /**
   * Cancel lesson
   */
  async cancelLesson(id: string): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/cancel`, {
      method: 'POST'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to cancel lesson')
    }

    return response.json()
  }

  /**
   * Convert lesson to template
   */
  async convertToTemplate(id: string): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/convert-to-template`, {
      method: 'POST'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to convert to template')
    }

    return response.json()
  }

  /**
   * Duplicate lesson
   */
  async duplicateLesson(id: string, data: LessonDuplicateRequest): Promise<Lesson> {
    const response = await fetch(`${this.baseUrl}/${id}/duplicate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to duplicate lesson')
    }

    return response.json()
  }

  /**
   * Delete lesson
   */
  async deleteLesson(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete lesson')
    }
  }
}

export const lessonService = new LessonService()
export default lessonService
