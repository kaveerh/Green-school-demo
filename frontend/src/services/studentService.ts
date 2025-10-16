/**
 * Student Service
 * API client for student-related operations
 */
import type {
  Student,
  StudentCreateInput,
  StudentUpdateInput,
  StudentStatusChangeInput,
  StudentSearchParams,
  StudentStatistics,
  ParentStudentRelationship,
  ParentStudentLinkInput,
  ParentStudentRelationshipListResponse
} from '@/types/student'
import type { PaginatedResponse } from '@/types/user'

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
 * Student Service
 * Handles all student-related API operations
 */
class StudentService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/students`
  }

  /**
   * Get list of students with optional filters
   */
  async getStudents(params?: StudentSearchParams): Promise<PaginatedResponse<Student>> {
    return this.client.get<PaginatedResponse<Student>>(this.basePath, params)
  }

  /**
   * Get a single student by ID
   */
  async getStudentById(id: string): Promise<Student> {
    return this.client.get<Student>(`${this.basePath}/${id}`)
  }

  /**
   * Get student by user ID
   */
  async getStudentByUserId(userId: string): Promise<Student> {
    return this.client.get<Student>(`${this.basePath}/user/${userId}`)
  }

  /**
   * Get student by student ID
   */
  async getStudentByStudentId(studentId: string): Promise<Student> {
    return this.client.get<Student>(`${this.basePath}/student-id/${studentId}`)
  }

  /**
   * Get enrolled students
   */
  async getEnrolledStudents(params?: { page?: number; limit?: number }): Promise<PaginatedResponse<Student>> {
    return this.client.get<PaginatedResponse<Student>>(`${this.basePath}/enrolled`, params)
  }

  /**
   * Get students by grade level
   */
  async getStudentsByGrade(grade: number, params?: { page?: number; limit?: number }): Promise<PaginatedResponse<Student>> {
    return this.client.get<PaginatedResponse<Student>>(`${this.basePath}/grade/${grade}`, params)
  }

  /**
   * Create a new student
   */
  async createStudent(studentData: StudentCreateInput): Promise<Student> {
    return this.client.post<Student>(this.basePath, studentData)
  }

  /**
   * Update an existing student
   */
  async updateStudent(id: string, studentData: StudentUpdateInput): Promise<Student> {
    return this.client.put<Student>(`${this.basePath}/${id}`, studentData)
  }

  /**
   * Delete a student (soft delete)
   */
  async deleteStudent(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Change student status
   */
  async changeStudentStatus(id: string, status: StudentStatusChangeInput['status']): Promise<Student> {
    return this.client.patch<Student>(`${this.basePath}/${id}/status`, { status })
  }

  /**
   * Promote student to next grade
   */
  async promoteStudent(id: string): Promise<Student> {
    return this.client.post<Student>(`${this.basePath}/${id}/promote`, {})
  }

  /**
   * Link parent to student
   */
  async linkParent(studentId: string, linkData: ParentStudentLinkInput): Promise<ParentStudentRelationship> {
    return this.client.post<ParentStudentRelationship>(`${this.basePath}/${studentId}/link-parent`, linkData)
  }

  /**
   * Unlink parent from student
   */
  async unlinkParent(studentId: string, parentId: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${studentId}/unlink-parent/${parentId}`)
  }

  /**
   * Get student's parents
   */
  async getStudentParents(studentId: string): Promise<ParentStudentRelationshipListResponse> {
    return this.client.get<ParentStudentRelationshipListResponse>(`${this.basePath}/${studentId}/parents`)
  }

  /**
   * Get student statistics
   */
  async getStatistics(): Promise<StudentStatistics> {
    return this.client.get<StudentStatistics>(`${this.basePath}/statistics/summary`)
  }

  /**
   * Search students by query string
   */
  async searchStudents(query: string, params?: Omit<StudentSearchParams, 'search'>): Promise<PaginatedResponse<Student>> {
    return this.getStudents({ ...params, search: query })
  }

  /**
   * Get students by status
   */
  async getStudentsByStatus(status: StudentSearchParams['status'], params?: Omit<StudentSearchParams, 'status'>): Promise<PaginatedResponse<Student>> {
    return this.getStudents({ ...params, status })
  }

  /**
   * Get students by gender
   */
  async getStudentsByGender(gender: StudentSearchParams['gender'], params?: Omit<StudentSearchParams, 'gender'>): Promise<PaginatedResponse<Student>> {
    return this.getStudents({ ...params, gender })
  }
}

// Export singleton instance
export const studentService = new StudentService()

// Export class for testing
export { StudentService }
