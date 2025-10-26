<template>
  <div class="activity-roster-page">
    <div class="page-header">
      <div>
        <h1>Activity Roster</h1>
        <p v-if="roster" class="activity-name">{{ roster.activity.name }}</p>
      </div>
      <router-link to="/activities" class="btn btn-link">Back to Activities</router-link>
    </div>

    <div v-if="loading" class="loading">Loading roster...</div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="roster && !loading" class="roster-content">
      <!-- Activity Summary -->
      <div class="activity-summary">
        <div class="summary-card">
          <div class="summary-item">
            <span class="summary-label">Activity Type</span>
            <span class="summary-value">
              <span :class="`activity-badge activity-${roster.activity.activity_type}`">
                {{ roster.activity.activity_type }}
              </span>
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Status</span>
            <span class="summary-value">
              <span :class="`status-badge status-${roster.activity.status}`">
                {{ roster.activity.status }}
              </span>
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Enrolled</span>
            <span class="summary-value">{{ roster.total_enrolled }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Waitlisted</span>
            <span class="summary-value">{{ roster.total_waitlisted }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Available Slots</span>
            <span class="summary-value">
              {{ roster.available_slots !== null ? roster.available_slots : 'Unlimited' }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Cost</span>
            <span class="summary-value">${{ formatCost(roster.activity.total_cost) }}</span>
          </div>
        </div>
      </div>

      <!-- Enroll New Student -->
      <div class="enroll-section">
        <button @click="showEnrollForm = !showEnrollForm" class="btn btn-primary">
          {{ showEnrollForm ? 'Cancel' : 'Enroll New Student' }}
        </button>

        <div v-if="showEnrollForm" class="enroll-form">
          <h3>Enroll Student</h3>
          <form @submit.prevent="handleEnrollStudent">
            <div class="form-group">
              <label for="student_id" class="required">Student</label>
              <select id="student_id" v-model="enrollForm.student_id" required>
                <option value="">Select student...</option>
                <!-- TODO: Load students from API -->
                <option value="student-1">Student 1</option>
                <option value="student-2">Student 2</option>
              </select>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="enrollForm.parent_consent" />
                Parent Consent Received
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="enrollForm.medical_clearance" />
                Medical Clearance Received
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="enrollForm.emergency_contact_provided" />
                Emergency Contact Provided
              </label>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="enrolling">
                {{ enrolling ? 'Enrolling...' : 'Enroll Student' }}
              </button>
              <button type="button" @click="showEnrollForm = false" class="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Active Enrollments -->
      <div class="enrollments-section">
        <h2>Active Enrollments ({{ roster.active_enrollments.length }})</h2>

        <div v-if="roster.active_enrollments.length === 0" class="empty-state">
          No students currently enrolled
        </div>

        <div v-else class="enrollment-table">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Grade</th>
                <th>Enrolled Date</th>
                <th>Payment Status</th>
                <th>Amount Paid</th>
                <th>Attendance</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="enrollment in roster.active_enrollments" :key="enrollment.id">
                <td>
                  <div class="student-info">
                    <strong>{{ enrollment.student?.name || 'Unknown' }}</strong>
                  </div>
                </td>
                <td>Grade {{ enrollment.student?.grade_level || '-' }}</td>
                <td>{{ formatDate(enrollment.enrollment_date) }}</td>
                <td>
                  <span :class="`payment-badge payment-${enrollment.payment_status}`">
                    {{ enrollment.payment_status }}
                  </span>
                </td>
                <td>${{ enrollment.amount_paid.toFixed(2) }}</td>
                <td>
                  {{ enrollment.attendance_count }} / {{ enrollment.total_sessions || '-' }}
                  <span v-if="enrollment.attendance_percentage" class="attendance-pct">
                    ({{ enrollment.attendance_percentage }}%)
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button
                      v-if="enrollment.payment_status !== 'paid' && enrollment.payment_status !== 'waived'"
                      @click="openPaymentModal(enrollment)"
                      class="btn-action btn-payment"
                      title="Record Payment"
                    >
                      💵
                    </button>
                    <button
                      @click="handleWithdraw(enrollment)"
                      class="btn-action btn-withdraw"
                      title="Withdraw Student"
                    >
                      ❌
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Waitlisted Enrollments -->
      <div v-if="roster.waitlisted_enrollments.length > 0" class="enrollments-section">
        <h2>Waitlist ({{ roster.waitlisted_enrollments.length }})</h2>

        <div class="enrollment-table">
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Grade</th>
                <th>Enrolled Date</th>
                <th>Payment Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="enrollment in roster.waitlisted_enrollments" :key="enrollment.id">
                <td>
                  <div class="student-info">
                    <strong>{{ enrollment.student?.name || 'Unknown' }}</strong>
                  </div>
                </td>
                <td>Grade {{ enrollment.student?.grade_level || '-' }}</td>
                <td>{{ formatDate(enrollment.enrollment_date) }}</td>
                <td>
                  <span :class="`payment-badge payment-${enrollment.payment_status}`">
                    {{ enrollment.payment_status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button
                      @click="handleWithdraw(enrollment)"
                      class="btn-action btn-withdraw"
                      title="Remove from Waitlist"
                    >
                      ❌
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="showPaymentModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal-content" @click.stop>
        <h3>Record Payment</h3>

        <div v-if="selectedEnrollment" class="payment-form">
          <p><strong>Student:</strong> {{ selectedEnrollment.student?.name }}</p>
          <p><strong>Amount Paid:</strong> ${{ selectedEnrollment.amount_paid.toFixed(2) }}</p>
          <p><strong>Total Cost:</strong> ${{ roster?.activity.total_cost?.toFixed(2) }}</p>

          <form @submit.prevent="handleRecordPayment">
            <div class="form-group">
              <label for="payment_amount" class="required">Payment Amount</label>
              <input
                id="payment_amount"
                v-model.number="paymentForm.amount"
                type="number"
                min="0.01"
                step="0.01"
                required
              />
            </div>

            <div class="form-group">
              <label for="payment_date">Payment Date</label>
              <input
                id="payment_date"
                v-model="paymentForm.payment_date"
                type="date"
              />
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="processing">
                {{ processing ? 'Processing...' : 'Record Payment' }}
              </button>
              <button
                type="button"
                @click="handleWaivePayment"
                class="btn btn-warning"
                :disabled="processing"
              >
                Waive Payment
              </button>
              <button type="button" @click="closePaymentModal" class="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useActivityStore } from '@/stores/activityStore'
import type { ActivityEnrollment, EnrollmentCreateInput } from '@/types/activity'

const route = useRoute()
const activityStore = useActivityStore()

// State
const showEnrollForm = ref(false)
const showPaymentModal = ref(false)
const selectedEnrollment = ref<ActivityEnrollment | null>(null)
const enrolling = ref(false)
const processing = ref(false)

const enrollForm = ref<EnrollmentCreateInput & { student_id: string }>({
  student_id: '',
  parent_consent: false,
  medical_clearance: false,
  emergency_contact_provided: false
})

const paymentForm = ref({
  amount: 0,
  payment_date: new Date().toISOString().split('T')[0]
})

// Computed
const loading = computed(() => activityStore.loading)
const error = computed(() => activityStore.error)
const roster = computed(() => activityStore.currentRoster)

// Methods
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

function formatCost(cost: number | undefined): string {
  return cost ? cost.toFixed(2) : '0.00'
}

function openPaymentModal(enrollment: ActivityEnrollment) {
  selectedEnrollment.value = enrollment
  const remainingAmount = (roster.value?.activity.total_cost || 0) - enrollment.amount_paid
  paymentForm.value.amount = Math.max(0, remainingAmount)
  showPaymentModal.value = true
}

function closePaymentModal() {
  showPaymentModal.value = false
  selectedEnrollment.value = null
  paymentForm.value = {
    amount: 0,
    payment_date: new Date().toISOString().split('T')[0]
  }
}

async function handleEnrollStudent() {
  if (!enrollForm.value.student_id) {
    alert('Please select a student')
    return
  }

  enrolling.value = true
  const activityId = route.params.id as string
  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  try {
    await activityStore.enrollStudent(
      activityId,
      {
        student_id: enrollForm.value.student_id,
        parent_consent: enrollForm.value.parent_consent,
        medical_clearance: enrollForm.value.medical_clearance,
        emergency_contact_provided: enrollForm.value.emergency_contact_provided
      },
      userId
    )

    // Reload roster
    await activityStore.fetchActivityRoster(activityId)

    // Reset form
    enrollForm.value = {
      student_id: '',
      parent_consent: false,
      medical_clearance: false,
      emergency_contact_provided: false
    }
    showEnrollForm.value = false
  } catch (err) {
    console.error('Failed to enroll student:', err)
    alert('Failed to enroll student. Please try again.')
  } finally {
    enrolling.value = false
  }
}

async function handleRecordPayment() {
  if (!selectedEnrollment.value) return

  processing.value = true
  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  try {
    await activityStore.recordPayment(
      selectedEnrollment.value.id,
      {
        amount: paymentForm.value.amount,
        payment_date: paymentForm.value.payment_date || undefined
      },
      userId
    )

    // Reload roster
    await activityStore.fetchActivityRoster(route.params.id as string)

    closePaymentModal()
  } catch (err) {
    console.error('Failed to record payment:', err)
    alert('Failed to record payment. Please try again.')
  } finally {
    processing.value = false
  }
}

async function handleWaivePayment() {
  if (!selectedEnrollment.value) return

  if (!confirm('Are you sure you want to waive payment for this student?')) {
    return
  }

  processing.value = true
  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  try {
    await activityStore.waivePayment(selectedEnrollment.value.id, userId)

    // Reload roster
    await activityStore.fetchActivityRoster(route.params.id as string)

    closePaymentModal()
  } catch (err) {
    console.error('Failed to waive payment:', err)
    alert('Failed to waive payment. Please try again.')
  } finally {
    processing.value = false
  }
}

async function handleWithdraw(enrollment: ActivityEnrollment) {
  const reason = prompt('Enter reason for withdrawal (optional):')

  if (reason === null) {
    // User cancelled
    return
  }

  const activityId = route.params.id as string
  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  try {
    await activityStore.withdrawStudent(
      activityId,
      enrollment.student_id,
      { reason: reason || undefined },
      userId
    )

    // Reload roster
    await activityStore.fetchActivityRoster(activityId)
  } catch (err) {
    console.error('Failed to withdraw student:', err)
    alert('Failed to withdraw student. Please try again.')
  }
}

// Lifecycle
onMounted(async () => {
  const activityId = route.params.id as string
  await activityStore.fetchActivityRoster(activityId)
})
</script>

<style scoped>
.activity-roster-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
}

.activity-name {
  color: #6b7280;
  font-size: 1.1rem;
  margin: 0;
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
  margin-bottom: 2rem;
}

.roster-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Activity Summary */
.activity-summary {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.summary-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.summary-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

/* Badges */
.activity-badge,
.status-badge,
.payment-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.activity-sports { background: #dbeafe; color: #1e40af; }
.activity-club { background: #fce7f3; color: #9f1239; }
.activity-art { background: #fef3c7; color: #92400e; }
.activity-music { background: #e9d5ff; color: #6b21a8; }
.activity-academic { background: #d1fae5; color: #065f46; }
.activity-other { background: #e5e7eb; color: #374151; }

.status-active { background: #d1fae5; color: #065f46; }
.status-full { background: #fef3c7; color: #92400e; }
.status-cancelled { background: #fee2e2; color: #991b1b; }
.status-completed { background: #e5e7eb; color: #374151; }

.payment-pending { background: #fef3c7; color: #92400e; }
.payment-partial { background: #dbeafe; color: #1e40af; }
.payment-paid { background: #d1fae5; color: #065f46; }
.payment-waived { background: #e5e7eb; color: #374151; }

/* Enroll Section */
.enroll-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.enroll-form {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.enroll-form h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

/* Enrollments Section */
.enrollments-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.enrollments-section h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

/* Table */
.enrollment-table {
  overflow-x: auto;
}

.enrollment-table table {
  width: 100%;
  border-collapse: collapse;
}

.enrollment-table th,
.enrollment-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.enrollment-table th {
  background: #f9fafb;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.enrollment-table td {
  font-size: 0.875rem;
}

.student-info strong {
  color: #111827;
}

.attendance-pct {
  color: #6b7280;
  font-size: 0.8125rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-action:hover {
  background: #f3f4f6;
}

/* Modal */
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
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.payment-form p {
  margin: 0.5rem 0;
  font-size: 0.9375rem;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group label.required::after {
  content: ' *';
  color: #dc2626;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  font-family: inherit;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background: #d97706;
}

.btn-link {
  background: transparent;
  color: #3b82f6;
  padding: 0.5rem;
}

.btn-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .activity-roster-page {
    padding: 1rem;
  }

  .summary-card {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
  }

  .enrollment-table {
    font-size: 0.8125rem;
  }

  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }
}
</style>
