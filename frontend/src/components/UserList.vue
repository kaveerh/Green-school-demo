<template>
  <div class="user-list">
    <!-- Header -->
    <div class="user-list-header">
      <h2>User Management</h2>
      <button @click="handleCreateUser" class="btn-primary">
        + Create User
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="user-list-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search users by name or email..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="filter-row">
        <select v-model="filters.persona" @change="handleFilterChange" class="filter-select">
          <option value="">All Personas</option>
          <option value="administrator">Administrator</option>
          <option value="teacher">Teacher</option>
          <option value="student">Student</option>
          <option value="parent">Parent</option>
          <option value="vendor">Vendor</option>
        </select>

        <select v-model="filters.status" @change="handleFilterChange" class="filter-select">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="suspended">Suspended</option>
        </select>

        <button @click="clearFilters" class="btn-secondary">Clear Filters</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="userStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading users...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="userStore.hasError" class="error-message">
      <p>{{ userStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
    </div>

    <!-- User Table -->
    <div v-else-if="userStore.hasUsers" class="user-table-container">
      <table class="user-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Persona</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in userStore.users" :key="user.id" :class="{ 'row-inactive': !user.is_active }">
            <td>
              <div class="user-name">
                <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.full_name" class="user-avatar" />
                <div v-else class="user-avatar-placeholder">
                  {{ getInitials(user.full_name) }}
                </div>
                <span>{{ user.full_name }}</span>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="`badge-${user.persona}`">
                {{ formatPersona(user.persona) }}
              </span>
            </td>
            <td>
              <span class="badge" :class="`badge-${user.status}`">
                {{ formatStatus(user.status) }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="handleViewUser(user)" class="btn-icon" title="View">
                  👁️
                </button>
                <button @click="handleEditUser(user)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button @click="handleDeleteUser(user)" class="btn-icon btn-danger" title="Delete">
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
          @click="goToPage(userStore.pagination.page - 1)"
          :disabled="userStore.pagination.page === 1"
          class="btn-secondary"
        >
          Previous
        </button>

        <span class="pagination-info">
          Page {{ userStore.pagination.page }} of {{ userStore.pagination.pages }}
          ({{ userStore.totalUsers }} total users)
        </span>

        <button
          @click="goToPage(userStore.pagination.page + 1)"
          :disabled="userStore.pagination.page >= userStore.pagination.pages"
          class="btn-secondary"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <p>No users found</p>
      <button @click="handleCreateUser" class="btn-primary">Create First User</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { useRouter } from 'vue-router'
import type { User } from '@/types/user'

const userStore = useUserStore()
const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  persona: '',
  status: '',
})

/**
 * Load users on component mount
 */
onMounted(async () => {
  await loadUsers()
})

/**
 * Load users with current filters
 */
async function loadUsers() {
  try {
    await userStore.fetchUsers({
      search: searchQuery.value || undefined,
      persona: filters.value.persona as any || undefined,
      status: filters.value.status as any || undefined,
      page: userStore.pagination.page,
      limit: userStore.pagination.limit,
    })
  } catch (error) {
    console.error('Failed to load users:', error)
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
    loadUsers()
  }, 500)
}

/**
 * Handle filter change
 */
function handleFilterChange() {
  loadUsers()
}

/**
 * Clear all filters
 */
function clearFilters() {
  searchQuery.value = ''
  filters.value.persona = ''
  filters.value.status = ''
  loadUsers()
}

/**
 * Retry loading users
 */
function retryLoad() {
  userStore.clearError()
  loadUsers()
}

/**
 * Navigate to page
 */
function goToPage(page: number) {
  if (page >= 1 && page <= userStore.pagination.pages) {
    userStore.pagination.page = page
    loadUsers()
  }
}

/**
 * Handle view user
 */
function handleViewUser(user: User) {
  router.push(`/users/${user.id}`)
}

/**
 * Handle edit user
 */
function handleEditUser(user: User) {
  router.push(`/users/${user.id}/edit`)
}

/**
 * Handle create user
 */
function handleCreateUser() {
  router.push('/users/create')
}

/**
 * Handle delete user
 */
async function handleDeleteUser(user: User) {
  if (confirm(`Are you sure you want to delete ${user.full_name}?`)) {
    try {
      await userStore.deleteUser(user.id)
      await loadUsers()
    } catch (error) {
      alert('Failed to delete user')
    }
  }
}

/**
 * Get user initials for avatar placeholder
 */
function getInitials(fullName: string): string {
  const names = fullName.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

/**
 * Format persona for display
 */
function formatPersona(persona: string): string {
  return persona.charAt(0).toUpperCase() + persona.slice(1)
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
.user-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.user-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.user-list-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.user-list-filters {
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

.user-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.user-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
}

.user-table td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.user-table tbody tr:hover {
  background: #f8f9fa;
}

.row-inactive {
  opacity: 0.6;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-avatar-placeholder {
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

.badge-administrator { background: #e3f2fd; color: #1976d2; }
.badge-teacher { background: #f3e5f5; color: #7b1fa2; }
.badge-student { background: #e8f5e9; color: #388e3c; }
.badge-parent { background: #fff3e0; color: #f57c00; }
.badge-vendor { background: #fce4ec; color: #c2185b; }
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
