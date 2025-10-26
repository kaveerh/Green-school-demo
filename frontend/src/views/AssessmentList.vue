<template>
  <div class="assessment-list">
    <div class="header">
      <h1 class="title">Assessments</h1>
      <router-link to="/assessments/create" class="btn btn-primary">Create Assessment</router-link>
    </div>

    <!-- Filters -->
    <div class="filters">
      <select v-model="quarterFilter" class="filter-select" @change="handleFilter">
        <option value="">All Quarters</option>
        <option value="Q1">Quarter 1</option>
        <option value="Q2">Quarter 2</option>
        <option value="Q3">Quarter 3</option>
        <option value="Q4">Quarter 4</option>
      </select>

      <select v-model="statusFilter" class="filter-select" @change="handleFilter">
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="submitted">Submitted</option>
        <option value="graded">Graded</option>
        <option value="returned">Returned</option>
        <option value="late">Late</option>
        <option value="missing">Missing</option>
        <option value="excused">Excused</option>
      </select>

      <select v-model="typeFilter" class="filter-select" @change="handleFilter">
        <option value="">All Types</option>
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

    <!-- Statistics -->
    <div v-if="statistics" class="stats-cards">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_assessments }}</div>
        <div class="stat-label">Total Assessments</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.graded_assessments }}</div>
        <div class="stat-label">Graded</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.pending_assessments }}</div>
        <div class="stat-label">Pending</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.average_score.toFixed(1) }}%</div>
        <div class="stat-label">Average Score</div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">Loading assessments...</div>

    <!-- Error -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Assessments List -->
    <div v-if="!loading && hasAssessments" class="assessments-grid">
      <div v-for="assessment in assessments" :key="assessment.id" class="assessment-card">
        <div class="assessment-header">
          <h3 class="assessment-title">{{ assessment.title }}</h3>
          <span :class="`status-badge status-${assessment.status}`">
            {{ getStatusLabel(assessment.status) }}
          </span>
        </div>

        <div class="assessment-details">
          <div class="detail">
            <span class="label">Student:</span>
            <span>{{ assessment.student?.name || assessment.student_id }}</span>
          </div>
          <div class="detail">
            <span class="label">Subject:</span>
            <span>{{ assessment.subject?.name || assessment.subject_id }}</span>
          </div>
          <div class="detail">
            <span class="label">Type:</span>
            <span>{{ getTypeLabel(assessment.assessment_type) }}</span>
          </div>
          <div class="detail">
            <span class="label">Quarter:</span>
            <span>{{ assessment.quarter }}</span>
          </div>
          <div class="detail">
            <span class="label">Date:</span>
            <span>{{ formatDate(assessment.assessment_date) }}</span>
          </div>
          <div class="detail">
            <span class="label">Points:</span>
            <span>{{ assessment.points_earned || '—' }} / {{ assessment.total_points }}</span>
          </div>
          <div class="detail">
            <span class="label">Grade:</span>
            <span :class="getGradeClass(assessment)">{{ assessment.grade_display }}</span>
          </div>
        </div>

        <div v-if="assessment.description" class="assessment-description">
          {{ assessment.description }}
        </div>

        <div v-if="assessment.is_overdue" class="overdue-notice">
          ⚠️ Past Due
        </div>

        <div class="assessment-actions">
          <router-link :to="`/assessments/${assessment.id}`" class="btn btn-sm btn-secondary">
            View
          </router-link>
          <router-link
            v-if="!assessment.is_graded"
            :to="`/assessments/${assessment.id}/edit`"
            class="btn btn-sm btn-secondary"
          >
            Edit
          </router-link>
          <router-link
            v-if="!assessment.is_graded"
            :to="`/assessments/${assessment.id}/grade`"
            class="btn btn-sm btn-success"
          >
            Grade
          </router-link>
          <button @click="handleDelete(assessment.id)" class="btn btn-sm btn-danger">Delete</button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !hasAssessments" class="empty-state">
      <p>No assessments found.</p>
      <router-link to="/assessments/create" class="btn btn-primary">
        Create Your First Assessment
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="total > 50" class="pagination">
      <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)" class="btn btn-sm">
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} ({{ total }} total)
      </span>
      <button :disabled="assessments.length < 50" @click="goToPage(currentPage + 1)" class="btn btn-sm">
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAssessmentStore } from '@/stores/assessmentStore'
import type { Assessment, AssessmentStatus, AssessmentType, Quarter } from '@/types/assessment'

const router = useRouter()
const assessmentStore = useAssessmentStore()

const quarterFilter = ref<Quarter | ''>('')
const statusFilter = ref<AssessmentStatus | ''>('')
const typeFilter = ref<AssessmentType | ''>('')
const currentSchoolId = ref('60da2256-81fc-4ca5-bf6b-467b8d371c61') // TODO: Get from auth/school context
const currentTeacherId = ref('fa4a570e-6ced-42e8-ab2f-beaf59b11a89') // TODO: Get from auth context

// Computed
const assessments = computed(() => assessmentStore.assessments)
const loading = computed(() => assessmentStore.loading)
const error = computed(() => assessmentStore.error)
const hasAssessments = computed(() => assessmentStore.hasAssessments)
const currentPage = computed(() => assessmentStore.currentPage)
const total = computed(() => assessmentStore.total)
const statistics = computed(() => assessmentStore.statistics)

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

function getGradeClass(assessment: Assessment): string {
  if (!assessment.is_graded) return ''
  if (assessment.is_passing) return 'grade-passing'
  return 'grade-failing'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

async function handleFilter() {
  await fetchAssessments()
}

async function fetchAssessments() {
  try {
    await assessmentStore.fetchTeacherAssessments({
      teacher_id: currentTeacherId.value,
      quarter: quarterFilter.value || undefined,
      status: statusFilter.value || undefined,
      page: currentPage.value,
      limit: 50
    })
  } catch (err) {
    console.error('Failed to fetch assessments:', err)
  }
}

async function fetchStatistics() {
  try {
    await assessmentStore.fetchStatistics({
      school_id: currentSchoolId.value,
      quarter: quarterFilter.value || undefined
    })
  } catch (err) {
    console.error('Failed to fetch statistics:', err)
  }
}

async function goToPage(page: number) {
  try {
    await assessmentStore.fetchTeacherAssessments({
      teacher_id: currentTeacherId.value,
      quarter: quarterFilter.value || undefined,
      status: statusFilter.value || undefined,
      page,
      limit: 50
    })
  } catch (err) {
    console.error('Failed to fetch page:', err)
  }
}

async function handleDelete(id: string) {
  if (!confirm('Are you sure you want to delete this assessment?')) return

  try {
    await assessmentStore.deleteAssessment(id)
  } catch (err) {
    console.error('Failed to delete assessment:', err)
    alert('Failed to delete assessment')
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([fetchAssessments(), fetchStatistics()])
})
</script>

<style scoped>
.assessment-list {
  padding: 2rem;
  max-width: 1400px;
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

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.loading,
.error {
  text-align: center;
  padding: 2rem;
  font-size: 1.125rem;
}

.error {
  color: #e53e3e;
}

.assessments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.assessment-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.assessment-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.assessment-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.assessment-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  flex: 1;
  margin-right: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-pending {
  background: #fef5e7;
  color: #d97706;
}

.status-submitted {
  background: #dbeafe;
  color: #2563eb;
}

.status-graded {
  background: #dcfce7;
  color: #16a34a;
}

.status-returned {
  background: #f3e8ff;
  color: #9333ea;
}

.status-late {
  background: #fee2e2;
  color: #dc2626;
}

.status-missing {
  background: #fef2f2;
  color: #991b1b;
}

.status-excused {
  background: #f1f5f9;
  color: #475569;
}

.assessment-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail {
  font-size: 0.875rem;
}

.label {
  font-weight: 600;
  color: #4a5568;
  margin-right: 0.5rem;
}

.grade-passing {
  color: #16a34a;
  font-weight: 600;
}

.grade-failing {
  color: #dc2626;
  font-weight: 600;
}

.assessment-description {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.overdue-notice {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.assessment-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state p {
  font-size: 1.125rem;
  color: #718096;
  margin-bottom: 1.5rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  font-size: 0.875rem;
  color: #4a5568;
}
</style>
