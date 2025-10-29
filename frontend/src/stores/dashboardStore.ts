/**
 * Dashboard Store
 * Pinia store for dashboard statistics and summary data
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Dashboard statistics interface
export interface DashboardStatistics {
  students: {
    total: number
    enrolled: number
    byGrade: Record<number, number>
  }
  teachers: {
    total: number
    active: number
  }
  parents: {
    total: number
  }
  classes: {
    total: number
    active: number
  }
  subjects: {
    total: number
  }
  rooms: {
    total: number
  }
  events: {
    total: number
    upcoming: number
  }
  lessons: {
    total: number
    thisWeek: number
  }
  assessments: {
    total: number
    pending: number
    graded: number
  }
  attendance: {
    todayPresent: number
    todayAbsent: number
    todayTotal: number
  }
  activities: {
    total: number
    active: number
  }
  vendors: {
    total: number
  }
  merits: {
    total: number
    thisMonth: number
  }
}

// School interface for selector
export interface School {
  id: string
  name: string
  slug: string
}

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const statistics = ref<DashboardStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastUpdated = ref<Date | null>(null)
  const schools = ref<School[]>([])
  const selectedSchoolId = ref<string | null>(null)
  const loadingSchools = ref(false)

  // Getters
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)
  const hasData = computed(() => statistics.value !== null)
  const selectedSchool = computed(() =>
    schools.value.find(s => s.id === selectedSchoolId.value) || null
  )

  // Quick stats computed properties
  const totalStudents = computed(() => statistics.value?.students.total || 0)
  const totalTeachers = computed(() => statistics.value?.teachers.total || 0)
  const totalClasses = computed(() => statistics.value?.classes.total || 0)
  const upcomingEvents = computed(() => statistics.value?.events.upcoming || 0)
  const totalParents = computed(() => statistics.value?.parents.total || 0)
  const totalSubjects = computed(() => statistics.value?.subjects.total || 0)
  const totalRooms = computed(() => statistics.value?.rooms.total || 0)
  const totalActivities = computed(() => statistics.value?.activities.total || 0)
  const totalVendors = computed(() => statistics.value?.vendors.total || 0)
  const totalMerits = computed(() => statistics.value?.merits.total || 0)
  const pendingAssessments = computed(() => statistics.value?.assessments.pending || 0)
  const todayAttendance = computed(() => statistics.value?.attendance.todayPresent || 0)

  // Actions
  async function fetchAllStatistics(schoolId?: string) {
    loading.value = true
    error.value = null

    try {
      // Use provided schoolId, selected school, environment variable, or default
      const targetSchoolId = schoolId ||
                             selectedSchoolId.value ||
                             import.meta.env.VITE_SCHOOL_ID ||
                             '60da2256-81fc-4ca5-bf6b-467b8d371c61'

      // Import all services dynamically
      const [
        studentServiceModule,
        teacherServiceModule,
        parentServiceModule,
        classServiceModule,
        subjectServiceModule,
        roomServiceModule,
        eventServiceModule,
        lessonServiceModule,
        assessmentServiceModule,
        attendanceServiceModule,
        activityServiceModule,
        vendorServiceModule,
        meritServiceModule
      ] = await Promise.all([
        import('@/services/studentService'),
        import('@/services/teacherService'),
        import('@/services/parentService'),
        import('@/services/classService'),
        import('@/services/subjectService'),
        import('@/services/roomService'),
        import('@/services/eventService'),
        import('@/services/lessonService'),
        import('@/services/assessmentService'),
        import('@/services/attendanceService'),
        import('@/services/activityService'),
        import('@/services/vendorService'),
        import('@/services/meritService')
      ])

      // Handle different export patterns (some use default export, some use named exports)
      const studentService = studentServiceModule.studentService || studentServiceModule.default
      const teacherService = teacherServiceModule.teacherService || teacherServiceModule.default
      const parentService = parentServiceModule.parentService || parentServiceModule.default
      const subjectService = subjectServiceModule.subjectService || subjectServiceModule.default
      const roomService = roomServiceModule.roomService || roomServiceModule.default
      const eventService = eventServiceModule.default || eventServiceModule.eventService
      const lessonService = lessonServiceModule.lessonService || lessonServiceModule.default
      const assessmentService = assessmentServiceModule.assessmentService || assessmentServiceModule.default
      const attendanceService = attendanceServiceModule.default || attendanceServiceModule.attendanceService
      const activityService = activityServiceModule.default || activityServiceModule.activityService
      const vendorService = vendorServiceModule.vendorService || vendorServiceModule.default
      const meritService = meritServiceModule.meritService || meritServiceModule.default

      // Get date range for attendance statistics (last 30 days)
      const today = new Date()
      const thirtyDaysAgo = new Date(today)
      thirtyDaysAgo.setDate(today.getDate() - 30)
      const startDate = thirtyDaysAgo.toISOString().split('T')[0]
      const endDate = today.toISOString().split('T')[0]

      // Fetch all statistics in parallel
      const [
        studentsData,
        teachersData,
        parentsData,
        classesData,
        subjectsData,
        roomsData,
        eventsData,
        lessonsData,
        assessmentsData,
        attendanceData,
        activitiesData,
        vendorsData,
        meritsData
      ] = await Promise.allSettled([
        studentService.getStudents({ school_id: targetSchoolId, limit: 1 }),
        teacherService.getTeachers({ school_id: targetSchoolId, limit: 1 }),
        parentService.getParents({ school_id: targetSchoolId, limit: 1 }),
        classServiceModule.getClasses({ school_id: targetSchoolId, limit: 1 }),
        subjectService.getSubjects({ school_id: targetSchoolId, limit: 1 }),
        roomService.getRooms({ school_id: targetSchoolId, limit: 1 }),
        eventService.getUpcomingEvents({ school_id: targetSchoolId, days_ahead: 30 }),
        lessonService.getLessons(targetSchoolId, { limit: 1 }),
        assessmentService.getStatistics({ school_id: targetSchoolId }),
        attendanceService.getStatistics({ school_id: targetSchoolId, start_date: startDate, end_date: endDate }),
        activityService.getActivities(targetSchoolId, { limit: 1 }),
        vendorService.getVendors(targetSchoolId, { limit: 1 }),
        meritService.getMerits(targetSchoolId, { limit: 1 })
      ])

      // Helper to safely extract pagination total
      // Handles two response structures:
      // 1. { data: [...], pagination: { total, page, limit } } - used by students, teachers
      // 2. { [resource]: [...], total, page, limit } - used by parents, subjects, rooms, events, etc.
      const getTotal = (result: PromiseSettledResult<any>): number => {
        if (result.status === 'fulfilled' && result.value) {
          // Try pagination.total first (structure 1)
          if (result.value.pagination?.total !== undefined) {
            return result.value.pagination.total
          }
          // Try flat total (structure 2)
          if (result.value.total !== undefined) {
            return result.value.total
          }
        }
        return 0
      }

      // Helper to safely extract data array length
      // Handles multiple data array keys: data, events, parents, subjects, etc.
      // Also handles direct arrays (like eventService.getUpcomingEvents returns Event[])
      const getDataLength = (result: PromiseSettledResult<any>): number => {
        if (result.status === 'fulfilled' && result.value) {
          // Check if result.value is directly an array
          if (Array.isArray(result.value)) {
            return result.value.length
          }
          // Try common array keys
          const arrayKeys = ['data', 'events', 'parents', 'subjects', 'rooms', 'activities', 'merits', 'classes', 'lessons']
          for (const key of arrayKeys) {
            if (Array.isArray(result.value[key])) {
              return result.value[key].length
            }
          }
        }
        return 0
      }

      // Helper to extract assessment statistics
      const getAssessmentStats = (result: PromiseSettledResult<any>) => {
        if (result.status === 'fulfilled' && result.value) {
          return {
            total: result.value.total_assessments || 0,
            pending: result.value.pending_assessments || 0,
            graded: result.value.graded_assessments || 0
          }
        }
        return { total: 0, pending: 0, graded: 0 }
      }

      // Helper to extract attendance statistics
      const getAttendanceStats = (result: PromiseSettledResult<any>) => {
        if (result.status === 'fulfilled' && result.value) {
          return {
            todayTotal: result.value.total_records || 0,
            todayPresent: result.value.present_count || 0,
            todayAbsent: result.value.absent_count || 0
          }
        }
        return { todayTotal: 0, todayPresent: 0, todayAbsent: 0 }
      }

      const assessmentStats = getAssessmentStats(assessmentsData)
      const attendanceStats = getAttendanceStats(attendanceData)

      // Build statistics object
      statistics.value = {
        students: {
          total: getTotal(studentsData),
          enrolled: getTotal(studentsData), // Will be filtered from actual enrolled API
          byGrade: {}
        },
        teachers: {
          total: getTotal(teachersData),
          active: getTotal(teachersData)
        },
        parents: {
          total: getTotal(parentsData)
        },
        classes: {
          total: getTotal(classesData),
          active: getTotal(classesData)
        },
        subjects: {
          total: getTotal(subjectsData)
        },
        rooms: {
          total: getTotal(roomsData)
        },
        events: {
          total: getDataLength(eventsData), // getUpcomingEvents returns Event[] directly
          upcoming: getDataLength(eventsData) // Actual upcoming events
        },
        lessons: {
          total: getTotal(lessonsData),
          thisWeek: 0 // Can be calculated from actual data if needed
        },
        assessments: {
          total: assessmentStats.total,
          pending: assessmentStats.pending,
          graded: assessmentStats.graded
        },
        attendance: {
          todayPresent: attendanceStats.todayPresent,
          todayAbsent: attendanceStats.todayAbsent,
          todayTotal: attendanceStats.todayTotal
        },
        activities: {
          total: getTotal(activitiesData),
          active: getTotal(activitiesData)
        },
        vendors: {
          total: getTotal(vendorsData)
        },
        merits: {
          total: getTotal(meritsData),
          thisMonth: 0 // Can be calculated from actual data if needed
        }
      }

      lastUpdated.value = new Date()
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch dashboard statistics'
      console.error('Dashboard statistics error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSchools() {
    loadingSchools.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const response = await schoolService.listSchools({ limit: 100 })

      schools.value = response.data.map((school: any) => ({
        id: school.id,
        name: school.name,
        slug: school.slug
      }))

      // Load selected school from localStorage or use first school
      const savedSchoolId = localStorage.getItem('selectedSchoolId')
      if (savedSchoolId && schools.value.some(s => s.id === savedSchoolId)) {
        selectedSchoolId.value = savedSchoolId
      } else if (schools.value.length > 0) {
        selectedSchoolId.value = schools.value[0].id
        localStorage.setItem('selectedSchoolId', schools.value[0].id)
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch schools'
      console.error('Failed to fetch schools:', err)
    } finally {
      loadingSchools.value = false
    }
  }

  function selectSchool(schoolId: string) {
    selectedSchoolId.value = schoolId
    localStorage.setItem('selectedSchoolId', schoolId)
    // Automatically fetch statistics for the new school
    fetchAllStatistics(schoolId)
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    statistics.value = null
    loading.value = false
    error.value = null
    lastUpdated.value = null
    schools.value = []
    selectedSchoolId.value = null
    loadingSchools.value = false
  }

  return {
    // State
    statistics,
    loading,
    error,
    lastUpdated,
    schools,
    selectedSchoolId,
    loadingSchools,

    // Getters
    isLoading,
    hasError,
    hasData,
    selectedSchool,
    totalStudents,
    totalTeachers,
    totalClasses,
    upcomingEvents,
    totalParents,
    totalSubjects,
    totalRooms,
    totalActivities,
    totalVendors,
    totalMerits,
    pendingAssessments,
    todayAttendance,

    // Actions
    fetchAllStatistics,
    fetchSchools,
    selectSchool,
    clearError,
    resetState
  }
})
