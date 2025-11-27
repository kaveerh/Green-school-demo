<template>
  <div class="registration-container">
    <div class="registration-card">
      <!-- Logo and Branding -->
      <div class="registration-header">
        <div class="brand-logo">
          <span class="brand-icon">🌱</span>
          <h1 class="brand-title">Green School</h1>
        </div>
        <p class="brand-subtitle">Management System</p>
      </div>

      <!-- Registration Content -->
      <div class="registration-content">
        <h2>Create Your Account</h2>
        <p class="registration-description">Join Green School Management System</p>

        <!-- Success Message -->
        <div v-if="successMessage" class="alert alert-success">
          <span class="alert-icon">✓</span>
          <span>{{ successMessage }}</span>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-error">
          <span class="alert-icon">⚠️</span>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- Registration Form -->
        <form @submit.prevent="handleRegistration" class="registration-form">
          <!-- Personal Information -->
          <div class="form-section">
            <h3 class="section-title">Personal Information</h3>

            <div class="form-row">
              <div class="form-group">
                <label for="firstName" class="form-label">
                  First Name <span class="required">*</span>
                </label>
                <input
                  id="firstName"
                  v-model="formData.firstName"
                  type="text"
                  class="form-input"
                  placeholder="Enter your first name"
                  required
                  :disabled="isLoading"
                />
              </div>

              <div class="form-group">
                <label for="lastName" class="form-label">
                  Last Name <span class="required">*</span>
                </label>
                <input
                  id="lastName"
                  v-model="formData.lastName"
                  type="text"
                  class="form-input"
                  placeholder="Enter your last name"
                  required
                  :disabled="isLoading"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="email" class="form-label">
                Email <span class="required">*</span>
              </label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                class="form-input"
                placeholder="your.email@school.edu"
                required
                :disabled="isLoading"
              />
              <small class="form-help">This will be your username for login</small>
            </div>

            <div class="form-group">
              <label for="phone" class="form-label">Phone</label>
              <input
                id="phone"
                v-model="formData.phone"
                type="tel"
                class="form-input"
                placeholder="+1234567890"
                :disabled="isLoading"
              />
            </div>
          </div>

          <!-- Account Settings -->
          <div class="form-section">
            <h3 class="section-title">Account Settings</h3>

            <div class="form-group">
              <label for="password" class="form-label">
                Password <span class="required">*</span>
              </label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                class="form-input"
                placeholder="Create a strong password"
                required
                minlength="8"
                :disabled="isLoading"
              />
              <small class="form-help">
                Must be at least 8 characters with uppercase, digit, and special character
              </small>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">
                Confirm Password <span class="required">*</span>
              </label>
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                type="password"
                class="form-input"
                placeholder="Confirm your password"
                required
                minlength="8"
                :disabled="isLoading"
              />
            </div>

            <div class="form-group">
              <label for="persona" class="form-label">
                I am a <span class="required">*</span>
              </label>
              <select
                id="persona"
                v-model="formData.persona"
                class="form-select"
                required
                :disabled="isLoading"
              >
                <option value="">Select your role</option>
                <option value="teacher">Teacher</option>
                <option value="student">Student</option>
                <option value="parent">Parent</option>
              </select>
              <small class="form-help">Select your role in the school</small>
            </div>

            <div class="form-group">
              <label for="schoolId" class="form-label">
                School <span class="required">*</span>
              </label>
              <select
                id="schoolId"
                v-model="formData.schoolId"
                class="form-select"
                required
                :disabled="isLoading || loadingSchools"
              >
                <option value="">
                  {{ loadingSchools ? 'Loading schools...' : 'Select your school' }}
                </option>
                <option v-for="school in schools" :key="school.id" :value="school.id">
                  {{ school.name }} - {{ school.city }}, {{ school.state }}
                </option>
              </select>
              <small v-if="schoolsError" class="form-error">
                {{ schoolsError }}
                <button
                  type="button"
                  @click="fetchSchools"
                  class="retry-link"
                  :disabled="loadingSchools"
                >
                  Retry
                </button>
              </small>
              <small v-else class="form-help">
                Select the school you are registering for
              </small>
            </div>
          </div>

          <!-- Terms and Conditions -->
          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="formData.acceptTerms"
                type="checkbox"
                class="form-checkbox"
                required
                :disabled="isLoading"
              />
              <span>
                I accept the
                <router-link to="/terms" class="link-primary" target="_blank">
                  Terms of Service
                </router-link>
                and
                <router-link to="/privacy" class="link-primary" target="_blank">
                  Privacy Policy
                </router-link>
              </span>
            </label>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="btn btn-primary btn-large" :disabled="isLoading">
            <span v-if="isLoading" class="btn-loading">
              <span class="spinner"></span>
              Creating Account...
            </span>
            <span v-else>
              <span class="btn-icon">✨</span>
              Create Account
            </span>
          </button>
        </form>

        <!-- Login Link -->
        <div class="registration-footer">
          <p class="text-muted">Already have an account?</p>
          <router-link to="/login" class="link-primary"> Sign In </router-link>
        </div>
      </div>
    </div>

    <!-- Background Decoration -->
    <div class="registration-decoration">
      <div class="decoration-circle decoration-circle-1"></div>
      <div class="decoration-circle decoration-circle-2"></div>
      <div class="decoration-circle decoration-circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

interface School {
  id: string
  name: string
  city: string
  state: string
}

const router = useRouter()
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const schools = ref<School[]>([])
const loadingSchools = ref(false)
const schoolsError = ref('')

const formData = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  persona: '',
  schoolId: '',
  acceptTerms: false
})

// Fetch schools on component mount
onMounted(async () => {
  await fetchSchools()
})

async function fetchSchools() {
  loadingSchools.value = true
  schoolsError.value = ''

  try {
    const response = await axios.get(
      `${import.meta.env.VITE_API_BASE_URL}/api/v1/schools`,
      {
        params: {
          page: 1,
          limit: 100,
          status: 'active'
        }
      }
    )

    if (response.data && response.data.data) {
      schools.value = response.data.data
        .map((school: any) => ({
          id: school.id,
          name: school.name,
          city: school.city || 'Unknown',
          state: school.state || 'Unknown'
        }))
        .sort((a: School, b: School) => a.name.localeCompare(b.name))
    }
  } catch (error: any) {
    console.error('Failed to fetch schools:', error)
    schoolsError.value = 'Unable to load schools. Please try again later.'
  } finally {
    loadingSchools.value = false
  }
}

async function handleRegistration() {
  // Clear previous messages
  successMessage.value = ''
  errorMessage.value = ''

  // Validate passwords match
  if (formData.password !== formData.confirmPassword) {
    errorMessage.value = 'Passwords do not match'
    return
  }

  // Validate password strength
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
  if (!passwordRegex.test(formData.password)) {
    errorMessage.value =
      'Password must be at least 8 characters with uppercase, lowercase, digit, and special character'
    return
  }

  isLoading.value = true

  try {
    // Call backend API to create user (which will also create Keycloak user)
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/api/v1/users`,
      {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
        persona: formData.persona,
        school_id: formData.schoolId,
        status: 'active'
      }
    )

    if (response.data) {
      successMessage.value =
        'Account created successfully! Redirecting to login...'

      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push({
          path: '/login',
          query: { registered: 'true', email: formData.email }
        })
      }, 2000)
    }
  } catch (error: any) {
    console.error('Registration error:', error)

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (error.response?.status === 400) {
      errorMessage.value = 'Invalid registration data. Please check your information.'
    } else if (error.response?.status === 409) {
      errorMessage.value = 'An account with this email already exists.'
    } else {
      errorMessage.value = 'Registration failed. Please try again later.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.registration-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
  position: relative;
  overflow: hidden;
}

/* Registration Card */
.registration-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 3rem;
  max-width: 600px;
  width: 100%;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header */
.registration-header {
  text-align: center;
  margin-bottom: 2rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.brand-icon {
  font-size: 3rem;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.brand-subtitle {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0;
}

/* Content */
.registration-content {
  margin-bottom: 2rem;
}

.registration-content h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.registration-description {
  color: #64748b;
  margin: 0 0 2rem 0;
  font-size: 1rem;
  text-align: center;
}

/* Alert */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9375rem;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.alert-success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.alert-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

/* Form */
.registration-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select {
  padding: 0.75rem 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled,
.form-select:disabled {
  background: #f1f5f9;
  cursor: not-allowed;
}

.form-help {
  font-size: 0.8125rem;
  color: #64748b;
}

.form-error {
  font-size: 0.8125rem;
  color: #ef4444;
  font-weight: 500;
}

.retry-link {
  margin-left: 0.5rem;
  color: #667eea;
  text-decoration: underline;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  padding: 0;
  font-family: inherit;
}

.retry-link:hover:not(:disabled) {
  color: #764ba2;
}

.retry-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  align-items: start;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #475569;
  cursor: pointer;
}

.form-checkbox {
  margin-top: 0.25rem;
  cursor: pointer;
}

/* Button */
.btn {
  width: 100%;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.25rem;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Footer */
.registration-footer {
  text-align: center;
  margin-top: 2rem;
}

.text-muted {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.link-primary {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: color 0.2s;
}

.link-primary:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Background Decoration */
.registration-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.decoration-circle-1 {
  width: 400px;
  height: 400px;
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.decoration-circle-2 {
  width: 300px;
  height: 300px;
  bottom: -150px;
  left: -100px;
  animation-delay: 5s;
}

.decoration-circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: -50px;
  animation-delay: 10s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .registration-container {
    padding: 1rem;
  }

  .registration-card {
    padding: 2rem 1.5rem;
  }

  .brand-title {
    font-size: 2rem;
  }

  .registration-content h2 {
    font-size: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
