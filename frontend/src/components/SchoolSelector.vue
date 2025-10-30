<template>
  <div class="school-selector">
    <!-- Selected School Display -->
    <button
      v-if="selectedSchool"
      @click="toggleDropdown"
      class="school-selector-button"
      :class="{ 'is-open': isDropdownOpen }"
    >
      <div class="school-info">
        <span class="school-icon">🏫</span>
        <div class="school-details">
          <span class="school-name">{{ selectedSchool.name }}</span>
          <span v-if="selectedSchool.city" class="school-location">
            {{ selectedSchool.city }}<template v-if="selectedSchool.state">, {{ selectedSchool.state }}</template>
          </span>
        </div>
      </div>
      <span class="dropdown-arrow">{{ isDropdownOpen ? '▼' : '▶' }}</span>
    </button>

    <!-- No School Selected -->
    <button
      v-else
      @click="toggleDropdown"
      class="school-selector-button no-school"
      :class="{ 'is-open': isDropdownOpen }"
    >
      <span class="school-icon">🏫</span>
      <span class="no-school-text">Select a School</span>
      <span class="dropdown-arrow">{{ isDropdownOpen ? '▼' : '▶' }}</span>
    </button>

    <!-- Dropdown Menu -->
    <div v-if="isDropdownOpen" class="school-dropdown" ref="dropdownRef">
      <!-- Search -->
      <div class="school-search">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search schools..."
          class="search-input"
          @input="handleSearch"
        />
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="dropdown-loading">
        <div class="spinner"></div>
        <span>Loading schools...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="dropdown-error">
        <span>{{ error }}</span>
        <button @click="loadSchools" class="retry-button">Retry</button>
      </div>

      <!-- Schools List -->
      <div v-else-if="filteredSchools.length > 0" class="schools-list">
        <button
          v-for="school in filteredSchools"
          :key="school.id"
          @click="handleSelectSchool(school)"
          class="school-option"
          :class="{ 'is-selected': selectedSchool?.id === school.id }"
        >
          <div class="school-option-info">
            <span class="school-option-name">{{ school.name }}</span>
            <span v-if="school.city || school.state" class="school-option-location">
              <template v-if="school.city">{{ school.city }}</template>
              <template v-if="school.city && school.state">, </template>
              <template v-if="school.state">{{ school.state }}</template>
            </span>
          </div>
          <span v-if="selectedSchool?.id === school.id" class="selected-indicator">✓</span>
        </button>
      </div>

      <!-- Empty State -->
      <div v-else class="dropdown-empty">
        <span>No schools found</span>
        <p v-if="searchQuery">Try a different search term</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

// State
const isDropdownOpen = ref(false)
const searchQuery = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)

// Computed
const selectedSchool = computed(() => authStore.selectedSchool)

const filteredSchools = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) {
    return authStore.availableSchools
  }

  return authStore.availableSchools.filter(school => {
    const nameMatch = school.name.toLowerCase().includes(query)
    const cityMatch = school.city?.toLowerCase().includes(query)
    const stateMatch = school.state?.toLowerCase().includes(query)
    const slugMatch = school.slug?.toLowerCase().includes(query)

    return nameMatch || cityMatch || stateMatch || slugMatch
  })
})

/**
 * Toggle dropdown open/closed
 */
function toggleDropdown() {
  isDropdownOpen.value = !isDropdownOpen.value

  if (isDropdownOpen.value && authStore.availableSchools.length === 0) {
    loadSchools()
  }
}

/**
 * Load schools from API
 */
async function loadSchools() {
  isLoading.value = true
  error.value = null

  try {
    await authStore.fetchSchools()
  } catch (e) {
    error.value = 'Failed to load schools. Please try again.'
    console.error('Failed to load schools:', e)
  } finally {
    isLoading.value = false
  }
}

/**
 * Handle school selection
 */
function handleSelectSchool(school: any) {
  authStore.selectSchool(school)
  isDropdownOpen.value = false
  searchQuery.value = ''
}

/**
 * Handle search input
 */
function handleSearch() {
  // Search is reactive through computed property
}

/**
 * Close dropdown when clicking outside
 */
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  const dropdown = dropdownRef.value
  const button = target.closest('.school-selector-button')

  if (!button && dropdown && !dropdown.contains(target)) {
    isDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)

  // Load schools on mount if not already loaded
  if (authStore.availableSchools.length === 0) {
    loadSchools()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.school-selector {
  position: relative;
}

.school-selector-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 240px;
  font-size: 0.875rem;
}

.school-selector-button:hover {
  border-color: #42b883;
  background: #f9fafb;
}

.school-selector-button.is-open {
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.school-selector-button.no-school {
  color: #6b7280;
}

.school-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.school-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.school-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
  flex: 1;
}

.school-name {
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.school-location {
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.no-school-text {
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  color: #9ca3af;
  font-size: 0.75rem;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.school-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  max-height: 400px;
  display: flex;
  flex-direction: column;
  min-width: 300px;
}

.school-search {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.schools-list {
  overflow-y: auto;
  max-height: 300px;
}

.school-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  transition: background 0.15s;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
}

.school-option:last-child {
  border-bottom: none;
}

.school-option:hover {
  background: #f9fafb;
}

.school-option.is-selected {
  background: #f0fdf4;
}

.school-option-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.school-option-name {
  font-weight: 500;
  color: #111827;
  font-size: 0.875rem;
}

.school-option-location {
  font-size: 0.75rem;
  color: #6b7280;
}

.selected-indicator {
  color: #42b883;
  font-weight: 600;
  flex-shrink: 0;
}

.dropdown-loading,
.dropdown-error,
.dropdown-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #42b883;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.dropdown-error {
  color: #dc2626;
}

.retry-button {
  padding: 0.375rem 0.75rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.retry-button:hover {
  background: #35a372;
}

.dropdown-empty p {
  margin-top: 0.25rem;
  font-size: 0.75rem;
}
</style>
