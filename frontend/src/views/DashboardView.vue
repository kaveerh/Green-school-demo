<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">Green School</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">Welcome, Admin</span>
            <button class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">Dashboard</h2>
          <div class="flex items-center gap-4">
            <!-- School Selector -->
            <div class="relative">
              <label for="school-select" class="sr-only">Select School</label>
              <select
                id="school-select"
                v-model="dashboardStore.selectedSchoolId"
                @change="handleSchoolChange"
                :disabled="dashboardStore.loadingSchools || dashboardStore.schools.length === 0"
                class="block w-64 pl-3 pr-10 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 bg-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-if="dashboardStore.schools.length === 0" value="">
                  {{ dashboardStore.loadingSchools ? 'Loading schools...' : 'No schools available' }}
                </option>
                <option
                  v-for="school in dashboardStore.schools"
                  :key="school.id"
                  :value="school.id"
                >
                  {{ school.name }}
                </option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </div>

            <button
              @click="refreshData"
              :disabled="dashboardStore.isLoading"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <svg
                class="h-4 w-4 mr-2"
                :class="{ 'animate-spin': dashboardStore.isLoading }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="dashboardStore.hasError" class="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-700">
                {{ dashboardStore.error }}
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="dashboardStore.isLoading && !dashboardStore.hasData" class="flex justify-center items-center py-12">
          <div class="text-center">
            <svg class="animate-spin h-8 w-8 text-primary-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-600">Loading dashboard data...</p>
          </div>
        </div>

        <!-- Main Stats Grid -->
        <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <!-- Students Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Total Students</dt>
                    <dd class="text-2xl font-bold text-gray-900">{{ dashboardStore.totalStudents }}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/students" class="font-medium text-primary-600 hover:text-primary-500">
                  View all students
                </router-link>
              </div>
            </div>
          </div>

          <!-- Teachers Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Total Teachers</dt>
                    <dd class="text-2xl font-bold text-gray-900">{{ dashboardStore.totalTeachers }}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/teachers" class="font-medium text-primary-600 hover:text-primary-500">
                  View all teachers
                </router-link>
              </div>
            </div>
          </div>

          <!-- Classes Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-purple-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Total Classes</dt>
                    <dd class="text-2xl font-bold text-gray-900">{{ dashboardStore.totalClasses }}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/classes" class="font-medium text-primary-600 hover:text-primary-500">
                  View all classes
                </router-link>
              </div>
            </div>
          </div>

          <!-- Events Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                  <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Upcoming Events</dt>
                    <dd class="text-2xl font-bold text-gray-900">{{ dashboardStore.upcomingEvents }}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/events" class="font-medium text-primary-600 hover:text-primary-500">
                  View all events
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Secondary Stats Grid -->
        <div v-if="!dashboardStore.isLoading || dashboardStore.hasData" class="grid grid-cols-2 gap-5 sm:grid-cols-3 lg:grid-cols-5 mb-8">
          <!-- Parents Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <dt class="text-sm font-medium text-gray-500 truncate">Parents</dt>
              <dd class="mt-1 text-xl font-semibold text-gray-900">{{ dashboardStore.totalParents }}</dd>
            </div>
          </div>

          <!-- Subjects Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <dt class="text-sm font-medium text-gray-500 truncate">Subjects</dt>
              <dd class="mt-1 text-xl font-semibold text-gray-900">{{ dashboardStore.totalSubjects }}</dd>
            </div>
          </div>

          <!-- Rooms Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <dt class="text-sm font-medium text-gray-500 truncate">Rooms</dt>
              <dd class="mt-1 text-xl font-semibold text-gray-900">{{ dashboardStore.totalRooms }}</dd>
            </div>
          </div>

          <!-- Activities Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <dt class="text-sm font-medium text-gray-500 truncate">Activities</dt>
              <dd class="mt-1 text-xl font-semibold text-gray-900">{{ dashboardStore.totalActivities }}</dd>
            </div>
          </div>

          <!-- Merits Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <dt class="text-sm font-medium text-gray-500 truncate">Merits</dt>
              <dd class="mt-1 text-xl font-semibold text-gray-900">{{ dashboardStore.totalMerits }}</dd>
            </div>
          </div>
        </div>

        <!-- Quick Links -->
        <div v-if="!dashboardStore.isLoading || dashboardStore.hasData" class="bg-white shadow rounded-lg p-6 mb-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <router-link to="/users" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Manage Users</p>
            </router-link>
            <router-link to="/students" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">View Students</p>
            </router-link>
            <router-link to="/teachers" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">View Teachers</p>
            </router-link>
            <router-link to="/classes" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">View Classes</p>
            </router-link>
            <router-link to="/assessments" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Assessments</p>
            </router-link>
            <router-link to="/attendance" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Attendance</p>
            </router-link>
            <router-link to="/lessons" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Lesson Plans</p>
            </router-link>
            <router-link to="/events" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Events</p>
            </router-link>
            <router-link to="/activities" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Activities</p>
            </router-link>
            <router-link to="/merits" class="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-center">
              <p class="text-sm font-medium text-gray-700">Merits</p>
            </router-link>
          </div>
        </div>

        <!-- Last Updated -->
        <div v-if="dashboardStore.lastUpdated && !dashboardStore.isLoading" class="text-sm text-gray-500 text-center">
          Last updated: {{ formatDate(dashboardStore.lastUpdated) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useAuthStore } from '@/stores/authStore'

const dashboardStore = useDashboardStore()
const authStore = useAuthStore()

onMounted(async () => {
  // Wait a bit for auth store to initialize and fetch schools
  await new Promise(resolve => setTimeout(resolve, 500))

  // Load dashboard data if school is selected
  if (authStore.currentSchoolId) {
    await loadDashboardData()
  } else {
    console.warn('No school selected, waiting for school selection...')
  }
})

// Watch for school changes and reload data
watch(() => authStore.currentSchoolId, async (newSchoolId) => {
  if (newSchoolId) {
    console.log('School changed, reloading dashboard data for:', newSchoolId)
    await loadDashboardData()
  }
})

async function loadDashboardData() {
  try {
    if (!authStore.currentSchoolId) {
      console.warn('Cannot load dashboard: no school selected')
      return
    }
    await dashboardStore.fetchAllStatistics()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

async function refreshData() {
  await loadDashboardData()
}

function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(date))
}
</script>
