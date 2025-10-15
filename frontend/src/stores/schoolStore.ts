/**
 * School Store
 * Pinia store for school state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  School,
  SchoolCreate,
  SchoolUpdate,
  SchoolSearchParams,
  SchoolListResponse,
  SchoolStatistics,
  SchoolStatus,
  SchoolLeadership
} from '@/types/school'

export const useSchoolStore = defineStore('school', () => {
  // State
  const schools = ref<School[]>([])
  const selectedSchool = ref<School | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const statistics = ref<SchoolStatistics | null>(null)

  // Getters
  const totalSchools = computed(() => pagination.value.total)
  const hasSchools = computed(() => schools.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const activeSchools = computed(() =>
    schools.value.filter(s => s.status === 'active')
  )

  const inactiveSchools = computed(() =>
    schools.value.filter(s => s.status === 'inactive')
  )

  const suspendedSchools = computed(() =>
    schools.value.filter(s => s.status === 'suspended')
  )

  const schoolsByState = computed(() => {
    const byState: Record<string, School[]> = {}
    schools.value.forEach(school => {
      if (school.state) {
        if (!byState[school.state]) {
          byState[school.state] = []
        }
        byState[school.state].push(school)
      }
    })
    return byState
  })

  // Actions
  async function fetchSchools(params?: SchoolSearchParams): Promise<SchoolListResponse> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const response = await schoolService.listSchools(params)

      schools.value = response.data
      pagination.value = response.pagination

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch schools'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSchoolById(id: string): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const school = await schoolService.getSchool(id)

      selectedSchool.value = school
      return school
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch school'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSchoolBySlug(slug: string): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const school = await schoolService.getSchoolBySlug(slug)

      selectedSchool.value = school
      return school
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch school'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createSchool(schoolData: SchoolCreate): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const school = await schoolService.createSchool(schoolData)

      // Add to local state
      schools.value.unshift(school)
      pagination.value.total++

      return school
    } catch (err: any) {
      error.value = err.message || 'Failed to create school'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateSchool(id: string, schoolData: SchoolUpdate): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const updatedSchool = await schoolService.updateSchool(id, schoolData)

      // Update in local state
      const index = schools.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = updatedSchool
      }

      return updatedSchool
    } catch (err: any) {
      error.value = err.message || 'Failed to update school'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteSchool(id: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      await schoolService.deleteSchool(id)

      // Remove from local state
      schools.value = schools.value.filter(s => s.id !== id)
      pagination.value.total--

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete school'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function changeSchoolStatus(id: string, status: SchoolStatus): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const updatedSchool = await schoolService.changeStatus(id, status)

      // Update in local state
      const index = schools.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = updatedSchool
      }

      return updatedSchool
    } catch (err: any) {
      error.value = err.message || 'Failed to change school status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateSchoolSettings(id: string, settings: Record<string, any>): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const updatedSchool = await schoolService.updateSettings(id, settings)

      // Update in local state
      const index = schools.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = updatedSchool
      }

      return updatedSchool
    } catch (err: any) {
      error.value = err.message || 'Failed to update school settings'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function assignSchoolLeadership(id: string, leadership: SchoolLeadership): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const updatedSchool = await schoolService.assignLeadership(id, leadership)

      // Update in local state
      const index = schools.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = updatedSchool
      }

      return updatedSchool
    } catch (err: any) {
      error.value = err.message || 'Failed to assign school leadership'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function uploadSchoolLogo(id: string, logoUrl: string): Promise<School> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const updatedSchool = await schoolService.uploadLogo(id, logoUrl)

      // Update in local state
      const index = schools.value.findIndex(s => s.id === id)
      if (index !== -1) {
        schools.value[index] = updatedSchool
      }

      if (selectedSchool.value?.id === id) {
        selectedSchool.value = updatedSchool
      }

      return updatedSchool
    } catch (err: any) {
      error.value = err.message || 'Failed to upload school logo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics(): Promise<SchoolStatistics> {
    loading.value = true
    error.value = null

    try {
      const { schoolService } = await import('@/services/schoolService')
      const stats = await schoolService.getStatistics()

      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedSchool(school: School | null) {
    selectedSchool.value = school
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    schools.value = []
    selectedSchool.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    }
    statistics.value = null
  }

  return {
    // State
    schools,
    selectedSchool,
    loading,
    error,
    pagination,
    statistics,

    // Getters
    totalSchools,
    hasSchools,
    isLoading,
    hasError,
    activeSchools,
    inactiveSchools,
    suspendedSchools,
    schoolsByState,

    // Actions
    fetchSchools,
    fetchSchoolById,
    fetchSchoolBySlug,
    createSchool,
    updateSchool,
    deleteSchool,
    changeSchoolStatus,
    updateSchoolSettings,
    assignSchoolLeadership,
    uploadSchoolLogo,
    fetchStatistics,
    setSelectedSchool,
    clearError,
    resetState
  }
})
