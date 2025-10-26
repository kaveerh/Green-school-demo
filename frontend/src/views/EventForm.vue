<template>
  <div class="event-form-page">
    <div class="page-header">
      <h1>{{ isEditMode ? 'Edit Event' : 'Create New Event' }}</h1>
      <router-link to="/events" class="btn btn-link">Back to Events</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <form v-if="!loading" @submit.prevent="handleSubmit" class="event-form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2>Basic Information</h2>

        <div class="form-group">
          <label for="title" class="required">Title</label>
          <input
            id="title"
            v-model="formData.title"
            type="text"
            required
            maxlength="200"
            placeholder="Event title"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="4"
            placeholder="Event description"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="event_type" class="required">Event Type</label>
            <select id="event_type" v-model="formData.event_type" required>
              <option value="">Select type...</option>
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

          <div class="form-group">
            <label for="status">Status</label>
            <select id="status" v-model="formData.status">
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="postponed">Postponed</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="color">Calendar Color</label>
          <input
            id="color"
            v-model="formData.color"
            type="color"
          />
          <small>Choose a color for calendar display</small>
        </div>
      </div>

      <!-- Date & Time -->
      <div class="form-section">
        <h2>Date & Time</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="start_date" class="required">Start Date</label>
            <input
              id="start_date"
              v-model="formData.start_date"
              type="date"
              required
            />
          </div>

          <div class="form-group">
            <label for="end_date" class="required">End Date</label>
            <input
              id="end_date"
              v-model="formData.end_date"
              type="date"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.is_all_day" />
            All Day Event
          </label>
        </div>

        <div v-if="!formData.is_all_day" class="form-row">
          <div class="form-group">
            <label for="start_time">Start Time</label>
            <input
              id="start_time"
              v-model="formData.start_time"
              type="time"
            />
          </div>

          <div class="form-group">
            <label for="end_time">End Time</label>
            <input
              id="end_time"
              v-model="formData.end_time"
              type="time"
            />
          </div>
        </div>
      </div>

      <!-- Location -->
      <div class="form-section">
        <h2>Location</h2>

        <div class="form-group">
          <label for="location">Location</label>
          <input
            id="location"
            v-model="formData.location"
            type="text"
            maxlength="255"
            placeholder="e.g., Main Auditorium, Gymnasium, etc."
          />
        </div>
      </div>

      <!-- Audience -->
      <div class="form-section">
        <h2>Target Audience</h2>

        <div class="form-group">
          <label for="target_audience">Audience Type</label>
          <select id="target_audience" v-model="formData.target_audience">
            <option value="">Not specified</option>
            <option value="all_school">All School</option>
            <option value="grade_level">Specific Grade Levels</option>
            <option value="class">Specific Classes</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        <div v-if="formData.target_audience === 'grade_level'" class="form-group">
          <label>Grade Levels (1-7)</label>
          <div class="checkbox-group">
            <label v-for="grade in [1, 2, 3, 4, 5, 6, 7]" :key="grade" class="checkbox-label">
              <input
                type="checkbox"
                :value="grade"
                v-model="selectedGrades"
              />
              Grade {{ grade }}
            </label>
          </div>
        </div>
      </div>

      <!-- Recurring Event -->
      <div class="form-section">
        <h2>Recurring Event</h2>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.is_recurring" />
            This is a recurring event
          </label>
        </div>

        <div v-if="formData.is_recurring" class="form-row">
          <div class="form-group">
            <label for="recurrence_pattern">Recurrence Pattern</label>
            <select id="recurrence_pattern" v-model="formData.recurrence_pattern">
              <option value="">Select pattern...</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div class="form-group">
            <label for="recurrence_end_date">Recurrence End Date</label>
            <input
              id="recurrence_end_date"
              v-model="formData.recurrence_end_date"
              type="date"
            />
          </div>
        </div>
      </div>

      <!-- RSVP -->
      <div class="form-section">
        <h2>RSVP Settings</h2>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.requires_rsvp" />
            Require RSVP for this event
          </label>
        </div>

        <div v-if="formData.requires_rsvp" class="form-group">
          <label for="max_attendees">Maximum Attendees</label>
          <input
            id="max_attendees"
            v-model.number="formData.max_attendees"
            type="number"
            min="1"
            placeholder="Leave empty for unlimited"
          />
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Event' : 'Create Event') }}
        </button>
        <router-link to="/events" class="btn btn-secondary">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEventStore } from '@/stores/eventStore'
import type { EventCreateRequest, EventType, EventStatus } from '@/types/event'

const route = useRoute()
const router = useRouter()
const eventStore = useEventStore()

// State
const formData = ref({
  title: '',
  description: '',
  event_type: '' as EventType | '',
  status: 'scheduled' as EventStatus,
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  is_all_day: false,
  location: '',
  target_audience: '' as any,
  is_recurring: false,
  recurrence_pattern: '' as any,
  recurrence_end_date: '',
  requires_rsvp: false,
  max_attendees: null as number | null,
  color: '#3B82F6'
})

const selectedGrades = ref<number[]>([])
const submitting = ref(false)

// Computed
const isEditMode = computed(() => !!route.params.id)
const loading = computed(() => eventStore.loading)
const error = computed(() => eventStore.error)

// Watch for all-day toggle
watch(() => formData.value.is_all_day, (isAllDay) => {
  if (isAllDay) {
    formData.value.start_time = ''
    formData.value.end_time = ''
  }
})

// Watch for recurring toggle
watch(() => formData.value.is_recurring, (isRecurring) => {
  if (!isRecurring) {
    formData.value.recurrence_pattern = ''
    formData.value.recurrence_end_date = ''
  }
})

// Watch for RSVP toggle
watch(() => formData.value.requires_rsvp, (requiresRsvp) => {
  if (!requiresRsvp) {
    formData.value.max_attendees = null
  }
})

// Methods
async function loadEvent() {
  if (!isEditMode.value) return

  const eventId = route.params.id as string

  try {
    const event = await eventStore.fetchEventById(eventId)

    formData.value = {
      title: event.title,
      description: event.description || '',
      event_type: event.event_type,
      status: event.status,
      start_date: event.start_date,
      end_date: event.end_date,
      start_time: event.start_time || '',
      end_time: event.end_time || '',
      is_all_day: event.is_all_day,
      location: event.location || '',
      target_audience: event.target_audience || '',
      is_recurring: event.is_recurring,
      recurrence_pattern: event.recurrence_pattern || '',
      recurrence_end_date: event.recurrence_end_date || '',
      requires_rsvp: event.requires_rsvp,
      max_attendees: event.max_attendees,
      color: event.color || '#3B82F6'
    }

    if (event.grade_levels) {
      selectedGrades.value = event.grade_levels
    }
  } catch (err) {
    console.error('Failed to load event:', err)
  }
}

async function handleSubmit() {
  submitting.value = true

  const schoolId = '60da2256-81fc-4ca5-bf6b-467b8d371c61' // TODO: Get from auth
  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  const eventData: EventCreateRequest = {
    school_id: schoolId,
    title: formData.value.title,
    description: formData.value.description || null,
    event_type: formData.value.event_type as EventType,
    start_date: formData.value.start_date,
    end_date: formData.value.end_date,
    start_time: formData.value.is_all_day ? null : (formData.value.start_time || null),
    end_time: formData.value.is_all_day ? null : (formData.value.end_time || null),
    is_all_day: formData.value.is_all_day,
    location: formData.value.location || null,
    target_audience: formData.value.target_audience || null,
    grade_levels: selectedGrades.value.length > 0 ? selectedGrades.value : null,
    status: formData.value.status,
    is_recurring: formData.value.is_recurring,
    recurrence_pattern: formData.value.is_recurring ? (formData.value.recurrence_pattern || null) : null,
    recurrence_end_date: formData.value.is_recurring ? (formData.value.recurrence_end_date || null) : null,
    requires_rsvp: formData.value.requires_rsvp,
    max_attendees: formData.value.requires_rsvp ? formData.value.max_attendees : null,
    color: formData.value.color
  }

  try {
    if (isEditMode.value) {
      await eventStore.updateEvent(route.params.id as string, eventData, userId)
    } else {
      await eventStore.createEvent(eventData, userId)
    }

    router.push('/events')
  } catch (err) {
    console.error('Failed to save event:', err)
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  if (isEditMode.value) {
    loadEvent()
  } else {
    // Set default dates for new event
    const today = new Date().toISOString().split('T')[0]
    formData.value.start_date = today
    formData.value.end_date = today
  }
})
</script>

<style scoped>
.event-form-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
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
  margin-bottom: 2rem;
}

.event-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-group label.required::after {
  content: ' *';
  color: #dc2626;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="time"],
.form-group input[type="number"],
.form-group input[type="color"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.625rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  font-family: inherit;
}

.form-group input[type="color"] {
  width: 100px;
  height: 40px;
}

.form-group textarea {
  resize: vertical;
}

.form-group small {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  color: #6b7280;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
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

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
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
</style>
