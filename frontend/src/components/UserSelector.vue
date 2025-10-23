<template>
  <div class="user-selector">
    <label :for="inputId">{{ label }} {{ required ? '*' : '' }}</label>

    <!-- Search/Filter Input -->
    <div class="search-container">
      <input
        :id="inputId"
        v-model="searchQuery"
        type="text"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        @focus="showDropdown = true"
        @input="handleSearch"
        autocomplete="off"
        class="search-input"
      />
      <span v-if="isLoading" class="loading-icon">🔄</span>
      <span v-else-if="selectedUser" class="selected-icon">✓</span>
    </div>

    <!-- Dropdown with filtered users -->
    <div v-if="showDropdown && !disabled" class="dropdown">
      <div v-if="isLoading" class="dropdown-item loading">
        Loading users...
      </div>
      <div v-else-if="filteredUsers.length === 0" class="dropdown-item empty">
        {{ searchQuery ? 'No users found matching your search' : 'No users available' }}
      </div>
      <div
        v-else
        v-for="user in filteredUsers"
        :key="user.id"
        class="dropdown-item"
        :class="{ selected: modelValue === user.id }"
        @click="selectUser(user)"
      >
        <div class="user-info">
          <div class="user-name">
            {{ user.first_name }} {{ user.last_name }}
            <span v-if="user.persona" class="user-persona">{{ formatPersona(user.persona) }}</span>
          </div>
          <div class="user-email">{{ user.email }}</div>
          <div v-if="showSchool && user.school_name" class="user-school">
            🏫 {{ user.school_name }}
          </div>
        </div>
      </div>
    </div>

    <!-- Selected user display -->
    <div v-if="selectedUser && !showDropdown" class="selected-user">
      <div class="user-info">
        <div class="user-name">
          {{ selectedUser.first_name }} {{ selectedUser.last_name }}
          <span v-if="selectedUser.persona" class="user-persona">{{ formatPersona(selectedUser.persona) }}</span>
        </div>
        <div class="user-email">{{ selectedUser.email }}</div>
      </div>
      <button
        v-if="!disabled"
        type="button"
        @click="clearSelection"
        class="clear-btn"
        title="Clear selection"
      >
        ✕
      </button>
    </div>

    <!-- Hidden input for form submission -->
    <input
      type="hidden"
      :name="name"
      :value="modelValue"
      :required="required"
    />

    <small v-if="helpText" class="help-text">{{ helpText }}</small>
    <small v-if="error" class="error-text">{{ error }}</small>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface User {
  id: string
  first_name: string
  last_name: string
  email: string
  persona?: string
  school_name?: string
}

interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  helpText?: string
  required?: boolean
  disabled?: boolean
  name?: string
  inputId?: string
  filterPersona?: string // Filter users by persona (e.g., 'teacher', 'student')
  showSchool?: boolean // Show school name in dropdown
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: 'Select User',
  placeholder: 'Search by name or email...',
  helpText: '',
  required: false,
  disabled: false,
  name: 'user_id',
  inputId: 'user_selector',
  filterPersona: '',
  showSchool: false,
  error: ''
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'select', user: User): void
}>()

const searchQuery = ref('')
const showDropdown = ref(false)
const isLoading = ref(false)
const users = ref<User[]>([])
const selectedUser = ref<User | null>(null)

// Filtered users based on search query and persona filter
const filteredUsers = computed(() => {
  let filtered = users.value

  // Filter by persona if specified
  if (props.filterPersona) {
    filtered = filtered.filter(user => user.persona === props.filterPersona)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user =>
      `${user.first_name} ${user.last_name}`.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  return filtered.slice(0, 50) // Limit to 50 results
})

// Watch for changes to modelValue from parent
watch(() => props.modelValue, async (newValue) => {
  if (newValue && newValue !== selectedUser.value?.id) {
    await loadSelectedUser(newValue)
  } else if (!newValue) {
    selectedUser.value = null
    searchQuery.value = ''
  }
}, { immediate: true })

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-selector')) {
    showDropdown.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  await loadUsers()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

/**
 * Load all users from API
 */
async function loadUsers() {
  isLoading.value = true
  try {
    const schoolId = localStorage.getItem('current_school_id')
    const params = new URLSearchParams({
      limit: '100' // API max limit is 100
    })

    if (schoolId) {
      params.append('school_id', schoolId)
    }

    const response = await fetch(`http://localhost:8000/api/v1/users?${params}`)

    if (!response.ok) {
      throw new Error('Failed to load users')
    }

    const data = await response.json()
    users.value = data.data || data.users || data || []
  } catch (error) {
    console.error('Error loading users:', error)
    users.value = []
  } finally {
    isLoading.value = false
  }
}

/**
 * Load a specific user by ID
 */
async function loadSelectedUser(userId: string) {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/users/${userId}`)

    if (!response.ok) {
      throw new Error('Failed to load user')
    }

    const user = await response.json()
    selectedUser.value = user
    searchQuery.value = `${user.first_name} ${user.last_name}`
  } catch (error) {
    console.error('Error loading user:', error)
    selectedUser.value = null
  }
}

/**
 * Handle search input
 */
function handleSearch() {
  showDropdown.value = true
}

/**
 * Select a user from dropdown
 */
function selectUser(user: User) {
  selectedUser.value = user
  searchQuery.value = `${user.first_name} ${user.last_name}`
  showDropdown.value = false
  emit('update:modelValue', user.id)
  emit('select', user)
}

/**
 * Clear selection
 */
function clearSelection() {
  selectedUser.value = null
  searchQuery.value = ''
  emit('update:modelValue', '')
  showDropdown.value = true
}

/**
 * Format persona for display
 */
function formatPersona(persona: string): string {
  return persona.charAt(0).toUpperCase() + persona.slice(1).replace('_', ' ')
}
</script>

<style scoped>
.user-selector {
  position: relative;
}

.user-selector label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 500;
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  padding-right: 2.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #42b883;
}

.search-input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.loading-icon,
.selected-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: translateY(-50%) rotate(0deg); }
  to { transform: translateY(-50%) rotate(360deg); }
}

.selected-icon {
  color: #42b883;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  margin-top: -1px;
}

.dropdown-item {
  padding: 0.75rem;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item.selected {
  background: #e8f5e9;
}

.dropdown-item.loading,
.dropdown-item.empty {
  color: #6c757d;
  text-align: center;
  cursor: default;
}

.dropdown-item.empty:hover {
  background: white;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 500;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-persona {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background: #42b883;
  color: white;
  font-size: 0.75rem;
  border-radius: 12px;
  font-weight: normal;
}

.user-email {
  font-size: 0.875rem;
  color: #6c757d;
}

.user-school {
  font-size: 0.8rem;
  color: #9e9e9e;
}

.selected-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #e8f5e9;
  border: 1px solid #42b883;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.clear-btn {
  background: none;
  border: none;
  color: #c62828;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: rgba(198, 40, 40, 0.1);
}

.help-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.error-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #c62828;
}
</style>
