/**
 * Lesson Store
 *
 * Pinia store for lesson planning state management
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Lesson,
  LessonCreateRequest,
  LessonUpdateRequest,
  LessonCompleteRequest,
  LessonFromTemplateRequest,
  LessonDuplicateRequest,
  LessonStatistics,
  LessonFilters,
  LessonSearchParams,
  LessonDateRangeParams,
  LessonUpcomingParams,
  LessonTemplateParams,
  LessonStatisticsParams
} from '@/types/lesson'
import { lessonService } from '@/services/lessonService'

export const useLessonStore = defineStore('lesson', () => {
  // State
  const lessons = ref<Lesson[]>([])
  const currentLesson = ref<Lesson | null>(null)
  const templates = ref<Lesson[]>([])
  const upcomingLessons = ref<Lesson[]>([])
  const pastDueLessons = ref<Lesson[]>([])
  const statistics = ref<LessonStatistics | null>(null)

  const total = ref(0)
  const currentPage = ref(1)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasLessons = computed(() => lessons.value.length > 0)
  const hasTemplates = computed(() => templates.value.length > 0)
  const hasUpcoming = computed(() => upcomingLessons.value.length > 0)
  const hasPastDue = computed(() => pastDueLessons.value.length > 0)

  // Actions
  async function fetchLessons(schoolId: string, filters?: LessonFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await lessonService.getLessons(schoolId, filters)
      lessons.value = response.lessons
      total.value = response.total
      currentPage.value = response.page
      totalPages.value = response.pages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch lessons'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLessonsByDateRange(schoolId: string, params: LessonDateRangeParams) {
    loading.value = true
    error.value = null

    try {
      lessons.value = await lessonService.getLessonsByDateRange(schoolId, params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch lessons'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchUpcomingLessons(schoolId: string, params?: LessonUpcomingParams) {
    loading.value = true
    error.value = null

    try {
      upcomingLessons.value = await lessonService.getUpcomingLessons(schoolId, params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch upcoming lessons'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPastDueLessons(schoolId: string, teacherId?: string, limit = 50) {
    loading.value = true
    error.value = null

    try {
      pastDueLessons.value = await lessonService.getPastDueLessons(schoolId, teacherId, limit)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch past due lessons'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchLessons(schoolId: string, params: LessonSearchParams) {
    loading.value = true
    error.value = null

    try {
      lessons.value = await lessonService.searchLessons(schoolId, params)
      total.value = lessons.value.length
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search lessons'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplates(schoolId: string, params?: LessonTemplateParams) {
    loading.value = true
    error.value = null

    try {
      templates.value = await lessonService.getTemplates(schoolId, params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch templates'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics(schoolId: string, params?: LessonStatisticsParams) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await lessonService.getStatistics(schoolId, params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLessonById(id: string) {
    loading.value = true
    error.value = null

    try {
      currentLesson.value = await lessonService.getLessonById(id)
      return currentLesson.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createLesson(schoolId: string, data: LessonCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const newLesson = await lessonService.createLesson(schoolId, data)
      lessons.value.unshift(newLesson)
      total.value++
      return newLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createFromTemplate(schoolId: string, data: LessonFromTemplateRequest) {
    loading.value = true
    error.value = null

    try {
      const newLesson = await lessonService.createFromTemplate(schoolId, data)
      lessons.value.unshift(newLesson)
      total.value++
      return newLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create lesson from template'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateLesson(id: string, data: LessonUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updatedLesson = await lessonService.updateLesson(id, data)

      // Update in list
      const index = lessons.value.findIndex((l) => l.id === id)
      if (index !== -1) {
        lessons.value[index] = updatedLesson
      }

      // Update current if it's the same
      if (currentLesson.value?.id === id) {
        currentLesson.value = updatedLesson
      }

      return updatedLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(id: string, status: string) {
    loading.value = true
    error.value = null

    try {
      const updatedLesson = await lessonService.updateStatus(id, status)

      // Update in list
      const index = lessons.value.findIndex((l) => l.id === id)
      if (index !== -1) {
        lessons.value[index] = updatedLesson
      }

      // Update current if it's the same
      if (currentLesson.value?.id === id) {
        currentLesson.value = updatedLesson
      }

      return updatedLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function startLesson(id: string) {
    return updateStatus(id, 'in_progress')
  }

  async function completeLesson(id: string, data: LessonCompleteRequest) {
    loading.value = true
    error.value = null

    try {
      const updatedLesson = await lessonService.completeLesson(id, data)

      // Update in list
      const index = lessons.value.findIndex((l) => l.id === id)
      if (index !== -1) {
        lessons.value[index] = updatedLesson
      }

      // Update current if it's the same
      if (currentLesson.value?.id === id) {
        currentLesson.value = updatedLesson
      }

      return updatedLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to complete lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function cancelLesson(id: string) {
    return updateStatus(id, 'cancelled')
  }

  async function convertToTemplate(id: string) {
    loading.value = true
    error.value = null

    try {
      const updatedLesson = await lessonService.convertToTemplate(id)

      // Update in list
      const index = lessons.value.findIndex((l) => l.id === id)
      if (index !== -1) {
        lessons.value[index] = updatedLesson
      }

      // Add to templates
      templates.value.push(updatedLesson)

      return updatedLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to convert to template'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function duplicateLesson(id: string, data: LessonDuplicateRequest) {
    loading.value = true
    error.value = null

    try {
      const newLesson = await lessonService.duplicateLesson(id, data)
      lessons.value.unshift(newLesson)
      total.value++
      return newLesson
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to duplicate lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteLesson(id: string) {
    loading.value = true
    error.value = null

    try {
      await lessonService.deleteLesson(id)

      // Remove from list
      lessons.value = lessons.value.filter((l) => l.id !== id)
      total.value--

      // Clear current if it's the same
      if (currentLesson.value?.id === id) {
        currentLesson.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete lesson'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrent() {
    currentLesson.value = null
  }

  function reset() {
    lessons.value = []
    currentLesson.value = null
    templates.value = []
    upcomingLessons.value = []
    pastDueLessons.value = []
    statistics.value = null
    total.value = 0
    currentPage.value = 1
    totalPages.value = 0
    loading.value = false
    error.value = null
  }

  return {
    // State
    lessons,
    currentLesson,
    templates,
    upcomingLessons,
    pastDueLessons,
    statistics,
    total,
    currentPage,
    totalPages,
    loading,
    error,

    // Computed
    hasLessons,
    hasTemplates,
    hasUpcoming,
    hasPastDue,

    // Actions
    fetchLessons,
    fetchLessonsByDateRange,
    fetchUpcomingLessons,
    fetchPastDueLessons,
    searchLessons,
    fetchTemplates,
    fetchStatistics,
    fetchLessonById,
    createLesson,
    createFromTemplate,
    updateLesson,
    updateStatus,
    startLesson,
    completeLesson,
    cancelLesson,
    convertToTemplate,
    duplicateLesson,
    deleteLesson,
    clearError,
    clearCurrent,
    reset
  }
})
