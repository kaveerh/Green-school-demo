<template>
  <div class="room-form-container">
    <div class="form-header">
      <h1>{{ isEditMode ? 'Edit Room' : 'Create Room' }}</h1>
      <router-link to="/rooms" class="btn btn-secondary">Back to List</router-link>
    </div>

    <form @submit.prevent="handleSubmit" class="room-form">
      <!-- Basic Information -->
      <section class="form-section">
        <h2>Basic Information</h2>

        <div class="form-group">
          <label for="room_number" class="required">Room Number</label>
          <input
            id="room_number"
            v-model="formData.room_number"
            type="text"
            :disabled="isEditMode"
            required
            maxlength="50"
            pattern="[A-Za-z0-9\s\-]+"
            placeholder="e.g., 101, LAB-A, GYM-1"
            class="form-control"
          />
          <small class="form-help">
            Alphanumeric, spaces, and hyphens allowed. Cannot be changed after creation.
          </small>
        </div>

        <div class="form-group">
          <label for="room_name">Room Name</label>
          <input
            id="room_name"
            v-model="formData.room_name"
            type="text"
            maxlength="200"
            placeholder="e.g., Math Classroom A"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="3"
            placeholder="Describe the room..."
            class="form-control"
          ></textarea>
        </div>
      </section>

      <!-- Location -->
      <section class="form-section">
        <h2>Location</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="building">Building</label>
            <input
              id="building"
              v-model="formData.building"
              type="text"
              maxlength="100"
              placeholder="e.g., Main Building"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="floor">Floor</label>
            <input
              id="floor"
              v-model.number="formData.floor"
              type="number"
              min="-2"
              max="10"
              placeholder="Floor number"
              class="form-control"
            />
            <small class="form-help">-2 to 10 (negative for basement)</small>
          </div>
        </div>
      </section>

      <!-- Classification -->
      <section class="form-section">
        <h2>Classification</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="room_type" class="required">Room Type</label>
            <select
              id="room_type"
              v-model="formData.room_type"
              required
              @change="handleTypeChange"
              class="form-control"
            >
              <option value="">Select type...</option>
              <option value="classroom">Classroom</option>
              <option value="lab">Laboratory</option>
              <option value="gym">Gymnasium</option>
              <option value="library">Library</option>
              <option value="office">Office</option>
              <option value="cafeteria">Cafeteria</option>
            </select>
          </div>

          <div class="form-group">
            <label for="capacity" class="required">Capacity</label>
            <input
              id="capacity"
              v-model.number="formData.capacity"
              type="number"
              required
              min="1"
              max="1000"
              placeholder="30"
              class="form-control"
            />
            <small class="form-help">Number of people</small>
          </div>

          <div class="form-group">
            <label for="area_sqft">Area (sq ft)</label>
            <input
              id="area_sqft"
              v-model.number="formData.area_sqft"
              type="number"
              min="0"
              step="0.1"
              placeholder="800.5"
              class="form-control"
            />
          </div>
        </div>
      </section>

      <!-- Equipment & Features -->
      <section class="form-section">
        <h2>Equipment & Features</h2>

        <div class="form-group">
          <label>Equipment</label>
          <div class="items-list">
            <div v-for="(item, index) in formData.equipment" :key="index" class="item-row">
              <input
                v-model="formData.equipment[index]"
                type="text"
                placeholder="Equipment item"
                class="form-control"
              />
              <button type="button" @click="removeEquipment(index)" class="btn btn-sm btn-danger">
                Remove
              </button>
            </div>
          </div>
          <button type="button" @click="addEquipment" class="btn btn-sm btn-secondary">
            Add Equipment
          </button>
        </div>

        <div class="form-group">
          <label>Features</label>
          <div class="items-list">
            <div v-for="(item, index) in formData.features" :key="index" class="item-row">
              <input
                v-model="formData.features[index]"
                type="text"
                placeholder="Feature"
                class="form-control"
              />
              <button type="button" @click="removeFeature(index)" class="btn btn-sm btn-danger">
                Remove
              </button>
            </div>
          </div>
          <button type="button" @click="addFeature" class="btn btn-sm btn-secondary">
            Add Feature
          </button>
        </div>
      </section>

      <!-- Status -->
      <section class="form-section">
        <h2>Status</h2>

        <div class="form-row">
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="formData.is_active" type="checkbox" />
              <span>Active</span>
            </label>
            <small class="form-help">Room can be used for scheduling</small>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="formData.is_available" type="checkbox" />
              <span>Available</span>
            </label>
            <small class="form-help">Room is currently available</small>
          </div>
        </div>
      </section>

      <!-- Display Properties -->
      <section class="form-section">
        <h2>Display Properties</h2>

        <div class="form-row">
          <div class="form-group">
            <label for="color">Color</label>
            <div class="color-input-group">
              <input
                id="color"
                v-model="formData.color"
                type="color"
                class="color-picker"
              />
              <input
                v-model="formData.color"
                type="text"
                pattern="^#[0-9A-Fa-f]{6}$"
                placeholder="#4CAF50"
                maxlength="7"
                class="form-control color-text"
              />
              <button type="button" @click="useDefaultColor" class="btn btn-sm btn-secondary">
                Use Default
              </button>
            </div>
            <small class="form-help">Hex format (#RRGGBB)</small>
          </div>

          <div class="form-group">
            <label for="icon">Icon</label>
            <div class="icon-input-group">
              <input
                id="icon"
                v-model="formData.icon"
                type="text"
                maxlength="50"
                placeholder="🏫"
                class="form-control"
              />
              <button type="button" @click="useDefaultIcon" class="btn btn-sm btn-secondary">
                Use Default
              </button>
            </div>
            <small class="form-help">Emoji or icon identifier</small>
          </div>

          <div class="form-group">
            <label for="display_order">Display Order</label>
            <input
              id="display_order"
              v-model.number="formData.display_order"
              type="number"
              min="0"
              placeholder="0"
              class="form-control"
            />
          </div>
        </div>
      </section>

      <!-- Preview -->
      <section class="form-section preview-section">
        <h2>Preview</h2>
        <div class="room-preview">
          <div class="preview-icon" :style="{ backgroundColor: formData.color || '#757575' }">
            {{ formData.icon || '🏫' }}
          </div>
          <div class="preview-details">
            <div class="preview-number">{{ formData.room_number || 'ROOM-XXX' }}</div>
            <div class="preview-name">{{ formData.room_name || 'Room Name' }}</div>
            <div class="preview-meta">
              <span class="preview-badge" :style="{ backgroundColor: formData.color || '#757575' }">
                {{ getRoomTypeLabel(formData.room_type) || 'Type' }}
              </span>
              <span class="preview-capacity">{{ formData.capacity || 0 }} people</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" @click="handleCancel" class="btn btn-secondary">
          Cancel
        </button>
        <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
          {{ isSubmitting ? 'Saving...' : (isEditMode ? 'Update Room' : 'Create Room') }}
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRoomStore } from '@/stores/roomStore'
import {
  getRoomTypeLabel,
  getDefaultRoomIcon,
  getDefaultRoomColor,
  formatRoomNumber,
  isValidRoomNumber,
  isValidHexColor,
  isValidFloor
} from '@/types/room'
import type { RoomCreateInput, RoomUpdateInput, RoomType } from '@/types/room'

const router = useRouter()
const route = useRoute()
const roomStore = useRoomStore()

// Hard-coded school ID (TODO: Get from auth context)
const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

// Form state
const isEditMode = ref(false)
const roomId = ref<string>('')
const isSubmitting = ref(false)
const errorMessage = ref('')

// Form data
const formData = reactive({
  room_number: '',
  building: '',
  floor: null as number | null,
  room_type: '' as RoomType | '',
  room_name: '',
  description: '',
  capacity: 30,
  area_sqft: null as number | null,
  equipment: [] as string[],
  features: [] as string[],
  is_active: true,
  is_available: true,
  color: '',
  icon: '',
  display_order: 0
})

/**
 * Initialize form
 */
onMounted(async () => {
  if (route.params.id) {
    isEditMode.value = true
    roomId.value = route.params.id as string
    await loadRoom()
  }
})

/**
 * Load room for editing
 */
async function loadRoom() {
  try {
    const room = await roomStore.fetchRoomById(roomId.value)

    // Populate form
    formData.room_number = room.room_number
    formData.building = room.building || ''
    formData.floor = room.floor !== undefined ? room.floor : null
    formData.room_type = room.room_type
    formData.room_name = room.room_name || ''
    formData.description = room.description || ''
    formData.capacity = room.capacity
    formData.area_sqft = room.area_sqft || null
    formData.equipment = room.equipment || []
    formData.features = room.features || []
    formData.is_active = room.is_active
    formData.is_available = room.is_available
    formData.color = room.color || ''
    formData.icon = room.icon || ''
    formData.display_order = room.display_order
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to load room'
  }
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  errorMessage.value = ''

  // Validation
  if (!formData.room_number || !formData.room_number.trim()) {
    errorMessage.value = 'Room number is required'
    return
  }

  if (!isValidRoomNumber(formData.room_number)) {
    errorMessage.value = 'Invalid room number format. Use letters, numbers, spaces, and hyphens only.'
    return
  }

  if (!formData.room_type) {
    errorMessage.value = 'Room type is required'
    return
  }

  if (!formData.capacity || formData.capacity < 1) {
    errorMessage.value = 'Capacity must be at least 1'
    return
  }

  if (formData.floor !== null && !isValidFloor(formData.floor)) {
    errorMessage.value = 'Floor must be between -2 and 10'
    return
  }

  if (formData.color && !isValidHexColor(formData.color)) {
    errorMessage.value = 'Invalid color format. Use hex format (#RRGGBB)'
    return
  }

  isSubmitting.value = true

  try {
    if (isEditMode.value) {
      await updateRoom()
    } else {
      await createRoom()
    }

    // Navigate back to list
    router.push('/rooms')
  } catch (error: any) {
    errorMessage.value = error.message || 'Failed to save room'
  } finally {
    isSubmitting.value = false
  }
}

/**
 * Create new room
 */
async function createRoom() {
  const roomData: RoomCreateInput = {
    school_id: SCHOOL_ID,
    room_number: formatRoomNumber(formData.room_number),
    building: formData.building || undefined,
    floor: formData.floor !== null ? formData.floor : undefined,
    room_type: formData.room_type as RoomType,
    room_name: formData.room_name || undefined,
    description: formData.description || undefined,
    capacity: formData.capacity,
    area_sqft: formData.area_sqft || undefined,
    equipment: formData.equipment.filter(e => e.trim()),
    features: formData.features.filter(f => f.trim()),
    is_active: formData.is_active,
    is_available: formData.is_available,
    color: formData.color || undefined,
    icon: formData.icon || undefined,
    display_order: formData.display_order
  }

  await roomStore.createRoom(roomData)
}

/**
 * Update existing room
 */
async function updateRoom() {
  const roomData: RoomUpdateInput = {
    building: formData.building || undefined,
    floor: formData.floor !== null ? formData.floor : undefined,
    room_type: formData.room_type as RoomType,
    room_name: formData.room_name || undefined,
    description: formData.description || undefined,
    capacity: formData.capacity,
    area_sqft: formData.area_sqft || undefined,
    equipment: formData.equipment.filter(e => e.trim()),
    features: formData.features.filter(f => f.trim()),
    is_active: formData.is_active,
    is_available: formData.is_available,
    color: formData.color || undefined,
    icon: formData.icon || undefined,
    display_order: formData.display_order
  }

  await roomStore.updateRoom(roomId.value, roomData)
}

/**
 * Handle cancel button
 */
function handleCancel() {
  router.push('/rooms')
}

/**
 * Handle room type change
 */
function handleTypeChange() {
  if (formData.room_type && !formData.color) {
    formData.color = getDefaultRoomColor(formData.room_type as RoomType)
  }
  if (formData.room_type && !formData.icon) {
    formData.icon = getDefaultRoomIcon(formData.room_type as RoomType)
  }
}

/**
 * Use default color for room type
 */
function useDefaultColor() {
  if (formData.room_type) {
    formData.color = getDefaultRoomColor(formData.room_type as RoomType)
  }
}

/**
 * Use default icon for room type
 */
function useDefaultIcon() {
  if (formData.room_type) {
    formData.icon = getDefaultRoomIcon(formData.room_type as RoomType)
  }
}

/**
 * Add equipment item
 */
function addEquipment() {
  formData.equipment.push('')
}

/**
 * Remove equipment item
 */
function removeEquipment(index: number) {
  formData.equipment.splice(index, 1)
}

/**
 * Add feature item
 */
function addFeature() {
  formData.features.push('')
}

/**
 * Remove feature item
 */
function removeFeature(index: number) {
  formData.features.splice(index, 1)
}
</script>

<style scoped>
.room-form-container {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.form-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.room-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.form-section:last-of-type {
  border-bottom: none;
}

.form-section h2 {
  font-size: 1.25rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

label.required::after {
  content: ' *';
  color: #e74c3c;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.form-control:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #666;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

/* Equipment/Features Lists */
.items-list {
  margin-bottom: 1rem;
}

.item-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.item-row .form-control {
  flex: 1;
}

/* Color and Icon Inputs */
.color-input-group,
.icon-input-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.color-picker {
  width: 60px;
  height: 42px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.color-text {
  flex: 1;
}

/* Preview */
.preview-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

.room-preview {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.preview-icon {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.preview-details {
  flex: 1;
}

.preview-number {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.preview-name {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.preview-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.preview-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  color: white;
}

.preview-capacity {
  color: #666;
  font-size: 0.9rem;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #42b883;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #35a372;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background: #fee;
  border: 1px solid #e74c3c;
  border-radius: 4px;
  color: #e74c3c;
}
</style>
