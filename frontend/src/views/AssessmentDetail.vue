<template>
  <div class="assessment-detail">
    <div class="header">
      <h1 class="title">Assessment Details</h1>
      <router-link to="/assessments" class="btn btn-secondary">Back to List</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="assessment && !loading" class="content">
      <!-- Assessment Info Card -->
      <div class="info-card">
        <div class="card-header">
          <h2 class="card-title">{{ assessment.title }}</h2>
          <span :class="`status-badge status-${assessment.status}`">
            {{ getStatusLabel(assessment.status) }}
          </span>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Student:</span>
            <span class="info-value">{{ assessment.student?.name || assessment.student_id }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Subject:</span>
            <span class="info-value">{{ assessment.subject?.name || 'N/A' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Class:</span>
            <span class="info-value">{{ assessment.class?.name || 'N/A' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Teacher:</span>
            <span class="info-value">{{ assessment.teacher?.name || 'N/A' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Type:</span>
            <span class="info-value">{{ getTypeLabel(assessment.assessment_type) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Quarter:</span>
            <span class="info-value">{{ assessment.quarter }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Assessment Date:</span>
            <span class="info-value">{{ formatDate(assessment.assessment_date) }}</span>
          </div>

          <div class="info-item" v-if="assessment.due_date">
            <span class="info-label">Due Date:</span>
            <span class="info-value">{{ formatDate(assessment.due_date) }}</span>
          </div>
        </div>

        <div v-if="assessment.description" class="description">
          <h3 class="description-title">Description</h3>
          <p>{{ assessment.description }}</p>
        </div>

        <div class="actions">
          <router-link v-if="!assessment.is_graded" :to="`/assessments/${assessment.id}/edit`" class="btn btn-primary">
            Edit
          </router-link>
          <button @click="handleDelete" class="btn btn-danger">Delete</button>
        </div>
      </div>

      <!-- Grading Card -->
      <div class="grading-card">
        <h2 class="card-title">Grading</h2>

        <div class="grading-info">
          <div class="grade-item">
            <span class="grade-label">Total Points:</span>
            <span class="grade-value">{{ assessment.total_points }}</span>
          </div>

          <div class="grade-item" v-if="assessment.is_graded">
            <span class="grade-label">Points Earned:</span>
            <span class="grade-value">{{ assessment.points_earned }}</span>
          </div>

          <div class="grade-item" v-if="assessment.is_graded">
            <span class="grade-label">Percentage:</span>
            <span :class="['grade-value', assessment.is_passing ? 'passing' : 'failing']">
              {{ assessment.percentage?.toFixed(1) }}%
            </span>
          </div>

          <div class="grade-item" v-if="assessment.is_graded">
            <span class="grade-label">Letter Grade:</span>
            <span :class="['grade-value', 'letter-grade', assessment.is_passing ? 'passing' : 'failing']">
              {{ assessment.letter_grade }}
            </span>
          </div>

          <div class="grade-item">
            <span class="grade-label">Weight:</span>
            <span class="grade-value">{{ assessment.weight }}</span>
          </div>

          <div class="grade-item" v-if="assessment.is_extra_credit">
            <span class="badge badge-info">Extra Credit</span>
          </div>

          <div class="grade-item" v-if="assessment.is_makeup">
            <span class="badge badge-warning">Makeup</span>
          </div>
        </div>

        <!-- Feedback -->
        <div v-if="assessment.feedback" class="feedback">
          <h3 class="feedback-title">Feedback</h3>
          <p>{{ assessment.feedback }}</p>
        </div>

        <!-- Grade Form (if not yet graded) -->
        <div v-if="!assessment.is_graded" class="grade-form">
          <h3 class="form-title">Grade This Assessment</h3>

          <form @submit.prevent="handleGrade">
            <div class="form-group">
              <label for="points_earned" class="label">Points Earned *</label>
              <input
                id="points_earned"
                v-model.number="gradeForm.points_earned"
                type="number"
                min="0"
                :max="assessment.total_points"
                step="0.1"
                required
                class="input"
                placeholder="0"
              />
              <span class="help-text">Out of {{ assessment.total_points }} points</span>
            </div>

            <div class="form-group">
              <label for="feedback" class="label">Feedback</label>
              <textarea
                id="feedback"
                v-model="gradeForm.feedback"
                rows="4"
                class="input"
                placeholder="Provide feedback to the student..."
              />
            </div>

            <button type="submit" :disabled="grading" class="btn btn-success">
              {{ grading ? 'Grading...' : 'Submit Grade' }}
            </button>
          </form>
        </div>

        <!-- Already Graded Info -->
        <div v-else class="graded-info">
          <p class="graded-text">✓ Graded on {{ formatDateTime(assessment.graded_at!) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessmentStore'
import type { AssessmentGradeRequest } from '@/types/assessment'

const router = useRouter()
const route = useRoute()
const assessmentStore = useAssessmentStore()

const assessmentId = computed(() => route.params.id as string)
const assessment = computed(() => assessmentStore.currentAssessment)

const loading = ref(false)
const grading = ref(false)
const error = ref<string | null>(null)

const gradeForm = ref<AssessmentGradeRequest>({
  points_earned: 0,
  feedback: ''
})

// Methods
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pending',
    submitted: 'Submitted',
    graded: 'Graded',
    returned: 'Returned',
    late: 'Late',
    missing: 'Missing',
    excused: 'Excused'
  }
  return labels[status] || status
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    test: 'Test',
    quiz: 'Quiz',
    project: 'Project',
    assignment: 'Assignment',
    exam: 'Exam',
    presentation: 'Presentation',
    homework: 'Homework',
    lab: 'Lab',
    other: 'Other'
  }
  return labels[type] || type
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

async function loadAssessment() {
  loading.value = true
  error.value = null

  try {
    await assessmentStore.fetchAssessmentById(assessmentId.value)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load assessment'
    console.error('Failed to load assessment:', err)
  } finally {
    loading.value = false
  }
}

async function handleGrade() {
  if (!assessment.value) return

  grading.value = true
  error.value = null

  try {
    await assessmentStore.gradeAssessment(assessmentId.value, gradeForm.value)
    alert('Assessment graded successfully!')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to grade assessment'
    console.error('Failed to grade assessment:', err)
    alert(error.value)
  } finally {
    grading.value = false
  }
}

async function handleDelete() {
  if (!confirm('Are you sure you want to delete this assessment?')) return

  try {
    await assessmentStore.deleteAssessment(assessmentId.value)
    alert('Assessment deleted successfully!')
    router.push('/assessments')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to delete assessment'
    console.error('Failed to delete assessment:', err)
    alert(error.value)
  }
}

// Lifecycle
onMounted(async () => {
  await loadAssessment()
})
</script>

<style scoped>
.assessment-detail {
  padding: 2rem;
  max-width: 1200px;
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
}

.content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.info-card,
.grading-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 2rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
}

.status-badge {
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending { background: #fef5e7; color: #d97706; }
.status-submitted { background: #dbeafe; color: #2563eb; }
.status-graded { background: #dcfce7; color: #16a34a; }
.status-returned { background: #f3e8ff; color: #9333ea; }
.status-late { background: #fee2e2; color: #dc2626; }
.status-missing { background: #fef2f2; color: #991b1b; }
.status-excused { background: #f1f5f9; color: #475569; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 0.875rem;
  color: #2d3748;
}

.description {
  margin-bottom: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.description-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.description p {
  font-size: 0.875rem;
  color: #4a5568;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.grading-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.grade-item {
  display: flex;
  flex-direction: column;
}

.grade-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.grade-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
}

.grade-value.passing {
  color: #16a34a;
}

.grade-value.failing {
  color: #dc2626;
}

.grade-value.letter-grade {
  font-size: 2rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-info {
  background: #dbeafe;
  color: #2563eb;
}

.badge-warning {
  background: #fef5e7;
  color: #d97706;
}

.feedback {
  margin-bottom: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.feedback-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.feedback p {
  font-size: 0.875rem;
  color: #4a5568;
  line-height: 1.6;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 0.375rem;
}

.grade-form {
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.form-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
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
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

textarea.input {
  resize: vertical;
  min-height: 100px;
}

.help-text {
  display: block;
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}

.graded-info {
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.graded-text {
  font-size: 0.875rem;
  color: #16a34a;
  font-weight: 600;
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
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .info-grid,
  .grading-info {
    grid-template-columns: 1fr;
  }
}
</style>
