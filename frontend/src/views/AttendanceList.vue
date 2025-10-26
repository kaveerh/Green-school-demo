<template>
  <div class="attendance-list">
    <div class="page-header">
      <div>
        <h1>Attendance</h1>
        <p>Track daily student attendance and view reports</p>
      </div>
      <div class="header-actions">
        <router-link to="/attendance/mark" class="btn btn-primary">
          <span class="icon">✓</span>
          Mark Attendance
        </router-link>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background-color: #dcfce7">
          <span style="color: #16a34a">✓</span>
        </div>
        <div class="stat-content">
          <div class="stat-label">Attendance Rate</div>
          <div class="stat-value">{{ statistics.attendance_rate.toFixed(1) }}%</div>
          <div class="stat-subtitle">{{ statistics.present_count }} present</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background-color: #fee2e2">
          <span style="color: #dc2626">✗</span>
        </div>
        <div class="stat-content">
          <div class="stat-label">Absence Rate</div>
          <div class="stat-value">{{ statistics.absence_rate.toFixed(1) }}%</div>
          <div class="stat-subtitle">{{ statistics.absent_count }} absent</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background-color: #fef3c7">
          <span style="color: #d97706">⏰</span>
        </div>
        <div class="stat-content">
          <div class="stat-label">Tardy</div>
          <div class="stat-value">{{ statistics.tardy_count }}</div>
          <div class="stat-subtitle">Late arrivals</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon" style="background-color: #e0e7ff">
          <span style="color: #4f46e5">📊</span>
        </div>
        <div class="stat-content">
          <div class="stat-label">Total Records</div>
          <div class="stat-value">{{ statistics.total_records }}</div>
          <div class="stat-subtitle">{{ statistics.days_tracked }} days tracked</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-group">
        <label>View Type</label>
        <select v-model="viewType" class="filter-select">
          <option value="student">Student</option>
          <option value="class">Class</option>
          <option value="school">School</option>
        </select>
      </div>

      <div v-if="viewType === 'student'" class="filter-group">
        <label>Student</label>
        <input v-model="selectedStudentId" type="text" placeholder="Student ID" class="filter-input" />
      </div>

      <div v-if="viewType === 'class'" class="filter-group">
        <label>Class</label>
        <input v-model="selectedClassId" type="text" placeholder="Class ID" class="filter-input" />
      </div>

      <div class="filter-group">
        <label>Date</label>
        <input v-model="selectedDate" type="date" class="filter-input" />
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="selectedStatus" class="filter-select">
          <option value="">All Statuses</option>
          <option value="present">Present</option>
          <option value="absent">Absent</option>
          <option value="tardy">Tardy</option>
          <option value="excused">Excused</option>
          <option value="sick">Sick</option>
        </select>
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Loading...' : 'Apply Filters' }}
        </button>
        <button @click="clearFilters" class="btn btn-secondary">Clear</button>
      </div>
    </div>

    <!-- Unnotified Absences Alert -->
    <div v-if="hasUnnotifiedAbsences" class="alert alert-warning">
      <div class="alert-content">
        <span class="alert-icon">⚠️</span>
        <div>
          <strong>{{ unnotifiedAbsences.length }} Unnotified Absences</strong>
          <p>There are students with absences that parents haven't been notified about.</p>
        </div>
      </div>
      <button @click="notifyParents" class="btn btn-sm btn-primary">
        Notify Parents
      </button>
    </div>

    <!-- Attendance Table -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading attendance records...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <span class="icon">⚠️</span>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="attendanceList.length === 0" class="empty-state">
      <span class="icon">📋</span>
      <h3>No Attendance Records</h3>
      <p>No attendance records found for the selected filters.</p>
      <router-link to="/attendance/mark" class="btn btn-primary">
        Mark Attendance
      </router-link>
    </div>

    <div v-else class="attendance-table-container">
      <table class="attendance-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Student</th>
            <th v-if="viewType !== 'class'">Class</th>
            <th>Status</th>
            <th>Check In</th>
            <th>Check Out</th>
            <th>Duration</th>
            <th>Parent Notified</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in attendanceList" :key="record.id">
            <td>{{ formatDate(record.attendance_date) }}</td>
            <td>
              <div class="student-cell">
                <strong>{{ record.student?.name || 'Unknown' }}</strong>
                <span class="student-id">{{ record.student?.student_id }}</span>
              </div>
            </td>
            <td v-if="viewType !== 'class'">
              <div v-if="record.class" class="class-cell">
                <strong>{{ record.class.name }}</strong>
                <span class="class-code">{{ record.class.code }}</span>
              </div>
              <span v-else class="text-muted">Homeroom</span>
            </td>
            <td>
              <span :class="['status-badge', `status-${record.status}`]">
                {{ getStatusLabel(record.status) }}
              </span>
            </td>
            <td>{{ formatTime(record.check_in_time) }}</td>
            <td>{{ formatTime(record.check_out_time) }}</td>
            <td>{{ formatDuration(record.duration_minutes) }}</td>
            <td>
              <span v-if="record.parent_notified" class="badge badge-success">
                ✓ Notified
              </span>
              <span v-else-if="record.needs_parent_notification" class="badge badge-warning">
                Pending
              </span>
              <span v-else class="badge badge-secondary">N/A</span>
            </td>
            <td>
              <div class="action-buttons">
                <button
                  @click="editAttendance(record)"
                  class="btn-icon"
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  @click="deleteRecord(record)"
                  class="btn-icon btn-danger"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="totalRecords > pageSize" class="pagination">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="btn btn-sm"
        >
          Previous
        </button>
        <span class="pagination-info">
          Page {{ currentPage }} of {{ totalPages }} ({{ totalRecords }} total)
        </span>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="btn btn-sm"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAttendanceStore } from '@/stores/attendanceStore'
import { getStatusLabel, formatTime, formatDuration } from '@/types/attendance'
import type { Attendance, AttendanceStatus } from '@/types/attendance'

const router = useRouter()
const attendanceStore = useAttendanceStore()

// Mock school ID - replace with actual from auth
const schoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61')

// Filters
const viewType = ref<'student' | 'class' | 'school'>('class')
const selectedStudentId = ref('')
const selectedClassId = ref('2e008ff4-dc05-4c6b-8059-ca92fceb3f9a')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedStatus = ref<AttendanceStatus | ''>('')

// State
const loading = computed(() => attendanceStore.loading)
const error = computed(() => attendanceStore.error)
const statistics = computed(() => attendanceStore.statistics)
const unnotifiedAbsences = computed(() => attendanceStore.unnotifiedAbsences)
const hasUnnotifiedAbsences = computed(() => attendanceStore.hasUnnotifiedAbsences)

const attendanceList = computed(() => {
  if (viewType.value === 'student') return attendanceStore.studentAttendance
  if (viewType.value === 'class') return attendanceStore.classAttendance
  return attendanceStore.schoolAttendance
})

const totalRecords = computed(() => {
  if (viewType.value === 'student') return attendanceStore.studentTotal
  if (viewType.value === 'class') return attendanceStore.classTotal
  return attendanceStore.schoolTotal
})

const currentPage = computed(() => attendanceStore.currentPage)
const pageSize = computed(() => attendanceStore.pageSize)
const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value))

// Methods
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

async function applyFilters() {
  try {
    if (viewType.value === 'student' && selectedStudentId.value) {
      await attendanceStore.fetchStudentAttendance(selectedStudentId.value, {
        start_date: selectedDate.value,
        end_date: selectedDate.value,
        status: selectedStatus.value || undefined
      })
    } else if (viewType.value === 'class' && selectedClassId.value) {
      await attendanceStore.fetchClassAttendance(selectedClassId.value, selectedDate.value)
    } else if (viewType.value === 'school') {
      await attendanceStore.fetchSchoolAttendance(
        schoolId.value,
        selectedDate.value,
        selectedStatus.value || undefined
      )
    }

    // Fetch statistics
    await attendanceStore.fetchStatistics(
      schoolId.value,
      selectedDate.value,
      selectedDate.value,
      selectedClassId.value || undefined
    )

    // Fetch unnotified absences
    await attendanceStore.fetchUnnotifiedAbsences(schoolId.value, selectedDate.value)
  } catch (err) {
    console.error('Failed to fetch attendance:', err)
  }
}

function clearFilters() {
  selectedStudentId.value = ''
  selectedClassId.value = ''
  selectedDate.value = new Date().toISOString().split('T')[0]
  selectedStatus.value = ''
  attendanceStore.clearAttendance()
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  // Implement pagination logic
}

function editAttendance(record: Attendance) {
  router.push(`/attendance/${record.id}/edit`)
}

async function deleteRecord(record: Attendance) {
  if (!confirm('Are you sure you want to delete this attendance record?')) return

  try {
    await attendanceStore.deleteAttendance(record.id)
    await applyFilters() // Refresh list
  } catch (err) {
    console.error('Failed to delete attendance:', err)
  }
}

async function notifyParents() {
  if (!hasUnnotifiedAbsences.value) return

  const ids = unnotifiedAbsences.value.map((a) => a.id)

  try {
    await attendanceStore.markParentNotified(ids)
    alert(`Successfully notified parents for ${ids.length} absences`)
  } catch (err) {
    console.error('Failed to notify parents:', err)
  }
}

onMounted(() => {
  applyFilters()
})
</script>

<style scoped>
.attendance-list {
  max-width: 1400px;
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

.header-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-subtitle {
  font-size: 0.875rem;
  color: #9ca3af;
  margin-top: 0.25rem;
}

.filters-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-input,
.filter-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.alert {
  background: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-content {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert strong {
  display: block;
  color: #92400e;
  margin-bottom: 0.25rem;
}

.alert p {
  margin: 0;
  color: #78350f;
  font-size: 0.875rem;
}

.attendance-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.attendance-table {
  width: 100%;
  border-collapse: collapse;
}

.attendance-table thead {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.attendance-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.attendance-table td {
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.875rem;
}

.student-cell,
.class-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.student-id,
.class-code {
  font-size: 0.75rem;
  color: #6b7280;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-present {
  background: #dcfce7;
  color: #16a34a;
}

.status-absent {
  background: #fee2e2;
  color: #dc2626;
}

.status-tardy {
  background: #fef3c7;
  color: #d97706;
}

.status-excused {
  background: #e0e7ff;
  color: #4f46e5;
}

.status-sick {
  background: #fed7aa;
  color: #ea580c;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-success {
  background: #dcfce7;
  color: #16a34a;
}

.badge-warning {
  background: #fef3c7;
  color: #d97706;
}

.badge-secondary {
  background: #f3f4f6;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1.125rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 1;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  font-size: 0.875rem;
  color: #6b7280;
}

.loading,
.error-message,
.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state .icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.btn {
  padding: 0.5rem 1rem;
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.text-muted {
  color: #9ca3af;
  font-style: italic;
}
</style>
