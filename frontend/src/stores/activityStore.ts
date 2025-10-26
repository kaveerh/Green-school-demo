/**
 * Activity Store
 *
 * Pinia store for managing activity state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import activityService from '@/services/activityService'
import type {
  Activity,
  ActivityEnrollment,
  ActivityCreateInput,
  ActivityUpdateInput,
  EnrollmentCreateInput,
  EnrollmentWithdrawInput,
  PaymentRecordInput,
  RosterResponse,
  PaymentSummary,
  ActivityStatistics,
  ActivityFilters,
  ActivityType,
  ActivityStatus
} from '@/types/activity'

export const useActivityStore = defineStore('activity', () => {
  // State
  const activities = ref<Activity[]>([])
  const featuredActivities = ref<Activity[]>([])
  const currentActivity = ref<Activity | null>(null)
  const currentRoster = ref<RosterResponse | null>(null)
  const studentEnrollments = ref<ActivityEnrollment[]>([])
  const paymentSummary = ref<PaymentSummary | null>(null)
  const statistics = ref<ActivityStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const total = ref(0)
  const page = ref(1)
  const limit = ref(50)
  const pages = ref(0)

  // Computed
  const totalActivities = computed(() => total.value)

  const activitiesByType = computed(() => {
    const grouped: Record<ActivityType, Activity[]> = {} as Record<
      ActivityType,
      Activity[]
    >
    activities.value.forEach(activity => {
      if (!grouped[activity.activity_type]) {
        grouped[activity.activity_type] = []
      }
      grouped[activity.activity_type].push(activity)
    })
    return grouped
  })

  const activitiesByStatus = computed(() => {
    const grouped: Record<ActivityStatus, Activity[]> = {} as Record<
      ActivityStatus,
      Activity[]
    >
    activities.value.forEach(activity => {
      if (!grouped[activity.status]) {
        grouped[activity.status] = []
      }
      grouped[activity.status].push(activity)
    })
    return grouped
  })

  const activeActivities = computed(() =>
    activities.value.filter(a => a.status === 'active')
  )

  const fullActivities = computed(() =>
    activities.value.filter(a => a.status === 'full')
  )

  const openForRegistration = computed(() =>
    activities.value.filter(a => a.registration_open && a.status === 'active')
  )

  const sportsActivities = computed(() =>
    activities.value.filter(a => a.activity_type === 'sports')
  )

  const clubsActivities = computed(() =>
    activities.value.filter(a => a.activity_type === 'club')
  )

  const artsActivities = computed(() =>
    activities.value.filter(a => a.activity_type === 'art')
  )

  const musicActivities = computed(() =>
    activities.value.filter(a => a.activity_type === 'music')
  )

  const academicActivities = computed(() =>
    activities.value.filter(a => a.activity_type === 'academic')
  )

  const totalEnrollments = computed(() => {
    return activities.value.reduce(
      (sum, activity) => sum + (activity.enrollment_count || 0),
      0
    )
  })

  const averageEnrollmentRate = computed(() => {
    const withCapacity = activities.value.filter(a => a.max_participants)
    if (withCapacity.length === 0) return 0

    const totalRate = withCapacity.reduce((sum, activity) => {
      const rate =
        ((activity.enrollment_count || 0) / (activity.max_participants || 1)) *
        100
      return sum + rate
    }, 0)

    return Math.round(totalRate / withCapacity.length)
  })

  // Actions

  /**
   * Fetch all activities with filters
   */
  async function fetchActivities(schoolId: string, filters?: ActivityFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await activityService.getActivities(schoolId, filters)
      activities.value = response.activities
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
      pages.value = response.pages
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch activities'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch activity by ID
   */
  async function fetchActivityById(activityId: string) {
    loading.value = true
    error.value = null

    try {
      currentActivity.value = await activityService.getActivityById(activityId)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch activity'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch featured activities
   */
  async function fetchFeaturedActivities(schoolId: string, limitCount: number = 10) {
    loading.value = true
    error.value = null

    try {
      featuredActivities.value = await activityService.getFeaturedActivities(
        schoolId,
        limitCount
      )
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch featured activities'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch activities by type
   */
  async function fetchActivitiesByType(
    schoolId: string,
    activityType: string,
    pageNum: number = 1,
    limitCount: number = 50
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await activityService.getActivitiesByType(
        schoolId,
        activityType,
        pageNum,
        limitCount
      )
      activities.value = response.activities
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
      pages.value = response.pages
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch activities by type'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Search activities
   */
  async function searchActivities(
    schoolId: string,
    query: string,
    pageNum: number = 1,
    limitCount: number = 50
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await activityService.searchActivities(
        schoolId,
        query,
        pageNum,
        limitCount
      )
      activities.value = response.activities
      total.value = response.total
      page.value = response.page
      limit.value = response.limit
      pages.value = response.pages
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to search activities'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new activity
   */
  async function createActivity(
    data: ActivityCreateInput,
    createdById: string
  ): Promise<Activity> {
    loading.value = true
    error.value = null

    try {
      const activity = await activityService.createActivity(data, createdById)
      activities.value.unshift(activity) // Add to beginning of list
      total.value++
      return activity
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to create activity'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update an activity
   */
  async function updateActivity(
    activityId: string,
    data: ActivityUpdateInput,
    updatedById: string
  ): Promise<Activity> {
    loading.value = true
    error.value = null

    try {
      const activity = await activityService.updateActivity(
        activityId,
        data,
        updatedById
      )

      // Update in list
      const index = activities.value.findIndex(a => a.id === activityId)
      if (index !== -1) {
        activities.value[index] = activity
      }

      // Update current if it's the same
      if (currentActivity.value?.id === activityId) {
        currentActivity.value = activity
      }

      return activity
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to update activity'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete an activity
   */
  async function deleteActivity(activityId: string, deletedById: string) {
    loading.value = true
    error.value = null

    try {
      await activityService.deleteActivity(activityId, deletedById)

      // Remove from list
      activities.value = activities.value.filter(a => a.id !== activityId)
      total.value--

      // Clear current if it's the deleted one
      if (currentActivity.value?.id === activityId) {
        currentActivity.value = null
      }
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to delete activity'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Enroll a student in an activity
   */
  async function enrollStudent(
    activityId: string,
    data: EnrollmentCreateInput,
    createdById: string
  ): Promise<ActivityEnrollment> {
    loading.value = true
    error.value = null

    try {
      const enrollment = await activityService.enrollStudent(
        activityId,
        data,
        createdById
      )

      // Update enrollment count in activity
      const activity = activities.value.find(a => a.id === activityId)
      if (activity && activity.enrollment_count !== undefined) {
        activity.enrollment_count++
      }

      return enrollment
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to enroll student'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Withdraw a student from an activity
   */
  async function withdrawStudent(
    activityId: string,
    studentId: string,
    data: EnrollmentWithdrawInput,
    withdrawnById: string
  ): Promise<ActivityEnrollment> {
    loading.value = true
    error.value = null

    try {
      const enrollment = await activityService.withdrawStudent(
        activityId,
        studentId,
        data,
        withdrawnById
      )

      // Update enrollment count in activity
      const activity = activities.value.find(a => a.id === activityId)
      if (activity && activity.enrollment_count !== undefined) {
        activity.enrollment_count = Math.max(0, activity.enrollment_count - 1)
      }

      return enrollment
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to withdraw student'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch activity roster
   */
  async function fetchActivityRoster(activityId: string) {
    loading.value = true
    error.value = null

    try {
      currentRoster.value = await activityService.getActivityRoster(activityId)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch activity roster'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch student enrollments
   */
  async function fetchStudentActivities(studentId: string, status?: string) {
    loading.value = true
    error.value = null

    try {
      studentEnrollments.value = await activityService.getStudentActivities(
        studentId,
        status
      )
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch student activities'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Record a payment
   */
  async function recordPayment(
    enrollmentId: string,
    data: PaymentRecordInput,
    updatedById: string
  ): Promise<ActivityEnrollment> {
    loading.value = true
    error.value = null

    try {
      return await activityService.recordPayment(
        enrollmentId,
        data,
        updatedById
      )
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to record payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Waive payment
   */
  async function waivePayment(
    enrollmentId: string,
    updatedById: string
  ): Promise<ActivityEnrollment> {
    loading.value = true
    error.value = null

    try {
      return await activityService.waivePayment(enrollmentId, updatedById)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to waive payment'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch payment summary
   */
  async function fetchPaymentSummary(activityId: string) {
    loading.value = true
    error.value = null

    try {
      paymentSummary.value = await activityService.getPaymentSummary(activityId)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch payment summary'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch activity statistics
   */
  async function fetchStatistics(schoolId: string) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await activityService.getStatistics(schoolId)
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : 'Failed to fetch statistics'
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
  function reset() {
    activities.value = []
    featuredActivities.value = []
    currentActivity.value = null
    currentRoster.value = null
    studentEnrollments.value = []
    paymentSummary.value = null
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
    activities,
    featuredActivities,
    currentActivity,
    currentRoster,
    studentEnrollments,
    paymentSummary,
    statistics,
    loading,
    error,
    total,
    page,
    limit,
    pages,

    // Computed
    totalActivities,
    activitiesByType,
    activitiesByStatus,
    activeActivities,
    fullActivities,
    openForRegistration,
    sportsActivities,
    clubsActivities,
    artsActivities,
    musicActivities,
    academicActivities,
    totalEnrollments,
    averageEnrollmentRate,

    // Actions
    fetchActivities,
    fetchActivityById,
    fetchFeaturedActivities,
    fetchActivitiesByType,
    searchActivities,
    createActivity,
    updateActivity,
    deleteActivity,
    enrollStudent,
    withdrawStudent,
    fetchActivityRoster,
    fetchStudentActivities,
    recordPayment,
    waivePayment,
    fetchPaymentSummary,
    fetchStatistics,
    clearError,
    reset
  }
})
