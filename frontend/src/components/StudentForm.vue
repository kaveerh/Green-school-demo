<template>
  <div class="student-form">
    <!-- Header -->
    <div class="form-header">
      <button @click="goBack" class="btn-back">← Back to Students</button>
      <h2>{{ isEditMode ? 'Edit Student' : 'Create New Student' }}</h2>
    </div>

    <!-- Loading State -->
    <div v-if="isEditMode && studentStore.isLoading" class="loading-spinner">
      <div class="spinner"></div>
      <p>Loading student data...</p>
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
            <UserSelector
              v-model="formData.user_id"
              label="Student User Account"
              placeholder="Search for student by name or email..."
              help-text="Select the user account that will be associated with this student"
              filter-persona="student"
              :required="true"
              :disabled="isSubmitting || isEditMode"
              input-id="user_id"
              name="user_id"
              @select="handleUserSelect"
            />
            <small v-if="isEditMode" class="help-text">User account cannot be changed after creation</small>
          </div>

          <div class="form-group">
            <label for="student_id">Student ID *</label>
            <input
              id="student_id"
              v-model="formData.student_id"
              type="text"
              required
              :disabled="isSubmitting || isEditMode"
              placeholder="STU001"
            />
            <small v-if="isEditMode" class="help-text">Student ID cannot be changed</small>
          </div>
        </div>

        <div class="form-row">

          <div class="form-group">
            <label for="grade_level">Grade Level *</label>
            <select
              id="grade_level"
              v-model.number="formData.grade_level"
              required
              :disabled="isSubmitting"
            >
              <option value="">Select grade</option>
              <option :value="1">Grade 1</option>
              <option :value="2">Grade 2</option>
              <option :value="3">Grade 3</option>
              <option :value="4">Grade 4</option>
              <option :value="5">Grade 5</option>
              <option :value="6">Grade 6</option>
              <option :value="7">Grade 7</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="date_of_birth">Date of Birth *</label>
            <input
              id="date_of_birth"
              v-model="formData.date_of_birth"
              type="date"
              required
              :disabled="isSubmitting || isEditMode"
            />
            <small class="help-text">Must be between 5-15 years old</small>
          </div>

          <div class="form-group">
            <label for="gender">Gender</label>
            <select
              id="gender"
              v-model="formData.gender"
              :disabled="isSubmitting"
            >
              <option value="">Prefer not to say</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="enrollment_date">Enrollment Date *</label>
            <input
              id="enrollment_date"
              v-model="formData.enrollment_date"
              type="date"
              required
              :disabled="isSubmitting || isEditMode"
            />
          </div>

          <div class="form-group">
            <label for="graduation_date">Graduation Date</label>
            <input
              id="graduation_date"
              v-model="formData.graduation_date"
              type="date"
              :disabled="isSubmitting"
            />
            <small class="help-text">Optional - for graduated students</small>
          </div>
        </div>

        <div class="form-group">
          <label for="status">Status *</label>
          <select
            id="status"
            v-model="formData.status"
            required
            :disabled="isSubmitting"
          >
            <option value="enrolled">Enrolled</option>
            <option value="graduated">Graduated</option>
            <option value="transferred">Transferred</option>
            <option value="withdrawn">Withdrawn</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>
      </div>

      <!-- Medical Information -->
      <div class="form-section">
        <h3>Medical Information</h3>

        <div class="form-group">
          <label for="allergies">Allergies</label>
          <textarea
            id="allergies"
            v-model="formData.allergies"
            :disabled="isSubmitting"
            placeholder="List any known allergies"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="medical_notes">Medical Notes</label>
          <textarea
            id="medical_notes"
            v-model="formData.medical_notes"
            :disabled="isSubmitting"
            placeholder="Additional medical information"
            rows="3"
          ></textarea>
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
            placeholder="Emergency contact full name"
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
            <label for="emergency_contact_relation">Relationship</label>
            <input
              id="emergency_contact_relation"
              v-model="formData.emergency_contact_relation"
              type="text"
              :disabled="isSubmitting"
              placeholder="e.g., Mother, Guardian"
            />
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="form-section">
        <h3>Additional Information</h3>

        <div class="form-group">
          <label for="photo_url">Photo URL</label>
          <input
            id="photo_url"
            v-model="formData.photo_url"
            type="url"
            :disabled="isSubmitting"
            placeholder="https://example.com/photo.jpg"
          />
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="goBack" class="btn-secondary" :disabled="isSubmitting">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update Student' : 'Create Student') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/studentStore'
import type { StudentCreateInput, StudentUpdateInput } from '@/types/student'
import UserSelector from './UserSelector.vue'

const route = useRoute()
const router = useRouter()
const studentStore = useStudentStore()

const studentId = computed(() => route.params.id as string)
const isEditMode = computed(() => !!studentId.value && studentId.value !== 'create')

const isSubmitting = ref(false)
const formError = ref<string | null>(null)

interface FormData {
  school_id: string
  user_id: string
  student_id: string
  grade_level: number | string
  date_of_birth: string
  gender: string
  enrollment_date: string
  graduation_date: string
  allergies: string
  medical_notes: string
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relation: string
  photo_url: string
  status: string
}

const formData = reactive<FormData>({
  school_id: '',
  user_id: '',
  student_id: '',
  grade_level: '',
  date_of_birth: '',
  gender: '',
  enrollment_date: '',
  graduation_date: '',
  allergies: '',
  medical_notes: '',
  emergency_contact_name: '',
  emergency_contact_phone: '',
  emergency_contact_relation: '',
  photo_url: '',
  status: 'enrolled'
})

/**
 * Load student data if in edit mode
 */
onMounted(async () => {
  if (isEditMode.value) {
    await loadStudent()
  }
})

/**
 * Load student for editing
 */
async function loadStudent() {
  try {
    await studentStore.fetchStudentById(studentId.value)
    const student = studentStore.selectedStudent

    if (student) {
      formData.school_id = student.school_id
      formData.user_id = student.user_id
      formData.student_id = student.student_id
      formData.grade_level = student.grade_level
      formData.date_of_birth = student.date_of_birth
      formData.gender = student.gender || ''
      formData.enrollment_date = student.enrollment_date
      formData.graduation_date = student.graduation_date || ''
      formData.allergies = student.allergies || ''
      formData.medical_notes = student.medical_notes || ''
      formData.emergency_contact_name = student.emergency_contact_name || ''
      formData.emergency_contact_phone = student.emergency_contact_phone || ''
      formData.emergency_contact_relation = student.emergency_contact_relation || ''
      formData.photo_url = student.photo_url || ''
      formData.status = student.status
    }
  } catch (error: any) {
    formError.value = error.message || 'Failed to load student'
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
      await updateStudent()
    } else {
      await createStudent()
    }

    router.push('/students')
  } catch (error: any) {
    formError.value = error.message || 'Failed to save student'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Create new student
 */
async function createStudent() {
  // Get school_id from localStorage (set during login/session)
  const schoolId = localStorage.getItem('current_school_id') || formData.school_id

  const studentData: StudentCreateInput = {
    school_id: schoolId,
    user_id: formData.user_id,
    student_id: formData.student_id,
    grade_level: Number(formData.grade_level),
    date_of_birth: formData.date_of_birth,
    enrollment_date: formData.enrollment_date,
    status: formData.status as any,
  }

  // Add optional fields if provided
  if (formData.gender) studentData.gender = formData.gender as any
  if (formData.graduation_date) studentData.graduation_date = formData.graduation_date
  if (formData.allergies) studentData.allergies = formData.allergies
  if (formData.medical_notes) studentData.medical_notes = formData.medical_notes
  if (formData.emergency_contact_name) studentData.emergency_contact_name = formData.emergency_contact_name
  if (formData.emergency_contact_phone) studentData.emergency_contact_phone = formData.emergency_contact_phone
  if (formData.emergency_contact_relation) studentData.emergency_contact_relation = formData.emergency_contact_relation
  if (formData.photo_url) studentData.photo_url = formData.photo_url

  await studentStore.createStudent(studentData)
}

/**
 * Update existing student
 */
async function updateStudent() {
  const studentData: StudentUpdateInput = {
    grade_level: Number(formData.grade_level),
  }

  // Add optional fields if provided
  if (formData.gender) studentData.gender = formData.gender as any
  if (formData.graduation_date) studentData.graduation_date = formData.graduation_date
  if (formData.allergies) studentData.allergies = formData.allergies
  if (formData.medical_notes) studentData.medical_notes = formData.medical_notes
  if (formData.emergency_contact_name) studentData.emergency_contact_name = formData.emergency_contact_name
  if (formData.emergency_contact_phone) studentData.emergency_contact_phone = formData.emergency_contact_phone
  if (formData.emergency_contact_relation) studentData.emergency_contact_relation = formData.emergency_contact_relation
  if (formData.photo_url) studentData.photo_url = formData.photo_url
  if (formData.status) studentData.status = formData.status as any

  await studentStore.updateStudent(studentId.value, studentData)
}

/**
 * Navigate back to student list
 */
function goBack() {
  router.push('/students')
}

/**
 * Handle user selection from UserSelector
 */
function handleUserSelect(user: any) {
  console.log('Selected user:', user)
  // Optionally auto-populate fields from user data
  // For example, you could pre-fill emergency contact if it's in the user profile
}
</script>

<style scoped>
.student-form {
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
