/**
 * Payment Store
 * Pinia store for payment state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Payment,
  PaymentCreateInput,
  PaymentUpdateInput,
  PaymentPendingCreateInput,
  PaymentConfirmInput,
  PaymentRefundInput,
  PaymentSearchParams,
  PaymentReceipt,
  RevenueReport
} from '@/types/payment'

export const usePaymentStore = defineStore('payment', () => {
  // State
  const payments = ref<Payment[]>([])
  const selectedPayment = ref<Payment | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const currentReceipt = ref<PaymentReceipt | null>(null)
  const revenueReport = ref<RevenueReport | null>(null)

  // Getters
  const totalPayments = computed(() => pagination.value.total)
  const hasPayments = computed(() => payments.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const completedPayments = computed(() =>
    payments.value.filter(p => p.status === 'completed')
  )

  const pendingPayments = computed(() =>
    payments.value.filter(p => p.status === 'pending')
  )

  const refundedPayments = computed(() =>
    payments.value.filter(p => p.status === 'refunded')
  )

  const paymentsByMethod = computed(() => {
    return (method: string) => payments.value.filter(p => p.payment_method === method)
  })

  const paymentsByStatus = computed(() => {
    return (status: string) => payments.value.filter(p => p.status === status)
  })

  const totalRevenue = computed(() => {
    return completedPayments.value.reduce((sum, p) => sum + p.amount, 0)
  })

  // Actions
  async function fetchPayments(params: PaymentSearchParams) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const response = await paymentService.getPayments(params)

      payments.value = response.data
      pagination.value = {
        page: response.page,
        limit: response.limit,
        total: response.total,
        pages: response.pages
      }

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch payments'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPaymentById(id: string) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const payment = await paymentService.getPaymentById(id)

      selectedPayment.value = payment
      return payment
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPaymentByReceipt(receiptNumber: string) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const payment = await paymentService.getPaymentByReceipt(receiptNumber)

      selectedPayment.value = payment
      return payment
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch payment by receipt'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentPayments(studentId: string, params?: { page?: number; limit?: number }) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const response = await paymentService.getStudentPayments(studentId, params)

      payments.value = response.data
      pagination.value = {
        page: response.page,
        limit: response.limit,
        total: response.total,
        pages: response.pages
      }

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student payments'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPendingPayments(schoolId: string, params?: { page?: number; limit?: number }) {
    return fetchPayments({
      school_id: schoolId,
      payment_status: 'pending',
      ...params
    })
  }

  async function fetchPaymentsByDateRange(
    schoolId: string,
    startDate: string,
    endDate: string,
    params?: { page?: number; limit?: number }
  ) {
    return fetchPayments({
      school_id: schoolId,
      start_date: startDate,
      end_date: endDate,
      ...params
    })
  }

  async function fetchPaymentsByMethod(
    schoolId: string,
    paymentMethod: PaymentSearchParams['payment_method'],
    params?: { page?: number; limit?: number }
  ) {
    return fetchPayments({
      school_id: schoolId,
      payment_method: paymentMethod,
      ...params
    })
  }

  async function fetchReceiptData(paymentId: string) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const receipt = await paymentService.getReceiptData(paymentId)

      currentReceipt.value = receipt
      return receipt
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch receipt data'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRevenueReport(params: {
    school_id: string
    start_date?: string
    end_date?: string
    group_by?: 'day' | 'month' | 'year'
  }) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const report = await paymentService.getRevenueReport(params)

      revenueReport.value = report
      return report
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch revenue report'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createPayment(paymentData: PaymentCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const payment = await paymentService.createPayment(paymentData)

      // Add to local state
      payments.value.unshift(payment)
      pagination.value.total++

      return payment
    } catch (err: any) {
      error.value = err.message || 'Failed to create payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createPendingPayment(paymentData: PaymentPendingCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const payment = await paymentService.createPendingPayment(paymentData)

      // Add to local state
      payments.value.unshift(payment)
      pagination.value.total++

      return payment
    } catch (err: any) {
      error.value = err.message || 'Failed to create pending payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function confirmPayment(paymentId: string, confirmData?: PaymentConfirmInput) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const updatedPayment = await paymentService.confirmPayment(paymentId, confirmData)

      // Update in local state
      const index = payments.value.findIndex(p => p.id === paymentId)
      if (index !== -1) {
        payments.value[index] = updatedPayment
      }

      if (selectedPayment.value?.id === paymentId) {
        selectedPayment.value = updatedPayment
      }

      return updatedPayment
    } catch (err: any) {
      error.value = err.message || 'Failed to confirm payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function refundPayment(paymentId: string, refundData: PaymentRefundInput) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const updatedPayment = await paymentService.refundPayment(paymentId, refundData)

      // Update in local state
      const index = payments.value.findIndex(p => p.id === paymentId)
      if (index !== -1) {
        payments.value[index] = updatedPayment
      }

      if (selectedPayment.value?.id === paymentId) {
        selectedPayment.value = updatedPayment
      }

      return updatedPayment
    } catch (err: any) {
      error.value = err.message || 'Failed to refund payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updatePayment(id: string, paymentData: PaymentUpdateInput) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      const updatedPayment = await paymentService.updatePayment(id, paymentData)

      // Update in local state
      const index = payments.value.findIndex(p => p.id === id)
      if (index !== -1) {
        payments.value[index] = updatedPayment
      }

      if (selectedPayment.value?.id === id) {
        selectedPayment.value = updatedPayment
      }

      return updatedPayment
    } catch (err: any) {
      error.value = err.message || 'Failed to update payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deletePayment(id: string) {
    loading.value = true
    error.value = null

    try {
      const { paymentService } = await import('@/services/paymentService')
      await paymentService.deletePayment(id)

      // Remove from local state
      payments.value = payments.value.filter(p => p.id !== id)
      pagination.value.total--

      if (selectedPayment.value?.id === id) {
        selectedPayment.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedPayment(payment: Payment | null) {
    selectedPayment.value = payment
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    payments.value = []
    selectedPayment.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    }
    currentReceipt.value = null
    revenueReport.value = null
  }

  return {
    // State
    payments,
    selectedPayment,
    loading,
    error,
    pagination,
    currentReceipt,
    revenueReport,

    // Getters
    totalPayments,
    hasPayments,
    isLoading,
    hasError,
    completedPayments,
    pendingPayments,
    refundedPayments,
    paymentsByMethod,
    paymentsByStatus,
    totalRevenue,

    // Actions
    fetchPayments,
    fetchPaymentById,
    fetchPaymentByReceipt,
    fetchStudentPayments,
    fetchPendingPayments,
    fetchPaymentsByDateRange,
    fetchPaymentsByMethod,
    fetchReceiptData,
    fetchRevenueReport,
    createPayment,
    createPendingPayment,
    confirmPayment,
    refundPayment,
    updatePayment,
    deletePayment,
    setSelectedPayment,
    clearError,
    resetState
  }
})
