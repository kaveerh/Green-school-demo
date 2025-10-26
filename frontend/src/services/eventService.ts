/**
 * Event Service
 *
 * API client for Event operations.
 */

import type {
  Event,
  EventCreateRequest,
  EventUpdateRequest,
  EventStatusUpdateRequest,
  EventPostponeRequest,
  EventRSVPUpdateRequest,
  EventListResponse,
  EventStatistics,
  EventListParams,
  UpcomingEventsParams,
  DateRangeEventsParams,
  EventsByTypeParams,
  StatisticsParams
} from '@/types/event'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class EventService {
  /**
   * Create a new event
   */
  async createEvent(
    data: EventCreateRequest,
    createdById: string
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events?created_by_id=${createdById}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create event')
    }

    return response.json()
  }

  /**
   * Get all events with filters and pagination
   */
  async getEvents(params: EventListParams): Promise<EventListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)

    if (params.start_date) queryParams.append('start_date', params.start_date)
    if (params.end_date) queryParams.append('end_date', params.end_date)
    if (params.event_type) queryParams.append('event_type', params.event_type)
    if (params.status) queryParams.append('status', params.status)
    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/events?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch events')
    }

    return response.json()
  }

  /**
   * Get upcoming events
   */
  async getUpcomingEvents(params: UpcomingEventsParams): Promise<Event[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)

    if (params.days_ahead)
      queryParams.append('days_ahead', params.days_ahead.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/events/upcoming?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch upcoming events')
    }

    return response.json()
  }

  /**
   * Get events by date range
   */
  async getEventsByDateRange(
    params: DateRangeEventsParams
  ): Promise<Event[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)
    queryParams.append('start_date', params.start_date)
    queryParams.append('end_date', params.end_date)

    const response = await fetch(
      `${API_BASE}/api/v1/events/date-range?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch events by date range')
    }

    return response.json()
  }

  /**
   * Get events by type
   */
  async getEventsByType(params: EventsByTypeParams): Promise<EventListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)

    if (params.page) queryParams.append('page', params.page.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/events/type/${params.event_type}?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch events by type')
    }

    return response.json()
  }

  /**
   * Get events by organizer
   */
  async getEventsByOrganizer(
    organizerId: string,
    page: number = 1,
    limit: number = 50
  ): Promise<EventListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', page.toString())
    queryParams.append('limit', limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/events/organizer/${organizerId}?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch events by organizer')
    }

    return response.json()
  }

  /**
   * Get events by room
   */
  async getEventsByRoom(
    roomId: string,
    startDate?: string,
    endDate?: string
  ): Promise<Event[]> {
    const queryParams = new URLSearchParams()
    if (startDate) queryParams.append('start_date', startDate)
    if (endDate) queryParams.append('end_date', endDate)

    const response = await fetch(
      `${API_BASE}/api/v1/events/room/${roomId}?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch events by room')
    }

    return response.json()
  }

  /**
   * Get RSVP events
   */
  async getRSVPEvents(
    schoolId: string,
    upcomingOnly: boolean = true
  ): Promise<Event[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)
    queryParams.append('upcoming_only', upcomingOnly.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/events/rsvp?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch RSVP events')
    }

    return response.json()
  }

  /**
   * Get recurring events
   */
  async getRecurringEvents(schoolId: string): Promise<Event[]> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/recurring?school_id=${schoolId}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch recurring events')
    }

    return response.json()
  }

  /**
   * Get event statistics
   */
  async getStatistics(params: StatisticsParams): Promise<EventStatistics> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', params.school_id)

    if (params.start_date) queryParams.append('start_date', params.start_date)
    if (params.end_date) queryParams.append('end_date', params.end_date)

    const response = await fetch(
      `${API_BASE}/api/v1/events/statistics/summary?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch event statistics')
    }

    return response.json()
  }

  /**
   * Get event by ID
   */
  async getEventById(id: string): Promise<Event> {
    const response = await fetch(`${API_BASE}/api/v1/events/${id}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch event')
    }

    return response.json()
  }

  /**
   * Update an event
   */
  async updateEvent(
    id: string,
    data: EventUpdateRequest,
    updatedById: string
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}?updated_by_id=${updatedById}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update event')
    }

    return response.json()
  }

  /**
   * Update event status
   */
  async updateEventStatus(
    id: string,
    data: EventStatusUpdateRequest,
    updatedById: string
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}/status?updated_by_id=${updatedById}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update event status')
    }

    return response.json()
  }

  /**
   * Postpone an event
   */
  async postponeEvent(
    id: string,
    data: EventPostponeRequest,
    updatedById: string
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}/postpone?updated_by_id=${updatedById}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to postpone event')
    }

    return response.json()
  }

  /**
   * Increment RSVP count
   */
  async incrementRSVP(
    id: string,
    data: EventRSVPUpdateRequest
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}/rsvp/increment`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to increment RSVP count')
    }

    return response.json()
  }

  /**
   * Decrement RSVP count
   */
  async decrementRSVP(
    id: string,
    data: EventRSVPUpdateRequest
  ): Promise<Event> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}/rsvp/decrement`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to decrement RSVP count')
    }

    return response.json()
  }

  /**
   * Delete an event
   */
  async deleteEvent(id: string, deletedById: string): Promise<void> {
    const response = await fetch(
      `${API_BASE}/api/v1/events/${id}?deleted_by_id=${deletedById}`,
      {
        method: 'DELETE'
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete event')
    }
  }
}

export default new EventService()
