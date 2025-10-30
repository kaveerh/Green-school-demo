<template>
  <div class="debug-container">
    <h1>Debug Information</h1>

    <div class="debug-section">
      <h2>Authentication State</h2>
      <table>
        <tr>
          <td><strong>Is Authenticated:</strong></td>
          <td>{{ authStore.isAuthenticated }}</td>
        </tr>
        <tr>
          <td><strong>Is Initialized:</strong></td>
          <td>{{ authStore.isInitialized }}</td>
        </tr>
        <tr>
          <td><strong>Current User:</strong></td>
          <td>{{ authStore.currentUser?.email || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>Full Name:</strong></td>
          <td>{{ authStore.currentUser?.full_name || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>Persona:</strong></td>
          <td>{{ authStore.currentUser?.persona || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>Roles:</strong></td>
          <td>{{ authStore.currentUser?.roles?.join(', ') || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>User Role (computed):</strong></td>
          <td>{{ authStore.userRole }}</td>
        </tr>
        <tr>
          <td><strong>Has Token:</strong></td>
          <td>{{ authStore.token ? 'Yes' : 'No' }}</td>
        </tr>
      </table>
    </div>

    <div class="debug-section">
      <h2>School Context</h2>
      <table>
        <tr>
          <td><strong>Selected School:</strong></td>
          <td>{{ authStore.selectedSchool?.name || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>School ID:</strong></td>
          <td>{{ authStore.currentSchoolId || 'None' }}</td>
        </tr>
        <tr>
          <td><strong>Available Schools:</strong></td>
          <td>{{ authStore.availableSchools.length }}</td>
        </tr>
      </table>
    </div>

    <div class="debug-section">
      <h2>Role Checks</h2>
      <table>
        <tr>
          <td><strong>Is Administrator:</strong></td>
          <td>{{ authStore.hasRole('administrator') }}</td>
        </tr>
        <tr>
          <td><strong>Is Teacher:</strong></td>
          <td>{{ authStore.hasRole('teacher') }}</td>
        </tr>
        <tr>
          <td><strong>Is Parent:</strong></td>
          <td>{{ authStore.hasRole('parent') }}</td>
        </tr>
        <tr>
          <td><strong>Is Student:</strong></td>
          <td>{{ authStore.hasRole('student') }}</td>
        </tr>
        <tr>
          <td><strong>Can access users:</strong></td>
          <td>{{ authStore.hasRole('administrator') }}</td>
        </tr>
        <tr>
          <td><strong>Can access students:</strong></td>
          <td>{{ authStore.hasAnyRole(['administrator', 'teacher']) }}</td>
        </tr>
      </table>
    </div>

    <div class="debug-section">
      <h2>Keycloak Token Info</h2>
      <pre>{{ keycloakInfo }}</pre>
    </div>

    <div class="debug-section">
      <h2>Test Navigation</h2>
      <div class="test-links">
        <router-link to="/dashboard" class="test-link">Go to Dashboard</router-link>
        <router-link to="/users" class="test-link">Go to Users</router-link>
        <router-link to="/students" class="test-link">Go to Students</router-link>
        <router-link to="/classes" class="test-link">Go to Classes</router-link>
      </div>
    </div>

    <div class="debug-section">
      <h2>Current Route</h2>
      <table>
        <tr>
          <td><strong>Path:</strong></td>
          <td>{{ $route.path }}</td>
        </tr>
        <tr>
          <td><strong>Name:</strong></td>
          <td>{{ $route.name }}</td>
        </tr>
        <tr>
          <td><strong>Params:</strong></td>
          <td>{{ JSON.stringify($route.params) }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import * as KeycloakService from '@/services/keycloak'

const authStore = useAuthStore()

const keycloakInfo = computed(() => {
  const keycloak = KeycloakService.getKeycloak()
  if (!keycloak || !keycloak.tokenParsed) {
    return 'No Keycloak token available'
  }

  return {
    authenticated: keycloak.authenticated,
    tokenParsed: keycloak.tokenParsed,
    realmAccess: keycloak.tokenParsed.realm_access
  }
})
</script>

<style scoped>
.debug-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #1e293b;
  margin-bottom: 2rem;
}

h2 {
  color: #475569;
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.debug-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

tr {
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 0.75rem;
}

td:first-child {
  width: 250px;
}

pre {
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.875rem;
}

.test-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.test-link {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background 0.2s;
}

.test-link:hover {
  background: #5568d3;
}
</style>
