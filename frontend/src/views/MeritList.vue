<template>
  <div class="merit-list">
    <div class="page-header">
      <h1>Merit System</h1>
      <button @click="handleAwardMerit" class="btn btn-primary">
        Award Merit
      </button>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Merits</div>
        <div class="stat-value">{{ statistics.total_merits }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Points</div>
        <div class="stat-value">{{ statistics.total_points }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Students Recognized</div>
        <div class="stat-value">{{ statistics.unique_students }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Per Student</div>
        <div class="stat-value">{{ statistics.average_per_student.toFixed(1) }}</div>
      </div>
    </div>

    <!-- Leaderboard -->
    <div v-if="leaderboard.length > 0" class="leaderboard-section">
      <h2>Merit Leaderboard - Top 10</h2>
      <div class="leaderboard-grid">
        <div
          v-for="entry in leaderboard"
          :key="entry.student_id"
          class="leaderboard-card"
        >
          <div class="rank-badge" :class="`rank-${entry.rank}`">
            {{ entry.rank }}
          </div>
          <div class="student-info">
            <div class="student-name">Student ID: {{ entry.student_id.substring(0, 8) }}</div>
            <div class="student-stats">
              {{ entry.total_points }} points • {{ entry.merit_count }} merits
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Category</label>
        <select v-model="localFilters.category">
          <option value="">All Categories</option>
          <option value="academic">Academic</option>
          <option value="behavior">Behavior</option>
          <option value="participation">Participation</option>
          <option value="leadership">Leadership</option>
          <option value="attendance">Attendance</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Quarter</label>
        <select v-model="localFilters.quarter">
          <option value="">All Quarters</option>
          <option value="Q1">Q1</option>
          <option value="Q2">Q2</option>
          <option value="Q3">Q3</option>
          <option value="Q4">Q4</option>
        </select>
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">Apply Filters</button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading merits...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Merits Table -->
    <div v-if="!loading && merits.length > 0" class="merits-table-container">
      <table class="merits-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Student</th>
            <th>Category</th>
            <th>Points</th>
            <th>Reason</th>
            <th>Awarded By</th>
            <th>Quarter</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="merit in merits" :key="merit.id" :class="{ 'recent-merit': merit.is_recent }">
            <td>
              <div class="date-cell">
                {{ formatDate(merit.awarded_date) }}
                <span v-if="merit.is_recent" class="recent-badge">New</span>
              </div>
            </td>
            <td>
              <div v-if="merit.student" class="student-cell">
                <div class="student-name">{{ merit.student.name }}</div>
                <div class="student-grade">Grade {{ merit.student.grade_level }}</div>
              </div>
              <div v-else class="text-muted">{{ merit.student_id.substring(0, 8) }}</div>
            </td>
            <td>
              <span class="category-badge" :class="`category-${merit.category}`">
                {{ merit.category_display }}
              </span>
            </td>
            <td>
              <div class="points-cell">
                <span class="points-value" :class="`tier-${merit.points_tier}`">
                  {{ merit.points }}
                </span>
                <span class="tier-badge">{{ merit.points_tier }}</span>
              </div>
            </td>
            <td>
              <div class="reason-cell">
                {{ truncateText(merit.reason, 60) }}
              </div>
            </td>
            <td>
              <div v-if="merit.awarded_by" class="teacher-name">
                {{ merit.awarded_by.name }}
              </div>
              <div v-else class="text-muted">-</div>
            </td>
            <td>
              <span v-if="merit.quarter" class="quarter-badge">
                {{ merit.quarter }}
              </span>
              <span v-else class="text-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && merits.length === 0" class="empty-state">
      <p>No merits found.</p>
      <button @click="handleAwardMerit" class="btn btn-primary">Award First Merit</button>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="pagination-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ totalMerits }} total)
      </span>
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useMeritStore } from '@/stores/meritStore'
import type { MeritFilters } from '@/types/merit'

const meritStore = useMeritStore()

// Hardcoded school ID for demo
const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

// Local state
const localFilters = ref<MeritFilters>({})

// Computed from store
const merits = computed(() => meritStore.merits)
const loading = computed(() => meritStore.loading)
const error = computed(() => meritStore.error)
const statistics = computed(() => meritStore.statistics)
const leaderboard = computed(() => meritStore.leaderboard)
const currentPage = computed(() => meritStore.currentPage)
const totalPages = computed(() => meritStore.totalPages)
const totalMerits = computed(() => meritStore.totalMerits)

// Methods
async function loadData() {
  try {
    await Promise.all([
      meritStore.fetchMerits(SCHOOL_ID, localFilters.value),
      meritStore.fetchStatistics(SCHOOL_ID),
      meritStore.fetchLeaderboard(SCHOOL_ID, undefined, undefined, 10),
    ])
  } catch (err) {
    console.error('Failed to load merit data:', err)
  }
}

function applyFilters() {
  loadData()
}

function clearFilters() {
  localFilters.value = {}
  meritStore.clearFilters()
  loadData()
}

function goToPage(page: number) {
  meritStore.setPage(page)
  loadData()
}

function handleAwardMerit() {
  // TODO: Open award merit modal or navigate to form
  console.log('Award merit')
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function truncateText(text: string, length: number): string {
  return text.length > length ? text.substring(0, length) + '...' : text
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.merit-list {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1a202c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 14px;
  color: #718096;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
}

.leaderboard-section {
  margin-bottom: 24px;
}

.leaderboard-section h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.leaderboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.leaderboard-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank-badge {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}

.rank-1 {
  background: #ffd700;
  color: #744210;
}

.rank-2 {
  background: #c0c0c0;
  color: #4a5568;
}

.rank-3 {
  background: #cd7f32;
  color: #fff;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 600;
  color: #2d3748;
}

.student-stats {
  font-size: 12px;
  color: #718096;
}

.filters {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  margin-bottom: 8px;
}

.filter-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.loading,
.error-message {
  text-align: center;
  padding: 40px;
  font-size: 16px;
}

.error-message {
  color: #e53e3e;
}

.merits-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.merits-table {
  width: 100%;
  border-collapse: collapse;
}

.merits-table thead {
  background-color: #f7fafc;
  border-bottom: 2px solid #e2e8f0;
}

.merits-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
}

.merits-table td {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.recent-merit {
  background-color: #f0fff4;
}

.date-cell {
  font-size: 14px;
}

.recent-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #48bb78;
  color: white;
  border-radius: 12px;
  font-size: 10px;
  margin-left: 8px;
}

.student-cell .student-name {
  font-weight: 600;
  color: #2d3748;
}

.student-cell .student-grade {
  font-size: 12px;
  color: #718096;
}

.category-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.category-academic {
  background: #bee3f8;
  color: #2c5282;
}

.category-behavior {
  background: #c6f6d5;
  color: #22543d;
}

.category-participation {
  background: #fed7d7;
  color: #742a2a;
}

.category-leadership {
  background: #fefcbf;
  color: #744210;
}

.category-attendance {
  background: #e9d8fd;
  color: #44337a;
}

.points-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.points-value {
  font-size: 18px;
  font-weight: 700;
}

.tier-bronze {
  color: #cd7f32;
}

.tier-silver {
  color: #94a3b8;
}

.tier-gold {
  color: #fbbf24;
}

.tier-platinum {
  color: #a78bfa;
}

.tier-badge {
  font-size: 10px;
  text-transform: uppercase;
  color: #718096;
}

.reason-cell {
  font-size: 14px;
  color: #4a5568;
}

.quarter-badge {
  padding: 4px 8px;
  background: #edf2f7;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background-color: #cbd5e0;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  color: #3b82f6;
}

.btn-link:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.empty-state p {
  font-size: 18px;
  color: #718096;
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.pagination-info {
  font-size: 14px;
  color: #718096;
}

.text-muted {
  color: #a0aec0;
}
</style>
