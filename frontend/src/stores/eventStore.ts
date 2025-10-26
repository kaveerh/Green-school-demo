/**
 * Event Store
 *
 * Pinia store for managing event state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import eventService from '@/services/eventService'
import type {
  Event,
  EventCreateRequest,
  EventUpdateRequest,
  EventStatusUpdateRequest,
  EventPostponeRequest,
  EventRSVPUpdateRequest,
  EventStatistics,
  EventListParams,
  UpcomingEventsParams,
  DateRangeEventsParams,
  EventsByTypeParams,
  StatisticsParams,
  EventType,
  EventStatus
} from '@/types/event'

export const useEventStore = defineStore('event', () => {
  // State
  const events = ref<Event[]>([])
  const upcomingEvents = ref<Event[]>([])
  const currentEvent = ref<Event | null>(null)
  const statistics = ref<EventStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const total = ref(0)
  const page = ref(1)
  const limit = ref(50)
  const pages = ref(0)

  // Computed
  const totalEvents = computed(() => total.value)

  const eventsByType = computed(() => {
    const grouped: Record<string, Event[]> = {}
    events.value.forEach(event => {
      if (!grouped[event.event_type]) {
        grouped[event.event_type] = []
      }
      grouped[event.event_type].push(event)
    })
    return grouped
  })

  const eventsByStatus = computed(() => {
    const grouped: Record<string, Event[]> = {}
    events.value.forEach(event => {
      if (!grouped[event.status]) {
        grouped[event.status] = []
      }
      grouped[event.status].push(event)
    })
    return grouped
  })

  const upcomingCount = computed(() =>
    events.value.filter(e => e.is_upcoming).length
  )

  const ongoingCount = computed(() =>
    events.value.filter(e => e.is_ongoing).length
  )

  const rsvpEvents = computed(() =>
    events.value.filter(e => e.requires_rsvp)
  )

  const recurringEvents = computed(() =>
    events.value.filter(e => e.is_recurring)
  )

  const eventsByMonth = computed(() => {
    const grouped: Record<string, Event[]> = {}
    events.value.forEach(event => {
      const monthKey = event.start_date.substring(0, 7) // YYYY-MM
      if (!grouped[monthKey]) {
        grouped[monthKey] = []
      }
      grouped[monthKey].push(event)
    })
    return grouped
  })

  // Actions

  /**
   * Fetch all events with filters
   */
  async function fetchEvents(params: EventListParams) {
    loading.value = true
    error.value = null

    try {
      const response = await eventService.getEvents(params)
      events.value = response.events
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
      pages.value = response.pages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch events'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch upcoming events
   */
  async function fetchUpcomingEvents(params: UpcomingEventsParams) {
    loading.value = true
    error.value = null

    try {
      upcomingEvents.value = await eventService.getUpcomingEvents(params)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch upcoming events'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch events by date range
   */
  async function fetchEventsByDateRange(params: DateRangeEventsParams) {
    loading.value = true
    error.value = null

    try {
      const rangeEvents = await eventService.getEventsByDateRange(params)
      // Add to events array without replacing it
      events.value = rangeEvents
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch events by date range'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch events by type
   */
  async function fetchEventsByType(params: EventsByTypeParams) {
    loading.value = true
    error.value = null

    try {
      const response = await eventService.getEventsByType(params)
      events.value = response.events
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
      pages.value = response.pages
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch events by type'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch RSVP events
   */
  async function fetchRSVPEvents(schoolId: string, upcomingOnly: boolean = true) {
    loading.value = true
    error.value = null

    try {
      const rsvpEventsList = await eventService.getRSVPEvents(schoolId, upcomingOnly)
      events.value = rsvpEventsList
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch RSVP events'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch recurring events
   */
  async function fetchRecurringEvents(schoolId: string) {
    loading.value = true
    error.value = null

    try {
      const recurringEventsList = await eventService.getRecurringEvents(schoolId)
      events.value = recurringEventsList
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch recurring events'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch event statistics
   */
  async function fetchStatistics(params: StatisticsParams) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await eventService.getStatistics(params)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch a single event by ID
   */
  async function fetchEventById(id: string) {
    loading.value = true
    error.value = null

    try {
      currentEvent.value = await eventService.getEventById(id)
      return currentEvent.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch event'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new event
   */
  async function createEvent(data: EventCreateRequest, createdById: string) {
    loading.value = true
    error.value = null

    try {
      const newEvent = await eventService.createEvent(data, createdById)
      events.value.unshift(newEvent)
      total.value++
      return newEvent
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create event'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update an event
   */
  async function updateEvent(
    id: string,
    data: EventUpdateRequest,
    updatedById: string
  ) {
    loading.value = true
    error.value = null

    try {
      const updatedEvent = await eventService.updateEvent(id, data, updatedById)

      // Update in events array
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = updatedEvent
      }

      // Update current event if it's the one being updated
      if (currentEvent.value?.id === id) {
        currentEvent.value = updatedEvent
      }

      return updatedEvent
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update event'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update event status
   */
  async function updateEventStatus(
    id: string,
    status: EventStatus,
    updatedById: string
  ) {
    loading.value = true
    error.value = null

    try {
      const updatedEvent = await eventService.updateEventStatus(
        id,
        { status },
        updatedById
      )

      // Update in events array
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = updatedEvent
      }

      // Update current event if it's the one being updated
      if (currentEvent.value?.id === id) {
        currentEvent.value = updatedEvent
      }

      return updatedEvent
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to update event status'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Postpone an event
   */
  async function postponeEvent(
    id: string,
    newStartDate: string,
    newEndDate: string,
    updatedById: string
  ) {
    loading.value = true
    error.value = null

    try {
      const postponedEvent = await eventService.postponeEvent(
        id,
        { new_start_date: newStartDate, new_end_date: newEndDate },
        updatedById
      )

      // Update in events array
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = postponedEvent
      }

      // Update current event if it's the one being updated
      if (currentEvent.value?.id === id) {
        currentEvent.value = postponedEvent
      }

      return postponedEvent
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to postpone event'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Increment RSVP count
   */
  async function incrementRSVP(id: string, count: number = 1) {
    loading.value = true
    error.value = null

    try {
      const updatedEvent = await eventService.incrementRSVP(id, { count })

      // Update in events array
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = updatedEvent
      }

      // Update current event if it's the one being updated
      if (currentEvent.value?.id === id) {
        currentEvent.value = updatedEvent
      }

      return updatedEvent
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to increment RSVP count'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Decrement RSVP count
   */
  async function decrementRSVP(id: string, count: number = 1) {
    loading.value = true
    error.value = null

    try {
      const updatedEvent = await eventService.decrementRSVP(id, { count })

      // Update in events array
      const index = events.value.findIndex(e => e.id === id)
      if (index !== -1) {
        events.value[index] = updatedEvent
      }

      // Update current event if it's the one being updated
      if (currentEvent.value?.id === id) {
        currentEvent.value = updatedEvent
      }

      return updatedEvent
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to decrement RSVP count'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete an event
   */
  async function deleteEvent(id: string, deletedById: string) {
    loading.value = true
    error.value = null

    try {
      await eventService.deleteEvent(id, deletedById)

      // Remove from events array
      events.value = events.value.filter(e => e.id !== id)
      total.value--

      // Clear current event if it's the one being deleted
      if (currentEvent.value?.id === id) {
        currentEvent.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete event'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Reset store
   */
  function $reset() {
    events.value = []
    upcomingEvents.value = []
    currentEvent.value = null
    statistics.value = null
    loading.value = false
    error.value = null
    total.value = 0
    page.value = 1
    limit.value = 50
    pages.value = 0
  }

  return {
    // State
    events,
    upcomingEvents,
    currentEvent,
    statistics,
    loading,
    error,
    total,
    page,
    limit,
    pages,

    // Computed
    totalEvents,
    eventsByType,
    eventsByStatus,
    upcomingCount,
    ongoingCount,
    rsvpEvents,
    recurringEvents,
    eventsByMonth,

    // Actions
    fetchEvents,
    fetchUpcomingEvents,
    fetchEventsByDateRange,
    fetchEventsByType,
    fetchRSVPEvents,
    fetchRecurringEvents,
    fetchStatistics,
    fetchEventById,
    createEvent,
    updateEvent,
    updateEventStatus,
    postponeEvent,
    incrementRSVP,
    decrementRSVP,
    deleteEvent,
    clearError,
    $reset
  }
})
