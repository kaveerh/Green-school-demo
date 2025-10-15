<template>
  <div class="user-form">
    <!-- Header -->
    <div class="form-header">
      <button @click="goBack" class="btn-back">← Back to Users</button>
      <h2>{{ isEditMode ? 'Edit User' : 'Create New User' }}</h2>
    </div>

    <!-- Loading State -->
    <div v-if="isEditMode && userStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading user data...</p>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="form-container">
      <!-- Error Messages -->
      <div v-if="formError" class="error-banner">
        {{ formError }}
      </div>

      <!-- Personal Information -->
      <div class="form-section">
        <h3>Personal Information</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">First Name *</label>
            <input
              id="first_name"
              v-model="formData.first_name"
              type="text"
              required
              :disabled="isSubmitting"
              placeholder="Enter first name"
            />
          </div>

          <div class="form-group">
            <label for="last_name">Last Name *</label>
            <input
              id="last_name"
              v-model="formData.last_name"
              type="text"
              required
              :disabled="isSubmitting"
              placeholder="Enter last name"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email *</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            :disabled="isSubmitting || isEditMode"
            placeholder="user@example.com"
          />
          <small v-if="isEditMode" class="help-text">Email cannot be changed</small>
        </div>

        <div class="form-group">
          <label for="phone">Phone</label>
          <input
            id="phone"
            v-model="formData.phone"
            type="tel"
            :disabled="isSubmitting"
            placeholder="+1234567890"
          />
        </div>
      </div>

      <!-- Account Settings -->
      <div class="form-section">
        <h3>Account Settings</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="persona">Persona (Role) *</label>
            <select
              id="persona"
              v-model="formData.persona"
              required
              :disabled="isSubmitting"
            >
              <option value="">Select persona</option>
              <option value="administrator">Administrator</option>
              <option value="teacher">Teacher</option>
              <option value="student">Student</option>
              <option value="parent">Parent</option>
              <option value="vendor">Vendor</option>
            </select>
            <small class="help-text">Determines user permissions and access</small>
          </div>

          <div class="form-group" v-if="!isEditMode">
            <label for="school_id">School ID *</label>
            <input
              id="school_id"
              v-model="formData.school_id"
              type="text"
              required
              :disabled="isSubmitting"
              placeholder="Enter school UUID"
            />
            <small class="help-text">UUID of the school this user belongs to</small>
          </div>
        </div>

        <div class="form-group" v-if="!isEditMode">
          <label for="password">Password *</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            :disabled="isSubmitting"
            placeholder="Enter password"
          />
          <small class="help-text">
            Must be at least 8 characters with uppercase, digit, and special character
          </small>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="form-section">
        <h3>Additional Information</h3>

        <div class="form-group">
          <label for="avatar_url">Avatar URL</label>
          <input
            id="avatar_url"
            v-model="formData.avatar_url"
            type="url"
            :disabled="isSubmitting"
            placeholder="https://example.com/avatar.jpg"
          />
        </div>

        <div class="form-group">
          <label for="bio">Bio</label>
          <textarea
            id="bio"
            v-model="formData.bio"
            :disabled="isSubmitting"
            placeholder="Enter a brief bio"
            rows="4"
          ></textarea>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary" :disabled="isSubmitting">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update User' : 'Create User') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import type { UserCreateInput, UserUpdateInput } from '@/types/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const userId = computed(() => route.params.id as string)
const isEditMode = computed(() => !!userId.value && userId.value !== 'create')

const isSubmitting = ref(false)
const formError = ref<string | null>(null)

interface FormData {
  email: string
  first_name: string
  last_name: string
  persona: string
  password: string
  school_id: string
  phone: string
  avatar_url: string
  bio: string
}

const formData = reactive<FormData>({
  email: '',
  first_name: '',
  last_name: '',
  persona: '',
  password: '',
  school_id: '',
  phone: '',
  avatar_url: '',
  bio: ''
})

/**
 * Load user data if in edit mode
 */
onMounted(async () => {
  if (isEditMode.value) {
    await loadUser()
  }
})

/**
 * Load user for editing
 */
async function loadUser() {
  try {
    await userStore.fetchUserById(userId.value)
    const user = userStore.selectedUser

    if (user) {
      formData.email = user.email
      formData.first_name = user.first_name
      formData.last_name = user.last_name
      formData.persona = user.persona
      formData.school_id = user.school_id
      formData.phone = user.phone || ''
      formData.avatar_url = user.avatar_url || ''
      formData.bio = user.bio || ''
    }
  } catch (error: any) {
    formError.value = error.message || 'Failed to load user'
  }
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  formError.value = null
  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      await updateUser()
    } else {
      await createUser()
    }

    router.push('/users')
  } catch (error: any) {
    formError.value = error.message || 'Failed to save user'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Create new user
 */
async function createUser() {
  const userData: UserCreateInput = {
    email: formData.email,
    first_name: formData.first_name,
    last_name: formData.last_name,
    persona: formData.persona as any,
    password: formData.password,
    school_id: formData.school_id,
  }

  // Add optional fields if provided
  if (formData.phone) userData.phone = formData.phone
  if (formData.avatar_url) userData.avatar_url = formData.avatar_url
  if (formData.bio) userData.bio = formData.bio

  await userStore.createUser(userData)
}

/**
 * Update existing user
 */
async function updateUser() {
  const userData: UserUpdateInput = {
    first_name: formData.first_name,
    last_name: formData.last_name,
  }

  // Add optional fields if provided
  if (formData.phone) userData.phone = formData.phone
  if (formData.avatar_url) userData.avatar_url = formData.avatar_url
  if (formData.bio) userData.bio = formData.bio

  await userStore.updateUser(userId.value, userData)
}

/**
 * Navigate back to user list
 */
function goBack() {
  router.push('/users')
}
</script>

<style scoped>
.user-form {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 2rem;
}

.form-header h2 {
  margin: 1rem 0 0 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.btn-back {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #42b883;
  margin-bottom: 1rem;
}

.btn-back:hover {
  background: #f8f9fa;
}

.form-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.error-banner {
  background: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 2rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.form-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b883;
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
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

.btn-primary:hover:not(:disabled) {
  background: #35a372;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.btn-secondary:hover:not(:disabled) {
  background: #42b883;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
</style>
