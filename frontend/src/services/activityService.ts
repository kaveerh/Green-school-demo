/**
 * Activity Service
 *
 * API client for Activity and ActivityEnrollment operations.
 */

import type {
  Activity,
  ActivityEnrollment,
  ActivityCreateInput,
  ActivityUpdateInput,
  EnrollmentCreateInput,
  EnrollmentWithdrawInput,
  PaymentRecordInput,
  ActivityListResponse,
  RosterResponse,
  PaymentSummary,
  ActivityStatistics,
  ActivityFilters
} from '@/types/activity'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ActivityService {
  // ===== Activity CRUD Methods =====

  /**
   * Create a new activity
   */
  async createActivity(
    data: ActivityCreateInput,
    createdById: string
  ): Promise<Activity> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities?created_by_id=${createdById}`,
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
      throw new Error(error.detail || 'Failed to create activity')
    }

    return response.json()
  }

  /**
   * Get all activities with filters and pagination
   */
  async getActivities(
    schoolId: string,
    filters?: ActivityFilters
  ): Promise<ActivityListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)

    if (filters?.activity_type)
      queryParams.append('activity_type', filters.activity_type)
    if (filters?.status) queryParams.append('activity_status', filters.status)
    if (filters?.grade_level)
      queryParams.append('grade_level', filters.grade_level.toString())
    if (filters?.registration_open !== undefined)
      queryParams.append('registration_open', filters.registration_open.toString())
    if (filters?.page) queryParams.append('page', filters.page.toString())
    if (filters?.limit) queryParams.append('limit', filters.limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/activities?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activities')
    }

    return response.json()
  }

  /**
   * Get activity by ID
   */
  async getActivityById(activityId: string): Promise<Activity> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activity')
    }

    return response.json()
  }

  /**
   * Update an activity
   */
  async updateActivity(
    activityId: string,
    data: ActivityUpdateInput,
    updatedById: string
  ): Promise<Activity> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}?updated_by_id=${updatedById}`,
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
      throw new Error(error.detail || 'Failed to update activity')
    }

    return response.json()
  }

  /**
   * Delete an activity (soft delete)
   */
  async deleteActivity(activityId: string, deletedById: string): Promise<void> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}?deleted_by_id=${deletedById}`,
      {
        method: 'DELETE'
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete activity')
    }
  }

  // ===== Query Methods =====

  /**
   * Get activities by type
   */
  async getActivitiesByType(
    schoolId: string,
    activityType: string,
    page: number = 1,
    limit: number = 50
  ): Promise<ActivityListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)
    queryParams.append('page', page.toString())
    queryParams.append('limit', limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/activities/type/${activityType}?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activities by type')
    }

    return response.json()
  }

  /**
   * Get activities by coordinator
   */
  async getActivitiesByCoordinator(
    coordinatorId: string,
    schoolId: string,
    page: number = 1,
    limit: number = 50
  ): Promise<ActivityListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)
    queryParams.append('page', page.toString())
    queryParams.append('limit', limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/activities/coordinator/${coordinatorId}?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activities by coordinator')
    }

    return response.json()
  }

  /**
   * Get featured activities
   */
  async getFeaturedActivities(
    schoolId: string,
    limit: number = 10
  ): Promise<Activity[]> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)
    queryParams.append('limit', limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/activities/featured/list?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch featured activities')
    }

    return response.json()
  }

  /**
   * Search activities
   */
  async searchActivities(
    schoolId: string,
    query: string,
    page: number = 1,
    limit: number = 50
  ): Promise<ActivityListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)
    queryParams.append('q', query)
    queryParams.append('page', page.toString())
    queryParams.append('limit', limit.toString())

    const response = await fetch(
      `${API_BASE}/api/v1/activities/search/query?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to search activities')
    }

    return response.json()
  }

  // ===== Enrollment Methods =====

  /**
   * Enroll a student in an activity
   */
  async enrollStudent(
    activityId: string,
    data: EnrollmentCreateInput,
    createdById: string
  ): Promise<ActivityEnrollment> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}/enroll?created_by_id=${createdById}`,
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
      throw new Error(error.detail || 'Failed to enroll student')
    }

    return response.json()
  }

  /**
   * Withdraw a student from an activity
   */
  async withdrawStudent(
    activityId: string,
    studentId: string,
    data: EnrollmentWithdrawInput,
    withdrawnById: string
  ): Promise<ActivityEnrollment> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}/withdraw/${studentId}?withdrawn_by_id=${withdrawnById}`,
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
      throw new Error(error.detail || 'Failed to withdraw student')
    }

    return response.json()
  }

  /**
   * Get activity roster
   */
  async getActivityRoster(activityId: string): Promise<RosterResponse> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}/roster`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activity roster')
    }

    return response.json()
  }

  /**
   * Get student activities
   */
  async getStudentActivities(
    studentId: string,
    status?: string
  ): Promise<ActivityEnrollment[]> {
    const queryParams = new URLSearchParams()
    if (status) queryParams.append('enrollment_status', status)

    const response = await fetch(
      `${API_BASE}/api/v1/activities/student/${studentId}/enrollments?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch student activities')
    }

    return response.json()
  }

  // ===== Payment Methods =====

  /**
   * Record a payment for an enrollment
   */
  async recordPayment(
    enrollmentId: string,
    data: PaymentRecordInput,
    updatedById: string
  ): Promise<ActivityEnrollment> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/enrollments/${enrollmentId}/payment?updated_by_id=${updatedById}`,
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
      throw new Error(error.detail || 'Failed to record payment')
    }

    return response.json()
  }

  /**
   * Waive payment for an enrollment
   */
  async waivePayment(
    enrollmentId: string,
    updatedById: string
  ): Promise<ActivityEnrollment> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/enrollments/${enrollmentId}/waive-payment?updated_by_id=${updatedById}`,
      {
        method: 'POST'
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to waive payment')
    }

    return response.json()
  }

  /**
   * Get payment summary for an activity
   */
  async getPaymentSummary(activityId: string): Promise<PaymentSummary> {
    const response = await fetch(
      `${API_BASE}/api/v1/activities/${activityId}/payments`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch payment summary')
    }

    return response.json()
  }

  // ===== Statistics Methods =====

  /**
   * Get activity statistics for a school
   */
  async getStatistics(schoolId: string): Promise<ActivityStatistics> {
    const queryParams = new URLSearchParams()
    queryParams.append('school_id', schoolId)

    const response = await fetch(
      `${API_BASE}/api/v1/activities/statistics/summary?${queryParams.toString()}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to fetch activity statistics')
    }

    return response.json()
  }
}

export default new ActivityService()
