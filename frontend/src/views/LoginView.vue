<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Logo and Branding -->
      <div class="login-header">
        <div class="brand-logo">
          <span class="brand-icon">🌱</span>
          <h1 class="brand-title">Green School</h1>
        </div>
        <p class="brand-subtitle">Management System</p>
      </div>

      <!-- Login Content -->
      <div class="login-content">
        <h2>Welcome Back</h2>
        <p class="login-description">Sign in to access your school management dashboard</p>

        <!-- Error Message -->
        <div v-if="authStore.authError" class="alert alert-error">
          <span class="alert-icon">⚠️</span>
          <span>{{ authStore.authError }}</span>
        </div>

        <!-- Login Button -->
        <button @click="handleLogin" class="btn btn-primary btn-large" :disabled="isLoading">
          <span v-if="isLoading" class="btn-loading">
            <span class="spinner"></span>
            Connecting...
          </span>
          <span v-else>
            <span class="btn-icon">🔐</span>
            Sign In with Keycloak
          </span>
        </button>

        <!-- Demo Accounts Link -->
        <div class="login-footer">
          <p class="text-muted">Don't have an account?</p>
          <router-link to="/demo" class="link-primary">
            View Demo Accounts
          </router-link>
        </div>
      </div>

      <!-- Info Section -->
      <div class="login-info">
        <div class="info-item">
          <span class="info-icon">✓</span>
          <span>Secure Single Sign-On</span>
        </div>
        <div class="info-item">
          <span class="info-icon">✓</span>
          <span>Role-Based Access Control</span>
        </div>
        <div class="info-item">
          <span class="info-icon">✓</span>
          <span>Multi-School Management</span>
        </div>
      </div>
    </div>

    <!-- Background Decoration -->
    <div class="login-decoration">
      <div class="decoration-circle decoration-circle-1"></div>
      <div class="decoration-circle decoration-circle-2"></div>
      <div class="decoration-circle decoration-circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const isLoading = ref(false)

function handleLogin() {
  isLoading.value = true
  authStore.login()
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

/* Login Card */
.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 3rem;
  max-width: 480px;
  width: 100%;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.brand-icon {
  font-size: 3rem;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.brand-subtitle {
  font-size: 1.125rem;
  color: #64748b;
  margin: 0;
}

/* Content */
.login-content {
  margin-bottom: 2rem;
}

.login-content h2 {
  font-size: 1.75rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.login-description {
  color: #64748b;
  margin: 0 0 2rem 0;
  font-size: 1rem;
}

/* Alert */
.alert {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9375rem;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.alert-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

/* Button */
.btn {
  width: 100%;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-family: inherit;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.25rem;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Footer */
.login-footer {
  text-align: center;
  margin-top: 2rem;
}

.text-muted {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
}

.link-primary {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9375rem;
  transition: color 0.2s;
}

.link-primary:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Info Section */
.login-info {
  border-top: 1px solid #e2e8f0;
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #475569;
  font-size: 0.9375rem;
}

.info-icon {
  color: #10b981;
  font-weight: 600;
}

/* Background Decoration */
.login-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.decoration-circle-1 {
  width: 400px;
  height: 400px;
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.decoration-circle-2 {
  width: 300px;
  height: 300px;
  bottom: -150px;
  left: -100px;
  animation-delay: 5s;
}

.decoration-circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: -50px;
  animation-delay: 10s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .login-container {
    padding: 1rem;
  }

  .login-card {
    padding: 2rem 1.5rem;
  }

  .brand-title {
    font-size: 2rem;
  }

  .login-content h2 {
    font-size: 1.5rem;
  }
}
</style>
