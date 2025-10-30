<template>
  <aside class="app-sidebar" :class="{ 'is-collapsed': isCollapsed, 'is-mobile-open': mobileMenuOpen }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <router-link to="/" class="brand-link" @click="closeMobileMenu">
        <span class="brand-icon">🌱</span>
        <span class="brand-text" v-show="!isCollapsed">Green School</span>
      </router-link>

      <!-- Desktop Collapse Toggle -->
      <button
        class="collapse-toggle"
        @click="toggleCollapse"
        aria-label="Toggle sidebar"
        v-show="!mobileMenuOpen"
      >
        <span class="toggle-icon">{{ isCollapsed ? '▶' : '◀' }}</span>
      </button>

      <!-- Mobile Close Button -->
      <button
        class="mobile-close"
        @click="closeMobileMenu"
        aria-label="Close menu"
      >
        <span class="close-icon">✕</span>
      </button>
    </div>

    <!-- Scrollable Menu Content -->
    <div class="sidebar-content">
      <!-- Navigation Links -->
      <nav class="sidebar-nav">
        <!-- Dashboard -->
        <router-link to="/dashboard" class="nav-item" @click="closeMobileMenu">
          <span class="nav-icon">📊</span>
          <span class="nav-text" v-show="!isCollapsed">Dashboard</span>
        </router-link>

        <!-- Users Management -->
        <div class="nav-group" v-if="canAccessUsers">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('users')"
            :class="{ 'is-active': isDropdownOpen('users') || isUsersRoute }"
          >
            <span class="nav-icon">👥</span>
            <span class="nav-text" v-show="!isCollapsed">Users</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('users') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('users') && !isCollapsed" class="nav-submenu">
            <router-link to="/users" class="submenu-item" @click="closeMobileMenu">
              List Users
            </router-link>
            <router-link to="/users/statistics" class="submenu-item" @click="closeMobileMenu">
              Statistics
            </router-link>
            <router-link to="/users/create" class="submenu-item" @click="closeMobileMenu">
              Create User
            </router-link>
          </div>
        </div>

        <!-- Schools Management -->
        <div class="nav-group" v-if="canAccessSchools">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('schools')"
            :class="{ 'is-active': isDropdownOpen('schools') || isSchoolsRoute }"
          >
            <span class="nav-icon">🏫</span>
            <span class="nav-text" v-show="!isCollapsed">Schools</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('schools') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('schools') && !isCollapsed" class="nav-submenu">
            <router-link to="/schools" class="submenu-item" @click="closeMobileMenu">
              List Schools
            </router-link>
            <router-link to="/schools/create" class="submenu-item" @click="closeMobileMenu">
              Create School
            </router-link>
          </div>
        </div>

        <!-- Teachers Management -->
        <div class="nav-group" v-if="canAccessTeachers">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('teachers')"
            :class="{ 'is-active': isDropdownOpen('teachers') || isTeachersRoute }"
          >
            <span class="nav-icon">👨‍🏫</span>
            <span class="nav-text" v-show="!isCollapsed">Teachers</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('teachers') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('teachers') && !isCollapsed" class="nav-submenu">
            <router-link to="/teachers" class="submenu-item" @click="closeMobileMenu">
              List Teachers
            </router-link>
            <router-link to="/teachers/create" class="submenu-item" @click="closeMobileMenu">
              Create Teacher
            </router-link>
          </div>
        </div>

        <!-- Students Management -->
        <div class="nav-group" v-if="canAccessStudents">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('students')"
            :class="{ 'is-active': isDropdownOpen('students') || isStudentsRoute }"
          >
            <span class="nav-icon">🎓</span>
            <span class="nav-text" v-show="!isCollapsed">Students</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('students') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('students') && !isCollapsed" class="nav-submenu">
            <router-link to="/students" class="submenu-item" @click="closeMobileMenu">
              List Students
            </router-link>
            <router-link to="/students/create" class="submenu-item" @click="closeMobileMenu">
              Create Student
            </router-link>
          </div>
        </div>

        <!-- Parents Management -->
        <div class="nav-group" v-if="canAccessParents">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('parents')"
            :class="{ 'is-active': isDropdownOpen('parents') || isParentsRoute }"
          >
            <span class="nav-icon">👪</span>
            <span class="nav-text" v-show="!isCollapsed">Parents</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('parents') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('parents') && !isCollapsed" class="nav-submenu">
            <router-link to="/parents" class="submenu-item" @click="closeMobileMenu">
              List Parents
            </router-link>
            <router-link to="/parents/create" class="submenu-item" @click="closeMobileMenu">
              Create Parent
            </router-link>
          </div>
        </div>

        <!-- Subjects Management -->
        <div class="nav-group" v-if="canAccessSubjects">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('subjects')"
            :class="{ 'is-active': isDropdownOpen('subjects') || isSubjectsRoute }"
          >
            <span class="nav-icon">📚</span>
            <span class="nav-text" v-show="!isCollapsed">Subjects</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('subjects') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('subjects') && !isCollapsed" class="nav-submenu">
            <router-link to="/subjects" class="submenu-item" @click="closeMobileMenu">
              List Subjects
            </router-link>
            <router-link to="/subjects/create" class="submenu-item" @click="closeMobileMenu">
              Create Subject
            </router-link>
          </div>
        </div>

        <!-- Rooms Management -->
        <div class="nav-group" v-if="canAccessRooms">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('rooms')"
            :class="{ 'is-active': isDropdownOpen('rooms') || isRoomsRoute }"
          >
            <span class="nav-icon">🏢</span>
            <span class="nav-text" v-show="!isCollapsed">Rooms</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('rooms') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('rooms') && !isCollapsed" class="nav-submenu">
            <router-link to="/rooms" class="submenu-item" @click="closeMobileMenu">
              List Rooms
            </router-link>
            <router-link to="/rooms/create" class="submenu-item" @click="closeMobileMenu">
              Create Room
            </router-link>
          </div>
        </div>

        <!-- Classes Management -->
        <div class="nav-group" v-if="canAccessClasses">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('classes')"
            :class="{ 'is-active': isDropdownOpen('classes') || isClassesRoute }"
          >
            <span class="nav-icon">🎒</span>
            <span class="nav-text" v-show="!isCollapsed">Classes</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('classes') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('classes') && !isCollapsed" class="nav-submenu">
            <router-link to="/classes" class="submenu-item" @click="closeMobileMenu">
              List Classes
            </router-link>
            <router-link to="/classes/create" class="submenu-item" @click="closeMobileMenu">
              Create Class
            </router-link>
          </div>
        </div>

        <!-- Lessons Management -->
        <div class="nav-group" v-if="canAccessLessons">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('lessons')"
            :class="{ 'is-active': isDropdownOpen('lessons') || isLessonsRoute }"
          >
            <span class="nav-icon">📝</span>
            <span class="nav-text" v-show="!isCollapsed">Lessons</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('lessons') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('lessons') && !isCollapsed" class="nav-submenu">
            <router-link to="/lessons" class="submenu-item" @click="closeMobileMenu">
              List Lessons
            </router-link>
            <router-link to="/lessons/create" class="submenu-item" @click="closeMobileMenu">
              Create Lesson
            </router-link>
          </div>
        </div>

        <!-- Assessments Management -->
        <div class="nav-group" v-if="canAccessAssessments">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('assessments')"
            :class="{ 'is-active': isDropdownOpen('assessments') || isAssessmentsRoute }"
          >
            <span class="nav-icon">📋</span>
            <span class="nav-text" v-show="!isCollapsed">Assessments</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('assessments') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('assessments') && !isCollapsed" class="nav-submenu">
            <router-link to="/assessments" class="submenu-item" @click="closeMobileMenu">
              List Assessments
            </router-link>
            <router-link to="/assessments/create" class="submenu-item" @click="closeMobileMenu">
              Create Assessment
            </router-link>
          </div>
        </div>

        <!-- Attendance Management -->
        <div class="nav-group" v-if="canAccessAttendance">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('attendance')"
            :class="{ 'is-active': isDropdownOpen('attendance') || isAttendanceRoute }"
          >
            <span class="nav-icon">✓</span>
            <span class="nav-text" v-show="!isCollapsed">Attendance</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('attendance') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('attendance') && !isCollapsed" class="nav-submenu">
            <router-link to="/attendance" class="submenu-item" @click="closeMobileMenu">
              View Attendance
            </router-link>
            <router-link to="/attendance/mark" class="submenu-item" @click="closeMobileMenu">
              Mark Attendance
            </router-link>
          </div>
        </div>

        <!-- Events Management -->
        <div class="nav-group" v-if="canAccessEvents">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('events')"
            :class="{ 'is-active': isDropdownOpen('events') || isEventsRoute }"
          >
            <span class="nav-icon">📅</span>
            <span class="nav-text" v-show="!isCollapsed">Events</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('events') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('events') && !isCollapsed" class="nav-submenu">
            <router-link to="/events" class="submenu-item" @click="closeMobileMenu">
              View Events
            </router-link>
            <router-link to="/events/create" class="submenu-item" @click="closeMobileMenu">
              Create Event
            </router-link>
          </div>
        </div>

        <!-- Activities Management -->
        <div class="nav-group" v-if="canAccessActivities">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('activities')"
            :class="{ 'is-active': isDropdownOpen('activities') || isActivitiesRoute }"
          >
            <span class="nav-icon">⚽</span>
            <span class="nav-text" v-show="!isCollapsed">Activities</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('activities') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('activities') && !isCollapsed" class="nav-submenu">
            <router-link to="/activities" class="submenu-item" @click="closeMobileMenu">
              View Activities
            </router-link>
            <router-link to="/activities/create" class="submenu-item" @click="closeMobileMenu">
              Create Activity
            </router-link>
          </div>
        </div>

        <!-- Vendors Management -->
        <div class="nav-group" v-if="canAccessVendors">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('vendors')"
            :class="{ 'is-active': isDropdownOpen('vendors') || isVendorsRoute }"
          >
            <span class="nav-icon">🏪</span>
            <span class="nav-text" v-show="!isCollapsed">Vendors</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('vendors') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('vendors') && !isCollapsed" class="nav-submenu">
            <router-link to="/vendors" class="submenu-item" @click="closeMobileMenu">
              View Vendors
            </router-link>
            <router-link to="/vendors/create" class="submenu-item" @click="closeMobileMenu">
              Create Vendor
            </router-link>
          </div>
        </div>

        <!-- Merits Management -->
        <div class="nav-group" v-if="canAccessMerits">
          <button
            class="nav-item nav-toggle"
            @click="toggleDropdown('merits')"
            :class="{ 'is-active': isDropdownOpen('merits') || isMeritsRoute }"
          >
            <span class="nav-icon">⭐</span>
            <span class="nav-text" v-show="!isCollapsed">Merits</span>
            <span class="nav-arrow" v-show="!isCollapsed">{{ isDropdownOpen('merits') ? '▼' : '▶' }}</span>
          </button>
          <div v-show="isDropdownOpen('merits') && !isCollapsed" class="nav-submenu">
            <router-link to="/merits" class="submenu-item" @click="closeMobileMenu">
              View Merits
            </router-link>
            <router-link to="/merits/leaderboard" class="submenu-item" @click="closeMobileMenu">
              Leaderboard
            </router-link>
            <router-link to="/merits/award" class="submenu-item" @click="closeMobileMenu">
              Award Merit
            </router-link>
          </div>
        </div>
      </nav>
    </div>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer">
      <!-- School Selector -->
      <div class="footer-section" v-show="!isCollapsed">
        <SchoolSelector />
      </div>

      <!-- User Menu -->
      <div class="footer-section user-section">
        <button
          class="user-button"
          @click="toggleDropdown('user')"
          :class="{ 'is-active': isDropdownOpen('user') }"
        >
          <span class="user-avatar">{{ userInitials }}</span>
          <div class="user-info" v-show="!isCollapsed">
            <span class="user-name">{{ authStore.userName }}</span>
            <span class="user-role">{{ authStore.currentUser?.persona || 'User' }}</span>
          </div>
          <span class="user-arrow" v-show="!isCollapsed">{{ isDropdownOpen('user') ? '▲' : '▼' }}</span>
        </button>

        <div v-show="isDropdownOpen('user') && !isCollapsed" class="user-menu">
          <router-link to="/profile" class="user-menu-item" @click="closeMobileMenu">
            <span class="menu-icon">👤</span>
            Profile
          </router-link>
          <router-link to="/settings" class="user-menu-item" @click="closeMobileMenu">
            <span class="menu-icon">⚙️</span>
            Settings
          </router-link>
          <div class="menu-divider"></div>
          <button class="user-menu-item" @click="handleLogout">
            <span class="menu-icon">🚪</span>
            Logout
          </button>
        </div>
      </div>
    </div>
  </aside>

  <!-- Mobile Overlay -->
  <div
    v-if="mobileMenuOpen"
    class="sidebar-overlay"
    @click="closeMobileMenu"
  ></div>

  <!-- Mobile Menu Toggle -->
  <button
    class="mobile-menu-button"
    @click="toggleMobileMenu"
    aria-label="Open menu"
  >
    <span class="hamburger-icon">☰</span>
  </button>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import SchoolSelector from './SchoolSelector.vue'

const route = useRoute()
const authStore = useAuthStore()

// State
const isCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const openDropdowns = ref<Set<string>>(new Set())

// Load collapsed state from localStorage
onMounted(() => {
  const saved = localStorage.getItem('sidebar-collapsed')
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
  }

  // Apply initial collapsed state to document
  updateGlobalCollapsedClass()
})

/**
 * Update global collapsed class on document
 */
function updateGlobalCollapsedClass() {
  if (isCollapsed.value) {
    document.documentElement.classList.add('sidebar-collapsed')
  } else {
    document.documentElement.classList.remove('sidebar-collapsed')
  }
}

/**
 * User initials for avatar
 */
const userInitials = computed(() => {
  const names = authStore.userName.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

/**
 * Check if user can access users module
 */
const canAccessUsers = computed(() => {
  return authStore.hasRole('administrator')
})

/**
 * Check if user can access schools module
 */
const canAccessSchools = computed(() => {
  return authStore.hasRole('administrator')
})

/**
 * Check if user can access teachers module
 */
const canAccessTeachers = computed(() => {
  return authStore.hasRole('administrator')
})

/**
 * Check if user can access students module
 */
const canAccessStudents = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access parents module
 */
const canAccessParents = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access subjects module
 */
const canAccessSubjects = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access rooms module
 */
const canAccessRooms = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access classes module
 */
const canAccessClasses = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access lessons module
 */
const canAccessLessons = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access assessments module
 */
const canAccessAssessments = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access attendance module
 */
const canAccessAttendance = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access events module
 */
const canAccessEvents = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access activities module
 */
const canAccessActivities = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if user can access vendors module
 */
const canAccessVendors = computed(() => {
  return authStore.hasRole('administrator')
})

/**
 * Check if user can access merits module
 */
const canAccessMerits = computed(() => {
  return authStore.hasAnyRole(['administrator', 'teacher'])
})

/**
 * Check if current route is users-related
 */
const isUsersRoute = computed(() => route.path.startsWith('/users'))
const isSchoolsRoute = computed(() => route.path.startsWith('/schools'))
const isTeachersRoute = computed(() => route.path.startsWith('/teachers'))
const isStudentsRoute = computed(() => route.path.startsWith('/students'))
const isParentsRoute = computed(() => route.path.startsWith('/parents'))
const isSubjectsRoute = computed(() => route.path.startsWith('/subjects'))
const isRoomsRoute = computed(() => route.path.startsWith('/rooms'))
const isClassesRoute = computed(() => route.path.startsWith('/classes'))
const isLessonsRoute = computed(() => route.path.startsWith('/lessons'))
const isAssessmentsRoute = computed(() => route.path.startsWith('/assessments'))
const isAttendanceRoute = computed(() => route.path.startsWith('/attendance'))
const isEventsRoute = computed(() => route.path.startsWith('/events'))
const isActivitiesRoute = computed(() => route.path.startsWith('/activities'))
const isVendorsRoute = computed(() => route.path.startsWith('/vendors'))
const isMeritsRoute = computed(() => route.path.startsWith('/merits'))

/**
 * Check if dropdown is open
 */
function isDropdownOpen(name: string): boolean {
  return openDropdowns.value.has(name)
}

/**
 * Toggle dropdown
 */
function toggleDropdown(name: string) {
  if (openDropdowns.value.has(name)) {
    openDropdowns.value.delete(name)
  } else {
    openDropdowns.value.add(name)
  }
}

/**
 * Toggle sidebar collapse
 */
function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar-collapsed', String(isCollapsed.value))

  // Update global class
  updateGlobalCollapsedClass()

  // Close all dropdowns when collapsing
  if (isCollapsed.value) {
    openDropdowns.value.clear()
  }
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

/**
 * Close mobile menu
 */
function closeMobileMenu() {
  mobileMenuOpen.value = false
}

/**
 * Handle logout
 */
function handleLogout() {
  authStore.logout()
  closeMobileMenu()
}
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  background: #1e293b;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.app-sidebar.is-collapsed {
  width: 70px;
}

/* Sidebar Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #334155;
  min-height: 70px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #f8fafc;
  font-weight: 700;
  font-size: 1.125rem;
  transition: color 0.2s;
  flex: 1;
}

.brand-link:hover {
  color: #10b981;
}

.brand-icon {
  font-size: 1.75rem;
  flex-shrink: 0;
}

.brand-text {
  white-space: nowrap;
  overflow: hidden;
}

.collapse-toggle {
  background: #334155;
  border: none;
  color: #e2e8f0;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.collapse-toggle:hover {
  background: #475569;
  color: #10b981;
}

.toggle-icon {
  font-size: 0.875rem;
}

.mobile-close {
  display: none;
}

/* Sidebar Content */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0.5rem 0;
}

.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #1e293b;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Navigation */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  font-size: 0.9375rem;
  font-family: inherit;
  text-align: left;
}

.nav-item:hover {
  background: #334155;
  color: #f8fafc;
}

.nav-item.router-link-active {
  background: #10b981;
  color: #ffffff;
  font-weight: 500;
}

.nav-item.is-active {
  background: #334155;
  color: #10b981;
}

.nav-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-arrow {
  font-size: 0.75rem;
  margin-left: auto;
  flex-shrink: 0;
}

/* Nav Groups & Submenus */
.nav-group {
  display: flex;
  flex-direction: column;
}

.nav-toggle {
  justify-content: space-between;
}

.nav-submenu {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.25rem 0 0.25rem 2.75rem;
  margin-top: 0.25rem;
}

.submenu-item {
  display: block;
  padding: 0.625rem 1rem;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.submenu-item:hover {
  background: #334155;
  color: #f8fafc;
}

.submenu-item.router-link-active {
  background: #334155;
  color: #10b981;
  font-weight: 500;
}

/* Collapsed State */
.is-collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
}

.is-collapsed .nav-submenu {
  display: none;
}

/* Sidebar Footer */
.sidebar-footer {
  border-top: 1px solid #334155;
  padding: 0.75rem 0.5rem;
}

.footer-section {
  padding: 0.5rem;
}

/* User Section */
.user-section {
  padding: 0;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  transition: all 0.2s;
  color: #e2e8f0;
  font-family: inherit;
}

.user-button:hover {
  background: #334155;
}

.user-button.is-active {
  background: #334155;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  min-width: 0;
}

.user-name {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #f8fafc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: capitalize;
}

.user-arrow {
  font-size: 0.75rem;
  margin-left: auto;
  flex-shrink: 0;
}

.user-menu {
  margin-top: 0.5rem;
  background: #0f172a;
  border-radius: 8px;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.875rem;
  font-family: inherit;
}

.user-menu-item:hover {
  background: #1e293b;
  color: #f8fafc;
}

.user-menu-item.router-link-active {
  background: #1e293b;
  color: #10b981;
}

.menu-icon {
  font-size: 1rem;
}

.menu-divider {
  height: 1px;
  background: #334155;
  margin: 0.25rem 0;
}

/* Mobile Overlay */
.sidebar-overlay {
  display: none;
}

.mobile-menu-button {
  display: none;
}

/* Mobile Styles */
@media (max-width: 1024px) {
  .app-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    width: 280px;
  }

  .app-sidebar.is-mobile-open {
    transform: translateX(0);
  }

  .app-sidebar.is-collapsed {
    width: 280px;
  }

  .collapse-toggle {
    display: none;
  }

  .mobile-close {
    display: flex;
    background: #334155;
    border: none;
    color: #e2e8f0;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .mobile-close:hover {
    background: #475569;
    color: #ef4444;
  }

  .close-icon {
    font-size: 1.25rem;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .mobile-menu-button {
    display: flex;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 998;
    background: #1e293b;
    border: none;
    color: #e2e8f0;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.2s;
  }

  .mobile-menu-button:hover {
    background: #334155;
    color: #10b981;
  }

  .hamburger-icon {
    font-size: 1.5rem;
  }
}
</style>
