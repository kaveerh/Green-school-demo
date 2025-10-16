<template>
  <div class="student-list">
    <!-- Header -->
    <div class="student-list-header">
      <h2>Student Management</h2>
      <button @click="handleCreateStudent" class="btn-primary">
        + Create Student
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="student-list-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search students by ID or name..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <select v-model="filters.grade_level" @change="handleFilterChange" class="filter-select">
          <option value="">All Grades</option>
          <option value="1">Grade 1</option>
          <option value="2">Grade 2</option>
          <option value="3">Grade 3</option>
          <option value="4">Grade 4</option>
          <option value="5">Grade 5</option>
          <option value="6">Grade 6</option>
          <option value="7">Grade 7</option>
        </select>

        <select v-model="filters.status" @change="handleFilterChange" class="filter-select">
          <option value="">All Statuses</option>
          <option value="enrolled">Enrolled</option>
          <option value="graduated">Graduated</option>
          <option value="transferred">Transferred</option>
          <option value="withdrawn">Withdrawn</option>
          <option value="suspended">Suspended</option>
        </select>

        <select v-model="filters.gender" @change="handleFilterChange" class="filter-select">
          <option value="">All Genders</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
          <option value="prefer_not_to_say">Prefer not to say</option>
        </select>

        <button @click="clearFilters" class="btn-secondary">Clear Filters</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="studentStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading students...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="studentStore.hasError" class="error-message">
      <p>{{ studentStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
    </div>

    <!-- Student Table -->
    <div v-else-if="studentStore.hasStudents" class="student-table-container">
      <table class="student-table">
        <thead>
          <tr>
            <th>Student ID</th>
            <th>Name</th>
            <th>Grade</th>
            <th>Age</th>
            <th>Status</th>
            <th>Enrollment Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in studentStore.students" :key="student.id" :class="{ 'row-inactive': !student.is_currently_enrolled }">
            <td>
              <strong>{{ student.student_id }}</strong>
            </td>
            <td>
              <div class="student-name">
                <img v-if="student.photo_url" :src="student.photo_url" :alt="student.student_id" class="student-avatar" />
                <div v-else class="student-avatar-placeholder">
                  {{ getInitials(student.student_id) }}
                </div>
                <span>{{ student.student_id }}</span>
              </div>
            </td>
            <td>
              <span class="badge badge-grade">
                Grade {{ student.grade_level }}
              </span>
            </td>
            <td>{{ student.age || '-' }}</td>
            <td>
              <span class="badge" :class="`badge-${student.status}`">
                {{ formatStatus(student.status) }}
              </span>
            </td>
            <td>{{ formatDate(student.enrollment_date) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="handleViewStudent(student)" class="btn-icon" title="View">
                  👁️
                </button>
                <button @click="handleEditStudent(student)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button
                  v-if="student.can_promote"
                  @click="handlePromoteStudent(student)"
                  class="btn-icon"
                  title="Promote"
                >
                  ⬆️
                </button>
                <button @click="handleDeleteStudent(student)" class="btn-icon btn-danger" title="Delete">
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination">
        <button
          @click="goToPage(studentStore.pagination.page - 1)"
          :disabled="studentStore.pagination.page === 1"
          class="btn-secondary"
        >
          Previous
        </button>

        <span class="pagination-info">
          Page {{ studentStore.pagination.page }} of {{ studentStore.pagination.pages }}
          ({{ studentStore.totalStudents }} total students)
        </span>

        <button
          @click="goToPage(studentStore.pagination.page + 1)"
          :disabled="studentStore.pagination.page >= studentStore.pagination.pages"
          class="btn-secondary"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No students found</p>
      <button @click="handleCreateStudent" class="btn-primary">Create First Student</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStudentStore } from '@/stores/studentStore'
import { useRouter } from 'vue-router'
import type { Student } from '@/types/student'

const studentStore = useStudentStore()
const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  grade_level: '',
  status: '',
  gender: '',
})

/**
 * Load students on component mount
 */
onMounted(async () => {
  await loadStudents()
})

/**
 * Load students with current filters
 */
async function loadStudents() {
  try {
    await studentStore.fetchStudents({
      search: searchQuery.value || undefined,
      grade_level: filters.value.grade_level ? parseInt(filters.value.grade_level) : undefined,
      status: filters.value.status as any || undefined,
      gender: filters.value.gender as any || undefined,
      page: studentStore.pagination.page,
      limit: studentStore.pagination.limit,
    })
  } catch (error) {
    console.error('Failed to load students:', error)
  }
}

/**
 * Handle search with debouncing
 */
let searchTimeout: number | null = null
function handleSearch() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadStudents()
  }, 500)
}

/**
 * Handle filter change
 */
function handleFilterChange() {
  loadStudents()
}

/**
 * Clear all filters
 */
function clearFilters() {
  searchQuery.value = ''
  filters.value.grade_level = ''
  filters.value.status = ''
  filters.value.gender = ''
  loadStudents()
}

/**
 * Retry loading students
 */
function retryLoad() {
  studentStore.clearError()
  loadStudents()
}

/**
 * Navigate to page
 */
function goToPage(page: number) {
  if (page >= 1 && page <= studentStore.pagination.pages) {
    studentStore.pagination.page = page
    loadStudents()
  }
}

/**
 * Handle view student
 */
function handleViewStudent(student: Student) {
  router.push(`/students/${student.id}`)
}

/**
 * Handle edit student
 */
function handleEditStudent(student: Student) {
  router.push(`/students/${student.id}/edit`)
}

/**
 * Handle create student
 */
function handleCreateStudent() {
  router.push('/students/create')
}

/**
 * Handle promote student
 */
async function handlePromoteStudent(student: Student) {
  if (confirm(`Promote ${student.student_id} to Grade ${(student.grade_level || 0) + 1}?`)) {
    try {
      await studentStore.promoteStudent(student.id)
      await loadStudents()
      alert('Student promoted successfully!')
    } catch (error) {
      alert('Failed to promote student')
    }
  }
}

/**
 * Handle delete student
 */
async function handleDeleteStudent(student: Student) {
  if (confirm(`Are you sure you want to delete student ${student.student_id}?`)) {
    try {
      await studentStore.deleteStudent(student.id)
      await loadStudents()
    } catch (error) {
      alert('Failed to delete student')
    }
  }
}

/**
 * Get student initials for avatar placeholder
 */
function getInitials(studentId: string): string {
  return studentId.slice(0, 2).toUpperCase()
}

/**
 * Format status for display
 */
function formatStatus(status: string): string {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.student-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.student-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.student-list-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.student-list-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.student-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.student-table {
  width: 100%;
  border-collapse: collapse;
}

.student-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.student-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
}

.student-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.student-table tbody tr:hover {
  background: #f8f9fa;
}

.row-inactive {
  opacity: 0.6;
}

.student-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.student-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.student-avatar-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #42b883;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-grade { background: #e3f2fd; color: #1976d2; }
.badge-enrolled { background: #e8f5e9; color: #388e3c; }
.badge-graduated { background: #fff3e0; color: #f57c00; }
.badge-transferred { background: #e1f5fe; color: #0277bd; }
.badge-withdrawn { background: #f5f5f5; color: #757575; }
.badge-suspended { background: #ffebee; color: #d32f2f; }

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  padding: 0.25rem 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-icon:hover {
  opacity: 1;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #35a372;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: white;
  color: #42b883;
  border: 1px solid #42b883;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #42b883;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #6c757d;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b883;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 2rem;
  background: #ffebee;
  border-radius: 8px;
  color: #c62828;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  color: #6c757d;
}

.empty-state p {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}
</style>
