<template>
  <div class="app-layout">
    <!-- Navigation -->
    <AppNavigation />

    <!-- Main Content Area -->
    <main class="app-main" :class="{ 'has-breadcrumb': showBreadcrumb }">
      <!-- Breadcrumb -->
      <AppBreadcrumb v-if="showBreadcrumb" class="app-breadcrumb" />

      <!-- Page Content -->
      <div class="app-content" :class="contentClass">
        <slot></slot>
      </div>
    </main>

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
  flex-direction: column;
  background: #f8f9fa;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.app-main.has-breadcrumb {
  padding-top: 0;
}

.app-breadcrumb {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 1rem 2rem;
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

/* Footer */
.app-footer {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-text {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.footer-link {
  color: #42b883;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #35a372;
  text-decoration: underline;
}

.footer-separator {
  color: #dee2e6;
}

@media (max-width: 768px) {
  .app-breadcrumb {
    padding: 0.75rem 1rem;
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
