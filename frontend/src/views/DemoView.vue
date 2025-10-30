<template>
  <div class="demo-container">
    <div class="demo-content">
      <!-- Header -->
      <div class="demo-header">
        <router-link to="/login" class="back-link">
          <span class="back-icon">←</span>
          Back to Login
        </router-link>

        <div class="demo-title-section">
          <div class="brand-logo">
            <span class="brand-icon">🌱</span>
            <h1 class="brand-title">Green School</h1>
          </div>
          <h2 class="demo-title">Demo Accounts</h2>
          <p class="demo-description">
            Choose a persona to explore the system with different roles and permissions
          </p>
        </div>
      </div>

      <!-- Persona Cards -->
      <div class="persona-grid">
        <!-- Administrator -->
        <div class="persona-card administrator">
          <div class="persona-icon">👨‍💼</div>
          <h3 class="persona-name">Administrator</h3>
          <p class="persona-description">Full system access with user and school management</p>

          <div class="persona-credentials">
            <div class="credential-item">
              <span class="credential-label">Username:</span>
              <code class="credential-value">admin@greenschool.edu</code>
            </div>
            <div class="credential-item">
              <span class="credential-label">Password:</span>
              <code class="credential-value">Admin123</code>
            </div>
          </div>

          <div class="persona-features">
            <div class="feature-item">✓ User Management</div>
            <div class="feature-item">✓ School Settings</div>
            <div class="feature-item">✓ All Reports</div>
            <div class="feature-item">✓ System Configuration</div>
          </div>

          <button @click="handleLogin" class="btn btn-persona">
            Sign In as Administrator
          </button>
        </div>

        <!-- Teacher -->
        <div class="persona-card teacher">
          <div class="persona-icon">👨‍🏫</div>
          <h3 class="persona-name">Teacher</h3>
          <p class="persona-description">Manage classes, lessons, assessments, and attendance</p>

          <div class="persona-credentials">
            <div class="credential-item">
              <span class="credential-label">Username:</span>
              <code class="credential-value">teacher@greenschool.edu</code>
            </div>
            <div class="credential-item">
              <span class="credential-label">Password:</span>
              <code class="credential-value">Admin123</code>
            </div>
          </div>

          <div class="persona-features">
            <div class="feature-item">✓ Class Management</div>
            <div class="feature-item">✓ Grade Students</div>
            <div class="feature-item">✓ Mark Attendance</div>
            <div class="feature-item">✓ Lesson Planning</div>
          </div>

          <button @click="handleLogin" class="btn btn-persona">
            Sign In as Teacher
          </button>
        </div>

        <!-- Parent -->
        <div class="persona-card parent">
          <div class="persona-icon">👪</div>
          <h3 class="persona-name">Parent</h3>
          <p class="persona-description">Monitor children's progress, attendance, and grades</p>

          <div class="persona-credentials">
            <div class="credential-item">
              <span class="credential-label">Username:</span>
              <code class="credential-value">parent@greenschool.edu</code>
            </div>
            <div class="credential-item">
              <span class="credential-label">Password:</span>
              <code class="credential-value">Admin123</code>
            </div>
          </div>

          <div class="persona-features">
            <div class="feature-item">✓ View Grades</div>
            <div class="feature-item">✓ Track Attendance</div>
            <div class="feature-item">✓ View Reports</div>
            <div class="feature-item">✓ School Events</div>
          </div>

          <button @click="handleLogin" class="btn btn-persona">
            Sign In as Parent
          </button>
        </div>

        <!-- Student -->
        <div class="persona-card student">
          <div class="persona-icon">🎓</div>
          <h3 class="persona-name">Student</h3>
          <p class="persona-description">Access assignments, grades, and school resources</p>

          <div class="persona-credentials">
            <div class="credential-item">
              <span class="credential-label">Username:</span>
              <code class="credential-value">student@greenschool.edu</code>
            </div>
            <div class="credential-item">
              <span class="credential-label">Password:</span>
              <code class="credential-value">Admin123</code>
            </div>
          </div>

          <div class="persona-features">
            <div class="feature-item">✓ View Assignments</div>
            <div class="feature-item">✓ Check Grades</div>
            <div class="feature-item">✓ Class Schedule</div>
            <div class="feature-item">✓ Personal Dashboard</div>
          </div>

          <button @click="handleLogin" class="btn btn-persona">
            Sign In as Student
          </button>
        </div>
      </div>

      <!-- Info Section -->
      <div class="demo-info">
        <div class="info-card">
          <h3>🔐 Authentication via Keycloak</h3>
          <p>
            This demo uses Keycloak for secure authentication. Each persona has different roles and permissions
            managed through Keycloak's role-based access control (RBAC).
          </p>
        </div>

        <div class="info-card">
          <h3>🏫 Multi-Tenant Architecture</h3>
          <p>
            The system supports multiple schools with complete data isolation. Each user can be associated
            with one or more schools, with separate dashboards and reports per school.
          </p>
        </div>

        <div class="info-card">
          <h3>📊 Role-Based Features</h3>
          <p>
            Different personas have access to different features. Administrators have full control,
            while teachers, parents, and students have access to features relevant to their roles.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

function handleLogin() {
  authStore.login()
}
</script>

<style scoped>
.demo-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.demo-content {
  max-width: 1400px;
  margin: 0 auto;
}

/* Header */
.demo-header {
  text-align: center;
  margin-bottom: 3rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  font-weight: 500;
  margin-bottom: 2rem;
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  transition: all 0.2s;
}

.back-link:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-4px);
}

.back-icon {
  font-size: 1.25rem;
}

.demo-title-section {
  background: white;
  padding: 3rem 2rem;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: fadeInDown 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
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

.demo-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.demo-description {
  font-size: 1.125rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto;
}

/* Persona Grid */
.persona-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.persona-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  animation: fadeInUp 0.6s ease-out;
  animation-fill-mode: both;
}

.persona-card:nth-child(1) {
  animation-delay: 0.1s;
}
.persona-card:nth-child(2) {
  animation-delay: 0.2s;
}
.persona-card:nth-child(3) {
  animation-delay: 0.3s;
}
.persona-card:nth-child(4) {
  animation-delay: 0.4s;
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

.persona-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.persona-icon {
  font-size: 4rem;
  text-align: center;
  margin-bottom: 1rem;
}

.persona-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  text-align: center;
}

.persona-description {
  color: #64748b;
  text-align: center;
  margin: 0 0 1.5rem 0;
  font-size: 0.9375rem;
}

/* Credentials */
.persona-credentials {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.credential-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.credential-item:last-child {
  margin-bottom: 0;
}

.credential-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.credential-value {
  background: white;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #1e293b;
  font-family: 'Courier New', monospace;
  border: 1px solid #e2e8f0;
}

/* Features */
.persona-features {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.feature-item {
  font-size: 0.875rem;
  color: #475569;
  padding: 0.5rem 0;
}

/* Button */
.btn {
  width: 100%;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-persona {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-persona:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Info Section */
.demo-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.info-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.6s ease-out 0.5s;
  animation-fill-mode: both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.info-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 1rem 0;
}

.info-card p {
  color: #64748b;
  margin: 0;
  line-height: 1.6;
  font-size: 0.9375rem;
}

/* Responsive */
@media (max-width: 768px) {
  .demo-container {
    padding: 1rem;
  }

  .demo-title-section {
    padding: 2rem 1.5rem;
  }

  .brand-title {
    font-size: 2rem;
  }

  .demo-title {
    font-size: 1.5rem;
  }

  .persona-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .demo-info {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>
