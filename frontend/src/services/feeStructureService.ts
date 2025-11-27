/**
 * Fee Structure Service
 * API client for fee structure (tuition pricing) operations
 */
import type {
  FeeStructure,
  FeeStructureCreateInput,
  FeeStructureUpdateInput,
  FeeStructureSearchParams,
  FeeStructureStatistics,
  FeeStructureListResponse
} from '@/types/feeStructure'

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

        // Handle FastAPI validation errors (array format)
        if (Array.isArray(errorData.detail)) {
          const errors = errorData.detail.map((err: any) => {
            const field = err.loc ? err.loc.join('.') : 'unknown'
            return `${field}: ${err.msg}`
          }).join('; ')
          errorMessage = errors || errorMessage
        }
        // Handle string detail
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        }
        // Handle message field
        else if (errorData.message) {
          errorMessage = errorData.message
        }
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
 * Fee Structure Service
 * Handles all fee structure-related API operations
 */
class FeeStructureService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/fee-structures`
  }

  /**
   * Get list of fee structures with optional filters
   */
  async getFeeStructures(params: FeeStructureSearchParams): Promise<FeeStructureListResponse> {
    return this.client.get<FeeStructureListResponse>(this.basePath, params)
  }

  /**
   * Get a single fee structure by ID
   */
  async getFeeStructureById(id: string): Promise<FeeStructure> {
    return this.client.get<FeeStructure>(`${this.basePath}/${id}`)
  }

  /**
   * Get fee structure by grade level and academic year
   */
  async getFeeStructureByGradeAndYear(
    schoolId: string,
    gradeLevel: number,
    academicYear: string
  ): Promise<FeeStructure> {
    return this.client.get<FeeStructure>(
      `${this.basePath}/grade/${gradeLevel}/year/${academicYear}`,
      { school_id: schoolId }
    )
  }

  /**
   * Create a new fee structure
   */
  async createFeeStructure(feeStructureData: FeeStructureCreateInput): Promise<FeeStructure> {
    return this.client.post<FeeStructure>(this.basePath, feeStructureData)
  }

  /**
   * Update an existing fee structure
   */
  async updateFeeStructure(id: string, feeStructureData: FeeStructureUpdateInput): Promise<FeeStructure> {
    return this.client.put<FeeStructure>(`${this.basePath}/${id}`, feeStructureData)
  }

  /**
   * Delete a fee structure (soft delete)
   */
  async deleteFeeStructure(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Get fee structure statistics
   */
  async getStatistics(schoolId: string, academicYear?: string): Promise<FeeStructureStatistics> {
    return this.client.get<FeeStructureStatistics>(
      `${this.basePath}/statistics/summary`,
      { school_id: schoolId, academic_year: academicYear }
    )
  }

  /**
   * Get fee structures by academic year
   */
  async getFeeStructuresByYear(
    schoolId: string,
    academicYear: string,
    params?: Omit<FeeStructureSearchParams, 'school_id' | 'academic_year'>
  ): Promise<FeeStructureListResponse> {
    return this.getFeeStructures({
      school_id: schoolId,
      academic_year: academicYear,
      ...params
    })
  }

  /**
   * Get fee structures by grade level
   */
  async getFeeStructuresByGrade(
    schoolId: string,
    gradeLevel: number,
    params?: Omit<FeeStructureSearchParams, 'school_id' | 'grade_level'>
  ): Promise<FeeStructureListResponse> {
    return this.getFeeStructures({
      school_id: schoolId,
      grade_level: gradeLevel,
      ...params
    })
  }

  /**
   * Get active fee structures
   */
  async getActiveFeeStructures(
    schoolId: string,
    params?: Omit<FeeStructureSearchParams, 'school_id' | 'is_active'>
  ): Promise<FeeStructureListResponse> {
    return this.getFeeStructures({
      school_id: schoolId,
      is_active: true,
      ...params
    })
  }

  /**
   * Get inactive fee structures
   */
  async getInactiveFeeStructures(
    schoolId: string,
    params?: Omit<FeeStructureSearchParams, 'school_id' | 'is_active'>
  ): Promise<FeeStructureListResponse> {
    return this.getFeeStructures({
      school_id: schoolId,
      is_active: false,
      ...params
    })
  }
}

// Export singleton instance
export const feeStructureService = new FeeStructureService()

// Export class for testing
export { FeeStructureService }
