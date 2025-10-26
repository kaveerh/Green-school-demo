<template>
  <div class="activity-list">
    <div class="page-header">
      <h1>Extracurricular Activities</h1>
      <router-link to="/activities/create" class="btn btn-primary">
        Create Activity
      </router-link>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Activities</div>
        <div class="stat-value">{{ statistics.total_activities }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Enrollments</div>
        <div class="stat-value">{{ statistics.total_enrollments }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Enrollment</div>
        <div class="stat-value">{{ statistics.average_enrollment_per_activity.toFixed(1) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Revenue</div>
        <div class="stat-value">${{ statistics.total_revenue.toFixed(2) }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Activity Type</label>
        <select v-model="filters.activity_type">
          <option value="">All Types</option>
          <option value="sports">Sports</option>
          <option value="club">Club</option>
          <option value="art">Art</option>
          <option value="music">Music</option>
          <option value="academic">Academic</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="full">Full</option>
          <option value="cancelled">Cancelled</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Grade Level</label>
        <select v-model.number="filters.grade_level">
          <option :value="undefined">All Grades</option>
          <option :value="1">Grade 1</option>
          <option :value="2">Grade 2</option>
          <option :value="3">Grade 3</option>
          <option :value="4">Grade 4</option>
          <option :value="5">Grade 5</option>
          <option :value="6">Grade 6</option>
          <option :value="7">Grade 7</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Registration</label>
        <select v-model="filters.registration_open">
          <option :value="undefined">All</option>
          <option :value="true">Open</option>
          <option :value="false">Closed</option>
        </select>
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">
          Apply Filters
        </button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading activities...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Activities Table -->
    <div v-if="!loading && activities.length > 0" class="activities-table-container">
      <table class="activities-table">
        <thead>
          <tr>
            <th>Activity Name</th>
            <th>Type</th>
            <th>Grade Levels</th>
            <th>Enrollment</th>
            <th>Cost</th>
            <th>Status</th>
            <th>Registration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="activity in activities"
            :key="activity.id"
            :class="getRowClass(activity)"
          >
            <td>
              <div class="activity-title">
                <span class="activity-icon">{{ getActivityIcon(activity.activity_type) }}</span>
                <div>
                  <div class="title-text">
                    {{ activity.name }}
                    <span v-if="activity.is_featured" class="featured-badge">⭐</span>
                  </div>
                  <div v-if="activity.code" class="title-code">{{ activity.code }}</div>
                  <div v-if="activity.description" class="title-description">
                    {{ truncateText(activity.description, 60) }}
                  </div>
                </div>
              </div>
            </td>
            <td>
              <span
                class="activity-type-badge"
                :style="{ backgroundColor: getActivityTypeColor(activity.activity_type) }"
              >
                {{ getActivityTypeLabel(activity.activity_type) }}
              </span>
            </td>
            <td>
              <div class="grade-levels">
                {{ formatGradeLevels(activity.grade_levels) }}
              </div>
            </td>
            <td>
              <div class="enrollment-info">
                <div class="enrollment-count">
                  {{ activity.enrollment_count || 0 }}
                  {{ activity.max_participants ? ` / ${activity.max_participants}` : '' }}
                </div>
                <div
                  v-if="activity.max_participants"
                  class="enrollment-progress"
                  :style="{ width: getEnrollmentPercentage(activity) + '%' }"
                ></div>
              </div>
            </td>
            <td>
              <div class="cost-info">
                <div v-if="activity.total_cost && activity.total_cost > 0">
                  ${{ activity.total_cost.toFixed(2) }}
                </div>
                <div v-else class="text-muted">Free</div>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="`status-${getStatusColor(activity.status)}`">
                {{ getStatusLabel(activity.status) }}
              </span>
            </td>
            <td>
              <span
                class="registration-badge"
                :class="activity.registration_open ? 'open' : 'closed'"
              >
                {{ activity.registration_open ? 'Open' : 'Closed' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <router-link
                  :to="`/activities/${activity.id}/roster`"
                  class="btn btn-sm btn-secondary"
                  title="View Roster"
                >
                  Roster
                </router-link>
                <router-link
                  :to="`/activities/${activity.id}/edit`"
                  class="btn btn-sm btn-secondary"
                >
                  Edit
                </router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && activities.length === 0" class="empty-state">
      <p>No activities found.</p>
      <router-link to="/activities/create" class="btn btn-primary">
        Create Your First Activity
      </router-link>
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="pagination">
      <button
        @click="goToPage(page - 1)"
        :disabled="page === 1"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ page }} of {{ pages }} ({{ total }} total)
      </span>
      <button
        @click="goToPage(page + 1)"
        :disabled="page === pages"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useActivityStore } from '@/stores/activityStore'
import { storeToRefs } from 'pinia'
import type { ActivityFilters } from '@/types/activity'

const activityStore = useActivityStore()
const {
  activities,
  statistics,
  loading,
  error,
  total,
  page,
  pages
} = storeToRefs(activityStore)

// TODO: Get from auth store
const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

const filters = ref<ActivityFilters>({
  page: 1,
  limit: 50
})

onMounted(async () => {
  await Promise.all([
    activityStore.fetchActivities(SCHOOL_ID, filters.value),
    activityStore.fetchStatistics(SCHOOL_ID)
  ])
})

function applyFilters() {
  filters.value.page = 1
  activityStore.fetchActivities(SCHOOL_ID, filters.value)
}

function clearFilters() {
  filters.value = {
    page: 1,
    limit: 50
  }
  activityStore.fetchActivities(SCHOOL_ID, filters.value)
}

function goToPage(newPage: number) {
  filters.value.page = newPage
  activityStore.fetchActivities(SCHOOL_ID, filters.value)
}

function getRowClass(activity: any) {
  return {
    'row-featured': activity.is_featured,
    'row-full': activity.status === 'full',
    'row-cancelled': activity.status === 'cancelled'
  }
}

function getActivityIcon(type: string): string {
  const icons: Record<string, string> = {
    sports: '⚽',
    club: '🎯',
    art: '🎨',
    music: '🎵',
    academic: '📚',
    other: '✨'
  }
  return icons[type] || '📌'
}

function getActivityTypeColor(type: string): string {
  const colors: Record<string, string> = {
    sports: '#FF5722',
    club: '#9C27B0',
    art: '#E91E63',
    music: '#2196F3',
    academic: '#4CAF50',
    other: '#607D8B'
  }
  return colors[type] || '#9E9E9E'
}

function getActivityTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    sports: 'Sports',
    club: 'Club',
    art: 'Art',
    music: 'Music',
    academic: 'Academic',
    other: 'Other'
  }
  return labels[type] || type
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'green',
    full: 'orange',
    cancelled: 'red',
    completed: 'gray'
  }
  return colors[status] || 'gray'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    active: 'Active',
    full: 'Full',
    cancelled: 'Cancelled',
    completed: 'Completed'
  }
  return labels[status] || status
}

function formatGradeLevels(levels: number[]): string {
  if (!levels || levels.length === 0) return '—'
  const sorted = [...levels].sort((a, b) => a - b)
  if (sorted.length === 1) return `Grade ${sorted[0]}`
  if (sorted.length === 7) return 'All Grades'
  return `Grades ${sorted.join(', ')}`
}

function getEnrollmentPercentage(activity: any): number {
  if (!activity.max_participants) return 0
  return ((activity.enrollment_count || 0) / activity.max_participants) * 100
}

function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.activity-list {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1a202c;
}

.filters {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 0.875rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.loading,
.error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1rem;
}

.error-message {
  color: #e53e3e;
  background: #fff5f5;
  border: 1px solid #fc8181;
  border-radius: 8px;
}

.activities-table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.activities-table {
  width: 100%;
  border-collapse: collapse;
}

.activities-table th {
  background: #f7fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: #4a5568;
  border-bottom: 2px solid #e2e8f0;
}

.activities-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.activities-table tbody tr:hover {
  background: #f7fafc;
}

.row-featured {
  background: #fffbeb;
}

.row-full {
  background: #fff5f5;
}

.row-cancelled {
  opacity: 0.6;
}

.activity-title {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.activity-icon {
  font-size: 1.5rem;
}

.title-text {
  font-weight: 500;
  color: #1a202c;
  margin-bottom: 0.25rem;
}

.featured-badge {
  margin-left: 0.5rem;
}

.title-code {
  font-size: 0.75rem;
  color: #718096;
  font-family: monospace;
}

.title-description {
  font-size: 0.875rem;
  color: #718096;
  margin-top: 0.25rem;
}

.activity-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.grade-levels {
  font-size: 0.875rem;
  color: #4a5568;
}

.enrollment-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.enrollment-count {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1a202c;
}

.enrollment-progress {
  height: 4px;
  background: #48bb78;
  border-radius: 2px;
  transition: width 0.3s;
}

.cost-info {
  font-weight: 500;
  color: #1a202c;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-green {
  background: #c6f6d5;
  color: #22543d;
}

.status-orange {
  background: #feebc8;
  color: #7c2d12;
}

.status-red {
  background: #fed7d7;
  color: #742a2a;
}

.status-gray {
  background: #e2e8f0;
  color: #2d3748;
}

.registration-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.registration-badge.open {
  background: #c6f6d5;
  color: #22543d;
}

.registration-badge.closed {
  background: #e2e8f0;
  color: #2d3748;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state p {
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

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover {
  background: #3182ce;
}

.btn-secondary {
  background: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  background: transparent;
  color: #4299e1;
  padding: 0.5rem;
}

.btn-link:hover {
  color: #3182ce;
  background: transparent;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}

.text-muted {
  color: #a0aec0;
}
</style>
