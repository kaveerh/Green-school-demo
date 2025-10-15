/**
 * User Service
 * API client for user-related operations
 */
import type {
  User,
  UserCreateInput,
  UserUpdateInput,
  UserStatusChangeInput,
  UserPersonaChangeInput,
  UserSearchParams,
  PaginatedResponse,
  UserStatistics
} from '@/types/user'

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
 * User Service
 * Handles all user-related API operations
 */
class UserService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/users`
  }

  /**
   * Get list of users with optional filters
   */
  async getUsers(params?: UserSearchParams): Promise<PaginatedResponse<User>> {
    return this.client.get<PaginatedResponse<User>>(this.basePath, params)
  }

  /**
   * Get a single user by ID
   */
  async getUserById(id: string): Promise<User> {
    return this.client.get<User>(`${this.basePath}/${id}`)
  }

  /**
   * Create a new user
   */
  async createUser(userData: UserCreateInput): Promise<User> {
    return this.client.post<User>(this.basePath, userData)
  }

  /**
   * Update an existing user
   */
  async updateUser(id: string, userData: UserUpdateInput): Promise<User> {
    return this.client.put<User>(`${this.basePath}/${id}`, userData)
  }

  /**
   * Delete a user (soft delete)
   */
  async deleteUser(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Change user status (active, inactive, suspended)
   */
  async changeUserStatus(id: string, status: UserStatusChangeInput['status']): Promise<User> {
    return this.client.patch<User>(`${this.basePath}/${id}/status`, { status })
  }

  /**
   * Change user persona/role
   */
  async changeUserPersona(id: string, persona: UserPersonaChangeInput['persona']): Promise<User> {
    return this.client.patch<User>(`${this.basePath}/${id}/persona`, { persona })
  }

  /**
   * Get user statistics
   */
  async getStatistics(): Promise<UserStatistics> {
    return this.client.get<UserStatistics>(`${this.basePath}/statistics/summary`)
  }

  /**
   * Search users by query string
   */
  async searchUsers(query: string, params?: Omit<UserSearchParams, 'search'>): Promise<PaginatedResponse<User>> {
    return this.getUsers({ ...params, search: query })
  }

  /**
   * Get users by persona
   */
  async getUsersByPersona(persona: UserSearchParams['persona'], params?: Omit<UserSearchParams, 'persona'>): Promise<PaginatedResponse<User>> {
    return this.getUsers({ ...params, persona })
  }

  /**
   * Get users by status
   */
  async getUsersByStatus(status: UserSearchParams['status'], params?: Omit<UserSearchParams, 'status'>): Promise<PaginatedResponse<User>> {
    return this.getUsers({ ...params, status })
  }

  /**
   * Get active users only
   */
  async getActiveUsers(params?: UserSearchParams): Promise<PaginatedResponse<User>> {
    return this.getUsers({ ...params, status: 'active' })
  }
}

// Export singleton instance
export const userService = new UserService()

// Export class for testing
export { UserService }
