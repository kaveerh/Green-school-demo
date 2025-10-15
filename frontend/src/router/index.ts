import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  // User Management Routes
  {
    path: '/users',
    name: 'users',
    component: () => import('@/components/UserList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/users/statistics',
    name: 'user-statistics',
    component: () => import('@/components/UserStatistics.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/users/create',
    name: 'user-create',
    component: () => import('@/components/UserForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/users/:id',
    name: 'user-detail',
    component: () => import('@/components/UserDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id/edit',
    name: 'user-edit',
    component: () => import('@/components/UserForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth) {
    // TODO: Check Keycloak authentication
    // For now, allow all routes
    next()
  } else {
    next()
  }
})

export default router
