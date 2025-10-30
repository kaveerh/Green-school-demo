<template>
  <div class="lesson-list">
    <div class="header">
      <h1 class="title">Lessons</h1>
      <router-link to="/lessons/create" class="btn btn-primary">Create Lesson</router-link>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search lessons..."
        class="search-input"
        @input="handleSearch"
      />
      <select v-model="statusFilter" class="filter-select" @change="handleFilter">
        <option value="">All Statuses</option>
        <option value="draft">Draft</option>
        <option value="scheduled">Scheduled</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">Loading lessons...</div>

    <!-- Error -->
    <div v-if="error" class="error">
      {{ error }}
    </div>

    <!-- Lessons List -->
    <div v-if="!loading && hasLessons" class="lessons-grid">
      <div v-for="lesson in lessons" :key="lesson.id" class="lesson-card">
        <div class="lesson-header">
          <h3 class="lesson-title">{{ lesson.title }}</h3>
          <span :class="`status-badge status-${lesson.status}`">
            {{ getLessonStatusLabel(lesson.status) }}
          </span>
        </div>

        <div class="lesson-details">
          <div class="detail">
            <span class="label">Class:</span>
            <span>{{ lesson.class_name || lesson.class_id }}</span>
          </div>
          <div class="detail">
            <span class="label">Subject:</span>
            <span>{{ lesson.subject_name || lesson.subject_id }}</span>
          </div>
          <div class="detail">
            <span class="label">Teacher:</span>
            <span>{{ lesson.teacher_name || 'N/A' }}</span>
          </div>
          <div class="detail">
            <span class="label">Scheduled:</span>
            <span>{{ formatDate(lesson.scheduled_date) }}</span>
          </div>
          <div class="detail">
            <span class="label">Duration:</span>
            <span>{{ lesson.duration_display || `${lesson.duration_minutes}m` }}</span>
          </div>
          <div class="detail">
            <span class="label">Lesson #:</span>
            <span>{{ lesson.lesson_number }}</span>
          </div>
        </div>

        <div v-if="lesson.description" class="lesson-description">
          {{ lesson.description }}
        </div>

        <div class="lesson-actions">
          <router-link :to="`/lessons/${lesson.id}`" class="btn btn-sm btn-secondary">
            View
          </router-link>
          <router-link :to="`/lessons/${lesson.id}/edit`" class="btn btn-sm btn-secondary">
            Edit
          </router-link>
          <button v-if="canStart(lesson)" @click="handleStart(lesson.id)" class="btn btn-sm btn-success">
            Start
          </button>
          <button v-if="canComplete(lesson)" @click="handleComplete(lesson.id)" class="btn btn-sm btn-success">
            Complete
          </button>
          <button @click="handleDelete(lesson.id)" class="btn btn-sm btn-danger">Delete</button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !hasLessons" class="empty-state">
      <p>No lessons found.</p>
      <router-link to="/lessons/create" class="btn btn-primary">Create Your First Lesson</router-link>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="btn btn-sm"
      >
        Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="btn btn-sm"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLessonStore } from '@/stores/lessonStore'
import { useSchool } from '@/composables/useSchool'
import { LessonStatusLabels } from '@/types/lesson'
import type { Lesson } from '@/types/lesson'

const lessonStore = useLessonStore()

const searchQuery = ref('')
const statusFilter = ref('')
const { currentSchoolId } = useSchool()

// Computed
const lessons = computed(() => lessonStore.lessons)
const loading = computed(() => lessonStore.loading)
const error = computed(() => lessonStore.error)
const hasLessons = computed(() => lessonStore.hasLessons)
const currentPage = computed(() => lessonStore.currentPage)
const totalPages = computed(() => lessonStore.totalPages)

// Methods
function getLessonStatusLabel(status: string): string {
  return LessonStatusLabels[status as keyof typeof LessonStatusLabels] || status
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function canStart(lesson: Lesson): boolean {
  return lesson.status === 'draft' || lesson.status === 'scheduled'
}

function canComplete(lesson: Lesson): boolean {
  return lesson.status === 'scheduled' || lesson.status === 'in_progress'
}

async function loadLessons(page = 1) {
  try {
    await lessonStore.fetchLessons(currentSchoolId.value, {
      page,
      limit: 20,
      status: statusFilter.value || undefined
    })
  } catch (err) {
    console.error('Failed to load lessons:', err)
  }
}

async function handleSearch() {
  if (searchQuery.value.trim()) {
    try {
      await lessonStore.searchLessons(currentSchoolId.value, {
        query: searchQuery.value
      })
    } catch (err) {
      console.error('Failed to search lessons:', err)
    }
  } else {
    loadLessons()
  }
}

async function handleFilter() {
  loadLessons()
}

async function handleStart(id: string) {
  if (confirm('Start this lesson?')) {
    try {
      await lessonStore.startLesson(id)
    } catch (err) {
      console.error('Failed to start lesson:', err)
      alert('Failed to start lesson')
    }
  }
}

async function handleComplete(id: string) {
  if (confirm('Mark this lesson as complete?')) {
    try {
      await lessonStore.completeLesson(id, {
        completion_percentage: 100
      })
    } catch (err) {
      console.error('Failed to complete lesson:', err)
      alert('Failed to complete lesson')
    }
  }
}

async function handleDelete(id: string) {
  if (confirm('Are you sure you want to delete this lesson?')) {
    try {
      await lessonStore.deleteLesson(id)
    } catch (err) {
      console.error('Failed to delete lesson:', err)
      alert('Failed to delete lesson')
    }
  }
}

function goToPage(page: number) {
  loadLessons(page)
}

onMounted(() => {
  loadLessons()
})
</script>

<style scoped>
.lesson-list {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 150px;
}

.loading,
.error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #ef4444;
  background-color: #fee2e2;
  border-radius: 4px;
}

.lessons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.lesson-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: white;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.lesson-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-draft {
  background-color: #f3f4f6;
  color: #6b7280;
}

.status-scheduled {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-in_progress {
  background-color: #fed7aa;
  color: #c2410c;
}

.status-completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background-color: #fee2e2;
  color: #991b1b;
}

.lesson-details {
  margin-bottom: 12px;
}

.detail {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 14px;
}

.detail .label {
  font-weight: 500;
  color: #6b7280;
}

.lesson-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
  line-height: 1.5;
}

.lesson-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-info {
  color: #6b7280;
  font-size: 14px;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover {
  background-color: #059669;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
