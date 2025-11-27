<template>
  <div class="payments-list">
    <div class="page-header">
      <h1>Payment Management</h1>
      <div class="header-actions">
        <router-link to="/payments/pending" class="btn btn-secondary">
          View Pending ({{ pendingCount }})
        </router-link>
        <router-link to="/payments/create" class="btn btn-primary">
          Record Payment
        </router-link>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-revenue">
        <div class="stat-label">Total Revenue</div>
        <div class="stat-value">R {{ formatCurrency(totalRevenue) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Payments</div>
        <div class="stat-value">{{ totalPayments }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Completed</div>
        <div class="stat-value">{{ completedPayments.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Pending</div>
        <div class="stat-value">{{ pendingCount }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Payment Status</label>
        <select v-model="filters.payment_status">
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="refunded">Refunded</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Payment Method</label>
        <select v-model="filters.payment_method">
          <option value="">All Methods</option>
          <option value="cash">Cash</option>
          <option value="card">Card</option>
          <option value="bank_transfer">Bank Transfer</option>
          <option value="check">Check</option>
          <option value="online">Online</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Start Date</label>
        <input type="date" v-model="filters.start_date" />
      </div>

      <div class="filter-group">
        <label>End Date</label>
        <input type="date" v-model="filters.end_date" />
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">
          Apply Filters
        </button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading payments...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Payments Table -->
    <div v-if="!loading && payments.length > 0" class="payments-table-container">
      <table class="payments-table">
        <thead>
          <tr>
            <th>Receipt #</th>
            <th>Date</th>
            <th>Student</th>
            <th>Amount</th>
            <th>Method</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="payment in payments" :key="payment.id" :class="getRowClass(payment)">
            <td>
              <span class="receipt-number">{{ payment.receipt_number }}</span>
            </td>
            <td>
              <div class="date-cell">{{ formatDate(payment.payment_date) }}</div>
            </td>
            <td>
              <div v-if="payment.student" class="student-info">
                <div class="student-name">{{ payment.student.name }}</div>
                <div class="student-id">{{ payment.student.student_id }}</div>
              </div>
              <span v-else>—</span>
            </td>
            <td>
              <div class="amount-cell">R {{ formatCurrency(payment.amount) }}</div>
            </td>
            <td>
              <span
                class="method-badge"
                :class="`method-${payment.payment_method}`"
              >
                {{ getPaymentMethodLabel(payment.payment_method) }}
              </span>
            </td>
            <td>
              <span
                class="status-badge"
                :class="`status-${payment.status}`"
              >
                {{ getStatusLabel(payment.status) }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <router-link
                  :to="`/payments/${payment.id}/receipt`"
                  class="btn btn-sm btn-secondary"
                  v-if="payment.status === 'completed'"
                  title="View Receipt"
                >
                  Receipt
                </router-link>
                <button
                  @click="handleConfirm(payment)"
                  class="btn btn-sm btn-success"
                  v-if="payment.status === 'pending'"
                  title="Confirm Payment"
                >
                  Confirm
                </button>
                <button
                  @click="handleRefund(payment)"
                  class="btn btn-sm btn-warning"
                  v-if="payment.status === 'completed' && !payment.is_refunded"
                  title="Refund Payment"
                >
                  Refund
                </button>
                <router-link
                  :to="`/payments/${payment.id}`"
                  class="btn btn-sm btn-link"
                >
                  View
                </router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && payments.length === 0" class="empty-state">
      <p>No payments found.</p>
      <router-link to="/payments/create" class="btn btn-primary">
        Record First Payment
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="pagination">
      <button
        @click="goToPage(page - 1)"
        :disabled="page === 1"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ page }} of {{ pages }} ({{ total }} total)
      </span>
      <button
        @click="goToPage(page + 1)"
        :disabled="page === pages"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>

    <!-- Refund Modal -->
    <div v-if="showRefundModal" class="modal-overlay" @click="closeRefundModal">
      <div class="modal-content" @click.stop>
        <h2>Refund Payment</h2>
        <p>Refunding payment {{ refundingPayment?.receipt_number }} for R {{ formatCurrency(refundingPayment?.amount || 0) }}</p>

        <div class="form-group">
          <label>Refund Reason *</label>
          <textarea
            v-model="refundReason"
            placeholder="Enter reason for refund..."
            rows="4"
            required
          ></textarea>
        </div>

        <div class="modal-actions">
          <button @click="closeRefundModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmRefund" class="btn btn-danger" :disabled="!refundReason">
            Confirm Refund
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePaymentStore } from '@/stores/paymentStore'
import { useSchool } from '@/composables/useSchool'
import { useRouter } from 'vue-router'
import type { Payment, PaymentMethod, PaymentStatus } from '@/types/payment'

const paymentStore = usePaymentStore()
const router = useRouter()
const { currentSchoolId } = useSchool()

// State
const filters = ref({
  payment_status: '' as PaymentStatus | '',
  payment_method: '' as PaymentMethod | '',
  start_date: '',
  end_date: ''
})

const showRefundModal = ref(false)
const refundingPayment = ref<Payment | null>(null)
const refundReason = ref('')

// Computed
const payments = computed(() => paymentStore.payments)
const loading = computed(() => paymentStore.loading)
const error = computed(() => paymentStore.error)
const total = computed(() => paymentStore.pagination.total)
const page = computed(() => paymentStore.pagination.page)
const pages = computed(() => paymentStore.pagination.pages)
const completedPayments = computed(() => paymentStore.completedPayments)
const pendingPayments = computed(() => paymentStore.pendingPayments)
const pendingCount = computed(() => pendingPayments.value.length)
const totalRevenue = computed(() => paymentStore.totalRevenue)
const totalPayments = computed(() => total.value)

// Methods
async function loadPayments() {
  if (!currentSchoolId.value) {
    console.warn('Cannot load payments: no school selected')
    return
  }

  const params: any = {
    school_id: currentSchoolId.value,
    page: page.value,
    limit: 50
  }

  if (filters.value.payment_status) params.payment_status = filters.value.payment_status
  if (filters.value.payment_method) params.payment_method = filters.value.payment_method
  if (filters.value.start_date) params.start_date = filters.value.start_date
  if (filters.value.end_date) params.end_date = filters.value.end_date

  try {
    await paymentStore.fetchPayments(params)
  } catch (err) {
    console.error('Failed to load payments:', err)
  }
}

function applyFilters() {
  paymentStore.pagination.page = 1
  loadPayments()
}

function clearFilters() {
  filters.value = {
    payment_status: '',
    payment_method: '',
    start_date: '',
    end_date: ''
  }
  applyFilters()
}

function goToPage(newPage: number) {
  paymentStore.pagination.page = newPage
  loadPayments()
}

async function handleConfirm(payment: Payment) {
  if (!confirm(`Are you sure you want to confirm this payment?`)) {
    return
  }

  try {
    await paymentStore.confirmPayment(payment.id)
    loadPayments() // Reload to reflect changes
  } catch (err) {
    console.error('Failed to confirm payment:', err)
    alert('Failed to confirm payment. Please try again.')
  }
}

function handleRefund(payment: Payment) {
  refundingPayment.value = payment
  refundReason.value = ''
  showRefundModal.value = true
}

async function confirmRefund() {
  if (!refundingPayment.value || !refundReason.value) {
    return
  }

  try {
    await paymentStore.refundPayment(refundingPayment.value.id, {
      refund_reason: refundReason.value
    })
    closeRefundModal()
    loadPayments() // Reload to reflect changes
  } catch (err) {
    console.error('Failed to refund payment:', err)
    alert('Failed to refund payment. Please try again.')
  }
}

function closeRefundModal() {
  showRefundModal.value = false
  refundingPayment.value = null
  refundReason.value = ''
}

function getRowClass(payment: Payment) {
  if (payment.status === 'refunded') return 'row-refunded'
  if (payment.status === 'pending') return 'row-pending'
  if (payment.status === 'failed') return 'row-failed'
  return ''
}

function formatCurrency(amount: number): string {
  return amount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-ZA', { year: 'numeric', month: 'short', day: 'numeric' })
}

function getPaymentMethodLabel(method: PaymentMethod): string {
  const labels: Record<PaymentMethod, string> = {
    cash: 'Cash',
    card: 'Card',
    bank_transfer: 'Bank Transfer',
    check: 'Check',
    online: 'Online',
    other: 'Other'
  }
  return labels[method] || method
}

function getStatusLabel(status: PaymentStatus): string {
  const labels: Record<PaymentStatus, string> = {
    completed: 'Completed',
    pending: 'Pending',
    refunded: 'Refunded',
    failed: 'Failed',
    cancelled: 'Cancelled'
  }
  return labels[status] || status
}

// Lifecycle
onMounted(() => {
  loadPayments()
})
</script>

<style scoped>
.payments-list {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card.stat-revenue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.stat-revenue .stat-label,
.stat-card.stat-revenue .stat-value {
  color: white;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
}

.filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
}

.loading,
.error-message {
  padding: 2rem;
  text-align: center;
}

.error-message {
  color: #dc2626;
  background: #fee2e2;
  border-radius: 8px;
}

.payments-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th,
.payments-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.payments-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.payments-table tbody tr:hover {
  background: #f9fafb;
}

.row-refunded {
  background: #fef3c7;
}

.row-pending {
  background: #dbeafe;
}

.row-failed {
  background: #fee2e2;
}

.receipt-number {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #6366f1;
}

.student-info {
  display: flex;
  flex-direction: column;
}

.student-name {
  font-weight: 500;
  color: #111827;
}

.student-id {
  font-size: 0.75rem;
  color: #6b7280;
}

.amount-cell {
  font-weight: 600;
  color: #059669;
  font-size: 1.125rem;
}

.method-badge,
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.method-cash { background: #d1fae5; color: #065f46; }
.method-card { background: #dbeafe; color: #1e40af; }
.method-bank_transfer { background: #e0e7ff; color: #3730a3; }
.method-check { background: #fce7f3; color: #831843; }
.method-online { background: #ede9fe; color: #5b21b6; }
.method-other { background: #f3f4f6; color: #374151; }

.status-completed { background: #d1fae5; color: #065f46; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-refunded { background: #fee2e2; color: #991b1b; }
.status-failed { background: #fee2e2; color: #991b1b; }
.status-cancelled { background: #f3f4f6; color: #374151; }

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.empty-state {
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  border-radius: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  font-size: 0.875rem;
  color: #6b7280;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #6366f1;
  color: white;
}

.btn-secondary {
  background: #64748b;
  color: white;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-link {
  background: transparent;
  color: #6366f1;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}
</style>
