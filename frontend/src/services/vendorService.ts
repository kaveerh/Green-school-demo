/**
 * Vendor Service
 * API client for vendor operations
 */

import type {
  Vendor,
  VendorCreateInput,
  VendorUpdateInput,
  VendorListResponse,
  VendorStatistics,
  VendorAlertsResponse,
  VendorFilters,
} from '@/types/vendor'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class VendorService {
  private baseUrl = `${API_BASE_URL}/api/v1/vendors`

  /**
   * Get all vendors with optional filters
   */
  async getVendors(
    schoolId: string,
    filters?: VendorFilters
  ): Promise<VendorListResponse> {
    const params = new URLSearchParams({
      school_id: schoolId,
      page: String(filters?.page || 1),
      limit: String(filters?.limit || 50),
    })

    if (filters?.vendor_type) {
      params.append('vendor_type', filters.vendor_type)
    }
    if (filters?.vendor_status) {
      params.append('vendor_status', filters.vendor_status)
    }

    const response = await fetch(`${this.baseUrl}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch vendors: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get vendor by ID
   */
  async getVendorById(vendorId: string): Promise<Vendor> {
    const response = await fetch(`${this.baseUrl}/${vendorId}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get vendors by type
   */
  async getVendorsByType(
    schoolId: string,
    vendorType: string,
    page: number = 1,
    limit: number = 50
  ): Promise<VendorListResponse> {
    const params = new URLSearchParams({
      school_id: schoolId,
      page: String(page),
      limit: String(limit),
    })

    const response = await fetch(`${this.baseUrl}/type/${vendorType}?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch vendors by type: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Search vendors
   */
  async searchVendors(
    schoolId: string,
    query: string,
    page: number = 1,
    limit: number = 50
  ): Promise<VendorListResponse> {
    const params = new URLSearchParams({
      school_id: schoolId,
      q: query,
      page: String(page),
      limit: String(limit),
    })

    const response = await fetch(`${this.baseUrl}/search/query?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to search vendors: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get preferred vendors
   */
  async getPreferredVendors(
    schoolId: string,
    limit: number = 20
  ): Promise<Vendor[]> {
    const params = new URLSearchParams({
      school_id: schoolId,
      limit: String(limit),
    })

    const response = await fetch(`${this.baseUrl}/preferred/list?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch preferred vendors: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Create vendor
   */
  async createVendor(
    vendorData: VendorCreateInput,
    createdById: string
  ): Promise<Vendor> {
    const params = new URLSearchParams({ created_by_id: createdById })

    const response = await fetch(`${this.baseUrl}?${params}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vendorData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to create vendor: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Update vendor
   */
  async updateVendor(
    vendorId: string,
    vendorData: VendorUpdateInput,
    updatedById: string
  ): Promise<Vendor> {
    const params = new URLSearchParams({ updated_by_id: updatedById })

    const response = await fetch(`${this.baseUrl}/${vendorId}?${params}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(vendorData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to update vendor: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Delete vendor (soft delete)
   */
  async deleteVendor(vendorId: string, deletedById: string): Promise<void> {
    const params = new URLSearchParams({ deleted_by_id: deletedById })

    const response = await fetch(`${this.baseUrl}/${vendorId}?${params}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`Failed to delete vendor: ${response.statusText}`)
    }
  }

  /**
   * Update vendor status
   */
  async updateVendorStatus(
    vendorId: string,
    status: string,
    updatedById: string
  ): Promise<Vendor> {
    const params = new URLSearchParams({ updated_by_id: updatedById })

    const response = await fetch(`${this.baseUrl}/${vendorId}/status?${params}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to update status: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Update vendor rating
   */
  async updateVendorRating(
    vendorId: string,
    rating: number,
    updatedById: string
  ): Promise<Vendor> {
    const params = new URLSearchParams({ updated_by_id: updatedById })

    const response = await fetch(`${this.baseUrl}/${vendorId}/rating?${params}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ rating }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to update rating: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get vendor alerts
   */
  async getVendorAlerts(schoolId: string): Promise<VendorAlertsResponse> {
    const params = new URLSearchParams({ school_id: schoolId })

    const response = await fetch(`${this.baseUrl}/alerts/summary?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor alerts: ${response.statusText}`)
    }
    return response.json()
  }

  /**
   * Get vendor statistics
   */
  async getVendorStatistics(schoolId: string): Promise<VendorStatistics> {
    const params = new URLSearchParams({ school_id: schoolId })

    const response = await fetch(`${this.baseUrl}/statistics/summary?${params}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch vendor statistics: ${response.statusText}`)
    }
    return response.json()
  }
}

export const vendorService = new VendorService()
