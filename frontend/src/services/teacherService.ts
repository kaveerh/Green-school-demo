/**
 * Teacher Service
 * API client for teacher-related operations
 */
import type {
  Teacher,
  TeacherCreateInput,
  TeacherUpdateInput,
  TeacherStatusChangeInput,
  TeacherSearchParams,
  PaginatedResponse,
  TeacherStatistics,
  TeacherWithDetails
} from '@/types'

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

/**
 * HTTP Client wrapper with error handling
 */
class ApiClient {
  private baseURL: string
  private defaultHeaders: Record<string, string>

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    }
  }

  /**
   * Get authorization token from storage
   */
  private getAuthToken(): string | null {
    // TODO: Replace with actual token retrieval from auth store
    return localStorage.getItem('auth_token')
  }

  /**
   * Build headers with authorization
   */
  private getHeaders(): Record<string, string> {
    const headers = { ...this.defaultHeaders }
    const token = this.getAuthToken()

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    return headers
  }

  /**
   * Handle API errors
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`

      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // If response is not JSON, use default error message
      }

      throw new Error(errorMessage)
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null as T
    }

    return response.json()
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`)

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.getHeaders(),
    })

    return this.handleResponse<T>(response)
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })

    return this.handleResponse<T>(response)
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })

    return this.handleResponse<T>(response)
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    })

    return this.handleResponse<T>(response)
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    })

    return this.handleResponse<T>(response)
  }
}

/**
 * Teacher Service
 * Handles all teacher-related API operations
 */
class TeacherService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/teachers`
  }

  /**
   * Get list of teachers with optional filters
   */
  async getTeachers(params?: TeacherSearchParams): Promise<PaginatedResponse<Teacher>> {
    return this.client.get<PaginatedResponse<Teacher>>(this.basePath, params)
  }

  /**
   * Get a single teacher by ID
   */
  async getTeacherById(id: string): Promise<Teacher> {
    return this.client.get<Teacher>(`${this.basePath}/${id}`)
  }

  /**
   * Get teacher by user ID
   */
  async getTeacherByUserId(userId: string): Promise<Teacher> {
    return this.client.get<Teacher>(`${this.basePath}/user/${userId}`)
  }

  /**
   * Get teacher by employee ID
   */
  async getTeacherByEmployeeId(employeeId: string): Promise<Teacher> {
    return this.client.get<Teacher>(`${this.basePath}/employee/${employeeId}`)
  }

  /**
   * Get all active teachers
   */
  async getActiveTeachers(page: number = 1, limit: number = 20): Promise<PaginatedResponse<Teacher>> {
    return this.client.get<PaginatedResponse<Teacher>>(`${this.basePath}/active`, { page, limit })
  }

  /**
   * Get teachers by grade level
   */
  async getTeachersByGrade(grade: number): Promise<Teacher[]> {
    return this.client.get<Teacher[]>(`${this.basePath}/grade/${grade}`)
  }

  /**
   * Get teachers by specialization
   */
  async getTeachersBySpecialization(specialization: string): Promise<Teacher[]> {
    return this.client.get<Teacher[]>(`${this.basePath}/specialization/${specialization}`)
  }

  /**
   * Create a new teacher
   */
  async createTeacher(teacherData: TeacherCreateInput): Promise<Teacher> {
    return this.client.post<Teacher>(this.basePath, teacherData)
  }

  /**
   * Update an existing teacher
   */
  async updateTeacher(id: string, teacherData: TeacherUpdateInput): Promise<Teacher> {
    return this.client.put<Teacher>(`${this.basePath}/${id}`, teacherData)
  }

  /**
   * Delete a teacher (soft delete)
   */
  async deleteTeacher(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Change teacher status (active, inactive, on_leave, terminated)
   */
  async changeTeacherStatus(id: string, status: TeacherStatusChangeInput['status']): Promise<Teacher> {
    return this.client.patch<Teacher>(`${this.basePath}/${id}/status`, { status })
  }

  /**
   * Assign grade levels to teacher
   */
  async assignGrades(id: string, gradeLevels: number[]): Promise<Teacher> {
    return this.client.patch<Teacher>(`${this.basePath}/${id}/grades`, { grade_levels: gradeLevels })
  }

  /**
   * Assign specializations to teacher
   */
  async assignSpecializations(id: string, specializations: string[]): Promise<Teacher> {
    return this.client.patch<Teacher>(`${this.basePath}/${id}/specializations`, { specializations })
  }

  /**
   * Get teacher statistics
   */
  async getStatistics(): Promise<TeacherStatistics> {
    return this.client.get<TeacherStatistics>(`${this.basePath}/statistics/summary`)
  }

  /**
   * Search teachers by query string
   */
  async searchTeachers(query: string, params?: Omit<TeacherSearchParams, 'search'>): Promise<PaginatedResponse<Teacher>> {
    return this.getTeachers({ ...params, search: query })
  }

  /**
   * Get teachers by status
   */
  async getTeachersByStatus(status: TeacherSearchParams['status'], params?: Omit<TeacherSearchParams, 'status'>): Promise<PaginatedResponse<Teacher>> {
    return this.getTeachers({ ...params, status })
  }

  /**
   * Get teachers by employment type
   */
  async getTeachersByEmploymentType(employmentType: TeacherSearchParams['employment_type'], params?: Omit<TeacherSearchParams, 'employment_type'>): Promise<PaginatedResponse<Teacher>> {
    return this.getTeachers({ ...params, employment_type: employmentType })
  }

  /**
   * Get teachers by department
   */
  async getTeachersByDepartment(department: string, params?: Omit<TeacherSearchParams, 'department'>): Promise<PaginatedResponse<Teacher>> {
    return this.getTeachers({ ...params, department })
  }

  /**
   * Get teachers with expiring certifications
   */
  async getTeachersWithExpiringCertifications(params?: Omit<TeacherSearchParams, 'certification_expiring'>): Promise<PaginatedResponse<Teacher>> {
    return this.getTeachers({ ...params, certification_expiring: true })
  }
}

// Export singleton instance
export const teacherService = new TeacherService()

// Export class for testing
export { TeacherService }
