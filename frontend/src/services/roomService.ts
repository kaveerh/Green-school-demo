/**
 * Room Service
 *
 * API client for Room operations.
 */

import type {
  Room,
  RoomCreateInput,
  RoomUpdateInput,
  RoomListResponse,
  RoomSearchParams,
  RoomStatistics
} from '@/types/room'

const API_BASE_URL = 'http://localhost:8000/api/v1'

class RoomService {
  /**
   * Create a new room
   */
  async createRoom(roomData: RoomCreateInput): Promise<Room> {
    const response = await fetch(`${API_BASE_URL}/rooms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(roomData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create room')
    }

    return response.json()
  }

  /**
   * Get all rooms with pagination and filters
   */
  async getRooms(params: RoomSearchParams = {}): Promise<RoomListResponse> {
    const searchParams = new URLSearchParams()

    if (params.school_id) {
      searchParams.append('school_id', params.school_id)
    }

    if (params.room_type) {
      searchParams.append('room_type', params.room_type)
    }

    if (params.building) {
      searchParams.append('building', params.building)
    }

    if (params.floor !== undefined) {
      searchParams.append('floor', params.floor.toString())
    }

    if (params.is_active !== undefined) {
      searchParams.append('is_active', params.is_active.toString())
    }

    if (params.is_available !== undefined) {
      searchParams.append('is_available', params.is_available.toString())
    }

    if (params.owner_id) {
      searchParams.append('owner_id', params.owner_id)
    }

    if (params.page) {
      searchParams.append('page', params.page.toString())
    }

    if (params.limit) {
      searchParams.append('limit', params.limit.toString())
    }

    const response = await fetch(`${API_BASE_URL}/rooms?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to fetch rooms')
    }

    return response.json()
  }

  /**
   * Get room by ID
   */
  async getRoomById(id: string): Promise<Room> {
    const response = await fetch(`${API_BASE_URL}/rooms/${id}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Room not found')
      }
      throw new Error('Failed to fetch room')
    }

    return response.json()
  }

  /**
   * Get room by room number
   */
  async getRoomByNumber(roomNumber: string, schoolId: string): Promise<Room> {
    const response = await fetch(
      `${API_BASE_URL}/rooms/number/${roomNumber}?school_id=${schoolId}`
    )

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Room not found')
      }
      throw new Error('Failed to fetch room')
    }

    return response.json()
  }

  /**
   * Update room
   */
  async updateRoom(id: string, roomData: RoomUpdateInput): Promise<Room> {
    const response = await fetch(`${API_BASE_URL}/rooms/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(roomData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update room')
    }

    return response.json()
  }

  /**
   * Delete room
   */
  async deleteRoom(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/rooms/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Room not found')
      }
      throw new Error('Failed to delete room')
    }
  }

  /**
   * Toggle room active status
   */
  async toggleStatus(id: string, isActive: boolean): Promise<Room> {
    const response = await fetch(`${API_BASE_URL}/rooms/${id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_active: isActive }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to toggle status')
    }

    return response.json()
  }

  /**
   * Toggle room availability
   */
  async toggleAvailability(id: string, isAvailable: boolean): Promise<Room> {
    const response = await fetch(`${API_BASE_URL}/rooms/${id}/availability`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_available: isAvailable }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to toggle availability')
    }

    return response.json()
  }

  /**
   * Get rooms by type
   */
  async getRoomsByType(type: string, schoolId: string): Promise<Room[]> {
    const response = await fetch(
      `${API_BASE_URL}/rooms/type/${type}?school_id=${schoolId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch rooms by type')
    }

    return response.json()
  }

  /**
   * Get rooms by building
   */
  async getRoomsByBuilding(building: string, schoolId: string): Promise<Room[]> {
    const response = await fetch(
      `${API_BASE_URL}/rooms/building/${building}?school_id=${schoolId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch rooms by building')
    }

    return response.json()
  }

  /**
   * Search rooms
   */
  async searchRooms(
    query: string,
    params: RoomSearchParams = {}
  ): Promise<RoomListResponse> {
    const searchParams = new URLSearchParams()
    searchParams.append('q', query)

    if (params.school_id) {
      searchParams.append('school_id', params.school_id)
    }

    if (params.page) {
      searchParams.append('page', params.page.toString())
    }

    if (params.limit) {
      searchParams.append('limit', params.limit.toString())
    }

    const response = await fetch(`${API_BASE_URL}/rooms/search/query?${searchParams}`)

    if (!response.ok) {
      throw new Error('Failed to search rooms')
    }

    return response.json()
  }

  /**
   * Get room statistics
   */
  async getStatistics(schoolId?: string): Promise<RoomStatistics> {
    const searchParams = new URLSearchParams()

    if (schoolId) {
      searchParams.append('school_id', schoolId)
    }

    const response = await fetch(
      `${API_BASE_URL}/rooms/statistics/summary?${searchParams}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch statistics')
    }

    return response.json()
  }

  /**
   * Get available rooms
   */
  async getAvailableRooms(schoolId: string): Promise<Room[]> {
    const response = await fetch(
      `${API_BASE_URL}/rooms/available/list?school_id=${schoolId}`
    )

    if (!response.ok) {
      throw new Error('Failed to fetch available rooms')
    }

    return response.json()
  }
}

// Export singleton instance
export const roomService = new RoomService()
export default roomService
