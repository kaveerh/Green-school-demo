<template>
  <div class="user-detail">
    <!-- Loading State -->
    <div v-if="userStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading user details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="userStore.hasError" class="error-message">
      <p>{{ userStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
      <button @click="goBack" class="btn-secondary">Go Back</button>
    </div>

    <!-- User Details -->
    <div v-else-if="user" class="user-detail-content">
      <!-- Header -->
      <div class="user-detail-header">
        <button @click="goBack" class="btn-back">← Back to Users</button>
        <div class="header-actions">
          <button @click="handleEdit" class="btn-secondary">Edit User</button>
          <button @click="handleDelete" class="btn-danger">Delete User</button>
        </div>
      </div>

      <!-- User Profile Card -->
      <div class="user-profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.full_name" />
            <div v-else class="avatar-placeholder">
              {{ getInitials(user.full_name) }}
            </div>
          </div>
          <div class="profile-info">
            <h1>{{ user.full_name }}</h1>
            <p class="email">{{ user.email }}</p>
            <div class="badges">
              <span class="badge" :class="`badge-${user.persona}`">
                {{ formatPersona(user.persona) }}
              </span>
              <span class="badge" :class="`badge-${user.status}`">
                {{ formatStatus(user.status) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Bio -->
        <div v-if="user.bio" class="profile-bio">
          <h3>Bio</h3>
          <p>{{ user.bio }}</p>
        </div>

        <!-- Contact Information -->
        <div class="profile-section">
          <h3>Contact Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Email</label>
              <p>{{ user.email }}</p>
            </div>
            <div class="info-item" v-if="user.phone">
              <label>Phone</label>
              <p>{{ user.phone }}</p>
            </div>
          </div>
        </div>

        <!-- Account Information -->
        <div class="profile-section">
          <h3>Account Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>User ID</label>
              <p class="monospace">{{ user.id }}</p>
            </div>
            <div class="info-item">
              <label>School ID</label>
              <p class="monospace">{{ user.school_id }}</p>
            </div>
            <div class="info-item">
              <label>Persona</label>
              <p>{{ formatPersona(user.persona) }}</p>
            </div>
            <div class="info-item">
              <label>Status</label>
              <p>
                <span class="badge" :class="`badge-${user.status}`">
                  {{ formatStatus(user.status) }}
                </span>
              </p>
            </div>
            <div class="info-item">
              <label>Active</label>
              <p>{{ user.is_active ? 'Yes' : 'No' }}</p>
            </div>
            <div class="info-item" v-if="user.last_login_at">
              <label>Last Login</label>
              <p>{{ formatDateTime(user.last_login_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Timestamps -->
        <div class="profile-section">
          <h3>Timestamps</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Created</label>
              <p>{{ formatDateTime(user.created_at) }}</p>
            </div>
            <div class="info-item">
              <label>Last Updated</label>
              <p>{{ formatDateTime(user.updated_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Metadata -->
        <div v-if="hasMetadata" class="profile-section">
          <h3>Additional Metadata</h3>
          <pre class="metadata-json">{{ JSON.stringify(user.metadata, null, 2) }}</pre>
        </div>

        <!-- Actions -->
        <div class="profile-actions">
          <button @click="handleChangeStatus" class="btn-secondary">Change Status</button>
          <button @click="handleChangePersona" class="btn-secondary">Change Persona</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import type { User } from '@/types/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const userId = computed(() => route.params.id as string)
const user = computed(() => userStore.selectedUser)
const hasMetadata = computed(() => {
  if (!user.value || !user.value.metadata) return false
  return Object.keys(user.value.metadata).length > 0
})

/**
 * Load user on component mount
 */
onMounted(async () => {
  await loadUser()
})

/**
 * Load user details
 */
async function loadUser() {
  try {
    await userStore.fetchUserById(userId.value)
  } catch (error) {
    console.error('Failed to load user:', error)
  }
}

/**
 * Retry loading user
 */
function retryLoad() {
  userStore.clearError()
  loadUser()
}

/**
 * Navigate back to user list
 */
function goBack() {
  router.push('/users')
}

/**
 * Handle edit user
 */
function handleEdit() {
  router.push(`/users/${userId.value}/edit`)
}

/**
 * Handle delete user
 */
async function handleDelete() {
  if (!user.value) return

  if (confirm(`Are you sure you want to delete ${user.value.full_name}?`)) {
    try {
      await userStore.deleteUser(userId.value)
      router.push('/users')
    } catch (error) {
      alert('Failed to delete user')
    }
  }
}

/**
 * Handle change status
 */
function handleChangeStatus() {
  if (!user.value) return

  const statuses = ['active', 'inactive', 'suspended']
  const currentStatus = user.value.status
  const otherStatuses = statuses.filter(s => s !== currentStatus)

  const newStatus = prompt(
    `Current status: ${currentStatus}\n\nEnter new status (${otherStatuses.join(', ')}):`
  )

  if (newStatus && statuses.includes(newStatus)) {
    changeStatus(newStatus as any)
  } else if (newStatus) {
    alert('Invalid status. Must be: active, inactive, or suspended')
  }
}

/**
 * Change user status
 */
async function changeStatus(status: 'active' | 'inactive' | 'suspended') {
  try {
    await userStore.changeUserStatus(userId.value, status)
    await loadUser()
  } catch (error) {
    alert('Failed to change user status')
  }
}

/**
 * Handle change persona
 */
function handleChangePersona() {
  if (!user.value) return

  const personas = ['administrator', 'teacher', 'student', 'parent', 'vendor']
  const currentPersona = user.value.persona
  const otherPersonas = personas.filter(p => p !== currentPersona)

  const newPersona = prompt(
    `Current persona: ${currentPersona}\n\nEnter new persona (${otherPersonas.join(', ')}):`
  )

  if (newPersona && personas.includes(newPersona)) {
    changePersona(newPersona as any)
  } else if (newPersona) {
    alert('Invalid persona. Must be: administrator, teacher, student, parent, or vendor')
  }
}

/**
 * Change user persona
 */
async function changePersona(persona: 'administrator' | 'teacher' | 'student' | 'parent' | 'vendor') {
  try {
    await userStore.changeUserPersona(userId.value, persona)
    await loadUser()
  } catch (error) {
    alert('Failed to change user persona')
  }
}

/**
 * Get user initials
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
 * Format datetime for display
 */
function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.user-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.user-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #42b883;
}

.btn-back:hover {
  background: #f8f9fa;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.user-profile-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  display: flex;
  gap: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #42b883 0%, #35a372 100%);
  color: white;
}

.profile-avatar img,
.avatar-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  background: white;
  color: #42b883;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 600;
}

.profile-info h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
}

.profile-info .email {
  margin: 0 0 1rem 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.badges {
  display: flex;
  gap: 0.5rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-administrator { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-teacher { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-student { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-parent { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-vendor { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-active { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-inactive { background: rgba(0, 0, 0, 0.2); color: white; }
.badge-suspended { background: rgba(211, 47, 47, 0.5); color: white; }

.profile-bio {
  padding: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.profile-section {
  padding: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.profile-section:last-of-type {
  border-bottom: none;
}

.profile-section h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-item label {
  display: block;
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.info-item p {
  margin: 0;
  color: #2c3e50;
}

.monospace {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.metadata-json {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.85rem;
}

.profile-actions {
  padding: 2rem;
  display: flex;
  gap: 1rem;
  background: #f8f9fa;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #42b883;
  border: 1px solid #42b883;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #42b883;
  color: white;
}

.btn-danger {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #dc3545;
  border: 1px solid #dc3545;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: #dc3545;
  color: white;
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

.error-message button {
  margin-top: 1rem;
  margin-right: 0.5rem;
}
</style>
