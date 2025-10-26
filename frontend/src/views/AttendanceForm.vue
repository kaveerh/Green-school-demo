<template>
  <div class="attendance-form">
    <div class="page-header">
      <div>
        <h1>{{ isEdit ? 'Edit Attendance' : 'Mark Attendance' }}</h1>
        <p>{{ isEdit ? 'Update attendance record' : 'Mark attendance for class' }}</p>
      </div>
      <router-link to="/attendance" class="btn btn-secondary">
        <span class="icon">←</span>
        Back to List
      </router-link>
    </div>

    <div class="form-container">
      <!-- Single Record Edit Mode -->
      <div v-if="isEdit" class="form-card">
        <h3>Attendance Record</h3>

        <div class="form-row">
          <div class="form-group">
            <label>Student</label>
            <div class="readonly-field">
              {{ currentAttendance?.student?.name || 'Unknown' }}
            </div>
          </div>

          <div class="form-group">
            <label>Date</label>
            <div class="readonly-field">
              {{ formatDate(currentAttendance?.attendance_date || '') }}
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="status">Status *</label>
            <select id="status" v-model="formData.status" class="form-select" required>
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="tardy">Tardy</option>
              <option value="excused">Excused</option>
              <option value="sick">Sick</option>
            </select>
          </div>

          <div class="form-group">
            <label for="checkIn">Check In Time</label>
            <input
              id="checkIn"
              v-model="formData.check_in_time"
              type="time"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="checkOut">Check Out Time</label>
            <input
              id="checkOut"
              v-model="formData.check_out_time"
              type="time"
              class="form-input"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="notes">Notes</label>
          <textarea
            id="notes"
            v-model="formData.notes"
            rows="3"
            class="form-textarea"
            placeholder="Optional notes about this attendance record..."
          ></textarea>
        </div>

        <div class="form-actions">
          <button @click="handleSubmit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Changes' }}
          </button>
          <router-link to="/attendance" class="btn btn-secondary">Cancel</router-link>
        </div>
      </div>

      <!-- Bulk Attendance Marking Mode -->
      <div v-else class="bulk-form">
        <div class="form-card">
          <h3>Class Information</h3>

          <div class="form-row">
            <div class="form-group">
              <label for="classId">Class *</label>
              <input
                id="classId"
                v-model="bulkData.class_id"
                type="text"
                class="form-input"
                placeholder="Enter Class ID"
                required
              />
            </div>

            <div class="form-group">
              <label for="date">Date *</label>
              <input
                id="date"
                v-model="bulkData.attendance_date"
                type="date"
                class="form-input"
                required
              />
            </div>
          </div>

          <button @click="loadStudents" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Loading...' : 'Load Students' }}
          </button>
        </div>

        <!-- Student Attendance Table -->
        <div v-if="students.length > 0" class="form-card">
          <div class="card-header">
            <h3>Mark Attendance ({{ students.length }} students)</h3>
            <div class="quick-actions">
              <button @click="markAllPresent" class="btn btn-sm btn-success">
                Mark All Present
              </button>
              <button @click="clearAll" class="btn btn-sm btn-secondary">Clear All</button>
            </div>
          </div>

          <div class="students-table">
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Status</th>
                  <th>Check In</th>
                  <th>Check Out</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(student, index) in students" :key="student.id">
                  <td>
                    <div class="student-info">
                      <strong>{{ student.name }}</strong>
                      <span class="student-id">{{ student.student_id }}</span>
                    </div>
                  </td>
                  <td>
                    <select
                      v-model="student.attendance.status"
                      class="form-select"
                      :class="`status-${student.attendance.status}`"
                    >
                      <option value="">Select...</option>
                      <option value="present">Present</option>
                      <option value="absent">Absent</option>
                      <option value="tardy">Tardy</option>
                      <option value="excused">Excused</option>
                      <option value="sick">Sick</option>
                    </select>
                  </td>
                  <td>
                    <input
                      v-model="student.attendance.check_in_time"
                      type="time"
                      class="form-input form-input-sm"
                      :disabled="student.attendance.status !== 'present' && student.attendance.status !== 'tardy'"
                    />
                  </td>
                  <td>
                    <input
                      v-model="student.attendance.check_out_time"
                      type="time"
                      class="form-input form-input-sm"
                      :disabled="!student.attendance.check_in_time"
                    />
                  </td>
                  <td>
                    <input
                      v-model="student.attendance.notes"
                      type="text"
                      class="form-input form-input-sm"
                      placeholder="Optional notes..."
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="form-actions">
            <button @click="submitBulkAttendance" class="btn btn-primary" :disabled="loading || !hasValidRecords">
              {{ loading ? 'Saving...' : `Save Attendance (${validRecordsCount})` }}
            </button>
            <router-link to="/attendance" class="btn btn-secondary">Cancel</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-alert">
      <span class="icon">⚠️</span>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAttendanceStore } from '@/stores/attendanceStore'
import type { AttendanceStatus } from '@/types/attendance'

interface StudentAttendanceData {
  id: string
  name: string
  student_id: string
  attendance: {
    status: AttendanceStatus | ''
    check_in_time: string | null
    check_out_time: string | null
    notes: string | null
  }
}

const route = useRoute()
const router = useRouter()
const attendanceStore = useAttendanceStore()

const isEdit = computed(() => !!route.params.id)
const attendanceId = computed(() => route.params.id as string)

// Mock school ID - replace with actual from auth
const schoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61')

// Single record edit form
const formData = ref({
  status: 'present' as AttendanceStatus,
  check_in_time: null as string | null,
  check_out_time: null as string | null,
  notes: null as string | null
})

// Bulk attendance form
const bulkData = ref({
  class_id: '2e008ff4-dc05-4c6b-8059-ca92fceb3f9a',
  attendance_date: new Date().toISOString().split('T')[0]
})

const students = ref<StudentAttendanceData[]>([])

const loading = computed(() => attendanceStore.loading)
const error = computed(() => attendanceStore.error)
const currentAttendance = computed(() => attendanceStore.currentAttendance)

const hasValidRecords = computed(() => {
  return students.value.some(s => s.attendance.status !== '')
})

const validRecordsCount = computed(() => {
  return students.value.filter(s => s.attendance.status !== '').length
})

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

function markAllPresent() {
  const currentTime = new Date().toTimeString().slice(0, 5)
  students.value.forEach(student => {
    student.attendance.status = 'present'
    student.attendance.check_in_time = currentTime
  })
}

function clearAll() {
  students.value.forEach(student => {
    student.attendance.status = ''
    student.attendance.check_in_time = null
    student.attendance.check_out_time = null
    student.attendance.notes = null
  })
}

async function loadStudents() {
  // Mock student data - replace with actual API call
  students.value = [
    {
      id: 'c7d715a4-cca0-4133-9a6d-172d585a10e6',
      name: 'Alice Johnson',
      student_id: 'STU2024001',
      attendance: {
        status: '',
        check_in_time: null,
        check_out_time: null,
        notes: null
      }
    }
    // Add more students as needed
  ]
}

async function handleSubmit() {
  if (!isEdit.value || !attendanceId.value) return

  try {
    await attendanceStore.updateAttendance(attendanceId.value, {
      status: formData.value.status,
      check_in_time: formData.value.check_in_time,
      check_out_time: formData.value.check_out_time,
      notes: formData.value.notes
    })

    router.push('/attendance')
  } catch (err) {
    console.error('Failed to update attendance:', err)
  }
}

async function submitBulkAttendance() {
  const validStudents = students.value.filter(s => s.attendance.status !== '')

  if (validStudents.length === 0) {
    alert('Please mark attendance for at least one student')
    return
  }

  try {
    await attendanceStore.bulkCreateAttendance({
      school_id: schoolId.value,
      class_id: bulkData.value.class_id,
      attendance_date: bulkData.value.attendance_date,
      students: validStudents.map(s => ({
        student_id: s.id,
        status: s.attendance.status as AttendanceStatus,
        check_in_time: s.attendance.check_in_time,
        check_out_time: s.attendance.check_out_time,
        notes: s.attendance.notes
      }))
    })

    router.push('/attendance')
  } catch (err) {
    console.error('Failed to create bulk attendance:', err)
  }
}

onMounted(async () => {
  if (isEdit.value && attendanceId.value) {
    await attendanceStore.fetchAttendanceById(attendanceId.value)

    if (currentAttendance.value) {
      formData.value = {
        status: currentAttendance.value.status as AttendanceStatus,
        check_in_time: currentAttendance.value.check_in_time,
        check_out_time: currentAttendance.value.check_out_time,
        notes: currentAttendance.value.notes
      }
    }
  }
})
</script>

<style scoped>
.attendance-form {
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
  font-size: 2rem;
  color: #1f2937;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-card h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.25rem;
  color: #1f2937;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  margin: 0;
}

.quick-actions {
  display: flex;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.readonly-field {
  padding: 0.625rem 0.875rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  color: #6b7280;
  font-size: 0.875rem;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input-sm {
  padding: 0.375rem 0.625rem;
  font-size: 0.8125rem;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.students-table {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.students-table table {
  width: 100%;
  border-collapse: collapse;
}

.students-table thead {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.students-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.students-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.student-id {
  font-size: 0.75rem;
  color: #6b7280;
}

.status-present {
  color: #16a34a;
  font-weight: 500;
}

.status-absent {
  color: #dc2626;
  font-weight: 500;
}

.status-tardy {
  color: #d97706;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-success {
  background: #16a34a;
  color: white;
}

.btn-success:hover {
  background: #15803d;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-alert {
  background: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #991b1b;
}

.error-alert .icon {
  font-size: 1.5rem;
}

.icon {
  font-size: 1rem;
}
</style>
