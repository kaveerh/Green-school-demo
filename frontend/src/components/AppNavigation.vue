<template>
  <nav class="app-navigation" :class="{ 'is-mobile-open': mobileMenuOpen }">
    <!-- Logo/Brand -->
    <div class="nav-brand">
      <router-link to="/" class="brand-link">
        <span class="brand-icon">🌱</span>
        <span class="brand-text">Green School</span>
      </router-link>

      <!-- Mobile Menu Toggle -->
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        aria-label="Toggle menu"
      >
        <span class="hamburger-icon">☰</span>
      </button>
    </div>

    <!-- Navigation Links -->
    <ul class="nav-menu" :class="{ 'is-open': mobileMenuOpen }">
      <!-- Dashboard -->
      <li class="nav-item">
        <router-link to="/dashboard" class="nav-link" @click="closeMobileMenu">
          <span class="nav-icon">📊</span>
          <span class="nav-text">Dashboard</span>
        </router-link>
      </li>

      <!-- Users Management -->
      <li class="nav-item" v-if="canAccessUsers">
        <div class="nav-dropdown">
          <button
            class="nav-link nav-dropdown-toggle"
            @click="toggleDropdown('users')"
            :class="{ 'is-active': isDropdownOpen('users') || isUsersRoute }"
          >
            <span class="nav-icon">👥</span>
            <span class="nav-text">Users</span>
            <span class="dropdown-arrow">{{ isDropdownOpen('users') ? '▼' : '▶' }}</span>
          </button>

          <ul
            v-show="isDropdownOpen('users')"
            class="nav-dropdown-menu"
          >
            <li>
              <router-link to="/users" class="nav-dropdown-link" @click="closeMobileMenu">
                List Users
              </router-link>
            </li>
            <li>
              <router-link to="/users/statistics" class="nav-dropdown-link" @click="closeMobileMenu">
                Statistics
              </router-link>
            </li>
            <li>
              <router-link to="/users/create" class="nav-dropdown-link" @click="closeMobileMenu">
                Create User
              </router-link>
            </li>
          </ul>
        </div>
      </li>

      <!-- Placeholder for future modules -->
      <li class="nav-item nav-item-disabled">
        <span class="nav-link">
          <span class="nav-icon">🏫</span>
          <span class="nav-text">Schools</span>
          <span class="coming-soon">Coming Soon</span>
        </span>
      </li>

      <li class="nav-item nav-item-disabled">
        <span class="nav-link">
          <span class="nav-icon">📚</span>
          <span class="nav-text">Classes</span>
          <span class="coming-soon">Coming Soon</span>
        </span>
      </li>
    </ul>

    <!-- User Menu -->
    <div class="nav-user">
      <div class="nav-dropdown">
        <button
          class="nav-user-button"
          @click="toggleDropdown('user')"
          :class="{ 'is-active': isDropdownOpen('user') }"
        >
          <span class="user-avatar">{{ userInitials }}</span>
          <span class="user-name">{{ currentUserName }}</span>
          <span class="dropdown-arrow">{{ isDropdownOpen('user') ? '▼' : '▶' }}</span>
        </button>

        <ul
          v-show="isDropdownOpen('user')"
          class="nav-dropdown-menu nav-user-menu"
        >
          <li>
            <router-link to="/profile" class="nav-dropdown-link" @click="closeMobileMenu">
              Profile
            </router-link>
          </li>
          <li>
            <router-link to="/settings" class="nav-dropdown-link" @click="closeMobileMenu">
              Settings
            </router-link>
          </li>
          <li class="nav-dropdown-divider"></li>
          <li>
            <button class="nav-dropdown-link" @click="handleLogout">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// State
const mobileMenuOpen = ref(false)
const openDropdowns = ref<Set<string>>(new Set())

// Mock user data (TODO: Replace with actual auth store)
const currentUserName = ref('Admin User')
const currentUserRole = ref('administrator')

/**
 * User initials for avatar
 */
const userInitials = computed(() => {
  const names = currentUserName.value.split(' ')
  return names.map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

/**
 * Check if user can access users module
 */
const canAccessUsers = computed(() => {
  return currentUserRole.value === 'administrator'
})

/**
 * Check if current route is users-related
 */
const isUsersRoute = computed(() => {
  return route.path.startsWith('/users')
})

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
  openDropdowns.value.clear()
}

/**
 * Handle logout
 */
function handleLogout() {
  // TODO: Implement actual logout logic
  console.log('Logout clicked')
  closeMobileMenu()
}
</script>

<style scoped>
.app-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Brand */
.nav-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.25rem;
  transition: color 0.2s;
}

.brand-link:hover {
  color: #42b883;
}

.brand-icon {
  font-size: 1.75rem;
}

.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  color: #2c3e50;
}

/* Navigation Menu */
.nav-menu {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1;
  margin-left: 2rem;
}

.nav-item {
  position: relative;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #2c3e50;
  border-radius: 4px;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
  cursor: pointer;
  border: none;
  background: none;
  font-size: 1rem;
  font-family: inherit;
}

.nav-link:hover {
  background: #f8f9fa;
  color: #42b883;
}

.nav-link.router-link-active {
  background: #e8f5e9;
  color: #42b883;
  font-weight: 500;
}

.nav-icon {
  font-size: 1.1rem;
}

.nav-item-disabled .nav-link {
  cursor: not-allowed;
  opacity: 0.5;
}

.coming-soon {
  font-size: 0.7rem;
  background: #ffc107;
  color: #212529;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  font-weight: 600;
  margin-left: 0.5rem;
}

/* Dropdown */
.nav-dropdown {
  position: relative;
}

.nav-dropdown-toggle {
  width: 100%;
}

.dropdown-arrow {
  font-size: 0.7rem;
  margin-left: 0.25rem;
  transition: transform 0.2s;
}

.nav-dropdown-toggle.is-active .dropdown-arrow {
  transform: rotate(90deg);
}

.nav-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  list-style: none;
  padding: 0.5rem 0;
  min-width: 180px;
  z-index: 1000;
}

.nav-dropdown-link {
  display: block;
  padding: 0.75rem 1rem;
  color: #2c3e50;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.95rem;
  font-family: inherit;
}

.nav-dropdown-link:hover {
  background: #f8f9fa;
  color: #42b883;
}

.nav-dropdown-link.router-link-active {
  background: #e8f5e9;
  color: #42b883;
  font-weight: 500;
}

.nav-dropdown-divider {
  height: 1px;
  background: #e0e0e0;
  margin: 0.5rem 0;
}

/* User Menu */
.nav-user {
  margin-left: auto;
}

.nav-user-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  font-family: inherit;
}

.nav-user-button:hover {
  background: #f8f9fa;
  border-color: #42b883;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #42b883;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 600;
}

.user-name {
  font-size: 0.95rem;
  color: #2c3e50;
}

.nav-user-menu {
  right: 0;
  left: auto;
}

/* Mobile Styles */
@media (max-width: 768px) {
  .app-navigation {
    padding: 0 1rem;
    height: auto;
    flex-wrap: wrap;
  }

  .nav-brand {
    width: 100%;
    justify-content: space-between;
    padding: 1rem 0;
  }

  .mobile-menu-toggle {
    display: block;
  }

  .nav-menu {
    display: none;
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    margin: 0;
    padding: 1rem 0;
    border-top: 1px solid #e0e0e0;
  }

  .nav-menu.is-open {
    display: flex;
  }

  .nav-item {
    width: 100%;
  }

  .nav-link {
    width: 100%;
    justify-content: flex-start;
  }

  .nav-dropdown-menu {
    position: static;
    margin-top: 0.5rem;
    box-shadow: none;
    border: none;
    border-left: 2px solid #42b883;
    padding-left: 1rem;
  }

  .nav-user {
    width: 100%;
    margin: 0;
    padding: 1rem 0;
    border-top: 1px solid #e0e0e0;
  }

  .nav-user-button {
    width: 100%;
    justify-content: space-between;
  }

  .nav-user-menu {
    position: static;
    margin-top: 0.5rem;
  }
}
</style>
