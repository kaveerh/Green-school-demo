/**
 * Merit Store
 * Pinia store for managing merit state
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { meritService } from '@/services/meritService'
import type {
  Merit,
  MeritCreateInput,
  MeritBatchCreateInput,
  MeritUpdateInput,
  MeritFilters,
  MeritSummary,
  ClassMeritSummary,
  LeaderboardEntry,
  MeritStatistics,
} from '@/types/merit'

export const useMeritStore = defineStore('merit', () => {
  // State
  const merits = ref<Merit[]>([])
  const selectedMerit = ref<Merit | null>(null)
  const studentSummary = ref<MeritSummary | null>(null)
  const classSummary = ref<ClassMeritSummary | null>(null)
  const leaderboard = ref<LeaderboardEntry[]>([])
  const statistics = ref<MeritStatistics | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalMerits = ref(0)
  const pageLimit = ref(50)

  // Filters
  const filters = ref<MeritFilters>({})

  // Computed
  const meritsByCategory = computed(() => {
    const grouped: Record<string, Merit[]> = {}
    merits.value.forEach((merit) => {
      if (!grouped[merit.category]) {
        grouped[merit.category] = []
      }
      grouped[merit.category].push(merit)
    })
    return grouped
  })

  const recentMerits = computed(() =>
    merits.value.filter((m) => m.is_recent).slice(0, 10)
  )

  const totalPoints = computed(() =>
    merits.value.reduce((sum, m) => sum + m.points, 0)
  )

  // Actions
  async function fetchMerits(schoolId: string, filterOptions?: MeritFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await meritService.getMerits(schoolId, {
        ...filterOptions,
        page: currentPage.value,
        limit: pageLimit.value,
      })

      merits.value = response.merits
      totalPages.value = response.pages
      totalMerits.value = response.total
      currentPage.value = response.page

      if (filterOptions) {
        filters.value = filterOptions
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch merits'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchMeritById(meritId: string) {
    loading.value = true
    error.value = null

    try {
      const merit = await meritService.getMeritById(meritId)
      selectedMerit.value = merit
      return merit
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch merit'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentMerits(
    studentId: string,
    filterOptions?: { category?: string; quarter?: string }
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await meritService.getStudentMerits(studentId, {
        ...filterOptions,
        page: currentPage.value,
        limit: pageLimit.value,
      })

      merits.value = response.merits
      totalPages.value = response.pages
      totalMerits.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch student merits'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStudentSummary(studentId: string) {
    loading.value = true
    error.value = null

    try {
      studentSummary.value = await meritService.getStudentSummary(studentId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch student summary'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchClassMerits(
    classId: string,
    filterOptions?: { quarter?: string; category?: string }
  ) {
    loading.value = true
    error.value = null

    try {
      const response = await meritService.getClassMerits(classId, {
        ...filterOptions,
        page: currentPage.value,
        limit: pageLimit.value,
      })

      merits.value = response.merits
      totalPages.value = response.pages
      totalMerits.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch class merits'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchClassSummary(classId: string, quarter?: string) {
    loading.value = true
    error.value = null

    try {
      classSummary.value = await meritService.getClassSummary(classId, quarter)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch class summary'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLeaderboard(
    schoolId: string,
    gradeLevel?: number,
    quarter?: string,
    limit: number = 20
  ) {
    loading.value = true
    error.value = null

    try {
      leaderboard.value = await meritService.getLeaderboard(schoolId, gradeLevel, quarter, limit)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch leaderboard'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics(schoolId: string, quarter?: string, gradeLevel?: number) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await meritService.getStatistics(schoolId, quarter, gradeLevel)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function awardMerit(
    meritData: MeritCreateInput,
    awardedById: string
  ): Promise<Merit> {
    loading.value = true
    error.value = null

    try {
      const merit = await meritService.awardMerit(meritData, awardedById)
      merits.value.unshift(merit)
      totalMerits.value++
      return merit
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to award merit'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function awardBatchMerits(
    meritData: MeritBatchCreateInput,
    awardedById: string
  ): Promise<Merit[]> {
    loading.value = true
    error.value = null

    try {
      const newMerits = await meritService.awardBatchMerits(meritData, awardedById)
      merits.value.unshift(...newMerits)
      totalMerits.value += newMerits.length
      return newMerits
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to award batch merits'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateMerit(
    meritId: string,
    meritData: MeritUpdateInput,
    updatedById: string
  ): Promise<Merit> {
    loading.value = true
    error.value = null

    try {
      const updatedMerit = await meritService.updateMerit(meritId, meritData, updatedById)

      const index = merits.value.findIndex((m) => m.id === meritId)
      if (index !== -1) {
        merits.value[index] = updatedMerit
      }

      if (selectedMerit.value?.id === meritId) {
        selectedMerit.value = updatedMerit
      }

      return updatedMerit
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update merit'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function revokeMerit(meritId: string, deletedById: string) {
    loading.value = true
    error.value = null

    try {
      await meritService.revokeMerit(meritId, deletedById)
      merits.value = merits.value.filter((m) => m.id !== meritId)
      totalMerits.value--

      if (selectedMerit.value?.id === meritId) {
        selectedMerit.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to revoke merit'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setPage(page: number) {
    currentPage.value = page
  }

  function setPageLimit(limit: number) {
    pageLimit.value = limit
  }

  function clearFilters() {
    filters.value = {}
    currentPage.value = 1
  }

  function clearError() {
    error.value = null
  }

  function clearSelectedMerit() {
    selectedMerit.value = null
  }

  return {
    // State
    merits,
    selectedMerit,
    studentSummary,
    classSummary,
    leaderboard,
    statistics,
    loading,
    error,
    currentPage,
    totalPages,
    totalMerits,
    pageLimit,
    filters,

    // Computed
    meritsByCategory,
    recentMerits,
    totalPoints,

    // Actions
    fetchMerits,
    fetchMeritById,
    fetchStudentMerits,
    fetchStudentSummary,
    fetchClassMerits,
    fetchClassSummary,
    fetchLeaderboard,
    fetchStatistics,
    awardMerit,
    awardBatchMerits,
    updateMerit,
    revokeMerit,
    setPage,
    setPageLimit,
    clearFilters,
    clearError,
    clearSelectedMerit,
  }
})
