<template>
  <div class="event-list">
    <div class="page-header">
      <h1>School Calendar Events</h1>
      <router-link to="/events/create" class="btn btn-primary">
        Create Event
      </router-link>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Total Events</div>
        <div class="stat-value">{{ statistics.total_events }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Upcoming</div>
        <div class="stat-value">{{ upcomingCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">RSVP Events</div>
        <div class="stat-value">{{ statistics.rsvp_events }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Recurring</div>
        <div class="stat-value">{{ statistics.recurring_events }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>Event Type</label>
        <select v-model="filters.event_type">
          <option value="">All Types</option>
          <option value="assembly">Assembly</option>
          <option value="exam">Exam</option>
          <option value="holiday">Holiday</option>
          <option value="meeting">Meeting</option>
          <option value="parent_conference">Parent Conference</option>
          <option value="field_trip">Field Trip</option>
          <option value="sports">Sports</option>
          <option value="performance">Performance</option>
          <option value="workshop">Workshop</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status">
          <option value="">All Statuses</option>
          <option value="scheduled">Scheduled</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
          <option value="postponed">Postponed</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Start Date</label>
        <input type="date" v-model="filters.start_date" />
      </div>

      <div class="filter-group">
        <label>End Date</label>
        <input type="date" v-model="filters.end_date" />
      </div>

      <div class="filter-actions">
        <button @click="applyFilters" class="btn btn-secondary">
          Apply Filters
        </button>
        <button @click="clearFilters" class="btn btn-link">Clear</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">Loading events...</div>

    <!-- Error State -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- Events Table -->
    <div v-if="!loading && events.length > 0" class="events-table-container">
      <table class="events-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Date & Time</th>
            <th>Location</th>
            <th>Status</th>
            <th>RSVP</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="event in events" :key="event.id" :class="getRowClass(event)">
            <td>
              <div class="event-title">
                <span class="event-icon">{{ getEventIcon(event.event_type) }}</span>
                <div>
                  <div class="title-text">{{ event.title }}</div>
                  <div v-if="event.description" class="title-description">
                    {{ truncateText(event.description, 60) }}
                  </div>
                </div>
              </div>
            </td>
            <td>
              <span
                class="event-type-badge"
                :style="{ backgroundColor: getEventTypeColor(event.event_type) }"
              >
                {{ getEventTypeLabel(event.event_type) }}
              </span>
            </td>
            <td>
              <div class="date-time">
                <div class="date">{{ formatEventDate(event) }}</div>
                <div class="time">{{ formatEventTime(event) }}</div>
              </div>
            </td>
            <td>
              {{ event.location || event.room?.name || '—' }}
            </td>
            <td>
              <span class="status-badge" :class="`status-${getStatusColor(event.status)}`">
                {{ getStatusLabel(event.status) }}
              </span>
            </td>
            <td>
              <div v-if="event.requires_rsvp" class="rsvp-info">
                <div class="rsvp-count">
                  {{ event.current_attendees }}{{ event.max_attendees ? ` / ${event.max_attendees}` : '' }}
                </div>
                <div class="rsvp-percentage">{{ event.attendance_percentage.toFixed(0) }}%</div>
              </div>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <div class="action-buttons">
                <router-link
                  :to="`/events/${event.id}/edit`"
                  class="btn btn-sm btn-secondary"
                  v-if="isEventEditable(event)"
                >
                  Edit
                </router-link>
                <button
                  @click="handleDelete(event)"
                  class="btn btn-sm btn-danger"
                  v-if="isEventEditable(event)"
                >
                  Delete
                </button>
                <router-link
                  :to="`/events/${event.id}`"
                  class="btn btn-sm btn-link"
                >
                  View
                </router-link>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && events.length === 0" class="empty-state">
      <p>No events found.</p>
      <router-link to="/events/create" class="btn btn-primary">
        Create First Event
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
import { useEventStore } from '@/stores/eventStore'
import { useRouter } from 'vue-router'
import {
  getEventTypeLabel,
  getEventTypeColor,
  getStatusLabel,
  getStatusColor,
  formatEventDate,
  formatEventTime,
  getEventIcon,
  isEventEditable,
  type EventType,
  type EventStatus
} from '@/types/event'

const eventStore = useEventStore()
const router = useRouter()

// State
const filters = ref({
  event_type: '' as EventType | '',
  status: '' as EventStatus | '',
  start_date: '',
  end_date: ''
})

// Computed
const events = computed(() => eventStore.events)
const loading = computed(() => eventStore.loading)
const error = computed(() => eventStore.error)
const statistics = computed(() => eventStore.statistics)
const total = computed(() => eventStore.total)
const page = computed(() => eventStore.page)
const pages = computed(() => eventStore.pages)
const upcomingCount = computed(() => eventStore.upcomingCount)

// Methods
async function loadEvents() {
  const schoolId = '60da2256-81fc-4ca5-bf6b-467b8d371c61' // TODO: Get from auth

  const params: any = {
    school_id: schoolId,
    page: page.value,
    limit: 50
  }

  if (filters.value.event_type) params.event_type = filters.value.event_type
  if (filters.value.status) params.status = filters.value.status
  if (filters.value.start_date) params.start_date = filters.value.start_date
  if (filters.value.end_date) params.end_date = filters.value.end_date

  try {
    await eventStore.fetchEvents(params)
  } catch (err) {
    console.error('Failed to load events:', err)
  }
}

async function loadStatistics() {
  const schoolId = '60da2256-81fc-4ca5-bf6b-467b8d371c61' // TODO: Get from auth

  try {
    await eventStore.fetchStatistics({
      school_id: schoolId,
      start_date: filters.value.start_date || undefined,
      end_date: filters.value.end_date || undefined
    })
  } catch (err) {
    console.error('Failed to load statistics:', err)
  }
}

function applyFilters() {
  eventStore.page = 1
  loadEvents()
  loadStatistics()
}

function clearFilters() {
  filters.value = {
    event_type: '',
    status: '',
    start_date: '',
    end_date: ''
  }
  applyFilters()
}

function goToPage(newPage: number) {
  eventStore.page = newPage
  loadEvents()
}

async function handleDelete(event: any) {
  if (!confirm(`Are you sure you want to delete "${event.title}"?`)) {
    return
  }

  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  try {
    await eventStore.deleteEvent(event.id, userId)
  } catch (err) {
    console.error('Failed to delete event:', err)
  }
}

function getRowClass(event: any) {
  if (event.status === 'cancelled') return 'row-cancelled'
  if (event.is_ongoing) return 'row-ongoing'
  if (event.is_past) return 'row-past'
  return ''
}

function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// Lifecycle
onMounted(() => {
  loadEvents()
  loadStatistics()
})
</script>

<style scoped>
.event-list {
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #111827;
}

.filters {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.filter-group input,
.filter-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
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
  padding: 2rem;
  text-align: center;
}

.error-message {
  color: #dc2626;
  background: #fee2e2;
  border-radius: 8px;
}

.events-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.events-table {
  width: 100%;
  border-collapse: collapse;
}

.events-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
  background: #f9fafb;
}

.events-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.events-table tr:hover {
  background: #f9fafb;
}

.row-cancelled {
  opacity: 0.6;
  text-decoration: line-through;
}

.row-ongoing {
  background: #fef3c7;
}

.row-past {
  opacity: 0.7;
}

.event-title {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.event-icon {
  font-size: 1.5rem;
}

.title-text {
  font-weight: 500;
  color: #111827;
}

.title-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.event-type-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.date-time {
  font-size: 0.875rem;
}

.date {
  font-weight: 500;
  color: #111827;
}

.time {
  color: #6b7280;
  margin-top: 0.25rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-blue {
  background: #dbeafe;
  color: #1e40af;
}

.status-yellow {
  background: #fef3c7;
  color: #92400e;
}

.status-green {
  background: #d1fae5;
  color: #065f46;
}

.status-red {
  background: #fee2e2;
  color: #991b1b;
}

.status-orange {
  background: #fed7aa;
  color: #9a3412;
}

.rsvp-info {
  font-size: 0.875rem;
}

.rsvp-count {
  font-weight: 500;
  color: #111827;
}

.rsvp-percentage {
  color: #6b7280;
  margin-top: 0.25rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
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
  color: #6b7280;
}

.text-muted {
  color: #9ca3af;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #dc2626;
  color: white;
}

.btn-danger:hover {
  background: #b91c1c;
}

.btn-link {
  background: transparent;
  color: #3b82f6;
  padding: 0.5rem;
}

.btn-link:hover {
  color: #2563eb;
  text-decoration: underline;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
}
</style>
