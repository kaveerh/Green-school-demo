<template>
  <div class="room-list-container">
    <div class="room-list-header">
      <h1>Rooms</h1>
      <router-link to="/rooms/create" class="btn btn-primary">
        Create Room
      </router-link>
    </div>

    <!-- Search and Filters -->
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search rooms by number, name, or description..."
          @input="handleSearch"
          class="search-input"
        />
      </div>

      <div class="filters">
        <select v-model="filters.room_type" @change="applyFilters" class="filter-select">
          <option value="">All Types</option>
          <option value="classroom">Classroom</option>
          <option value="lab">Laboratory</option>
          <option value="gym">Gymnasium</option>
          <option value="library">Library</option>
          <option value="office">Office</option>
          <option value="cafeteria">Cafeteria</option>
        </select>

        <input
          v-model="filters.building"
          type="text"
          placeholder="Building"
          @input="applyFilters"
          class="filter-input"
        />

        <select v-model="filters.is_active" @change="applyFilters" class="filter-select">
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>

        <select v-model="filters.is_available" @change="applyFilters" class="filter-select">
          <option value="">All Availability</option>
          <option value="true">Available</option>
          <option value="false">Unavailable</option>
        </select>

        <button @click="clearFilters" class="btn btn-secondary">Clear Filters</button>
      </div>
    </div>

    <!-- Statistics -->
    <div v-if="statistics" class="statistics-summary">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_rooms }}</div>
        <div class="stat-label">Total Rooms</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.active_rooms }}</div>
        <div class="stat-label">Active</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.available_rooms }}</div>
        <div class="stat-label">Available</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_capacity }}</div>
        <div class="stat-label">Total Capacity</div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="roomStore.isLoading" class="loading">Loading rooms...</div>

    <!-- Error State -->
    <div v-if="roomStore.error" class="error-message">
      {{ roomStore.error }}
    </div>

    <!-- Rooms Table -->
    <div v-if="!roomStore.isLoading && roomStore.rooms.length > 0" class="rooms-table-container">
      <table class="rooms-table">
        <thead>
          <tr>
            <th>Icon</th>
            <th>Room Number</th>
            <th>Name</th>
            <th>Type</th>
            <th>Location</th>
            <th>Capacity</th>
            <th>Status</th>
            <th>Availability</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in roomStore.rooms" :key="room.id">
            <td>
              <div class="room-icon" :style="{ backgroundColor: room.color || '#757575' }">
                {{ room.icon || '🏫' }}
              </div>
            </td>
            <td class="room-number">{{ room.room_number }}</td>
            <td>{{ room.room_name || '—' }}</td>
            <td>
              <span class="badge badge-type" :style="{ backgroundColor: getRoomTypeColor(room.room_type) }">
                {{ getRoomTypeLabel(room.room_type) }}
              </span>
            </td>
            <td>{{ room.location || '—' }}</td>
            <td>{{ room.capacity_label }}</td>
            <td>
              <span :class="['badge', room.is_active ? 'badge-success' : 'badge-danger']">
                {{ room.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span :class="['badge', room.is_available ? 'badge-success' : 'badge-warning']">
                {{ room.is_available ? 'Available' : 'Unavailable' }}
              </span>
            </td>
            <td class="actions">
              <router-link :to="`/rooms/${room.id}/edit`" class="btn-icon" title="Edit">
                ✏️
              </router-link>
              <button
                @click="toggleRoomStatus(room.id, !room.is_active)"
                class="btn-icon"
                :title="room.is_active ? 'Deactivate' : 'Activate'"
              >
                {{ room.is_active ? '⏸️' : '▶️' }}
              </button>
              <button
                @click="toggleRoomAvailability(room.id, !room.is_available)"
                class="btn-icon"
                :title="room.is_available ? 'Mark Unavailable' : 'Mark Available'"
              >
                {{ room.is_available ? '🔒' : '🔓' }}
              </button>
              <button @click="confirmDelete(room)" class="btn-icon btn-danger" title="Delete">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!roomStore.isLoading && roomStore.rooms.length === 0" class="empty-state">
      <p>No rooms found.</p>
      <router-link to="/rooms/create" class="btn btn-primary">Create First Room</router-link>
    </div>

    <!-- Pagination -->
    <div v-if="roomStore.totalPages > 1" class="pagination">
      <button
        @click="roomStore.previousPage()"
        :disabled="!roomStore.hasPreviousPage"
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="pagination-info">
        Page {{ roomStore.currentPage }} of {{ roomStore.totalPages }}
        ({{ roomStore.totalRooms }} total)
      </span>
      <button
        @click="roomStore.nextPage()"
        :disabled="!roomStore.hasNextPage"
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h3>Confirm Delete</h3>
        <p>
          Are you sure you want to delete room <strong>{{ roomToDelete?.room_number }}</strong>?
        </p>
        <p v-if="roomToDelete?.room_name" class="room-details">
          {{ roomToDelete.room_name }}
        </p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn btn-secondary">Cancel</button>
          <button @click="executeDelete" class="btn btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoomStore } from '@/stores/roomStore'
import { getRoomTypeLabel, getRoomTypeColor } from '@/types/room'
import type { Room } from '@/types/room'

const roomStore = useRoomStore()

// Hard-coded school ID (TODO: Get from auth context)
const SCHOOL_ID = '60da2256-81fc-4ca5-bf6b-467b8d371c61'

// Search and filters
const searchQuery = ref('')
const filters = ref({
  school_id: SCHOOL_ID,
  room_type: '',
  building: '',
  is_active: '',
  is_available: ''
})

// Statistics
const statistics = ref(null)

// Delete modal
const showDeleteModal = ref(false)
const roomToDelete = ref<Room | null>(null)

/**
 * Load rooms on component mount
 */
onMounted(async () => {
  await loadRooms()
  await loadStatistics()
})

/**
 * Load rooms with current filters
 */
async function loadRooms() {
  try {
    const params: any = { ...filters.value }

    // Convert string boolean values
    if (params.is_active !== '') {
      params.is_active = params.is_active === 'true'
    } else {
      delete params.is_active
    }

    if (params.is_available !== '') {
      params.is_available = params.is_available === 'true'
    } else {
      delete params.is_available
    }

    // Remove empty filters
    if (!params.room_type) delete params.room_type
    if (!params.building) delete params.building

    await roomStore.fetchRooms(params)
  } catch (error) {
    console.error('Failed to load rooms:', error)
  }
}

/**
 * Load statistics
 */
async function loadStatistics() {
  try {
    statistics.value = await roomStore.fetchStatistics(SCHOOL_ID)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

/**
 * Handle search input
 */
async function handleSearch() {
  if (searchQuery.value.trim()) {
    await roomStore.searchRooms(searchQuery.value, { school_id: SCHOOL_ID })
  } else {
    await loadRooms()
  }
}

/**
 * Apply filters
 */
async function applyFilters() {
  searchQuery.value = ''
  await loadRooms()
}

/**
 * Clear all filters
 */
async function clearFilters() {
  searchQuery.value = ''
  filters.value = {
    school_id: SCHOOL_ID,
    room_type: '',
    building: '',
    is_active: '',
    is_available: ''
  }
  await loadRooms()
}

/**
 * Toggle room status
 */
async function toggleRoomStatus(id: string, isActive: boolean) {
  try {
    await roomStore.toggleStatus(id, isActive)
    await loadStatistics()
  } catch (error) {
    console.error('Failed to toggle status:', error)
  }
}

/**
 * Toggle room availability
 */
async function toggleRoomAvailability(id: string, isAvailable: boolean) {
  try {
    await roomStore.toggleAvailability(id, isAvailable)
    await loadStatistics()
  } catch (error) {
    console.error('Failed to toggle availability:', error)
  }
}

/**
 * Show delete confirmation modal
 */
function confirmDelete(room: Room) {
  roomToDelete.value = room
  showDeleteModal.value = true
}

/**
 * Cancel delete
 */
function cancelDelete() {
  roomToDelete.value = null
  showDeleteModal.value = false
}

/**
 * Execute delete
 */
async function executeDelete() {
  if (!roomToDelete.value) return

  try {
    await roomStore.deleteRoom(roomToDelete.value.id)
    showDeleteModal.value = false
    roomToDelete.value = null
    await loadStatistics()
  } catch (error) {
    console.error('Failed to delete room:', error)
  }
}
</script>

<style scoped>
.room-list-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.room-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.room-list-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

/* Filters Section */
.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select,
.filter-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.filter-input {
  min-width: 150px;
}

/* Statistics */
.statistics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #42b883;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

/* Table */
.rooms-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.rooms-table {
  width: 100%;
  border-collapse: collapse;
}

.rooms-table th,
.rooms-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.rooms-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.room-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.room-number {
  font-weight: 600;
  color: #2c3e50;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  color: white;
  display: inline-block;
}

.badge-type {
  color: white;
}

.badge-success {
  background: #42b883;
}

.badge-danger {
  background: #e74c3c;
}

.badge-warning {
  background: #f39c12;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  transition: transform 0.2s;
}

.btn-icon:hover {
  transform: scale(1.2);
}

.btn-icon.btn-danger:hover {
  filter: brightness(1.2);
}

/* Buttons */
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

.btn-primary:hover {
  background: #35a372;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

/* States */
.loading,
.error-message,
.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #e74c3c;
}

.empty-state p {
  margin-bottom: 1rem;
  color: #666;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-info {
  color: #666;
  font-size: 0.95rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
}

.modal h3 {
  margin-top: 0;
  color: #2c3e50;
}

.room-details {
  color: #666;
  font-style: italic;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>
