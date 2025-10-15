<template>
  <div class="user-statistics">
    <h2>User Statistics</h2>

    <!-- Loading State -->
    <div v-if="userStore.isLoading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading statistics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="userStore.hasError" class="error-container">
      <p>{{ userStore.error }}</p>
      <button @click="loadStatistics" class="btn-retry">Retry</button>
    </div>

    <!-- Statistics Cards -->
    <div v-else-if="stats" class="statistics-grid">
      <!-- Total Users Card -->
      <div class="stat-card total-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <p class="stat-label">Total Users</p>
          <p class="stat-value">{{ stats.total }}</p>
        </div>
      </div>

      <!-- Active Users Card -->
      <div class="stat-card active-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <p class="stat-label">Active Users</p>
          <p class="stat-value">{{ stats.by_status.active }}</p>
          <p class="stat-percentage">{{ calculatePercentage(stats.by_status.active) }}%</p>
        </div>
      </div>

      <!-- Inactive Users Card -->
      <div class="stat-card inactive-card">
        <div class="stat-icon">⏸️</div>
        <div class="stat-content">
          <p class="stat-label">Inactive Users</p>
          <p class="stat-value">{{ stats.by_status.inactive }}</p>
          <p class="stat-percentage">{{ calculatePercentage(stats.by_status.inactive) }}%</p>
        </div>
      </div>

      <!-- Suspended Users Card -->
      <div class="stat-card suspended-card">
        <div class="stat-icon">🚫</div>
        <div class="stat-content">
          <p class="stat-label">Suspended Users</p>
          <p class="stat-value">{{ stats.by_status.suspended }}</p>
          <p class="stat-percentage">{{ calculatePercentage(stats.by_status.suspended) }}%</p>
        </div>
      </div>

      <!-- Persona Breakdown Card -->
      <div class="stat-card persona-card wide-card">
        <h3>Users by Persona</h3>
        <div class="persona-grid">
          <div class="persona-item">
            <div class="persona-bar" :style="{ width: getPersonaPercentage('administrators') + '%' }">
              <span class="persona-label">Administrators</span>
            </div>
            <span class="persona-count">{{ stats.by_persona.administrators }}</span>
          </div>

          <div class="persona-item">
            <div class="persona-bar teacher-bar" :style="{ width: getPersonaPercentage('teachers') + '%' }">
              <span class="persona-label">Teachers</span>
            </div>
            <span class="persona-count">{{ stats.by_persona.teachers }}</span>
          </div>

          <div class="persona-item">
            <div class="persona-bar student-bar" :style="{ width: getPersonaPercentage('students') + '%' }">
              <span class="persona-label">Students</span>
            </div>
            <span class="persona-count">{{ stats.by_persona.students }}</span>
          </div>

          <div class="persona-item">
            <div class="persona-bar parent-bar" :style="{ width: getPersonaPercentage('parents') + '%' }">
              <span class="persona-label">Parents</span>
            </div>
            <span class="persona-count">{{ stats.by_persona.parents }}</span>
          </div>

          <div class="persona-item">
            <div class="persona-bar vendor-bar" :style="{ width: getPersonaPercentage('vendors') + '%' }">
              <span class="persona-label">Vendors</span>
            </div>
            <span class="persona-count">{{ stats.by_persona.vendors }}</span>
          </div>
        </div>
      </div>

      <!-- Status Pie Chart Visualization -->
      <div class="stat-card chart-card">
        <h3>Status Distribution</h3>
        <div class="pie-chart">
          <svg viewBox="0 0 100 100" class="pie-svg">
            <circle
              v-for="(segment, index) in pieSegments"
              :key="index"
              cx="50"
              cy="50"
              r="25"
              fill="transparent"
              :stroke="segment.color"
              stroke-width="50"
              :stroke-dasharray="segment.dashArray"
              :stroke-dashoffset="segment.dashOffset"
              :class="`pie-segment-${segment.name}`"
            />
          </svg>
          <div class="pie-legend">
            <div class="legend-item">
              <span class="legend-color active"></span>
              <span>Active ({{ stats.by_status.active }})</span>
            </div>
            <div class="legend-item">
              <span class="legend-color inactive"></span>
              <span>Inactive ({{ stats.by_status.inactive }})</span>
            </div>
            <div class="legend-item">
              <span class="legend-color suspended"></span>
              <span>Suspended ({{ stats.by_status.suspended }})</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Refresh Button -->
    <div v-if="stats" class="refresh-container">
      <button @click="loadStatistics" class="btn-refresh" :disabled="userStore.isLoading">
        🔄 Refresh Statistics
      </button>
      <p class="last-updated">Last updated: {{ formattedLastUpdate }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/userStore'

const userStore = useUserStore()
const lastUpdate = ref<Date>(new Date())

const stats = computed(() => userStore.statistics)

/**
 * Load statistics on mount
 */
onMounted(async () => {
  await loadStatistics()
})

/**
 * Load user statistics
 */
async function loadStatistics() {
  try {
    await userStore.fetchStatistics()
    lastUpdate.value = new Date()
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

/**
 * Calculate percentage of total
 */
function calculatePercentage(count: number): string {
  if (!stats.value || stats.value.total === 0) return '0'
  return ((count / stats.value.total) * 100).toFixed(1)
}

/**
 * Get persona percentage for bar chart
 */
function getPersonaPercentage(persona: keyof typeof stats.value.by_persona): number {
  if (!stats.value || stats.value.total === 0) return 0
  const count = stats.value.by_persona[persona]
  return Math.max((count / stats.value.total) * 100, 5) // Min 5% for visibility
}

/**
 * Calculate pie chart segments
 */
const pieSegments = computed(() => {
  if (!stats.value) return []

  const total = stats.value.total
  if (total === 0) return []

  const active = stats.value.by_status.active
  const inactive = stats.value.by_status.inactive
  const suspended = stats.value.by_status.suspended

  const circumference = 2 * Math.PI * 25 // radius = 25

  const activePercent = (active / total) * circumference
  const inactivePercent = (inactive / total) * circumference
  const suspendedPercent = (suspended / total) * circumference

  let offset = 0

  return [
    {
      name: 'active',
      color: '#4caf50',
      dashArray: `${activePercent} ${circumference}`,
      dashOffset: -offset
    },
    {
      name: 'inactive',
      color: '#9e9e9e',
      dashArray: `${inactivePercent} ${circumference}`,
      dashOffset: -(offset += activePercent)
    },
    {
      name: 'suspended',
      color: '#f44336',
      dashArray: `${suspendedPercent} ${circumference}`,
      dashOffset: -(offset += inactivePercent)
    }
  ]
})

/**
 * Format last update time
 */
const formattedLastUpdate = computed(() => {
  return lastUpdate.value.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})
</script>

<style scoped>
.user-statistics {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.user-statistics h2 {
  margin: 0 0 2rem 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.error-container {
  background: #ffebee;
  color: #c62828;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.stat-card.total-card {
  border-top: 4px solid #42b883;
}

.stat-card.active-card {
  border-top: 4px solid #4caf50;
}

.stat-card.inactive-card {
  border-top: 4px solid #9e9e9e;
}

.stat-card.suspended-card {
  border-top: 4px solid #f44336;
}

.stat-card.wide-card {
  grid-column: span 2;
}

.stat-card.chart-card {
  grid-column: span 1;
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.stat-value {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-percentage {
  margin: 0;
  color: #42b883;
  font-size: 0.9rem;
  font-weight: 500;
}

.persona-card h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.persona-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.persona-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.persona-bar {
  flex: 1;
  background: #42b883;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  min-width: 150px;
  transition: all 0.3s ease;
}

.persona-bar.teacher-bar { background: #9c27b0; }
.persona-bar.student-bar { background: #4caf50; }
.persona-bar.parent-bar { background: #ff9800; }
.persona-bar.vendor-bar { background: #e91e63; }

.persona-label {
  font-size: 0.9rem;
  font-weight: 500;
}

.persona-count {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  color: #2c3e50;
}

.chart-card h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.pie-chart {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.pie-svg {
  width: 200px;
  height: 200px;
  transform: rotate(-90deg);
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.legend-color.active { background: #4caf50; }
.legend-color.inactive { background: #9e9e9e; }
.legend-color.suspended { background: #f44336; }

.refresh-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #35a372;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-updated {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }

  .stat-card.wide-card,
  .stat-card.chart-card {
    grid-column: span 1;
  }

  .refresh-container {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
