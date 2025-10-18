<template>
  <div class="subject-list-container">
    <!-- Header -->
    <div class="header">
      <h1 class="title">Subjects</h1>
      <button class="btn btn-primary" @click="goToCreate">
        + New Subject
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="search-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by code or name..."
          class="search-input"
          @input="handleSearch"
        />
        <button v-if="searchQuery" class="clear-btn" @click="clearSearch">×</button>
      </div>

      <div class="filters">
        <select v-model="filters.category" class="filter-select" @change="applyFilters">
          <option value="">All Categories</option>
          <option value="core">Core</option>
          <option value="elective">Elective</option>
          <option value="enrichment">Enrichment</option>
          <option value="remedial">Remedial</option>
          <option value="other">Other</option>
        </select>

        <select v-model="filters.subject_type" class="filter-select" @change="applyFilters">
          <option value="">All Types</option>
          <option value="academic">Academic</option>
          <option value="arts">Arts</option>
          <option value="physical">Physical</option>
          <option value="technical">Technical</option>
          <option value="other">Other</option>
        </select>

        <label class="checkbox-filter">
          <input v-model="filters.is_active" type="checkbox" @change="applyFilters" />
          Active Only
        </label>

        <label class="checkbox-filter">
          <input v-model="filters.is_required" type="checkbox" @change="applyFilters" />
          Required Only
        </label>
      </div>
    </div>

    <!-- Statistics -->
    <div v-if="statistics" class="statistics-summary">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_subjects }}</div>
        <div class="stat-label">Total Subjects</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.active_subjects }}</div>
        <div class="stat-label">Active</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.required_subjects }}</div>
        <div class="stat-label">Required</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.by_category.core || 0 }}</div>
        <div class="stat-label">Core Subjects</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="subjectStore.isLoading" class="loading">
      Loading subjects...
    </div>

    <!-- Error State -->
    <div v-else-if="subjectStore.error" class="error">
      {{ subjectStore.error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="subjectStore.subjects.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h2>No Subjects Found</h2>
      <p>Create your first subject to get started.</p>
      <button class="btn btn-primary" @click="goToCreate">
        + Create Subject
      </button>
    </div>

    <!-- Subjects Table -->
    <div v-else class="table-container">
      <table class="subjects-table">
        <thead>
          <tr>
            <th>Icon</th>
            <th>Code</th>
            <th>Name</th>
            <th>Category</th>
            <th>Type</th>
            <th>Grade Levels</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subject in subjectStore.subjects" :key="subject.id" class="subject-row">
            <td>
              <div
                class="subject-icon"
                :style="{ backgroundColor: subject.color || '#757575' }"
              >
                {{ subject.icon || '📝' }}
              </div>
            </td>
            <td>
              <span class="subject-code">{{ subject.code }}</span>
            </td>
            <td>
              <div class="subject-name-cell">
                <div class="subject-name">{{ subject.name }}</div>
                <div v-if="subject.description" class="subject-description">
                  {{ truncateText(subject.description, 60) }}
                </div>
              </div>
            </td>
            <td>
              <span
                class="badge badge-category"
                :style="{ backgroundColor: getCategoryColor(subject.category) }"
              >
                {{ getSubjectCategoryLabel(subject.category) }}
              </span>
            </td>
            <td>
              <span v-if="subject.subject_type" class="subject-type">
                {{ getSubjectTypeLabel(subject.subject_type) }}
              </span>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <span class="grade-levels">{{ formatGradeLevels(subject.grade_levels) }}</span>
            </td>
            <td>
              <span
                class="badge"
                :class="subject.is_active ? 'badge-success' : 'badge-inactive'"
              >
                {{ subject.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span v-if="subject.is_required" class="badge badge-required">Required</span>
            </td>
            <td>
              <div class="actions">
                <button
                  class="action-btn"
                  title="View"
                  @click="viewSubject(subject.id)"
                >
                  👁️
                </button>
                <button
                  class="action-btn"
                  title="Edit"
                  @click="editSubject(subject.id)"
                >
                  ✏️
                </button>
                <button
                  class="action-btn"
                  title="Toggle Status"
                  @click="toggleSubjectStatus(subject.id)"
                >
                  {{ subject.is_active ? '🔴' : '🟢' }}
                </button>
                <button
                  class="action-btn action-btn-danger"
                  title="Delete"
                  @click="confirmDelete(subject)"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="subjectStore.subjects.length > 0" class="pagination">
      <button
        class="btn btn-secondary"
        :disabled="!subjectStore.hasPreviousPage"
        @click="subjectStore.previousPage()"
      >
        ← Previous
      </button>
      <span class="page-info">
        Page {{ subjectStore.currentPage }} of {{ subjectStore.totalPages }}
        ({{ subjectStore.totalSubjects }} total)
      </span>
      <button
        class="btn btn-secondary"
        :disabled="!subjectStore.hasNextPage"
        @click="subjectStore.nextPage()"
      >
        Next →
      </button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deleteConfirmation" class="modal-overlay" @click="deleteConfirmation = null">
      <div class="modal-content" @click.stop>
        <h3>Confirm Delete</h3>
        <p>
          Are you sure you want to delete subject <strong>{{ deleteConfirmation.name }}</strong> ({{ deleteConfirmation.code }})?
        </p>
        <p class="warning-text">This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="deleteConfirmation = null">
            Cancel
          </button>
          <button class="btn btn-danger" @click="executeDelete">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSubjectStore } from '@/stores/subjectStore'
import {
  getSubjectCategoryLabel,
  getSubjectTypeLabel,
  formatGradeLevels,
  getCategoryColor
} from '@/types/subject'
import type { Subject, SubjectStatistics } from '@/types/subject'

const router = useRouter()
const subjectStore = useSubjectStore()

// State
const searchQuery = ref('')
const filters = ref({
  category: '',
  subject_type: '',
  is_active: false,
  is_required: false
})
const statistics = ref<SubjectStatistics | null>(null)
const deleteConfirmation = ref<Subject | null>(null)

// Methods
async function loadSubjects() {
  const schoolId = localStorage.getItem('current_school_id') || '60da2256-81fc-4ca5-bf6b-467b8d371c61'

  const params: any = { school_id: schoolId }

  if (filters.value.category) params.category = filters.value.category
  if (filters.value.subject_type) params.subject_type = filters.value.subject_type
  if (filters.value.is_active) params.is_active = true
  if (filters.value.is_required) params.is_required = true

  await subjectStore.fetchSubjects(params)
}

async function loadStatistics() {
  const schoolId = localStorage.getItem('current_school_id') || '60da2256-81fc-4ca5-bf6b-467b8d371c61'
  statistics.value = await subjectStore.fetchStatistics(schoolId)
}

async function handleSearch() {
  if (searchQuery.value.trim().length >= 2) {
    const schoolId = localStorage.getItem('current_school_id') || '60da2256-81fc-4ca5-bf6b-467b8d371c61'
    await subjectStore.searchSubjects(searchQuery.value.trim(), { school_id: schoolId })
  } else if (searchQuery.value.trim().length === 0) {
    await loadSubjects()
  }
}

function clearSearch() {
  searchQuery.value = ''
  loadSubjects()
}

function applyFilters() {
  loadSubjects()
}

function goToCreate() {
  router.push('/subjects/create')
}

function viewSubject(id: string) {
  router.push(`/subjects/${id}`)
}

function editSubject(id: string) {
  router.push(`/subjects/${id}/edit`)
}

async function toggleSubjectStatus(id: string) {
  try {
    await subjectStore.toggleStatus(id)
    await loadStatistics()
  } catch (err) {
    console.error('Failed to toggle status:', err)
  }
}

function confirmDelete(subject: Subject) {
  deleteConfirmation.value = subject
}

async function executeDelete() {
  if (!deleteConfirmation.value) return

  try {
    await subjectStore.deleteSubject(deleteConfirmation.value.id)
    deleteConfirmation.value = null
    await loadStatistics()
  } catch (err) {
    console.error('Failed to delete subject:', err)
  }
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Lifecycle
onMounted(async () => {
  await loadSubjects()
  await loadStatistics()
})
</script>

<style scoped>
.subject-list-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.search-filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.checkbox-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.statistics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #42b883;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.loading, .error, .empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.subjects-table {
  width: 100%;
  border-collapse: collapse;
}

.subjects-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #e0e0e0;
}

.subjects-table td {
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.subject-row:hover {
  background: #f8f9fa;
}

.subject-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.subject-code {
  font-weight: 600;
  color: #2c3e50;
  font-family: monospace;
}

.subject-name-cell {
  max-width: 300px;
}

.subject-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.subject-description {
  font-size: 0.85rem;
  color: #666;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  display: inline-block;
  margin-right: 0.5rem;
}

.badge-category {
  color: white;
}

.badge-success {
  background: #4CAF50;
  color: white;
}

.badge-inactive {
  background: #9E9E9E;
  color: white;
}

.badge-required {
  background: #FF9800;
  color: white;
}

.grade-levels {
  font-size: 0.9rem;
  color: #666;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #f0f0f0;
}

.action-btn-danger:hover {
  background: #ffebee;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  color: #666;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-primary:hover {
  background: #35a372;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #f44336;
  color: white;
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
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.warning-text {
  color: #f44336;
  font-size: 0.9rem;
}

.text-muted {
  color: #999;
}
</style>
