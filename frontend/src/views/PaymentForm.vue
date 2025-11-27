<template>
  <div class="payment-form">
    <div class="header">
      <h1 class="title">Record Payment</h1>
      <router-link to="/payments" class="btn btn-secondary">Back to Payments</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">{{ error }}</div>

    <form v-if="!loading" @submit.prevent="handleSubmit" class="form">
      <!-- Student Selection -->
      <div class="form-section">
        <h2 class="section-title">Student Information</h2>

        <div class="form-group">
          <label for="student_search" class="label">Search Student *</label>
          <div class="search-input-wrapper">
            <input
              id="student_search"
              v-model="studentSearch"
              type="text"
              class="input"
              placeholder="Search by name or student ID..."
              @input="onSearchInput"
              :disabled="!!selectedStudent"
            />
            <div v-if="searchingStudents" class="search-loading">
              <span class="spinner"></span>
            </div>
          </div>
          <div v-if="studentSearch.length > 0 && studentSearch.length < 2 && !selectedStudent" class="field-hint">
            Type at least 2 characters to search
          </div>
        </div>

        <!-- Student Search Results -->
        <div v-if="showSearchResults && !selectedStudent" class="search-results">
          <div v-if="searchingStudents" class="search-loading-message">
            Searching students...
          </div>
          <div v-else-if="searchResults.length === 0 && studentSearch.length >= 2" class="no-results">
            No students found matching "{{ studentSearch }}"
          </div>
          <div
            v-else
            v-for="student in searchResults"
            :key="student.id"
            class="search-result-item"
            @click="selectStudent(student)"
          >
            <div class="student-name">{{ student.user?.first_name }} {{ student.user?.last_name }}</div>
            <div class="student-details">
              ID: {{ student.student_id }} | Grade {{ student.grade_level }}
            </div>
          </div>
        </div>

        <!-- Selected Student Display -->
        <div v-if="selectedStudent" class="selected-student">
          <div class="selected-student-info">
            <div class="student-name">{{ selectedStudent.name }}</div>
            <div class="student-details">
              ID: {{ selectedStudent.student_id }} | Grade {{ selectedStudent.grade_level }}
            </div>
          </div>
          <button type="button" @click="clearStudent" class="btn btn-link">Change Student</button>
        </div>
      </div>

      <!-- Student Fee Selection -->
      <div v-if="selectedStudent" class="form-section">
        <h2 class="section-title">Fee Selection</h2>

        <div v-if="loadingFees" class="loading-small">Loading student fees...</div>

        <div v-if="studentFees.length === 0 && !loadingFees" class="info-message">
          No active fees found for this student. Please assign a fee structure first.
        </div>

        <div v-if="studentFees.length > 0" class="form-group">
          <label for="student_fee_id" class="label">Student Fee *</label>
          <select
            id="student_fee_id"
            v-model="form.student_fee_id"
            required
            class="input"
            @change="onFeeSelected"
          >
            <option value="">Select fee to pay</option>
            <option
              v-for="fee in studentFees"
              :key="fee.id"
              :value="fee.id"
            >
              {{ fee.academic_year }} - {{ fee.payment_frequency }} | Balance Due: R {{ formatCurrency(fee.balance_due) }}
            </option>
          </select>
        </div>

        <!-- Fee Balance Display -->
        <div v-if="selectedFee" class="fee-balance-card">
          <div class="balance-row">
            <span class="balance-label">Total Amount Due:</span>
            <span class="balance-value">R {{ formatCurrency(selectedFee.total_amount_due) }}</span>
          </div>
          <div class="balance-row">
            <span class="balance-label">Total Paid:</span>
            <span class="balance-value paid">R {{ formatCurrency(selectedFee.total_paid) }}</span>
          </div>
          <div class="balance-row balance-due">
            <span class="balance-label">Balance Due:</span>
            <span class="balance-value">R {{ formatCurrency(selectedFee.balance_due) }}</span>
          </div>
        </div>
      </div>

      <!-- Payment Details -->
      <div v-if="selectedStudent && form.student_fee_id" class="form-section">
        <h2 class="section-title">Payment Details</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="amount" class="label">Payment Amount (R) *</label>
            <input
              id="amount"
              v-model.number="form.amount"
              type="number"
              step="0.01"
              min="0.01"
              :max="selectedFee?.balance_due"
              required
              class="input"
              placeholder="0.00"
            />
            <div v-if="selectedFee && form.amount > selectedFee.balance_due" class="field-hint error">
              Amount exceeds balance due
            </div>
          </div>

          <div class="form-group">
            <label for="payment_method" class="label">Payment Method *</label>
            <select id="payment_method" v-model="form.payment_method" required class="input">
              <option value="">Select method</option>
              <option value="cash">Cash</option>
              <option value="card">Card</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="check">Check</option>
              <option value="online">Online</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="payment_date" class="label">Payment Date *</label>
            <input
              id="payment_date"
              v-model="form.payment_date"
              type="date"
              required
              class="input"
              :max="today"
            />
          </div>

          <div class="form-group">
            <label for="transaction_reference" class="label">Transaction Reference</label>
            <input
              id="transaction_reference"
              v-model="form.transaction_reference"
              type="text"
              class="input"
              placeholder="Check #, confirmation #, etc."
            />
          </div>
        </div>

        <div class="form-group">
          <label for="allocation_notes" class="label">Allocation Notes</label>
          <textarea
            id="allocation_notes"
            v-model="form.allocation_notes"
            rows="2"
            class="input"
            placeholder="How should this payment be allocated? (optional)"
          />
        </div>

        <div class="form-group">
          <label for="notes" class="label">Additional Notes</label>
          <textarea
            id="notes"
            v-model="form.notes"
            rows="3"
            class="input"
            placeholder="Any additional notes about this payment..."
          />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="form.auto_generate_receipt"
              class="checkbox"
            />
            <span>Auto-generate receipt number</span>
          </label>
        </div>
      </div>

      <!-- Payment Type Selection -->
      <div v-if="selectedStudent && form.student_fee_id" class="form-section">
        <h2 class="section-title">Payment Type</h2>

        <div class="form-group">
          <label class="radio-label">
            <input
              type="radio"
              v-model="paymentType"
              value="completed"
              class="radio"
            />
            <span>Completed Payment</span>
            <span class="radio-hint">Payment is confirmed and complete</span>
          </label>
        </div>

        <div class="form-group">
          <label class="radio-label">
            <input
              type="radio"
              v-model="paymentType"
              value="pending"
              class="radio"
            />
            <span>Pending Payment</span>
            <span class="radio-hint">For checks or pending authorization</span>
          </label>
        </div>
      </div>

      <!-- Form Actions -->
      <div v-if="selectedStudent && form.student_fee_id" class="form-actions">
        <button type="button" @click="handleCancel" class="btn btn-secondary">
          Cancel
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="submitting || !isFormValid"
        >
          {{ submitting ? 'Recording Payment...' : 'Record Payment' }}
        </button>
      </div>
    </form>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <p>{{ successMessage }}</p>
      <div class="success-actions">
        <router-link to="/payments" class="btn btn-primary">View All Payments</router-link>
        <button @click="resetForm" class="btn btn-secondary">Record Another Payment</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePaymentStore } from '@/stores/paymentStore'
import { useStudentStore } from '@/stores/studentStore'
import { useSchool } from '@/composables/useSchool'
import type { PaymentMethod } from '@/types/payment'
import type { Student } from '@/types/student'

const router = useRouter()
const paymentStore = usePaymentStore()
const studentStore = useStudentStore()
const { currentSchoolId } = useSchool()

// State
const loading = ref(false)
const loadingFees = ref(false)
const submitting = ref(false)
const searchingStudents = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const studentSearch = ref('')
const searchResults = ref<any[]>([])
const selectedStudent = ref<any | null>(null)
const studentFees = ref<any[]>([])
const selectedFee = ref<any | null>(null)
const paymentType = ref<'completed' | 'pending'>('completed')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const form = ref({
  student_fee_id: '',
  amount: 0,
  payment_method: '' as PaymentMethod | '',
  payment_date: new Date().toISOString().split('T')[0],
  transaction_reference: '',
  allocation_notes: '',
  notes: '',
  auto_generate_receipt: true
})

// Computed
const today = computed(() => new Date().toISOString().split('T')[0])

const showSearchResults = computed(() => {
  return studentSearch.value.length >= 2 && !selectedStudent.value
})

const isFormValid = computed(() => {
  return (
    selectedStudent.value &&
    form.value.student_fee_id &&
    form.value.amount > 0 &&
    form.value.payment_method &&
    form.value.payment_date &&
    (!selectedFee.value || form.value.amount <= selectedFee.value.balance_due)
  )
})

// Methods
function onSearchInput() {
  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  // If search is less than 2 characters, clear results
  if (studentSearch.value.length < 2) {
    searchResults.value = []
    return
  }

  // Debounce search by 300ms
  searchTimeout = setTimeout(() => {
    searchStudents()
  }, 300)
}

async function searchStudents() {
  if (studentSearch.value.length < 2) {
    searchResults.value = []
    return
  }

  if (!currentSchoolId.value) {
    error.value = 'Please select a school first'
    return
  }

  searchingStudents.value = true
  error.value = null

  try {
    // Search students using the student store
    await studentStore.fetchStudents({
      school_id: currentSchoolId.value,
      limit: 50,
      page: 1
    })

    // Filter students by search term (name or student_id)
    const lowerSearch = studentSearch.value.toLowerCase()
    searchResults.value = studentStore.students.filter((s: Student) => {
      const fullName = `${s.user?.first_name || ''} ${s.user?.last_name || ''}`.toLowerCase()
      return (
        fullName.includes(lowerSearch) ||
        s.student_id.toLowerCase().includes(lowerSearch)
      )
    }).slice(0, 10) // Limit to 10 results
  } catch (err: any) {
    console.error('Failed to search students:', err)
    error.value = 'Failed to search students. Please try again.'
    searchResults.value = []
  } finally {
    searchingStudents.value = false
  }
}

function selectStudent(student: Student) {
  selectedStudent.value = {
    id: student.id,
    name: `${student.user?.first_name || ''} ${student.user?.last_name || ''}`.trim(),
    student_id: student.student_id,
    grade_level: student.grade_level
  }
  studentSearch.value = selectedStudent.value.name
  searchResults.value = []
  loadStudentFees()
}

function clearStudent() {
  selectedStudent.value = null
  studentSearch.value = ''
  studentFees.value = []
  selectedFee.value = null
  form.value.student_fee_id = ''
}

async function loadStudentFees() {
  if (!selectedStudent.value || !currentSchoolId.value) return

  loadingFees.value = true
  error.value = null

  try {
    // Fetch student fees from API
    const response = await fetch(
      `http://localhost:8000/api/v1/student-fees?school_id=${currentSchoolId.value}&student_id=${selectedStudent.value.id}`,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch student fees')
    }

    const data = await response.json()

    // Filter to only show fees with balance due > 0 (unpaid or partially paid)
    studentFees.value = (data.data || []).filter((fee: any) => fee.balance_due > 0)
  } catch (err: any) {
    error.value = err.message || 'Failed to load student fees'
    console.error('Failed to load student fees:', err)
  } finally {
    loadingFees.value = false
  }
}

function onFeeSelected() {
  selectedFee.value = studentFees.value.find(f => f.id === form.value.student_fee_id) || null

  // Auto-fill amount with balance due
  if (selectedFee.value) {
    form.value.amount = selectedFee.value.balance_due
  }
}

async function handleSubmit() {
  if (!isFormValid.value || !currentSchoolId.value) return

  submitting.value = true
  error.value = null

  try {
    const paymentData = {
      school_id: currentSchoolId.value,
      student_fee_id: form.value.student_fee_id,
      amount: form.value.amount,
      payment_method: form.value.payment_method as PaymentMethod,
      payment_date: form.value.payment_date,
      transaction_reference: form.value.transaction_reference || undefined,
      allocation_notes: form.value.allocation_notes || undefined,
      notes: form.value.notes || undefined,
      auto_generate_receipt: form.value.auto_generate_receipt
    }

    if (paymentType.value === 'completed') {
      await paymentStore.createPayment(paymentData)
      successMessage.value = `Payment of R ${formatCurrency(form.value.amount)} recorded successfully!`
    } else {
      await paymentStore.createPendingPayment({
        school_id: currentSchoolId.value,
        student_fee_id: form.value.student_fee_id,
        amount: form.value.amount,
        payment_method: form.value.payment_method as PaymentMethod,
        transaction_reference: form.value.transaction_reference || undefined,
        notes: form.value.notes || undefined
      })
      successMessage.value = `Pending payment of R ${formatCurrency(form.value.amount)} recorded successfully!`
    }

    // Clear form on success
    // Don't reset immediately - show success message
  } catch (err: any) {
    error.value = err.message || 'Failed to record payment'
    console.error('Failed to record payment:', err)
  } finally {
    submitting.value = false
  }
}

function handleCancel() {
  router.push('/payments')
}

function resetForm() {
  selectedStudent.value = null
  studentSearch.value = ''
  studentFees.value = []
  selectedFee.value = null
  successMessage.value = null

  form.value = {
    student_fee_id: '',
    amount: 0,
    payment_method: '',
    payment_date: new Date().toISOString().split('T')[0],
    transaction_reference: '',
    allocation_notes: '',
    notes: '',
    auto_generate_receipt: true
  }

  paymentType.value = 'completed'
}

function formatCurrency(amount: number): string {
  return amount.toLocaleString('en-ZA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Lifecycle
onMounted(() => {
  if (!currentSchoolId.value) {
    error.value = 'Please select a school first'
  }
})
</script>

<style scoped>
.payment-form {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #111827;
  margin: 0;
}

.loading,
.loading-small {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
}

.loading-small {
  padding: 1rem;
  font-size: 0.875rem;
}

.error {
  padding: 1rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.info-message {
  padding: 1rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.success-message {
  padding: 2rem;
  background: #d1fae5;
  border-radius: 8px;
  text-align: center;
}

.success-message p {
  font-size: 1.125rem;
  font-weight: 500;
  color: #065f46;
  margin-bottom: 1.5rem;
}

.success-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

.field-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.field-hint.error {
  color: #dc2626;
}

.checkbox-label,
.radio-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.checkbox-label:hover,
.radio-label:hover {
  background: #f9fafb;
}

.checkbox,
.radio {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.radio-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: auto;
}

.search-results {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-top: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-result-item {
  padding: 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background: #f9fafb;
}

.selected-student {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.selected-student-info {
  flex: 1;
}

.student-name {
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.student-details {
  font-size: 0.875rem;
  color: #6b7280;
}

.search-input-wrapper {
  position: relative;
}

.search-loading {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-loading-message {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.no-results {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.fee-balance-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.balance-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.balance-row:last-child {
  border-bottom: none;
}

.balance-row.balance-due {
  font-weight: 600;
  font-size: 1.125rem;
  padding-top: 0.75rem;
  margin-top: 0.5rem;
  border-top: 2px solid #d1d5db;
}

.balance-label {
  color: #6b7280;
}

.balance-value {
  color: #111827;
  font-weight: 500;
}

.balance-value.paid {
  color: #059669;
}

.balance-due .balance-value {
  color: #dc2626;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

/* Button Styles */
.btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9375rem;
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

.btn-link {
  background: transparent;
  color: #6366f1;
  padding: 0.25rem 0.5rem;
}

@media (max-width: 768px) {
  .payment-form {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .success-actions {
    flex-direction: column;
  }
}
</style>
