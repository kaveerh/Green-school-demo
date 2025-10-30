<template>
  <div id="app">
    <!-- Loading Screen -->
    <div v-if="!authStore.isInitialized" class="auth-loading">
      <div class="loading-content">
        <div class="brand-logo">
          <span class="brand-icon">🌱</span>
          <h1 class="brand-title">Green School</h1>
        </div>
        <div class="loading-spinner"></div>
        <p class="loading-text">Initializing...</p>
      </div>
    </div>

    <!-- Main App -->
    <AppLayout v-else>
      <RouterView />
    </AppLayout>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import AppLayout from './components/AppLayout.vue'

const authStore = useAuthStore()
</script>

<style>
#app {
  font-family: Inter, system-ui, -apple-system, sans-serif;
}

/* Auth Loading Screen */
.auth-loading {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 9999;
}

.loading-content {
  text-align: center;
  color: white;
}

.brand-logo {
  margin-bottom: 2rem;
}

.brand-icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 1rem;
}

.brand-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: white;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  margin: 2rem auto;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}
</style>
