/**
 * Authentication Store
 * Manages user authentication state using Keycloak and school context
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as KeycloakService from '@/services/keycloak'

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
  username?: string
  roles?: string[]
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const isAuthenticated = ref(false)
  const isInitialized = ref(false)
  const currentUser = ref<CurrentUser | null>(null)
  const selectedSchool = ref<School | null>(null)
  const availableSchools = ref<School[]>([])
  const token = ref<string | null>(null)
  const authError = ref<string | null>(null)

  // Computed
  const currentSchoolId = computed(() => selectedSchool.value?.id || null)
  const currentSchoolName = computed(() => selectedSchool.value?.name || 'No School Selected')
  const userName = computed(() => currentUser.value?.full_name || 'User')
  const userRole = computed(() => currentUser.value?.persona || 'guest')

  /**
   * Initialize Keycloak authentication
   */
  async function initializeKeycloak() {
    try {
      console.log('🔄 Initializing Keycloak...')
      const authenticated = await KeycloakService.initializeAuth()

      if (authenticated) {
        // Get user profile from Keycloak token
        const profile = KeycloakService.getUserProfile()

        if (profile) {
          console.log('👤 User profile loaded:', profile.email, profile.persona)

          // Load saved school from localStorage
          const savedSchool = localStorage.getItem('selectedSchool')
          if (savedSchool) {
            try {
              selectedSchool.value = JSON.parse(savedSchool)
            } catch (e) {
              console.error('Failed to parse saved school:', e)
            }
          }

          // Create user object from Keycloak profile
          currentUser.value = {
            id: profile.id,
            email: profile.email,
            first_name: profile.firstName,
            last_name: profile.lastName,
            full_name: profile.fullName,
            username: profile.username,
            persona: profile.persona,
            status: 'active',
            roles: profile.roles,
            school_id: selectedSchool.value?.id || '',
            school: selectedSchool.value || undefined
          }

          // Set authentication state BEFORE fetching schools
          isAuthenticated.value = true
          token.value = KeycloakService.getToken() || null

          // Save to localStorage
          localStorage.setItem('currentUser', JSON.stringify(currentUser.value))

          // Fetch schools if not already loaded
          if (availableSchools.value.length === 0) {
            try {
              await fetchSchools()
            } catch (error) {
              console.error('Failed to fetch schools:', error)
              // Don't fail auth if schools fetch fails
            }
          }

          console.log('✅ Keycloak authentication successful:', profile.fullName, `(${profile.persona})`)
          console.log('🏫 Available schools:', availableSchools.value.length)
        }
      } else {
        console.log('ℹ️ User is not authenticated')
        isAuthenticated.value = false
        currentUser.value = null
        token.value = null
      }

      isInitialized.value = true
      console.log('✓ Auth initialization complete. Authenticated:', isAuthenticated.value)
      return authenticated
    } catch (error) {
      console.error('❌ Failed to initialize Keycloak:', error)
      authError.value = 'Authentication initialization failed'
      isAuthenticated.value = false
      isInitialized.value = true
      return false
    }
  }

  /**
   * Fetch available schools from API
   */
  async function fetchSchools() {
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      }

      // Add auth token if available
      const authToken = KeycloakService.getToken()
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`
      }

      const response = await fetch(`${apiBaseUrl}/api/v1/schools?page=1&limit=100`, {
        headers
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch schools: ${response.statusText}`)
      }

      const responseData = await response.json()

      // Handle different response formats
      if (responseData.data && Array.isArray(responseData.data)) {
        availableSchools.value = responseData.data
      } else if (responseData.schools && Array.isArray(responseData.schools)) {
        availableSchools.value = responseData.schools
      } else if (Array.isArray(responseData)) {
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

    console.log('🏫 School selected:', school.name, school.id)
  }

  /**
   * Clear selected school
   */
  function clearSchool() {
    selectedSchool.value = null
    localStorage.removeItem('selectedSchool')
  }

  /**
   * Login with Keycloak
   */
  function login() {
    KeycloakService.login()
  }

  /**
   * Logout from Keycloak and clear local state
   */
  function logout() {
    // Clear local state
    currentUser.value = null
    isAuthenticated.value = false
    token.value = null
    selectedSchool.value = null
    availableSchools.value = []

    // Clear localStorage
    localStorage.removeItem('currentUser')
    localStorage.removeItem('authToken')
    localStorage.removeItem('selectedSchool')

    // Logout from Keycloak
    KeycloakService.logout()
  }

  /**
   * Get authentication token
   */
  function getToken(): string | null {
    return token.value || KeycloakService.getToken() || null
  }

  /**
   * Check if user has specific role (Keycloak-aware)
   */
  function hasRole(role: string): boolean {
    // Check Keycloak roles first
    if (KeycloakService.hasRole(role)) {
      return true
    }

    // Fallback to user persona
    return userRole.value === role
  }

  /**
   * Check if user has any of the specified roles (Keycloak-aware)
   */
  function hasAnyRole(roles: string[]): boolean {
    // Check Keycloak roles first
    if (KeycloakService.hasAnyRole(roles)) {
      return true
    }

    // Fallback to user persona
    return roles.includes(userRole.value)
  }

  /**
   * Refresh authentication state
   */
  async function refreshAuth() {
    const keycloak = KeycloakService.getKeycloak()
    if (!keycloak) {
      return false
    }

    try {
      const refreshed = await keycloak.updateToken(5)
      if (refreshed) {
        token.value = keycloak.token || null
        console.log('🔄 Token refreshed')
      }
      return true
    } catch (error) {
      console.error('Failed to refresh token:', error)
      return false
    }
  }

  return {
    // State
    isAuthenticated,
    isInitialized,
    currentUser,
    selectedSchool,
    availableSchools,
    token,
    authError,

    // Computed
    currentSchoolId,
    currentSchoolName,
    userName,
    userRole,

    // Actions
    initializeKeycloak,
    fetchSchools,
    selectSchool,
    clearSchool,
    login,
    logout,
    getToken,
    hasRole,
    hasAnyRole,
    refreshAuth
  }
})
