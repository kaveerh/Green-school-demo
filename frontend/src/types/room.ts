/**
 * Room Types
 *
 * TypeScript type definitions for Room management.
 */

// Room Type Enum
export type RoomType = 'classroom' | 'lab' | 'gym' | 'library' | 'office' | 'cafeteria'

// Room Interface
export interface Room {
  id: string
  school_id: string

  // Identification
  room_number: string
  building?: string
  floor?: number

  // Classification
  room_type: RoomType
  room_name?: string
  description?: string

  // Capacity
  capacity: number
  area_sqft?: number
  equipment: string[]
  features: string[]

  // Assignment
  owner_id?: string
  owner_name?: string

  // Status
  is_active: boolean
  is_available: boolean

  // Display
  color?: string
  icon?: string
  display_order: number

  // Audit
  created_at: string
  updated_at: string
  deleted_at?: string

  // Computed fields
  location?: string
  capacity_label?: string
  equipment_count?: number
}

// Room Create Input
export interface RoomCreateInput {
  school_id: string
  room_number: string
  building?: string
  floor?: number
  room_type: RoomType
  room_name?: string
  description?: string
  capacity: number
  area_sqft?: number
  equipment?: string[]
  features?: string[]
  owner_id?: string
  is_active?: boolean
  is_available?: boolean
  color?: string
  icon?: string
  display_order?: number
}

// Room Update Input
export interface RoomUpdateInput {
  room_name?: string
  building?: string
  floor?: number
  room_type?: RoomType
  description?: string
  capacity?: number
  area_sqft?: number
  equipment?: string[]
  features?: string[]
  owner_id?: string
  is_active?: boolean
  is_available?: boolean
  color?: string
  icon?: string
  display_order?: number
}

// Room Search Parameters
export interface RoomSearchParams {
  school_id?: string
  room_type?: RoomType
  building?: string
  floor?: number
  is_active?: boolean
  is_available?: boolean
  owner_id?: string
  page?: number
  limit?: number
}

// Room List Response
export interface RoomListResponse {
  rooms: Room[]
  total: number
  page: number
  limit: number
}

// Room Statistics
export interface RoomStatistics {
  total_rooms: number
  active_rooms: number
  inactive_rooms: number
  available_rooms: number
  unavailable_rooms: number
  by_type: Record<string, number>
  by_building: Record<string, number>
  total_capacity: number
  average_capacity: number
  equipment_count: number
}

/**
 * Get label for room type
 */
export function getRoomTypeLabel(type: RoomType): string {
  const labels: Record<RoomType, string> = {
    classroom: 'Classroom',
    lab: 'Laboratory',
    gym: 'Gymnasium',
    library: 'Library',
    office: 'Office',
    cafeteria: 'Cafeteria'
  }
  return labels[type] || type
}

/**
 * Get default icon for room type
 */
export function getDefaultRoomIcon(type: RoomType): string {
  const icons: Record<RoomType, string> = {
    classroom: '🏫',
    lab: '🔬',
    gym: '⚽',
    library: '📚',
    office: '💼',
    cafeteria: '🍽️'
  }
  return icons[type] || '🏫'
}

/**
 * Get default color for room type
 */
export function getDefaultRoomColor(type: RoomType): string {
  const colors: Record<RoomType, string> = {
    classroom: '#4CAF50',
    lab: '#9C27B0',
    gym: '#F44336',
    library: '#795548',
    office: '#607D8B',
    cafeteria: '#FF9800'
  }
  return colors[type] || '#757575'
}

/**
 * Format location string
 */
export function formatLocation(room: Room): string {
  if (!room.building && room.floor === undefined) {
    return 'Location not specified'
  }

  const parts: string[] = []

  if (room.building) {
    parts.push(room.building)
  }

  if (room.floor !== undefined) {
    const floorLabel = room.floor === 0 ? 'Ground Floor' :
                      room.floor < 0 ? `Basement ${Math.abs(room.floor)}` :
                      `Floor ${room.floor}`
    parts.push(floorLabel)
  }

  return parts.join(' - ')
}

/**
 * Format capacity label
 */
export function formatCapacity(capacity: number): string {
  return `${capacity} ${capacity === 1 ? 'person' : 'people'}`
}

/**
 * Validate room number format
 */
export function isValidRoomNumber(roomNumber: string): boolean {
  return /^[A-Za-z0-9\s\-]+$/.test(roomNumber) &&
         roomNumber.length >= 1 &&
         roomNumber.length <= 50
}

/**
 * Format room number (uppercase, trim)
 */
export function formatRoomNumber(roomNumber: string): string {
  return roomNumber.toUpperCase().trim()
}

/**
 * Validate hex color format
 */
export function isValidHexColor(color: string): boolean {
  return /^#[0-9A-Fa-f]{6}$/.test(color)
}

/**
 * Get color for room type badge
 */
export function getRoomTypeColor(type: RoomType): string {
  return getDefaultRoomColor(type)
}

/**
 * Format floor display
 */
export function formatFloor(floor: number): string {
  if (floor === 0) return 'Ground Floor'
  if (floor < 0) return `Basement ${Math.abs(floor)}`
  return `Floor ${floor}`
}

/**
 * Validate floor range
 */
export function isValidFloor(floor: number): boolean {
  return floor >= -2 && floor <= 10
}

/**
 * Get all room types
 */
export function getAllRoomTypes(): RoomType[] {
  return ['classroom', 'lab', 'gym', 'library', 'office', 'cafeteria']
}

/**
 * Get room type options for select
 */
export function getRoomTypeOptions(): Array<{ value: RoomType; label: string }> {
  return getAllRoomTypes().map(type => ({
    value: type,
    label: getRoomTypeLabel(type)
  }))
}

/**
 * Check if room is large capacity
 */
export function isLargeCapacity(capacity: number): boolean {
  return capacity > 50
}

/**
 * Check if room is small capacity
 */
export function isSmallCapacity(capacity: number): boolean {
  return capacity < 15
}

/**
 * Get capacity size label
 */
export function getCapacitySizeLabel(capacity: number): string {
  if (isLargeCapacity(capacity)) return 'Large'
  if (isSmallCapacity(capacity)) return 'Small'
  return 'Medium'
}
