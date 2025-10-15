/**
 * School Types
 * TypeScript interfaces for school entities
 */

export type SchoolStatus = 'active' | 'inactive' | 'suspended';

export interface School {
  id: string;
  name: string;
  slug: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country: string;
  phone?: string;
  email?: string;
  website_url?: string;
  facebook_url?: string;
  twitter_url?: string;
  instagram_url?: string;
  logo_url?: string;
  principal_id?: string;
  hod_id?: string;
  timezone: string;
  locale: string;
  status: SchoolStatus;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  is_active?: boolean;
  full_address?: string;
}

export interface SchoolCreate {
  name: string;
  slug?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  facebook_url?: string;
  twitter_url?: string;
  instagram_url?: string;
  logo_url?: string;
  principal_id?: string;
  hod_id?: string;
  timezone?: string;
  locale?: string;
  status?: SchoolStatus;
  settings?: Record<string, any>;
}

export interface SchoolUpdate {
  name?: string;
  slug?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  phone?: string;
  email?: string;
  website_url?: string;
  facebook_url?: string;
  twitter_url?: string;
  instagram_url?: string;
  logo_url?: string;
  principal_id?: string;
  hod_id?: string;
  timezone?: string;
  locale?: string;
}

export interface SchoolSearchParams {
  search?: string;
  status?: SchoolStatus;
  city?: string;
  state?: string;
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface SchoolListResponse {
  data: School[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface SchoolStatistics {
  total: number;
  by_status: Record<string, number>;
  by_state: Record<string, number>;
  active_count: number;
  inactive_count: number;
}

export interface SchoolLeadership {
  principal_id?: string;
  hod_id?: string;
}
