<template>
  <div class="teacher-list">
    <!-- Header -->
    <div class="teacher-list-header">
      <h2>Teacher Management</h2>
      <button @click="handleCreateTeacher" class="btn-primary">
        + Create Teacher
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="teacher-list-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search teachers by employee ID, department, or name..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <select v-model="filters.status" @change="handleFilterChange" class="filter-select">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="on_leave">On Leave</option>
          <option value="terminated">Terminated</option>
        </select>

        <select v-model="filters.employment_type" @change="handleFilterChange" class="filter-select">
          <option value="">All Employment Types</option>
          <option value="full-time">Full-time</option>
          <option value="part-time">Part-time</option>
          <option value="contract">Contract</option>
          <option value="substitute">Substitute</option>
        </select>

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

        <input
          v-model="filters.department"
          type="text"
          placeholder="Department..."
          @input="handleFilterChange"
          class="filter-input"
        />

        <button @click="clearFilters" class="btn-secondary">Clear Filters</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="teacherStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading teachers...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="teacherStore.hasError" class="error-message">
      <p>{{ teacherStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
    </div>

    <!-- Teacher Table -->
    <div v-else-if="teacherStore.hasTeachers" class="teacher-table-container">
      <table class="teacher-table">
        <thead>
          <tr>
            <th>Employee ID</th>
            <th>Name</th>
            <th>Department</th>
            <th>Grade Levels</th>
            <th>Employment Type</th>
            <th>Status</th>
            <th>Years of Service</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="teacher in teacherStore.teachers"
            :key="teacher.id"
            :class="{ 'row-inactive': !teacher.is_currently_employed }"
          >
            <td>
              <strong>{{ teacher.employee_id }}</strong>
            </td>
            <td>
              <div class="teacher-name">
                <div class="teacher-avatar-placeholder">
                  {{ getInitials(teacher.user?.full_name || 'TBD') }}
                </div>
                <div>
                  <div>{{ teacher.user?.full_name || 'Unknown' }}</div>
                  <div class="teacher-title">{{ teacher.job_title || 'Teacher' }}</div>
                </div>
              </div>
            </td>
            <td>{{ teacher.department || '-' }}</td>
            <td>
              <div class="grade-badges">
                <span
                  v-for="grade in teacher.grade_levels"
                  :key="grade"
                  class="grade-badge"
                >
                  Grade {{ grade }}
                </span>
                <span v-if="!teacher.grade_levels?.length" class="text-muted">None</span>
              </div>
            </td>
            <td>
              <span class="badge" :class="`badge-${teacher.employment_type}`">
                {{ formatEmploymentType(teacher.employment_type) }}
              </span>
            </td>
            <td>
              <span class="badge" :class="`badge-status-${teacher.status}`">
                {{ formatStatus(teacher.status) }}
              </span>
              <span
                v-if="teacher.is_certification_valid === false"
                class="cert-warning"
                title="Certification expired"
              >
                ⚠️
              </span>
            </td>
            <td>{{ teacher.years_of_service || 0 }} years</td>
            <td>
              <div class="action-buttons">
                <button @click="handleViewTeacher(teacher)" class="btn-icon" title="View">
                  👁️
                </button>
                <button @click="handleEditTeacher(teacher)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="handleDeleteTeacher(teacher)" class="btn-icon btn-danger" title="Delete">
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
          @click="goToPage(teacherStore.pagination.page - 1)"
          :disabled="teacherStore.pagination.page === 1"
          class="btn-secondary"
        >
          Previous
        </button>

        <span class="pagination-info">
          Page {{ teacherStore.pagination.page }} of {{ teacherStore.pagination.pages }}
          ({{ teacherStore.totalTeachers }} total teachers)
        </span>

        <button
          @click="goToPage(teacherStore.pagination.page + 1)"
          :disabled="teacherStore.pagination.page >= teacherStore.pagination.pages"
          class="btn-secondary"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No teachers found</p>
      <button @click="handleCreateTeacher" class="btn-primary">Create First Teacher</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacherStore'
import { useRouter } from 'vue-router'
import type { Teacher } from '@/types'

const teacherStore = useTeacherStore()
const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  status: '',
  employment_type: '',
  department: '',
  grade_level: '',
})

/**
 * Load teachers on component mount
 */
onMounted(async () => {
  await loadTeachers()
})

/**
 * Load teachers with current filters
 */
async function loadTeachers() {
  try {
    await teacherStore.fetchTeachers({
      search: searchQuery.value || undefined,
      status: filters.value.status as any || undefined,
      employment_type: filters.value.employment_type as any || undefined,
      department: filters.value.department || undefined,
      grade_level: filters.value.grade_level ? parseInt(filters.value.grade_level) : undefined,
      page: teacherStore.pagination.page,
      limit: teacherStore.pagination.limit,
    })
  } catch (error) {
    console.error('Failed to load teachers:', error)
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
    loadTeachers()
  }, 500)
}

/**
 * Handle filter change
 */
function handleFilterChange() {
  loadTeachers()
}

/**
 * Clear all filters
 */
function clearFilters() {
  searchQuery.value = ''
  filters.value.status = ''
  filters.value.employment_type = ''
  filters.value.department = ''
  filters.value.grade_level = ''
  loadTeachers()
}

/**
 * Retry loading teachers
 */
function retryLoad() {
  teacherStore.clearError()
  loadTeachers()
}

/**
 * Navigate to page
 */
function goToPage(page: number) {
  if (page >= 1 && page <= teacherStore.pagination.pages) {
    teacherStore.pagination.page = page
    loadTeachers()
  }
}

/**
 * Handle view teacher
 */
function handleViewTeacher(teacher: Teacher) {
  router.push(`/teachers/${teacher.id}`)
}

/**
 * Handle edit teacher
 */
function handleEditTeacher(teacher: Teacher) {
  router.push(`/teachers/${teacher.id}/edit`)
}

/**
 * Handle create teacher
 */
function handleCreateTeacher() {
  router.push('/teachers/create')
}

/**
 * Handle delete teacher
 */
async function handleDeleteTeacher(teacher: Teacher) {
  const teacherName = teacher.user?.full_name || teacher.employee_id
  if (confirm(`Are you sure you want to delete teacher ${teacherName}?`)) {
    try {
      await teacherStore.deleteTeacher(teacher.id)
      await loadTeachers()
    } catch (error) {
      alert('Failed to delete teacher')
    }
  }
}

/**
 * Get teacher initials for avatar placeholder
 */
function getInitials(fullName: string): string {
  const names = fullName.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

/**
 * Format employment type for display
 */
function formatEmploymentType(type: string | undefined): string {
  if (!type) return 'Unknown'
  return type.split('-').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join('-')
}

/**
 * Format status for display
 */
function formatStatus(status: string | undefined): string {
  if (!status) return 'Unknown'
  return status.split('_').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}
</script>

<style scoped>
.teacher-list {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.teacher-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.teacher-list-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.teacher-list-filters {
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
  flex-wrap: wrap;
}

.filter-select, .filter-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.filter-input {
  width: 150px;
}

.teacher-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.teacher-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.teacher-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.teacher-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.teacher-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.teacher-table tbody tr:hover {
  background: #f8f9fa;
}

.row-inactive {
  opacity: 0.6;
}

.teacher-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.teacher-avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #7b1fa2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
  flex-shrink: 0;
}

.teacher-title {
  font-size: 0.85rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.grade-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.grade-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
}

.text-muted {
  color: #6c757d;
  font-style: italic;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
}

.badge-full-time { background: #e8f5e9; color: #388e3c; }
.badge-part-time { background: #fff3e0; color: #f57c00; }
.badge-contract { background: #e3f2fd; color: #1976d2; }
.badge-substitute { background: #f3e5f5; color: #7b1fa2; }

.badge-status-active { background: #e8f5e9; color: #388e3c; }
.badge-status-inactive { background: #f5f5f5; color: #757575; }
.badge-status-on_leave { background: #fff3e0; color: #f57c00; }
.badge-status-terminated { background: #ffebee; color: #d32f2f; }

.cert-warning {
  margin-left: 0.5rem;
  cursor: help;
}

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
