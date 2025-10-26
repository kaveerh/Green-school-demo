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
  // School Management Routes
  {
    path: '/schools',
    name: 'schools',
    component: () => import('@/components/SchoolList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/schools/create',
    name: 'school-create',
    component: () => import('@/components/SchoolForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/schools/:id',
    name: 'school-detail',
    component: () => import('@/components/SchoolDetail.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/schools/:id/edit',
    name: 'school-edit',
    component: () => import('@/components/SchoolForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Teacher Management Routes
  {
    path: '/teachers',
    name: 'teachers',
    component: () => import('@/components/TeacherList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/teachers/create',
    name: 'teacher-create',
    component: () => import('@/components/TeacherForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/teachers/:id',
    name: 'teacher-detail',
    component: () => import('@/components/TeacherList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/teachers/:id/edit',
    name: 'teacher-edit',
    component: () => import('@/components/TeacherForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Student Management Routes
  {
    path: '/students',
    name: 'students',
    component: () => import('@/components/StudentList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/students/create',
    name: 'student-create',
    component: () => import('@/components/StudentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/students/:id',
    name: 'student-detail',
    component: () => import('@/components/StudentList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/students/:id/edit',
    name: 'student-edit',
    component: () => import('@/components/StudentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Parent Management Routes
  {
    path: '/parents',
    name: 'parents',
    component: () => import('@/components/ParentList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/parents/create',
    name: 'parent-create',
    component: () => import('@/components/ParentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/parents/:id',
    name: 'parent-detail',
    component: () => import('@/components/ParentList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/parents/:id/edit',
    name: 'parent-edit',
    component: () => import('@/components/ParentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Subject Management Routes
  {
    path: '/subjects',
    name: 'subjects',
    component: () => import('@/components/SubjectList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/subjects/create',
    name: 'subject-create',
    component: () => import('@/components/SubjectForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/subjects/:id',
    name: 'subject-detail',
    component: () => import('@/components/SubjectList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/subjects/:id/edit',
    name: 'subject-edit',
    component: () => import('@/components/SubjectForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Room Management Routes
  {
    path: '/rooms',
    name: 'rooms',
    component: () => import('@/components/RoomList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/rooms/create',
    name: 'room-create',
    component: () => import('@/components/RoomForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/rooms/:id',
    name: 'room-detail',
    component: () => import('@/components/RoomList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rooms/:id/edit',
    name: 'room-edit',
    component: () => import('@/components/RoomForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Class Management Routes
  {
    path: '/classes',
    name: 'classes',
    component: () => import('@/components/ClassList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/classes/create',
    name: 'class-create',
    component: () => import('@/components/ClassForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  {
    path: '/classes/:id',
    name: 'class-detail',
    component: () => import('@/components/ClassList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/classes/:id/edit',
    name: 'class-edit',
    component: () => import('@/components/ClassForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator'] }
  },
  // Lesson Management Routes
  {
    path: '/lessons',
    name: 'lessons',
    component: () => import('@/views/LessonList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/lessons/create',
    name: 'lesson-create',
    component: () => import('@/views/LessonForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/lessons/:id',
    name: 'lesson-detail',
    component: () => import('@/views/LessonList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/lessons/:id/edit',
    name: 'lesson-edit',
    component: () => import('@/views/LessonForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  // Assessment Management Routes
  {
    path: '/assessments',
    name: 'assessments',
    component: () => import('@/views/AssessmentList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/assessments/create',
    name: 'assessment-create',
    component: () => import('@/views/AssessmentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/assessments/:id',
    name: 'assessment-detail',
    component: () => import('@/views/AssessmentDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/assessments/:id/edit',
    name: 'assessment-edit',
    component: () => import('@/views/AssessmentForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/assessments/:id/grade',
    name: 'assessment-grade',
    component: () => import('@/views/AssessmentDetail.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  // Attendance Management Routes
  {
    path: '/attendance',
    name: 'attendance',
    component: () => import('@/views/AttendanceList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/attendance/mark',
    name: 'attendance-mark',
    component: () => import('@/views/AttendanceForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/attendance/:id/edit',
    name: 'attendance-edit',
    component: () => import('@/views/AttendanceForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },

  // Events
  {
    path: '/events',
    name: 'events',
    component: () => import('@/views/EventList.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/events/create',
    name: 'event-create',
    component: () => import('@/views/EventForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
  },
  {
    path: '/events/:id/edit',
    name: 'event-edit',
    component: () => import('@/views/EventForm.vue'),
    meta: { requiresAuth: true, requiresRole: ['administrator', 'teacher'] }
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
