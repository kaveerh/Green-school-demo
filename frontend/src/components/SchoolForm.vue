<template>
  <div class="school-form">
    <!-- Header -->
    <div class="form-header">
      <button @click="goBack" class="btn-back">← Back to Schools</button>
      <h2>{{ isEditMode ? 'Edit School' : 'Create New School' }}</h2>
    </div>

    <!-- Loading State -->
    <div v-if="isEditMode && schoolStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading school data...</p>
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="form-container">
      <!-- Error Messages -->
      <div v-if="formError" class="error-banner">
        {{ formError }}
      </div>

      <!-- Basic Information -->
      <div class="form-section">
        <h3>Basic Information</h3>

        <div class="form-group">
          <label for="name">School Name *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            :disabled="isSubmitting"
            placeholder="Enter school name"
          />
        </div>

        <div class="form-group">
          <label for="slug">URL Slug</label>
          <input
            id="slug"
            v-model="formData.slug"
            type="text"
            :disabled="isSubmitting"
            placeholder="url-friendly-name (auto-generated if empty)"
            pattern="[a-z0-9-]+"
          />
          <small class="help-text">URL-friendly identifier (lowercase, numbers, hyphens only)</small>
        </div>
      </div>

      <!-- Address Information -->
      <div class="form-section">
        <h3>Address</h3>

        <div class="form-group">
          <label for="address_line1">Address Line 1</label>
          <input
            id="address_line1"
            v-model="formData.address_line1"
            type="text"
            :disabled="isSubmitting"
            placeholder="123 Main Street"
          />
        </div>

        <div class="form-group">
          <label for="address_line2">Address Line 2</label>
          <input
            id="address_line2"
            v-model="formData.address_line2"
            type="text"
            :disabled="isSubmitting"
            placeholder="Suite 100"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="city">City</label>
            <input
              id="city"
              v-model="formData.city"
              type="text"
              :disabled="isSubmitting"
              placeholder="City"
            />
          </div>

          <div class="form-group">
            <label for="state">State/Province</label>
            <input
              id="state"
              v-model="formData.state"
              type="text"
              :disabled="isSubmitting"
              placeholder="State"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="postal_code">Postal Code</label>
            <input
              id="postal_code"
              v-model="formData.postal_code"
              type="text"
              :disabled="isSubmitting"
              placeholder="12345"
            />
          </div>

          <div class="form-group">
            <label for="country">Country</label>
            <input
              id="country"
              v-model="formData.country"
              type="text"
              :disabled="isSubmitting"
              placeholder="USA"
            />
          </div>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="form-section">
        <h3>Contact Information</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              :disabled="isSubmitting"
              placeholder="contact@school.edu"
            />
          </div>

          <div class="form-group">
            <label for="phone">Phone</label>
            <input
              id="phone"
              v-model="formData.phone"
              type="tel"
              :disabled="isSubmitting"
              placeholder="+1-234-567-8900"
            />
          </div>
        </div>
      </div>

      <!-- Online Presence -->
      <div class="form-section">
        <h3>Online Presence</h3>

        <div class="form-group">
          <label for="website_url">Website URL</label>
          <input
            id="website_url"
            v-model="formData.website_url"
            type="url"
            :disabled="isSubmitting"
            placeholder="https://school.edu"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="facebook_url">Facebook URL</label>
            <input
              id="facebook_url"
              v-model="formData.facebook_url"
              type="url"
              :disabled="isSubmitting"
              placeholder="https://facebook.com/schoolname"
            />
          </div>

          <div class="form-group">
            <label for="twitter_url">Twitter URL</label>
            <input
              id="twitter_url"
              v-model="formData.twitter_url"
              type="url"
              :disabled="isSubmitting"
              placeholder="https://twitter.com/schoolname"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="instagram_url">Instagram URL</label>
          <input
            id="instagram_url"
            v-model="formData.instagram_url"
            type="url"
            :disabled="isSubmitting"
            placeholder="https://instagram.com/schoolname"
          />
        </div>

        <div class="form-group">
          <label for="logo_url">Logo URL</label>
          <input
            id="logo_url"
            v-model="formData.logo_url"
            type="url"
            :disabled="isSubmitting"
            placeholder="https://example.com/logo.png"
          />
          <small class="help-text">URL to publicly accessible logo image</small>
        </div>
      </div>

      <!-- Settings -->
      <div class="form-section">
        <h3>Settings</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="timezone">Timezone</label>
            <select
              id="timezone"
              v-model="formData.timezone"
              :disabled="isSubmitting"
            >
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
              <option value="America/Phoenix">Arizona Time</option>
              <option value="America/Anchorage">Alaska Time</option>
              <option value="Pacific/Honolulu">Hawaii Time</option>
            </select>
          </div>

          <div class="form-group">
            <label for="locale">Locale</label>
            <select
              id="locale"
              v-model="formData.locale"
              :disabled="isSubmitting"
            >
              <option value="en_US">English (US)</option>
              <option value="es_ES">Spanish</option>
              <option value="fr_FR">French</option>
            </select>
          </div>
        </div>

        <div class="form-group" v-if="!isEditMode">
          <label for="status">Status</label>
          <select
            id="status"
            v-model="formData.status"
            :disabled="isSubmitting"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary" :disabled="isSubmitting">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update School' : 'Create School') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSchoolStore } from '@/stores/schoolStore'
import type { SchoolCreate, SchoolUpdate } from '@/types/school'

const route = useRoute()
const router = useRouter()
const schoolStore = useSchoolStore()

const schoolId = computed(() => route.params.id as string)
const isEditMode = computed(() => !!schoolId.value && schoolId.value !== 'create')

const isSubmitting = ref(false)
const formError = ref<string | null>(null)

interface FormData {
  name: string
  slug: string
  address_line1: string
  address_line2: string
  city: string
  state: string
  postal_code: string
  country: string
  phone: string
  email: string
  website_url: string
  facebook_url: string
  twitter_url: string
  instagram_url: string
  logo_url: string
  timezone: string
  locale: string
  status: string
}

const formData = reactive<FormData>({
  name: '',
  slug: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'USA',
  phone: '',
  email: '',
  website_url: '',
  facebook_url: '',
  twitter_url: '',
  instagram_url: '',
  logo_url: '',
  timezone: 'America/New_York',
  locale: 'en_US',
  status: 'active'
})

/**
 * Load school data if in edit mode
 */
onMounted(async () => {
  if (isEditMode.value) {
    await loadSchool()
  }
})

/**
 * Load school for editing
 */
async function loadSchool() {
  try {
    await schoolStore.fetchSchoolById(schoolId.value)
    const school = schoolStore.selectedSchool

    if (school) {
      formData.name = school.name
      formData.slug = school.slug
      formData.address_line1 = school.address_line1 || ''
      formData.address_line2 = school.address_line2 || ''
      formData.city = school.city || ''
      formData.state = school.state || ''
      formData.postal_code = school.postal_code || ''
      formData.country = school.country
      formData.phone = school.phone || ''
      formData.email = school.email || ''
      formData.website_url = school.website_url || ''
      formData.facebook_url = school.facebook_url || ''
      formData.twitter_url = school.twitter_url || ''
      formData.instagram_url = school.instagram_url || ''
      formData.logo_url = school.logo_url || ''
      formData.timezone = school.timezone
      formData.locale = school.locale
      formData.status = school.status
    }
  } catch (error: any) {
    formError.value = error.message || 'Failed to load school'
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
      await updateSchool()
    } else {
      await createSchool()
    }

    router.push('/schools')
  } catch (error: any) {
    formError.value = error.message || 'Failed to save school'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Create new school
 */
async function createSchool() {
  const schoolData: SchoolCreate = {
    name: formData.name,
    slug: formData.slug || undefined,
    country: formData.country,
    timezone: formData.timezone,
    locale: formData.locale,
    status: formData.status as any,
  }

  // Add optional fields if provided
  if (formData.address_line1) schoolData.address_line1 = formData.address_line1
  if (formData.address_line2) schoolData.address_line2 = formData.address_line2
  if (formData.city) schoolData.city = formData.city
  if (formData.state) schoolData.state = formData.state
  if (formData.postal_code) schoolData.postal_code = formData.postal_code
  if (formData.phone) schoolData.phone = formData.phone
  if (formData.email) schoolData.email = formData.email
  if (formData.website_url) schoolData.website_url = formData.website_url
  if (formData.facebook_url) schoolData.facebook_url = formData.facebook_url
  if (formData.twitter_url) schoolData.twitter_url = formData.twitter_url
  if (formData.instagram_url) schoolData.instagram_url = formData.instagram_url
  if (formData.logo_url) schoolData.logo_url = formData.logo_url

  await schoolStore.createSchool(schoolData)
}

/**
 * Update existing school
 */
async function updateSchool() {
  const schoolData: SchoolUpdate = {
    name: formData.name,
    slug: formData.slug || undefined,
  }

  // Add optional fields
  if (formData.address_line1) schoolData.address_line1 = formData.address_line1
  if (formData.address_line2) schoolData.address_line2 = formData.address_line2
  if (formData.city) schoolData.city = formData.city
  if (formData.state) schoolData.state = formData.state
  if (formData.postal_code) schoolData.postal_code = formData.postal_code
  if (formData.country) schoolData.country = formData.country
  if (formData.phone) schoolData.phone = formData.phone
  if (formData.email) schoolData.email = formData.email
  if (formData.website_url) schoolData.website_url = formData.website_url
  if (formData.facebook_url) schoolData.facebook_url = formData.facebook_url
  if (formData.twitter_url) schoolData.twitter_url = formData.twitter_url
  if (formData.instagram_url) schoolData.instagram_url = formData.instagram_url
  if (formData.logo_url) schoolData.logo_url = formData.logo_url
  if (formData.timezone) schoolData.timezone = formData.timezone
  if (formData.locale) schoolData.locale = formData.locale

  await schoolStore.updateSchool(schoolId.value, schoolData)
}

/**
 * Navigate back to school list
 */
function goBack() {
  router.push('/schools')
}
</script>

<style scoped>
.school-form {
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
