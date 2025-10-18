/**
 * Subject Types
 *
 * TypeScript type definitions for Subject management.
 */

// Subject Category
export type SubjectCategory = 'core' | 'elective' | 'enrichment' | 'remedial' | 'other'

// Subject Type
export type SubjectType = 'academic' | 'arts' | 'physical' | 'technical' | 'other'

// Subject Interface
export interface Subject {
  id: string
  school_id: string
  code: string
  name: string
  description?: string
  category: SubjectCategory
  subject_type?: SubjectType
  grade_levels: number[]
  color?: string
  icon?: string
  display_order: number
  credits?: number
  is_required: boolean
  is_active: boolean
  created_at: string
  updated_at: string
  deleted_at?: string

  // Computed fields
  is_available?: boolean
  is_core?: boolean
  grade_range?: string
}

// Subject Create Input
export interface SubjectCreateInput {
  school_id: string
  code: string
  name: string
  description?: string
  category: SubjectCategory
  subject_type?: SubjectType
  grade_levels: number[]
  color?: string
  icon?: string
  display_order?: number
  credits?: number
  is_required?: boolean
  is_active?: boolean
}

// Subject Update Input
export interface SubjectUpdateInput {
  name?: string
  description?: string
  category?: SubjectCategory
  subject_type?: SubjectType
  grade_levels?: number[]
  color?: string
  icon?: string
  display_order?: number
  credits?: number
  is_required?: boolean
  is_active?: boolean
}

// Subject Search Parameters
export interface SubjectSearchParams {
  school_id?: string
  category?: SubjectCategory
  subject_type?: SubjectType
  is_active?: boolean
  is_required?: boolean
  page?: number
  limit?: number
}

// Subject List Response
export interface SubjectListResponse {
  subjects: Subject[]
  total: number
  page: number
  limit: number
}

// Subject Statistics
export interface SubjectStatistics {
  total_subjects: number
  active_subjects: number
  inactive_subjects: number
  by_category: Record<string, number>
  by_type: Record<string, number>
  required_subjects: number
  elective_subjects: number
}

/**
 * Get label for subject category
 */
export function getSubjectCategoryLabel(category: SubjectCategory): string {
  const labels: Record<SubjectCategory, string> = {
    core: 'Core',
    elective: 'Elective',
    enrichment: 'Enrichment',
    remedial: 'Remedial',
    other: 'Other'
  }
  return labels[category] || category
}

/**
 * Get label for subject type
 */
export function getSubjectTypeLabel(type: SubjectType): string {
  const labels: Record<SubjectType, string> = {
    academic: 'Academic',
    arts: 'Arts',
    physical: 'Physical Education',
    technical: 'Technical',
    other: 'Other'
  }
  return labels[type] || type
}

/**
 * Format grade levels array into readable string
 */
export function formatGradeLevels(grades: number[]): string {
  if (!grades || grades.length === 0) {
    return ''
  }

  const sorted = [...grades].sort((a, b) => a - b)

  if (sorted.length === 1) {
    return `Grade ${sorted[0]}`
  }

  // Check if consecutive
  const isConsecutive = sorted.every((grade, index) => {
    if (index === 0) return true
    return grade === sorted[index - 1] + 1
  })

  if (isConsecutive) {
    return `Grades ${sorted[0]}-${sorted[sorted.length - 1]}`
  }

  // Non-consecutive
  return `Grades ${sorted.join(', ')}`
}

/**
 * Get color for subject category (for UI badges)
 */
export function getCategoryColor(category: SubjectCategory): string {
  const colors: Record<SubjectCategory, string> = {
    core: '#4CAF50',
    elective: '#2196F3',
    enrichment: '#FF9800',
    remedial: '#9C27B0',
    other: '#757575'
  }
  return colors[category] || '#757575'
}

/**
 * Validate hex color format
 */
export function isValidHexColor(color: string): boolean {
  return /^#[0-9A-Fa-f]{6}$/.test(color)
}

/**
 * Get default icon for subject code
 */
export function getDefaultIcon(code: string): string {
  const icons: Record<string, string> = {
    MATH: '🔢',
    ELA: '📚',
    SCIENCE: '🔬',
    SOCIAL_STUDIES: '🌍',
    ART: '🎨',
    PE: '⚽',
    MUSIC: '🎵',
    LIBRARY: '📖',
    TECHNOLOGY: '💻',
    FOREIGN_LANGUAGE: '🌐',
    DRAMA: '🎭',
    HEALTH: '🏥',
    STEM: '🔧',
    HOMEROOM: '🏠'
  }
  return icons[code.toUpperCase()] || '📝'
}

/**
 * Get default color for subject code
 */
export function getDefaultColor(code: string): string {
  const colors: Record<string, string> = {
    MATH: '#2196F3',
    ELA: '#4CAF50',
    SCIENCE: '#9C27B0',
    SOCIAL_STUDIES: '#FF9800',
    ART: '#E91E63',
    PE: '#F44336',
    MUSIC: '#673AB7',
    LIBRARY: '#795548',
    TECHNOLOGY: '#00BCD4',
    FOREIGN_LANGUAGE: '#009688',
    DRAMA: '#FF5722',
    HEALTH: '#8BC34A',
    STEM: '#607D8B',
    HOMEROOM: '#FFC107'
  }
  return colors[code.toUpperCase()] || '#757575'
}

/**
 * Validate subject code format
 */
export function isValidSubjectCode(code: string): boolean {
  return /^[A-Z0-9_]+$/.test(code) && code.length >= 2 && code.length <= 50
}

/**
 * Format subject code (uppercase, trim)
 */
export function formatSubjectCode(code: string): string {
  return code.toUpperCase().trim()
}
