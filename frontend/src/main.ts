import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/main.css'
import { useAuthStore } from '@/stores/authStore'

/**
 * Initialize the application with Keycloak authentication
 */
async function initializeApp() {
  try {
    // Create app instance
    const app = createApp(App)

    // Create Pinia instance and use it (required before accessing stores)
    const pinia = createPinia()
    app.use(pinia)

    // Initialize Keycloak authentication
    console.log('🔐 Initializing Keycloak authentication...')
    const authStore = useAuthStore()
    await authStore.initializeKeycloak()

    // Use router after auth is initialized
    app.use(router)

    // Mount the app
    app.mount('#app')

    console.log('✅ Application initialized successfully')
  } catch (error) {
    console.error('❌ Failed to initialize application:', error)

    // Show error to user
    document.body.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: system-ui, -apple-system, sans-serif;">
        <div style="background: white; border-radius: 20px; padding: 3rem; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
          <h1 style="font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0 0 1rem 0;">⚠️ Initialization Error</h1>
          <p style="color: #64748b; margin: 0 0 1.5rem 0;">Failed to initialize the application. Please check your connection and try again.</p>
          <button onclick="location.reload()" style="width: 100%; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer;">
            Retry
          </button>
        </div>
      </div>
    `
  }
}

// Start the application
initializeApp()
