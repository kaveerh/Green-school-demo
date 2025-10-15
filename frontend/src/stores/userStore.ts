/**
 * User Store
 * Pinia store for user state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  User,
  UserCreateInput,
  UserUpdateInput,
  UserSearchParams,
  PaginatedResponse,
  UserStatistics
} from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const selectedUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const statistics = ref<UserStatistics | null>(null)

  // Getters
  const totalUsers = computed(() => pagination.value.total)
  const hasUsers = computed(() => users.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const usersByPersona = computed(() => {
    return (persona: string) => users.value.filter(u => u.persona === persona)
  })

  const activeUsers = computed(() =>
    users.value.filter(u => u.status === 'active')
  )

  const inactiveUsers = computed(() =>
    users.value.filter(u => u.status !== 'active')
  )

  // Actions
  async function fetchUsers(params?: UserSearchParams) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const response = await userService.getUsers(params)

      users.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch users'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUserById(id: string) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const user = await userService.getUserById(id)

      selectedUser.value = user
      return user
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch user'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createUser(userData: UserCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const user = await userService.createUser(userData)

      // Add to local state
      users.value.unshift(user)
      pagination.value.total++

      return user
    } catch (err: any) {
      error.value = err.message || 'Failed to create user'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateUser(id: string, userData: UserUpdateInput) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const updatedUser = await userService.updateUser(id, userData)

      // Update in local state
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      if (selectedUser.value?.id === id) {
        selectedUser.value = updatedUser
      }

      return updatedUser
    } catch (err: any) {
      error.value = err.message || 'Failed to update user'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteUser(id: string) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      await userService.deleteUser(id)

      // Remove from local state
      users.value = users.value.filter(u => u.id !== id)
      pagination.value.total--

      if (selectedUser.value?.id === id) {
        selectedUser.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete user'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changeUserStatus(id: string, status: 'active' | 'inactive' | 'suspended') {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const updatedUser = await userService.changeUserStatus(id, status)

      // Update in local state
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      if (selectedUser.value?.id === id) {
        selectedUser.value = updatedUser
      }

      return updatedUser
    } catch (err: any) {
      error.value = err.message || 'Failed to change user status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changeUserPersona(id: string, persona: string) {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const updatedUser = await userService.changeUserPersona(id, persona)

      // Update in local state
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      if (selectedUser.value?.id === id) {
        selectedUser.value = updatedUser
      }

      return updatedUser
    } catch (err: any) {
      error.value = err.message || 'Failed to change user persona'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics() {
    loading.value = true
    error.value = null

    try {
      const { userService } = await import('@/services/userService')
      const stats = await userService.getStatistics()

      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedUser(user: User | null) {
    selectedUser.value = user
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    users.value = []
    currentUser.value = null
    selectedUser.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    }
    statistics.value = null
  }

  return {
    // State
    users,
    currentUser,
    selectedUser,
    loading,
    error,
    pagination,
    statistics,

    // Getters
    totalUsers,
    hasUsers,
    isLoading,
    hasError,
    usersByPersona,
    activeUsers,
    inactiveUsers,

    // Actions
    fetchUsers,
    fetchUserById,
    createUser,
    updateUser,
    deleteUser,
    changeUserStatus,
    changeUserPersona,
    fetchStatistics,
    setSelectedUser,
    clearError,
    resetState
  }
})
