/**
 * Parent Store
 *
 * Pinia store for managing parent state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { parentService } from '@/services/parentService'
import type {
  Parent,
  ParentCreateInput,
  ParentUpdateInput,
  ParentSearchParams,
  ParentStudentLinkInput,
  ParentStatistics
} from '@/types/parent'
import type { Student } from '@/types/student'

export const useParentStore = defineStore('parent', () => {
  // State
  const parents = ref<Parent[]>([])
  const selectedParent = ref<Parent | null>(null)
  const statistics = ref<ParentStatistics | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalParents = ref(0)
  const pageSize = ref(50)

  // Computed
  const totalPages = computed(() => Math.ceil(totalParents.value / pageSize.value))

  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  const hasPreviousPage = computed(() => currentPage.value > 1)

  // Actions

  /**
   * Fetch all parents
   */
  async function fetchParents(params: ParentSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await parentService.getParents({
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      parents.value = response.parents
      totalParents.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch parents'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch parent by ID
   */
  async function fetchParentById(id: string) {
    isLoading.value = true
    error.value = null

    try {
      const parent = await parentService.getParentById(id)
      selectedParent.value = parent
      return parent
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch parent'
      selectedParent.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create new parent
   */
  async function createParent(parentData: ParentCreateInput) {
    isLoading.value = true
    error.value = null

    try {
      const newParent = await parentService.createParent(parentData)

      // Add to list
      parents.value.unshift(newParent)
      totalParents.value++

      return newParent
    } catch (err: any) {
      error.value = err.message || 'Failed to create parent'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update parent
   */
  async function updateParent(id: string, parentData: ParentUpdateInput) {
    isLoading.value = true
    error.value = null

    try {
      const updatedParent = await parentService.updateParent(id, parentData)

      // Update in list
      const index = parents.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        parents.value[index] = updatedParent
      }

      // Update selected if it's the same
      if (selectedParent.value?.id === id) {
        selectedParent.value = updatedParent
      }

      return updatedParent
    } catch (err: any) {
      error.value = err.message || 'Failed to update parent'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete parent
   */
  async function deleteParent(id: string) {
    isLoading.value = true
    error.value = null

    try {
      await parentService.deleteParent(id)

      // Remove from list
      parents.value = parents.value.filter((p) => p.id !== id)
      totalParents.value--

      // Clear selected if it's the same
      if (selectedParent.value?.id === id) {
        selectedParent.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to delete parent'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Link parent to student
   */
  async function linkStudent(parentId: string, linkData: ParentStudentLinkInput) {
    isLoading.value = true
    error.value = null

    try {
      const relationship = await parentService.linkStudent(parentId, linkData)

      // Refresh parent data to get updated children
      if (selectedParent.value?.id === parentId) {
        await fetchParentById(parentId)
      }

      return relationship
    } catch (err: any) {
      error.value = err.message || 'Failed to link student'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Unlink parent from student
   */
  async function unlinkStudent(parentId: string, studentId: string) {
    isLoading.value = true
    error.value = null

    try {
      await parentService.unlinkStudent(parentId, studentId)

      // Refresh parent data to get updated children
      if (selectedParent.value?.id === parentId) {
        await fetchParentById(parentId)
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Failed to unlink student'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get parent's children
   */
  async function fetchParentChildren(parentId: string): Promise<Student[]> {
    isLoading.value = true
    error.value = null

    try {
      const children = await parentService.getParentChildren(parentId)
      return children
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch children'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Search parents
   */
  async function searchParents(query: string, params: ParentSearchParams = {}) {
    isLoading.value = true
    error.value = null

    try {
      const response = await parentService.searchParents(query, {
        ...params,
        page: params.page || currentPage.value,
        limit: params.limit || pageSize.value,
      })

      parents.value = response.parents
      totalParents.value = response.total
      currentPage.value = response.page

      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to search parents'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Get student's parents
   */
  async function fetchStudentParents(studentId: string): Promise<Parent[]> {
    isLoading.value = true
    error.value = null

    try {
      const studentParents = await parentService.getStudentParents(studentId)
      return studentParents
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch student parents'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch statistics
   */
  async function fetchStatistics(schoolId?: string) {
    isLoading.value = true
    error.value = null

    try {
      const stats = await parentService.getStatistics(schoolId)
      statistics.value = stats
      return stats
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch statistics'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Go to next page
   */
  async function nextPage() {
    if (hasNextPage.value) {
      currentPage.value++
      await fetchParents()
    }
  }

  /**
   * Go to previous page
   */
  async function previousPage() {
    if (hasPreviousPage.value) {
      currentPage.value--
      await fetchParents()
    }
  }

  /**
   * Go to specific page
   */
  async function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
      await fetchParents()
    }
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null
  }

  /**
   * Clear selected parent
   */
  function clearSelected() {
    selectedParent.value = null
  }

  /**
   * Reset store
   */
  function $reset() {
    parents.value = []
    selectedParent.value = null
    statistics.value = null
    isLoading.value = false
    error.value = null
    currentPage.value = 1
    totalParents.value = 0
    pageSize.value = 50
  }

  return {
    // State
    parents,
    selectedParent,
    statistics,
    isLoading,
    error,
    currentPage,
    totalParents,
    pageSize,

    // Computed
    totalPages,
    hasNextPage,
    hasPreviousPage,

    // Actions
    fetchParents,
    fetchParentById,
    createParent,
    updateParent,
    deleteParent,
    linkStudent,
    unlinkStudent,
    fetchParentChildren,
    searchParents,
    fetchStudentParents,
    fetchStatistics,
    nextPage,
    previousPage,
    goToPage,
    clearError,
    clearSelected,
    $reset,
  }
})
