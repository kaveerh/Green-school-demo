/**
 * Payment Service
 * API client for payment-related operations
 */
import type {
  Payment,
  PaymentCreateInput,
  PaymentUpdateInput,
  PaymentPendingCreateInput,
  PaymentConfirmInput,
  PaymentRefundInput,
  PaymentSearchParams,
  PaymentReceipt,
  RevenueReport,
  PaymentListResponse
} from '@/types/payment'

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
 * Payment Service
 * Handles all payment-related API operations
 */
class PaymentService {
  private client: ApiClient
  private basePath: string

  constructor() {
    this.client = new ApiClient(API_BASE_URL)
    this.basePath = `/payments`
  }

  /**
   * Get list of payments with optional filters
   */
  async getPayments(params: PaymentSearchParams): Promise<PaymentListResponse> {
    return this.client.get<PaymentListResponse>(this.basePath, params)
  }

  /**
   * Get a single payment by ID
   */
  async getPaymentById(id: string): Promise<Payment> {
    return this.client.get<Payment>(`${this.basePath}/${id}`)
  }

  /**
   * Get payment by receipt number
   */
  async getPaymentByReceipt(receiptNumber: string): Promise<Payment> {
    return this.client.get<Payment>(`${this.basePath}/receipt/${receiptNumber}`)
  }

  /**
   * Get payments for a student
   */
  async getStudentPayments(studentId: string, params?: Omit<PaymentSearchParams, 'school_id'>): Promise<PaymentListResponse> {
    return this.client.get<PaymentListResponse>(`${this.basePath}/student/${studentId}`, params)
  }

  /**
   * Get receipt data for printing/PDF
   */
  async getReceiptData(paymentId: string): Promise<PaymentReceipt> {
    return this.client.get<PaymentReceipt>(`${this.basePath}/${paymentId}/receipt-data`)
  }

  /**
   * Get revenue report with analytics
   */
  async getRevenueReport(params: {
    school_id: string
    start_date?: string
    end_date?: string
    group_by?: 'day' | 'month' | 'year'
  }): Promise<RevenueReport> {
    return this.client.get<RevenueReport>(`${this.basePath}/reports/revenue`, params)
  }

  /**
   * Create a new completed payment
   */
  async createPayment(paymentData: PaymentCreateInput): Promise<Payment> {
    return this.client.post<Payment>(this.basePath, paymentData)
  }

  /**
   * Create a pending payment (for checks, authorization holds)
   */
  async createPendingPayment(paymentData: PaymentPendingCreateInput): Promise<Payment> {
    return this.client.post<Payment>(`${this.basePath}/pending`, paymentData)
  }

  /**
   * Confirm a pending payment
   */
  async confirmPayment(paymentId: string, confirmData?: PaymentConfirmInput): Promise<Payment> {
    return this.client.post<Payment>(`${this.basePath}/${paymentId}/confirm`, confirmData || {})
  }

  /**
   * Process a payment refund
   */
  async refundPayment(paymentId: string, refundData: PaymentRefundInput): Promise<Payment> {
    return this.client.post<Payment>(`${this.basePath}/${paymentId}/refund`, refundData)
  }

  /**
   * Update payment details
   */
  async updatePayment(id: string, paymentData: PaymentUpdateInput): Promise<Payment> {
    return this.client.put<Payment>(`${this.basePath}/${id}`, paymentData)
  }

  /**
   * Delete a payment (soft delete - pending payments only)
   */
  async deletePayment(id: string): Promise<void> {
    return this.client.delete<void>(`${this.basePath}/${id}`)
  }

  /**
   * Get pending payments
   */
  async getPendingPayments(schoolId: string, params?: { page?: number; limit?: number }): Promise<PaymentListResponse> {
    return this.getPayments({
      school_id: schoolId,
      payment_status: 'pending',
      ...params
    })
  }

  /**
   * Get payments by date range
   */
  async getPaymentsByDateRange(
    schoolId: string,
    startDate: string,
    endDate: string,
    params?: Omit<PaymentSearchParams, 'school_id' | 'start_date' | 'end_date'>
  ): Promise<PaymentListResponse> {
    return this.getPayments({
      school_id: schoolId,
      start_date: startDate,
      end_date: endDate,
      ...params
    })
  }

  /**
   * Get payments by method
   */
  async getPaymentsByMethod(
    schoolId: string,
    paymentMethod: PaymentSearchParams['payment_method'],
    params?: Omit<PaymentSearchParams, 'school_id' | 'payment_method'>
  ): Promise<PaymentListResponse> {
    return this.getPayments({
      school_id: schoolId,
      payment_method: paymentMethod,
      ...params
    })
  }

  /**
   * Get payments by status
   */
  async getPaymentsByStatus(
    schoolId: string,
    status: PaymentSearchParams['payment_status'],
    params?: Omit<PaymentSearchParams, 'school_id' | 'payment_status'>
  ): Promise<PaymentListResponse> {
    return this.getPayments({
      school_id: schoolId,
      payment_status: status,
      ...params
    })
  }
}

// Export singleton instance
export const paymentService = new PaymentService()

// Export class for testing
export { PaymentService }
