<template>
  <div class="app-layout">
    <!-- Sidebar Navigation -->
    <AppNavigation />

    <!-- Main Content Area -->
    <main class="app-main" :class="{ 'has-breadcrumb': showBreadcrumb }">
      <!-- Breadcrumb -->
      <AppBreadcrumb v-if="showBreadcrumb" class="app-breadcrumb" />

      <!-- Page Content -->
      <div class="app-content" :class="contentClass">
        <slot></slot>
      </div>

      <!-- Footer -->
      <footer v-if="showFooter" class="app-footer">
        <div class="footer-content">
          <p class="footer-text">
            © {{ currentYear }} Green School Management System
          </p>
          <div class="footer-links">
            <a href="#" class="footer-link">Privacy Policy</a>
            <span class="footer-separator">·</span>
            <a href="#" class="footer-link">Terms of Service</a>
            <span class="footer-separator">·</span>
            <a href="#" class="footer-link">Help</a>
          </div>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppNavigation from './AppNavigation.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'

interface Props {
  showBreadcrumb?: boolean
  showFooter?: boolean
  contentClass?: string
}

withDefaults(defineProps<Props>(), {
  showBreadcrumb: true,
  showFooter: true,
  contentClass: ''
})

/**
 * Current year for footer
 */
const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  background: #f8f9fa;
}

/* Main Content Area */
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 260px; /* Width of expanded sidebar */
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

/* Adjust when sidebar is collapsed (using global class that will be added via JS) */
:global(.sidebar-collapsed) .app-main {
  margin-left: 70px;
}

.app-main.has-breadcrumb {
  padding-top: 0;
}

.app-breadcrumb {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1600px;
  width: 100%;
}

/* Footer */
.app-footer {
  background: white;
  border-top: 1px solid #e5e7eb;
  padding: 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-text {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-link {
  color: #10b981;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #059669;
  text-decoration: underline;
}

.footer-separator {
  color: #d1d5db;
}

/* Mobile Styles */
@media (max-width: 1024px) {
  .app-main {
    margin-left: 0;
  }

  :global(.sidebar-collapsed) .app-main {
    margin-left: 0;
  }

  .app-breadcrumb {
    padding: 0.75rem 1rem;
    padding-top: 5rem; /* Space for mobile menu button */
  }

  .app-content {
    padding: 1rem;
  }

  .app-footer {
    padding: 1.5rem 1rem;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
