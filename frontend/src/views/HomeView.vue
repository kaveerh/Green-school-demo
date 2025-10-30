<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
    <div class="text-center">
      <div class="mb-6">
        <span class="text-8xl">🌱</span>
      </div>
      <h1 class="text-6xl font-bold text-primary-700 mb-4">
        Green School Management System
      </h1>
      <p class="text-xl text-gray-600 mb-8">
        Comprehensive digital platform for primary school administration (Grades 1-7)
      </p>
      <div class="space-x-4">
        <router-link
          v-if="authStore.isAuthenticated"
          to="/dashboard"
          class="inline-block px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition"
        >
          Go to Dashboard
        </router-link>
        <router-link
          v-else
          to="/login"
          class="inline-block px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition"
        >
          Sign In
        </router-link>
        <router-link
          v-if="!authStore.isAuthenticated"
          to="/demo"
          class="inline-block px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg border-2 border-primary-600 hover:bg-primary-50 transition"
        >
          View Demo Accounts
        </router-link>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          class="inline-block px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg border-2 border-primary-600 hover:bg-primary-50 transition"
        >
          View API Docs
        </a>
      </div>
      <div class="mt-12 text-sm text-gray-500">
        <p>Version 1.0.0 | Infrastructure Complete</p>
        <p class="mt-2">
          <a href="http://localhost:8080" target="_blank" class="text-primary-600 hover:underline">Keycloak</a> |
          <a href="http://localhost:8000/api/v1/health" target="_blank" class="text-primary-600 hover:underline ml-2">Backend Health</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
</script>
