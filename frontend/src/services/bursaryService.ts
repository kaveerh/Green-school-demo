/**
 * Bursary Service
 * API client for bursary (financial aid) operations
 */
import type {
  Bursary,
  BursaryCreateInput,
  BursaryUpdateInput,
  BursarySearchParams,
  BursaryStatistics,
  BursaryListResponse
} from '@/types/bursary'

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
 * Bursary Service
 * Handles all bursary-related API operations
 */
class BursaryService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/bursaries`
  }

  /**
   * Get list of bursaries with optional filters
   */
  async getBursaries(params: BursarySearchParams): Promise<BursaryListResponse> {
    return this.client.get<BursaryListResponse>(this.basePath, params)
  }

  /**
   * Get a single bursary by ID
   */
  async getBursaryById(id: string): Promise<Bursary> {
    return this.client.get<Bursary>(`${this.basePath}/${id}`)
  }

  /**
   * Get active bursaries
   */
  async getActiveBursaries(
    schoolId: string,
    params?: Omit<BursarySearchParams, 'school_id' | 'is_active'>
  ): Promise<BursaryListResponse> {
    return this.getBursaries({
      school_id: schoolId,
      is_active: true,
      ...params
    })
  }

  /**
   * Get bursaries by type
   */
  async getBursariesByType(
    schoolId: string,
    bursaryType: BursarySearchParams['bursary_type'],
    params?: Omit<BursarySearchParams, 'school_id' | 'bursary_type'>
  ): Promise<BursaryListResponse> {
    return this.getBursaries({
      school_id: schoolId,
      bursary_type: bursaryType,
      ...params
    })
  }

  /**
   * Get bursaries by academic year
   */
  async getBursariesByYear(
    schoolId: string,
    academicYear: string,
    params?: Omit<BursarySearchParams, 'school_id' | 'academic_year'>
  ): Promise<BursaryListResponse> {
    return this.getBursaries({
      school_id: schoolId,
      academic_year: academicYear,
      ...params
    })
  }

  /**
   * Create a new bursary
   */
  async createBursary(bursaryData: BursaryCreateInput): Promise<Bursary> {
    return this.client.post<Bursary>(this.basePath, bursaryData)
  }

  /**
   * Update an existing bursary
   */
  async updateBursary(id: string, bursaryData: BursaryUpdateInput): Promise<Bursary> {
    return this.client.put<Bursary>(`${this.basePath}/${id}`, bursaryData)
  }

  /**
   * Delete a bursary (soft delete)
   */
  async deleteBursary(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Change bursary status
   */
  async changeBursaryStatus(id: string, status: BursarySearchParams['status']): Promise<Bursary> {
    return this.client.patch<Bursary>(`${this.basePath}/${id}/status`, { status })
  }

  /**
   * Increment recipients count
   */
  async incrementRecipients(id: string): Promise<Bursary> {
    return this.client.post<Bursary>(`${this.basePath}/${id}/increment-recipients`, {})
  }

  /**
   * Decrement recipients count
   */
  async decrementRecipients(id: string): Promise<Bursary> {
    return this.client.post<Bursary>(`${this.basePath}/${id}/decrement-recipients`, {})
  }

  /**
   * Get bursary statistics
   */
  async getStatistics(schoolId: string, academicYear?: string): Promise<BursaryStatistics> {
    return this.client.get<BursaryStatistics>(
      `${this.basePath}/statistics/summary`,
      { school_id: schoolId, academic_year: academicYear }
    )
  }

  /**
   * Get bursaries accepting applications
   */
  async getBursariesAcceptingApplications(
    schoolId: string,
    params?: Omit<BursarySearchParams, 'school_id' | 'status'>
  ): Promise<BursaryListResponse> {
    return this.getBursaries({
      school_id: schoolId,
      status: 'active',
      ...params
    })
  }

  /**
   * Get bursaries by status
   */
  async getBursariesByStatus(
    schoolId: string,
    status: BursarySearchParams['status'],
    params?: Omit<BursarySearchParams, 'school_id' | 'status'>
  ): Promise<BursaryListResponse> {
    return this.getBursaries({
      school_id: schoolId,
      status,
      ...params
    })
  }
}

// Export singleton instance
export const bursaryService = new BursaryService()

// Export class for testing
export { BursaryService }
