# Feature #7: Rooms (Facility Management)

**Priority**: 7 of 15
**Dependencies**: Users (Feature #1), Schools (Feature #2)
**Status**: In Progress
**Last Updated**: 2025-10-22

## Overview

Room (facility) management for tracking classrooms, labs, specialized rooms, and their equipment. Supports scheduling, capacity management, and resource allocation.

## Business Requirements

### Room Management
- Administrators can create, update, and delete rooms
- Each room belongs to a school (multi-tenant)
- Room numbers must be unique within a school
- Rooms have types: classroom, lab, gym, library, office, cafeteria
- Track capacity for scheduling purposes
- Maintain equipment inventory per room
- Support room availability and status tracking

### Scheduling Support
- Rooms can be assigned to classes
- Rooms can be reserved for events
- Track room owner (responsible teacher/admin)
- Support room availability status

### Equipment Tracking
- Each room can have multiple equipment items
- Equipment list stored as array
- Support specialized equipment for labs, gyms, etc.

## Database Schema

### Table: rooms

```sql
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id) ON DELETE CASCADE,

    -- Room Identification
    room_number VARCHAR(50) NOT NULL,
    building VARCHAR(100),
    floor INTEGER,

    -- Room Classification
    room_type VARCHAR(50) NOT NULL, -- classroom, lab, gym, library, office, cafeteria
    room_name VARCHAR(200),
    description TEXT,

    -- Capacity and Features
    capacity INTEGER NOT NULL DEFAULT 30,
    area_sqft DECIMAL(10, 2),
    equipment TEXT[], -- Array of equipment items
    features TEXT[], -- Array of features (projector, whiteboard, etc.)

    -- Assignment
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL, -- Responsible teacher/admin

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,

    -- Display
    color VARCHAR(7), -- #RRGGBB for calendar/schedule display
    icon VARCHAR(50), -- Emoji or icon identifier
    display_order INTEGER DEFAULT 0,

    -- Audit fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),

    -- Constraints
    CONSTRAINT uq_rooms_number_school UNIQUE(school_id, room_number),
    CONSTRAINT chk_rooms_type CHECK (room_type IN ('classroom', 'lab', 'gym', 'library', 'office', 'cafeteria')),
    CONSTRAINT chk_rooms_capacity CHECK (capacity > 0),
    CONSTRAINT chk_rooms_floor CHECK (floor >= -2 AND floor <= 10)
);

-- Indexes
CREATE INDEX idx_rooms_school_id ON rooms(school_id);
CREATE INDEX idx_rooms_owner_id ON rooms(owner_id);
CREATE INDEX idx_rooms_type ON rooms(room_type);
CREATE INDEX idx_rooms_active ON rooms(is_active);
CREATE INDEX idx_rooms_deleted_at ON rooms(deleted_at);
CREATE INDEX idx_rooms_school_type ON rooms(school_id, room_type);
```

## API Endpoints

### 1. Create Room
**POST** `/api/v1/rooms`

**Request Body**:
```json
{
  "school_id": "uuid",
  "room_number": "101",
  "building": "Main Building",
  "floor": 1,
  "room_type": "classroom",
  "room_name": "Math Classroom A",
  "description": "Primary mathematics classroom",
  "capacity": 30,
  "area_sqft": 800.50,
  "equipment": ["whiteboard", "projector", "30 desks", "teacher desk"],
  "features": ["air conditioning", "natural light", "internet"],
  "owner_id": "uuid",
  "is_active": true,
  "is_available": true,
  "color": "#4CAF50",
  "icon": "🏫",
  "display_order": 1
}
```

**Response**: Room object with computed fields

**Validation**:
- `school_id` (required, valid UUID, school must exist)
- `room_number` (required, 1-50 chars, unique per school)
- `room_type` (required, valid enum value)
- `capacity` (required, positive integer)
- `floor` (optional, -2 to 10)
- `color` (optional, valid hex format #RRGGBB)
- `owner_id` (optional, valid user ID, must be teacher or administrator)

### 2. List Rooms
**GET** `/api/v1/rooms`

**Query Parameters**:
- `school_id` (required) - Filter by school
- `room_type` - Filter by type
- `building` - Filter by building
- `floor` - Filter by floor
- `is_active` - Filter by active status
- `is_available` - Filter by availability
- `owner_id` - Filter by owner
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 50)

**Response**:
```json
{
  "rooms": [Room],
  "total": 45,
  "page": 1,
  "limit": 50
}
```

### 3. Get Room by ID
**GET** `/api/v1/rooms/{id}`

**Response**: Single Room object with relationships

### 4. Get Room by Number
**GET** `/api/v1/rooms/number/{room_number}`

**Query Parameters**:
- `school_id` (required)

**Response**: Single Room object

### 5. Update Room
**PUT** `/api/v1/rooms/{id}`

**Request Body**: Partial Room object (all fields optional except room_number)

**Response**: Updated Room object

**Validation**: Same as create, but all fields optional

### 6. Delete Room
**DELETE** `/api/v1/rooms/{id}`

**Response**: Success message

**Soft Delete**: Sets `deleted_at` timestamp

### 7. Toggle Room Status
**PATCH** `/api/v1/rooms/{id}/status`

**Request Body**:
```json
{
  "is_active": true
}
```

**Response**: Updated Room object

### 8. Toggle Room Availability
**PATCH** `/api/v1/rooms/{id}/availability`

**Request Body**:
```json
{
  "is_available": true
}
```

**Response**: Updated Room object

### 9. Get Rooms by Type
**GET** `/api/v1/rooms/type/{room_type}`

**Query Parameters**:
- `school_id` (required)

**Response**: Array of Room objects

### 10. Get Rooms by Building
**GET** `/api/v1/rooms/building/{building}`

**Query Parameters**:
- `school_id` (required)

**Response**: Array of Room objects

### 11. Search Rooms
**GET** `/api/v1/rooms/search/query`

**Query Parameters**:
- `q` (required) - Search query (room number, name, description)
- `school_id` (required)
- `page` - Page number
- `limit` - Results per page

**Response**: Paginated list of matching rooms

### 12. Get Room Statistics
**GET** `/api/v1/rooms/statistics/summary`

**Query Parameters**:
- `school_id` (optional) - Filter by school

**Response**:
```json
{
  "total_rooms": 45,
  "active_rooms": 42,
  "inactive_rooms": 3,
  "available_rooms": 38,
  "unavailable_rooms": 4,
  "by_type": {
    "classroom": 30,
    "lab": 5,
    "gym": 2,
    "library": 1,
    "office": 5,
    "cafeteria": 2
  },
  "by_building": {
    "Main Building": 35,
    "Science Wing": 10
  },
  "total_capacity": 1250,
  "average_capacity": 27.8,
  "equipment_count": 180
}
```

## Sample Data (5 Rooms)

```sql
-- Sample rooms for testing
INSERT INTO rooms (school_id, room_number, building, floor, room_type, room_name, capacity, equipment, features, is_active, is_available, color, icon) VALUES

-- Classroom
('{school_id}', '101', 'Main Building', 1, 'classroom', 'Math Classroom A', 30,
 ARRAY['whiteboard', 'projector', '30 desks', 'teacher desk', 'bookshelf'],
 ARRAY['air conditioning', 'natural light', 'internet'],
 TRUE, TRUE, '#4CAF50', '🏫'),

-- Science Lab
('{school_id}', '201', 'Science Wing', 2, 'lab', 'Chemistry Lab', 24,
 ARRAY['lab benches', 'fume hood', 'microscopes', 'safety equipment', 'chemical storage'],
 ARRAY['gas outlets', 'water taps', 'ventilation', 'emergency shower'],
 TRUE, TRUE, '#9C27B0', '🔬'),

-- Gymnasium
('{school_id}', 'GYM-1', 'Athletic Center', 1, 'gym', 'Main Gymnasium', 100,
 ARRAY['basketball hoops', 'volleyball nets', 'bleachers', 'scoreboard', 'mats'],
 ARRAY['high ceiling', 'locker rooms', 'sound system'],
 TRUE, TRUE, '#F44336', '⚽'),

-- Library
('{school_id}', 'LIB', 'Main Building', 2, 'library', 'School Library', 50,
 ARRAY['bookshelves', 'reading tables', '10 computers', 'printer', 'study carrels'],
 ARRAY['quiet zone', 'internet', 'catalog system', 'air conditioning'],
 TRUE, TRUE, '#795548', '📚'),

-- Art Room
('{school_id}', '305', 'Arts Building', 3, 'classroom', 'Art Studio', 25,
 ARRAY['easels', 'sink', 'storage cabinets', 'drying racks', 'pottery wheel'],
 ARRAY['natural light', 'large windows', 'ventilation', 'tile floor'],
 TRUE, TRUE, '#E91E63', '🎨');
```

## Validation Rules

### Room Number
- Required for creation
- 1-50 characters
- Can include letters, numbers, hyphens, spaces
- Unique per school (case-insensitive comparison recommended)
- Cannot be changed after creation (immutable)

### Room Type
- Required
- Must be one of: classroom, lab, gym, library, office, cafeteria
- Determines default icon and color if not specified

### Capacity
- Required
- Positive integer
- Used for class scheduling and event planning
- Minimum: 1, Maximum: 1000

### Building & Floor
- Building: optional, free text
- Floor: optional, integer between -2 and 10 (-2 for sub-basements)

### Equipment & Features
- Both are TEXT[] arrays
- Optional
- No limit on number of items
- Used for searching and filtering

### Owner
- Optional reference to a user
- Must be teacher or administrator persona
- Owner can be changed or removed
- Used to identify responsible person for room

### Color & Icon
- Color: optional, hex format #RRGGBB
- Icon: optional, emoji or icon identifier
- Default values based on room_type if not provided

## Frontend Components

### RoomList.vue
**Purpose**: Display and manage room inventory

**Features**:
- Table view with room_number, name, type, building, floor, capacity, owner, status
- Search by room number, name, description
- Filter by type, building, floor, is_active, is_available, owner
- Sort by room_number, capacity, type, building
- Statistics summary cards (total, by type, capacity, availability)
- Quick actions: view, edit, toggle status, toggle availability, delete
- Pagination
- Delete confirmation modal
- Bulk actions (future)

**Columns**:
1. Icon (color-coded by type)
2. Room Number
3. Name
4. Type (badge)
5. Building/Floor
6. Capacity
7. Owner
8. Status (active/inactive badge)
9. Availability (available/unavailable badge)
10. Actions (edit, delete)

### RoomForm.vue
**Purpose**: Create and edit rooms

**Sections**:

1. **Basic Information**
   - Room Number (immutable in edit mode)
   - Room Name
   - Description (textarea)

2. **Location**
   - Building (text input)
   - Floor (number input with -2 to 10 range)

3. **Classification**
   - Room Type (dropdown: classroom, lab, gym, library, office, cafeteria)
   - Capacity (number input, required)
   - Area (square feet, optional)

4. **Equipment & Features**
   - Equipment (multi-input field, array)
   - Features (multi-input field, array)
   - Add/remove items dynamically

5. **Assignment**
   - Owner (user dropdown, filter by teacher/administrator)
   - Status (active/inactive checkbox)
   - Availability (available/unavailable checkbox)

6. **Display Properties**
   - Color (color picker + text input for hex)
   - Icon (text input for emoji)
   - Display Order (number input)
   - Use default color/icon button (based on room_type)

7. **Preview**
   - Visual preview of how room will appear in schedules

**Validation**:
- Client-side validation for required fields
- Format validation for color (hex)
- Capacity must be positive
- Floor range validation
- Real-time duplicate room number checking

## TypeScript Types

### frontend/src/types/room.ts

```typescript
/**
 * Room Types
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
  owner_name?: string // Computed from user relationship

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
  location?: string // "Building - Floor X"
  capacity_label?: string // "30 people"
  equipment_count?: number
  is_occupied?: boolean
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
 * Helper Functions
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

export function formatLocation(room: Room): string {
  if (!room.building && room.floor === undefined) {
    return 'Location not specified'
  }

  if (room.building && room.floor !== undefined) {
    const floorLabel = room.floor === 0 ? 'Ground Floor' :
                      room.floor < 0 ? `Basement ${Math.abs(room.floor)}` :
                      `Floor ${room.floor}`
    return `${room.building} - ${floorLabel}`
  }

  if (room.building) {
    return room.building
  }

  if (room.floor !== undefined) {
    return room.floor === 0 ? 'Ground Floor' :
           room.floor < 0 ? `Basement ${Math.abs(room.floor)}` :
           `Floor ${room.floor}`
  }

  return ''
}

export function formatCapacity(capacity: number): string {
  return `${capacity} ${capacity === 1 ? 'person' : 'people'}`
}

export function isValidRoomNumber(roomNumber: string): boolean {
  return /^[A-Za-z0-9\s\-]+$/.test(roomNumber) &&
         roomNumber.length >= 1 &&
         roomNumber.length <= 50
}

export function formatRoomNumber(roomNumber: string): string {
  return roomNumber.toUpperCase().trim()
}
```

## Implementation Checklist

### Database Phase
- [x] Design schema
- [ ] Create migration SQL
- [ ] Apply migration
- [ ] Create ORM model (backend/models/room.py)
- [ ] Add sample data (5 rooms)
- [ ] Test constraints and indexes

### API Phase
- [ ] Create RoomRepository (backend/repositories/room_repository.py)
- [ ] Create RoomService (backend/services/room_service.py)
- [ ] Create RoomController (backend/controllers/room_controller.py)
- [ ] Create Pydantic schemas (backend/schemas/room_schema.py)
- [ ] Register routes in main.py
- [ ] Test all 12 endpoints manually
- [ ] Document API in docs/api/

### Frontend Phase
- [ ] Create TypeScript types (frontend/src/types/room.ts)
- [ ] Create RoomService (frontend/src/services/roomService.ts)
- [ ] Create RoomStore (frontend/src/stores/roomStore.ts)
- [ ] Create RoomList.vue component
- [ ] Create RoomForm.vue component
- [ ] Add routes to Vue Router
- [ ] Update AppNavigation.vue
- [ ] Test CRUD operations

### Testing Phase
- [ ] Backend unit tests
- [ ] API integration tests
- [ ] Playwright E2E tests
- [ ] Multi-tenancy verification

### Documentation Phase
- [ ] Update feature plan with completion status
- [ ] Update API documentation
- [ ] Commit to git

## Success Criteria

- [ ] All 12 API endpoints working
- [ ] Room CRUD operations complete
- [ ] Multi-tenant isolation verified
- [ ] Search and filtering functional
- [ ] Statistics dashboard accurate
- [ ] Frontend components responsive
- [ ] Validation working correctly
- [ ] Sample data loaded successfully
- [ ] No TypeScript errors
- [ ] All tests passing

## Notes

- Rooms are foundational for class scheduling (Feature #8)
- Room assignments used in events (Feature #12)
- Equipment tracking supports lab/gym management
- Capacity limits class enrollment
- Owner assignment creates accountability
- Availability tracking prevents double-booking

---

**Status**: Database schema designed, ready for implementation
**Next Step**: Create ORM model and migration
