<template>
  <div class="teacher-form">
    <!-- Header -->
    <div class="form-header">
      <button @click="goBack" class="btn-back">← Back to Teachers</button>
      <h2>{{ isEditMode ? 'Edit Teacher' : 'Create New Teacher' }}</h2>
    </div>

    <!-- Loading State -->
    <div v-if="isEditMode && teacherStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading teacher data...</p>
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

        <div class="form-row">
          <div class="form-group">
            <label for="user_id">User Account * {{ !isEditMode ? '' : '(cannot be changed)' }}</label>
            <input
              id="user_id"
              v-model="formData.user_id"
              type="text"
              required
              :disabled="isSubmitting || isEditMode"
              placeholder="Enter user UUID"
            />
            <small class="help-text">UUID of the user with teacher persona</small>
          </div>

          <div class="form-group">
            <label for="employee_id">Employee ID *</label>
            <input
              id="employee_id"
              v-model="formData.employee_id"
              type="text"
              required
              :disabled="isSubmitting || isEditMode"
              placeholder="e.g., EMP001"
            />
            <small v-if="isEditMode" class="help-text">Employee ID cannot be changed</small>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="hire_date">Hire Date *</label>
            <input
              id="hire_date"
              v-model="formData.hire_date"
              type="date"
              required
              :disabled="isSubmitting"
            />
          </div>

          <div class="form-group">
            <label for="termination_date">Termination Date</label>
            <input
              id="termination_date"
              v-model="formData.termination_date"
              type="date"
              :disabled="isSubmitting"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="department">Department</label>
            <input
              id="department"
              v-model="formData.department"
              type="text"
              :disabled="isSubmitting"
              placeholder="e.g., Mathematics, Science"
            />
          </div>

          <div class="form-group">
            <label for="job_title">Job Title</label>
            <input
              id="job_title"
              v-model="formData.job_title"
              type="text"
              :disabled="isSubmitting"
              placeholder="e.g., Teacher, Lead Teacher"
            />
          </div>
        </div>
      </div>

      <!-- Teaching Credentials -->
      <div class="form-section">
        <h3>Teaching Credentials</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="certification_number">Certification Number</label>
            <input
              id="certification_number"
              v-model="formData.certification_number"
              type="text"
              :disabled="isSubmitting"
              placeholder="Enter certification number"
            />
          </div>

          <div class="form-group">
            <label for="certification_expiry">Certification Expiry</label>
            <input
              id="certification_expiry"
              v-model="formData.certification_expiry"
              type="date"
              :disabled="isSubmitting"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="education_level">Education Level</label>
            <select
              id="education_level"
              v-model="formData.education_level"
              :disabled="isSubmitting"
            >
              <option value="">Select education level</option>
              <option value="High School">High School</option>
              <option value="Associate">Associate</option>
              <option value="Bachelor's">Bachelor's</option>
              <option value="Master's">Master's</option>
              <option value="PhD">PhD</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label for="university">University</label>
            <input
              id="university"
              v-model="formData.university"
              type="text"
              :disabled="isSubmitting"
              placeholder="Enter university name"
            />
          </div>
        </div>
      </div>

      <!-- Teaching Assignments -->
      <div class="form-section">
        <h3>Teaching Assignments</h3>

        <div class="form-group">
          <label>Grade Levels * (Select one or more)</label>
          <div class="checkbox-group">
            <label v-for="grade in [1, 2, 3, 4, 5, 6, 7]" :key="grade" class="checkbox-label">
              <input
                type="checkbox"
                :value="grade"
                v-model="formData.grade_levels"
                :disabled="isSubmitting"
              />
              Grade {{ grade }}
            </label>
          </div>
          <small class="help-text">Select all grades this teacher will teach</small>
        </div>

        <div class="form-group">
          <label for="specializations">Specializations (comma-separated)</label>
          <input
            id="specializations"
            v-model="specializationsInput"
            type="text"
            :disabled="isSubmitting"
            placeholder="e.g., MATH, SCIENCE, ELA"
          />
          <small class="help-text">Subject codes separated by commas</small>
        </div>
      </div>

      <!-- Employment Details -->
      <div class="form-section">
        <h3>Employment Details</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="employment_type">Employment Type</label>
            <select
              id="employment_type"
              v-model="formData.employment_type"
              :disabled="isSubmitting"
            >
              <option value="full-time">Full-time</option>
              <option value="part-time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="substitute">Substitute</option>
            </select>
          </div>

          <div class="form-group">
            <label for="work_hours_per_week">Work Hours per Week</label>
            <input
              id="work_hours_per_week"
              v-model.number="formData.work_hours_per_week"
              type="number"
              min="1"
              max="80"
              :disabled="isSubmitting"
              placeholder="40"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="salary">Salary (optional - sensitive information)</label>
          <input
            id="salary"
            v-model.number="formData.salary"
            type="number"
            min="0"
            step="0.01"
            :disabled="isSubmitting"
            placeholder="0.00"
          />
          <small class="help-text">This information is kept confidential</small>
        </div>
      </div>

      <!-- Emergency Contact -->
      <div class="form-section">
        <h3>Emergency Contact</h3>

        <div class="form-group">
          <label for="emergency_contact_name">Contact Name</label>
          <input
            id="emergency_contact_name"
            v-model="formData.emergency_contact_name"
            type="text"
            :disabled="isSubmitting"
            placeholder="Enter full name"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="emergency_contact_phone">Contact Phone</label>
            <input
              id="emergency_contact_phone"
              v-model="formData.emergency_contact_phone"
              type="tel"
              :disabled="isSubmitting"
              placeholder="+1234567890"
            />
          </div>

          <div class="form-group">
            <label for="emergency_contact_relationship">Relationship</label>
            <input
              id="emergency_contact_relationship"
              v-model="formData.emergency_contact_relationship"
              type="text"
              :disabled="isSubmitting"
              placeholder="e.g., Spouse, Parent, Sibling"
            />
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="form-section">
        <h3>Additional Information</h3>

        <div class="form-row">
          <div class="form-group">
            <label for="office_room">Office Room</label>
            <input
              id="office_room"
              v-model="formData.office_room"
              type="text"
              :disabled="isSubmitting"
              placeholder="e.g., Room 101, Building A"
            />
          </div>

          <div class="form-group">
            <label for="status">Status</label>
            <select
              id="status"
              v-model="formData.status"
              :disabled="isSubmitting"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="on_leave">On Leave</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="bio">Bio / Notes</label>
          <textarea
            id="bio"
            v-model="formData.bio"
            :disabled="isSubmitting"
            placeholder="Enter bio or additional notes"
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
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update Teacher' : 'Create Teacher') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTeacherStore } from '@/stores/teacherStore'
import type { TeacherCreateInput, TeacherUpdateInput } from '@/types'

const route = useRoute()
const router = useRouter()
const teacherStore = useTeacherStore()

const teacherId = computed(() => route.params.id as string)
const isEditMode = computed(() => !!teacherId.value && teacherId.value !== 'create')

const isSubmitting = ref(false)
const formError = ref<string | null>(null)

interface FormData {
  user_id: string
  employee_id: string
  hire_date: string
  termination_date: string
  department: string
  job_title: string
  certification_number: string
  certification_expiry: string
  education_level: string
  university: string
  grade_levels: number[]
  employment_type: string
  salary: number | null
  work_hours_per_week: number | null
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  bio: string
  office_room: string
  status: string
}

const formData = reactive<FormData>({
  user_id: '',
  employee_id: '',
  hire_date: '',
  termination_date: '',
  department: '',
  job_title: '',
  certification_number: '',
  certification_expiry: '',
  education_level: '',
  university: '',
  grade_levels: [],
  employment_type: 'full-time',
  salary: null,
  work_hours_per_week: 40,
  emergency_contact_name: '',
  emergency_contact_phone: '',
  emergency_contact_relationship: '',
  bio: '',
  office_room: '',
  status: 'active'
})

// Helper for specializations input
const specializationsInput = ref('')

// Convert array to comma-separated string for display
watch(() => formData.grade_levels, () => {
  // This watcher helps with reactivity
}, { deep: true })

/**
 * Load teacher data if in edit mode
 */
onMounted(async () => {
  if (isEditMode.value) {
    await loadTeacher()
  }

  // Get school_id from current user/session
  // TODO: Replace with actual school_id from auth store
  if (!isEditMode.value && !formData.user_id) {
    // In create mode, we need to provide user_id and school_id
    const urlParams = new URLSearchParams(window.location.search)
    const userId = urlParams.get('user_id')
    if (userId) {
      formData.user_id = userId
    }
  }
})

/**
 * Load teacher for editing
 */
async function loadTeacher() {
  try {
    await teacherStore.fetchTeacherById(teacherId.value)
    const teacher = teacherStore.selectedTeacher

    if (teacher) {
      formData.user_id = teacher.user_id
      formData.employee_id = teacher.employee_id
      formData.hire_date = teacher.hire_date ? teacher.hire_date.split('T')[0] : ''
      formData.termination_date = teacher.termination_date ? teacher.termination_date.split('T')[0] : ''
      formData.department = teacher.department || ''
      formData.job_title = teacher.job_title || ''
      formData.certification_number = teacher.certification_number || ''
      formData.certification_expiry = teacher.certification_expiry ? teacher.certification_expiry.split('T')[0] : ''
      formData.education_level = teacher.education_level || ''
      formData.university = teacher.university || ''
      formData.grade_levels = teacher.grade_levels || []
      formData.employment_type = teacher.employment_type || 'full-time'
      formData.salary = teacher.salary || null
      formData.work_hours_per_week = teacher.work_hours_per_week || 40
      formData.emergency_contact_name = teacher.emergency_contact_name || ''
      formData.emergency_contact_phone = teacher.emergency_contact_phone || ''
      formData.emergency_contact_relationship = teacher.emergency_contact_relationship || ''
      formData.bio = teacher.bio || ''
      formData.office_room = teacher.office_room || ''
      formData.status = teacher.status || 'active'

      // Set specializations
      specializationsInput.value = teacher.specializations?.join(', ') || ''
    }
  } catch (error: any) {
    formError.value = error.message || 'Failed to load teacher'
  }
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  formError.value = null

  // Validate grade levels
  if (formData.grade_levels.length === 0) {
    formError.value = 'Please select at least one grade level'
    return
  }

  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      await updateTeacher()
    } else {
      await createTeacher()
    }

    router.push('/teachers')
  } catch (error: any) {
    formError.value = error.message || 'Failed to save teacher'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Create new teacher
 */
async function createTeacher() {
  // Get school_id from somewhere (TODO: use auth store)
  const schoolId = localStorage.getItem('current_school_id') || 'SCHOOL_ID_PLACEHOLDER'

  const teacherData: TeacherCreateInput = {
    school_id: schoolId,
    user_id: formData.user_id,
    employee_id: formData.employee_id,
    hire_date: formData.hire_date,
    grade_levels: formData.grade_levels,
  }

  // Add optional fields if provided
  if (formData.termination_date) teacherData.termination_date = formData.termination_date
  if (formData.department) teacherData.department = formData.department
  if (formData.job_title) teacherData.job_title = formData.job_title
  if (formData.certification_number) teacherData.certification_number = formData.certification_number
  if (formData.certification_expiry) teacherData.certification_expiry = formData.certification_expiry
  if (formData.education_level) teacherData.education_level = formData.education_level as any
  if (formData.university) teacherData.university = formData.university
  if (formData.employment_type) teacherData.employment_type = formData.employment_type as any
  if (formData.salary) teacherData.salary = formData.salary
  if (formData.work_hours_per_week) teacherData.work_hours_per_week = formData.work_hours_per_week
  if (formData.emergency_contact_name) teacherData.emergency_contact_name = formData.emergency_contact_name
  if (formData.emergency_contact_phone) teacherData.emergency_contact_phone = formData.emergency_contact_phone
  if (formData.emergency_contact_relationship) teacherData.emergency_contact_relationship = formData.emergency_contact_relationship
  if (formData.bio) teacherData.bio = formData.bio
  if (formData.office_room) teacherData.office_room = formData.office_room

  // Parse specializations
  if (specializationsInput.value.trim()) {
    teacherData.specializations = specializationsInput.value
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0)
  }

  await teacherStore.createTeacher(teacherData)
}

/**
 * Update existing teacher
 */
async function updateTeacher() {
  const teacherData: TeacherUpdateInput = {}

  // Add all fields (they're all optional in update)
  if (formData.department) teacherData.department = formData.department
  if (formData.job_title) teacherData.job_title = formData.job_title
  if (formData.certification_number) teacherData.certification_number = formData.certification_number
  if (formData.certification_expiry) teacherData.certification_expiry = formData.certification_expiry
  if (formData.education_level) teacherData.education_level = formData.education_level as any
  if (formData.university) teacherData.university = formData.university
  if (formData.grade_levels.length > 0) teacherData.grade_levels = formData.grade_levels
  if (formData.employment_type) teacherData.employment_type = formData.employment_type as any
  if (formData.salary !== null) teacherData.salary = formData.salary
  if (formData.work_hours_per_week !== null) teacherData.work_hours_per_week = formData.work_hours_per_week
  if (formData.emergency_contact_name) teacherData.emergency_contact_name = formData.emergency_contact_name
  if (formData.emergency_contact_phone) teacherData.emergency_contact_phone = formData.emergency_contact_phone
  if (formData.emergency_contact_relationship) teacherData.emergency_contact_relationship = formData.emergency_contact_relationship
  if (formData.bio) teacherData.bio = formData.bio
  if (formData.office_room) teacherData.office_room = formData.office_room
  if (formData.termination_date) teacherData.termination_date = formData.termination_date

  // Parse specializations
  if (specializationsInput.value.trim()) {
    teacherData.specializations = specializationsInput.value
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0)
  }

  await teacherStore.updateTeacher(teacherId.value, teacherData)
}

/**
 * Navigate back to teacher list
 */
function goBack() {
  router.push('/teachers')
}
</script>

<style scoped>
.teacher-form {
  padding: 2rem;
  max-width: 1000px;
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

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
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
