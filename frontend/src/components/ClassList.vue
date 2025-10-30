<template>
  <div class="class-list-container">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Classes</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage class sections, schedules, and enrollments
        </p>
      </div>
      <router-link
        to="/classes/create"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        <svg class="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Class
      </router-link>
    </div>

    <!-- Statistics Cards -->
    <div v-if="statistics" class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Classes</dt>
                <dd class="text-lg font-semibold text-gray-900">{{ statistics.total_classes }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Classes</dt>
                <dd class="text-lg font-semibold text-gray-900">{{ statistics.active_classes }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Enrollment</dt>
                <dd class="text-lg font-semibold text-gray-900">{{ statistics.total_enrollment }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0h2a2 2 0 012 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2v14z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Avg. Class Size</dt>
                <dd class="text-lg font-semibold text-gray-900">{{ statistics.average_class_size.toFixed(1) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Search -->
        <div class="sm:col-span-2">
          <label for="search" class="block text-sm font-medium text-gray-700">Search</label>
          <div class="mt-1 relative rounded-md shadow-sm">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              id="search"
              v-model="searchQuery"
              @input="handleSearch"
              class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md"
              placeholder="Search by code, name, or description"
            />
          </div>
        </div>

        <!-- Grade Level Filter -->
        <div>
          <label for="grade" class="block text-sm font-medium text-gray-700">Grade Level</label>
          <select
            id="grade"
            v-model="filters.grade_level"
            @change="applyFilters"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option :value="undefined">All Grades</option>
            <option v-for="grade in GRADE_LEVELS" :key="grade" :value="grade">
              Grade {{ grade }}
            </option>
          </select>
        </div>

        <!-- Quarter Filter -->
        <div>
          <label for="quarter" class="block text-sm font-medium text-gray-700">Quarter</label>
          <select
            id="quarter"
            v-model="filters.quarter"
            @change="applyFilters"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option :value="undefined">All Quarters</option>
            <option v-for="quarter in QUARTERS" :key="quarter" :value="quarter">
              {{ getQuarterLabel(quarter) }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label for="status" class="block text-sm font-medium text-gray-700">Status</label>
          <select
            id="status"
            v-model="filters.is_active"
            @change="applyFilters"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option :value="undefined">All Status</option>
            <option :value="true">Active</option>
            <option :value="false">Inactive</option>
          </select>
        </div>

        <!-- Academic Year Filter -->
        <div>
          <label for="year" class="block text-sm font-medium text-gray-700">Academic Year</label>
          <select
            id="year"
            v-model="filters.academic_year"
            @change="applyFilters"
            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          >
            <option :value="undefined">All Years</option>
            <option :value="getPreviousAcademicYear()">{{ getPreviousAcademicYear() }}</option>
            <option :value="getCurrentAcademicYear()">{{ getCurrentAcademicYear() }} (Current)</option>
            <option :value="getNextAcademicYear()">{{ getNextAcademicYear() }}</option>
          </select>
        </div>

        <!-- Clear Filters -->
        <div class="flex items-end">
          <button
            @click="clearFilters"
            type="button"
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-sm text-gray-500">Loading classes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Classes Table -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Code
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Subject
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Teacher
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Grade
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Quarter
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Enrollment
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Schedule
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" class="relative px-6 py-3">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="classes.length === 0">
            <td colspan="10" class="px-6 py-12 text-center text-sm text-gray-500">
              No classes found. Create your first class to get started.
            </td>
          </tr>
          <tr v-for="classItem in classes" :key="classItem.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div
                  v-if="classItem.color"
                  class="flex-shrink-0 h-3 w-3 rounded-full mr-2"
                  :style="{ backgroundColor: classItem.color }"
                ></div>
                <div class="text-sm font-medium text-gray-900">{{ classItem.code }}</div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="text-sm text-gray-900">{{ classItem.name }}</div>
              <div v-if="classItem.room_number" class="text-sm text-gray-500">Room {{ classItem.room_number }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ classItem.subject_name || 'N/A' }}</div>
              <div class="text-sm text-gray-500">{{ classItem.subject_code || '' }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ classItem.teacher_name || 'Not assigned' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              Grade {{ classItem.grade_level }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                {{ classItem.quarter }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ classItem.current_enrollment }} / {{ classItem.max_students }}</div>
              <div class="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div
                  class="h-1.5 rounded-full"
                  :class="getCapacityBarColor(classItem.capacity_percent || 0)"
                  :style="{ width: `${classItem.capacity_percent || 0}%` }"
                ></div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500">
              {{ formatSchedule(classItem.schedule) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                v-if="classItem.is_active"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                Active
              </span>
              <span
                v-else
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
              >
                Inactive
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link
                :to="`/classes/${classItem.id}`"
                class="text-indigo-600 hover:text-indigo-900 mr-4"
              >
                View
              </router-link>
              <router-link
                :to="`/classes/${classItem.id}/edit`"
                class="text-indigo-600 hover:text-indigo-900 mr-4"
              >
                Edit
              </router-link>
              <button
                @click="confirmDelete(classItem)"
                class="text-red-600 hover:text-red-900"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="pagination.totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="goToPage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="goToPage(pagination.page + 1)"
            :disabled="pagination.page === pagination.totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ (pagination.page - 1) * pagination.limit + 1 }}</span>
              to
              <span class="font-medium">{{ Math.min(pagination.page * pagination.limit, pagination.total) }}</span>
              of
              <span class="font-medium">{{ pagination.total }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="goToPage(pagination.page - 1)"
                :disabled="pagination.page === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  page === pagination.page
                    ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                ]"
              >
                {{ page }}
              </button>

              <button
                @click="goToPage(pagination.page + 1)"
                :disabled="pagination.page === pagination.totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="classToDelete" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Delete Class
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Are you sure you want to delete <strong>{{ classToDelete.code }} - {{ classToDelete.name }}</strong>?
                  This action cannot be undone and will affect all enrolled students.
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button
              @click="handleDelete"
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Delete
            </button>
            <button
              @click="classToDelete = null"
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useClassStore } from '@/stores/classStore';
import { useSchool } from '@/composables/useSchool'
import {
  QUARTERS,
  GRADE_LEVELS,
  getQuarterLabel,
  getCurrentAcademicYear,
  getNextAcademicYear,
  getPreviousAcademicYear,
  formatSchedule
} from '@/types/class';
import type { Class, Quarter } from '@/types/class';

const classStore = useClassStore();
const { currentSchoolId } = useSchool();
const searchQuery = ref('');
const searchTimeout = ref<number | null>(null);
const classToDelete = ref<Class | null>(null);

const filters = ref({
  grade_level: undefined as number | undefined,
  quarter: undefined as Quarter | undefined,
  academic_year: undefined as string | undefined,
  is_active: undefined as boolean | undefined
});

const classes = computed(() => classStore.classes);
const isLoading = computed(() => classStore.isLoading);
const error = computed(() => classStore.error);
const statistics = computed(() => classStore.statistics);
const pagination = computed(() => classStore.pagination);

const visiblePages = computed(() => {
  const current = pagination.value.page;
  const total = pagination.value.totalPages;
  const delta = 2;
  const range: number[] = [];

  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i);
  }

  if (current - delta > 2) {
    range.unshift(-1);
  }
  if (current + delta < total - 1) {
    range.push(-1);
  }

  range.unshift(1);
  if (total > 1) {
    range.push(total);
  }

  return range;
});

onMounted(async () => {
  await loadClasses();
  await loadStatistics();
});

async function loadClasses() {
  if (!currentSchoolId.value) {
    console.warn('Cannot load classes: no school selected');
    return;
  }

  await classStore.fetchClasses({
    school_id: currentSchoolId.value,
    page: pagination.value.page,
    limit: pagination.value.limit,
    ...filters.value
  });
}

async function loadStatistics() {
  if (!currentSchoolId.value) {
    console.warn('Cannot load class statistics: no school selected');
    return;
  }
  await classStore.fetchStatistics(currentSchoolId.value);
}

function handleSearch() {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  searchTimeout.value = window.setTimeout(async () => {
    if (searchQuery.value.trim().length >= 2) {
      if (!currentSchoolId.value) {
        console.warn('Cannot search classes: no school selected');
        return;
      }
      await classStore.searchClasses(currentSchoolId.value, searchQuery.value.trim());
    } else if (searchQuery.value.trim().length === 0) {
      await loadClasses();
    }
  }, 300);
}

async function applyFilters() {
  await loadClasses();
}

async function clearFilters() {
  filters.value = {
    grade_level: undefined,
    quarter: undefined,
    academic_year: undefined,
    is_active: undefined
  };
  searchQuery.value = '';
  await loadClasses();
}

async function goToPage(page: number) {
  if (page < 1 || page > pagination.value.totalPages) return;
  classStore.setPage(page);
  await loadClasses();
}

function confirmDelete(classItem: Class) {
  classToDelete.value = classItem;
}

async function handleDelete() {
  if (!classToDelete.value) return;

  try {
    await classStore.deleteClass(classToDelete.value.id);
    classToDelete.value = null;
    await loadStatistics(); // Refresh statistics
  } catch (err) {
    console.error('Failed to delete class:', err);
  }
}

function getCapacityBarColor(percent: number): string {
  if (percent >= 100) return 'bg-red-600';
  if (percent >= 90) return 'bg-orange-600';
  if (percent >= 75) return 'bg-yellow-600';
  return 'bg-green-600';
}
</script>

<style scoped>
.class-list-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
