<template>
  <div class="assessment-form">
    <div class="header">
      <h1 class="title">{{ isEditing ? 'Edit Assessment' : 'Create Assessment' }}</h1>
      <router-link to="/assessments" class="btn btn-secondary">Back to List</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <form v-if="!loading" @submit.prevent="handleSubmit" class="form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2 class="section-title">Basic Information</h2>

        <div class="form-group">
          <label for="title" class="label">Title *</label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            required
            class="input"
            placeholder="Chapter 5 Test"
          />
        </div>

        <div class="form-group">
          <label for="description" class="label">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            class="input"
            placeholder="Describe the assessment..."
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="assessment_type" class="label">Type *</label>
            <select id="assessment_type" v-model="form.assessment_type" required class="input">
              <option value="">Select type</option>
              <option value="test">Test</option>
              <option value="quiz">Quiz</option>
              <option value="project">Project</option>
              <option value="assignment">Assignment</option>
              <option value="exam">Exam</option>
              <option value="presentation">Presentation</option>
              <option value="homework">Homework</option>
              <option value="lab">Lab</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label for="quarter" class="label">Quarter *</label>
            <select id="quarter" v-model="form.quarter" required class="input">
              <option value="">Select quarter</option>
              <option value="Q1">Quarter 1</option>
              <option value="Q2">Quarter 2</option>
              <option value="Q3">Quarter 3</option>
              <option value="Q4">Quarter 4</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Assignment Details -->
      <div class="form-section">
        <h2 class="section-title">Assignment Details</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="student_id" class="label">Student *</label>
            <select id="student_id" v-model="form.student_id" required class="input" :disabled="isEditing">
              <option value="">Select student</option>
              <option value="c7d715a4-cca0-4133-9a6d-172d585a10e6">Alice Johnson (Grade 5)</option>
              <!-- TODO: Load from students store -->
            </select>
          </div>

          <div class="form-group">
            <label for="class_id" class="label">Class *</label>
            <select id="class_id" v-model="form.class_id" required class="input" :disabled="isEditing">
              <option value="">Select class</option>
              <option value="2e008ff4-dc05-4c6b-8059-ca92fceb3f9a">Math Grade 5 Q1 A</option>
              <!-- TODO: Load from classes store -->
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="subject_id" class="label">Subject *</label>
            <select id="subject_id" v-model="form.subject_id" required class="input" :disabled="isEditing">
              <option value="">Select subject</option>
              <option value="94473bd5-c1de-4e8c-9ef3-bde10cacc143">Mathematics</option>
              <option value="4b01652c-ecf4-440e-ba17-bc81da0580ba">Science</option>
              <!-- TODO: Load from subjects store -->
            </select>
          </div>

          <div class="form-group">
            <label for="teacher_id" class="label">Teacher *</label>
            <select id="teacher_id" v-model="form.teacher_id" required class="input" :disabled="isEditing">
              <option value="">Select teacher</option>
              <option value="fa4a570e-6ced-42e8-ab2f-beaf59b11a89">Demo Teacher</option>
              <!-- TODO: Load from teachers store -->
            </select>
          </div>
        </div>
      </div>

      <!-- Dates and Grading -->
      <div class="form-section">
        <h2 class="section-title">Dates and Grading</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="assessment_date" class="label">Assessment Date *</label>
            <input
              id="assessment_date"
              v-model="form.assessment_date"
              type="date"
              required
              class="input"
            />
          </div>

          <div class="form-group">
            <label for="due_date" class="label">Due Date</label>
            <input
              id="due_date"
              v-model="form.due_date"
              type="date"
              class="input"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="total_points" class="label">Total Points *</label>
            <input
              id="total_points"
              v-model.number="form.total_points"
              type="number"
              min="0"
              step="0.1"
              required
              class="input"
              placeholder="100"
            />
          </div>

          <div class="form-group">
            <label for="weight" class="label">Weight</label>
            <input
              id="weight"
              v-model.number="form.weight"
              type="number"
              min="0"
              max="10"
              step="0.1"
              class="input"
              placeholder="1.0"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.is_extra_credit" type="checkbox" class="checkbox" />
              Extra Credit
            </label>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.is_makeup" type="checkbox" class="checkbox" />
              Makeup Assessment
            </label>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="submit" :disabled="submitting" class="btn btn-primary">
          {{ submitting ? 'Saving...' : (isEditing ? 'Update Assessment' : 'Create Assessment') }}
        </button>
        <router-link to="/assessments" class="btn btn-secondary">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessmentStore'
import { useSchool } from '@/composables/useSchool'
import type { AssessmentCreateRequest, AssessmentUpdateRequest } from '@/types/assessment'

const router = useRouter()
const route = useRoute()
const assessmentStore = useAssessmentStore()

const assessmentId = computed(() => route.params.id as string)
const isEditing = computed(() => !!assessmentId.value && route.name !== 'assessment-create')

const { currentSchoolId } = useSchool()

const form = ref<Partial<AssessmentCreateRequest>>({
  school_id: currentSchoolId.value,
  student_id: '',
  class_id: '',
  subject_id: '',
  teacher_id: '',
  title: '',
  description: '',
  assessment_type: 'test' as any,
  quarter: '' as any,
  assessment_date: '',
  due_date: '',
  total_points: 100,
  weight: 1.0,
  is_extra_credit: false,
  is_makeup: false
})

const loading = ref(false)
const submitting = ref(false)
const error = ref<string | null>(null)

// Methods
async function loadAssessment() {
  if (!isEditing.value) return

  loading.value = true
  error.value = null

  try {
    const assessment = await assessmentStore.fetchAssessmentById(assessmentId.value)

    // Populate form with existing data
    form.value = {
      school_id: assessment.school_id,
      student_id: assessment.student_id,
      class_id: assessment.class_id,
      subject_id: assessment.subject_id,
      teacher_id: assessment.teacher_id,
      title: assessment.title,
      description: assessment.description,
      assessment_type: assessment.assessment_type,
      quarter: assessment.quarter,
      assessment_date: assessment.assessment_date,
      due_date: assessment.due_date,
      total_points: assessment.total_points,
      weight: assessment.weight,
      is_extra_credit: assessment.is_extra_credit,
      is_makeup: assessment.is_makeup
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load assessment'
    console.error('Failed to load assessment:', err)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  submitting.value = true
  error.value = null

  try {
    if (isEditing.value) {
      // Update existing assessment
      const updateData: AssessmentUpdateRequest = {
        title: form.value.title,
        description: form.value.description,
        assessment_type: form.value.assessment_type,
        assessment_date: form.value.assessment_date,
        due_date: form.value.due_date,
        total_points: form.value.total_points,
        weight: form.value.weight,
        is_extra_credit: form.value.is_extra_credit,
        is_makeup: form.value.is_makeup
      }

      await assessmentStore.updateAssessment(assessmentId.value, updateData)
      alert('Assessment updated successfully!')
      router.push(`/assessments/${assessmentId.value}`)
    } else {
      // Create new assessment
      const newAssessment = await assessmentStore.createAssessment(form.value as AssessmentCreateRequest)
      alert('Assessment created successfully!')
      router.push(`/assessments/${newAssessment.id}`)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save assessment'
    console.error('Failed to save assessment:', err)
    alert(error.value)
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadAssessment()
})
</script>

<style scoped>
.assessment-form {
  padding: 2rem;
  max-width: 900px;
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
  font-weight: 700;
  color: #1a202c;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.125rem;
}

.error {
  color: #e53e3e;
  background: #fee2e2;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
}

.form {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input:disabled {
  background: #f7fafc;
  color: #a0aec0;
  cursor: not-allowed;
}

textarea.input {
  resize: vertical;
  min-height: 80px;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
}

.checkbox {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  padding-top: 2rem;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
