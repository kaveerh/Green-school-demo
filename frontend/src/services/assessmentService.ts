/**
 * Assessment Service
 *
 * API client for student assessments, grading, and evaluation
 */

import type {
  Assessment,
  AssessmentCreateRequest,
  AssessmentUpdateRequest,
  AssessmentGradeRequest,
  AssessmentListResponse,
  AssessmentStatistics,
  AssessmentFilters,
  StudentAssessmentParams,
  ClassAssessmentParams,
  TeacherAssessmentParams,
  AssessmentStatisticsParams
} from '@/types/assessment'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class AssessmentService {
  private baseUrl = `${API_BASE_URL}/api/v1/assessments`

  /**
   * Create a new assessment
   */
  async createAssessment(data: AssessmentCreateRequest): Promise<Assessment> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create assessment')
    }

    return response.json()
  }

  /**
   * Get assessment by ID
   */
  async getAssessmentById(id: string): Promise<Assessment> {
    const response = await fetch(`${this.baseUrl}/${id}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch assessment')
    }

    return response.json()
  }

  /**
   * Update an assessment
   */
  async updateAssessment(id: string, data: AssessmentUpdateRequest): Promise<Assessment> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update assessment')
    }

    return response.json()
  }

  /**
   * Grade an assessment
   */
  async gradeAssessment(id: string, data: AssessmentGradeRequest): Promise<Assessment> {
    const response = await fetch(`${this.baseUrl}/${id}/grade`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to grade assessment')
    }

    return response.json()
  }

  /**
   * Delete an assessment
   */
  async deleteAssessment(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete assessment')
    }
  }

  /**
   * Get assessments for a student
   */
  async getStudentAssessments(params: StudentAssessmentParams): Promise<AssessmentListResponse> {
    const { student_id, ...filters } = params
    const queryParams = new URLSearchParams()

    if (filters.page) queryParams.append('page', filters.page.toString())
    if (filters.limit) queryParams.append('limit', filters.limit.toString())
    if (filters.quarter) queryParams.append('quarter', filters.quarter)
    if (filters.subject_id) queryParams.append('subject_id', filters.subject_id)

    const response = await fetch(`${this.baseUrl}/student/${student_id}?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch student assessments')
    }

    return response.json()
  }

  /**
   * Get assessments for a class
   */
  async getClassAssessments(params: ClassAssessmentParams): Promise<AssessmentListResponse> {
    const { class_id, ...filters } = params
    const queryParams = new URLSearchParams()

    if (filters.page) queryParams.append('page', filters.page.toString())
    if (filters.limit) queryParams.append('limit', filters.limit.toString())
    if (filters.quarter) queryParams.append('quarter', filters.quarter)
    if (filters.assessment_type) queryParams.append('assessment_type', filters.assessment_type)

    const response = await fetch(`${this.baseUrl}/class/${class_id}?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch class assessments')
    }

    return response.json()
  }

  /**
   * Get assessments for a teacher
   */
  async getTeacherAssessments(params: TeacherAssessmentParams): Promise<AssessmentListResponse> {
    const { teacher_id, ...filters } = params
    const queryParams = new URLSearchParams()

    if (filters.page) queryParams.append('page', filters.page.toString())
    if (filters.limit) queryParams.append('limit', filters.limit.toString())
    if (filters.quarter) queryParams.append('quarter', filters.quarter)
    if (filters.status) queryParams.append('status', filters.status)

    const response = await fetch(`${this.baseUrl}/teacher/${teacher_id}?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch teacher assessments')
    }

    return response.json()
  }

  /**
   * Get assessment statistics
   */
  async getStatistics(params: AssessmentStatisticsParams): Promise<AssessmentStatistics> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)
    if (params.quarter) queryParams.append('quarter', params.quarter)

    const response = await fetch(`${this.baseUrl}/statistics/summary?${queryParams}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch statistics')
    }

    return response.json()
  }
}

export const assessmentService = new AssessmentService()
