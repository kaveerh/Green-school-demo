<template>
  <div class="activity-form-page">
    <div class="page-header">
      <h1>{{ isEditMode ? 'Edit Activity' : 'Create New Activity' }}</h1>
      <router-link to="/activities" class="btn btn-link">Back to Activities</router-link>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <form v-if="!loading" @submit.prevent="handleSubmit" class="activity-form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2>Basic Information</h2>

        <div class="form-group">
          <label for="name" class="required">Activity Name</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            maxlength="255"
            placeholder="e.g., Basketball Team, Chess Club, Art Studio"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="code">Activity Code</label>
            <input
              id="code"
              v-model="formData.code"
              type="text"
              maxlength="20"
              placeholder="e.g., BBALL-01, CHESS-01"
            />
            <small>Optional unique identifier</small>
          </div>

          <div class="form-group">
            <label for="activity_type" class="required">Activity Type</label>
            <select id="activity_type" v-model="formData.activity_type" required>
              <option value="">Select type...</option>
              <option value="sports">Sports</option>
              <option value="club">Club</option>
              <option value="art">Art</option>
              <option value="music">Music</option>
              <option value="academic">Academic</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="category">Category</label>
          <input
            id="category"
            v-model="formData.category"
            type="text"
            maxlength="100"
            placeholder="e.g., Team Sports, STEM, Visual Arts"
          />
          <small>Optional subcategory for organization</small>
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="4"
            placeholder="Describe the activity, its goals, and what students will learn"
          />
        </div>

        <div class="form-group">
          <label for="color">Display Color</label>
          <input
            id="color"
            v-model="formData.color"
            type="color"
          />
          <small>Choose a color for visual identification</small>
        </div>
      </div>

      <!-- Eligibility -->
      <div class="form-section">
        <h2>Eligibility</h2>

        <div class="form-group">
          <label class="required">Grade Levels</label>
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
          <small>Select all grade levels eligible for this activity</small>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="min_participants">Minimum Participants</label>
            <input
              id="min_participants"
              v-model.number="formData.min_participants"
              type="number"
              min="1"
              placeholder="Optional"
            />
            <small>Minimum enrollment to run activity</small>
          </div>

          <div class="form-group">
            <label for="max_participants">Maximum Participants</label>
            <input
              id="max_participants"
              v-model.number="formData.max_participants"
              type="number"
              min="1"
              placeholder="Optional"
            />
            <small>Maximum enrollment capacity</small>
          </div>
        </div>
      </div>

      <!-- Schedule -->
      <div class="form-section">
        <h2>Schedule</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="start_date">Start Date</label>
            <input
              id="start_date"
              v-model="formData.start_date"
              type="date"
            />
          </div>

          <div class="form-group">
            <label for="end_date">End Date</label>
            <input
              id="end_date"
              v-model="formData.end_date"
              type="date"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="hasSchedule" />
            Define weekly schedule
          </label>
        </div>

        <div v-if="hasSchedule" class="schedule-section">
          <div class="form-group">
            <label>Days of Week</label>
            <div class="checkbox-group">
              <label v-for="day in weekDays" :key="day" class="checkbox-label">
                <input
                  type="checkbox"
                  :value="day"
                  v-model="scheduleDays"
                />
                {{ day }}
              </label>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="start_time">Start Time</label>
              <input
                id="start_time"
                v-model="scheduleStartTime"
                type="time"
              />
            </div>

            <div class="form-group">
              <label for="end_time">End Time</label>
              <input
                id="end_time"
                v-model="scheduleEndTime"
                type="time"
              />
            </div>
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
            placeholder="e.g., Main Gym, Art Room 101, Music Hall"
          />
        </div>
      </div>

      <!-- Financial -->
      <div class="form-section">
        <h2>Financial Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="cost">Activity Cost</label>
            <input
              id="cost"
              v-model.number="formData.cost"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
            <small>Main cost for participation</small>
          </div>

          <div class="form-group">
            <label for="registration_fee">Registration Fee</label>
            <input
              id="registration_fee"
              v-model.number="formData.registration_fee"
              type="number"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
            <small>One-time registration fee</small>
          </div>
        </div>

        <div class="form-group">
          <label for="equipment_fee">Equipment Fee</label>
          <input
            id="equipment_fee"
            v-model.number="formData.equipment_fee"
            type="number"
            min="0"
            step="0.01"
            placeholder="0.00"
          />
          <small>Cost for equipment or materials</small>
        </div>
      </div>

      <!-- Requirements -->
      <div class="form-section">
        <h2>Requirements</h2>

        <div class="form-group">
          <label for="requirements">Prerequisites/Requirements</label>
          <textarea
            id="requirements"
            v-model="requirementsText"
            rows="3"
            placeholder="Enter each requirement on a new line"
          />
          <small>One requirement per line (e.g., "Parent consent required")</small>
        </div>

        <div class="form-group">
          <label for="equipment_needed">Equipment Needed</label>
          <textarea
            id="equipment_needed"
            v-model="equipmentText"
            rows="3"
            placeholder="Enter each item on a new line"
          />
          <small>One item per line (e.g., "Basketball shoes", "Calculator")</small>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.uniform_required" />
            Uniform Required
          </label>
        </div>
      </div>

      <!-- Contact Information -->
      <div class="form-section">
        <h2>Contact Information</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="contact_email">Contact Email</label>
            <input
              id="contact_email"
              v-model="formData.contact_email"
              type="email"
              placeholder="activity@example.com"
            />
          </div>

          <div class="form-group">
            <label for="contact_phone">Contact Phone</label>
            <input
              id="contact_phone"
              v-model="formData.contact_phone"
              type="tel"
              placeholder="+1234567890"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="parent_info">Information for Parents</label>
          <textarea
            id="parent_info"
            v-model="formData.parent_info"
            rows="3"
            placeholder="Important information for parents about this activity"
          />
        </div>
      </div>

      <!-- Status & Settings -->
      <div class="form-section">
        <h2>Status & Settings</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="status">Status</label>
            <select id="status" v-model="formData.status">
              <option value="active">Active</option>
              <option value="full">Full</option>
              <option value="cancelled">Cancelled</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.registration_open" />
            Registration Open
          </label>
          <small>Allow students to register for this activity</small>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="formData.is_featured" />
            Featured Activity
          </label>
          <small>Highlight this activity on the main activities page</small>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Activity' : 'Create Activity') }}
        </button>
        <router-link to="/activities" class="btn btn-secondary">Cancel</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActivityStore } from '@/stores/activityStore'
import { useSchool } from '@/composables/useSchool'
import type { ActivityCreateInput, ActivityType, ActivityStatus, ActivitySchedule } from '@/types/activity'

const route = useRoute()
const router = useRouter()
const activityStore = useActivityStore()
const { currentSchoolId } = useSchool()

// Week days for schedule
const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// State
const formData = ref({
  name: '',
  code: '',
  activity_type: '' as ActivityType | '',
  category: '',
  description: '',
  location: '',
  cost: 0,
  registration_fee: 0,
  equipment_fee: 0,
  min_participants: null as number | null,
  max_participants: null as number | null,
  start_date: '',
  end_date: '',
  contact_email: '',
  contact_phone: '',
  parent_info: '',
  uniform_required: false,
  status: 'active' as ActivityStatus,
  registration_open: true,
  is_featured: false,
  color: '#3B82F6'
})

const selectedGrades = ref<number[]>([])
const hasSchedule = ref(false)
const scheduleDays = ref<string[]>([])
const scheduleStartTime = ref('')
const scheduleEndTime = ref('')
const requirementsText = ref('')
const equipmentText = ref('')
const submitting = ref(false)

// Computed
const isEditMode = computed(() => !!route.params.id)
const loading = computed(() => activityStore.loading)
const error = computed(() => activityStore.error)

// Watch for schedule toggle
watch(hasSchedule, (value) => {
  if (!value) {
    scheduleDays.value = []
    scheduleStartTime.value = ''
    scheduleEndTime.value = ''
  }
})

// Methods
async function loadActivity() {
  if (!isEditMode.value) return

  const activityId = route.params.id as string

  try {
    await activityStore.fetchActivityById(activityId)
    const activity = activityStore.currentActivity

    if (!activity) return

    formData.value = {
      name: activity.name,
      code: activity.code || '',
      activity_type: activity.activity_type,
      category: activity.category || '',
      description: activity.description || '',
      location: activity.location || '',
      cost: activity.cost,
      registration_fee: activity.registration_fee,
      equipment_fee: activity.equipment_fee,
      min_participants: activity.min_participants,
      max_participants: activity.max_participants,
      start_date: activity.start_date || '',
      end_date: activity.end_date || '',
      contact_email: activity.contact_email || '',
      contact_phone: activity.contact_phone || '',
      parent_info: activity.parent_info || '',
      uniform_required: activity.uniform_required,
      status: activity.status,
      registration_open: activity.registration_open,
      is_featured: activity.is_featured,
      color: activity.color || '#3B82F6'
    }

    selectedGrades.value = activity.grade_levels || []

    if (activity.schedule) {
      hasSchedule.value = true
      scheduleDays.value = activity.schedule.days || []
      scheduleStartTime.value = activity.schedule.start_time || ''
      scheduleEndTime.value = activity.schedule.end_time || ''
    }

    if (activity.requirements) {
      requirementsText.value = activity.requirements.join('\n')
    }

    if (activity.equipment_needed) {
      equipmentText.value = activity.equipment_needed.join('\n')
    }
  } catch (err) {
    console.error('Failed to load activity:', err)
  }
}

async function handleSubmit() {
  // Validation
  if (selectedGrades.value.length === 0) {
    alert('Please select at least one grade level')
    return
  }

  submitting.value = true

  if (!currentSchoolId.value) {
    console.error('Cannot save activity: no school selected')
    submitting.value = false
    return
  }

  const userId = 'bed3ada7-ab32-4a74-84a0-75602181f553' // TODO: Get from auth

  // Parse requirements and equipment from textarea
  const requirements = requirementsText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0)

  const equipment = equipmentText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0)

  // Build schedule object
  let schedule: ActivitySchedule | undefined = undefined
  if (hasSchedule.value && scheduleDays.value.length > 0 && scheduleStartTime.value && scheduleEndTime.value) {
    schedule = {
      days: scheduleDays.value,
      start_time: scheduleStartTime.value,
      end_time: scheduleEndTime.value
    }
  }

  const activityData: ActivityCreateInput = {
    school_id: currentSchoolId.value,
    name: formData.value.name,
    code: formData.value.code || undefined,
    activity_type: formData.value.activity_type as ActivityType,
    category: formData.value.category || undefined,
    description: formData.value.description || undefined,
    grade_levels: selectedGrades.value,
    max_participants: formData.value.max_participants || undefined,
    min_participants: formData.value.min_participants || undefined,
    schedule: schedule,
    start_date: formData.value.start_date || undefined,
    end_date: formData.value.end_date || undefined,
    location: formData.value.location || undefined,
    cost: formData.value.cost,
    registration_fee: formData.value.registration_fee,
    equipment_fee: formData.value.equipment_fee,
    requirements: requirements.length > 0 ? requirements : undefined,
    equipment_needed: equipment.length > 0 ? equipment : undefined,
    uniform_required: formData.value.uniform_required,
    contact_email: formData.value.contact_email || undefined,
    contact_phone: formData.value.contact_phone || undefined,
    parent_info: formData.value.parent_info || undefined,
    status: formData.value.status,
    is_featured: formData.value.is_featured,
    registration_open: formData.value.registration_open,
    color: formData.value.color
  }

  try {
    if (isEditMode.value) {
      await activityStore.updateActivity(route.params.id as string, activityData, userId)
    } else {
      await activityStore.createActivity(activityData, userId)
    }

    router.push('/activities')
  } catch (err) {
    console.error('Failed to save activity:', err)
  } finally {
    submitting.value = false
  }
}

// Lifecycle
onMounted(() => {
  if (isEditMode.value) {
    loadActivity()
  }
})
</script>

<style scoped>
.activity-form-page {
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

.activity-form {
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
.form-group input[type="email"],
.form-group input[type="tel"],
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
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.schedule-section {
  padding: 1rem;
  background: #f9fafb;
  border-radius: 6px;
  margin-top: 1rem;
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

@media (max-width: 768px) {
  .activity-form-page {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .checkbox-group {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>
