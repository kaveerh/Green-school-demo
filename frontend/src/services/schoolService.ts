/**
 * School Service
 * API service for school operations
 */
import type {
  School,
  SchoolCreate,
  SchoolUpdate,
  SchoolSearchParams,
  SchoolListResponse,
  SchoolStatistics,
  SchoolLeadership,
  SchoolStatus
} from '@/types/school';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class SchoolService {
  /**
   * List schools with filtering and pagination
   */
  async listSchools(params?: SchoolSearchParams): Promise<SchoolListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.search) queryParams.append('search', params.search);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.city) queryParams.append('city', params.city);
    if (params?.state) queryParams.append('state', params.state);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.sort) queryParams.append('sort', params.sort);
    if (params?.order) queryParams.append('order', params.order);

    const response = await fetch(
      `${API_BASE_URL}/schools?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch schools');
    }

    return response.json();
  }

  /**
   * Get a school by ID
   */
  async getSchool(id: string): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch school');
    }

    return response.json();
  }

  /**
   * Get a school by slug
   */
  async getSchoolBySlug(slug: string): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/slug/${slug}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch school');
    }

    return response.json();
  }

  /**
   * Create a new school
   */
  async createSchool(data: SchoolCreate): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create school');
    }

    return response.json();
  }

  /**
   * Update a school
   */
  async updateSchool(id: string, data: SchoolUpdate): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update school');
    }

    return response.json();
  }

  /**
   * Delete a school (soft delete)
   */
  async deleteSchool(id: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}`,
      {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete school');
    }
  }

  /**
   * Change school status
   */
  async changeStatus(id: string, status: SchoolStatus): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}/status`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to change school status');
    }

    return response.json();
  }

  /**
   * Update school settings
   */
  async updateSettings(id: string, settings: Record<string, any>): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}/settings`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ settings }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update school settings');
    }

    return response.json();
  }

  /**
   * Assign school leadership (principal/HOD)
   */
  async assignLeadership(id: string, data: SchoolLeadership): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}/leadership`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to assign school leadership');
    }

    return response.json();
  }

  /**
   * Upload school logo
   */
  async uploadLogo(id: string, logoUrl: string): Promise<School> {
    const response = await fetch(
      `${API_BASE_URL}/schools/${id}/logo`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ logo_url: logoUrl }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload school logo');
    }

    return response.json();
  }

  /**
   * Get school statistics
   */
  async getStatistics(): Promise<SchoolStatistics> {
    const response = await fetch(
      `${API_BASE_URL}/schools/statistics/summary`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch school statistics');
    }

    return response.json();
  }
}

export const schoolService = new SchoolService();
export default schoolService;
