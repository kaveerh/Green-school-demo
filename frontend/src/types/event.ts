/**
 * Event Types
 *
 * TypeScript type definitions for school calendar events.
 */

// Event type enum
export type EventType =
  | 'assembly'
  | 'exam'
  | 'holiday'
  | 'meeting'
  | 'parent_conference'
  | 'field_trip'
  | 'sports'
  | 'performance'
  | 'workshop'
  | 'other'

// Event status enum
export type EventStatus =
  | 'scheduled'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'postponed'

// Target audience enum
export type TargetAudience =
  | 'all_school'
  | 'grade_level'
  | 'class'
  | 'custom'

// Recurrence pattern enum
export type RecurrencePattern =
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'yearly'

// Nested types
export interface EventRoom {
  id: string
  name: string
  code: string | null
}

export interface EventOrganizer {
  id: string
  name: string
  email: string
}

export interface EventSchool {
  id: string
  name: string
}

// Main Event interface
export interface Event {
  id: string
  school_id: string

  // Event details
  title: string
  description: string | null
  event_type: EventType

  // Scheduling
  start_date: string
  end_date: string
  start_time: string | null
  end_time: string | null
  is_all_day: boolean

  // Location
  location: string | null
  room_id: string | null

  // Participants
  target_audience: TargetAudience | null
  grade_levels: number[] | null
  class_ids: string[] | null

  // Organization
  organizer_id: string | null
  organizer_name: string | null

  // Settings
  status: EventStatus
  is_recurring: boolean
  recurrence_pattern: RecurrencePattern | null
  recurrence_end_date: string | null

  // RSVP
  requires_rsvp: boolean
  max_attendees: number | null
  current_attendees: number

  // Additional
  color: string | null
  reminder_sent: boolean
  attachments: Record<string, any> | null

  // Computed properties
  is_upcoming: boolean
  is_ongoing: boolean
  is_past: boolean
  duration_days: number
  has_capacity: boolean
  attendance_percentage: number

  // Relationships (optional)
  room?: EventRoom
  organizer?: EventOrganizer
  school?: EventSchool

  // Audit fields
  created_at: string
  updated_at: string
  created_by: string | null
  updated_by: string | null
}

// Request types
export interface EventCreateRequest {
  school_id: string
  title: string
  description?: string | null
  event_type: EventType

  start_date: string
  end_date: string
  start_time?: string | null
  end_time?: string | null
  is_all_day?: boolean

  location?: string | null
  room_id?: string | null

  target_audience?: TargetAudience | null
  grade_levels?: number[] | null
  class_ids?: string[] | null

  organizer_id?: string | null
  organizer_name?: string | null

  status?: EventStatus
  is_recurring?: boolean
  recurrence_pattern?: RecurrencePattern | null
  recurrence_end_date?: string | null

  requires_rsvp?: boolean
  max_attendees?: number | null

  color?: string | null
  attachments?: Record<string, any> | null
}

export interface EventUpdateRequest {
  title?: string
  description?: string | null
  event_type?: EventType

  start_date?: string
  end_date?: string
  start_time?: string | null
  end_time?: string | null
  is_all_day?: boolean

  location?: string | null
  room_id?: string | null

  target_audience?: TargetAudience | null
  grade_levels?: number[] | null
  class_ids?: string[] | null

  organizer_id?: string | null
  organizer_name?: string | null

  status?: EventStatus
  is_recurring?: boolean
  recurrence_pattern?: RecurrencePattern | null
  recurrence_end_date?: string | null

  requires_rsvp?: boolean
  max_attendees?: number | null

  color?: string | null
  attachments?: Record<string, any> | null
}

export interface EventStatusUpdateRequest {
  status: EventStatus
}

export interface EventPostponeRequest {
  new_start_date: string
  new_end_date: string
}

export interface EventRSVPUpdateRequest {
  count: number
}

// Response types
export interface EventListResponse {
  events: Event[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface EventStatistics {
  total_events: number
  by_type: Record<EventType, number>
  by_status: Record<EventStatus, number>
  rsvp_events: number
  recurring_events: number
}

// Query parameters
export interface EventListParams {
  school_id: string
  start_date?: string
  end_date?: string
  event_type?: EventType
  status?: EventStatus
  page?: number
  limit?: number
}

export interface UpcomingEventsParams {
  school_id: string
  days_ahead?: number
  limit?: number
}

export interface DateRangeEventsParams {
  school_id: string
  start_date: string
  end_date: string
}

export interface EventsByTypeParams {
  event_type: EventType
  school_id: string
  page?: number
  limit?: number
}

export interface StatisticsParams {
  school_id: string
  start_date?: string
  end_date?: string
}

// Helper functions
export function getEventTypeLabel(type: EventType): string {
  const labels: Record<EventType, string> = {
    assembly: 'Assembly',
    exam: 'Exam',
    holiday: 'Holiday',
    meeting: 'Meeting',
    parent_conference: 'Parent Conference',
    field_trip: 'Field Trip',
    sports: 'Sports',
    performance: 'Performance',
    workshop: 'Workshop',
    other: 'Other'
  }
  return labels[type]
}

export function getEventTypeColor(type: EventType): string {
  const colors: Record<EventType, string> = {
    assembly: '#3B82F6', // blue
    exam: '#EF4444', // red
    holiday: '#10B981', // green
    meeting: '#8B5CF6', // purple
    parent_conference: '#F59E0B', // amber
    field_trip: '#06B6D4', // cyan
    sports: '#EC4899', // pink
    performance: '#F97316', // orange
    workshop: '#6366F1', // indigo
    other: '#6B7280' // gray
  }
  return colors[type]
}

export function getStatusLabel(status: EventStatus): string {
  const labels: Record<EventStatus, string> = {
    scheduled: 'Scheduled',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled',
    postponed: 'Postponed'
  }
  return labels[status]
}

export function getStatusColor(status: EventStatus): string {
  const colors: Record<EventStatus, string> = {
    scheduled: 'blue',
    in_progress: 'yellow',
    completed: 'green',
    cancelled: 'red',
    postponed: 'orange'
  }
  return colors[status]
}

export function getAudienceLabel(audience: TargetAudience): string {
  const labels: Record<TargetAudience, string> = {
    all_school: 'All School',
    grade_level: 'Grade Level',
    class: 'Class',
    custom: 'Custom'
  }
  return labels[audience]
}

export function formatEventDate(event: Event): string {
  const start = new Date(event.start_date)
  const end = new Date(event.end_date)

  if (event.start_date === event.end_date) {
    return start.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
}

export function formatEventTime(event: Event): string {
  if (event.is_all_day) {
    return 'All Day'
  }

  if (!event.start_time || !event.end_time) {
    return ''
  }

  const formatTime = (timeStr: string) => {
    const [hours, minutes] = timeStr.split(':')
    const hour = parseInt(hours)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour
    return `${displayHour}:${minutes} ${ampm}`
  }

  return `${formatTime(event.start_time)} - ${formatTime(event.end_time)}`
}

export function formatEventDateTime(event: Event): string {
  const date = formatEventDate(event)
  const time = formatEventTime(event)
  return time ? `${date} • ${time}` : date
}

export function getEventIcon(type: EventType): string {
  const icons: Record<EventType, string> = {
    assembly: '👥',
    exam: '📝',
    holiday: '🎉',
    meeting: '💼',
    parent_conference: '👨‍👩‍👧',
    field_trip: '🚌',
    sports: '⚽',
    performance: '🎭',
    workshop: '🛠️',
    other: '📌'
  }
  return icons[type]
}

export function isEventEditable(event: Event): boolean {
  // Can't edit completed or cancelled events
  return !['completed', 'cancelled'].includes(event.status)
}

export function canRSVP(event: Event): boolean {
  return event.requires_rsvp && event.is_upcoming && event.has_capacity
}

export function getRSVPStatus(event: Event): string {
  if (!event.requires_rsvp) return 'No RSVP Required'
  if (!event.max_attendees) return `${event.current_attendees} registered`
  return `${event.current_attendees} / ${event.max_attendees} (${event.attendance_percentage.toFixed(0)}%)`
}
