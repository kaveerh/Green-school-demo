<template>
  <div class="school-list">
    <!-- Header -->
    <div class="school-list-header">
      <h2>School Management</h2>
      <button @click="handleCreateSchool" class="btn-primary">
        + Create School
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="school-list-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search schools by name, city, or email..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <select v-model="filters.status" @change="handleFilterChange" class="filter-select">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>

        <input
          v-model="filters.city"
          type="text"
          placeholder="Filter by city"
          @input="handleFilterChange"
          class="filter-input"
        />

        <input
          v-model="filters.state"
          type="text"
          placeholder="Filter by state"
          @input="handleFilterChange"
          class="filter-input"
        />

        <button @click="clearFilters" class="btn-secondary">Clear Filters</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="schoolStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading schools...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="schoolStore.hasError" class="error-message">
      <p>{{ schoolStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
    </div>

    <!-- School Table -->
    <div v-else-if="schoolStore.hasSchools" class="school-table-container">
      <table class="school-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Location</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="school in schoolStore.schools" :key="school.id" :class="{ 'row-inactive': !school.is_active }">
            <td>
              <div class="school-name">
                <img v-if="school.logo_url" :src="school.logo_url" :alt="school.name" class="school-logo" />
                <div v-else class="school-logo-placeholder">
                  {{ getInitials(school.name) }}
                </div>
                <div>
                  <div class="name-text">{{ school.name }}</div>
                  <div class="slug-text">{{ school.slug }}</div>
                </div>
              </div>
            </td>
            <td>
              <div class="location-info">
                <div v-if="school.city || school.state">{{ school.city }}<span v-if="school.city && school.state">, </span>{{ school.state }}</div>
                <div v-if="school.country" class="text-muted">{{ school.country }}</div>
              </div>
            </td>
            <td>
              <div class="contact-info">
                <div v-if="school.email">📧 {{ school.email }}</div>
                <div v-if="school.phone">📞 {{ school.phone }}</div>
              </div>
            </td>
            <td>
              <span class="badge" :class="`badge-${school.status}`">
                {{ formatStatus(school.status) }}
              </span>
            </td>
            <td>{{ formatDate(school.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="handleViewSchool(school)" class="btn-icon" title="View">
                  👁️
                </button>
                <button @click="handleEditSchool(school)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="handleDeleteSchool(school)" class="btn-icon btn-danger" title="Delete">
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
          @click="goToPage(schoolStore.pagination.page - 1)"
          :disabled="schoolStore.pagination.page === 1"
          class="btn-secondary"
        >
          Previous
        </button>

        <span class="pagination-info">
          Page {{ schoolStore.pagination.page }} of {{ schoolStore.pagination.pages }}
          ({{ schoolStore.totalSchools }} total schools)
        </span>

        <button
          @click="goToPage(schoolStore.pagination.page + 1)"
          :disabled="schoolStore.pagination.page >= schoolStore.pagination.pages"
          class="btn-secondary"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No schools found</p>
      <button @click="handleCreateSchool" class="btn-primary">Create First School</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSchoolStore } from '@/stores/schoolStore'
import { useRouter } from 'vue-router'
import type { School } from '@/types/school'

const schoolStore = useSchoolStore()
const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  status: '',
  city: '',
  state: '',
})

/**
 * Load schools on component mount
 */
onMounted(async () => {
  await loadSchools()
})

/**
 * Load schools with current filters
 */
async function loadSchools() {
  try {
    await schoolStore.fetchSchools({
      search: searchQuery.value || undefined,
      status: filters.value.status as any || undefined,
      city: filters.value.city || undefined,
      state: filters.value.state || undefined,
      page: schoolStore.pagination.page,
      limit: schoolStore.pagination.limit,
    })
  } catch (error) {
    console.error('Failed to load schools:', error)
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
    loadSchools()
  }, 500)
}

/**
 * Handle filter change with debouncing
 */
let filterTimeout: number | null = null
function handleFilterChange() {
  if (filterTimeout) {
    clearTimeout(filterTimeout)
  }
  filterTimeout = setTimeout(() => {
    loadSchools()
  }, 300)
}

/**
 * Clear all filters
 */
function clearFilters() {
  searchQuery.value = ''
  filters.value.status = ''
  filters.value.city = ''
  filters.value.state = ''
  loadSchools()
}

/**
 * Retry loading schools
 */
function retryLoad() {
  schoolStore.clearError()
  loadSchools()
}

/**
 * Navigate to page
 */
function goToPage(page: number) {
  if (page >= 1 && page <= schoolStore.pagination.pages) {
    schoolStore.pagination.page = page
    loadSchools()
  }
}

/**
 * Handle view school
 */
function handleViewSchool(school: School) {
  router.push(`/schools/${school.id}`)
}

/**
 * Handle edit school
 */
function handleEditSchool(school: School) {
  router.push(`/schools/${school.id}/edit`)
}

/**
 * Handle create school
 */
function handleCreateSchool() {
  router.push('/schools/create')
}

/**
 * Handle delete school
 */
async function handleDeleteSchool(school: School) {
  if (confirm(`Are you sure you want to delete ${school.name}? This action cannot be undone.`)) {
    try {
      await schoolStore.deleteSchool(school.id)
      await loadSchools()
    } catch (error) {
      alert('Failed to delete school')
    }
  }
}

/**
 * Get school initials for logo placeholder
 */
function getInitials(name: string): string {
  const words = name.split(' ')
  return words.map(w => w[0]).join('').toUpperCase().slice(0, 2)
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
.school-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.school-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.school-list-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.school-list-filters {
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

.filter-select,
.filter-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  min-width: 150px;
}

.school-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.school-table {
  width: 100%;
  border-collapse: collapse;
}

.school-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.school-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
}

.school-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.school-table tbody tr:hover {
  background: #f8f9fa;
}

.row-inactive {
  opacity: 0.6;
}

.school-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.school-logo {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  object-fit: cover;
}

.school-logo-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  background: #42b883;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
}

.name-text {
  font-weight: 500;
  color: #2c3e50;
}

.slug-text {
  font-size: 0.85rem;
  color: #6c757d;
}

.location-info,
.contact-info {
  font-size: 0.9rem;
}

.location-info div,
.contact-info div {
  margin-bottom: 0.25rem;
}

.text-muted {
  color: #6c757d;
  font-size: 0.85rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-active { background: #e8f5e9; color: #388e3c; }
.badge-inactive { background: #f5f5f5; color: #757575; }
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
