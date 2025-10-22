/**
 * Room Store
 *
 * Pinia store for managing room state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { roomService } from '@/services/roomService'
import type {
  Room,
  RoomCreateInput,
  RoomUpdateInput,
  RoomSearchParams,
  RoomStatistics
} from '@/types/room'

export const useRoomStore = defineStore('room', () => {
  // State
  const rooms = ref<Room[]>([])
  const selectedRoom = ref<Room | null>(null)
  const statistics = ref<RoomStatistics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalRooms = ref(0)
  const pageSize = ref(50)

  // Computed
  const totalPages = computed(() => Math.ceil(totalRooms.value / pageSize.value))

  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  const hasPreviousPage = computed(() => currentPage.value > 1)

  // Actions

  /**
   * Fetch all rooms
   */
  async function fetchRooms(params: RoomSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await roomService.getRooms({
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      rooms.value = response.rooms
      totalRooms.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch rooms'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch room by ID
   */
  async function fetchRoomById(id: string) {
    isLoading.value = true
    error.value = null

    try {
      const room = await roomService.getRoomById(id)
      selectedRoom.value = room
      return room
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch room'
      selectedRoom.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch room by room number
   */
  async function fetchRoomByNumber(roomNumber: string, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const room = await roomService.getRoomByNumber(roomNumber, schoolId)
      selectedRoom.value = room
      return room
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch room'
      selectedRoom.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create new room
   */
  async function createRoom(roomData: RoomCreateInput) {
    isLoading.value = true
    error.value = null

    try {
      const newRoom = await roomService.createRoom(roomData)

      // Add to list
      rooms.value.unshift(newRoom)
      totalRooms.value++

      return newRoom
    } catch (err: any) {
      error.value = err.message || 'Failed to create room'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update room
   */
  async function updateRoom(id: string, roomData: RoomUpdateInput) {
    isLoading.value = true
    error.value = null

    try {
      const updatedRoom = await roomService.updateRoom(id, roomData)

      // Update in list
      const index = rooms.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        rooms.value[index] = updatedRoom
      }

      // Update selected if it's the same
      if (selectedRoom.value?.id === id) {
        selectedRoom.value = updatedRoom
      }

      return updatedRoom
    } catch (err: any) {
      error.value = err.message || 'Failed to update room'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete room
   */
  async function deleteRoom(id: string) {
    isLoading.value = true
    error.value = null

    try {
      await roomService.deleteRoom(id)

      // Remove from list
      rooms.value = rooms.value.filter((r) => r.id !== id)
      totalRooms.value--

      // Clear selected if it's the same
      if (selectedRoom.value?.id === id) {
        selectedRoom.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete room'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle room status
   */
  async function toggleStatus(id: string, isActive: boolean) {
    isLoading.value = true
    error.value = null

    try {
      const updatedRoom = await roomService.toggleStatus(id, isActive)

      // Update in list
      const index = rooms.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        rooms.value[index] = updatedRoom
      }

      // Update selected if it's the same
      if (selectedRoom.value?.id === id) {
        selectedRoom.value = updatedRoom
      }

      return updatedRoom
    } catch (err: any) {
      error.value = err.message || 'Failed to toggle status'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Toggle room availability
   */
  async function toggleAvailability(id: string, isAvailable: boolean) {
    isLoading.value = true
    error.value = null

    try {
      const updatedRoom = await roomService.toggleAvailability(id, isAvailable)

      // Update in list
      const index = rooms.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        rooms.value[index] = updatedRoom
      }

      // Update selected if it's the same
      if (selectedRoom.value?.id === id) {
        selectedRoom.value = updatedRoom
      }

      return updatedRoom
    } catch (err: any) {
      error.value = err.message || 'Failed to toggle availability'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Search rooms
   */
  async function searchRooms(query: string, params: RoomSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await roomService.searchRooms(query, {
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      rooms.value = response.rooms
      totalRooms.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to search rooms'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch rooms by type
   */
  async function fetchRoomsByType(type: string, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const typeRooms = await roomService.getRoomsByType(type, schoolId)
      return typeRooms
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch rooms by type'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch rooms by building
   */
  async function fetchRoomsByBuilding(building: string, schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const buildingRooms = await roomService.getRoomsByBuilding(building, schoolId)
      return buildingRooms
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch rooms by building'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch statistics
   */
  async function fetchStatistics(schoolId?: string) {
    isLoading.value = true
    error.value = null

    try {
      const stats = await roomService.getStatistics(schoolId)
      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch available rooms
   */
  async function fetchAvailableRooms(schoolId: string) {
    isLoading.value = true
    error.value = null

    try {
      const availableRooms = await roomService.getAvailableRooms(schoolId)
      return availableRooms
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch available rooms'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Go to next page
   */
  async function nextPage() {
    if (hasNextPage.value) {
      currentPage.value++
      await fetchRooms()
    }
  }

  /**
   * Go to previous page
   */
  async function previousPage() {
    if (hasPreviousPage.value) {
      currentPage.value--
      await fetchRooms()
    }
  }

  /**
   * Go to specific page
   */
  async function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      await fetchRooms()
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Clear selected room
   */
  function clearSelected() {
    selectedRoom.value = null
  }

  /**
   * Reset store
   */
  function $reset() {
    rooms.value = []
    selectedRoom.value = null
    statistics.value = null
    isLoading.value = false
    error.value = null
    currentPage.value = 1
    totalRooms.value = 0
    pageSize.value = 50
  }

  return {
    // State
    rooms,
    selectedRoom,
    statistics,
    isLoading,
    error,
    currentPage,
    totalRooms,
    pageSize,

    // Computed
    totalPages,
    hasNextPage,
    hasPreviousPage,

    // Actions
    fetchRooms,
    fetchRoomById,
    fetchRoomByNumber,
    createRoom,
    updateRoom,
    deleteRoom,
    toggleStatus,
    toggleAvailability,
    searchRooms,
    fetchRoomsByType,
    fetchRoomsByBuilding,
    fetchStatistics,
    fetchAvailableRooms,
    nextPage,
    previousPage,
    goToPage,
    clearError,
    clearSelected,
    $reset,
  }
})
