/**
 * Fee Structure Store
 * Pinia store for fee structure state management
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  FeeStructure,
  FeeStructureCreateInput,
  FeeStructureUpdateInput,
  FeeStructureSearchParams,
  FeeStructureStatistics
} from '@/types/feeStructure'

export const useFeeStructureStore = defineStore('feeStructure', () => {
  // State
  const feeStructures = ref<FeeStructure[]>([])
  const selectedFeeStructure = ref<FeeStructure | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const statistics = ref<FeeStructureStatistics | null>(null)

  // Getters
  const totalFeeStructures = computed(() => pagination.value.total)
  const hasFeeStructures = computed(() => feeStructures.value.length > 0)
  const isLoading = computed(() => loading.value)
  const hasError = computed(() => error.value !== null)

  const feeStructuresByGrade = computed(() => {
    return (grade: number) => feeStructures.value.filter(f => f.grade_level === grade)
  })

  const feeStructuresByYear = computed(() => {
    return (year: string) => feeStructures.value.filter(f => f.academic_year === year)
  })

  const activeFeeStructures = computed(() =>
    feeStructures.value.filter(f => f.is_active)
  )

  const inactiveFeeStructures = computed(() =>
    feeStructures.value.filter(f => !f.is_active)
  )

  // Actions
  async function fetchFeeStructures(params: FeeStructureSearchParams) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const response = await feeStructureService.getFeeStructures(params)

      feeStructures.value = response.data
      pagination.value = {
        page: response.page,
        limit: response.limit,
        total: response.total,
        pages: response.pages
      }

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch fee structures'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchFeeStructureById(id: string) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const feeStructure = await feeStructureService.getFeeStructureById(id)

      selectedFeeStructure.value = feeStructure
      return feeStructure
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch fee structure'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchFeeStructureByGradeAndYear(
    schoolId: string,
    gradeLevel: number,
    academicYear: string
  ) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const feeStructure = await feeStructureService.getFeeStructureByGradeAndYear(
        schoolId,
        gradeLevel,
        academicYear
      )

      selectedFeeStructure.value = feeStructure
      return feeStructure
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch fee structure'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchActiveFeeStructures(schoolId: string, params?: { page?: number; limit?: number }) {
    return fetchFeeStructures({
      school_id: schoolId,
      is_active: true,
      ...params
    })
  }

  async function fetchFeeStructuresByYear(schoolId: string, academicYear: string, params?: { page?: number; limit?: number }) {
    return fetchFeeStructures({
      school_id: schoolId,
      academic_year: academicYear,
      ...params
    })
  }

  async function fetchFeeStructuresByGrade(schoolId: string, gradeLevel: number, params?: { page?: number; limit?: number }) {
    return fetchFeeStructures({
      school_id: schoolId,
      grade_level: gradeLevel,
      ...params
    })
  }

  async function createFeeStructure(feeStructureData: FeeStructureCreateInput) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const feeStructure = await feeStructureService.createFeeStructure(feeStructureData)

      // Add to local state
      feeStructures.value.unshift(feeStructure)
      pagination.value.total++

      return feeStructure
    } catch (err: any) {
      error.value = err.message || 'Failed to create fee structure'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateFeeStructure(id: string, feeStructureData: FeeStructureUpdateInput) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const updatedFeeStructure = await feeStructureService.updateFeeStructure(id, feeStructureData)

      // Update in local state
      const index = feeStructures.value.findIndex(f => f.id === id)
      if (index !== -1) {
        feeStructures.value[index] = updatedFeeStructure
      }

      if (selectedFeeStructure.value?.id === id) {
        selectedFeeStructure.value = updatedFeeStructure
      }

      return updatedFeeStructure
    } catch (err: any) {
      error.value = err.message || 'Failed to update fee structure'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteFeeStructure(id: string) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      await feeStructureService.deleteFeeStructure(id)

      // Remove from local state
      feeStructures.value = feeStructures.value.filter(f => f.id !== id)
      pagination.value.total--

      if (selectedFeeStructure.value?.id === id) {
        selectedFeeStructure.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete fee structure'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics(schoolId: string, academicYear?: string) {
    loading.value = true
    error.value = null

    try {
      const { feeStructureService } = await import('@/services/feeStructureService')
      const stats = await feeStructureService.getStatistics(schoolId, academicYear)

      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedFeeStructure(feeStructure: FeeStructure | null) {
    selectedFeeStructure.value = feeStructure
  }

  function clearError() {
    error.value = null
  }

  function resetState() {
    feeStructures.value = []
    selectedFeeStructure.value = null
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
    feeStructures,
    selectedFeeStructure,
    loading,
    error,
    pagination,
    statistics,

    // Getters
    totalFeeStructures,
    hasFeeStructures,
    isLoading,
    hasError,
    feeStructuresByGrade,
    feeStructuresByYear,
    activeFeeStructures,
    inactiveFeeStructures,

    // Actions
    fetchFeeStructures,
    fetchFeeStructureById,
    fetchFeeStructureByGradeAndYear,
    fetchActiveFeeStructures,
    fetchFeeStructuresByYear,
    fetchFeeStructuresByGrade,
    createFeeStructure,
    updateFeeStructure,
    deleteFeeStructure,
    fetchStatistics,
    setSelectedFeeStructure,
    clearError,
    resetState
  }
})
