/**
 * Authentication Store
 * Manages user authentication state and school context
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface School {
  id: string
  name: string
  slug: string
  city?: string
  state?: string
}

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  persona: string
  status: string
  phone?: string
  avatar_url?: string
}

interface CurrentUser extends User {
  school_id: string
  school?: School
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const isAuthenticated = ref(false)
  const currentUser = ref<CurrentUser | null>(null)
  const selectedSchool = ref<School | null>(null)
  const availableSchools = ref<School[]>([])
  const token = ref<string | null>(null)

  // Computed
  const currentSchoolId = computed(() => selectedSchool.value?.id || null)
  const currentSchoolName = computed(() => selectedSchool.value?.name || 'No School Selected')
  const userName = computed(() => currentUser.value?.full_name || 'User')
  const userRole = computed(() => currentUser.value?.persona || 'guest')

  /**
   * Initialize auth state from localStorage
   */
  function initializeAuth() {
    // Load from localStorage
    const savedSchool = localStorage.getItem('selectedSchool')
    const savedUser = localStorage.getItem('currentUser')
    const savedToken = localStorage.getItem('authToken')

    if (savedSchool) {
      try {
        selectedSchool.value = JSON.parse(savedSchool)
      } catch (e) {
        console.error('Failed to parse saved school:', e)
        localStorage.removeItem('selectedSchool')
      }
    }

    if (savedUser) {
      try {
        currentUser.value = JSON.parse(savedUser)
        isAuthenticated.value = true
      } catch (e) {
        console.error('Failed to parse saved user:', e)
        localStorage.removeItem('currentUser')
      }
    } else {
      // Create a default mock user if none exists (for development)
      // This will be replaced when Keycloak is integrated
      currentUser.value = {
        id: 'bed3ada7-ab32-4a74-84a0-75602181f553',
        email: 'admin@greenschool.edu',
        first_name: 'Admin',
        last_name: 'User',
        full_name: 'Admin User',
        persona: 'administrator',
        status: 'active',
        school_id: selectedSchool.value?.id || '',
        school: selectedSchool.value || undefined
      }
      isAuthenticated.value = true
      token.value = 'mock-token-dev'

      localStorage.setItem('currentUser', JSON.stringify(currentUser.value))
      localStorage.setItem('authToken', token.value)
    }

    if (savedToken) {
      token.value = savedToken
    }

    // Fetch schools asynchronously (non-blocking)
    // This will also auto-select first school if none selected
    if (availableSchools.value.length === 0) {
      fetchSchools().catch(error => {
        console.error('Failed to fetch schools on init:', error)
      })
    }
  }

  /**
   * Fetch available schools from API
   */
  async function fetchSchools() {
    try {
      const response = await fetch('http://localhost:8000/api/v1/schools?page=1&limit=100')

      if (!response.ok) {
        throw new Error(`Failed to fetch schools: ${response.statusText}`)
      }

      const responseData = await response.json()

      // Handle different response formats
      if (responseData.data && Array.isArray(responseData.data)) {
        // Format: { data: [...], pagination: {...} }
        availableSchools.value = responseData.data
      } else if (responseData.schools && Array.isArray(responseData.schools)) {
        // Format: { schools: [...] }
        availableSchools.value = responseData.schools
      } else if (Array.isArray(responseData)) {
        // Format: [...]
        availableSchools.value = responseData
      } else {
        console.error('Unexpected schools response format:', responseData)
        availableSchools.value = []
      }

      // Auto-select first school if no school is currently selected
      if (!selectedSchool.value && availableSchools.value.length > 0) {
        selectSchool(availableSchools.value[0])
      }

      return availableSchools.value
    } catch (error) {
      console.error('Failed to fetch schools:', error)
      throw error
    }
  }

  /**
   * Select a school for the current session
   */
  function selectSchool(school: School) {
    selectedSchool.value = school
    localStorage.setItem('selectedSchool', JSON.stringify(school))

    // Update current user's school context if user is logged in
    if (currentUser.value) {
      currentUser.value.school_id = school.id
      currentUser.value.school = school
      localStorage.setItem('currentUser', JSON.stringify(currentUser.value))
    }

    console.log('School selected:', school.name, school.id)
  }

  /**
   * Clear selected school
   */
  function clearSchool() {
    selectedSchool.value = null
    localStorage.removeItem('selectedSchool')
  }

  /**
   * Mock login (TODO: Replace with Keycloak integration)
   */
  async function login(email: string, password: string) {
    // TODO: Implement Keycloak authentication
    // For now, create a mock user

    // Ensure we have schools loaded and one selected
    if (availableSchools.value.length === 0) {
      await fetchSchools()
    }

    const mockUser: CurrentUser = {
      id: 'bed3ada7-ab32-4a74-84a0-75602181f553',
      email: email,
      first_name: 'Admin',
      last_name: 'User',
      full_name: 'Admin User',
      persona: 'administrator',
      status: 'active',
      school_id: selectedSchool.value?.id || '',
      school: selectedSchool.value || undefined
    }

    currentUser.value = mockUser
    isAuthenticated.value = true
    token.value = 'mock-token-' + Date.now()

    localStorage.setItem('currentUser', JSON.stringify(mockUser))
    localStorage.setItem('authToken', token.value)
  }

  /**
   * Logout
   */
  function logout() {
    currentUser.value = null
    isAuthenticated.value = false
    token.value = null
    selectedSchool.value = null
    availableSchools.value = []

    localStorage.removeItem('currentUser')
    localStorage.removeItem('authToken')
    localStorage.removeItem('selectedSchool')
  }

  /**
   * Get authentication token
   */
  function getToken(): string | null {
    return token.value
  }

  /**
   * Check if user has specific role
   */
  function hasRole(role: string): boolean {
    return userRole.value === role
  }

  /**
   * Check if user has any of the specified roles
   */
  function hasAnyRole(roles: string[]): boolean {
    return roles.includes(userRole.value)
  }

  // Initialize on store creation
  initializeAuth()

  return {
    // State
    isAuthenticated,
    currentUser,
    selectedSchool,
    availableSchools,
    token,

    // Computed
    currentSchoolId,
    currentSchoolName,
    userName,
    userRole,

    // Actions
    initializeAuth,
    fetchSchools,
    selectSchool,
    clearSchool,
    login,
    logout,
    getToken,
    hasRole,
    hasAnyRole
  }
})
