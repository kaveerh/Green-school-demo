<template>
  <div class="school-detail">
    <!-- Loading State -->
    <div v-if="schoolStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading school details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="schoolStore.hasError" class="error-message">
      <p>{{ schoolStore.error }}</p>
      <button @click="retryLoad" class="btn-secondary">Retry</button>
      <button @click="goBack" class="btn-secondary">Go Back</button>
    </div>

    <!-- School Details -->
    <div v-else-if="school" class="school-detail-content">
      <!-- Header -->
      <div class="school-detail-header">
        <button @click="goBack" class="btn-back">← Back to Schools</button>
        <div class="header-actions">
          <button @click="handleEdit" class="btn-secondary">Edit School</button>
          <button @click="handleDelete" class="btn-danger">Delete School</button>
        </div>
      </div>

      <!-- School Profile Card -->
      <div class="school-profile-card">
        <div class="profile-header">
          <div class="profile-logo">
            <img v-if="school.logo_url" :src="school.logo_url" :alt="school.name" />
            <div v-else class="logo-placeholder">
              {{ getInitials(school.name) }}
            </div>
          </div>
          <div class="profile-info">
            <h1>{{ school.name }}</h1>
            <p class="slug">{{ school.slug }}</p>
            <div class="badges">
              <span class="badge" :class="`badge-${school.status}`">
                {{ formatStatus(school.status) }}
              </span>
              <span v-if="school.is_active" class="badge badge-active">Active</span>
            </div>
          </div>
        </div>

        <!-- Address Information -->
        <div v-if="hasAddress" class="profile-section">
          <h3>📍 Address</h3>
          <div class="address-block">
            <p v-if="school.address_line1">{{ school.address_line1 }}</p>
            <p v-if="school.address_line2">{{ school.address_line2 }}</p>
            <p v-if="school.city || school.state || school.postal_code">
              {{ school.city }}<span v-if="school.city && school.state">, </span>{{ school.state }} {{ school.postal_code }}
            </p>
            <p v-if="school.country">{{ school.country }}</p>
            <p v-if="school.full_address" class="text-muted">{{ school.full_address }}</p>
          </div>
        </div>

        <!-- Contact Information -->
        <div v-if="hasContact" class="profile-section">
          <h3>📞 Contact Information</h3>
          <div class="info-grid">
            <div class="info-item" v-if="school.email">
              <label>Email</label>
              <p><a :href="`mailto:${school.email}`">{{ school.email }}</a></p>
            </div>
            <div class="info-item" v-if="school.phone">
              <label>Phone</label>
              <p><a :href="`tel:${school.phone}`">{{ school.phone }}</a></p>
            </div>
          </div>
        </div>

        <!-- Online Presence -->
        <div v-if="hasOnlinePresence" class="profile-section">
          <h3>🌐 Online Presence</h3>
          <div class="info-grid">
            <div class="info-item" v-if="school.website_url">
              <label>Website</label>
              <p><a :href="school.website_url" target="_blank" rel="noopener">{{ school.website_url }}</a></p>
            </div>
            <div class="info-item" v-if="school.facebook_url">
              <label>Facebook</label>
              <p><a :href="school.facebook_url" target="_blank" rel="noopener">View Profile</a></p>
            </div>
            <div class="info-item" v-if="school.twitter_url">
              <label>Twitter</label>
              <p><a :href="school.twitter_url" target="_blank" rel="noopener">View Profile</a></p>
            </div>
            <div class="info-item" v-if="school.instagram_url">
              <label>Instagram</label>
              <p><a :href="school.instagram_url" target="_blank" rel="noopener">View Profile</a></p>
            </div>
          </div>
        </div>

        <!-- Settings & Configuration -->
        <div class="profile-section">
          <h3>⚙️ Settings & Configuration</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Timezone</label>
              <p>{{ school.timezone }}</p>
            </div>
            <div class="info-item">
              <label>Locale</label>
              <p>{{ school.locale }}</p>
            </div>
            <div class="info-item">
              <label>Status</label>
              <p>
                <span class="badge" :class="`badge-${school.status}`">
                  {{ formatStatus(school.status) }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <!-- Leadership -->
        <div v-if="school.principal_id || school.hod_id" class="profile-section">
          <h3>👥 Leadership</h3>
          <div class="info-grid">
            <div class="info-item" v-if="school.principal_id">
              <label>Principal</label>
              <p class="monospace">{{ school.principal_id }}</p>
            </div>
            <div class="info-item" v-if="school.hod_id">
              <label>Head of Department</label>
              <p class="monospace">{{ school.hod_id }}</p>
            </div>
          </div>
        </div>

        <!-- System Information -->
        <div class="profile-section">
          <h3>System Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>School ID</label>
              <p class="monospace">{{ school.id }}</p>
            </div>
            <div class="info-item">
              <label>Created</label>
              <p>{{ formatDateTime(school.created_at) }}</p>
            </div>
            <div class="info-item">
              <label>Last Updated</label>
              <p>{{ formatDateTime(school.updated_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Custom Settings -->
        <div v-if="hasSettings" class="profile-section">
          <h3>Custom Settings</h3>
          <pre class="settings-json">{{ JSON.stringify(school.settings, null, 2) }}</pre>
        </div>

        <!-- Actions -->
        <div class="profile-actions">
          <button @click="handleChangeStatus" class="btn-secondary">Change Status</button>
          <button @click="handleEdit" class="btn-secondary">Edit School</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSchoolStore } from '@/stores/schoolStore'

const route = useRoute()
const router = useRouter()
const schoolStore = useSchoolStore()

const schoolId = computed(() => route.params.id as string)
const school = computed(() => schoolStore.selectedSchool)

const hasAddress = computed(() => {
  if (!school.value) return false
  return !!(school.value.address_line1 || school.value.city || school.value.state)
})

const hasContact = computed(() => {
  if (!school.value) return false
  return !!(school.value.email || school.value.phone)
})

const hasOnlinePresence = computed(() => {
  if (!school.value) return false
  return !!(school.value.website_url || school.value.facebook_url || school.value.twitter_url || school.value.instagram_url)
})

const hasSettings = computed(() => {
  if (!school.value || !school.value.settings) return false
  return Object.keys(school.value.settings).length > 0
})

/**
 * Load school on component mount
 */
onMounted(async () => {
  await loadSchool()
})

/**
 * Load school details
 */
async function loadSchool() {
  try {
    await schoolStore.fetchSchoolById(schoolId.value)
  } catch (error) {
    console.error('Failed to load school:', error)
  }
}

/**
 * Retry loading school
 */
function retryLoad() {
  schoolStore.clearError()
  loadSchool()
}

/**
 * Navigate back to school list
 */
function goBack() {
  router.push('/schools')
}

/**
 * Handle edit school
 */
function handleEdit() {
  router.push(`/schools/${schoolId.value}/edit`)
}

/**
 * Handle delete school
 */
async function handleDelete() {
  if (!school.value) return

  if (confirm(`Are you sure you want to delete ${school.value.name}? This action cannot be undone.`)) {
    try {
      await schoolStore.deleteSchool(schoolId.value)
      router.push('/schools')
    } catch (error) {
      alert('Failed to delete school')
    }
  }
}

/**
 * Handle change status
 */
function handleChangeStatus() {
  if (!school.value) return

  const statuses = ['active', 'inactive', 'suspended']
  const currentStatus = school.value.status
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
 * Change school status
 */
async function changeStatus(status: 'active' | 'inactive' | 'suspended') {
  try {
    await schoolStore.changeSchoolStatus(schoolId.value, status)
    await loadSchool()
  } catch (error) {
    alert('Failed to change school status')
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
.school-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.school-detail-header {
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

.school-profile-card {
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

.profile-logo img,
.logo-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  object-fit: cover;
}

.logo-placeholder {
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

.profile-info .slug {
  margin: 0 0 1rem 0;
  opacity: 0.9;
  font-size: 1.1rem;
  font-family: monospace;
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

.badge-active { background: rgba(255, 255, 255, 0.3); color: white; }
.badge-inactive { background: rgba(0, 0, 0, 0.2); color: white; }
.badge-suspended { background: rgba(211, 47, 47, 0.5); color: white; }

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

.address-block p {
  margin: 0.25rem 0;
  color: #2c3e50;
}

.text-muted {
  color: #6c757d;
  font-size: 0.9rem;
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

.info-item a {
  color: #42b883;
  text-decoration: none;
}

.info-item a:hover {
  text-decoration: underline;
}

.monospace {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.settings-json {
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
