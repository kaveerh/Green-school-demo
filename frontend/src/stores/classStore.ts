/**
 * Class Store
 *
 * Pinia store for Class state management
 */

import { defineStore } from 'pinia';
import type {
  Class,
  ClassCreateInput,
  ClassUpdateInput,
  ClassSearchParams,
  ClassStatistics,
  StudentClass,
  EnrollmentCreateInput,
  Quarter
} from '@/types/class';
import * as classService from '@/services/classService';

interface ClassState {
  classes: Class[];
  selectedClass: Class | null;
  statistics: ClassStatistics | null;
  enrollments: StudentClass[];
  isLoading: boolean;
  error: string | null;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export const useClassStore = defineStore('class', {
  state: (): ClassState => ({
    classes: [],
    selectedClass: null,
    statistics: null,
    enrollments: [],
    isLoading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 50,
      total: 0,
      totalPages: 0
    }
  }),

  getters: {
    /**
     * Get classes for a specific quarter
     */
    getClassesByQuarter: (state) => (quarter: Quarter) => {
      return state.classes.filter(c => c.quarter === quarter);
    },

    /**
     * Get classes for a specific grade level
     */
    getClassesByGrade: (state) => (grade: number) => {
      return state.classes.filter(c => c.grade_level === grade);
    },

    /**
     * Get active classes only
     */
    activeClasses: (state) => {
      return state.classes.filter(c => c.is_active);
    },

    /**
     * Get inactive classes only
     */
    inactiveClasses: (state) => {
      return state.classes.filter(c => !c.is_active);
    },

    /**
     * Get classes that are full
     */
    fullClasses: (state) => {
      return state.classes.filter(c => c.is_full);
    },

    /**
     * Get classes that have available seats
     */
    availableClasses: (state) => {
      return state.classes.filter(c => !c.is_full && c.is_active);
    },

    /**
     * Get total enrollment across all classes
     */
    totalEnrollment: (state) => {
      return state.classes.reduce((sum, c) => sum + c.current_enrollment, 0);
    },

    /**
     * Get average class size
     */
    averageClassSize: (state) => {
      if (state.classes.length === 0) return 0;
      const total = state.classes.reduce((sum, c) => sum + c.current_enrollment, 0);
      return Math.round((total / state.classes.length) * 10) / 10;
    },

    /**
     * Get overall capacity utilization
     */
    capacityUtilization: (state) => {
      const totalCapacity = state.classes.reduce((sum, c) => sum + c.max_students, 0);
      const totalEnrolled = state.classes.reduce((sum, c) => sum + c.current_enrollment, 0);

      if (totalCapacity === 0) return 0;
      return Math.round((totalEnrolled / totalCapacity) * 100);
    }
  },

  actions: {
    /**
     * Fetch classes with filters
     */
    async fetchClasses(params: ClassSearchParams) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await classService.getClasses(params);
        this.classes = response.classes || [];
        this.pagination = {
          page: response.page,
          limit: response.limit,
          total: response.total,
          totalPages: response.total_pages
        };
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch classes';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch class by ID
     */
    async fetchClassById(classId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        this.selectedClass = await classService.getClassById(classId);
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch class';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Search classes
     */
    async searchClasses(schoolId: string, query: string, page: number = 1, limit: number = 50) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await classService.searchClasses(schoolId, query, page, limit);
        this.classes = response.classes || [];
        this.pagination = {
          page: response.page,
          limit: response.limit,
          total: response.total,
          totalPages: response.total_pages
        };
      } catch (err: any) {
        this.error = err.message || 'Failed to search classes';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Create new class
     */
    async createClass(schoolId: string, data: ClassCreateInput) {
      this.isLoading = true;
      this.error = null;

      try {
        const newClass = await classService.createClass(schoolId, data);
        this.classes.unshift(newClass);
        this.pagination.total += 1;
        return newClass;
      } catch (err: any) {
        this.error = err.message || 'Failed to create class';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Update class
     */
    async updateClass(classId: string, data: ClassUpdateInput) {
      this.isLoading = true;
      this.error = null;

      try {
        const updated = await classService.updateClass(classId, data);

        const index = this.classes.findIndex(c => c.id === classId);
        if (index !== -1) {
          this.classes[index] = updated;
        }

        if (this.selectedClass?.id === classId) {
          this.selectedClass = updated;
        }

        return updated;
      } catch (err: any) {
        this.error = err.message || 'Failed to update class';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Delete class
     */
    async deleteClass(classId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        await classService.deleteClass(classId);

        this.classes = this.classes.filter(c => c.id !== classId);
        this.pagination.total -= 1;

        if (this.selectedClass?.id === classId) {
          this.selectedClass = null;
        }
      } catch (err: any) {
        this.error = err.message || 'Failed to delete class';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Toggle class active status
     */
    async toggleStatus(classId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const updated = await classService.toggleClassStatus(classId);

        const index = this.classes.findIndex(c => c.id === classId);
        if (index !== -1) {
          this.classes[index] = updated;
        }

        if (this.selectedClass?.id === classId) {
          this.selectedClass = updated;
        }

        return updated;
      } catch (err: any) {
        this.error = err.message || 'Failed to toggle status';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch statistics
     */
    async fetchStatistics(schoolId?: string) {
      this.isLoading = true;
      this.error = null;

      try {
        this.statistics = await classService.getClassStatistics(schoolId);
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch statistics';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch classes by teacher
     */
    async fetchClassesByTeacher(schoolId: string, teacherId: string, quarter?: Quarter, academicYear?: string) {
      this.isLoading = true;
      this.error = null;

      try {
        this.classes = await classService.getClassesByTeacher(schoolId, teacherId, quarter, academicYear);
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch teacher classes';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch classes by subject
     */
    async fetchClassesBySubject(schoolId: string, subjectId: string, gradeLevel?: number, quarter?: Quarter) {
      this.isLoading = true;
      this.error = null;

      try {
        this.classes = await classService.getClassesBySubject(schoolId, subjectId, gradeLevel, quarter);
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch subject classes';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch classes by room
     */
    async fetchClassesByRoom(schoolId: string, roomId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        this.classes = await classService.getClassesByRoom(schoolId, roomId);
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch room classes';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Enroll student in class
     */
    async enrollStudent(data: EnrollmentCreateInput) {
      this.isLoading = true;
      this.error = null;

      try {
        const enrollment = await classService.enrollStudent(data);

        // Update class enrollment count
        const classIndex = this.classes.findIndex(c => c.id === data.class_id);
        if (classIndex !== -1) {
          this.classes[classIndex].current_enrollment += 1;
        }

        if (this.selectedClass?.id === data.class_id) {
          this.selectedClass.current_enrollment += 1;
        }

        return enrollment;
      } catch (err: any) {
        this.error = err.message || 'Failed to enroll student';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Fetch students in class
     */
    async fetchStudentsInClass(classId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await classService.getStudentsInClass(classId);
        this.enrollments = response.enrollments;
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch students';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Drop student from class
     */
    async dropStudent(enrollmentId: string, classId: string) {
      this.isLoading = true;
      this.error = null;

      try {
        await classService.dropStudent(enrollmentId);

        // Update class enrollment count
        const classIndex = this.classes.findIndex(c => c.id === classId);
        if (classIndex !== -1 && this.classes[classIndex].current_enrollment > 0) {
          this.classes[classIndex].current_enrollment -= 1;
        }

        if (this.selectedClass?.id === classId && this.selectedClass.current_enrollment > 0) {
          this.selectedClass.current_enrollment -= 1;
        }

        // Update enrollments list
        const enrollmentIndex = this.enrollments.findIndex(e => e.id === enrollmentId);
        if (enrollmentIndex !== -1) {
          this.enrollments[enrollmentIndex].status = 'dropped';
        }
      } catch (err: any) {
        this.error = err.message || 'Failed to drop student';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Pagination: Go to specific page
     */
    setPage(page: number) {
      this.pagination.page = page;
    },

    /**
     * Pagination: Set page size
     */
    setPageSize(limit: number) {
      this.pagination.limit = limit;
      this.pagination.page = 1; // Reset to first page
    },

    /**
     * Clear selected class
     */
    clearSelection() {
      this.selectedClass = null;
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null;
    },

    /**
     * Reset store state
     */
    reset() {
      this.classes = [];
      this.selectedClass = null;
      this.statistics = null;
      this.enrollments = [];
      this.isLoading = false;
      this.error = null;
      this.pagination = {
        page: 1,
        limit: 50,
        total: 0,
        totalPages: 0
      };
    }
  }
});
