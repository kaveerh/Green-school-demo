/**
 * Vendor Store
 * Pinia store for managing vendor state
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { vendorService } from '@/services/vendorService'
import type {
  Vendor,
  VendorCreateInput,
  VendorUpdateInput,
  VendorFilters,
  VendorStatistics,
  VendorAlertsResponse,
} from '@/types/vendor'

export const useVendorStore = defineStore('vendor', () => {
  // State
  const vendors = ref<Vendor[]>([])
  const selectedVendor = ref<Vendor | null>(null)
  const preferredVendors = ref<Vendor[]>([])
  const statistics = ref<VendorStatistics | null>(null)
  const alerts = ref<VendorAlertsResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Pagination
  const currentPage = ref(1)
  const totalPages = ref(1)
  const totalVendors = ref(0)
  const pageLimit = ref(50)

  // Filters
  const filters = ref<VendorFilters>({})

  // Computed
  const activeVendors = computed(() =>
    vendors.value.filter((v) => v.is_active)
  )

  const vendorsByType = computed(() => {
    const grouped: Record<string, Vendor[]> = {}
    vendors.value.forEach((vendor) => {
      if (!grouped[vendor.vendor_type]) {
        grouped[vendor.vendor_type] = []
      }
      grouped[vendor.vendor_type].push(vendor)
    })
    return grouped
  })

  const hasExpiringContracts = computed(() =>
    vendors.value.some((v) => v.contract_expiring_soon)
  )

  const hasExpiredInsurance = computed(() =>
    vendors.value.some((v) => v.insurance_expired)
  )

  // Actions
  async function fetchVendors(schoolId: string, filterOptions?: VendorFilters) {
    loading.value = true
    error.value = null

    try {
      const response = await vendorService.getVendors(schoolId, {
        ...filterOptions,
        page: currentPage.value,
        limit: pageLimit.value,
      })

      vendors.value = response.vendors
      totalPages.value = response.pages
      totalVendors.value = response.total
      currentPage.value = response.page

      if (filterOptions) {
        filters.value = filterOptions
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch vendors'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchVendorById(vendorId: string) {
    loading.value = true
    error.value = null

    try {
      const vendor = await vendorService.getVendorById(vendorId)
      selectedVendor.value = vendor
      return vendor
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch vendor'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPreferredVendors(schoolId: string, limit: number = 20) {
    loading.value = true
    error.value = null

    try {
      preferredVendors.value = await vendorService.getPreferredVendors(schoolId, limit)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch preferred vendors'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchVendors(schoolId: string, query: string) {
    loading.value = true
    error.value = null

    try {
      const response = await vendorService.searchVendors(
        schoolId,
        query,
        currentPage.value,
        pageLimit.value
      )

      vendors.value = response.vendors
      totalPages.value = response.pages
      totalVendors.value = response.total
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to search vendors'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createVendor(
    vendorData: VendorCreateInput,
    createdById: string
  ): Promise<Vendor> {
    loading.value = true
    error.value = null

    try {
      const vendor = await vendorService.createVendor(vendorData, createdById)
      vendors.value.unshift(vendor)
      totalVendors.value++
      return vendor
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create vendor'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateVendor(
    vendorId: string,
    vendorData: VendorUpdateInput,
    updatedById: string
  ): Promise<Vendor> {
    loading.value = true
    error.value = null

    try {
      const updatedVendor = await vendorService.updateVendor(
        vendorId,
        vendorData,
        updatedById
      )

      const index = vendors.value.findIndex((v) => v.id === vendorId)
      if (index !== -1) {
        vendors.value[index] = updatedVendor
      }

      if (selectedVendor.value?.id === vendorId) {
        selectedVendor.value = updatedVendor
      }

      return updatedVendor
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update vendor'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteVendor(vendorId: string, deletedById: string) {
    loading.value = true
    error.value = null

    try {
      await vendorService.deleteVendor(vendorId, deletedById)
      vendors.value = vendors.value.filter((v) => v.id !== vendorId)
      totalVendors.value--

      if (selectedVendor.value?.id === vendorId) {
        selectedVendor.value = null
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete vendor'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateVendorStatus(
    vendorId: string,
    status: string,
    updatedById: string
  ): Promise<Vendor> {
    loading.value = true
    error.value = null

    try {
      const updatedVendor = await vendorService.updateVendorStatus(
        vendorId,
        status,
        updatedById
      )

      const index = vendors.value.findIndex((v) => v.id === vendorId)
      if (index !== -1) {
        vendors.value[index] = updatedVendor
      }

      if (selectedVendor.value?.id === vendorId) {
        selectedVendor.value = updatedVendor
      }

      return updatedVendor
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update vendor status'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateVendorRating(
    vendorId: string,
    rating: number,
    updatedById: string
  ): Promise<Vendor> {
    loading.value = true
    error.value = null

    try {
      const updatedVendor = await vendorService.updateVendorRating(
        vendorId,
        rating,
        updatedById
      )

      const index = vendors.value.findIndex((v) => v.id === vendorId)
      if (index !== -1) {
        vendors.value[index] = updatedVendor
      }

      if (selectedVendor.value?.id === vendorId) {
        selectedVendor.value = updatedVendor
      }

      return updatedVendor
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update vendor rating'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatistics(schoolId: string) {
    loading.value = true
    error.value = null

    try {
      statistics.value = await vendorService.getVendorStatistics(schoolId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch statistics'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAlerts(schoolId: string) {
    loading.value = true
    error.value = null

    try {
      alerts.value = await vendorService.getVendorAlerts(schoolId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch alerts'
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

  function clearSelectedVendor() {
    selectedVendor.value = null
  }

  return {
    // State
    vendors,
    selectedVendor,
    preferredVendors,
    statistics,
    alerts,
    loading,
    error,
    currentPage,
    totalPages,
    totalVendors,
    pageLimit,
    filters,

    // Computed
    activeVendors,
    vendorsByType,
    hasExpiringContracts,
    hasExpiredInsurance,

    // Actions
    fetchVendors,
    fetchVendorById,
    fetchPreferredVendors,
    searchVendors,
    createVendor,
    updateVendor,
    deleteVendor,
    updateVendorStatus,
    updateVendorRating,
    fetchStatistics,
    fetchAlerts,
    setPage,
    setPageLimit,
    clearFilters,
    clearError,
    clearSelectedVendor,
  }
})
